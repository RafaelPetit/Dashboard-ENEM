import gc
import streamlit as st
from functools import wraps
from typing import Any, Optional, List, Union, Callable, TypeVar, Dict

# Definir type variables para uso em type hints genéricos
T = TypeVar('T')  # Tipo de retorno da função
InputType = TypeVar('InputType')  # Tipo de entrada para função

# Constantes para configuração de cache
DEFAULT_TTL = 3600  # Tempo padrão de vida do cache em segundos (1 hora)
MEMORIA_LIMITE_AVISO = 0.8  # 80% de uso de memória para aviso


def release_memory(obj: Optional[Union[Any, List[Any]]] = None) -> None:
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
                try:
                    del item
                except:
                    pass
            obj.clear()
        else:
            try:
                del obj
            except:
                pass
    
    # Executar coleta de lixo
    gc.collect()


def optimized_cache(ttl: int = DEFAULT_TTL, max_entries: Optional[int] = None, persist: bool = False) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Wrapper para cache do Streamlit com funcionalidades adicionais.
    
    Parâmetros:
    -----------
    ttl : int, default=3600
        Tempo de vida do cache em segundos
    max_entries : int, opcional
        Número máximo de entradas no cache
    persist : bool, default=False
        Se True, usa cache_resource (persistente), senão cache_data (temporário)
        
    Retorna:
    --------
    Callable: Decorator que aplica cache otimizado
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Aplicar cache do Streamlit
        cache_options = {"ttl": ttl}
        if max_entries is not None:
            cache_options["max_entries"] = max_entries
        
        # Escolher tipo de cache baseado na configuração
        if persist:
            cached_func = st.cache_resource(**cache_options)(func)
        else:
            cached_func = st.cache_data(**cache_options)(func)
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Executar coleta de lixo antes de operações pesadas
            if should_collect_garbage():
                gc.collect()
            
            # Executar a função cacheada
            result = cached_func(*args, **kwargs)
            return result
            
        return wrapper
    
    return decorator


def should_collect_garbage() -> bool:
    """
    Determina se deve executar coleta de lixo baseado no uso de memória.
    
    Retorna:
    --------
    bool: True se deve coletar lixo
    """
    try:
        memory_info = get_memory_usage()
        return memory_info.get("warning", False)
    except Exception:
        return False


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
            "total_memory": memory_info.total,
            "available": memory_info.available,
            "percentage": memory_info.percent / 100,
            "warning": memory_info.percent / 100 > MEMORIA_LIMITE_AVISO
        }
    except ImportError:
        # Fallback se psutil não estiver disponível
        return {
            "current_usage": 0,
            "total_memory": 0,
            "available": 0,
            "percentage": 0,
            "warning": False
        }


def clear_all_cache() -> None:
    """
    Limpa todos os caches do Streamlit na sessão atual.
    """
    try:
        # Limpar cache de dados
        st.cache_data.clear()
        
        # Limpar cache de recursos
        st.cache_resource.clear()
        
        # Limpar session state desnecessário (manter apenas navegação e filtros essenciais)
        keys_to_keep = {
            'current_page', 'previous_page', 
            'estados_selecionados', 'locais_selecionados',
            'filtros_aplicados'
        }
        
        # Identificar chaves a remover
        keys_to_remove = [key for key in st.session_state.keys() if key not in keys_to_keep]
        
        # Remover chaves desnecessárias
        for key in keys_to_remove:
            try:
                del st.session_state[key]
            except KeyError:
                pass
        
        # Executar coleta de lixo
        gc.collect()
        
        print("[CACHE_UTILS] Cache e session state limpos com sucesso")
    except Exception as e:
        print(f"[CACHE_UTILS] Erro ao limpar cache: {e}")


