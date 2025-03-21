import numpy as np
import pandas as pd
from utils.data_loader import calcular_seguro

def analisar_metricas_principais(microdados_estados, estados_selecionados, colunas_notas):
    """
    Calcula as métricas principais para a aba Geral.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os dados dos candidatos
    estados_selecionados : list
        Lista de estados selecionados para análise
    colunas_notas : list
        Lista de colunas com notas das competências
        
    Retorna:
    --------
    dict
        Dicionário com métricas calculadas
    """
    # Calcular médias por estado
    media_por_estado = []
    medias_estados = {}
    
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        medias_estado_atual = []       
        
        for col in colunas_notas:
            dados_validos = dados_estado[dados_estado[col] > 0][col]
            media = calcular_seguro(dados_validos)
            media_por_estado.append(media)
            medias_estado_atual.append(media)

        # Calcular média geral do estado (média de todas as competências)
        if medias_estado_atual:
            medias_estados[estado] = np.mean(medias_estado_atual)
    
    # Métricas gerais
    media_geral = np.mean(media_por_estado) if media_por_estado else 0.0
    
    # Encontrar o estado com a maior média
    estado_maior_media = "N/A"
    valor_maior_media_estado = 0.0
    if medias_estados:
        estado_maior_media, valor_maior_media_estado = max(medias_estados.items(), key=lambda x: x[1])
    
    # Maior média entre todas as áreas e estados
    maior_media = np.max(media_por_estado) if media_por_estado else 0.0
    
    # Total de candidatos
    total_candidatos = microdados_estados.shape[0]
    
    return {
        'media_geral': media_geral,
        'maior_media': maior_media,
        'estado_maior_media': estado_maior_media,
        'valor_maior_media_estado': valor_maior_media_estado,
        'total_candidatos': total_candidatos,
        'medias_estados': medias_estados
    }

def analisar_distribuicao_notas(df_dados, coluna):
    """
    Analisa a distribuição de notas para uma área específica.
    
    Parâmetros:
    -----------
    df_dados : DataFrame
        DataFrame com os dados filtrados
    coluna : str
        Nome da coluna a ser analisada
        
    Retorna:
    --------
    dict
        Dicionário com análises estatísticas
    """
    # Dados apenas para notas válidas (maiores que zero)
    df_valido = df_dados[df_dados[coluna] > 0]
    
    # Calcular estatísticas básicas
    media = calcular_seguro(df_valido[coluna])
    mediana = calcular_seguro(df_valido[coluna], 'mediana')
    min_valor = calcular_seguro(df_valido[coluna], 'min')
    max_valor = calcular_seguro(df_valido[coluna], 'max')
    desvio_padrao = calcular_seguro(df_valido[coluna], 'std')
    curtose = calcular_seguro(df_valido[coluna], 'curtose')
    assimetria = calcular_seguro(df_valido[coluna], 'assimetria')
    
    # Percentis
    percentis = {}
    for p in [10, 25, 50, 75, 90, 95, 99]:
        percentis[p] = np.percentile(df_valido[coluna], p)
    
    # Calcular faixas de desempenho
    faixas = {
        'Abaixo de 300': len(df_valido[df_valido[coluna] < 300]) / len(df_valido) * 100,
        '300 a 500': len(df_valido[(df_valido[coluna] >= 300) & (df_valido[coluna] < 500)]) / len(df_valido) * 100,
        '500 a 700': len(df_valido[(df_valido[coluna] >= 500) & (df_valido[coluna] < 700)]) / len(df_valido) * 100,
        '700 a 900': len(df_valido[(df_valido[coluna] >= 700) & (df_valido[coluna] < 900)]) / len(df_valido) * 100,
        '900 ou mais': len(df_valido[df_valido[coluna] >= 900]) / len(df_valido) * 100
    }
    
    # Análise de conceito (baseado em faixas típicas de nota do ENEM)
    conceitos = {
        'Insuficiente (abaixo de 450)': len(df_valido[df_valido[coluna] < 450]) / len(df_valido) * 100,
        'Regular (450 a 600)': len(df_valido[(df_valido[coluna] >= 450) & (df_valido[coluna] < 600)]) / len(df_valido) * 100,
        'Bom (600 a 750)': len(df_valido[(df_valido[coluna] >= 600) & (df_valido[coluna] < 750)]) / len(df_valido) * 100,
        'Muito bom (750 a 850)': len(df_valido[(df_valido[coluna] >= 750) & (df_valido[coluna] < 850)]) / len(df_valido) * 100,
        'Excelente (850 ou mais)': len(df_valido[df_valido[coluna] >= 850]) / len(df_valido) * 100
    }
    
    # Retornar análise completa
    return {
        'total_valido': len(df_valido),
        'total_invalido': len(df_dados) - len(df_valido),
        'media': media,
        'mediana': mediana,
        'min_valor': min_valor,
        'max_valor': max_valor,
        'desvio_padrao': desvio_padrao,
        'curtose': curtose,
        'assimetria': assimetria,
        'percentis': percentis,
        'faixas': faixas,
        'conceitos': conceitos
    }

