"""
Gerenciador de memória otimizado para o módulo de dados.
Implementa estratégias de limpeza e otimização de memória.
"""

import gc
import pandas as pd
import numpy as np
from typing import Union, List, Any

from .data_types import DataFrameType, MemoryManager
from .exceptions import MemoryOptimizationError
from .logger import logger


class DataFrameOptimizer:
    """Otimizador especializado para DataFrames do pandas."""
    
    def __init__(self, category_threshold_absolute: int = 100, 
                 category_threshold_relative: float = 0.1):
        """
        Inicializa o otimizador.
        
        Args:
            category_threshold_absolute: Limite absoluto para conversão categórica
            category_threshold_relative: Limite relativo para conversão categórica
        """
        self.category_threshold_absolute = category_threshold_absolute
        self.category_threshold_relative = category_threshold_relative
    
    def optimize(self, df: DataFrameType) -> DataFrameType:
        """
        Otimiza tipos de dados do DataFrame para reduzir uso de memória.
        
        Args:
            df: DataFrame a ser otimizado
            
        Returns:
            DataFrame com tipos otimizados
            
        Raises:
            MemoryOptimizationError: Se ocorrer erro durante otimização
        """
        if df.empty:
            logger.warning("DataFrame vazio recebido para otimização")
            return df
        
        try:
            logger.info(f"Iniciando otimização de DataFrame com shape {df.shape}")
            memory_before = df.memory_usage(deep=True).sum() / 1024**2
            
            # Otimizar cada tipo de coluna
            df = self._optimize_integers(df)
            df = self._optimize_floats(df)
            df = self._optimize_objects(df)
            
            memory_after = df.memory_usage(deep=True).sum() / 1024**2
            reduction = ((memory_before - memory_after) / memory_before) * 100
            
            logger.info(f"Otimização concluída. Redução de memória: {reduction:.1f}%")
            logger.info(f"Memória antes: {memory_before:.1f}MB, depois: {memory_after:.1f}MB")
            
            return df
            
        except Exception as e:
            raise MemoryOptimizationError(f"Falha na otimização: {str(e)}")
    
    def _optimize_integers(self, df: DataFrameType) -> DataFrameType:
        """Otimiza colunas de inteiros."""
        int_cols = df.select_dtypes(include=['int64']).columns
        
        for col in int_cols:
            col_min, col_max = df[col].min(), df[col].max()
            
            if col_min >= 0:  # Valores positivos
                if col_max < 256:
                    df[col] = df[col].astype(np.uint8)
                elif col_max < 65536:
                    df[col] = df[col].astype(np.uint16)
                else:
                    df[col] = df[col].astype(np.uint32)
            else:  # Valores que podem ser negativos
                if col_min > -128 and col_max < 128:
                    df[col] = df[col].astype(np.int8)
                elif col_min > -32768 and col_max < 32768:
                    df[col] = df[col].astype(np.int16)
                else:
                    df[col] = df[col].astype(np.int32)
        
        return df
    
    def _optimize_floats(self, df: DataFrameType) -> DataFrameType:
        """Otimiza colunas de ponto flutuante."""
        float_cols = df.select_dtypes(include=['float64']).columns
        
        for col in float_cols:
            df[col] = df[col].astype(np.float32)
        
        return df
    
    def _optimize_objects(self, df: DataFrameType) -> DataFrameType:
        """Otimiza colunas de objeto (strings)."""
        obj_cols = df.select_dtypes(include=['object']).columns
        
        for col in obj_cols:
            n_unique = df[col].nunique()
            should_categorize = (
                n_unique < self.category_threshold_absolute or 
                (n_unique / len(df)) < self.category_threshold_relative
            )
            
            if should_categorize:
                df[col] = df[col].astype('category')
        
        return df


class MemoryManagerImpl(MemoryManager):
    """Implementação do gerenciador de memória."""
    
    def release(self, objects: Union[object, List[object]]) -> None:
        """
        Libera objetos da memória.
        
        Args:
            objects: Objeto ou lista de objetos a serem liberados
        """
        if not isinstance(objects, list):
            objects = [objects]
        
        released_count = 0
        for obj in objects:
            if obj is not None:
                del obj
                released_count += 1
        
        logger.debug(f"Liberados {released_count} objetos da memória")
        self.force_gc()
    
    def force_gc(self) -> None:
        """Força coleta de lixo."""
        collected = gc.collect()
        logger.debug(f"Coleta de lixo executada. Objetos coletados: {collected}")


# Instâncias globais
dataframe_optimizer = DataFrameOptimizer()
memory_manager = MemoryManagerImpl()