def clear_page_specific_cache(page_name: str) -> None:
    """
    Limpa cache específico de uma página.
    
    Args:
        page_name: Nome da página para limpeza específica
    """
    try:
        # Identificar e remover chaves específicas da página
        page_keys = [key for key in st.session_state.keys() 
                    if key.startswith(f"{page_name.lower()}_") or 
                       key.endswith(f"_{page_name.lower()}")]
        
        for key in page_keys:
            try:
                del st.session_state[key]
            except KeyError:
                pass
        
        # Executar coleta de lixo
        gc.collect()
        
        print(f"[CACHE_UTILS] Cache específico da página '{page_name}' limpo")
    except Exception as e:
        print(f"[CACHE_UTILS] Erro ao limpar cache da página '{page_name}': {e}")


def monitor_session_state_size() -> Dict[str, Any]:
    """
    Monitora o tamanho do session state.
    
    Returns:
        Dict com informações sobre o session state
    """
    try:
        import sys
        
        total_size = 0
        key_sizes = {}
        
        for key, value in st.session_state.items():
            try:
                size = sys.getsizeof(value)
                key_sizes[key] = size
                total_size += size
            except (TypeError, AttributeError):
                key_sizes[key] = 0
        
        # Ordenar por tamanho
        sorted_keys = sorted(key_sizes.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "num_keys": len(st.session_state),
            "largest_keys": sorted_keys[:10],  # Top 10 maiores
            "warning": total_size > 50 * 1024 * 1024  # Warning se > 50MB
        }
    except Exception as e:
        print(f"[CACHE_UTILS] Erro ao monitorar session state: {e}")
        return {"error": str(e)}


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
        # Executar coleta de lixo antes
        gc.collect()
        
        try:
            # Executar a função
            result = func(*args, **kwargs)
            return result
        finally:
            # Executar coleta de lixo depois, mesmo em caso de erro
            gc.collect()
    
    return wrapper


def batch_processor(batch_size: int = 1000) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator para processamento em lotes com liberação de memória.
    
    Parâmetros:
    -----------
    batch_size : int, default=1000
        Tamanho do lote para processamento
        
    Retorna:
    --------
    Callable: Decorator que processa em lotes
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Adicionar informação de batch_size nos kwargs se não existir
            if 'batch_size' not in kwargs:
                kwargs['batch_size'] = batch_size
            
            # Executar coleta de lixo antes do processamento
            gc.collect()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Liberar memória após processamento
                gc.collect()
                
        return wrapper
    
    return decorator


def cache_key_builder(*args: Any, **kwargs: Any) -> str:
    """
    Constrói uma chave de cache baseada nos argumentos.
    
    Parâmetros:
    -----------
    *args : Any
        Argumentos posicionais
    **kwargs : Any
        Argumentos nomeados
        
    Retorna:
    --------
    str: Chave de cache única
    """
    import hashlib
    
    # Converter argumentos para string
    key_parts = []
    
    # Processar argumentos posicionais
    for arg in args:
        if hasattr(arg, 'shape'):  # Para DataFrames/Arrays
            key_parts.append(f"shape_{arg.shape}")
        elif hasattr(arg, '__len__'):  # Para listas/strings
            key_parts.append(f"len_{len(arg)}")
        else:
            key_parts.append(str(arg))
    
    # Processar argumentos nomeados
    for key, value in sorted(kwargs.items()):
        if hasattr(value, 'shape'):
            key_parts.append(f"{key}_shape_{value.shape}")
        elif hasattr(value, '__len__') and not isinstance(value, str):
            key_parts.append(f"{key}_len_{len(value)}")
        else:
            key_parts.append(f"{key}_{value}")
    
    # Criar hash da chave
    key_string = "_".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()[:16]


