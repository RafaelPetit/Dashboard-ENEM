import pandas as pd
from typing import Dict

def calcular_indicadores_desigualdade(
    df: pd.DataFrame, 
    coluna_categoria: str, 
    coluna_valor: str
) -> Dict[str, float]:
    """
    Calcula indicadores de desigualdade para uma variável categórica.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    coluna_categoria : str
        Coluna que contém as categorias
    coluna_valor : str
        Coluna que contém os valores a serem analisados
        
    Retorna:
    --------
    Dict[str, float]: Dicionário com indicadores de desigualdade:
        - razao_max_min: Razão entre valor máximo e mínimo
        - coef_variacao: Coeficiente de variação entre categorias
        - range_percentual: Amplitude percentual (max-min)/média
    """
    # Agrupar por categoria e calcular médias
    medias_por_categoria = df.groupby(coluna_categoria)[coluna_valor].mean()
    
    # Calcular indicadores
    min_valor = medias_por_categoria.min()
    max_valor = medias_por_categoria.max()
    media_geral = medias_por_categoria.mean()
    desvio_padrao = medias_por_categoria.std()
    
    # Criar dicionário de resultados
    resultados = {
        'razao_max_min': max_valor / min_valor if min_valor > 0 else float('inf'),
        'coef_variacao': (desvio_padrao / media_geral * 100) if media_geral > 0 else 0,
        'range_percentual': ((max_valor - min_valor) / media_geral * 100) if media_geral > 0 else 0
    }
    
    return resultados