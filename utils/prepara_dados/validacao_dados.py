import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple

def validar_completude_dados(
    df: pd.DataFrame, 
    colunas_requeridas: List[str], 
    limiar_completude: float = 0.7
) -> Tuple[bool, Dict[str, float]]:
    """
    Verifica se o DataFrame tem dados suficientes nas colunas requeridas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame a ser validado
    colunas_requeridas : List[str]
        Lista de colunas que precisam estar presentes e com dados suficientes
    limiar_completude : float, default=0.7
        Proporção mínima de valores não-nulos para considerar uma coluna válida
        
    Retorna:
    --------
    Tuple[bool, Dict[str, float]]: 
        - Booleano indicando se todas as colunas têm dados suficientes
        - Dicionário com taxas de completude por coluna
    """
    # Verificar se o DataFrame existe e não está vazio
    if df is None or df.empty:
        return False, {col: 0.0 for col in colunas_requeridas}
    
    # Verificar se todas as colunas existem
    colunas_ausentes = [col for col in colunas_requeridas if col not in df.columns]
    if colunas_ausentes:
        taxas = {col: 0.0 if col in colunas_ausentes else 1.0 for col in colunas_requeridas}
        return False, taxas
    
    # Calcular taxas de completude
    taxas_completude = {}
    for coluna in colunas_requeridas:
        taxa = 1.0 - (df[coluna].isna().sum() / len(df))
        taxas_completude[coluna] = taxa
    
    # Verificar se todas atendem ao limiar
    todas_validas = all(taxa >= limiar_completude for taxa in taxas_completude.values())
    
    return todas_validas, taxas_completude


def verificar_outliers(
    df: pd.DataFrame,
    colunas_numericas: List[str],
    metodo: str = 'iqr',
    limiar: float = 1.5
) -> Dict[str, Dict[str, Any]]:
    """
    Verifica a presença de outliers em colunas numéricas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame a ser analisado
    colunas_numericas : List[str]
        Lista de colunas numéricas para verificar outliers
    metodo : str, default='iqr'
        Método para detecção de outliers ('iqr' ou 'zscore')
    limiar : float, default=1.5
        Limiar para considerar valor como outlier (1.5 para IQR, 3.0 para Z-score)
        
    Retorna:
    --------
    Dict[str, Dict[str, Any]]: Dicionário com resultados por coluna:
        - quantidade: número de outliers
        - percentual: percentual de outliers
        - limites: limites inferior e superior
    """
    resultados = {}
    
    # Verificar se o DataFrame existe e não está vazio
    if df is None or df.empty:
        return {col: {'quantidade': 0, 'percentual': 0, 'limites': (0, 0)} for col in colunas_numericas}
    
    # Processar cada coluna
    for coluna in colunas_numericas:
        if coluna not in df.columns:
            resultados[coluna] = {'quantidade': 0, 'percentual': 0, 'limites': (0, 0)}
            continue
        
        # Obter série de dados sem valores nulos
        serie = df[coluna].dropna()
        
        if serie.empty:
            resultados[coluna] = {'quantidade': 0, 'percentual': 0, 'limites': (0, 0)}
            continue
        
        # Detectar outliers baseado no método escolhido
        if metodo == 'iqr':
            q1 = serie.quantile(0.25)
            q3 = serie.quantile(0.75)
            iqr = q3 - q1
            
            limite_inferior = q1 - limiar * iqr
            limite_superior = q3 + limiar * iqr
            
            outliers = serie[(serie < limite_inferior) | (serie > limite_superior)]
            
        elif metodo == 'zscore':
            media = serie.mean()
            desvio = serie.std()
            
            if desvio == 0:  # Evitar divisão por zero
                outliers = pd.Series([])
            else:
                z_scores = np.abs((serie - media) / desvio)
                outliers = serie[z_scores > limiar]
        else:
            raise ValueError(f"Método de detecção de outliers '{metodo}' não suportado")
        
        # Armazenar resultados
        resultados[coluna] = {
            'quantidade': len(outliers),
            'percentual': len(outliers) / len(serie) if len(serie) > 0 else 0,
            'limites': (limite_inferior, limite_superior) if metodo == 'iqr' else None
        }
    
    return resultados


def validar_distribuicao_dados(
    df: pd.DataFrame,
    colunas_numericas: List[str],
    min_valores_unicos: int = 5
) -> Dict[str, Dict[str, Any]]:
    """
    Valida a distribuição de dados em colunas numéricas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame a ser analisado
    colunas_numericas : List[str]
        Lista de colunas numéricas para analisar
    min_valores_unicos : int, default=5
        Número mínimo de valores únicos para considerar coluna válida
        
    Retorna:
    --------
    Dict[str, Dict[str, Any]]: Dicionário com resultados por coluna:
        - valida: booleano indicando se a distribuição é válida
        - valores_unicos: número de valores únicos
        - normalidade: p-valor do teste de normalidade
        - eh_normal: booleano indicando se distribuição é normal
    """
    from scipy import stats
    
    resultados = {}
    
    # Verificar se o DataFrame existe e não está vazio
    if df is None or df.empty:
        return {col: {'valida': False, 'valores_unicos': 0} for col in colunas_numericas}
    
    # Processar cada coluna
    for coluna in colunas_numericas:
        if coluna not in df.columns:
            resultados[coluna] = {'valida': False, 'valores_unicos': 0}
            continue
        
        # Obter série de dados sem valores nulos
        serie = df[coluna].dropna()
        
        if serie.empty:
            resultados[coluna] = {'valida': False, 'valores_unicos': 0}
            continue
        
        # Contar valores únicos
        valores_unicos = serie.nunique()
        
        # Verificar se temos valores únicos suficientes
        valida = valores_unicos >= min_valores_unicos
        
        # Resultados básicos
        resultado = {
            'valida': valida,
            'valores_unicos': valores_unicos
        }
        
        # Testar normalidade se tivermos pelo menos 20 observações
        if len(serie) >= 20:
            try:
                # Teste de Shapiro-Wilk (para amostras menores)
                if len(serie) < 5000:
                    stat, p_valor = stats.shapiro(serie.sample(min(len(serie), 5000)))
                # Teste de Kolmogorov-Smirnov (para amostras maiores)
                else:
                    stat, p_valor = stats.kstest(serie, 'norm')
                
                resultado['normalidade'] = p_valor
                resultado['eh_normal'] = p_valor > 0.05
            except Exception:
                resultado['normalidade'] = None
                resultado['eh_normal'] = None
        
        resultados[coluna] = resultado
    
    return resultados