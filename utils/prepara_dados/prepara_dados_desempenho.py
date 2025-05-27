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
    Versão otimizada para usar menos memória.
    """
    # Criar cópia apenas das colunas necessárias
    colunas_necessarias = [variavel_selecionada] + colunas_notas
    df_trabalho = microdados_full[colunas_necessarias].copy()
    
    # Filtrar registros com valores inválidos
    df_trabalho = df_trabalho.dropna(subset=[variavel_selecionada])
    
    # Converter para tipo categórico para economizar memória
    if variavel_selecionada in variaveis_categoricas and "mapeamento" in variaveis_categoricas[variavel_selecionada]:
        mapeamento = variaveis_categoricas[variavel_selecionada]["mapeamento"]
        # Criar coluna mapeada apenas se for realmente usar
        nome_coluna_mapeada = variavel_selecionada
    else:
        # Sem mapeamento disponível
        mapeamento = None
        nome_coluna_mapeada = variavel_selecionada
    
    # Calcular médias por categoria de forma otimizada
    resultados = []
    categorias_unicas = df_trabalho[nome_coluna_mapeada].unique()
    
    # Pré-calcular médias para cada categoria e competência
    for categoria in categorias_unicas:
        # Filtrar apenas uma vez por categoria (mais eficiente)
        dados_categoria = df_trabalho[df_trabalho[nome_coluna_mapeada] == categoria]
        
        # Aplicar mapeamento, se disponível
        categoria_exibicao = mapeamento.get(categoria, str(categoria)) if mapeamento else str(categoria)
        
        # Calcular médias para cada competência na mesma filtragem
        for competencia in colunas_notas:
            # Filtra valores inválidos
            notas_validas = dados_categoria[dados_categoria[competencia] > 0][competencia]
            
            if len(notas_validas) > 0:
                media_comp = notas_validas.mean()
            else:
                media_comp = 0
                
            resultados.append({
                'Categoria': categoria_exibicao,
                'Competência': competencia_mapping[competencia],
                'Média': round(media_comp, 2)
            })
    
    # Criar DataFrame para visualização
    return pd.DataFrame(resultados)

@optimized_cache()
def preparar_dados_grafico_linha(df_resultados, competencia_ordenacao=None, competencia_filtro=None, ordenar_decrescente=False):
    """
    Prepara os dados para o gráfico de linha de desempenho por categoria.
    Versão otimizada com melhor manipulação de categorias.
    """
    # Trabalhar com uma cópia otimizada
    df_linha = df_resultados.copy()
    
    # Aplicar filtro de competência (se solicitado)
    if competencia_filtro is not None:
        df_linha = df_linha[df_linha['Competência'] == competencia_filtro]
    
    # Aplicar ordenação (se solicitada)
    if ordenar_decrescente and competencia_ordenacao:
        # Criar um DataFrame apenas com a competência de ordenação para determinar a ordem
        df_ordem = df_resultados[df_resultados['Competência'] == competencia_ordenacao].copy()
        ordem_categorias = df_ordem.sort_values('Média', ascending=False)['Categoria'].unique().tolist()
        
        # Aplicar essa ordem categoricamente
        df_linha['Categoria'] = pd.Categorical(df_linha['Categoria'], 
                                               categories=ordem_categorias, 
                                               ordered=True)
        df_linha = df_linha.sort_values('Categoria')
    
    return df_linha

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


# def preparar_dados_grafico_linha(df_resultados, competencia_ordenacao=None, competencia_filtro=None, ordenar_decrescente=False):
#     """
#     Prepara os dados para o gráfico de linha de desempenho por categoria.
#     """
#     # Criar cópia para não modificar o original
#     df_linha = df_resultados.copy()
    
#     # Primeiro aplicar ordenação (se solicitada)
#     if ordenar_decrescente and competencia_ordenacao:
#         # Criar um DataFrame apenas com a competência de ordenação para determinar a ordem
#         df_ordem = df_resultados[df_resultados['Competência'] == competencia_ordenacao].copy()
#         ordem_categorias = df_ordem.sort_values('Média', ascending=False)['Categoria'].unique().tolist()
        
#         # Aplicar essa ordem a todos os dados
#         df_linha['Categoria'] = pd.Categorical(df_linha['Categoria'], 
#                                                categories=ordem_categorias, 
#                                                ordered=True)
#         df_linha = df_linha.sort_values('Categoria')
    
#     # Aplicar filtro de competência (se solicitado)
#     if competencia_filtro is not None:
#         df_linha = df_linha[df_linha['Competência'] == competencia_filtro]
    
#     # Garantir que temos uma ordem categórica mesmo quando não ordenamos por valor
#     if not ordenar_decrescente and 'Categoria' in df_linha.columns:
#         # Preservar a ordem original da categoria se ela já for categórica e ordenada
#         if not (isinstance(df_linha['Categoria'].dtype, pd.CategoricalDtype) and 
#                 df_linha['Categoria'].dtype.ordered):
#             # Caso contrário, ordenar alfabeticamente
#             categorias_unicas = df_linha['Categoria'].unique()
#             df_linha['Categoria'] = pd.Categorical(df_linha['Categoria'], 
#                                                   categories=categorias_unicas, 
#                                                   ordered=True)
    
