"""
Definições de tipos customizados e protocolos para o módulo de dados.
Estabelece contratos claros entre os componentes.
"""

from typing import Protocol, Dict, List, Union, Optional
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


# Tipos customizados
DataFrameType = pd.DataFrame
SeriesType = pd.Series
ArrayLike = Union[SeriesType, np.ndarray, List]
StatisticResult = Union[float, int]


class DataLoader(Protocol):
    """Protocolo para carregadores de dados."""
    
    def load(self, **kwargs) -> DataFrameType:
        """Carrega dados conforme os parâmetros especificados."""
        ...
    
    def validate_source(self) -> bool:
        """Valida se a fonte de dados está acessível."""
        ...


class DataProcessor(Protocol):
    """Protocolo para processadores de dados."""
    
    def process(self, data: DataFrameType, **kwargs) -> DataFrameType:
        """Processa os dados conforme os parâmetros especificados."""
        ...


class DataOptimizer(Protocol):
    """Protocolo para otimizadores de dados."""
    
    def optimize(self, data: DataFrameType) -> DataFrameType:
        """Otimiza o DataFrame para uso eficiente de memória."""
        ...


class StatisticsCalculator(Protocol):
    """Protocolo para calculadores de estatísticas."""
    
    def calculate(self, data: ArrayLike, operation: str) -> StatisticResult:
        """Calcula estatística específica nos dados."""
        ...


class MemoryManager(Protocol):
    """Protocolo para gerenciamento de memória."""
    
    def release(self, objects: Union[object, List[object]]) -> None:
        """Libera objetos da memória."""
        ...
    
    def force_gc(self) -> None:
        """Força coleta de lixo."""
        ...
