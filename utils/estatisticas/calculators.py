"""
Calculadores estatísticos básicos.
Implementa cálculos fundamentais seguindo princípios SOLID.
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
from utils.mappings import get_mappings


class SafeCalculator:
    """Calculador seguro para operações estatísticas básicas."""
    
    @staticmethod
    def safe_mean(data: pd.Series) -> float:
        """
        Calcula média de forma segura.
        
        Args:
            data: Série com dados numéricos
            
        Returns:
            Média dos dados ou 0.0 se não puder calcular
        """
        try:
            valid_data = data.dropna()
            if len(valid_data) == 0:
                return 0.0
            
            result = valid_data.mean()
            return float(result) if np.isfinite(result) else 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def safe_std(data: pd.Series) -> float:
        """
        Calcula desvio padrão de forma segura.
        
        Args:
            data: Série com dados numéricos
            
        Returns:
            Desvio padrão ou 0.0 se não puder calcular
        """
        try:
            valid_data = data.dropna()
            if len(valid_data) <= 1:
                return 0.0
            
            result = valid_data.std()
            return float(result) if np.isfinite(result) else 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def safe_median(data: pd.Series) -> float:
        """
        Calcula mediana de forma segura.
        
        Args:
            data: Série com dados numéricos
            
        Returns:
            Mediana ou 0.0 se não puder calcular
        """
        try:
            valid_data = data.dropna()
            if len(valid_data) == 0:
                return 0.0
            
            result = valid_data.median()
            return float(result) if np.isfinite(result) else 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def safe_percentile(data: pd.Series, percentile: float) -> float:
        """
        Calcula percentil de forma segura.
        
        Args:
            data: Série com dados numéricos
            percentile: Percentil a calcular (0-100)
            
        Returns:
            Valor do percentil ou 0.0 se não puder calcular
        """
        try:
            valid_data = data.dropna()
            if len(valid_data) == 0:
                return 0.0
            
            result = np.percentile(valid_data, percentile)
            return float(result) if np.isfinite(result) else 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def safe_correlation(x: pd.Series, y: pd.Series) -> float:
        """
        Calcula correlação de forma segura.
        
        Args:
            x: Primeira série de dados
            y: Segunda série de dados
            
        Returns:
            Coeficiente de correlação ou 0.0 se não puder calcular
        """
        try:
            # Filtrar apenas valores válidos em ambas as séries
            combined = pd.concat([x, y], axis=1).dropna()
            if len(combined) < 2:
                return 0.0
            
            result = combined.iloc[:, 0].corr(combined.iloc[:, 1])
            return float(result) if np.isfinite(result) else 0.0
        except Exception:
            return 0.0


class DistributionCalculator:
    """Calculador para análises de distribuição."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.safe_calc = SafeCalculator()
    
    def calculate_basic_stats(self, data: pd.Series) -> Dict[str, float]:
        """
        Calcula estatísticas básicas de distribuição.
        
        Args:
            data: Série com dados para análise
            
        Returns:
            Dict com estatísticas básicas
        """
        return {
            'mean': self.safe_calc.safe_mean(data),
            'median': self.safe_calc.safe_median(data),
            'std_dev': self.safe_calc.safe_std(data),
            'min': float(data.min()) if len(data) > 0 else 0.0,
            'max': float(data.max()) if len(data) > 0 else 0.0,
            'count': len(data)
        }
    
    def calculate_percentiles(self, data: pd.Series, percentiles: List[float]) -> Dict[str, float]:
        """
        Calcula múltiplos percentis.
        
        Args:
            data: Série com dados
            percentiles: Lista de percentis a calcular
            
        Returns:
            Dict com percentis calculados
        """
        result = {}
        for p in percentiles:
            result[f'P{int(p)}'] = self.safe_calc.safe_percentile(data, p)
        return result
    
    def calculate_concentration_index(self, proportions: pd.Series) -> float:
        """
        Calcula índice de concentração (Gini simplificado).
        
        Args:
            proportions: Série com proporções
            
        Returns:
            Índice de concentração
        """
        try:
            if len(proportions) == 0 or proportions.sum() == 0:
                return 0.0
            
            # Normalizar proporções
            normalized = proportions / proportions.sum()
            
            # Calcular índice de Gini simplificado
            n = len(normalized)
            if n <= 1:
                return 0.0
            
            index = 1 - (1 / n) * (normalized**2).sum() * n
            return float(index) if np.isfinite(index) else 0.0
        except Exception:
            return 0.0
    
    def calculate_entropy(self, proportions: pd.Series) -> Tuple[float, float]:
        """
        Calcula entropia e entropia normalizada.
        
        Args:
            proportions: Série com proporções
            
        Returns:
            Tupla com (entropia, entropia_normalizada)
        """
        try:
            if len(proportions) == 0 or proportions.sum() == 0:
                return 0.0, 0.0
            
            # Normalizar proporções
            normalized = proportions / proportions.sum()
            valid_props = normalized[normalized > 0]
            
            if len(valid_props) == 0:
                return 0.0, 0.0
            
            # Calcular entropia
            entropy = -np.sum(valid_props * np.log2(valid_props))
            
            # Normalizar pela entropia máxima
            max_entropy = np.log2(len(valid_props))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
            
            return (
                float(entropy) if np.isfinite(entropy) else 0.0,
                float(normalized_entropy) if np.isfinite(normalized_entropy) else 0.0
            )
        except Exception:
            return 0.0, 0.0


