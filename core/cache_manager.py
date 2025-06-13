"""
Sistema de cache inteligente para o Dashboard.
Implementa estratégias de cache para dados, mapeamentos e visualizações.
"""

import gc
import pickle
import hashlib
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st

from .core_types import DataFrameType
from .config import PERFORMANCE_CONFIG, SECURITY_CONFIG
from .exceptions import CacheError


class CacheKey:
    """Gerador de chaves de cache inteligentes."""
    
    @staticmethod
    def generate(prefix: str, **kwargs) -> str:
        """
        Gera uma chave de cache baseada nos argumentos.
        
        Args:
            prefix: Prefixo da chave
            **kwargs: Argumentos para gerar hash
            
        Returns:
            Chave de cache única
        """
        # Serializar argumentos de forma determinística
        content = str(sorted(kwargs.items()))
        hash_obj = hashlib.md5(content.encode())
        
        return f"{prefix}_{hash_obj.hexdigest()[:12]}"


class MemoryCache:
    """Cache em memória com TTL e gerenciamento automático."""
    
    def __init__(self):
        """Inicializa o cache."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
        self._size_bytes = 0
        self._max_size = PERFORMANCE_CONFIG.MAX_CACHE_SIZE * 1024 * 1024  # MB para bytes
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera item do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor do cache ou None se não encontrado/expirado
        """
        if not PERFORMANCE_CONFIG.ENABLE_CACHE:
            return None
        
        if key not in self._cache:
            return None
        
        # Verificar TTL
        cache_data = self._cache[key]
        if self._is_expired(cache_data['timestamp']):
            self.remove(key)
            return None
        
        # Atualizar tempo de acesso
        self._access_times[key] = datetime.now()
        
        return cache_data['value']
    
    def set(self, key: str, value: Any) -> bool:
        """
        Armazena item no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            
        Returns:
            True se armazenado com sucesso
        """
        if not PERFORMANCE_CONFIG.ENABLE_CACHE:
            return False
        
        try:
            # Calcular tamanho do objeto
            value_size = self._estimate_size(value)
            
            # Verificar se cabe no cache
            if value_size > self._max_size:
                return False
            
            # Liberar espaço se necessário
            while self._size_bytes + value_size > self._max_size:
                if not self._evict_lru():
                    return False
            
            # Armazenar
            cache_data = {
                'value': value,
                'timestamp': datetime.now(),
                'size': value_size
            }
            
            self._cache[key] = cache_data
            self._access_times[key] = datetime.now()
            self._size_bytes += value_size
            
            return True
            
        except Exception as e:
            st.warning(f"Erro ao armazenar no cache: {e}")
            return False
    
    def remove(self, key: str) -> None:
        """Remove item do cache."""
        if key in self._cache:
            self._size_bytes -= self._cache[key]['size']
            del self._cache[key]
            
        if key in self._access_times:
            del self._access_times[key]
    
    def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()
        self._access_times.clear()
        self._size_bytes = 0
        gc.collect()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        return {
            'items_count': len(self._cache),
            'size_mb': self._size_bytes / (1024 * 1024),
            'max_size_mb': self._max_size / (1024 * 1024),
            'usage_percent': (self._size_bytes / self._max_size) * 100,
            'keys': list(self._cache.keys())
        }
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Verifica se item expirou."""
        ttl = timedelta(seconds=PERFORMANCE_CONFIG.CACHE_TTL)
        return datetime.now() - timestamp > ttl
    
    def _evict_lru(self) -> bool:
        """Remove item menos recentemente usado."""
        if not self._access_times:
            return False
        
        # Encontrar item mais antigo
        oldest_key = min(self._access_times.keys(), 
                        key=lambda k: self._access_times[k])
        
        self.remove(oldest_key)
        return True
    
    def _estimate_size(self, obj: Any) -> int:
        """Estima tamanho do objeto em bytes."""
        try:
            return len(pickle.dumps(obj))
        except:
            # Fallback: estimativa simples
            if hasattr(obj, '__sizeof__'):
                return obj.__sizeof__()
            return 1024  # Estimativa padrão


class SmartCacheManager:
    """Gerenciador de cache inteligente para o Dashboard."""
    
    def __init__(self):
        """Inicializa o gerenciador."""
        self.memory_cache = MemoryCache()
        self._hit_count = 0
        self._miss_count = 0
    
    def get_data(self, key: str, loader_func: callable, *args, **kwargs) -> Any:
        """
        Obtém dados do cache ou carrega usando função fornecida.
        
        Args:
            key: Chave do cache
            loader_func: Função para carregar dados se não estiver em cache
            *args, **kwargs: Argumentos para loader_func
            
        Returns:
            Dados do cache ou recém-carregados
        """
        # Tentar cache primeiro
        cached_data = self.memory_cache.get(key)
        if cached_data is not None:
            self._hit_count += 1
            return cached_data
        
        # Cache miss - carregar dados
        self._miss_count += 1
        data = loader_func(*args, **kwargs)
        
        # Armazenar no cache
        self.memory_cache.set(key, data)
        
        return data
    
    def cache_filtered_data(self, states: List[str], tab_type: str, 
                           data: DataFrameType) -> None:
        """
        Armazena dados filtrados no cache.
        
        Args:
            states: Estados filtrados
            tab_type: Tipo da aba
            data: Dados filtrados
        """
        cache_key = CacheKey.generate(
            f"filtered_{tab_type}",
            states=sorted(states)
        )
        
        self.memory_cache.set(cache_key, data)
    
    def get_filtered_data(self, states: List[str], tab_type: str) -> Optional[DataFrameType]:
        """
        Recupera dados filtrados do cache.
        
        Args:
            states: Estados filtrados
            tab_type: Tipo da aba
            
        Returns:
            Dados filtrados ou None se não encontrado
        """
        cache_key = CacheKey.generate(
            f"filtered_{tab_type}",
            states=sorted(states)
        )
        
        return self.memory_cache.get(cache_key)
    
    def clear_cache(self) -> None:
        """Limpa todo o cache."""
        self.memory_cache.clear()
        self._hit_count = 0
        self._miss_count = 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance do cache."""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'hit_rate_percent': hit_rate,
            'memory_stats': self.memory_cache.get_stats()
        }


# Instância global
cache_manager = SmartCacheManager()
