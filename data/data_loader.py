"""
Módulo de carregamento de dados - Versão refatorada.

AVISO: Este arquivo mantém compatibilidade com o código legado.
A nova implementação modular está disponível através dos submódulos.

Para usar a nova API:
    from data import load_data_for_tab, filter_data_by_states
    
Para desenvolvimento futuro, use os módulos especializados:
    from data.loaders import tab_loader
    from data.processors import state_filter
    from data.statistics import statistics_calculator
"""

# Importar interface compatível da nova API
from .api import (
    load_data_for_tab,
    filter_data_by_states,
    agrupar_estados_em_regioes,
    calcular_seguro,
    release_memory,
    optimize_dtypes
)

# Re-exportar funções para compatibilidade total
__all__ = [
    'load_data_for_tab',
    'filter_data_by_states', 
    'agrupar_estados_em_regioes',
    'calcular_seguro',
    'release_memory',
    'optimize_dtypes'
]