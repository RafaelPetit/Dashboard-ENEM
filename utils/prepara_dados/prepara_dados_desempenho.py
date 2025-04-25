import pandas as pd
import numpy as np
import streamlit as st
from utils.data_loader import calcular_seguro
from utils.helpers.cache_utils import optimized_cache

@optimized_cache()
def preparar_dados_comparativo(microdados_full, variavel_selecionada, variaveis_categoricas, 
                              colunas_notas, competencia_mapping):
    """
    Prepara os dados para análise comparativa de desempenho por variável categórica.
    """
    # Criar uma coluna com os valores mapeados
    nome_coluna_mapeada = f"{variavel_selecionada}_NOME"
    mapeamento = variaveis_categoricas[variavel_selecionada]["mapeamento"]
    
    # Aplicar mapeamento tratando valores NaN e garantindo strings
    df_trabalho = microdados_full.copy()
    df_trabalho[nome_coluna_mapeada] = df_trabalho[variavel_selecionada].apply(
        lambda x: str(mapeamento.get(x, f"Outro ({x})")) if pd.notna(x) else "Não informado"
    )
    
    # Calcular médias por categoria de forma otimizada
    resultados = []
    categorias_unicas = df_trabalho[nome_coluna_mapeada].unique()
    
    for categoria in categorias_unicas:
        dados_categoria = df_trabalho[df_trabalho[nome_coluna_mapeada] == categoria]
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
    """
    categorias_unicas = df_resultados['Categoria'].unique()
    
    # Tentar obter a ordem definida para esta variável
    if variavel_selecionada in variaveis_categoricas and 'ordem' in variaveis_categoricas[variavel_selecionada]:
        # Filtrar a ordem para incluir apenas categorias presentes nos dados
        ordem_definida = variaveis_categoricas[variavel_selecionada]['ordem']
        ordem_filtrada = [cat for cat in ordem_definida if cat in categorias_unicas]
        
        # Adicionar quaisquer categorias que estejam nos dados mas não na ordem definida
        categorias_faltantes = [cat for cat in categorias_unicas if cat not in ordem_filtrada]
        ordem_categorias = ordem_filtrada + sorted(categorias_faltantes)
    else:
        # Se não há ordem específica definida, usar ordem alfabética
        ordem_categorias = sorted(categorias_unicas)
    
    return ordem_categorias


def preparar_dados_grafico_linha(df_resultados, competencia_ordenacao=None, competencia_filtro=None, ordenar_decrescente=False):
    """
    Prepara os dados para o gráfico de linha de desempenho por categoria.
    """
    # Criar cópia para não modificar o original
    df_linha = df_resultados.copy()
    
    # Primeiro aplicar ordenação (se solicitada)
    if ordenar_decrescente and competencia_ordenacao:
        # Criar um DataFrame apenas com a competência de ordenação para determinar a ordem
        df_ordem = df_resultados[df_resultados['Competência'] == competencia_ordenacao].copy()
        ordem_categorias = df_ordem.sort_values('Média', ascending=False)['Categoria'].unique().tolist()
        
        # Aplicar essa ordem a todos os dados
        df_linha['Categoria'] = pd.Categorical(df_linha['Categoria'], 
                                               categories=ordem_categorias, 
                                               ordered=True)
        df_linha = df_linha.sort_values('Categoria')
    
    # Aplicar filtro de competência (se solicitado)
    if competencia_filtro is not None:
        df_linha = df_linha[df_linha['Competência'] == competencia_filtro]
    
    # Garantir que temos uma ordem categórica mesmo quando não ordenamos por valor
    if not ordenar_decrescente and 'Categoria' in df_linha.columns:
        # Preservar a ordem original da categoria se ela já for categórica e ordenada
        if not (isinstance(df_linha['Categoria'].dtype, pd.CategoricalDtype) and 
                df_linha['Categoria'].dtype.ordered):
            # Caso contrário, ordenar alfabeticamente
            categorias_unicas = df_linha['Categoria'].unique()
            df_linha['Categoria'] = pd.Categorical(df_linha['Categoria'], 
                                                  categories=categorias_unicas, 
                                                  ordered=True)
    
    return df_linha


@optimized_cache()
def preparar_dados_desempenho_geral(microdados, colunas_notas, desempenho_mapping):
    """
    Prepara dados gerais de desempenho, incluindo categorias de desempenho.
    """
    # Criar cópia do DataFrame para trabalhar
    microdados_full = microdados.copy()
    
    # Adicionar categoria de desempenho se existir a coluna
    if 'NU_DESEMPENHO' in microdados_full.columns:
        microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].map(desempenho_mapping)
    
    return microdados_full


@optimized_cache()
def filtrar_dados_scatter(dados, filtro_sexo, filtro_tipo_escola, eixo_x, eixo_y, excluir_notas_zero=True, race_mapping=None, filtro_faixa_salarial=None):
    df = dados.copy()
    registros_removidos = 0
    
    # Filtros existentes
    if filtro_sexo:
        df = df[df['TP_SEXO'] == filtro_sexo]
    
    if filtro_tipo_escola == 'Pública':
        df = df[df['TP_DEPENDENCIA_ADM_ESC'].isin(['1', '2', '3'])]
    elif filtro_tipo_escola == 'Privada':
        df = df[df['TP_DEPENDENCIA_ADM_ESC'] == '4']
    
    # Novo filtro para faixa salarial
    if filtro_faixa_salarial is not None:
        df = df[df['TP_FAIXA_SALARIAL'] == filtro_faixa_salarial]
    
    if excluir_notas_zero:
        tamanho_antes = len(df)
        df = df[(df[eixo_x] > 0) & (df[eixo_y] > 0)]
        registros_removidos = tamanho_antes - len(df)
    
    return df, registros_removidos


@optimized_cache()
def prepara_dados_grafico_linha_desempenho(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """
    Prepara dados para o gráfico de linha que mostra o desempenho médio por estado.
    """
    dados_grafico = []
    dados_medias_gerais = []
    
    # Calcular a média para cada área e estado de forma eficiente
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        medias_estado_atual = []
        
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
    
    # Combinar os DataFrames de forma otimizada
    df_final = pd.concat([pd.DataFrame(dados_medias_gerais), pd.DataFrame(dados_grafico)], ignore_index=True)
    
    return df_final