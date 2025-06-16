"""
API principal do módulo de dados refatorado.
Fornece interface unificada e compatível com o código existente.
"""

import streamlit as st
from typing import List, Dict, Optional

from .loaders import tab_loader, filtered_loader
from .processors import state_filter, data_combiner, RegionGrouper
from .statistics import statistics_calculator
from .memory import memory_manager
from .data_types import DataFrameType
from .exceptions import DataModuleError
from .logger import logger


class DataAPI:
    """API principal para operações de dados."""
    
    def __init__(self):
        """Inicializa a API com dependências."""
        self._region_grouper: Optional[RegionGrouper] = None
    
    def configure_regions(self, regions_mapping: Dict[str, List[str]]) -> None:
        """
        Configura o mapeamento de regiões.
        
        Args:
            regions_mapping: Dicionário que mapeia regiões para estados
        """
        self._region_grouper = RegionGrouper(regions_mapping)
        logger.info("Mapeamento de regiões configurado")
    
    @st.cache_data(ttl=3600)
    def load_data_for_tab(_self, tab_name: str, apenas_filtros: bool = False) -> DataFrameType:
        """
        Carrega dados otimizados para uma aba específica.
        Mantém compatibilidade com a interface original.
        
        Args:
            tab_name: Nome da aba ('geral', 'aspectos_sociais', 'desempenho')
            apenas_filtros: Se True, carrega apenas dados para filtros
            
        Returns:
            DataFrame com dados carregados
        """
        try:
            if apenas_filtros:
                logger.info("Carregando dados mínimos para filtros")
                return filtered_loader.load_for_filters()
            
            logger.info(f"Carregando dados completos para aba: {tab_name}")
            return tab_loader.load_tab_data(tab_name, include_generic=True)
            
        except DataModuleError as e:
            logger.error(f"Erro do módulo de dados: {str(e)}")
            st.error(f"Erro ao carregar dados para aba {tab_name}: {str(e)}")
            return DataFrameType()
            
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            st.error(f"Erro inesperado ao carregar dados: {str(e)}")
            return DataFrameType()
    
    def filter_data_by_states(self, df: DataFrameType, estados: List[str]) -> DataFrameType:
        """
        Filtra dados por estados selecionados.
        
        Args:
            df: DataFrame com dados completos
            estados: Lista de siglas de estados
            
        Returns:            DataFrame filtrado
        """
        try:
            return state_filter.process(df, estados)
        except DataModuleError as e:
            logger.error(f"Erro ao filtrar por estados: {str(e)}")
            return DataFrameType(columns=df.columns)
    
    def agrupar_estados_em_regioes(self, estados: List[str], 
                                  regioes_mapping: Dict[str, List[str]]) -> List[str]:
        """
        Agrupa estados em regiões para exibição.
        
        Args:
            estados: Lista de códigos dos estados
            regioes_mapping: Mapeamento de regiões para estados
            
        Returns:
            Lista de regiões e estados agrupados
        """
        if self._region_grouper is None:
            self.configure_regions(regioes_mapping)
        
        return self._region_grouper.group_states_by_regions(estados)
    
    def calcular_seguro(self, serie_dados, operacao: str = 'media') -> float:
        """
        Calcula estatísticas de forma segura, evitando overflow.
        
        Args:
            serie_dados: Array ou Series com os dados
            operacao: Tipo de operação ('media', 'mediana', 'std', 'min', 'max')
            
        Returns:
            Resultado da operação ou 0.0 se não puder calcular
        """
        try:
            return statistics_calculator.calculate(serie_dados, operacao)
        except DataModuleError as e:
            logger.error(f"Erro no cálculo estatístico: {str(e)}")
            return 0.0
    
    def release_memory(self, objects) -> None:
        """
        Libera objetos da memória.
        
        Args:
            objects: Objeto ou lista de objetos a serem liberados
        """
        memory_manager.release(objects)


# Instância global da API
data_api = DataAPI()

# Funções compatíveis com a interface original
def load_data_for_tab(tab_name: str, apenas_filtros: bool = False) -> DataFrameType:
    """Função compatível com a interface original."""
    return data_api.load_data_for_tab(tab_name, apenas_filtros)

def filter_data_by_states(df: DataFrameType, estados: List[str]) -> DataFrameType:
    """Função compatível com a interface original."""
    return data_api.filter_data_by_states(df, estados)

def agrupar_estados_em_regioes(estados: List[str], 
                              regioes_mapping: Dict[str, List[str]]) -> List[str]:
    """Função compatível com a interface original."""
    return data_api.agrupar_estados_em_regioes(estados, regioes_mapping)

def calcular_seguro(serie_dados, operacao: str = 'media') -> float:
    """Função compatível com a interface original."""
    return data_api.calcular_seguro(serie_dados, operacao)

def release_memory(objects) -> None:
    """Função compatível com a interface original."""
    data_api.release_memory(objects)

# Funções legacy para compatibilidade
def optimize_dtypes(df: DataFrameType) -> DataFrameType:
    """Função legacy para otimização de tipos."""
    from .memory import dataframe_optimizer
    return dataframe_optimizer.optimize(df)
