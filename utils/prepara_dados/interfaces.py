"""
Interfaces e contratos para o módulo prepara_dados.
Define abstrações para garantir baixo acoplamento e alta coesão.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, List, Any, Optional, Union, TypeVar, Generic
import pandas as pd

# Type variables para genericidade
T = TypeVar('T')
DataFrameType = Union[pd.DataFrame, pd.Series]


class DataValidator(Protocol):
    """Protocol para validação de dados."""
    
    def validate(self, data: DataFrameType, required_columns: List[str]) -> bool:
        """Valida se os dados atendem aos requisitos."""
        ...


class CacheManager(Protocol):
    """Protocol para gestão de cache."""
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera item do cache."""
        ...
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Armazena item no cache."""
        ...
    
    def clear(self, pattern: Optional[str] = None) -> None:
        """Limpa cache por padrão."""
        ...


class MemoryManager(Protocol):
    """Protocol para gestão de memória."""
    
    def release(self) -> None:
        """Libera memória não utilizada."""
        ...
    
    def optimize_dtypes(self, df: DataFrameType) -> DataFrameType:
        """Otimiza tipos de dados para economizar memória."""
        ...


class StateProcessor(ABC, Generic[T]):
    """Interface abstrata para processadores de dados por estado."""
    
    @abstractmethod
    def process_single_state(self, data: DataFrameType, state: str, **kwargs) -> T:
        """
        Processa dados de um único estado.
        
        Args:
            data: Dados do estado
            state: Código do estado
            **kwargs: Argumentos específicos
            
        Returns:
            Resultado processado para o estado
        """
        pass
    
    @abstractmethod
    def aggregate_results(self, results: List[T]) -> Any:
        """
        Agrega resultados de múltiplos estados.
        
        Args:
            results: Lista de resultados por estado
            
        Returns:
            Resultado agregado
        """
        pass


class RegionAggregator(ABC):
    """Interface para agregação por regiões."""
    
    @abstractmethod
    def group_by_region(self, state_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Agrupa dados de estados por região.
        
        Args:
            state_data: Dados por estado
            
        Returns:
            Dados agrupados por região
        """
        pass


class DataFormatter(ABC, Generic[T]):
    """Interface para formatação de dados."""
    
    @abstractmethod
    def format_for_visualization(self, data: T) -> pd.DataFrame:
        """
        Formata dados para visualização.
        
        Args:
            data: Dados a formatar
            
        Returns:
            DataFrame formatado para visualização
        """
        pass


class StatisticsCalculator(ABC):
    """Interface para cálculo de estatísticas."""
    
    @abstractmethod
    def calculate_mean(self, values: List[float]) -> float:
        """Calcula média de forma segura."""
        pass
    
    @abstractmethod
    def calculate_median(self, values: List[float]) -> float:
        """Calcula mediana de forma segura."""
        pass
    
    @abstractmethod
    def calculate_std(self, values: List[float]) -> float:
        """Calcula desvio padrão de forma segura."""
        pass


class DataFilterStrategy(ABC):
    """Strategy para diferentes tipos de filtros de dados."""
    
    @abstractmethod
    def apply_filter(self, data: DataFrameType, **criteria) -> DataFrameType:
        """
        Aplica filtro específico aos dados.
        
        Args:
            data: DataFrame a filtrar
            **criteria: Critérios de filtro
            
        Returns:
            DataFrame filtrado
        """
        pass


class VisualizationDataBuilder(ABC):
    """Builder para construção de dados para visualização."""
    
    @abstractmethod
    def reset(self) -> 'VisualizationDataBuilder':
        """Reinicia o builder."""
        pass
    
    @abstractmethod
    def add_states(self, states: List[str]) -> 'VisualizationDataBuilder':
        """Adiciona estados à análise."""
        pass
    
    @abstractmethod
    def add_metrics(self, metrics: List[str]) -> 'VisualizationDataBuilder':
        """Adiciona métricas à análise."""
        pass
    
    @abstractmethod
    def build(self) -> pd.DataFrame:
        """Constrói o DataFrame final."""
        pass


class ProcessingOrchestrator(ABC):
    """Orquestrador de processos de preparação de dados."""
    
    def __init__(self, 
                 validator: DataValidator,
                 cache_manager: CacheManager,
                 memory_manager: MemoryManager):
        self.validator = validator
        self.cache_manager = cache_manager
        self.memory_manager = memory_manager
    
    @abstractmethod
    def execute_pipeline(self, data: DataFrameType, **kwargs) -> Any:
        """
        Executa pipeline completo de processamento.
        
        Args:
            data: Dados de entrada
            **kwargs: Parâmetros do pipeline
            
        Returns:
            Resultado do processamento
        """
        pass