#     return df_linha


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
    """
    Filtra dados para visualização de dispersão.
    Versão otimizada para reduzir uso de memória.
    """
    # Selecionar apenas as colunas necessárias para economizar memória
    colunas_necessarias = [eixo_x, eixo_y, 'TP_SEXO', 'TP_DEPENDENCIA_ADM_ESC']
    
    # Adicionar coluna de raça se o mapeamento estiver disponível
    if race_mapping:
        colunas_necessarias.append('TP_COR_RACA')
    
    # Adicionar coluna de faixa salarial se o filtro estiver definido
    if filtro_faixa_salarial is not None:
        colunas_necessarias.append('TP_FAIXA_SALARIAL')
    
    # Filtrar apenas as colunas necessárias
    df = dados[colunas_necessarias].copy()
    
    # Registrar tamanho inicial para reportar registros removidos
    tamanho_inicial = len(df)
    
    # Aplicar filtros em sequência
    if filtro_sexo:
        df = df[df['TP_SEXO'] == filtro_sexo]
    
    if filtro_tipo_escola == 'Pública':
        df = df[df['TP_DEPENDENCIA_ADM_ESC'].isin(['1', '2', '3'])]
    elif filtro_tipo_escola == 'Privada':
        df = df[df['TP_DEPENDENCIA_ADM_ESC'] == '4']
    
    # Filtrar por faixa salarial se especificado
    if filtro_faixa_salarial is not None:
        df = df[df['TP_FAIXA_SALARIAL'] == filtro_faixa_salarial]
    
    # Filtrar notas zero em um único passo para mais eficiência
    if excluir_notas_zero:
        df = df[(df[eixo_x] > 0) & (df[eixo_y] > 0)]
    
    # Remover valores NaN
    df = df.dropna(subset=[eixo_x, eixo_y])
    
    # Calcular registros removidos
    registros_removidos = tamanho_inicial - len(df)
    
    return df, registros_removidos


@optimized_cache()
def prepara_dados_grafico_linha_desempenho(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping, agrupar_por_regiao=False):
    """
    Prepara dados para o gráfico de linha que mostra o desempenho médio por estado ou região.
    Versão otimizada para usar menos memória e processamento mais eficiente.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os dados dos candidatos filtrados por estado
    estados_selecionados : list
        Lista de estados selecionados para análise
    colunas_notas : list
        Lista de colunas com notas a serem analisadas
    competencia_mapping : dict
        Dicionário de mapeamento de códigos de competência para nomes legíveis
    agrupar_por_regiao : bool, default=False
        Se True, agrupa os dados por região em vez de mostrar por estado
        
    Retorna:
    --------
    DataFrame: DataFrame com os dados preparados para visualização
    """
    # Pré-alocar listas para melhor performance
    dados_grafico = []
    
    # Processar um estado por vez para usar menos memória
    for estado in estados_selecionados:
        # Filtrar apenas para o estado atual
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        
        if len(dados_estado) == 0:
            continue  # Pular estados sem dados
            
        # Armazenar médias para calcular média geral depois
        medias_estado_atual = []
        
        # Calcular médias para cada área
        for area in colunas_notas:
            # Filtrar notas válidas (maiores que zero)
            dados_filtrados = dados_estado[dados_estado[area] > 0][area]
            
            if len(dados_filtrados) > 0:
                media_area = round(dados_filtrados.mean(), 2)
            else:
                media_area = 0.0
                
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
            
            # Adicionar média geral ao DataFrame de resultados
            dados_grafico.append({
                'Estado': estado,
                'Área': 'Média Geral',
                'Média': media_geral_estado
            })
    
    # Criar DataFrame otimizado com tipos de dados eficientes
    df_final = pd.DataFrame(dados_grafico)
    
    # Se não houver dados, retorna DataFrame vazio
    if df_final.empty:
        return df_final
    
    # Converter coluna Área para tipo categórico para economizar memória
    areas_unicas = list(competencia_mapping.values()) + ['Média Geral']
    df_final['Área'] = pd.Categorical(df_final['Área'], categories=areas_unicas)
    
    # Converter Estado para categórico
    df_final['Estado'] = pd.Categorical(df_final['Estado'], categories=estados_selecionados)
    
    # Agrupar por região se solicitado
    if agrupar_por_regiao:
        from utils.helpers.regiao_utils import agrupar_por_regiao as agrupar_regiao
        df_final = agrupar_regiao(df_final, coluna_estado='Estado', coluna_valores='Média')
        
        # Converter a coluna Estado para categórico novamente, agora com as regiões
        regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
        df_final['Estado'] = pd.Categorical(df_final['Estado'], categories=regioes)
    
    return df_final