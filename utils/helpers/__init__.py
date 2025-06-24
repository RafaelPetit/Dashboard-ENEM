from .cache_utils import (
    optimized_cache,
    memory_intensive_function,
    release_memory,
    clear_all_cache,
    get_memory_usage
)

from .regiao_utils import (
    obter_mapa_regioes,
    agrupar_por_regiao,
    obter_estados_da_regiao,
    obter_regiao_do_estado,
    obter_todas_regioes
)

from .sidebar_filter import (
    render_sidebar_filters,
    load_filter_data
)
