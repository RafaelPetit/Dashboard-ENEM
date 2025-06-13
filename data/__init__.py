"""
Módulo de dados refatorado para análise do ENEM.

Este módulo implementa uma arquitetura modular e escalável para carregamento,
processamento e análise de dados do ENEM, seguindo princípios SOLID e
boas práticas de engenharia de software.

Principais componentes:
- config: Configurações centralizadas
- types: Definições de tipos e protocolos  
- exceptions: Exceções customizadas
- logger: Sistema de logging estruturado
- memory: Gerenciamento de memória e otimização
- statistics: Cálculos estatísticos seguros
- processors: Processadores de dados especializados
- loaders: Carregadores de dados com diferentes estratégias
- api: Interface unificada e compatível com código legado

Uso básico:
    from data import load_data_for_tab, filter_data_by_states
    
    # Carregar dados para uma aba
    df = load_data_for_tab('geral')
    
    # Filtrar por estados
    df_filtered = filter_data_by_states(df, ['SP', 'RJ'])

Autores: Equipe de desenvolvimento
Versão: 2.0.0
"""

# Importações principais para compatibilidade
from .api import (
    load_data_for_tab,
    filter_data_by_states, 
    agrupar_estados_em_regioes,
    calcular_seguro,
    release_memory,
    optimize_dtypes,
    data_api
)

# Importações avançadas para uso interno
from .loaders import (
    parquet_loader,
    filtered_loader, 
    tab_loader,
    DataLoaderFactory
)

from .processors import (
    state_filter,
    data_combiner,
    RegionGrouper
)

from .statistics import statistics_calculator
from .memory import dataframe_optimizer, memory_manager
from .logger import logger
from .config import DATA_CONFIG, STATS_CONFIG
from .exceptions import *

__version__ = "2.0.0"
__author__ = "Equipe de Desenvolvimento"

# Configuração do nível de log padrão
logger.set_level("INFO")
