"""
Analisadores especializados para aspectos sociais.
Implementa análises específicas seguindo princípios SOLID.
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from ..interfaces import IStatisticsCalculator, ICorrelationAnalyzer, IDistributionAnalyzer, IRegionalAnalyzer
from ..validators import CategoricalDataValidator, BaseDataValidator
from ..calculators import DistributionCalculator, CorrelationCalculator, VariabilityCalculator
from ..result_builders import DistributionResultBuilder, CorrelationResultBuilder, RegionalResultBuilder
from ..interpreters import CorrelationInterpreter, VariabilityInterpreter, ConcentrationInterpreter
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function


class SocialDistributionAnalyzer(IDistributionAnalyzer, IStatisticsCalculator):
    """Analisador de distribuição para aspectos sociais."""
    
    def __init__(self):
        self.validator = CategoricalDataValidator()
        self.calculator = DistributionCalculator()
        self.result_builder = DistributionResultBuilder()
        self.concentration_interpreter = ConcentrationInterpreter()
    
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida entrada para análise de distribuição."""
        required_columns = kwargs.get('required_columns', ['Quantidade'])
        return self.validator.validate(data, required_columns)
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Calcula estatísticas de distribuição para aspectos sociais.
        
        Args:
            data: DataFrame com contagem por categoria
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dict com estatísticas de distribuição
        """
        return self.analyze_distribution(data, 'Quantidade')
    
    def calculate_percentiles(
        self, 
        data: pd.Series, 
        percentiles: List[float]
    ) -> Dict[str, float]:
        """
        Calcula percentis para uma série.
        
        Args:
            data: Série com os dados
            percentiles: Lista de percentis a calcular
            
        Returns:
            Dict com percentis calculados
        """
        try:
            percentile_values = {}
            for p in percentiles:
                percentile_values[f'p{int(p)}'] = data.quantile(p / 100.0)
            return percentile_values
        except Exception:
            return {f'p{int(p)}': 0.0 for p in percentiles}
    
    def analyze_distribution(self, data: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Analisa distribuição de uma variável categórica.
        
        Args:
            data: DataFrame com dados de contagem
            column: Nome da coluna com quantidades
            
        Returns:
            Dict com análise de distribuição
        """
        if not self.validate_input(data, required_columns=[column]):
            return self.result_builder.build_empty_result()
        
        try:
            # Calcular estatísticas básicas
            quantities = data[column]
            total = quantities.sum()
            
            if total <= 0:
                return self.result_builder.build_empty_result("Total de dados é zero")
            
            # Encontrar categorias extremas
            categories_stats = self._calculate_category_extremes(data, column)
            
            # Calcular estatísticas de concentração
            proportions = quantities / total
            concentration_stats = self._calculate_concentration_stats(proportions)
            
            # Calcular estatísticas de variabilidade
            variability_stats = self.calculator.calculate_basic_stats(quantities)
            variability_stats.update(self._calculate_variability_metrics(quantities))
            
            return self.result_builder.build_distribution_result(
                total=int(total),
                categories_stats=categories_stats,
                concentration_stats=concentration_stats,
                variability_stats=variability_stats
            )
            
        except Exception as e:
            return self.result_builder.build_empty_result(f"Erro no cálculo: {str(e)}")
    
    def _calculate_category_extremes(self, data: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Calcula categorias com valores extremos."""
        try:
            max_idx = data[column].idxmax()
            min_idx = data[column].idxmin()
            
            most_frequent = data.loc[max_idx].copy() if max_idx in data.index else None
            least_frequent = data.loc[min_idx].copy() if min_idx in data.index else None
            
            return {
                'most_frequent': most_frequent,
                'least_frequent': least_frequent,
                'count': len(data)
            }
        except Exception:
            return {
                'most_frequent': None,
                'least_frequent': None,
                'count': 0
            }
    
    def _calculate_concentration_stats(self, proportions: pd.Series) -> Dict[str, Any]:
        """Calcula estatísticas de concentração."""
        gini_index = self.calculator.calculate_concentration_index(proportions)
        entropy, normalized_entropy = self.calculator.calculate_entropy(proportions)
        classification = self.concentration_interpreter.classify_concentration(gini_index)
        
        return {
            'gini_index': round(gini_index, 3),
            'entropy': round(entropy, 3),
            'normalized_entropy': round(normalized_entropy, 3),
            'classification': classification
        }
    
    def _calculate_variability_metrics(self, data: pd.Series) -> Dict[str, Any]:
        """Calcula métricas de variabilidade específicas."""
        variability_calc = VariabilityCalculator()
        
        cv = variability_calc.calculate_coefficient_of_variation(data)
        range_stats = variability_calc.calculate_range_statistics(data)
        
        return {
            'coefficient_of_variation': round(cv, 2),
            'max_min_ratio': round(range_stats['max_min_ratio'], 2)
        }


class SocialCorrelationAnalyzer(ICorrelationAnalyzer, IStatisticsCalculator):
    """Analisador de correlação entre variáveis categóricas sociais."""
    
    def __init__(self):
        self.validator = CategoricalDataValidator()
        self.calculator = CorrelationCalculator()
        self.result_builder = CorrelationResultBuilder()
        self.interpreter = CorrelationInterpreter()
    
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida entrada para análise de correlação."""
        var_x = kwargs.get('var_x')
        var_y = kwargs.get('var_y')
        
        if not var_x or not var_y:
            return False
        
        return self.validator.validate_contingency_table(data, var_x, var_y)
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Calcula correlação entre variáveis categóricas.
        
        Args:
            data: DataFrame com dados
            **kwargs: Deve conter 'var_x' e 'var_y'
            
        Returns:
            Dict com análise de correlação
        """
        var_x = kwargs.get('var_x')
        var_y = kwargs.get('var_y')
        
        return self.analyze_correlation(data, var_x, var_y)
    
    def analyze_correlation(self, data: pd.DataFrame, var_x: str, var_y: str) -> Dict[str, Any]:
        """
        Analisa correlação entre duas variáveis categóricas.
        
        Args:
            data: DataFrame com dados
            var_x: Primeira variável categórica
            var_y: Segunda variável categórica
            
        Returns:
            Dict com métricas de correlação
        """
        if not self.validate_input(data, var_x=var_x, var_y=var_y):
            return self.result_builder.build_empty_result()
        
        try:
            # Limpar dados e criar tabela de contingência
            clean_data = data.dropna(subset=[var_x, var_y])
            contingency_table = pd.crosstab(clean_data[var_x], clean_data[var_y])
            
            # Calcular estatísticas qui-quadrado
            chi_square_stats = self.calculator.calculate_chi_square(contingency_table)
            
            # Calcular métricas de associação
            n_samples = contingency_table.sum().sum()
            association_metrics = self._calculate_association_metrics(
                chi_square_stats, n_samples, contingency_table
            )
            
            # Gerar interpretações
            interpretation = self._generate_interpretations(association_metrics)
            
            return self.result_builder.build_correlation_result(
                chi_square_stats=chi_square_stats,
                association_metrics=association_metrics,
                interpretation=interpretation,
                contingency_table=contingency_table
            )
            
        except Exception as e:
            return self.result_builder.build_empty_result(f"Erro no cálculo: {str(e)}")
    
    def interpret_correlation(self, correlation_value: float) -> str:
        """Interpreta valor de correlação."""
        return self.interpreter.interpret_correlation_strength(correlation_value)
    
    def _calculate_association_metrics(
        self, 
        chi_square_stats: Dict[str, Any], 
        n_samples: int, 
        contingency_table: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calcula métricas de associação."""
        chi2 = chi_square_stats['chi2']
        
        # V de Cramer
        cramers_v = self.calculator.calculate_cramers_v(chi2, n_samples, contingency_table)
        
        # Coeficiente de contingência
        contingency_coef = self.calculator.calculate_contingency_coefficient(chi2, n_samples)
        
        # Normalizar coeficiente de contingência
        k = min(contingency_table.shape)
        c_max = np.sqrt((k - 1) / k) if k > 1 else 1
        normalized_coef = contingency_coef / c_max if c_max > 0 else 0
        
        # Informação mútua
        mutual_info, normalized_mi = self.calculator.calculate_mutual_information(contingency_table)
        
        return {
            'cramers_v': round(cramers_v, 3),
            'contingency_coefficient': round(normalized_coef, 3),
            'mutual_information': round(mutual_info, 3),
            'normalized_mutual_info': round(normalized_mi, 3)
        }
    
    def _generate_interpretations(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Gera interpretações textuais."""
        cramers_v = metrics['cramers_v']
        
        return {
            'strength': self.interpreter.interpret_correlation_strength(cramers_v),
            'context': self.interpreter.interpret_cramers_v(cramers_v),
            'effect_size': self.interpreter.classify_effect_size(cramers_v)
        }


class SocialRegionalAnalyzer(IRegionalAnalyzer, IStatisticsCalculator):
    """Analisador de distribuição regional para aspectos sociais."""
    
    def __init__(self):
        self.validator = BaseDataValidator()
        self.calculator = DistributionCalculator()
        self.variability_calc = VariabilityCalculator()
        self.result_builder = RegionalResultBuilder()
        self.interpreter = VariabilityInterpreter()
    
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida entrada para análise regional."""
        required_columns = ['Estado', 'Categoria', 'Percentual']
        return self.validator.validate(data, required_columns)
    
    @optimized_cache(ttl=1800)
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Calcula análise regional para aspectos sociais.
        
        Args:
            data: DataFrame com dados regionais
            **kwargs: Parâmetros como 'aspecto_social' e 'categoria'
            
        Returns:
            Dict com análise regional
        """
        aspecto_social = kwargs.get('aspecto_social', '')
        categoria = kwargs.get('categoria')
        
        return self.analyze_by_region(data, aspecto_social, 'Estado')
    
    def analyze_by_region(
        self, 
        data: pd.DataFrame, 
        variable: str, 
        region_column: str = 'Estado'
    ) -> Dict[str, Any]:
        """
        Analisa distribuição por região.
        
        Args:
            data: DataFrame com dados por estado
            variable: Variável sendo analisada
            region_column: Coluna com identificação regional
            
        Returns:
            Dict com análise regional
        """
        if not self.validate_input(data):
            return self.result_builder.build_empty_result()
        
        try:
            # Filtrar para categoria específica se aplicável
            analysis_data = self._filter_data_for_analysis(data)
            
            if len(analysis_data) < 3:
                return self.result_builder.build_empty_result("Dados regionais insuficientes")
            
            # Calcular medidas de tendência central
            central_tendency = self._calculate_central_tendency(analysis_data)
            
            # Calcular medidas de variabilidade
            variability = self._calculate_variability_measures(analysis_data)
            
            # Identificar valores extremos
            extremes = self._identify_extreme_values(analysis_data)
            
            # Gerar classificações
            classification = self._generate_classifications(variability)
            
            return self.result_builder.build_regional_result(
                central_tendency=central_tendency,
                variability=variability,
                extremes=extremes,
                classification=classification
            )
            
        except Exception as e:
            return self.result_builder.build_empty_result(f"Erro na análise: {str(e)}")
    
    def classify_regional_disparity(
        self, 
        coefficient_of_variation: float, 
        amplitude_percentage: float
    ) -> str:
        """Classifica disparidade regional."""
        return self.interpreter.classify_regional_disparity(
            coefficient_of_variation, amplitude_percentage
        )
    
    def _filter_data_for_analysis(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filtra dados para análise específica."""
        return data.copy()  # Implementar lógica de filtro conforme necessário
    
    def _calculate_central_tendency(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calcula medidas de tendência central."""
        percentual_series = data['Percentual']
        
        return {
            'mean': self.calculator.safe_calc.safe_mean(percentual_series),
            'median': self.calculator.safe_calc.safe_median(percentual_series)
        }
    
    def _calculate_variability_measures(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calcula medidas de variabilidade."""
        percentual_series = data['Percentual']
        
        std_dev = self.calculator.safe_calc.safe_std(percentual_series)
        cv = self.variability_calc.calculate_coefficient_of_variation(percentual_series)
        range_stats = self.variability_calc.calculate_range_statistics(percentual_series)
        gini = self.variability_calc.calculate_gini_coefficient(percentual_series)
        
        return {
            'std_dev': round(std_dev, 2),
            'coefficient_of_variation': round(cv, 2),
            'range': round(range_stats['range'], 2),
            'percentage_range': round(range_stats['percentage_range'], 2),
            'gini_index': round(gini, 3)
        }
    
    def _identify_extreme_values(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identifica valores extremos."""
        try:
            # Calcular percentis para identificar extremos
            percentil_75 = data['Percentual'].quantile(0.75)
            percentil_25 = data['Percentual'].quantile(0.25)
            
            # Identificar máximos e mínimos
            max_idx = data['Percentual'].idxmax()
            min_idx = data['Percentual'].idxmin()
            
            return {
                'maximum': data.loc[max_idx].copy() if max_idx in data.index else None,
                'minimum': data.loc[min_idx].copy() if min_idx in data.index else None,
                'above_threshold': data[data['Percentual'] >= percentil_75],
                'below_threshold': data[data['Percentual'] <= percentil_25]
            }
        except Exception:
            return {
                'maximum': None,
                'minimum': None,
                'above_threshold': pd.DataFrame(),
                'below_threshold': pd.DataFrame()
            }
    
    def _generate_classifications(self, variability: Dict[str, float]) -> Dict[str, str]:
        """Gera classificações baseadas na variabilidade."""
        cv = variability['coefficient_of_variation']
        amplitude_perc = variability['percentage_range']
        
        return {
            'variability_level': self.interpreter.interpret_regional_variability(cv),
            'disparity_level': self.interpreter.classify_regional_disparity(cv, amplitude_perc)
        }


class SocialCategoryStatsCalculator(IStatisticsCalculator):
    """Calculador de estatísticas por categoria social."""
    
    def __init__(self):
        self.validator = BaseDataValidator()
        self.calculator = DistributionCalculator()
    
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida entrada para cálculo por categoria."""
        required_columns = ['Estado', 'Categoria', 'Percentual']
        return self.validator.validate(data, required_columns)
    
    @optimized_cache(ttl=1800)
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Calcula estatísticas agregadas por categoria.
        
        Args:
            data: DataFrame com dados por estado e categoria
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dict com estatísticas por categoria
        """
        return self.calculate_statistics_by_category(data)
    
    def calculate_statistics_by_category(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Calcula estatísticas para cada categoria social.
        
        Args:
            data: DataFrame com dados por estado e categoria
            
        Returns:
            Dict com estatísticas por categoria
        """
        if not self.validate_input(data):
            return {}
        
        try:
            results = {}
            categories = data['Categoria'].unique()
            
            for category in categories:
                category_data = data[data['Categoria'] == category]
                
                if len(category_data) < 3:  # Mínimo de 3 estados
                    continue
                
                percentual_series = category_data['Percentual']
                basic_stats = self.calculator.calculate_basic_stats(percentual_series)
                
                # Calcular coeficiente de variação
                cv = (basic_stats['std_dev'] / basic_stats['mean'] * 100) if basic_stats['mean'] > 0 else 0
                
                results[category] = {
                    'percentual_medio': round(basic_stats['mean'], 2),
                    'desvio_padrao': round(basic_stats['std_dev'], 2),
                    'coef_variacao': round(cv, 2),
                    'n_estados': len(category_data),
                    'min': round(basic_stats['min'], 2),
                    'max': round(basic_stats['max'], 2),
                    'amplitude': round(basic_stats['max'] - basic_stats['min'], 2)
                }
            
            return results
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas por categoria: {e}")
            return {}
