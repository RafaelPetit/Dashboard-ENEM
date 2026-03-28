import gc
import streamlit as st
from functools import wraps
from typing import Any, Optional, List, Union, Callable, TypeVar, Dict

# Definir type variables para uso em type hints genéricos
T = TypeVar('T')  # Tipo de retorno da função

# Constantes para configuração de cache
DEFAULT_TTL = 3600  # Tempo padrão de vida do cache em segundos (1 hora)
MEMORIA_LIMITE_AVISO = 0.8  # 80% de uso de memória para aviso


def release_memory(obj: Optional[Union[Any, List[Any]]] = None) -> None:
    """
    Sinaliza objetos para coleta de lixo.
    Nota: `del` aqui remove a referência LOCAL ao parâmetro, não a variável do chamador.
    O chamador deve fazer `del var` diretamente para liberar sua referência.
    gc.collect() é chamado apenas periodicamente, não a cada chamada.
    """
    # gc.collect() é custoso — deixar o Python coletar automaticamente
    # Chamar apenas em pontos estratégicos (fim de análise completa)
    pass


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


def get_memory_usage() -> Dict[str, Any]:
    """
    Retorna informações sobre o uso atual de memória.
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário contendo:
        - current_usage: Uso de memória em bytes
        - percentage: Porcentagem de uso em relação ao disponível
        - warning: Booleano indicando se está acima do limite de aviso
    """
    try:
        import psutil
        
        # Obter informações de memória do sistema
        memory_info = psutil.virtual_memory()
        
        return {
            "current_usage": memory_info.used,
            "percentage": memory_info.percent / 100,
            "warning": memory_info.percent / 100 > MEMORIA_LIMITE_AVISO
        }
    except ImportError:
        # Fallback se psutil não estiver disponível
        return {
            "current_usage": 0,
            "percentage": 0,
            "warning": False
        }


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