"""
Tipos customizados e protocolos para o core do Dashboard.
Define contratos claros entre os componentes do sistema.
"""

from typing import Protocol, Dict, List, Optional, Tuple, Any, Callable
from abc import ABC, abstractmethod
import streamlit as st
import pandas as pd


# Tipos customizados
DataFrameType = pd.DataFrame
StateList = List[str]
MappingDict = Dict[str, Any]
TabConfig = Dict[str, Any]


class StateFilter(Protocol):
    """Protocolo para filtros de estado."""
    
    def get_selected_states(self) -> StateList:
        """Retorna lista de estados selecionados."""
        ...
    
    def get_display_names(self) -> List[str]:
        """Retorna nomes formatados para exibição."""
        ...
    
    def is_brasil_selected(self) -> bool:
        """Verifica se todo o Brasil está selecionado."""
        ...


class DataManager(Protocol):
    """Protocolo para gerenciamento de dados."""
    
    def load_tab_data(self, tab_type: str) -> DataFrameType:
        """Carrega dados para uma aba específica."""
        ...
    
    def filter_by_states(self, data: DataFrameType, states: StateList) -> DataFrameType:
        """Filtra dados por estados."""
        ...
    
    def release_memory(self, objects: Any) -> None:
        """Libera objetos da memória."""
        ...


class TabRenderer(Protocol):
    """Protocolo para renderizadores de aba."""
    
    def render(self, data: DataFrameType, states: StateList, 
               display_names: List[str], **kwargs) -> None:
        """Renderiza uma aba com os dados fornecidos."""
        ...
    
    def validate_data(self, data: DataFrameType) -> bool:
        """Valida se os dados são adequados para renderização."""
        ...


class UIComponent(Protocol):
    """Protocolo para componentes de interface."""
    
    def render(self) -> None:
        """Renderiza o componente."""
        ...
    
    def update_state(self, **kwargs) -> None:
        """Atualiza o estado do componente."""
        ...


class MappingProvider(Protocol):
    """Protocolo para provedores de mapeamento."""
    
    def get_all_mappings(self) -> MappingDict:
        """Retorna todos os mapeamentos disponíveis."""
        ...
    
    def get_mapping(self, key: str) -> Optional[Any]:
        """Retorna um mapeamento específico."""
        ...


class ErrorHandler(Protocol):
    """Protocolo para tratamento de erros."""
    
    def handle_tab_error(self, tab_name: str, error: Exception) -> None:
        """Trata erro específico de uma aba."""
        ...
    
    def handle_data_error(self, operation: str, error: Exception) -> None:
        """Trata erro relacionado aos dados."""
        ...


class PerformanceMonitor(Protocol):
    """Protocolo para monitoramento de performance."""
    
    def track_memory_usage(self) -> None:
        """Monitora uso de memória."""
        ...
    
    def optimize_performance(self) -> None:
        """Executa otimizações de performance."""
        ...


# Classes abstratas base

class BaseUIComponent(ABC, UIComponent):
    """Classe base para componentes de interface."""
    
    def __init__(self, config: Any):
        """Inicializa o componente com configuração."""
        self.config = config
    
    @abstractmethod
    def render(self) -> None:
        """Implementação específica de renderização."""
        pass
    
    def update_state(self, **kwargs) -> None:
        """Implementação padrão para atualização de estado."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BaseTabRenderer(ABC, TabRenderer):
    """Classe base para renderizadores de aba."""
    
    def __init__(self, name: str, config: Any):
        """Inicializa o renderizador."""
        self.name = name
        self.config = config
    
    @abstractmethod
    def render(self, data: DataFrameType, states: StateList, 
               display_names: List[str], **kwargs) -> None:
        """Implementação específica de renderização."""
        pass
    
    def validate_data(self, data: DataFrameType) -> bool:
        """Validação padrão de dados."""
        return not data.empty and len(data) > 0


# Types para callbacks e funções
TabRenderFunction = Callable[[DataFrameType, StateList, List[str]], None]
ErrorHandlerFunction = Callable[[str, Exception], None]
StateChangeCallback = Callable[[StateList], None]

# Tipos para configurações complexas
TabRendererConfig = Dict[str, Tuple[str, TabRenderFunction, Dict[str, Any]]]
FilterConfiguration = Dict[str, Any]
UIConfiguration = Dict[str, Any]
