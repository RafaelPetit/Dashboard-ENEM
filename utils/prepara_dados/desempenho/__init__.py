"""
Módulo para preparação de dados de desempenho do ENEM.

Este subpacote contém classes especializadas para processamento e análise
de dados de desempenho dos candidatos, incluindo análises comparativas,
distribuições de notas, e correlações entre competências.

Classes principais:
- ComparativePerformanceProcessor: Análise comparativa de desempenho
- PerformanceDistributionProcessor: Distribuição de notas e competências
- StatePerformanceProcessor: Análise de desempenho por estado/região
- ScatterAnalysisProcessor: Análise de correlação entre competências
"""

# Importar processadores principais
from .processors import (
    ComparativePerformanceProcessor,
    PerformanceDistributionProcessor,
    StatePerformanceProcessor,
    ScatterAnalysisProcessor
)

# Importar gerenciador de dados
from .data_manager import PerformanceDataManager, prepare_performance_data

__all__ = [
    'ComparativePerformanceProcessor',
    'PerformanceDistributionProcessor',
    'StatePerformanceProcessor', 
    'ScatterAnalysisProcessor',
    'PerformanceDataManager',
    'prepare_performance_data'
]
