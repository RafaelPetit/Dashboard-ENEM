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
    
    # Valores padrão caso não haja dados
    estado_maior_media = "N/A"
    estado_menor_media = "N/A"
    valor_maior_media_estado = 0.0
    valor_menor_media_estado = 0.0
    
    # Encontrar o estado com a maior e menor média
    if medias_estados:
        estado_maior_media, valor_maior_media_estado = max(medias_estados.items(), key=lambda x: x[1])
        estado_menor_media, valor_menor_media_estado = min(medias_estados.items(), key=lambda x: x[1])
    
    # Maior média entre todas as áreas e estados
    maior_media = np.max(media_por_estado) if media_por_estado else 0.0
    menor_media = np.min([m for m in media_por_estado if m > 0]) if media_por_estado else 0.0
    
    # Total de candidatos
    total_candidatos = microdados_estados.shape[0]
    
    return {
        'media_geral': media_geral,
        'maior_media': maior_media,
        'menor_media': menor_media,
        'estado_maior_media': estado_maior_media,
        'estado_menor_media': estado_menor_media,
        'valor_maior_media_estado': valor_maior_media_estado,
        'valor_menor_media_estado': valor_menor_media_estado,
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
    Analisa padrões de faltas no ENEM com base nos dias de ausência.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame preparado com dados de faltas
        
    Retorna:
    --------
    dict
        Dicionário com análises sobre faltas
    """
    # Filtrar para tipos específicos de falta
    df_ambos_dias = df_faltas[df_faltas['Tipo de Falta'].str.contains('Faltou nos dois dias')].copy()
    df_dia1 = df_faltas[df_faltas['Tipo de Falta'].str.contains('Faltou apenas no primeiro dia')].copy()
    df_dia2 = df_faltas[df_faltas['Tipo de Falta'].str.contains('Faltou apenas no segundo dia')].copy()
    
    # Calcular médias por tipo de falta
    media_faltas_ambos_dias = df_ambos_dias['Percentual de Faltas'].mean() if not df_ambos_dias.empty else 0
    media_faltas_dia1 = df_dia1['Percentual de Faltas'].mean() if not df_dia1.empty else 0
    media_faltas_dia2 = df_dia2['Percentual de Faltas'].mean() if not df_dia2.empty else 0
    
    # Calcular taxa média geral (soma das três médias)
    taxa_media_geral = media_faltas_ambos_dias + media_faltas_dia1 + media_faltas_dia2
    
    # Estado com maior taxa de faltas em ambos os dias
    estado_maior_falta = None
    estado_menor_falta = None
    
    if not df_ambos_dias.empty:
        estado_maior_falta = df_ambos_dias.loc[df_ambos_dias['Percentual de Faltas'].idxmax()]
    
    # Estado com menor taxa de faltas em ambos os dias
    if not df_ambos_dias.empty:
        estado_menor_falta = df_ambos_dias.loc[df_ambos_dias['Percentual de Faltas'].idxmin()]
    
    # Tipo de falta mais comum (média mais alta)
    tipo_mais_comum = 'Ambos os dias'
    maior_media = media_faltas_ambos_dias
    
    if media_faltas_dia1 > maior_media:
        tipo_mais_comum = 'Apenas o primeiro dia'
        maior_media = media_faltas_dia1
    
    if media_faltas_dia2 > maior_media:
        tipo_mais_comum = 'Apenas o segundo dia'
        maior_media = media_faltas_dia2
    
    # Criar DataFrame com médias por tipo
    medias_por_tipo = pd.DataFrame({
        'Tipo de Falta': ['Faltou nos dois dias', 'Faltou apenas no primeiro dia', 'Faltou apenas no segundo dia'],
        'Percentual de Faltas': [media_faltas_ambos_dias, media_faltas_dia1, media_faltas_dia2]
    })
    
    # Desvio padrão das faltas por estado (para os dois dias)
    desvio_padrao_faltas = df_ambos_dias['Percentual de Faltas'].std() if not df_ambos_dias.empty else 0
    
    # Análise da variabilidade de faltas por estado
    if desvio_padrao_faltas < 2:
        variabilidade = "Baixa variabilidade entre estados"
    elif desvio_padrao_faltas < 5:
        variabilidade = "Variabilidade moderada entre estados"
    else:
        variabilidade = "Alta variabilidade entre estados"
    
    # Diferença entre faltas no primeiro e segundo dia
    diferenca_dias = media_faltas_dia2 - media_faltas_dia1
    
    # Retornar análise completa
    return {
        'taxa_media_geral': taxa_media_geral,
        'estado_maior_falta': estado_maior_falta,
        'estado_menor_falta': estado_menor_falta,
        'medias_por_tipo': medias_por_tipo,
        'tipo_mais_comum': tipo_mais_comum,
        'media_faltas_ambos_dias': media_faltas_ambos_dias,
        'media_faltas_dia1': media_faltas_dia1,
        'media_faltas_dia2': media_faltas_dia2,
        'diferenca_dias': diferenca_dias,
        'desvio_padrao_faltas': desvio_padrao_faltas,
        'variabilidade': variabilidade
    }