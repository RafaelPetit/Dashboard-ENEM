"""
Analisador de tendências temporais para aspectos sociais.
Implementa análise específica de evolução temporal.
"""
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from scipy import stats
from ..interfaces import IStatisticsCalculator
from ..validators import BaseDataValidator
from ..calculators import SafeCalculator
from ..result_builders import BaseResultBuilder
from ..interpreters import TrendInterpreter
from utils.helpers.cache_utils import memory_intensive_function


class SocialTrendAnalyzer(IStatisticsCalculator):
    """Analisador de tendências temporais para aspectos sociais."""
    
    def __init__(self):
        self.validator = BaseDataValidator()
        self.safe_calc = SafeCalculator()
        self.result_builder = BaseResultBuilder()
        self.interpreter = TrendInterpreter()
    
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida entrada para análise de tendências."""
        required_columns = ['Ano', 'Categoria', 'Percentual']
        return self.validator.validate(data, required_columns)
    
    @memory_intensive_function
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Analisa tendências temporais de aspectos sociais.
        
        Args:
            data: DataFrame com dados históricos
            **kwargs: Parâmetros como 'aspecto_social' e 'categoria'
            
        Returns:
            Dict com análise de tendências
        """
        aspecto_social = kwargs.get('aspecto_social', '')
        categoria = kwargs.get('categoria')
        
        return self.analyze_temporal_trends(data, aspecto_social, categoria)
    
    def analyze_temporal_trends(
        self, 
        data: pd.DataFrame, 
        aspecto_social: str, 
        categoria: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analisa tendências temporais de um aspecto social.
        
        Args:
            data: DataFrame com dados históricos
            aspecto_social: Nome do aspecto social analisado
            categoria: Categoria específica para análise
            
        Returns:
            Dict com análise de tendências
        """
        if not self.validate_input(data):
            return self._build_empty_trend_result()
        
        try:
            # Filtrar dados para categoria específica se necessário
            analysis_data = self._filter_for_category(data, categoria)
            
            if len(analysis_data) < 3:
                return self._build_empty_trend_result("Pontos temporais insuficientes")
            
            # Ordenar por ano
            analysis_data = analysis_data.sort_values('Ano')
            
            # Calcular regressão linear
            trend_stats = self._calculate_linear_trend(analysis_data)
            
            # Calcular variação percentual
            variation_stats = self._calculate_percentage_variation(analysis_data)
            
            # Gerar interpretações
            interpretations = self._generate_trend_interpretations(trend_stats, variation_stats)
            
            # Construir resultado
            return {
                'tendencia': interpretations['trend_description'],
                'slope': round(trend_stats['slope'], 4),
                'r_squared': round(trend_stats['r_squared'], 3),
                'p_value': round(trend_stats['p_value'], 4),
                'significativa': trend_stats['p_value'] < 0.05,
                'variacao_percentual': round(variation_stats['percentage_change'], 2),
                'primeiro_valor': round(variation_stats['first_value'], 2),
                'ultimo_valor': round(variation_stats['last_value'], 2),
                'descricao': interpretations['change_description'],
                'mensagem': interpretations['summary_message'],
                'status': 'success'
            }
            
        except Exception as e:
            return self._build_empty_trend_result(f"Erro na análise: {str(e)}")
    
    def _filter_for_category(self, data: pd.DataFrame, categoria: Optional[str]) -> pd.DataFrame:
        """Filtra dados para categoria específica."""
        if categoria and 'Categoria' in data.columns:
            filtered = data[data['Categoria'] == categoria].copy()
            return filtered if not filtered.empty else data.copy()
        return data.copy()
    
    def _calculate_linear_trend(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calcula tendência linear usando regressão."""
        try:
            x = data['Ano'].astype(float)
            y = data['Percentual']
            
            # Remover valores inválidos
            valid_mask = np.isfinite(x) & np.isfinite(y)
            x_valid = x[valid_mask]
            y_valid = y[valid_mask]
            
            if len(x_valid) < 2:
                return {'slope': 0, 'r_squared': 0, 'p_value': 1}
            
            # Calcular regressão linear
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, y_valid)
            
            return {
                'slope': float(slope) if np.isfinite(slope) else 0,
                'intercept': float(intercept) if np.isfinite(intercept) else 0,
                'r_value': float(r_value) if np.isfinite(r_value) else 0,
                'r_squared': float(r_value**2) if np.isfinite(r_value) else 0,
                'p_value': float(p_value) if np.isfinite(p_value) else 1,
                'std_err': float(std_err) if np.isfinite(std_err) else 0
            }
            
        except Exception:
            return {'slope': 0, 'r_squared': 0, 'p_value': 1}
    
    def _calculate_percentage_variation(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calcula variação percentual entre primeiro e último período."""
        try:
            first_value = data.iloc[0]['Percentual']
            last_value = data.iloc[-1]['Percentual']
            
            percentage_change = 0.0
            if first_value > 0:
                percentage_change = ((last_value - first_value) / first_value) * 100
            
            return {
                'first_value': float(first_value),
                'last_value': float(last_value),
                'absolute_change': float(last_value - first_value),
                'percentage_change': float(percentage_change)
            }
            
        except Exception:
            return {
                'first_value': 0.0,
                'last_value': 0.0,
                'absolute_change': 0.0,
                'percentage_change': 0.0
            }
    
    def _generate_trend_interpretations(
        self, 
        trend_stats: Dict[str, float], 
        variation_stats: Dict[str, float]
    ) -> Dict[str, str]:
        """Gera interpretações das tendências."""
        # Interpretar direção e força da tendência
        trend_description = self.interpreter.interpret_trend_direction(
            trend_stats['slope'], trend_stats['r_squared']
        )
        
        # Interpretar mudança percentual
        change_description = self.interpreter.interpret_percentage_change(
            variation_stats['percentage_change']
        )
        
        # Criar mensagem resumo
        r_squared = trend_stats['r_squared']
        summary_message = f"Tendência {trend_description} (R² = {r_squared:.2f})"
        
        return {
            'trend_description': trend_description,
            'change_description': change_description,
            'summary_message': summary_message
        }
    
    def _build_empty_trend_result(self, reason: str = "Dados históricos insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio para análise de tendências."""
        return {
            'tendencia': 'indefinida',
            'slope': 0.0,
            'r_squared': 0.0,
            'p_value': 1.0,
            'significativa': False,
            'variacao_percentual': 0.0,
            'primeiro_valor': 0.0,
            'ultimo_valor': 0.0,
            'descricao': reason,
            'mensagem': reason,
            'status': 'empty',
            'reason': reason
        }


class SocialDataAggregator:
    """Agregador de dados para análises sociais."""
    
    def __init__(self):
        self.safe_calc = SafeCalculator()
    
    def aggregate_by_time_period(
        self, 
        data: pd.DataFrame, 
        time_column: str = 'Ano',
        value_column: str = 'Percentual',
        category_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Agrega dados por período temporal.
        
        Args:
            data: DataFrame com dados brutos
            time_column: Coluna com informação temporal
            value_column: Coluna com valores a agregar
            category_column: Coluna de categoria (opcional)
            
        Returns:
            DataFrame agregado por período
        """
        try:
            if category_column and category_column in data.columns:
                # Agregar por tempo e categoria
                group_columns = [time_column, category_column]
            else:
                # Agregar apenas por tempo
                group_columns = [time_column]
            
            # Realizar agregação
            aggregated = data.groupby(group_columns)[value_column].agg([
                'mean', 'median', 'std', 'count'
            ]).reset_index()
            
            # Renomear colunas
            aggregated.columns = group_columns + ['Media', 'Mediana', 'DesvPadrao', 'Contagem']
            
            return aggregated
            
        except Exception as e:
            print(f"Erro na agregação temporal: {e}")
            return pd.DataFrame()
    
    def calculate_year_over_year_change(
        self, 
        data: pd.DataFrame, 
        time_column: str = 'Ano',
        value_column: str = 'Media'
    ) -> pd.DataFrame:
        """
        Calcula variação ano a ano.
        
        Args:
            data: DataFrame com dados agregados
            time_column: Coluna com anos
            value_column: Coluna com valores
            
        Returns:
            DataFrame com variações calculadas
        """
        try:
            # Ordenar por tempo
            sorted_data = data.sort_values(time_column)
            
            # Calcular variações
            sorted_data['Variacao_Absoluta'] = sorted_data[value_column].diff()
            sorted_data['Variacao_Percentual'] = sorted_data[value_column].pct_change() * 100
            
            # Preencher primeiros valores
            sorted_data['Variacao_Absoluta'].iloc[0] = 0
            sorted_data['Variacao_Percentual'].iloc[0] = 0
            
            return sorted_data
            
        except Exception as e:
            print(f"Erro no cálculo de variação: {e}")
            return data.copy()
    
    def identify_trend_breakpoints(
        self, 
        data: pd.DataFrame, 
        value_column: str = 'Media',
        min_segment_length: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identifica pontos de quebra na tendência.
        
        Args:
            data: DataFrame com dados temporais
            value_column: Coluna com valores
            min_segment_length: Tamanho mínimo do segmento
            
        Returns:
            Lista com informações dos pontos de quebra
        """
        try:
            if len(data) < min_segment_length * 2:
                return []
            
            # Implementação simplificada - pode ser expandida
            values = data[value_column].values
            breakpoints = []
            
            # Identificar mudanças significativas na derivada
            derivatives = np.gradient(values)
            derivative_changes = np.gradient(derivatives)
            
            # Encontrar pontos com mudanças abruptas
            threshold = np.std(derivative_changes) * 2
            significant_changes = np.where(np.abs(derivative_changes) > threshold)[0]
            
            for idx in significant_changes:
                if min_segment_length <= idx < len(data) - min_segment_length:
                    breakpoints.append({
                        'index': int(idx),
                        'value': float(values[idx]),
                        'change_magnitude': float(derivative_changes[idx])
                    })
            
            return breakpoints
            
        except Exception as e:
            print(f"Erro na identificação de pontos de quebra: {e}")
            return []
