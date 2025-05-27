import gc
import streamlit as st
from functools import wraps  # Se estiver usando wraps para o optimized_cache

def release_memory(obj=None):
    """
    Libera memória de objetos específicos ou executa coleta de lixo geral.
    
    Parâmetros:
    -----------
    obj : objeto ou lista de objetos, opcional
        Objeto(s) a ser(em) explicitamente marcado(s) para coleta de lixo
    """
    if obj is not None:
        if isinstance(obj, list):
            for item in obj:
                item = None
        else:
            obj = None
    
    # Executar coleta de lixo
    gc.collect()

def optimized_cache(ttl=3600):
    """
    Wrapper para cache do Streamlit com funcionalidades adicionais.
    
    Parâmetros:
    -----------
    ttl : int, default=3600
        Tempo de vida do cache em segundos
        
    Retorna:
    --------
    function: Função decorada com cache otimizado
    """
    def decorator(func):
        # Aplicar cache do Streamlit
        cached_func = st.cache_data(ttl=ttl)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Executa a função cacheada
            result = cached_func(*args, **kwargs)
            return result
            
        return wrapper
    return decorator