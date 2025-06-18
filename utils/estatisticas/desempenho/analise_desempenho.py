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


# Função adicional para compatibilidade completa
@optimized_cache(ttl=1800)
def calcular_correlacao_competencias(
    df_notas: pd.DataFrame, 
    competencia_x: str = None,
    competencia_y: str = None,
    colunas_competencias: List[str] = None
) -> Union[Dict[str, Any], Tuple[float, str]]:
    """
    Calcula correlação entre competências (alias para compatibilidade).
    
    Suporta duas formas de chamada:
    1. Com lista de competências: calcular_correlacao_competencias(df, colunas_list)
    2. Com competências individuais: calcular_correlacao_competencias(df, comp_x, comp_y)
    """
    # Se apenas dois argumentos foram passados e o segundo é uma lista
    if colunas_competencias is None and isinstance(competencia_x, list):
        colunas_competencias = competencia_x
        return analisar_correlacao_competencias(df_notas, colunas_competencias)
    
    # Se foram passados argumentos de competências individuais
    if competencia_x is not None and competencia_y is not None:
        # Análise específica entre duas competências
        import numpy as np
        
        if competencia_x not in df_notas.columns or competencia_y not in df_notas.columns:
            return 0.0, "Colunas não encontradas"
        
        # Remover valores inválidos
        dados_limpos = df_notas[[competencia_x, competencia_y]].dropna()
        dados_limpos = dados_limpos[(dados_limpos[competencia_x] > 0) & (dados_limpos[competencia_y] > 0)]
        
        if len(dados_limpos) < 2:
            return 0.0, "Dados insuficientes"
        
        # Calcular correlação de Pearson
        correlacao = dados_limpos[competencia_x].corr(dados_limpos[competencia_y])
        
        # Interpretar correlação
        if abs(correlacao) >= 0.8:
            interpretacao = f"Correlação muito forte ({correlacao:.3f})"
        elif abs(correlacao) >= 0.6:
            interpretacao = f"Correlação forte ({correlacao:.3f})"
        elif abs(correlacao) >= 0.4:
            interpretacao = f"Correlação moderada ({correlacao:.3f})"
        elif abs(correlacao) >= 0.2:
            interpretacao = f"Correlação fraca ({correlacao:.3f})"
        else:
            interpretacao = f"Correlação muito fraca ({correlacao:.3f})"
            
        return correlacao, interpretacao
    
    # Fallback para lista de competências
    if colunas_competencias is not None:
        return analisar_correlacao_competencias(df_notas, colunas_competencias)
        
    return 0.0, "Argumentos inválidos"


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


@optimized_cache(ttl=1800)
def calcular_estatisticas_comparativas(
    df_resultados: pd.DataFrame, 
    competencias: List[str]
) -> Dict[str, Any]:
    """
    Calcula estatísticas comparativas entre competências e categorias.
    REFATORADO: Usa StatePerformanceAnalyzer modular.
    
    Parâmetros:
    -----------
    df_resultados : DataFrame
        DataFrame com resultados por categoria
    competencias : List[str]
        Lista das competências para análise
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com estatísticas comparativas
    """
    analyzer = StatePerformanceAnalyzer()
    return analyzer.calculate_comparative_stats(df_resultados, competencies=competencias)


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


# Função adicional para compatibilidade completa
@optimized_cache(ttl=1800)
def gerar_estatisticas_descritivas(
    df_notas: pd.DataFrame, 
    coluna_nota: str
) -> Dict[str, Any]:
    """
    Gera estatísticas descritivas (alias para compatibilidade).
    """
    return calcular_estatisticas_descritivas(df_notas, coluna_nota)


