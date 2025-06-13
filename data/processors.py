"""
Processadores de dados especializados.
Implementa filtros e transformações de dados com responsabilidades bem definidas.
"""

import pandas as pd
from typing import List, Dict, Set
from abc import ABC, abstractmethod

from .data_types import DataFrameType, DataProcessor
from .exceptions import DataProcessingError, DataValidationError
from .config import DATA_CONFIG
from .logger import logger


class BaseDataProcessor(ABC, DataProcessor):
    """Classe base abstrata para processadores de dados."""
    
    @abstractmethod
    def process(self, data: DataFrameType, **kwargs) -> DataFrameType:
        """Processa os dados conforme implementação específica."""
        pass
    
    def _validate_required_columns(self, data: DataFrameType, 
                                  required_columns: List[str]) -> None:
        """
        Valida se as colunas necessárias estão presentes no DataFrame.
        
        Args:
            data: DataFrame a ser validado
            required_columns: Lista de colunas obrigatórias
            
        Raises:
            DataValidationError: Se alguma coluna obrigatória estiver ausente
        """
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise DataValidationError(
                field="columns",
                value=str(missing_columns),
                expected=str(required_columns)
            )


class StateFilter(BaseDataProcessor):
    """Filtro especializado para estados brasileiros."""
    
    def process(self, data: DataFrameType, states: List[str]) -> DataFrameType:
        """
        Filtra dados por estados selecionados de forma eficiente.
        
        Args:
            data: DataFrame com dados completos
            states: Lista de siglas de estados para filtrar
            
        Returns:
            DataFrame filtrado apenas para os estados selecionados
            
        Raises:
            DataProcessingError: Se ocorrer erro durante filtragem
        """
        try:
            # Validar entrada
            if not states:
                logger.warning("Lista de estados vazia. Retornando DataFrame vazio.")
                return pd.DataFrame(columns=data.columns)
            
            # Validar coluna obrigatória
            self._validate_required_columns(data, [DATA_CONFIG.STATE_COLUMN])
            
            # Aplicar filtro
            logger.info(f"Filtrando dados para {len(states)} estados: {states}")
            filtered_data = data[data[DATA_CONFIG.STATE_COLUMN].isin(states)]
            
            logger.info(
                f"Filtro aplicado. Linhas antes: {len(data)}, depois: {len(filtered_data)}"
            )
            
            return filtered_data
            
        except Exception as e:
            if isinstance(e, (DataValidationError, DataProcessingError)):
                raise
            raise DataProcessingError("state_filter", str(e))


class RegionGrouper:
    """Agrupador de estados em regiões brasileiras."""
    
    def __init__(self, regions_mapping: Dict[str, List[str]]):
        """
        Inicializa o agrupador com mapeamento de regiões.
        
        Args:
            regions_mapping: Dicionário que mapeia regiões para seus estados
        """
        self.regions_mapping = regions_mapping
    
    def group_states_by_regions(self, states: List[str]) -> List[str]:
        """
        Converte lista de estados em formato mais amigável, agrupando por regiões.
        
        Args:
            states: Lista com códigos dos estados selecionados
            
        Returns:
            Lista de regiões completas e estados individuais
        """
        if not states:
            return []
        
        try:
            states_set = set(states)
            remaining_states = states_set.copy()
            result = []
            
            # Verificar regiões completas
            for region, region_states in self.regions_mapping.items():
                if region == "Todos os estados":
                    continue
                
                # Se todos os estados da região estão selecionados
                if region_states and all(state in states_set for state in region_states):
                    result.append(region)
                    # Remover estados já agrupados
                    remaining_states -= set(region_states)
            
            # Adicionar estados individuais restantes
            result.extend(sorted(remaining_states))
            
            logger.debug(f"Estados agrupados: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao agrupar estados por regiões: {str(e)}")
            return sorted(states)  # Fallback para lista original


class DataCombiner:
    """Combinador de DataFrames de diferentes fontes."""
    
    def combine_generic_and_specific(self, 
                                   generic_data: DataFrameType,
                                   specific_data: DataFrameType) -> DataFrameType:
        """
        Combina dados genéricos e específicos de forma eficiente.
        
        Args:
            generic_data: DataFrame com dados genéricos
            specific_data: DataFrame com dados específicos
            
        Returns:
            DataFrame combinado
            
        Raises:
            DataProcessingError: Se ocorrer erro na combinação
        """
        try:
            if generic_data.empty and specific_data.empty:
                logger.warning("Ambos DataFrames estão vazios")
                return pd.DataFrame()
            
            if generic_data.empty:
                logger.warning("DataFrame genérico vazio, retornando específico")
                return specific_data
            
            if specific_data.empty:
                logger.warning("DataFrame específico vazio, retornando genérico")
                return generic_data
            
            # Verificar se os índices são compatíveis
            if len(generic_data) != len(specific_data):
                logger.warning(
                    f"Tamanhos diferentes: genérico={len(generic_data)}, "
                    f"específico={len(specific_data)}"
                )
            
            # Combinar dados
            combined_data = pd.concat([generic_data, specific_data], axis=1)
            
            logger.info(
                f"DataFrames combinados. Shape final: {combined_data.shape}"
            )
            
            return combined_data
            
        except Exception as e:
            raise DataProcessingError("data_combination", str(e))


# Instâncias globais dos processadores
state_filter = StateFilter()
data_combiner = DataCombiner()
