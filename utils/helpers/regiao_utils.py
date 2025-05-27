import pandas as pd

def obter_mapa_regioes():
    """
    Retorna um dicionário de mapeamento de estados para regiões do Brasil.
    """
    return {
        'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 
        'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
    }

def agrupar_por_regiao(df, coluna_estado='Estado', coluna_valores='Média'):
    """
    Agrupa um DataFrame por região, baseado na coluna especificada para estados.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame contendo dados por estado
    coluna_estado : str
        Nome da coluna que contém os códigos dos estados
    coluna_valores : str
        Nome da coluna que contém os valores a serem agregados
        
    Retorna:
    --------
    DataFrame : DataFrame agrupado por região
    """
    # Criar uma cópia para evitar modificar o DataFrame original
    df_regioes = df.copy()
    
    # Mapear estados para regiões
    mapa_regioes = obter_mapa_regioes()
    df_regioes['Região'] = df_regioes[coluna_estado].map(mapa_regioes)
    
    # Agrupar os dados por região e outras colunas relevantes
    colunas_agrupamento = list(df_regioes.columns)
    colunas_agrupamento.remove(coluna_estado)
    colunas_agrupamento.remove(coluna_valores)
    colunas_agrupamento.remove('Região')
    
    # Criar lista de colunas para agrupar
    colunas_grupo = ['Região'] + colunas_agrupamento
    
    # Realizar o agrupamento e calcular a média
    df_agrupado = df_regioes.groupby(colunas_grupo)[coluna_valores].mean().reset_index()
    
    # Renomear coluna de região para manter compatibilidade com o restante do código
    df_agrupado = df_agrupado.rename(columns={'Região': coluna_estado})
    
    return df_agrupado