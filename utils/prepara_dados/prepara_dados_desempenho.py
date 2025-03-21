import pandas as pd
import numpy as np
import streamlit as st
from utils.data_loader import calcular_seguro




def preparar_dados_comparativo(microdados_full, variavel_selecionada, variaveis_categoricas, 
                              colunas_notas, competencia_mapping):
    """
    Prepara os dados para análise comparativa de desempenho por variável categórica.
    
    Parâmetros:
    -----------
    microdados_full: DataFrame
        DataFrame com os dados dos candidatos
    variavel_selecionada: str
        Nome da variável categórica selecionada para análise
    variaveis_categoricas: dict
        Dicionário com informações sobre variáveis categóricas
    colunas_notas: list
        Lista de colunas contendo as notas de cada competência
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
    
    Retorna:
    --------
    DataFrame: DataFrame com resultados para visualização
    """
    # Criar uma coluna com os valores mapeados
    nome_coluna_mapeada = f"{variavel_selecionada}_NOME"
    mapeamento = variaveis_categoricas[variavel_selecionada]["mapeamento"]
    
    # Aplicar mapeamento tratando valores NaN e garantindo strings
    microdados_full[nome_coluna_mapeada] = microdados_full[variavel_selecionada].apply(
        lambda x: str(mapeamento.get(x, f"Outro ({x})")) if pd.notna(x) else "Não informado"
    )
    
    # Calcular médias por categoria
    resultados = []
    categorias_unicas = microdados_full[nome_coluna_mapeada].unique()
    
    for categoria in categorias_unicas:
        dados_categoria = microdados_full[microdados_full[nome_coluna_mapeada] == categoria]
        for competencia in colunas_notas:
            media_comp = calcular_seguro(dados_categoria[competencia], operacao='media')
            resultados.append({
                'Categoria': categoria,
                'Competência': competencia_mapping[competencia],
                'Média': round(media_comp, 2)
            })
    
    # Criar DataFrame para visualização
    return pd.DataFrame(resultados)


def obter_ordem_categorias(df_resultados, variavel_selecionada, variaveis_categoricas):
    """
    Determina a ordem das categorias para exibição no gráfico.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com os resultados formatados
    variavel_selecionada: str
        Nome da variável categórica selecionada
    variaveis_categoricas: dict
        Dicionário com informações sobre variáveis categóricas
    
    Retorna:
    --------
    list: Lista ordenada de categorias
    """
    categorias_unicas = df_resultados['Categoria'].unique()
    ordem_categorias = variaveis_categoricas[variavel_selecionada].get('ordem')
    
    if not ordem_categorias:
        # Se não há ordem específica definida, usar ordem alfabética
        ordem_categorias = sorted(categorias_unicas)
    
    return ordem_categorias

def preparar_dados_grafico_linha(df_resultados, competencia_ordenacao=None, competencia_filtro=None, ordenar_decrescente=False):
    """
    Prepara os dados para o gráfico de linha de desempenho por categoria.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame contendo os resultados já preparados da análise comparativa
    competencia_ordenacao: str, opcional
        Competência usada como referência para ordenação
    competencia_filtro: str, opcional
        Se fornecido, filtra apenas para a competência específica
    ordenar_decrescente: bool
        Se True, ordena categorias por valor decrescente de média
        
    Retorna:
    --------
    DataFrame: DataFrame formatado para o gráfico de linha
    """
    # Criar cópia para não modificar o original
    df_linha = df_resultados.copy()
    
    # Primeiro aplicar ordenação (se solicitada)
    if ordenar_decrescente and competencia_ordenacao:
        # Criar um DataFrame apenas com a competência de ordenação para determinar a ordem
        df_ordem = df_resultados[df_resultados['Competência'] == competencia_ordenacao].copy()
        ordem_categorias = df_ordem.sort_values('Média', ascending=False)['Categoria'].unique().tolist()
        
        # Aplicar essa ordem a todos os dados
        df_linha['Categoria'] = pd.Categorical(df_linha['Categoria'], categories=ordem_categorias, ordered=True)
        df_linha = df_linha.sort_values(['Competência', 'Categoria'])
    
    # Depois aplicar filtro (se solicitado) - isso deve vir depois da ordenação
    if competencia_filtro:
        df_linha = df_linha[df_linha['Competência'] == competencia_filtro]
    
    return df_linha


def preparar_dados_desempenho_geral(microdados, colunas_notas, desempenho_mapping):
    """
    Prepara dados gerais de desempenho, incluindo categorias de desempenho.
    
    Parâmetros:
    -----------
    microdados: DataFrame
        DataFrame com os dados dos candidatos
    colunas_notas: list
        Lista de colunas contendo as notas de cada competência
    desempenho_mapping: dict
        Mapeamento de valores numéricos para categorias de desempenho
    
    Retorna:
    --------
    DataFrame: DataFrame com dados de desempenho categorizados
    """
    # Criar cópia do DataFrame para trabalhar
    microdados_full = microdados.copy()
    
    # Adicionar categoria de desempenho se existir a coluna
    if 'NU_DESEMPENHO' in microdados_full.columns:
        microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].map(desempenho_mapping)
    
    return microdados_full


