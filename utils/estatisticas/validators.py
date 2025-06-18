"""
Validadores base para dados estatísticos.
Implementa validações comuns seguindo o princípio Single Responsibility.
"""
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from .interfaces import IDataValidator
from utils.mappings import get_mappings


class BaseDataValidator(IDataValidator):
    """Validador base para dados estatísticos."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.min_samples = self.mappings['limiares_processamento']['min_amostras_correlacao']
    
    def validate(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Valida se os dados atendem aos requisitos básicos.
        
        Args:
            data: DataFrame a ser validado
            required_columns: Colunas obrigatórias
            
        Returns:
            True se dados são válidos, False caso contrário
        """
        errors = self.get_validation_errors(data, required_columns)
        return len(errors) == 0
    
    def get_validation_errors(self, data: pd.DataFrame, required_columns: List[str]) -> List[str]:
        """
        Retorna lista de erros de validação.
        
        Args:
            data: DataFrame a ser validado
            required_columns: Colunas obrigatórias
            
        Returns:
            Lista com mensagens de erro
        """
        errors = []
        
        # Verificar se DataFrame existe e não está vazio
        if data is None:
            errors.append("DataFrame é None")
            return errors
            
        if data.empty:
            errors.append("DataFrame está vazio")
            return errors
        
        # Verificar colunas obrigatórias
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            errors.append(f"Colunas obrigatórias ausentes: {missing_columns}")
        
        # Verificar número mínimo de amostras
        if len(data) < self.min_samples:
            errors.append(f"Amostras insuficientes: {len(data)} < {self.min_samples}")
        
        return errors


class NumericalDataValidator(BaseDataValidator):
    """Validador especializado para dados numéricos."""
    
    def validate_numerical_column(
        self, 
        data: pd.DataFrame, 
        column: str, 
        exclude_zeros: bool = True,
        min_valid_ratio: float = 0.1
    ) -> bool:
        """
        Valida uma coluna numérica específica.
        
        Args:
            data: DataFrame com os dados
            column: Nome da coluna a validar
            exclude_zeros: Se deve excluir zeros da validação
            min_valid_ratio: Proporção mínima de valores válidos
            
        Returns:
            True se coluna é válida, False caso contrário
        """
        if column not in data.columns:
            return False
        
        # Filtrar valores válidos
        valid_data = data[column].dropna()
        if exclude_zeros:
            valid_data = valid_data[valid_data > 0]
        
        # Verificar proporção de valores válidos
        valid_ratio = len(valid_data) / len(data)
        return valid_ratio >= min_valid_ratio
    
    def get_valid_numerical_data(
        self, 
        data: pd.DataFrame, 
        column: str, 
        exclude_zeros: bool = True
    ) -> pd.Series:
        """
        Retorna apenas dados válidos de uma coluna numérica.
        
        Args:
            data: DataFrame com os dados
            column: Nome da coluna
            exclude_zeros: Se deve excluir zeros
            
        Returns:
            Series com dados válidos
        """
        if column not in data.columns:
            return pd.Series(dtype=float)
        
        valid_data = data[column].dropna()
        if exclude_zeros:
            valid_data = valid_data[valid_data > 0]
        
        return valid_data


class CategoricalDataValidator(BaseDataValidator):
    """Validador especializado para dados categóricos."""
    
    def validate_categorical_columns(
        self, 
        data: pd.DataFrame, 
        columns: List[str],
        min_categories: int = 2
    ) -> bool:
        """
        Valida colunas categóricas.
        
        Args:
            data: DataFrame com os dados
            columns: Lista de colunas categóricas
            min_categories: Número mínimo de categorias únicas
            
        Returns:
            True se colunas são válidas, False caso contrário
        """
        for column in columns:
            if column not in data.columns:
                return False
            
            # Verificar número de categorias únicas
            unique_values = data[column].nunique()
            if unique_values < min_categories:
                return False
        
        return True
    
    def validate_contingency_table(
        self, 
        data: pd.DataFrame, 
        var_x: str, 
        var_y: str
    ) -> bool:
        """
        Valida se é possível criar tabela de contingência válida.
        
        Args:
            data: DataFrame com os dados
            var_x: Primeira variável categórica
            var_y: Segunda variável categórica
            
        Returns:
            True se tabela é válida, False caso contrário
        """
        if not self.validate(data, [var_x, var_y]):
            return False
        
        # Criar tabela de contingência
        try:
            contingency = pd.crosstab(data[var_x], data[var_y])
            return contingency.shape[0] > 1 and contingency.shape[1] > 1
        except Exception:
            return False


