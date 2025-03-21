import pandas as pd
import numpy as np

def calcular_correlacao_competencias(df, eixo_x, eixo_y):
    """
    Calcula a correlação entre duas competências.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame contendo os dados
    eixo_x: str
        Nome da coluna para o primeiro eixo
    eixo_y: str
        Nome da coluna para o segundo eixo
        
    Retorna:
    --------
    tuple: (coeficiente de correlação, interpretação da correlação)
    """
    # Calcular correlação
    correlacao = df[eixo_x].corr(df[eixo_y])
    
    # Interpretar valor de correlação
    if abs(correlacao) < 0.3:
        interpretacao = "Fraca"
    elif abs(correlacao) < 0.7:
        interpretacao = "Moderada"
    else:
        interpretacao = "Forte"
        
    if correlacao > 0:
        interpretacao += " positiva"
    elif correlacao < 0:
        interpretacao += " negativa"
    else:
        interpretacao = "Ausente"
    
    return correlacao, interpretacao


def gerar_estatisticas_descritivas(df, coluna):
    """
    Gera estatísticas descritivas para uma coluna.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame contendo os dados
    coluna: str
        Nome da coluna para análise
        
    Retorna:
    --------
    Series: Estatísticas descritivas
    """
    return df[coluna].describe().round(2)


def analisar_desempenho_por_estado(df_grafico, area_selecionada=None):
    """
    Analisa o desempenho por estado, identificando estados com melhor e pior desempenho.
    
    Parâmetros:
    -----------
    df_grafico: DataFrame
        DataFrame com dados do gráfico de linha
    area_selecionada: str, opcional
        Área específica para análise, se fornecida
        
    Retorna:
    --------
    dict: Dicionário com resultados da análise
    """
    if area_selecionada:
        df_analise = df_grafico[df_grafico['Área'] == area_selecionada]
    else:
        df_analise = df_grafico[df_grafico['Área'] == 'Média Geral']
    
    melhor_estado = df_analise.loc[df_analise['Média'].idxmax()]
    pior_estado = df_analise.loc[df_analise['Média'].idxmin()]
    media_geral = df_analise['Média'].mean()
    desvio_padrao = df_analise['Média'].std()
    
    return {
        'melhor_estado': melhor_estado,
        'pior_estado': pior_estado,
        'media_geral': media_geral,
        'desvio_padrao': desvio_padrao
    }