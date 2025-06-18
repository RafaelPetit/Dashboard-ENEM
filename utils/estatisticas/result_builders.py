"""
Construtores de resultados para estatísticas.
Implementa o padrão Builder para criar resultados estruturados.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
from .interfaces import IResultBuilder


class BaseResultBuilder(IResultBuilder):
    """Construtor base para resultados de estatísticas."""
    
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """
        Constrói um resultado vazio básico.
        
        Args:
            reason: Motivo pelo qual o resultado está vazio
            
        Returns:
            Dict com resultado vazio estruturado
        """
        return {
            'status': 'empty',
            'reason': reason,
            'message': f"Não foi possível calcular: {reason}",
            'data': {},
            'metadata': {
                'calculation_time': None,
                'sample_size': 0
            }
        }
    
    def build_result(self, calculations: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constrói o resultado final combinando cálculos e metadados.
        
        Args:
            calculations: Cálculos realizados
            metadata: Metadados adicionais
            
        Returns:
            Dict com resultado estruturado
        """
        return {
            'status': 'success',
            'reason': 'Cálculo realizado com sucesso',
            'message': 'Estatísticas calculadas',
            'data': calculations,
            'metadata': metadata
        }
    
    def add_interpretation(self, result: Dict[str, Any], interpretation: str) -> Dict[str, Any]:
        """
        Adiciona interpretação ao resultado.
        
        Args:
            result: Resultado base
            interpretation: Interpretação textual
            
        Returns:
            Resultado com interpretação adicionada
        """
        result['interpretation'] = interpretation
        return result


class DistributionResultBuilder(BaseResultBuilder):
    """Construtor específico para resultados de distribuição."""
    
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio para análise de distribuição."""
        return {
            'total': 0,
            'categoria_mais_frequente': None,
            'categoria_menos_frequente': None,
            'num_categorias': 0,
            'media': 0,
            'mediana': 0,
            'indice_concentracao': 0,
            'classificacao_concentracao': reason,
            'entropia': 0,
            'entropia_normalizada': 0,
            'razao_max_min': 0,
            'coef_variacao': 0,
            'desvio_padrao': 0,
            'status': 'empty',
            'reason': reason
        }
    
    def build_distribution_result(
        self,
        total: int,
        categories_stats: Dict[str, Any],
        concentration_stats: Dict[str, Any],
        variability_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constrói resultado completo de análise de distribuição.
        
        Args:
            total: Total de observações
            categories_stats: Estatísticas por categoria
            concentration_stats: Estatísticas de concentração
            variability_stats: Estatísticas de variabilidade
            
        Returns:
            Dict com resultado estruturado
        """
        return {
            'total': total,
            'categoria_mais_frequente': categories_stats.get('most_frequent'),
            'categoria_menos_frequente': categories_stats.get('least_frequent'),
            'num_categorias': categories_stats.get('count', 0),
            'media': variability_stats.get('mean', 0),
            'mediana': variability_stats.get('median', 0),
            'indice_concentracao': concentration_stats.get('gini_index', 0),
            'classificacao_concentracao': concentration_stats.get('classification', ''),
            'entropia': concentration_stats.get('entropy', 0),
            'entropia_normalizada': concentration_stats.get('normalized_entropy', 0),
            'razao_max_min': variability_stats.get('max_min_ratio', 0),
            'coef_variacao': variability_stats.get('coefficient_of_variation', 0),
            'desvio_padrao': variability_stats.get('std_dev', 0),
            'status': 'success'
        }


class CorrelationResultBuilder(BaseResultBuilder):
    """Construtor específico para resultados de correlação."""
    
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio para análise de correlação."""
        return {
            'qui_quadrado': 0,
            'gl': 0,
            'valor_p': 1,
            'coeficiente': 0,
            'v_cramer': 0,
            'info_mutua': 0,
            'info_mutua_norm': 0,
            'interpretacao': reason,
            'contexto': "Não foi possível calcular associação entre estas variáveis",
            'significativo': False,
            'tamanho_efeito': "indefinido",
            'tabela_contingencia': pd.DataFrame(),
            'n_amostras': 0,
            'status': 'empty',
            'reason': reason
        }
    
    def build_correlation_result(
        self,
        chi_square_stats: Dict[str, Any],
        association_metrics: Dict[str, Any],
        interpretation: Dict[str, Any],
        contingency_table: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Constrói resultado completo de análise de correlação.
        
        Args:
            chi_square_stats: Estatísticas do teste qui-quadrado
            association_metrics: Métricas de associação
            interpretation: Interpretações textuais
            contingency_table: Tabela de contingência
            
        Returns:
            Dict com resultado estruturado
        """
        return {
            'qui_quadrado': chi_square_stats.get('chi2', 0),
            'gl': chi_square_stats.get('degrees_freedom', 0),
            'valor_p': chi_square_stats.get('p_value', 1),
            'coeficiente': association_metrics.get('contingency_coefficient', 0),
            'v_cramer': association_metrics.get('cramers_v', 0),
            'info_mutua': association_metrics.get('mutual_information', 0),
            'info_mutua_norm': association_metrics.get('normalized_mutual_info', 0),
            'interpretacao': interpretation.get('strength', ''),
            'contexto': interpretation.get('context', ''),
            'significativo': chi_square_stats.get('p_value', 1) < 0.05,
            'tamanho_efeito': interpretation.get('effect_size', ''),
            'tabela_contingencia': contingency_table,
            'n_amostras': contingency_table.sum().sum() if not contingency_table.empty else 0,
            'status': 'success'
        }