class PerformanceDataValidator(BaseDataValidator):
    """Validador especializado para dados de desempenho."""
    
    def __init__(self):
        super().__init__()
        self.valid_score_range = (0, 1000)  # Faixa válida para notas ENEM
    
    def validate_performance_data(
        self, 
        data: pd.DataFrame, 
        performance_columns: List[str]
    ) -> bool:
        """
        Valida dados de desempenho (notas).
        
        Args:
            data: DataFrame com os dados
            performance_columns: Colunas com dados de desempenho
            
        Returns:
            True se dados são válidos, False caso contrário
        """
        if not self.validate(data, performance_columns):
            return False
        
        for column in performance_columns:
            if column in data.columns:
                # Verificar se valores estão na faixa válida
                valid_scores = data[
                    (data[column] >= self.valid_score_range[0]) & 
                    (data[column] <= self.valid_score_range[1])
                ]
                
                # Pelo menos 10% dos dados devem estar na faixa válida
                if len(valid_scores) / len(data) < 0.1:
                    return False
        
        return True
    
    def filter_valid_scores(
        self, 
        data: pd.DataFrame, 
        score_columns: List[str]
    ) -> pd.DataFrame:
        """
        Filtra apenas registros com notas válidas.
        
        Args:
            data: DataFrame com os dados
            score_columns: Colunas com notas
            
        Returns:
            DataFrame filtrado com notas válidas
        """
        filtered_data = data.copy()
        
        for column in score_columns:
            if column in filtered_data.columns:
                # Filtrar valores na faixa válida e maiores que zero
                filtered_data = filtered_data[
                    (filtered_data[column] > 0) & 
                    (filtered_data[column] <= self.valid_score_range[1])
                ]
        
        return filtered_data


class RegionalDataValidator(BaseDataValidator):
    """Validador especializado para dados regionais."""
    
    def __init__(self):
        super().__init__()
        self.mappings = get_mappings()
        self.valid_states = []
        for states in self.mappings['regioes_mapping'].values():
            self.valid_states.extend(states)
    
    def validate_regional_data(
        self, 
        data: pd.DataFrame, 
        state_column: str = 'SG_UF_PROVA'
    ) -> bool:
        """
        Valida dados regionais.
        
        Args:
            data: DataFrame com os dados
            state_column: Coluna com códigos dos estados
            
        Returns:
            True se dados regionais são válidos, False caso contrário
        """
        if not self.validate(data, [state_column]):
            return False
        
        # Verificar se há estados válidos nos dados
        valid_states_in_data = data[state_column].isin(self.valid_states).sum()
        return valid_states_in_data > 0
    
    def get_states_coverage(
        self, 
        data: pd.DataFrame, 
        state_column: str = 'SG_UF_PROVA'
    ) -> Dict[str, Any]:
        """
        Analisa a cobertura de estados nos dados.
        
        Args:
            data: DataFrame com os dados
            state_column: Coluna com códigos dos estados
            
        Returns:
            Dict com informações de cobertura
        """
        if state_column not in data.columns:
            return {
                'total_states': 0,
                'valid_states': 0,
                'coverage_percentage': 0,
                'missing_states': self.valid_states
            }
        
        states_in_data = set(data[state_column].unique())
        valid_states_in_data = states_in_data.intersection(set(self.valid_states))
        missing_states = set(self.valid_states) - valid_states_in_data
        
        return {
            'total_states': len(states_in_data),
            'valid_states': len(valid_states_in_data),
            'coverage_percentage': len(valid_states_in_data) / len(self.valid_states) * 100,
            'missing_states': list(missing_states)
        }
