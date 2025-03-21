import streamlit as st
import functools
import hashlib
import inspect
import pandas as pd

def hash_dataframe(df):
    """
    Gera um hash de um DataFrame para usar como chave de cache.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame para gerar hash
        
    Retorna:
    --------
    str: Hash representando o DataFrame
    """
    # Extrair características do DataFrame para comparação
    shape = df.shape
    columns = list(df.columns)
    dtypes = df.dtypes.to_dict()
    sample = df.head(5)
    
    # Criar um identificador único
    identifier = f"{shape}_{columns}_{dtypes}_{hash(sample.to_string())}"
    return hashlib.md5(identifier.encode()).hexdigest()


def optimized_cache(ttl=None):
    """
    Decorator para funções que processam DataFrames grandes, otimizando o cache.
    
    Parâmetros:
    -----------
    ttl: int, opcional
        Tempo de vida do cache em segundos
        
    Retorna:
    --------
    decorator: Função decoradora que aplica cache com otimização
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Identificar argumentos que são DataFrames
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Gerar hashes para DataFrames nos argumentos
            df_hashes = []
            for name, value in bound.arguments.items():
                if isinstance(value, pd.DataFrame):
                    df_hashes.append(f"{name}={hash_dataframe(value)}")
                elif isinstance(value, list) and value and isinstance(value[0], pd.DataFrame):
                    df_hashes.append(f"{name}=[{','.join(hash_dataframe(df) for df in value)}]")
            
            # Criar chave de cache com nome da função, hashes dos DataFrames e outros args
            cache_key = f"{func.__name__}_{df_hashes}_{args[1:]}_{kwargs}"
            
            # Usar cache do Streamlit
            if ttl:
                return st.cache_data(ttl=ttl)(func)(*args, **kwargs)
            else:
                return st.cache_data(func)(*args, **kwargs)
        
        return wrapper
    
    return decorator