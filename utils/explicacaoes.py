from utils.data_loader import calcular_seguro

def criar_explicacao_grafico_faltas(df_faltas, estados_selecionados):
    """
    Cria texto explicativo para o gráfico de faltas.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame com os dados de faltas
    estados_selecionados : lista
        Lista de estados selecionados para análise
        
    Retorna:
    --------
    str: Texto explicativo sobre os dados de faltas
    """
    # Filtrar apenas dados gerais para análise
    dados_gerais = df_faltas[df_faltas['Área'] == 'Geral (qualquer prova)']
    
    # Estado com maior e menor percentual de faltas
    estado_maior_falta = dados_gerais.loc[dados_gerais['Percentual de Faltas'].idxmax()]
    estado_menor_falta = dados_gerais.loc[dados_gerais['Percentual de Faltas'].idxmin()]
    
    # Média de faltas geral
    media_faltas_geral = dados_gerais['Percentual de Faltas'].mean()
    
    # Área de conhecimento com maior percentual de faltas
    grupo_por_area = df_faltas.groupby('Área')['Percentual de Faltas'].mean().reset_index()
    area_maior_falta = grupo_por_area.loc[grupo_por_area['Percentual de Faltas'].idxmax()]
    
    return f"""
        Este gráfico mostra o percentual de candidatos ausentes por estado e área de conhecimento.
        
        Entre os {len(estados_selecionados)} estados analisados, {estado_maior_falta['Estado']} apresenta o maior 
        percentual de faltas geral ({estado_maior_falta['Percentual de Faltas']:.1f}%), 
        enquanto {estado_menor_falta['Estado']} tem o menor percentual ({estado_menor_falta['Percentual de Faltas']:.1f}%).
        
        Em média, {media_faltas_geral:.1f}% dos candidatos faltaram em pelo menos uma prova.
        
        A área com maior índice de abstenção é {area_maior_falta['Área']}, 
        com média de {area_maior_falta['Percentual de Faltas']:.1f}% de candidatos ausentes.
    """

def criar_explicacao_grafico_linha(estados_selecionados, medias_estados, 
                                 microdados_estados, colunas_notas, competencia_mapping):
    """Cria texto explicativo para o gráfico de linha."""
    # Identificar melhor e pior estado
    melhor_estado = None
    pior_estado = None
    melhor_media = 0
    pior_media = float('inf')
    
    for estado, media_estado in medias_estados.items():
        if media_estado > melhor_media:
            melhor_media = media_estado
            melhor_estado = estado
        if media_estado < pior_media:
            pior_media = media_estado
            pior_estado = estado
    
    # Calcular médias por área de conhecimento
    medias_por_area = {}
    for col in colunas_notas:
        area_nome = competencia_mapping[col]
        medias_por_area[area_nome] = calcular_seguro(microdados_estados[col])
    
    # Encontrar área com melhor e pior desempenho
    melhor_area = max(medias_por_area.items(), key=lambda x: x[1])[0]
    melhor_media_area = medias_por_area[melhor_area]
    
    pior_area = min(medias_por_area.items(), key=lambda x: x[1])[0]
    pior_media_area = medias_por_area[pior_area]
    
    return f"""
        Este gráfico mostra as médias de desempenho por estado e área de conhecimento.
        
        Entre os {len(estados_selecionados)} estados analisados, {melhor_estado} apresenta a maior média geral ({melhor_media:.1f} pontos),
        enquanto {pior_estado} tem a menor média ({pior_media:.1f} pontos).
        
        A área com melhor desempenho médio é {melhor_area}, com média de {melhor_media_area:.1f} pontos.
        A área com menor desempenho médio é {pior_area}, com média de {pior_media_area:.1f} pontos.
    """

def criar_explicacao_histograma(df, coluna, nome_area, media, mediana, min_valor, max_valor):
    """Cria texto explicativo para o histograma."""
    import numpy as np
    
    candidatos_total = len(df)
    acima_media = len(df[df[coluna] > media])
    percentual_acima = (acima_media / candidatos_total * 100) if candidatos_total > 0 else 0
    
    # Definir bins com intervalos de 50 pontos (mais fácil de interpretar)
    # e garantir alinhamento com o gráfico visual
    bin_size = 50
    bin_edges = np.arange(0, 1001, bin_size)  # 0, 50, 100, ... 1000
    
    # Calcular o histograma com esses bins específicos
    hist, _ = np.histogram(df[coluna].dropna(), bins=bin_edges)
    
    # Encontrar o bin com maior contagem
    idx_max_count = np.argmax(hist)
    
    # Determinando a faixa mais comum
    inicio_faixa = bin_edges[idx_max_count]
    fim_faixa = bin_edges[idx_max_count + 1]
    
    # Para debugging (opcional)
    # Uncomment to debug:
    # print(f"Bins: {list(zip(bin_edges[:-1], bin_edges[1:]))}")
    # print(f"Counts: {hist}")
    # print(f"Max idx: {idx_max_count}, Range: {inicio_faixa}-{fim_faixa}")
    
    # Determinar a tendência da distribuição
    if media > mediana:
        tendencia = "A distribuição apresenta um viés para notas mais altas."
    elif media < mediana:
        tendencia = "A distribuição apresenta um viés para notas mais baixas."
    else:
        tendencia = "A distribuição é aproximadamente simétrica."
    
    return f"""
        Este histograma mostra a distribuição das notas de {nome_area}.
        A média é {media:.2f} e a mediana é {mediana:.2f}, com notas variando de {min_valor:.1f} a {max_valor:.1f}.
        
        {acima_media:,} candidatos ({percentual_acima:.1f}%) obtiveram notas acima da média.
        A faixa de notas mais comum está entre {int(inicio_faixa)} e {int(fim_faixa)} pontos.
        
        {tendencia}
    """