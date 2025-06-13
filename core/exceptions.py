"""
Exceções customizadas para o core do Dashboard.
Fornece tratamento de erro específico e informativo.
"""


class DashboardError(Exception):
    """Exceção base para o Dashboard."""
    pass


class UIComponentError(DashboardError):
    """Erro em componentes de interface."""
    
    def __init__(self, component: str, message: str):
        self.component = component
        super().__init__(f"Erro no componente '{component}': {message}")


class TabRenderError(DashboardError):
    """Erro durante renderização de aba."""
    
    def __init__(self, tab_name: str, message: str):
        self.tab_name = tab_name
        super().__init__(f"Erro ao renderizar aba '{tab_name}': {message}")


class DataLoadError(DashboardError):
    """Erro durante carregamento de dados."""
    
    def __init__(self, tab_type: str, message: str):
        self.tab_type = tab_type
        super().__init__(f"Erro ao carregar dados para '{tab_type}': {message}")


class FilterError(DashboardError):
    """Erro na aplicação de filtros."""
    
    def __init__(self, filter_type: str, message: str):
        self.filter_type = filter_type
        super().__init__(f"Erro no filtro '{filter_type}': {message}")


class ConfigurationError(DashboardError):
    """Erro de configuração."""
    
    def __init__(self, config_key: str, message: str):
        self.config_key = config_key
        super().__init__(f"Erro de configuração '{config_key}': {message}")


class MappingError(DashboardError):
    """Erro relacionado aos mapeamentos."""
    
    def __init__(self, mapping_key: str, message: str):
        self.mapping_key = mapping_key
        super().__init__(f"Erro no mapeamento '{mapping_key}': {message}")


class StateSelectionError(DashboardError):
    """Erro na seleção de estados."""
    
    def __init__(self, message: str):
        super().__init__(f"Erro na seleção de estados: {message}")


class PerformanceError(DashboardError):
    """Erro relacionado à performance."""
    
    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Erro de performance em '{operation}': {message}")


class MemoryError(DashboardError):
    """Erro relacionado ao gerenciamento de memória."""
    
    def __init__(self, message: str):
        super().__init__(f"Erro de memória: {message}")


class CacheError(DashboardError):
    """Erro relacionado ao sistema de cache."""
    
    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Erro de cache em '{operation}': {message}")


class ValidationError(DashboardError):
    """Erro de validação de dados."""
    
    def __init__(self, message: str):
        super().__init__(f"Erro de validação: {message}")
