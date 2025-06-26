import pandas as pd
from typing import Dict, List, Any, Optional, Union

# Mapeamento constante de regiões do Brasil para uso em múltiplas funções
# SUDESTE REMOVIDO - dados já filtrados no dataset
REGIOES_BRASIL = {
    'Norte': ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MS', 'MT'],
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
    Retorna o DataFrame com a coluna de Região já existente, sem recriar.
    Assume que o dataset já possui uma coluna 'Regiao' criada anteriormente.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame contendo dados por estado com coluna 'Regiao' já existente
    coluna_estado : str, default='Estado'
        Nome da coluna que contém os códigos dos estados (mantido para compatibilidade)
    coluna_valores : str, default='Média'
        Nome da coluna que contém os valores (mantido para compatibilidade)
        
    Retorna:
    --------
    DataFrame : DataFrame original com coluna 'Regiao' já existente
    """
    # Verificar se temos dados para processar
    if df.empty:
        return df
    
    # Verificar se a coluna Regiao já existe no DataFrame
    if 'Regiao' in df.columns:
        # Retornar o DataFrame original, pois a coluna Regiao já existe
        return df
    else:
        # Fallback: se por algum motivo a coluna não existir, criar usando o mapeamento
        # (mantendo compatibilidade com datasets antigos)
        df_com_regiao = df.copy()
        if coluna_estado in df_com_regiao.columns:
            df_com_regiao['SG_REGIAO'] = df_com_regiao[coluna_estado].map(ESTADO_PARA_REGIAO)
        return df_com_regiao


def obter_estados_da_regiao(regiao: str) -> List[str]:
    """
    Retorna lista de estados que compõem uma região.
    
    Parâmetros:
    -----------
    regiao : str
        Nome da região (Norte, Nordeste, Centro-Oeste, Sul)
        
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