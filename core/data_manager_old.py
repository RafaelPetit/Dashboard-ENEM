"""
Gerenciador de dados para o Dashboard.
Implementa carregamento, filtragem e gerenciamento de memória para as abas.
"""

import streamlit as st
import gc
from typing import Dict, Any, Optional

from .core_types import DataManager, DataFrameType, StateList, TabConfig
from .config import DATA_CONFIG, PERFORMANCE_CONFIG
from .exceptions import DataLoadError, MemoryError
from .cache_manager import cache_manager, CacheKey
from .validators import DataValidator, safe_validate_data
from .performance_monitor import performance_monitor, timed_operation


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
                self._loaded_data_cache[tab_type] = data
            
            return data
            
        except Exception as e:
            raise DataLoadError(tab_type, str(e))
    
    def filter_by_states(self, data: DataFrameType, states: StateList) -> DataFrameType:
        """
        Filtra dados por estados selecionados.
        
        Args:
            data: DataFrame a ser filtrado
            states: Lista de estados para filtrar
            
        Returns:
            DataFrame filtrado
        """
        try:
            if data.empty or not states:
                return data
            
            # Usar função do módulo de dados refatorado
            from data import filter_data_by_states
            
            filtered_data = filter_data_by_states(data, states)
            
            # Log de performance se configurado
            if len(states) > PERFORMANCE_CONFIG.MAX_STATES_WARNING:
                st.info(f"Filtro aplicado para {len(states)} estados. "
                       f"Performance pode ser afetada com muitos estados.")
            
            return filtered_data
            
        except Exception as e:
            st.error(f"Erro ao filtrar dados por estados: {str(e)}")
            return data  # Retornar dados originais em caso de erro
    
    def release_memory(self, objects: Any) -> None:
        """
        Libera objetos da memória.
        
        Args:
            objects: Objeto ou lista de objetos a serem liberados
        """
        try:
            if not PERFORMANCE_CONFIG.RELEASE_MEMORY_AFTER_USE:
                return
            
            # Usar função do módulo de dados refatorado
            from data import release_memory
            
            release_memory(objects)
            
            # Forçar coleta de lixo se configurado
            if self._memory_tracking:
                gc.collect()
                
        except Exception as e:
            # Log do erro mas não interromper execução
            st.error(f"Aviso: Erro ao liberar memória: {str(e)}")
    
    def load_filter_data(self) -> DataFrameType:
        """
        Carrega dados mínimos necessários para os filtros.
        
        Returns:
            DataFrame com dados para filtros
        """
        try:
            from data import load_data_for_tab
            
            with st.spinner("Carregando dados para filtros..."):
                return load_data_for_tab("geral", apenas_filtros=True)
                
        except Exception as e:
            raise DataLoadError("filter_data", str(e))
    
    def preload_all_tabs(self) -> None:
        """Pre-carrega dados de todas as abas (opcional para performance)."""
        if PERFORMANCE_CONFIG.LAZY_LOADING:
            return  # Não fazer preload se lazy loading estiver ativo
        
        try:
            for tab_type in DATA_CONFIG.TAB_TYPES.values():
                if tab_type not in self._loaded_data_cache:
                    self._loaded_data_cache[tab_type] = self.load_tab_data(tab_type)
        except Exception as e:
            st.warning(f"Aviso: Erro no preload de dados: {str(e)}")
    
    def clear_cache(self) -> None:
        """Limpa o cache de dados."""
        self._loaded_data_cache.clear()
        self.release_memory(None)  # Força limpeza geral
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre uso de memória.
        
        Returns:
            Dicionário com estatísticas de memória
        """
        import sys
        
        info = {
            'cached_tabs': len(self._loaded_data_cache),
            'cached_tab_names': list(self._loaded_data_cache.keys()),
            'python_objects': len(gc.get_objects()),
        }
        
        # Adicionar tamanho dos DataFrames em cache se possível
        try:
            total_memory = 0
            for tab_name, data in self._loaded_data_cache.items():
                if hasattr(data, 'memory_usage'):
                    tab_memory = data.memory_usage(deep=True).sum() / 1024**2  # MB
                    info[f'memory_{tab_name}_mb'] = round(tab_memory, 2)
                    total_memory += tab_memory
            
            info['total_cache_memory_mb'] = round(total_memory, 2)
            
        except Exception:
            info['memory_calculation_error'] = True
        
        return info


class TabDataProcessor:
    """Processador especializado para dados de abas."""
    
    def __init__(self, data_manager: DashboardDataManager):
        """
        Inicializa o processador.
        
        Args:
            data_manager: Gerenciador de dados
        """
        self.data_manager = data_manager
    
    def prepare_tab_data(self, tab_type: str, states: StateList) -> DataFrameType:
        """
        Prepara dados completos para uma aba.
        
        Args:
            tab_type: Tipo da aba
            states: Estados selecionados
            
        Returns:
            DataFrame preparado e filtrado
        """
        try:
            # Carregar dados
            raw_data = self.data_manager.load_tab_data(tab_type)
            
            # Filtrar por estados se configurado
            if PERFORMANCE_CONFIG.FILTER_BEFORE_PROCESSING and states:
                filtered_data = self.data_manager.filter_by_states(raw_data, states)
                
                # Liberar dados originais se diferentes dos filtrados
                if id(raw_data) != id(filtered_data):
                    self.data_manager.release_memory(raw_data)
                
                return filtered_data
            
            return raw_data
            
        except Exception as e:
            raise DataLoadError(tab_type, f"Erro na preparação de dados: {str(e)}")
    
    def validate_tab_data(self, data: DataFrameType, required_columns: Optional[list] = None) -> bool:
        """
        Valida dados de uma aba.
        
        Args:
            data: DataFrame a ser validado
            required_columns: Colunas obrigatórias (opcional)
            
        Returns:
            True se dados são válidos
        """
        if data.empty:
            return False
        
        if required_columns:
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                st.warning(f"Colunas ausentes nos dados: {missing_columns}")
                return False
        
        return True


# Instância global do gerenciador
data_manager = DashboardDataManager()