def monitor_memory_usage(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator para monitorar uso de memória de uma função.
    
    Parâmetros:
    -----------
    func : Callable
        Função a ser monitorada
        
    Retorna:
    --------
    Callable: Função decorada com monitoramento
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Medir memória antes
        memory_before = get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Medir memória depois
            memory_after = get_memory_usage()
            
            # Calcular diferença
            memory_diff = memory_after.get("current_usage", 0) - memory_before.get("current_usage", 0)
            
            # Log se usar muita memória
            if abs(memory_diff) > 100 * 1024 * 1024:  # 100MB
                print(f"Função {func.__name__} alterou uso de memória em {memory_diff / (1024*1024):.1f}MB")
    
    return wrapper


def deep_cleanup() -> None:
    """
    Executa limpeza profunda de memória e cache.
    
    Esta função deve ser chamada:
    - Ao trocar de página
    - Após operações pesadas
    - Em caso de warnings de memória
    """
    try:
        # 1. Limpar todos os caches do Streamlit
        clear_all_cache()
        
        # 2. Monitorar session state
        session_info = monitor_session_state_size()
        if session_info.get("warning", False):
            print(f"[DEEP_CLEANUP] Warning: Session state grande ({session_info['total_size_mb']:.1f}MB)")
        
        # 3. Forçar múltiplas coletas de lixo
        for i in range(3):
            collected = gc.collect()
            if collected > 0:
                print(f"[DEEP_CLEANUP] Coleta {i+1}: {collected} objetos removidos")
        
        # 4. Verificar uso de memória após limpeza
        memory_info = get_memory_usage()
        if memory_info.get("warning", False):
            print(f"[DEEP_CLEANUP] Warning: Memória ainda alta ({memory_info['percentage']*100:.1f}%)")
        
        print("[DEEP_CLEANUP] Limpeza profunda concluída")
        
    except Exception as e:
        print(f"[DEEP_CLEANUP] Erro na limpeza profunda: {e}")


def emergency_cleanup() -> None:
    """
    Limpeza de emergência para situações críticas de memória.
    
    Esta função remove agressivamente dados do session state,
    mantendo apenas o essencial para funcionamento básico.
    """
    try:
        print("[EMERGENCY_CLEANUP] Iniciando limpeza de emergência...")
        
        # Chaves críticas que DEVEM ser mantidas
        critical_keys = {
            'current_page', 'previous_page'
        }
        
        # Remover TUDO exceto chaves críticas
        keys_to_remove = [key for key in st.session_state.keys() 
                         if key not in critical_keys]
        
        removed_count = 0
        for key in keys_to_remove:
            try:
                del st.session_state[key]
                removed_count += 1
            except KeyError:
                pass
        
        # Limpar todos os caches
        st.cache_data.clear()
        st.cache_resource.clear()
        
        # Múltiplas coletas de lixo agressivas
        for i in range(5):
            gc.collect()
        
        print(f"[EMERGENCY_CLEANUP] Removidas {removed_count} chaves do session state")
        print("[EMERGENCY_CLEANUP] Limpeza de emergência concluída")
        
        # Exibir aviso ao usuário
        st.warning("⚠️ Limpeza de emergência executada devido ao alto uso de memória. Alguns filtros podem ter sido resetados.")
        
    except Exception as e:
        print(f"[EMERGENCY_CLEANUP] Erro na limpeza de emergência: {e}")
        st.error("Erro crítico de memória. Recarregue a página.")


def check_memory_and_cleanup() -> bool:
    """
    Verifica uso de memória e executa limpeza se necessário.
    
    Returns:
        True se limpeza foi executada, False caso contrário
    """
    try:
        memory_info = get_memory_usage()
        session_info = monitor_session_state_size()
        
        # Critérios para limpeza
        memory_critical = memory_info.get("percentage", 0) > 0.9  # 90%
        memory_warning = memory_info.get("percentage", 0) > 0.8   # 80%
        session_large = session_info.get("total_size_mb", 0) > 100  # 100MB
        
        if memory_critical or session_large:
            print(f"[AUTO_CLEANUP] Executando limpeza de emergência (Mem: {memory_info.get('percentage', 0)*100:.1f}%, Session: {session_info.get('total_size_mb', 0):.1f}MB)")
            emergency_cleanup()
            return True
            
        elif memory_warning:
            print(f"[AUTO_CLEANUP] Executando limpeza profunda (Mem: {memory_info.get('percentage', 0)*100:.1f}%)")
            deep_cleanup()
            return True
            
        return False
        
    except Exception as e:
        print(f"[AUTO_CLEANUP] Erro na verificação automática: {e}")
        return False