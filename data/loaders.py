"""
Carregadores de dados especializados com diferentes estratégias.
Implementa padrão Strategy para carregamento flexível de dados.
"""

import pandas as pd
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional, List

from .data_types import DataFrameType, DataLoader
from .exceptions import DataLoadError, DataValidationError
from .config import DATA_CONFIG
from .memory import dataframe_optimizer, memory_manager
from .logger import logger


class BaseDataLoader(ABC, DataLoader):
    """Classe base abstrata para carregadores de dados."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Inicializa o carregador com caminho base.
        
        Args:
            base_path: Caminho base para arquivos (None = diretório atual)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    @abstractmethod
    def load(self, **kwargs) -> DataFrameType:
        """Carrega dados conforme estratégia específica."""
        pass
    
    def validate_source(self) -> bool:
        """Valida se a fonte de dados está acessível."""
        return self.base_path.exists()
    
    def _get_file_path(self, filename: str) -> Path:
        """Constrói caminho completo do arquivo."""
        return self.base_path / filename
    
    def _validate_file_exists(self, file_path: Path) -> None:
        """
        Valida se o arquivo existe.
        
        Args:
            file_path: Caminho do arquivo
            
        Raises:
            DataLoadError: Se arquivo não existir
        """
        if not file_path.exists():
            raise DataLoadError(str(file_path), "Arquivo não encontrado")
    
    def _apply_enem_corrections(self, df: DataFrameType) -> DataFrameType:
        """
        Aplica correções específicas para dados do ENEM.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame com tipos corrigidos
        """
        try:
            if df is None or df.empty:
                return df
                
            df_corrigido = df.copy()
            
            # Identificar e corrigir colunas de notas
            colunas_notas = [col for col in df.columns if 'NOTA' in col.upper()]
            
            if colunas_notas:
                logger.info(f"Aplicando correções a {len(colunas_notas)} colunas de notas")
                
                for col in colunas_notas:
                    # Converter tipos de baixa precisão para float64
                    if df_corrigido[col].dtype in ['float16', 'int16']:
                        logger.debug(f"Convertendo {col} de {df_corrigido[col].dtype} para float64")
                        df_corrigido[col] = df_corrigido[col].astype('float64')
                    
                    # Limpar valores extremos (outliers absurdos)
                    import numpy as np
                    serie = df_corrigido[col]
                    mask_extremos = (serie > 2000) | (serie < -100)
                    
                    if mask_extremos.any():
                        num_extremos = mask_extremos.sum()
                        logger.warning(f"Removendo {num_extremos} valores extremos de {col}")
                        df_corrigido.loc[mask_extremos, col] = np.nan
            
            # Verificar e corrigir outras colunas numéricas se necessário
            for col in df_corrigido.select_dtypes(include=['float16']).columns:
                if col not in colunas_notas:
                    logger.debug(f"Convertendo {col} de float16 para float32")
                    df_corrigido[col] = df_corrigido[col].astype('float32')
            
            return df_corrigido
            
        except Exception as e:
            logger.error(f"Erro ao aplicar correções ENEM: {e}")
            return df


class ParquetLoader(BaseDataLoader):
    """Carregador especializado para arquivos Parquet."""
    
    def load(self, filename: str, columns: Optional[List[str]] = None,
             optimize_memory: bool = True) -> DataFrameType:
        """
        Carrega arquivo Parquet com opções de otimização.
        
        Args:
            filename: Nome do arquivo Parquet
            columns: Lista de colunas específicas a carregar (None = todas)
            optimize_memory: Se deve otimizar uso de memória
            
        Returns:
            DataFrame carregado
            
        Raises:
            DataLoadError: Se ocorrer erro no carregamento
        """
        file_path = self._get_file_path(filename)
        
        try:
            self._validate_file_exists(file_path)            
            logger.info(f"Carregando arquivo Parquet: {filename}")
            
            # Carregar com pyarrow para melhor performance
            load_params = {'engine': 'pyarrow'}
            if columns:
                load_params['columns'] = columns
                logger.debug(f"Carregando apenas colunas: {columns}")
            
            df = pd.read_parquet(file_path, **load_params)
            
            logger.info(f"Arquivo carregado. Shape: {df.shape}")
            
            # Aplicar correções específicas para dados ENEM
            df = self._apply_enem_corrections(df)
            
            # Otimizar memória se solicitado
            if optimize_memory:
                df = dataframe_optimizer.optimize(df)
            
            return df
            
        except Exception as e:
            raise DataLoadError(filename, str(e))


class FilteredParquetLoader(ParquetLoader):
    """Carregador Parquet com carregamento otimizado para filtros."""
    
    def load_for_filters(self, filename: str = None) -> DataFrameType:
        """
        Carrega apenas dados mínimos necessários para filtros.
        
        Args:
            filename: Nome do arquivo (padrão: arquivo genérico)
            
        Returns:
            DataFrame com dados mínimos para filtros
        """
        target_file = filename or DATA_CONFIG.GENERIC_FILE
        
        logger.info("Carregando dados mínimos para filtros")
        
        return self.load(
            filename=target_file,
            columns=[DATA_CONFIG.STATE_COLUMN],
            optimize_memory=True
        )


class TabDataLoader(ParquetLoader):
    """Carregador especializado para dados de abas específicas."""
    
    def load_tab_data(self, tab_name: str, 
                     include_generic: bool = True) -> DataFrameType:
        """
        Carrega dados para uma aba específica.
        
        Args:
            tab_name: Nome da aba
            include_generic: Se deve incluir dados genéricos
            
        Returns:
            DataFrame com dados da aba
            
        Raises:
            DataValidationError: Se nome da aba for inválido
            DataLoadError: Se ocorrer erro no carregamento
        """
        # Validar nome da aba
        if not DATA_CONFIG.validate_tab_name(tab_name):
            raise DataValidationError(
                field="tab_name",
                value=tab_name,
                expected=str(list(DATA_CONFIG.TAB_FILE_MAPPING.keys()))
            )
        
        try:
            logger.info(f"Carregando dados para aba: {tab_name}")
            
            dataframes_to_combine = []
            
            # Carregar dados genéricos se solicitado
            if include_generic:
                generic_df = self.load(DATA_CONFIG.GENERIC_FILE)
                dataframes_to_combine.append(generic_df)
                logger.debug("Dados genéricos carregados")
            
            # Carregar dados específicos da aba
            specific_file = DATA_CONFIG.get_tab_file_path(tab_name)
            specific_df = self.load(specific_file)
            dataframes_to_combine.append(specific_df)
            logger.debug(f"Dados específicos da aba '{tab_name}' carregados")
            
            # Combinar dados se necessário
            if len(dataframes_to_combine) == 1:
                result_df = dataframes_to_combine[0]
            else:
                result_df = pd.concat(dataframes_to_combine, axis=1)
                # Liberar DataFrames intermediários
                memory_manager.release(dataframes_to_combine)
            
            logger.info(f"Dados da aba carregados. Shape final: {result_df.shape}")
            
            return result_df
            
        except Exception as e:
            if isinstance(e, (DataValidationError, DataLoadError)):
                raise
            raise DataLoadError(f"tab_{tab_name}", str(e))


class DataLoaderFactory:
    """Factory para criação de carregadores de dados."""
    
    @staticmethod
    def create_parquet_loader(base_path: Optional[str] = None) -> ParquetLoader:
        """Cria carregador Parquet padrão."""
        return ParquetLoader(base_path)
    
    @staticmethod
    def create_filtered_loader(base_path: Optional[str] = None) -> FilteredParquetLoader:
        """Cria carregador para filtros."""
        return FilteredParquetLoader(base_path)
    
    @staticmethod
    def create_tab_loader(base_path: Optional[str] = None) -> TabDataLoader:
        """Cria carregador para abas."""
        return TabDataLoader(base_path)


# Instâncias globais dos carregadores
parquet_loader = DataLoaderFactory.create_parquet_loader()
filtered_loader = DataLoaderFactory.create_filtered_loader()
tab_loader = DataLoaderFactory.create_tab_loader()
