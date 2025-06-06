# Este arquivo permite que a pasta utils funcione como um pacote Python
from .data_loader import (
    load_data_for_tab, 
    filter_data_by_states, 
    agrupar_estados_em_regioes, 
    release_memory
)
from .mappings import get_mappings

# Funções para gerenciamento de memória e cache
from .helpers.cache_utils import (
    optimized_cache,
    memory_intensive_function, 
    release_memory,
    clear_all_cache,
    get_memory_usage
)

# Isso permite importar diretamente:
# from utils import load_data, get_mappings, optimized_cache, etc.