# Função adicional para compatibilidade completa
@optimized_cache(ttl=1800)
def analisar_desempenho_por_estado(
    df_notas: pd.DataFrame, 
    area_ou_estados: Union[str, List[str]] = None,
    colunas_competencias: List[str] = None
) -> Dict[str, Any]:
    """
    Analisa desempenho por estado (versão flexível para compatibilidade).
    
    Suporta duas formas de chamada:
    1. Com área específica: analisar_desempenho_por_estado(df, "Média Geral")
    2. Com lista de estados: analisar_desempenho_por_estado(df, estados_list, colunas_list)
    """
    print(f"[DEBUG] analisar_desempenho_por_estado chamada")
    print(f"[DEBUG] df_notas shape: {df_notas.shape if df_notas is not None else 'None'}")
    print(f"[DEBUG] df_notas columns: {list(df_notas.columns) if df_notas is not None else 'None'}")
    print(f"[DEBUG] area_ou_estados: {area_ou_estados}")
    print(f"[DEBUG] colunas_competencias: {colunas_competencias}")
    
    # Se apenas 2 argumentos e o segundo é string (área de análise)
    if isinstance(area_ou_estados, str) and colunas_competencias is None:
        # Análise por área específica
        area_analise = area_ou_estados
        print(f"[DEBUG] Análise por área específica: {area_analise}")
        
        # Verificar se temos a coluna de estado - tentar várias opções
        coluna_estado = None
        for col_possivel in ['SG_UF_RESIDENCIA', 'SG_UF_PROVA', 'Estado', 'UF']:
            if col_possivel in df_notas.columns:
                coluna_estado = col_possivel
                break
        if coluna_estado is None:
            print(f"[DEBUG] Nenhuma coluna de estado encontrada")
            return _criar_resultado_analise_vazio()
        
        print(f"[DEBUG] Usando coluna de estado: {coluna_estado}")
        
        # Verificar se temos a coluna da área - tentar várias opções
        coluna_area = None
        
        # Debug: mostrar valores únicos na coluna Área
        if 'Área' in df_notas.columns:
            print(f"[DEBUG] Valores únicos na coluna 'Área': {sorted(df_notas['Área'].unique())}")
        
        if area_analise in df_notas.columns:
            coluna_area = area_analise
        elif area_analise == "Média Geral" and 'Media' in df_notas.columns:
            coluna_area = 'Media'
        elif area_analise == "Média Geral" and 'Média' in df_notas.columns:
            coluna_area = 'Média'
        elif area_analise == "Média Geral" and 'Área' in df_notas.columns:
            # Para DataFrame agregado, precisa filtrar pela área "Média Geral"
            df_area_filtrado = df_notas[df_notas['Área'] == 'Média Geral'].copy()
            if not df_area_filtrado.empty:
                print(f"[DEBUG] Filtrando para área 'Média Geral', registros encontrados: {len(df_area_filtrado)}")
                # Usar a coluna 'Média' como valor
                coluna_area = 'Média'
                df_notas = df_area_filtrado
            else:
                print(f"[DEBUG] Nenhum registro encontrado para área 'Média Geral'")
        elif 'Área' in df_notas.columns and area_analise in df_notas['Área'].unique():
            # DataFrame agregado - filtrar pela área específica
            df_area_filtrado = df_notas[df_notas['Área'] == area_analise].copy()
            if not df_area_filtrado.empty:
                print(f"[DEBUG] Filtrando para área '{area_analise}', registros encontrados: {len(df_area_filtrado)}")
                coluna_area = 'Média'
                df_notas = df_area_filtrado
            else:
                print(f"[DEBUG] Nenhum registro encontrado para área '{area_analise}'")
        
        if coluna_area is None:
            print(f"[DEBUG] Coluna da área '{area_analise}' não encontrada")
            return _criar_resultado_analise_vazio()
        
        print(f"[DEBUG] Usando coluna de área: {coluna_area}")
        
        # Calcular estatísticas por estado para a área específica
        estados_stats = df_notas.groupby(coluna_estado)[coluna_area].agg([
            'mean', 'median', 'std', 'count'
        ]).round(2)
        
        print(f"[DEBUG] Estados stats shape: {estados_stats.shape}")
        print(f"[DEBUG] Estados stats head: {estados_stats.head()}")
        
        if estados_stats.empty:
            print(f"[DEBUG] Estados stats vazio")
            return _criar_resultado_analise_vazio()
        
        # Encontrar melhor e pior estado
        melhor_idx = estados_stats['mean'].idxmax()
        pior_idx = estados_stats['mean'].idxmin()
        
        melhor_estado = {
            'Estado': melhor_idx,
            'Média': estados_stats.loc[melhor_idx, 'mean'],
            'Mediana': estados_stats.loc[melhor_idx, 'median']
        }
        
        pior_estado = {
            'Estado': pior_idx,
            'Média': estados_stats.loc[pior_idx, 'mean'], 
            'Mediana': estados_stats.loc[pior_idx, 'median']
        }
        
        media_geral = round(estados_stats['mean'].mean(), 2)
        desvio_padrao = round(estados_stats['mean'].std(), 2)
        coef_variacao = round((desvio_padrao / media_geral * 100), 2) if media_geral > 0 else 0
        
        print(f"[DEBUG] Resultado calculado - média geral: {media_geral}, desvio: {desvio_padrao}")
        
        return {
            'melhor_estado': melhor_estado,
            'pior_estado': pior_estado,
            'desvio_padrao': desvio_padrao,
            'media_geral': media_geral,
            'coef_variacao': coef_variacao,
            'amplitude': round((estados_stats['mean'].max() - estados_stats['mean'].min()), 2),
            'estados_stats': estados_stats.to_dict('index'),
            'area_analisada': area_analise,
            'total_estados': len(estados_stats)
        }
    
    # Chamada tradicional com estados e competências
    elif isinstance(area_ou_estados, list) and colunas_competencias is not None:
        return calcular_desempenho_por_estado(df_notas, area_ou_estados, colunas_competencias)
    
    # Fallback
    return _criar_resultado_analise_vazio()


# Função adicional para compatibilidade completa
@optimized_cache(ttl=1800)
def calcular_percentis_desempenho(
    df_notas: pd.DataFrame, 
    colunas_competencias: List[str],
    percentis: List[float] = [10, 25, 50, 75, 90]
) -> Dict[str, Any]:
    """
    Calcula percentis de desempenho (alias para compatibilidade).
    """
    return calcular_percentis_competencias(df_notas, colunas_competencias, percentis)


@memory_intensive_function
def analisar_variabilidade_entre_categorias(
    df_resultados: pd.DataFrame, 
    competencia: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analisa variabilidade entre categorias (alias para compatibilidade).
    """
    return analisar_variabilidade_competencias(df_resultados, competencia)
