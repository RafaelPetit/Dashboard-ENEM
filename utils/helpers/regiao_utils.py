import pandas as pd
from typing import Dict, List, Any, Optional, Union

# Mapeamento constante de regiões do Brasil para uso em múltiplas funções
REGIOES_BRASIL = {
    'Norte': ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MS', 'MT'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC']
}

# Mapeamento inverso para uso eficiente
ESTADO_PARA_REGIAO = {estado: regiao for regiao, estados in REGIOES_BRASIL.items() for estado in estados}

def obter_mapa_regioes() -> Dict[str, str]:
    """
    Retorna um dicionário de mapeamento de estados para regiões do Brasil.
    
    Retorna:
    --------
    Dict[str, str]: Dicionário com siglas de estados como chaves e nomes de regiões como valores
    """
    return ESTADO_PARA_REGIAO


def agrupar_por_regiao(
    df: pd.DataFrame, 
    coluna_estado: str = 'Estado', 
    coluna_valores: str = 'Média'
) -> pd.DataFrame:
    """
    Agrupa um DataFrame por região, baseado na coluna especificada para estados.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame contendo dados por estado
    coluna_estado : str, default='Estado'
        Nome da coluna que contém os códigos dos estados
    coluna_valores : str, default='Média'
        Nome da coluna que contém os valores a serem agregados
        
    Retorna:
    --------
    DataFrame : DataFrame agrupado por região
    """
    # Verificar se temos dados para processar
    if df.empty:
        return pd.DataFrame(columns=df.columns)
        
    # Criar uma cópia para evitar modificar o DataFrame original
    df_regioes = df.copy()
    
    # Verificar se a coluna de estado existe
    if coluna_estado not in df_regioes.columns:
        raise ValueError(f"Coluna '{coluna_estado}' não encontrada no DataFrame")
    
    # Mapear estados para regiões
    df_regioes['Região'] = df_regioes[coluna_estado].map(ESTADO_PARA_REGIAO)
    
    # Verificar se todos os estados foram mapeados corretamente
    estados_nao_mapeados = df_regioes[df_regioes['Região'].isna()][coluna_estado].unique()
    if len(estados_nao_mapeados) > 0:
        print(f"Aviso: Os seguintes estados não foram mapeados para regiões: {estados_nao_mapeados}")
    
    # Identificar colunas para agrupamento (todas exceto estado, valores e região)
    colunas_para_remover = [coluna_estado, coluna_valores, 'Região']
    colunas_agrupamento = [col for col in df_regioes.columns if col not in colunas_para_remover]
    
    # Criar lista de colunas para agrupar
    colunas_grupo = ['Região'] + colunas_agrupamento
    
    # Realizar o agrupamento e calcular a média
    df_agrupado = df_regioes.groupby(colunas_grupo)[coluna_valores].mean().reset_index()
    
    # Renomear coluna de região para manter compatibilidade com o restante do código
    df_agrupado = df_agrupado.rename(columns={'Região': coluna_estado})
    
    return df_agrupado


def obter_estados_da_regiao(regiao: str) -> List[str]:
    """
    Retorna lista de estados que compõem uma região.
    
    Parâmetros:
    -----------
    regiao : str
        Nome da região (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)
        
    Retorna:
    --------
    List[str]: Lista com siglas dos estados da região, ou lista vazia se região inválida
    """
    return REGIOES_BRASIL.get(regiao, [])


def obter_regiao_do_estado(estado: str) -> str:
    """
    Retorna o nome da região a qual o estado pertence.
    
    Parâmetros:
    -----------
    estado : str
        Sigla do estado (ex: SP, RJ, MG)
        
    Retorna:
    --------
    str: Nome da região ou string vazia se estado inválido
    """
    return ESTADO_PARA_REGIAO.get(estado, "")


def obter_todas_regioes() -> List[str]:
    """
    Retorna lista com nomes de todas as regiões do Brasil.
    
    Retorna:
    --------
    List[str]: Lista de nomes das regiões
    """
    return list(REGIOES_BRASIL.keys())