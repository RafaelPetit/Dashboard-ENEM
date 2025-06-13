"""
Configurações centralizadas para o Dashboard ENEM.
Define constantes, configurações de interface e parâmetros do sistema.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass(frozen=True)
class UIConfig:
    """Configurações de interface do usuário."""
    
    # Configurações da página
    PAGE_TITLE: str = "Dashboard ENEM"
    PAGE_ICON: str = "📚"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"
    
    # Títulos e labels
    MAIN_TITLE: str = "📊 Dashboard de Análise do ENEM - 2023"
    SIDEBAR_HEADER: str = "Filtros"
    
    # Mensagens do sistema
    LOADING_FILTERS_MSG: str = "Carregando dados para filtros..."
    LOADING_TAB_MSG: str = "Carregando dados para análise..."
    
    # Configurações de abas
    TAB_NAMES: List[str] = None
    
    def __post_init__(self):
        if self.TAB_NAMES is None:
            object.__setattr__(self, 'TAB_NAMES', ["Geral", "Aspectos Sociais", "Desempenho"])


@dataclass(frozen=True)
class FilterConfig:
    """Configurações para filtros e seleções."""
    
    # Labels dos filtros
    BRASIL_CHECKBOX_LABEL: str = "Brasil (todos os estados)"
    REGION_SELECT_LABEL: str = "Selecione as regiões:"
    STATE_SELECT_LABEL: str = "Selecione estados específicos:"
    
    # Mensagens de ajuda
    REGION_HELP: str = "Selecionar uma região automaticamente seleciona todos os seus estados"
    STATE_HELP: str = "Selecione estados específicos além dos já incluídos pelas regiões selecionadas"
    DISABLED_HELP: str = "Todos os estados estão selecionados. Desmarque 'Brasil' para selecionar estados específicos."
    
    # Mensagens de status
    WARNING_NO_SELECTION: str = "⚠️ Selecione pelo menos uma região ou estado, ou marque a opção Brasil."
    SUCCESS_BRASIL: str = "✅ Dados de todo o Brasil"
    SUCCESS_REGIONS: str = "✅ Regiões: {}"
    SUCCESS_ADDITIONAL: str = "✅ Estados adicionais: {}"
    INFO_TOTAL: str = "Total: {} estados selecionados"


@dataclass(frozen=True)
class DataConfig:
    """Configurações relacionadas aos dados."""
    
    # Colunas essenciais
    STATE_COLUMN: str = "SG_UF_PROVA"
    
    # Configurações de cache
    CACHE_TTL: int = 3600
    
    # Tipos de abas para carregamento
    TAB_TYPES: Dict[str, str] = None
    
    def __post_init__(self):
        if self.TAB_TYPES is None:
            object.__setattr__(self, 'TAB_TYPES', {
                "Geral": "geral",
                "Aspectos Sociais": "aspectos_sociais", 
                "Desempenho": "desempenho"
            })


@dataclass(frozen=True)
class ErrorConfig:
    """Configurações para tratamento de erros."""
    
    # Mensagens de erro por aba
    ERROR_GERAL: str = "Erro ao carregar a aba Geral: {}"
    ERROR_ASPECTOS: str = "Erro ao carregar a aba Aspectos Sociais: {}"
    ERROR_DESEMPENHO: str = "Erro ao carregar a aba Desempenho: {}"
    
    # Mensagens de aviso
    WARNING_NO_DATA: str = "Não há dados suficientes para análise com os filtros atuais."
    WARNING_SELECT_STATE: str = "Selecione pelo menos um estado no filtro lateral para visualizar os dados."


@dataclass(frozen=True)
class FooterConfig:
    """Configurações do rodapé da aplicação."""
    
    # Informações da instituição
    UNIVERSITY_NAME: str = "UNIP - Universidade Paulista"
    CAMPUS_NAME: str = "Campus Sorocaba"
    COURSE_NAME: str = "Curso de Ciência da Computação"
    LOGO_PATH: str = "Logo.jpg"
    
    # Informações do projeto
    PROJECT_TITLE: str = "Dashboard de Análise do ENEM 2023"
    PROJECT_TYPE: str = "Projeto de Iniciação Científica"
    COPYRIGHT: str = "© 2025 - Todos os direitos reservados"
    VERSION: str = "v2.0.0"
    LAST_UPDATE: str = "Atualizado em 13/06/2025"
    
    # Informações da equipe
    DEVELOPER_NAME: str = "Rafael Petit"
    DEVELOPER_EMAIL: str = "rpetit.dev@gmail.com"
    ADVISOR_NAME: str = "Prof. Dr. César C. Xavier"
    ADVISOR_EMAIL: str = "cesarcx@gmail.com"


@dataclass(frozen=True)
class PerformanceConfig:
    """Configurações de performance e otimização."""
    
    # Cache settings
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # 1 hora
    MAX_CACHE_SIZE: int = 100  # MB
    
    # Memory management
    FORCE_GC_AFTER_TAB: bool = True
    MEMORY_THRESHOLD: float = 0.8  # 80% da memória disponível
    AUTO_RELEASE_MEMORY: bool = True
    
    # Data loading
    LAZY_LOADING: bool = True
    BATCH_SIZE: int = 10000
    OPTIMIZE_DTYPES: bool = True
    
    # UI performance
    DEBOUNCE_FILTERS: int = 300  # ms
    ASYNC_RENDERING: bool = False
    
    # Debug
    ENABLE_PROFILING: bool = False
    LOG_PERFORMANCE: bool = False


@dataclass(frozen=True)
class SecurityConfig:
    """Configurações de segurança."""
    
    # Input validation
    VALIDATE_INPUTS: bool = True
    MAX_STATES_SELECTION: int = 27
    SANITIZE_TEXT: bool = True
    
    # Error handling
    HIDE_STACK_TRACES: bool = True
    LOG_ERRORS: bool = True
    
    # Data protection
    ENCRYPT_CACHE: bool = False
    ANONYMIZE_DEBUG: bool = True


# Instâncias globais das configurações
UI_CONFIG = UIConfig()
FILTER_CONFIG = FilterConfig()
DATA_CONFIG = DataConfig()
ERROR_CONFIG = ErrorConfig()
FOOTER_CONFIG = FooterConfig()
PERFORMANCE_CONFIG = PerformanceConfig()
SECURITY_CONFIG = SecurityConfig()
