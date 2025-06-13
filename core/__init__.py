"""
Módulo core do Dashboard ENEM - Versão 2.0

Este módulo implementa uma arquitetura moderna e modular para o Dashboard de
análise do ENEM, seguindo princípios SOLID, Clean Code e boas práticas de
engenharia de software.

Principais componentes:
- config: Configurações centralizadas e imutáveis
- core_types: Definições de tipos e protocolos
- exceptions: Exceções customizadas
- filters: Gerenciamento de filtros de estado e região
- data_manager: Carregamento e gerenciamento de dados
- tab_renderers: Renderização modular das abas
- ui_components: Componentes de interface reutilizáveis
- mapping_manager: Gerenciamento centralizado de mapeamentos
- error_handler: Tratamento robusto de erros
- dashboard_api: Interface unificada do Dashboard

Arquitetura:
- Padrão Strategy para renderização de abas
- Padrão Factory para criação de componentes
- Padrão Facade para interface simplificada
- Injeção de dependências
- Separação clara de responsabilidades
- Tratamento centralizado de erros

Uso básico:
    from core import run_dashboard
    
    # Executar Dashboard completo
    run_dashboard()

Uso avançado:
    from core import create_dashboard, DashboardDebugger
    
    # Criar instância personalizada
    dashboard = create_dashboard()
    
    # Executar com debug
    dashboard.run()
    DashboardDebugger.show_debug_info(dashboard)

Compatibilidade:
    O módulo mantém total compatibilidade com o Dashboard.py existente,
    permitindo migração gradual ou uso híbrido.

Autores: Equipe de desenvolvimento
Versão: 2.0.0
"""

# Importações principais para interface pública
from .dashboard_api import (
    run_dashboard,
    create_dashboard,
    dashboard_api,
    DashboardDebugger
)

# Importações para uso avançado
from .config import (
    UI_CONFIG,
    FILTER_CONFIG,
    DATA_CONFIG,
    ERROR_CONFIG,
    FOOTER_CONFIG,
    PERFORMANCE_CONFIG,
    SECURITY_CONFIG
)

from .filters import FilterFactory
from .data_manager import data_manager
from .tab_renderers import tab_render_manager, tab_executor
from .ui_components import ui_factory
from .mapping_manager import mapping_manager
from .error_handler import error_handler, handle_exceptions, safe_execute
from .cache_manager import cache_manager
from .validators import DataValidator, StateValidator, safe_validate_data, safe_validate_states
from .performance_monitor import performance_monitor, timed_operation

# Importações para desenvolvimento e extensão
from .core_types import *
from .exceptions import *

__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"

# Interface pública principal
__all__ = [
    # Funções principais
    'run_dashboard',
    'create_dashboard',
    
    # Instâncias globais
    'dashboard_api',
    'DashboardDebugger',
      # Componentes para uso avançado
    'FilterFactory',
    'data_manager',
    'tab_render_manager',
    'tab_executor',
    'ui_factory',
    'mapping_manager',
    'error_handler',
    'cache_manager',
    'performance_monitor',
    
    # Validadores
    'DataValidator',
    'StateValidator',
    'safe_validate_data',
    'safe_validate_states',
      # Configurações
    'UI_CONFIG',
    'FILTER_CONFIG',
    'DATA_CONFIG',
    'ERROR_CONFIG',
    'FOOTER_CONFIG',
    'PERFORMANCE_CONFIG',
    'SECURITY_CONFIG',
      # Utilitários
    'handle_exceptions',
    'safe_execute',
    'timed_operation'
]
