"""
Gerenciador de dados para o Dashboard.
Implementa carregamento, filtragem e gerenciamento de memória para as abas.
"""

import streamlit as st
import gc
import logging
from typing import Dict, Any, Optional

from .core_types import DataManager, DataFrameType, StateList, TabConfig
from .config import DATA_CONFIG, PERFORMANCE_CONFIG
from .exceptions import DataLoadError, MemoryError
from .cache_manager import cache_manager, CacheKey
from .validators import DataValidator, safe_validate_data
from .performance_monitor import performance_monitor, timed_operation

logger = logging.getLogger(__name__)


class DashboardDataManager(DataManager):
    """Gerenciador de dados especializado para o Dashboard."""
    
    def __init__(self):
        """Inicializa o gerenciador de dados."""
        self._loaded_data_cache: Dict[str, DataFrameType] = {}
        self._memory_tracking = PERFORMANCE_CONFIG.FORCE_GC_AFTER_TAB
    
    @timed_operation("load_tab_data")
    def load_tab_data(self, tab_type: str) -> DataFrameType:
        """
        Carrega dados para uma aba específica.
        
        Args:
            tab_type: Tipo da aba ('geral', 'aspectos_sociais', 'desempenho')
            
        Returns:
            DataFrame com os dados da aba
            
        Raises:
            DataLoadError: Se ocorrer erro no carregamento
        """
        try:
            # Verificar se o tipo de aba é válido
            if tab_type not in DATA_CONFIG.TAB_TYPES.values():
                raise DataLoadError(tab_type, f"Tipo de aba inválido: {tab_type}")
            
            # Gerar chave de cache
            cache_key = CacheKey.generate("tab_data", tab_type=tab_type)
            
            # Tentar carregar do cache primeiro
            cached_data = cache_manager.memory_cache.get(cache_key)
            if cached_data is not None:
                performance_monitor.record_cache_hit()
                return cached_data
            
            performance_monitor.record_cache_miss()
            
            # Carregar dados usando o módulo de dados refatorado
            from data import load_data_for_tab
            
            with st.spinner(f"Carregando dados para {tab_type}..."):
                data = load_data_for_tab(tab_type)
            
            # Validar dados carregados
            if not safe_validate_data(data, tab_type):
                raise DataLoadError(tab_type, "Dados carregados falharam na validação")
                
            # Registrar uso de memória
            performance_monitor.record_memory_usage()
            
            # Armazenar no cache se habilitado
            if PERFORMANCE_CONFIG.ENABLE_CACHE:
                cache_manager.memory_cache.set(cache_key, data)
                
            return data
            
        except Exception as e:
            raise DataLoadError(tab_type, f"Erro ao carregar dados: {str(e)}")
    
    def load_filter_data(self) -> DataFrameType:
        """
        Carrega dados básicos para construção de filtros.
          Returns:
            DataFrame com dados básicos (SG_UF_PROVA, etc.)
            
        Raises:
            DataLoadError: Se ocorrer erro no carregamento
        """
        try:
            # Usar cache para dados de filtro
            cache_key = "filter_data"
            cached_data = cache_manager.memory_cache.get(cache_key)
            
            if cached_data is not None:
                performance_monitor.record_cache_hit()
                return cached_data
            
            performance_monitor.record_cache_miss()
            
            # Carregar dados básicos
            from data import load_data_for_tab
            
            # Usar dados da aba geral para filtros (mais leve)
            logger.info("Carregando dados para filtros...")
            data = load_data_for_tab("geral")
            
            if data is None or data.empty:
                raise DataLoadError("filter_data", "Dados carregados estão vazios")
            
            logger.info(f"Dados carregados: {len(data)} linhas, {len(data.columns)} colunas")
            logger.debug(f"Colunas disponíveis: {list(data.columns)}")
            
            # Manter apenas colunas necessárias para filtros
            filter_columns = ['SG_UF_PROVA']
            available_columns = [col for col in filter_columns if col in data.columns]
            
            if not available_columns:
                logger.error(f"Colunas de filtro não encontradas. Disponíveis: {list(data.columns)}")
                raise DataLoadError("filter_data", "Nenhuma coluna de filtro encontrada")
            
            filter_data = data[available_columns].copy()
            
            # Armazenar no cache
            if PERFORMANCE_CONFIG.ENABLE_CACHE:
                cache_manager.memory_cache.set(cache_key, filter_data)
            
            logger.info(f"Dados de filtro preparados: {len(filter_data)} linhas")
            return filter_data
            
        except Exception as e:
            raise DataLoadError("filter_data", f"Erro ao carregar dados de filtro: {str(e)}")
    
    @timed_operation("filter_by_states")
    def filter_by_states(self, data: DataFrameType, states: StateList) -> DataFrameType:
        """
        Filtra dados por estados selecionados.
        
        Args:
            data: DataFrame com dados completos
            states: Lista de estados para filtrar
            
        Returns:
            DataFrame filtrado
            
        Raises:
            DataLoadError: Se ocorrer erro na filtragem
        """
        try:
            # Validar entrada
            if not safe_validate_data(data, "geral"):
                raise DataLoadError("filter", "Dados inválidos para filtragem")
            
            DataValidator.validate_states(states)
            
            # Verificar se a coluna de estado existe
            if 'SG_UF_PROVA' not in data.columns:
                raise DataLoadError("filter", "Coluna SG_UF_PROVA não encontrada")
            
            # Verificar cache de dados filtrados
            cached_filtered = cache_manager.get_filtered_data(states, "filtered")
            if cached_filtered is not None:
                performance_monitor.record_cache_hit()
                return cached_filtered
            
            performance_monitor.record_cache_miss()
            
            # Realizar filtragem
            filtered_data = data[data['SG_UF_PROVA'].isin(states)].copy()
            
            if filtered_data.empty:
                st.warning("Nenhum dado encontrado para os estados selecionados")
            
            # Armazenar no cache
            cache_manager.cache_filtered_data(states, "filtered", filtered_data)
            
            # Registrar mudança de filtro
            performance_monitor.record_filter_change()
            
            return filtered_data
            
        except Exception as e:
            raise DataLoadError("filter", f"Erro ao filtrar dados: {str(e)}")
    
    def release_memory(self, data: DataFrameType) -> None:
        """
        Libera memória de um DataFrame.
        
        Args:
            data: DataFrame a ser liberado
        """
        if not PERFORMANCE_CONFIG.AUTO_RELEASE_MEMORY:
            return
        
        try:
            # Forçar deleção do DataFrame
            del data
            
            # Forçar garbage collection se configurado
            if PERFORMANCE_CONFIG.FORCE_GC_AFTER_TAB:
                collected = performance_monitor.force_gc_and_record()
                
                # Log se muitos objetos foram coletados
                if collected > 100:
                    st.write(f"🧹 Memória otimizada: {collected} objetos removidos")
            
        except Exception as e:
            st.warning(f"Aviso: Erro ao liberar memória: {e}")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre uso de memória.
        
        Returns:
            Dicionário com estatísticas de memória
        """
        try:
            import psutil
            
            # Informações do sistema
            memory = psutil.virtual_memory()
            
            # Informações do cache
            cache_stats = cache_manager.get_performance_stats()
            
            return {
                'system_memory_gb': memory.total / (1024**3),
                'used_memory_gb': memory.used / (1024**3),
                'available_memory_gb': memory.available / (1024**3),
                'memory_percent': memory.percent,
                'cache_stats': cache_stats
            }
            
        except ImportError:
            return {
                'error': 'psutil não disponível',
                'cache_stats': cache_manager.get_performance_stats()
            }
        except Exception as e:
            return {
                'error': f'Erro ao obter informações de memória: {e}',
                'cache_stats': {}
            }
    
    def clear_cache(self) -> None:
        """Limpa todos os caches."""
        cache_manager.clear_cache()
        self._loaded_data_cache.clear()
        
        # Forçar garbage collection
        if PERFORMANCE_CONFIG.FORCE_GC_AFTER_TAB:
            performance_monitor.force_gc_and_record()


# Instância global
data_manager = DashboardDataManager()
