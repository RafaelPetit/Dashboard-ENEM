"""
Calculador de estatísticas seguro e otimizado.
Implementa cálculos estatísticos com tratamento robusto de erros.
"""

import numpy as np
import pandas as pd
from typing import Union, Callable, Dict
from scipy import stats

from .data_types import ArrayLike, StatisticResult, StatisticsCalculator
from .exceptions import StatisticsCalculationError, UnsupportedOperationError
from .config import STATS_CONFIG
from .logger import logger


class SafeStatisticsCalculator(StatisticsCalculator):
    """Calculador de estatísticas com tratamento seguro de dados."""
    
    def __init__(self):
        """Inicializa o calculador com mapeamento de operações."""
        self._operations: Dict[str, Callable] = {
            'media': self._safe_mean,
            'mediana': self._safe_median,
            'min': self._safe_min,
            'max': self._safe_max,
            'std': self._safe_std,
            'desvio': self._safe_std,  # Alias para 'std'
            'curtose': self._calculate_kurtosis,
            'assimetria': self._calculate_skewness
        }
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calcula a curtose da distribuição."""
        try:
            # Verificar se há dados suficientes para evitar overflow
            if len(data) < 4:
                return 0.0
            
            # Limitar valores extremos
            data_clean = np.clip(data, -1e10, 1e10)
            
            with np.errstate(overflow='ignore', invalid='ignore'):
                result = stats.kurtosis(data_clean)
                
            if np.isfinite(result):
                return float(result)
            else:
                return 0.0
        except Exception:
            return 0.0
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calcula a assimetria da distribuição."""
        try:
            # Verificar se há dados suficientes para evitar overflow
            if len(data) < 3:
                return 0.0
            
            # Limitar valores extremos
            data_clean = np.clip(data, -1e10, 1e10)
            
            with np.errstate(overflow='ignore', invalid='ignore'):
                result = stats.skew(data_clean)
                
            if np.isfinite(result):
                return float(result)
            else:
                return 0.0
        except Exception:            return 0.0
    
    def _safe_mean(self, data: np.ndarray) -> float:
        """Calcula média de forma segura."""
        with np.errstate(overflow='ignore', invalid='ignore'):
            result = np.mean(data)
            return float(result) if np.isfinite(result) else 0.0
    
    def _safe_median(self, data: np.ndarray) -> float:
        """Calcula mediana de forma segura."""
        with np.errstate(overflow='ignore', invalid='ignore'):
            result = np.median(data)
            return float(result) if np.isfinite(result) else 0.0
    
    def _safe_min(self, data: np.ndarray) -> float:
        """Calcula mínimo de forma segura."""
        with np.errstate(overflow='ignore', invalid='ignore'):
            result = np.min(data)
            return float(result) if np.isfinite(result) else 0.0
    
    def _safe_max(self, data: np.ndarray) -> float:
        """Calcula máximo de forma segura."""
        with np.errstate(overflow='ignore', invalid='ignore'):
            result = np.max(data)
            return float(result) if np.isfinite(result) else 1000.0
    
    def _safe_std(self, data: np.ndarray) -> float:
        """Calcula desvio padrão de forma segura."""
        try:
            with np.errstate(overflow='ignore', invalid='ignore'):
                result = np.std(data)
                return float(result) if np.isfinite(result) else 0.0
        except Exception:
            return 0.0

    def calculate(self, data: ArrayLike, operation: str = 'media') -> StatisticResult:
        """
        Calcula estatística de forma segura, lidando com valores missing.
        
        Args:
            data: Dados para calcular a estatística (Series, array ou lista)
            operation: Tipo de operação estatística
            
        Returns:
            Resultado do cálculo estatístico
            
        Raises:
            UnsupportedOperationError: Se a operação não for suportada
            StatisticsCalculationError: Se ocorrer erro no cálculo
        """
        # Validar operação
        if not STATS_CONFIG.is_valid_operation(operation):
            raise UnsupportedOperationError(
                operation, STATS_CONFIG.SUPPORTED_OPERATIONS
            )
        
        try:
            # Limpar e converter dados
            clean_data = self._clean_data(data)
            
            if len(clean_data) == 0:
                logger.warning(f"Dados vazios para operação '{operation}'")
                return 0.0
            
            # Calcular estatística
            result = self._operations[operation](clean_data)
            
            # Converter para float nativo do Python
            if isinstance(result, (np.integer, np.floating)):
                result = float(result)
            
            logger.debug(
                f"Calculada estatística '{operation}' em {len(clean_data)} valores: {result}"
            )
            
            return result
            
        except Exception as e:
            raise StatisticsCalculationError(
                operation, f"Erro no cálculo: {str(e)}"
            )
    
    def _clean_data(self, data: ArrayLike) -> np.ndarray:
        """
        Limpa os dados removendo valores inválidos.
        
        Args:
            data: Dados a serem limpos
            
        Returns:
            Array NumPy limpo
        """
        if isinstance(data, pd.Series):
            # Usar método pandas para lidar com NaN
            clean_array = data.dropna().values
        else:
            # Converter para array NumPy e remover NaN
            array_data = np.array(data, dtype=float)
            clean_array = array_data[~np.isnan(array_data)]
        
        return clean_array
    
    def calculate_multiple(self, data: ArrayLike, 
                          operations: list) -> Dict[str, StatisticResult]:
        """
        Calcula múltiplas estatísticas de uma vez.
        
        Args:
            data: Dados para calcular as estatísticas
            operations: Lista de operações a serem calculadas
            
        Returns:
            Dicionário com resultados das operações
        """
        results = {}
        clean_data = self._clean_data(data)
        
        for operation in operations:
            try:
                if STATS_CONFIG.is_valid_operation(operation):
                    if len(clean_data) > 0:
                        result = self._operations[operation](clean_data)
                        results[operation] = float(result) if isinstance(
                            result, (np.integer, np.floating)
                        ) else result
                    else:
                        results[operation] = 0.0
                else:
                    logger.warning(f"Operação '{operation}' não suportada. Ignorando.")
                    
            except Exception as e:
                logger.error(f"Erro ao calcular '{operation}': {str(e)}")
                results[operation] = 0.0
        
        return results


# Instância global do calculador
statistics_calculator = SafeStatisticsCalculator()
