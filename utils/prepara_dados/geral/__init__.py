"""
Arquivo __init__.py para o módulo geral.
Fornece interface unificada para processamento de dados gerais.
"""

from .processors import (
    HistogramDataProcessor,
    AttendanceAnalysisProcessor,
    MainMetricsProcessor,
    StateAverageProcessor,
    ComparativeAnalysisProcessor
)

__all__ = [
    'HistogramDataProcessor',
    'AttendanceAnalysisProcessor', 
    'MainMetricsProcessor',
    'StateAverageProcessor',
    'ComparativeAnalysisProcessor'
]