def filtrar_dados_scatter(microdados_estados, sexo, tipo_escola, eixo_x, eixo_y, 
                         excluir_notas_zero, race_mapping, max_points=15000):
    """
    Filtra os dados para o gráfico de dispersão com base nas seleções do usuário.
    
    Parâmetros:
    -----------
    microdados_estados: DataFrame
        DataFrame com os dados filtrados por estado
    sexo: str
        Filtro de sexo selecionado ("Todos", "M" ou "F")
    tipo_escola: str
        Filtro de tipo de escola selecionado
    eixo_x: str
        Variável selecionada para o eixo X
    eixo_y: str
        Variável selecionada para o eixo Y
    excluir_notas_zero: bool
        Indica se notas zero devem ser excluídas
    race_mapping: dict
        Mapeamento de códigos para categorias de raça/cor
    
    Retorna:
    --------
    tuple: (DataFrame filtrado, int registros removidos)
    """
     # Cópia para evitar modificações no DataFrame original
    query_parts = []
    if sexo != "Todos":
        query_parts.append(f"TP_SEXO == '{sexo}'")
    if tipo_escola != "Todos":
        tipo_map = {"Federal": 1, "Estadual": 2, "Municipal": 3, "Privada": 4}
        query_parts.append(f"TP_DEPENDENCIA_ADM_ESC == {tipo_map[tipo_escola]}")
    if excluir_notas_zero:
        query_parts.append(f"{eixo_x} > 0 and {eixo_y} > 0")
    
    # Aplicar filtros em uma única operação
    if query_parts:
        query_string = " and ".join(query_parts)
        dados_filtrados = microdados_estados.query(query_string).copy()
    else:
        dados_filtrados = microdados_estados.copy()
    
    # Amostragem se o DataFrame for muito grande
    if len(dados_filtrados) > max_points:
        # Usar amostragem estratificada para preservar distribuição por raça
        dados_filtrados['RACA_COR'] = dados_filtrados['TP_COR_RACA'].map(race_mapping)
        resultado = []
        for raca in dados_filtrados['RACA_COR'].unique():
            subset = dados_filtrados[dados_filtrados['RACA_COR'] == raca]
            n_samples = int(max_points * len(subset) / len(dados_filtrados))
            if n_samples > 0:
                resultado.append(subset.sample(min(n_samples, len(subset))))
        dados_filtrados = pd.concat(resultado)
    
    return dados_filtrados, len(microdados_estados) - len(dados_filtrados)
    
@st.cache_data    
def prepara_dados_grafico_linha_desempenho(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """
    Prepara dados para o gráfico de linha que mostra o desempenho médio por estado.
    
    Parâmetros:
    -----------
    microdados_estados: DataFrame
        DataFrame com os dados filtrados pelos estados selecionados
    estados_selecionados: list
        Lista de siglas dos estados selecionados
    colunas_notas: list
        Lista de colunas contendo as notas de cada competência
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
    
    Retorna:
    --------
    DataFrame: DataFrame formatado para o gráfico de linha, com médias por estado e área
    """
    dados_grafico = []
    dados_medias_gerais = []  # Lista separada para médias gerais
    
    # Primeiro, calculamos a média para cada área e estado
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        medias_estado_atual = []  # Lista para armazenar médias deste estado
        
        for area in colunas_notas:
            # Filtrar notas válidas (maiores que zero)
            dados_filtrados = dados_estado[dados_estado[area] > 0][area]
            media_area = round(calcular_seguro(dados_filtrados), 2)
            
            # Adicionar ao DataFrame de resultados
            dados_grafico.append({
                'Estado': estado,
                'Área': competencia_mapping[area],
                'Média': media_area
            })
            
            # Armazenar para cálculo da média geral
            medias_estado_atual.append(media_area)
        
        # Calcular e armazenar a média geral para este estado
        if medias_estado_atual:
            media_geral_estado = round(sum(medias_estado_atual) / len(medias_estado_atual), 2)
            
            # Armazenar em lista separada
            dados_medias_gerais.append({
                'Estado': estado,
                'Área': 'Média Geral',
                'Média': media_geral_estado,
            })
    
    # Combinar os DataFrames com médias gerais primeiro para garantir ordem consistente
    df_medias_gerais = pd.DataFrame(dados_medias_gerais)
    df_outras_areas = pd.DataFrame(dados_grafico)
    df_final = pd.concat([df_medias_gerais, df_outras_areas], ignore_index=True)
    
    return df_final