class CorrelationCalculator:
    """Calculador para análises de correlação entre variáveis categóricas."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.safe_calc = SafeCalculator()
    
    def calculate_chi_square(self, contingency_table: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula estatística qui-quadrado.
        
        Args:
            contingency_table: Tabela de contingência
            
        Returns:
            Dict com estatísticas do qui-quadrado
        """
        try:
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            
            return {
                'chi2': float(chi2) if np.isfinite(chi2) else 0.0,
                'p_value': float(p_value) if np.isfinite(p_value) else 1.0,
                'degrees_freedom': int(dof),
                'expected_frequencies': expected
            }
        except Exception:
            return {
                'chi2': 0.0,
                'p_value': 1.0,
                'degrees_freedom': 0,
                'expected_frequencies': np.array([])
            }
    
    def calculate_cramers_v(self, chi2: float, n: int, contingency_table: pd.DataFrame) -> float:
        """
        Calcula V de Cramer.
        
        Args:
            chi2: Estatística qui-quadrado
            n: Tamanho da amostra
            contingency_table: Tabela de contingência
            
        Returns:
            Valor do V de Cramer
        """
        try:
            if n == 0 or contingency_table.empty:
                return 0.0
            
            min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)
            if min_dim == 0:
                return 0.0
            
            v_cramer = np.sqrt(chi2 / (n * min_dim))
            return float(v_cramer) if np.isfinite(v_cramer) else 0.0
        except Exception:
            return 0.0
    
    def calculate_contingency_coefficient(self, chi2: float, n: int) -> float:
        """
        Calcula coeficiente de contingência.
        
        Args:
            chi2: Estatística qui-quadrado
            n: Tamanho da amostra
            
        Returns:
            Coeficiente de contingência
        """
        try:
            if n == 0:
                return 0.0
            
            coefficient = np.sqrt(chi2 / (chi2 + n))
            return float(coefficient) if np.isfinite(coefficient) else 0.0
        except Exception:
            return 0.0
    
    def calculate_mutual_information(self, contingency_table: pd.DataFrame) -> Tuple[float, float]:
        """
        Calcula informação mútua e informação mútua normalizada.
        
        Args:
            contingency_table: Tabela de contingência
            
        Returns:
            Tupla com (informação_mútua, informação_mútua_normalizada)
        """
        try:
            if contingency_table.empty:
                return 0.0, 0.0
            
            n = contingency_table.sum().sum()
            if n == 0:
                return 0.0, 0.0
            
            # Calcular probabilidades
            p_xy = contingency_table.values / n
            p_x = contingency_table.sum(axis=1).values / n
            p_y = contingency_table.sum(axis=0).values / n
            
            # Calcular informação mútua
            mi = 0.0
            for i in range(len(p_x)):
                for j in range(len(p_y)):
                    if p_xy[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                        mi += p_xy[i, j] * np.log2(p_xy[i, j] / (p_x[i] * p_y[j]))
            
            # Calcular entropias para normalização
            h_x = -np.sum(p_x[p_x > 0] * np.log2(p_x[p_x > 0]))
            h_y = -np.sum(p_y[p_y > 0] * np.log2(p_y[p_y > 0]))
            h_max = min(h_x, h_y)
            
            # Normalizar
            mi_normalized = mi / h_max if h_max > 0 else 0.0
            
            return (
                float(mi) if np.isfinite(mi) else 0.0,
                float(mi_normalized) if np.isfinite(mi_normalized) else 0.0
            )
        except Exception:
            return 0.0, 0.0


class VariabilityCalculator:
    """Calculador para análises de variabilidade."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.safe_calc = SafeCalculator()
    
    def calculate_coefficient_of_variation(self, data: pd.Series) -> float:
        """
        Calcula coeficiente de variação.
        
        Args:
            data: Série com dados numéricos
            
        Returns:
            Coeficiente de variação em percentual
        """
        mean = self.safe_calc.safe_mean(data)
        std = self.safe_calc.safe_std(data)
        
        if mean == 0:
            return 0.0
        
        cv = (std / mean) * 100
        return float(cv) if np.isfinite(cv) else 0.0
    
    def calculate_range_statistics(self, data: pd.Series) -> Dict[str, float]:
        """
        Calcula estatísticas de amplitude.
        
        Args:
            data: Série com dados numéricos
            
        Returns:
            Dict com estatísticas de amplitude
        """
        try:
            if len(data) == 0:
                return {
                    'range': 0.0,
                    'percentage_range': 0.0,
                    'max_min_ratio': 0.0
                }
            
            min_val = float(data.min())
            max_val = float(data.max())
            range_val = max_val - min_val
            
            percentage_range = (range_val / min_val * 100) if min_val > 0 else 0.0
            max_min_ratio = (max_val / min_val) if min_val > 0 else 0.0
            
            return {
                'range': range_val,
                'percentage_range': percentage_range,
                'max_min_ratio': max_min_ratio
            }
        except Exception:
            return {
                'range': 0.0,
                'percentage_range': 0.0,
                'max_min_ratio': 0.0
            }
    
    def calculate_gini_coefficient(self, data: pd.Series) -> float:
        """
        Calcula coeficiente de Gini.
        
        Args:
            data: Série com dados numéricos
            
        Returns:
            Coeficiente de Gini
        """
        try:
            values = data.dropna().sort_values()
            if len(values) <= 1:
                return 0.0
            
            n = len(values)
            index = np.arange(1, n + 1)
            gini = 2 * np.sum(index * values) / (n * np.sum(values)) - (n + 1) / n
            
            return float(gini) if np.isfinite(gini) else 0.0
        except Exception:
            return 0.0


class PerformanceCalculator:
    """Calculador para análises de desempenho."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.safe_calc = SafeCalculator()
        self.variability_calc = VariabilityCalculator()
    
    def find_extreme_performers(
        self, 
        data: pd.DataFrame, 
        performance_column: str, 
        identifier_column: str
    ) -> Tuple[Optional[pd.Series], Optional[pd.Series]]:
        """
        Encontra os melhores e piores desempenhos.
        
        Args:
            data: DataFrame com os dados
            performance_column: Coluna com valores de desempenho
            identifier_column: Coluna identificadora (ex: estado)
            
        Returns:
            Tupla com (melhor_desempenho, pior_desempenho)
        """
        try:
            if data.empty or performance_column not in data.columns:
                return None, None
            
            # Encontrar extremos
            max_idx = data[performance_column].idxmax()
            min_idx = data[performance_column].idxmin()
            
            best = data.loc[max_idx] if max_idx in data.index else None
            worst = data.loc[min_idx] if min_idx in data.index else None
            
            return best, worst
        except Exception:
            return None, None
    
    def calculate_performance_gap(
        self, 
        best_value: float, 
        worst_value: float
    ) -> Dict[str, float]:
        """
        Calcula diferenças de desempenho.
        
        Args:
            best_value: Melhor valor de desempenho
            worst_value: Pior valor de desempenho
            
        Returns:
            Dict com métricas de diferença
        """
        try:
            absolute_difference = best_value - worst_value
            percentage_difference = (absolute_difference / worst_value * 100) if worst_value > 0 else 0.0
            
            return {
                'absolute_difference': float(absolute_difference),
                'percentage_difference': float(percentage_difference)
            }
        except Exception:
            return {
                'absolute_difference': 0.0,
                'percentage_difference': 0.0
            }
