import gc
import streamlit as st
from functools import wraps
from typing import Any, Optional, List, Union, Callable, TypeVar, Dict

# Definir type variables para uso em type hints genéricos
T = TypeVar('T')  # Tipo de retorno da função

# Constantes para configuração de cache
DEFAULT_TTL = 3600  # Tempo padrão de vida do cache em segundos (1 hora)
MEMORIA_LIMITE_AVISO = 0.8  # 80% de uso de memória para aviso



def optimized_cache(ttl: int = DEFAULT_TTL, max_entries: Optional[int] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Wrapper para cache do Streamlit com funcionalidades adicionais.
    
    Parâmetros:
    -----------
    ttl : int, default=3600
        Tempo de vida do cache em segundos
    max_entries : int, opcional
        Número máximo de entradas no cache
        
    Retorna:
    --------
    Callable: Decorator que aplica cache otimizado
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Aplicar cache do Streamlit
        cache_options = {"ttl": ttl}
        if max_entries is not None:
            cache_options["max_entries"] = max_entries
            
        cached_func = st.cache_data(**cache_options)(func)
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Executa a função cacheada
            result = cached_func(*args, **kwargs)
            return result
            
        return wrapper
    
    return decorator



def clear_all_cache() -> None:
    """
    Limpa todos os caches do Streamlit na sessão atual.
    """
    # Limpar cache de dados
    st.cache_data.clear()
    
    # Limpar cache de recursos
    st.cache_resource.clear()
    
    # Executar coleta de lixo
    gc.collect()


def memory_intensive_function(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator para funções que consomem muita memória.
    Libera automaticamente memória após a execução.
    
    Parâmetros:
    -----------
    func : Callable
        Função a ser decorada
        
    Retorna:
    --------
    Callable: Função decorada com gerenciamento de memória
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        result = func(*args, **kwargs)
        # gc.collect() apenas após execução, não antes (custoso demais)
        gc.collect()
        return result

    return wrapper