def analisar_faltas(df_faltas):
    """
    Analisa padrões de faltas no ENEM.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame preparado com dados de faltas
        
    Retorna:
    --------
    dict
        Dicionário com análises sobre faltas
    """
    # DataFrame para análise geral
    df_geral = df_faltas[df_faltas['Área'] == 'Geral (qualquer prova)'].copy()
    
    # Taxa média geral de faltas
    taxa_media_geral = df_geral['Percentual de Faltas'].mean()
    
    # Estado com maior taxa de faltas
    estado_maior_falta = df_geral.loc[df_geral['Percentual de Faltas'].idxmax()]
    
    # Estado com menor taxa de faltas
    estado_menor_falta = df_geral.loc[df_geral['Percentual de Faltas'].idxmin()]
    
    # Calcular média de faltas por área
    medias_por_area = df_faltas.groupby('Área')['Percentual de Faltas'].mean().reset_index()
    
    # Área com maior média de faltas
    area_maior_falta = medias_por_area.loc[medias_por_area['Percentual de Faltas'].idxmax()]
    
    # Área com menor média de faltas
    area_menor_falta = medias_por_area.loc[medias_por_area['Percentual de Faltas'].idxmin()]
    
    # Combinação de estado e área com maior faltas
    max_combo = None
    max_falta_valor = 0
    
    for i, row in df_faltas.iterrows():
        if row['Percentual de Faltas'] > max_falta_valor:
            max_falta_valor = row['Percentual de Faltas']
            max_combo = (row['Estado'], row['Área'], row['Percentual de Faltas'])
    
    # Calcular média do primeiro e segundo dia
    areas_primeiro_dia = ['Ciências Humanas', 'Linguagens e Códigos']
    areas_segundo_dia = ['Ciências da Natureza', 'Matemática']
    
    df_dia1 = df_faltas[df_faltas['Área'].isin(areas_primeiro_dia)]
    df_dia2 = df_faltas[df_faltas['Área'].isin(areas_segundo_dia)]
    
    media_faltas_dia1 = df_dia1['Percentual de Faltas'].mean() if not df_dia1.empty else 0
    media_faltas_dia2 = df_dia2['Percentual de Faltas'].mean() if not df_dia2.empty else 0
    
    # Comparar faltas entre dias
    diferenca_dias = media_faltas_dia2 - media_faltas_dia1
    
    # Desvio padrão das faltas por estado
    desvio_padrao_faltas = df_geral['Percentual de Faltas'].std()
    
    # Análise da variabilidade de faltas por estado
    if desvio_padrao_faltas < 2:
        variabilidade = "Baixa variabilidade entre estados"
    elif desvio_padrao_faltas < 5:
        variabilidade = "Variabilidade moderada entre estados"
    else:
        variabilidade = "Alta variabilidade entre estados"
    
    # Retornar análise completa
    return {
        'taxa_media_geral': taxa_media_geral,
        'estado_maior_falta': estado_maior_falta,
        'estado_menor_falta': estado_menor_falta,
        'medias_por_area': medias_por_area,
        'area_maior_falta': area_maior_falta,
        'area_menor_falta': area_menor_falta,
        'max_combo': max_combo,
        'media_faltas_dia1': media_faltas_dia1,
        'media_faltas_dia2': media_faltas_dia2,
        'diferenca_dias': diferenca_dias,
        'desvio_padrao_faltas': desvio_padrao_faltas,
        'variabilidade': variabilidade
    }