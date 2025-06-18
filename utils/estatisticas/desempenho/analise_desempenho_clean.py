"""
Análise de desempenho refatorada seguindo princípios SOLID.
Implementa análises de performance usando arquitetura modular e analisadores especializados.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function

# Importar analisadores modulares
from .performance_analyzers import (
    PerformanceDataValidator, PerformanceResultBuilder,
    CorrelationCalculator, DescriptiveStatisticsCalculator,
    StatePerformanceAnalyzer, VariabilityAnalyzer, PercentileCalculator
)

# Constantes para compatibilidade
LIMITE_OUTLIER_SUPERIOR = 2.5
LIMITE_OUTLIER_INFERIOR = -2.5


@optimized_cache(ttl=1800)
def calcular_estatisticas_descritivas(df_notas: pd.DataFrame, coluna_nota: str) -> Dict[str, Any]:
    """
    Calcula estatísticas descritivas para uma competência.
    REFATORADO: Usa DescriptiveStatisticsCalculator modular.
    
    Parâmetros:
    -----------
    df_notas : DataFrame
        DataFrame com as notas dos candidatos
    coluna_nota : str
        Nome da coluna com a nota da competência
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com estatísticas descritivas
    """
    calculator = DescriptiveStatisticsCalculator()
    return calculator.calculate(df_notas, column=coluna_nota)


@memory_intensive_function
@optimized_cache(ttl=1800)
def analisar_correlacao_competencias(
    df_notas: pd.DataFrame, 
    colunas_competencias: List[str]
) -> Dict[str, Any]:
    """
    Analisa correlação entre competências.
    REFATORADO: Usa CorrelationCalculator modular.
    
    Parâmetros:
    -----------
    df_notas : DataFrame
        DataFrame com as notas
    colunas_competencias : List[str]
        Lista com nomes das colunas das competências
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com análise de correlação
    """
    calculator = CorrelationCalculator()
    return calculator.calculate(df_notas, columns=colunas_competencias)


@optimized_cache(ttl=1800)
def calcular_desempenho_por_estado(
    df_notas: pd.DataFrame, 
    estados_selecionados: List[str],
    colunas_competencias: List[str]
) -> Dict[str, Any]:
    """
    Calcula desempenho por estado.
    REFATORADO: Usa StatePerformanceAnalyzer modular.
    
    Parâmetros:
    -----------
    df_notas : DataFrame
        DataFrame com as notas
    estados_selecionados : List[str]
        Lista de estados para análise
    colunas_competencias : List[str]
        Lista das competências
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com desempenho por estado
    """
    analyzer = StatePerformanceAnalyzer()
    return analyzer.calculate(
        df_notas, 
        states=estados_selecionados, 
        competency_columns=colunas_competencias
    )


@optimized_cache(ttl=1800)
def calcular_percentis_competencias(
    df_notas: pd.DataFrame, 
    colunas_competencias: List[str],
    percentis: List[float] = [10, 25, 50, 75, 90]
) -> Dict[str, Any]:
    """
    Calcula percentis para competências.
    REFATORADO: Usa PercentileCalculator modular.
    
    Parâmetros:
    -----------
    df_notas : DataFrame
        DataFrame com as notas
    colunas_competencias : List[str]
        Lista das competências
    percentis : List[float]
        Lista de percentis para calcular
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com percentis por competência
    """
    calculator = PercentileCalculator()
    return calculator.calculate(df_notas, columns=colunas_competencias, percentiles=percentis)


@optimized_cache(ttl=1800)
def calcular_indicadores_desigualdade(
    df_resultados: pd.DataFrame, 
    coluna_categoria: str = 'Categoria',
    coluna_valor: str = 'Média'
) -> Dict[str, Any]:
    """
    Calcula indicadores de desigualdade usando analisadores modulares.
    REFATORADO: Usa VariabilityAnalyzer para cálculos especializados.
    
    Parâmetros:
    -----------
    df_resultados : DataFrame
        DataFrame com os dados por categoria
    coluna_categoria : str
        Nome da coluna com as categorias
    coluna_valor : str
        Nome da coluna com os valores
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com indicadores de desigualdade
    """
    analyzer = VariabilityAnalyzer()
    return analyzer.calculate(df_resultados, metric_column=coluna_valor)


@memory_intensive_function
def analisar_variabilidade_competencias(
    df_resultados: pd.DataFrame, 
    competencia: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analisa a variabilidade entre diferentes categorias para uma ou mais competências.
    REFATORADO: Usa VariabilityAnalyzer modular.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com os resultados por categoria e competência
    competencia: str, opcional
        Competência específica para análise. Se None, analisa todas.
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com medidas de variabilidade
    """
    analyzer = VariabilityAnalyzer()
    
    if competencia is not None:
        # Filtrar por competência específica
        df_filtered = df_resultados[df_resultados['Competência'] == competencia]
        return analyzer.calculate(df_filtered, metric_column='Média')
    else:
        # Analisar todas as competências
        return analyzer.calculate(df_resultados, metric_column='Média')


# Funções auxiliares para compatibilidade com código legado
def _criar_resultado_analise_vazio() -> Dict[str, Any]:
    """
    Cria um resultado de análise vazio para casos onde não há dados suficientes.
    MANTIDO: Para compatibilidade com código legado.
    """
    builder = StatePerformanceAnalyzer().result_builder
    return builder.build_empty_result()


def _criar_resultado_comparativo_vazio() -> Dict[str, Any]:
    """
    Cria um resultado comparativo vazio para casos onde não há dados suficientes.
    MANTIDO: Para compatibilidade com código legado.
    """
    builder = StatePerformanceAnalyzer().result_builder
    return builder.build_comparative_result({})


def _validar_dados_entrada(df_data: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Valida dados de entrada usando validador modular.
    REFATORADO: Usa PerformanceDataValidator.
    """
    validator = PerformanceDataValidator()
    return validator.validate(df_data) and validator.validate_columns(df_data, required_columns)