class PerformanceResultBuilder(BaseResultBuilder):
    """Construtor específico para resultados de desempenho."""
    
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio para análise de desempenho."""
        return {
            'melhor_estado': None,
            'pior_estado': None,
            'media_geral': 0,
            'desvio_padrao': 0,
            'coef_variacao': 0,
            'diferenca_percentual': 0,
            'status': 'empty',
            'reason': reason
        }
    
    def build_performance_result(
        self,
        best_performer: Dict[str, Any],
        worst_performer: Dict[str, Any],
        general_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constrói resultado completo de análise de desempenho.
        
        Args:
            best_performer: Dados do melhor desempenho
            worst_performer: Dados do pior desempenho
            general_stats: Estatísticas gerais
            
        Returns:
            Dict com resultado estruturado
        """
        return {
            'melhor_estado': best_performer,
            'pior_estado': worst_performer,
            'media_geral': general_stats.get('mean', 0),
            'desvio_padrao': general_stats.get('std_dev', 0),
            'coef_variacao': general_stats.get('coefficient_of_variation', 0),
            'diferenca_percentual': general_stats.get('percentage_difference', 0),
            'status': 'success'
        }


class RegionalResultBuilder(BaseResultBuilder):
    """Construtor específico para resultados regionais."""
    
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio para análise regional."""
        return {
            'percentual_medio': 0,
            'desvio_padrao': 0,
            'coef_variacao': 0,
            'amplitude': 0,
            'amplitude_percentual': 0,
            'maior_percentual': None,
            'menor_percentual': None,
            'variabilidade': reason,
            'estados_acima': pd.DataFrame(),
            'estados_abaixo': pd.DataFrame(),
            'indice_gini': 0,
            'disparidade': "indefinida",
            'status': 'empty',
            'reason': reason
        }
    
    def build_regional_result(
        self,
        central_tendency: Dict[str, Any],
        variability: Dict[str, Any],
        extremes: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constrói resultado completo de análise regional.
        
        Args:
            central_tendency: Medidas de tendência central
            variability: Medidas de variabilidade
            extremes: Valores extremos
            classification: Classificações e interpretações
            
        Returns:
            Dict com resultado estruturado
        """
        return {
            'percentual_medio': central_tendency.get('mean', 0),
            'desvio_padrao': variability.get('std_dev', 0),
            'coef_variacao': variability.get('coefficient_of_variation', 0),
            'amplitude': variability.get('range', 0),
            'amplitude_percentual': variability.get('percentage_range', 0),
            'maior_percentual': extremes.get('maximum'),
            'menor_percentual': extremes.get('minimum'),
            'variabilidade': classification.get('variability_level', ''),
            'estados_acima': extremes.get('above_threshold', pd.DataFrame()),
            'estados_abaixo': extremes.get('below_threshold', pd.DataFrame()),
            'indice_gini': variability.get('gini_index', 0),
            'disparidade': classification.get('disparity_level', ''),
            'status': 'success'
        }


class ComparativeResultBuilder(BaseResultBuilder):
    """Construtor específico para resultados comparativos."""
    
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio para análise comparativa."""
        return {
            'maior_disparidade': {
                'competencia': None, 'diferenca': 0, 'diferenca_percentual': 0,
                'categoria_max': None, 'categoria_min': None, 'valor_max': 0, 'valor_min': 0,
                'razao_max_min': 0, 'coef_variacao': 0
            },
            'menor_disparidade': {
                'competencia': None, 'diferenca': 0, 'diferenca_percentual': 0,
                'categoria_max': None, 'categoria_min': None, 'valor_max': 0, 'valor_min': 0,
                'razao_max_min': 0, 'coef_variacao': 0
            },
            'disparidades_por_competencia': {},
            'indicadores_globais': {
                'razao_max_min': 0,
                'coef_variacao': 0,
                'range_percentual': 0
            },
            'status': 'empty',
            'reason': reason
        }
    
    def build_comparative_result(
        self,
        largest_disparity: Dict[str, Any],
        smallest_disparity: Dict[str, Any],
        disparities_by_subject: Dict[str, Any],
        global_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Constrói resultado completo de análise comparativa.
        
        Args:
            largest_disparity: Maior disparidade encontrada
            smallest_disparity: Menor disparidade encontrada
            disparities_by_subject: Disparidades por competência
            global_indicators: Indicadores globais
            
        Returns:
            Dict com resultado estruturado
        """
        return {
            'maior_disparidade': largest_disparity,
            'menor_disparidade': smallest_disparity,
            'disparidades_por_competencia': disparities_by_subject,
            'indicadores_globais': global_indicators,
            'status': 'success'
        }
