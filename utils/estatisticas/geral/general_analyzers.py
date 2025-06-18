"""
Analisadores modulares para estatísticas gerais seguindo princípios SOLID.
Criado como parte da refatoração para melhorar modularidade e performance.
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple, Union
from ..interfaces import (
    DataValidator, ResultBuilder, CorrelationAnalyzer,
    DistributionAnalyzer, RegionalAnalyzer
)


class GeneralDataValidator(DataValidator):
    """Validador de dados para análises gerais."""
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Valida se o DataFrame contém dados suficientes para análise."""
        if data is None or data.empty:
            st.error("DataFrame vazio ou nulo")
            return False
        
        if len(data) < 2:
            st.warning("Dados insuficientes para análise estatística")
            return False
        
        return True
    
    def validate_columns(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """Valida se as colunas necessárias estão presentes."""
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(f"Colunas ausentes: {missing_columns}")
            return False
        return True


class GeneralResultBuilder(ResultBuilder):
    """Construtor de resultados para análises gerais."""
    
    def build_summary(self, data: pd.DataFrame, analysis_type: str) -> Dict[str, Any]:
        """Constrói resumo das estatísticas gerais."""
        return {
            'total_registros': len(data),
            'analysis_type': analysis_type,
            'timestamp': pd.Timestamp.now().isoformat(),
            'data_shape': data.shape
        }
    
    def build_empty_result(self, message: str = "Dados insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio com mensagem."""
        return {
            'status': 'empty',
            'message': message,
            'data': {},
            'timestamp': pd.Timestamp.now().isoformat()
        }


class BasicStatsCalculator:
    """Calculador de estatísticas básicas."""
    
    def calculate_descriptive_stats(self, data: pd.Series) -> Dict[str, float]:
        """Calcula estatísticas descritivas básicas."""
        try:
            return {
                'count': int(data.count()),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'var': float(data.var()),
                'min': float(data.min()),
                'max': float(data.max()),
                'range': float(data.max() - data.min()),
                'q1': float(data.quantile(0.25)),
                'q3': float(data.quantile(0.75)),
                'iqr': float(data.quantile(0.75) - data.quantile(0.25))
            }
        except Exception as e:
            return self._empty_stats()
    
    def calculate_distribution_metrics(self, data: pd.Series) -> Dict[str, float]:
        """Calcula métricas de distribuição."""
        try:
            from scipy import stats
            
            # Calcular assimetria e curtose
            skewness = stats.skew(data.dropna())
            kurtosis = stats.kurtosis(data.dropna())
            
            # Calcular coeficiente de variação
            cv = (data.std() / data.mean() * 100) if data.mean() != 0 else 0
            
            return {
                'skewness': float(skewness),
                'kurtosis': float(kurtosis),
                'cv': float(cv)
            }
        except Exception:
            return {
                'skewness': 0.0,
                'kurtosis': 0.0,
                'cv': 0.0
            }
    
    def _empty_stats(self) -> Dict[str, float]:
        """Retorna estatísticas vazias."""
        return {
            'count': 0, 'mean': 0.0, 'median': 0.0, 'std': 0.0,
            'var': 0.0, 'min': 0.0, 'max': 0.0, 'range': 0.0,
            'q1': 0.0, 'q3': 0.0, 'iqr': 0.0
        }


class GeneralDistributionAnalyzer(DistributionAnalyzer):
    """Analisador de distribuições para estatísticas gerais."""
    
    def __init__(self):
        self.validator = GeneralDataValidator()
        self.stats_calc = BasicStatsCalculator()
    
    def analyze_distribution(self, data: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Analisa distribuição de uma variável."""
        if not self.validator.validate_columns(data, [column]):
            return {'error': f"Coluna '{column}' não encontrada"}
        
        series = data[column].dropna()
        
        if len(series) < 2:
            return {'error': 'Dados insuficientes para análise'}
        
        # Calcular estatísticas básicas
        basic_stats = self.stats_calc.calculate_descriptive_stats(series)
        
        # Calcular métricas de distribuição
        distribution_metrics = self.stats_calc.calculate_distribution_metrics(series)
        
        # Combinar resultados
        result = {
            'column': column,
            'basic_stats': basic_stats,
            'distribution_metrics': distribution_metrics,
            'data_type': str(series.dtype),
            'unique_values': int(series.nunique())
        }
        
        # Adicionar análise específica por tipo
        if series.dtype in ['object', 'category']:
            result['value_counts'] = series.value_counts().to_dict()
            result['analysis_type'] = 'categorical'
        else:
            result['histogram_data'] = self._calculate_histogram_data(series)
            result['analysis_type'] = 'numerical'
        
        return result
    
    def _calculate_histogram_data(self, series: pd.Series, bins: int = 10) -> Dict[str, Any]:
        """Calcula dados para histograma."""
        try:
            counts, bin_edges = np.histogram(series, bins=bins)
            return {
                'counts': counts.tolist(),
                'bin_edges': bin_edges.tolist(),
                'bins': bins
            }
        except Exception:
            return {'counts': [], 'bin_edges': [], 'bins': 0}


class GeneralCorrelationAnalyzer(CorrelationAnalyzer):
    """Analisador de correlações para estatísticas gerais."""
    
    def __init__(self):
        self.validator = GeneralDataValidator()
    
    def calculate_correlation(self, data: pd.DataFrame, variables: List[str]) -> pd.DataFrame:
        """Calcula matriz de correlação."""
        if not self.validator.validate_columns(data, variables):
            return pd.DataFrame()
        
        # Selecionar apenas colunas numéricas
        numeric_data = data[variables].select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            return pd.DataFrame()
        
        return numeric_data.corr()
    
    def calculate_pairwise_correlation(
        self, 
        data: pd.DataFrame, 
        var1: str, 
        var2: str
    ) -> Dict[str, Any]:
        """Calcula correlação entre duas variáveis específicas."""
        if not self.validator.validate_columns(data, [var1, var2]):
            return {'error': 'Variáveis não encontradas'}
        
        # Remover valores nulos
        clean_data = data[[var1, var2]].dropna()
        
        if len(clean_data) < 3:
            return {'error': 'Dados insuficientes para correlação'}
        
        try:
            from scipy.stats import pearsonr, spearmanr
            
            # Correlação de Pearson
            pearson_corr, pearson_p = pearsonr(clean_data[var1], clean_data[var2])
            
            # Correlação de Spearman
            spearman_corr, spearman_p = spearmanr(clean_data[var1], clean_data[var2])
            
            return {
                'pearson_correlation': float(pearson_corr),
                'pearson_pvalue': float(pearson_p),
                'spearman_correlation': float(spearman_corr),
                'spearman_pvalue': float(spearman_p),
                'sample_size': len(clean_data),
                'interpretation': self._interpret_correlation(pearson_corr)
            }
        except Exception as e:
            return {'error': f'Erro no cálculo: {str(e)}'}
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpreta força da correlação."""
        abs_corr = abs(correlation)
        
        if abs_corr < 0.1:
            return 'negligível'
        elif abs_corr < 0.3:
            return 'fraca'
        elif abs_corr < 0.5:
            return 'moderada'
        elif abs_corr < 0.7:
            return 'forte'
        else:
            return 'muito forte'


class GeneralRegionalAnalyzer(RegionalAnalyzer):
    """Analisador regional para estatísticas gerais."""
    
    def __init__(self):
        self.validator = GeneralDataValidator()
        self.stats_calc = BasicStatsCalculator()
    
    def analyze_by_region(self, data: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """Analisa métricas por região."""
        # Criar coluna REGIAO se não existir
        if 'REGIAO' not in data.columns:
            data = self._add_region_column(data)
        
        if 'REGIAO' not in data.columns:
            return {'error': 'Não foi possível determinar região'}
        
        regional_analysis = {}
        
        for region in data['REGIAO'].unique():
            if pd.notna(region):
                region_data = data[data['REGIAO'] == region]
                regional_analysis[region] = self._analyze_region_data(region_data, metric)
        
        return {
            'regional_data': regional_analysis,
            'summary': self._generate_regional_summary(regional_analysis),
            'total_regions': len(regional_analysis)
        }
    
    def _add_region_column(self, data: pd.DataFrame) -> pd.DataFrame:
        """Adiciona coluna REGIAO (será migrada para pré-processamento)."""
        regiao_mapping = {
            'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte',
            'BA': 'Nordeste', 'CE': 'Nordeste', 'DF': 'Centro-Oeste',
            'ES': 'Sudeste', 'GO': 'Centro-Oeste', 'MA': 'Nordeste',
            'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MG': 'Sudeste',
            'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul', 'PE': 'Nordeste',
            'PI': 'Nordeste', 'RJ': 'Sudeste', 'RN': 'Nordeste',
            'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte', 'SC': 'Sul',
            'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
        }
        
        # Tentar diferentes colunas de UF
        uf_columns = ['SG_UF_NASCIMENTO', 'SG_UF_ESC', 'SG_UF_PROVA', 'UF']
        
        for uf_col in uf_columns:
            if uf_col in data.columns:
                data['REGIAO'] = data[uf_col].map(regiao_mapping)
                break
        
        return data
    
    def _analyze_region_data(self, region_data: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """Analisa dados de uma região específica."""
        analysis = {
            'total_registros': len(region_data),
            'percentual_do_total': 0  # Será calculado posteriormente
        }
        
        # Análise específica por métrica
        if metric in region_data.columns:
            if region_data[metric].dtype in ['object', 'category']:
                analysis['distribuicao'] = region_data[metric].value_counts().to_dict()
            else:
                stats = self.stats_calc.calculate_descriptive_stats(region_data[metric])
                analysis['estatisticas'] = stats
        
        return analysis
    
    def _generate_regional_summary(self, regional_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo da análise regional."""
        if not regional_analysis:
            return {}
        
        total_records = sum(region.get('total_registros', 0) for region in regional_analysis.values())
        
        # Calcular percentuais
        for region_name, region_data in regional_analysis.items():
            if total_records > 0:
                region_data['percentual_do_total'] = (
                    region_data.get('total_registros', 0) / total_records * 100
                )
        
        return {
            'total_registros': total_records,
            'numero_regioes': len(regional_analysis),
            'regiao_maior': max(regional_analysis.keys(), 
                              key=lambda x: regional_analysis[x].get('total_registros', 0)),
            'regiao_menor': min(regional_analysis.keys(), 
                              key=lambda x: regional_analysis[x].get('total_registros', 0))
        }


class DataQualityAnalyzer:
    """Analisador de qualidade dos dados."""
    
    def __init__(self):
        self.validator = GeneralDataValidator()
    
    def analyze_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa qualidade geral dos dados."""
        if not self.validator.validate(data):
            return {'error': 'Dados inválidos'}
        
        quality_report = {
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'missing_data': self._analyze_missing_data(data),
            'data_types': self._analyze_data_types(data),
            'duplicates': self._analyze_duplicates(data),
            'outliers': self._analyze_outliers(data)
        }
        
        # Calcular score de qualidade
        quality_report['quality_score'] = self._calculate_quality_score(quality_report)
        
        return quality_report
    
    def _analyze_missing_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa dados faltantes."""
        missing_counts = data.isnull().sum()
        missing_percentages = (missing_counts / len(data) * 100).round(2)
        
        return {
            'total_missing': int(missing_counts.sum()),
            'columns_with_missing': int((missing_counts > 0).sum()),
            'missing_by_column': missing_counts.to_dict(),
            'missing_percentages': missing_percentages.to_dict(),
            'worst_column': missing_percentages.idxmax() if missing_percentages.max() > 0 else None,
            'worst_percentage': float(missing_percentages.max())
        }
    
    def _analyze_data_types(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa tipos de dados."""
        type_counts = data.dtypes.value_counts()
        
        return {
            'type_distribution': type_counts.to_dict(),
            'numeric_columns': int(data.select_dtypes(include=[np.number]).shape[1]),
            'categorical_columns': int(data.select_dtypes(include=['object', 'category']).shape[1]),
            'datetime_columns': int(data.select_dtypes(include=['datetime']).shape[1])
        }
    
    def _analyze_duplicates(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa registros duplicados."""
        total_duplicates = data.duplicated().sum()
        
        return {
            'total_duplicates': int(total_duplicates),
            'duplicate_percentage': float(total_duplicates / len(data) * 100),
            'unique_rows': int(len(data) - total_duplicates)
        }
    
    def _analyze_outliers(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa outliers em colunas numéricas."""
        numeric_data = data.select_dtypes(include=[np.number])
        outlier_info = {}
        
        for column in numeric_data.columns:
            series = numeric_data[column].dropna()
            if len(series) > 0:
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = series[(series < lower_bound) | (series > upper_bound)]
                
                outlier_info[column] = {
                    'count': len(outliers),
                    'percentage': float(len(outliers) / len(series) * 100),
                    'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)}
                }
        
        return outlier_info
    
    def _calculate_quality_score(self, quality_report: Dict[str, Any]) -> float:
        """Calcula score de qualidade dos dados (0-100)."""
        try:
            # Penalidades baseadas em problemas de qualidade
            score = 100.0
            
            # Penalidade por dados faltantes
            missing_penalty = quality_report['missing_data']['worst_percentage'] * 0.5
            score -= missing_penalty
            
            # Penalidade por duplicatas
            duplicate_penalty = quality_report['duplicates']['duplicate_percentage'] * 0.3
            score -= duplicate_penalty
            
            # Penalidade por outliers (média de outliers por coluna)
            outlier_percentages = [info['percentage'] for info in quality_report['outliers'].values()]
            if outlier_percentages:
                avg_outlier_percentage = sum(outlier_percentages) / len(outlier_percentages)
                outlier_penalty = avg_outlier_percentage * 0.2
                score -= outlier_penalty
            
            return max(0.0, min(100.0, score))
        except Exception:
            return 50.0  # Score neutro em caso de erro
