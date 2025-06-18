"""
Analisadores de desempenho modulares seguindo princípios SOLID.
Cada classe tem uma responsabilidade específica e bem definida.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function
from utils.estatisticas.metricas_desempenho import calcular_indicadores_desigualdade
from utils.mappings import get_mappings
from ..interfaces import IPerformanceAnalyzer, IStatisticsCalculator, IDataValidator, IResultBuilder


class PerformanceDataValidator(IDataValidator):
    """
    Validador especializado para dados de desempenho.
    Responsabilidade: Validar integridade dos dados de entrada.
    """
    
    def validate(self, data: pd.DataFrame, required_columns: Optional[List[str]] = None) -> bool:
        """Valida se os dados atendem aos requisitos para análise de desempenho."""
        if data is None or data.empty:
            return False
        
        if required_columns is None:
            required_columns = []
            
        if required_columns and not all(col in data.columns for col in required_columns):
            return False
            
        # Verificar se há dados válidos (notas > 0)
        for col in required_columns:
            if col.startswith('NU_NOTA_'):
                if (data[col] > 0).sum() == 0:
                    return False
                    
        return True
    
    def get_validation_errors(self, data: pd.DataFrame, required_columns: List[str]) -> List[str]:
        """Retorna lista de erros de validação específicos para desempenho."""
        errors = []
        
        if data is None or data.empty:
            errors.append("DataFrame está vazio ou nulo")
            return errors
            
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            errors.append(f"Colunas obrigatórias não encontradas: {missing_columns}")
            
        for col in required_columns:
            if col in data.columns and col.startswith('NU_NOTA_'):
                valid_count = (data[col] > 0).sum()
                if valid_count == 0:
                    errors.append(f"Nenhuma nota válida encontrada na coluna {col}")
                elif valid_count < 10:
                    errors.append(f"Poucas amostras válidas na coluna {col}: {valid_count}")
                    
        return errors


class PerformanceResultBuilder(IResultBuilder):
    """
    Construtor de resultados para análises de desempenho.
    Responsabilidade: Padronizar a estrutura dos resultados.
    """
    
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """Constrói resultado vazio padrão para análises de desempenho."""
        return {
            'melhor_estado': None,
            'pior_estado': None,
            'media_geral': 0,
            'desvio_padrao': 0,
            'coef_variacao': 0,
            'diferenca_percentual': 0,
            'total_amostras': 0,
            'motivo': reason,
            'valido': False
        }
    
    def build_result(self, calculations: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói resultado estruturado para análise de desempenho."""
        result = {
            'melhor_estado': calculations.get('melhor_estado'),
            'pior_estado': calculations.get('pior_estado'),
            'media_geral': round(calculations.get('media_geral', 0), 2),
            'desvio_padrao': round(calculations.get('desvio_padrao', 0), 2),
            'coef_variacao': round(calculations.get('coef_variacao', 0), 2),
            'diferenca_percentual': round(calculations.get('diferenca_percentual', 0), 2),
            'total_amostras': metadata.get('total_amostras', 0),
            'area_analisada': metadata.get('area_selecionada', 'Todas'),
            'valido': True
        }
        
        return result
    
    def build_comparative_result(self, disparities: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói resultado para análise comparativa."""
        return {
            'maior_disparidade': disparities.get('maior_disparidade', {}),
            'menor_disparidade': disparities.get('menor_disparidade', {}),
            'disparidades_por_competencia': disparities.get('disparidades_por_competencia', {}),
            'indicadores_globais': disparities.get('indicadores_globais', {}),
            'total_competencias_analisadas': len(disparities.get('disparidades_por_competencia', {}))
        }


class CorrelationCalculator(IStatisticsCalculator):
    """
    Calculador especializado em correlações entre competências.
    Responsabilidade: Calcular e interpretar correlações.
    """
    
    def __init__(self):
        mappings = get_mappings()
        self.limiares = mappings['limiares_estatisticos']
        self.min_amostras = mappings['limiares_processamento']['min_amostras_correlacao']
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Calcula correlação entre duas competências."""
        eixo_x = kwargs.get('eixo_x')
        eixo_y = kwargs.get('eixo_y')
        
        if not self.validate_input(data, eixo_x=eixo_x, eixo_y=eixo_y):
            return {'correlacao': 0.0, 'interpretacao': 'Dados insuficientes', 'valido': False}
        
        # Filtrar dados válidos
        df_valido = data[(data[eixo_x] > 0) & (data[eixo_y] > 0)].dropna(subset=[eixo_x, eixo_y])
        
        if len(df_valido) < self.min_amostras:
            return {
                'correlacao': 0.0, 
                'interpretacao': f'Amostras insuficientes (n={len(df_valido)})',
                'valido': False
            }
        
        try:
            correlacao = df_valido[eixo_x].corr(df_valido[eixo_y])
            
            if pd.isna(correlacao):
                return {'correlacao': 0.0, 'interpretacao': 'Correlação indefinida', 'valido': False}
            
            interpretacao = self._interpretar_correlacao(correlacao)
            
            return {
                'correlacao': round(correlacao, 4),
                'interpretacao': interpretacao,
                'amostras_utilizadas': len(df_valido),
                'valido': True
            }
            
        except Exception as e:
            return {'correlacao': 0.0, 'interpretacao': f'Erro no cálculo: {str(e)}', 'valido': False}
    
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida entrada para cálculo de correlação."""
        eixo_x = kwargs.get('eixo_x')
        eixo_y = kwargs.get('eixo_y')
        
        if data is None or data.empty:
            return False
            
        if not eixo_x or not eixo_y:
            return False
            
        if eixo_x not in data.columns or eixo_y not in data.columns:
            return False
            
        return True
    
    def _interpretar_correlacao(self, correlacao: float) -> str:
        """Interpreta o valor da correlação."""
        abs_corr = abs(correlacao)
        
        if abs_corr < self.limiares['correlacao_fraca']:
            intensidade = "Fraca"
        elif abs_corr < self.limiares['correlacao_moderada']:
            intensidade = "Moderada"
        else:
            intensidade = "Forte"
        
        if correlacao > 0:
            direcao = " positiva"
        elif correlacao < 0:
            direcao = " negativa"
        else:
            return "Ausente"
        
        return intensidade + direcao


class DescriptiveStatisticsCalculator(IStatisticsCalculator):
    """
    Calculador de estatísticas descritivas.
    Responsabilidade: Calcular estatísticas básicas e percentis.
    """
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Calcula estatísticas descritivas para uma coluna."""
        coluna = kwargs.get('coluna')
        precisao = kwargs.get('precisao', 2)
        excluir_zeros = kwargs.get('excluir_zeros', True)
        
        if not self.validate_input(data, coluna=coluna):
            return self._empty_statistics()
        
        # Filtrar dados
        dados = data[coluna]
        if excluir_zeros:
            dados = dados[dados > 0]
        
        if dados.empty:
            return self._empty_statistics()
        
        try:
            return self._calculate_statistics(dados, precisao)
        except Exception as e:
            print(f"Erro ao calcular estatísticas descritivas: {e}")
            return self._empty_statistics()
    
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida entrada para estatísticas descritivas."""
        coluna = kwargs.get('coluna')
        
        if data is None or data.empty:
            return False
            
        if not coluna or coluna not in data.columns:
            return False
            
        return True
    
    def _calculate_statistics(self, dados: pd.Series, precisao: int) -> Dict[str, Any]:
        """Calcula as estatísticas básicas."""
        stats = dados.describe()
        
        return {
            'count': int(stats['count']),
            'mean': round(stats['mean'], precisao),
            'std': round(stats['std'], precisao),
            'min': round(stats['min'], precisao),
            '25%': round(stats['25%'], precisao),
            '50%': round(stats['50%'], precisao),
            '75%': round(stats['75%'], precisao),
            'max': round(stats['max'], precisao),
            'valido': True
        }
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas vazias."""
        return {
            'count': 0, 'mean': 0, 'std': 0, 'min': 0,
            '25%': 0, '50%': 0, '75%': 0, 'max': 0,
            'valido': False
        }


class StatePerformanceAnalyzer(IPerformanceAnalyzer):
    """
    Analisador de desempenho por estado.
    Responsabilidade: Analisar desempenho acadêmico por unidade federativa.
    """
    
    def __init__(self):
        self.validator = PerformanceDataValidator()
        self.result_builder = PerformanceResultBuilder()
    
    def analyze_performance_by_state(
        self, 
        data: pd.DataFrame, 
        performance_column: str,
        area_selecionada: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analisa desempenho por estado."""
        required_columns = ['Área', 'Estado', performance_column]
        
        if not self.validator.validate(data, required_columns):
            errors = self.validator.get_validation_errors(data, required_columns)
            return self.result_builder.build_empty_result(f"Validação falhou: {'; '.join(errors)}")
        
        # Filtrar por área específica
        area_para_analise = area_selecionada if area_selecionada else 'Média Geral'
        df_analise = data[data['Área'] == area_para_analise]
        
        if df_analise.empty:
            return self.result_builder.build_empty_result(f"Nenhum dado encontrado para área: {area_para_analise}")
        
        try:
            calculations = self._calculate_state_performance(df_analise, performance_column)
            metadata = {
                'total_amostras': len(df_analise),
                'area_selecionada': area_para_analise
            }
            
            return self.result_builder.build_result(calculations, metadata)
            
        except Exception as e:
            return self.result_builder.build_empty_result(f"Erro no cálculo: {str(e)}")
    
    def calculate_comparative_statistics(
        self, 
        data: pd.DataFrame, 
        category_column: str, 
        value_column: str
    ) -> Dict[str, Any]:
        """Calcula estatísticas comparativas entre categorias."""
        required_columns = [category_column, value_column, 'Competência']
        
        if not self.validator.validate(data, required_columns):
            return self.result_builder.build_comparative_result({})
        
        try:
            disparities = self._calculate_disparities_by_competence(data, category_column, value_column)
            return self.result_builder.build_comparative_result(disparities)
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas comparativas: {e}")
            return self.result_builder.build_comparative_result({})
    
    def _calculate_state_performance(self, df_analise: pd.DataFrame, performance_column: str) -> Dict[str, Any]:
        """Calcula métricas de desempenho por estado."""
        # Encontrar estados com melhor e pior desempenho
        indice_melhor = df_analise[performance_column].idxmax()
        indice_pior = df_analise[performance_column].idxmin()
        
        melhor_estado = df_analise.loc[indice_melhor] if indice_melhor in df_analise.index else None
        pior_estado = df_analise.loc[indice_pior] if indice_pior in df_analise.index else None
        
        # Calcular estatísticas gerais
        media_geral = df_analise[performance_column].mean()
        desvio_padrao = df_analise[performance_column].std()
        coef_variacao = (desvio_padrao / media_geral * 100) if media_geral > 0 else 0
        
        # Calcular diferença percentual
        if melhor_estado is not None and pior_estado is not None:
            diferenca_percentual = (
                (melhor_estado[performance_column] - pior_estado[performance_column]) / 
                pior_estado[performance_column] * 100
            ) if pior_estado[performance_column] > 0 else 0
        else:
            diferenca_percentual = 0
        
        return {
            'melhor_estado': melhor_estado,
            'pior_estado': pior_estado,
            'media_geral': media_geral,
            'desvio_padrao': desvio_padrao,
            'coef_variacao': coef_variacao,
            'diferenca_percentual': diferenca_percentual
        }
    
    def _calculate_disparities_by_competence(
        self, 
        df_resultados: pd.DataFrame, 
        category_column: str, 
        value_column: str
    ) -> Dict[str, Any]:
        """Calcula disparidades por competência."""
        competencias = df_resultados['Competência'].unique()
        
        disparities = {
            'maior_disparidade': {'competencia': None, 'diferenca': 0},
            'menor_disparidade': {'competencia': None, 'diferenca': float('inf')},
            'disparidades_por_competencia': {},
            'indicadores_globais': {}
        }
        
        # Calcular indicadores globais
        try:
            indicadores_globais = calcular_indicadores_desigualdade(
                df_resultados, 
                coluna_categoria=category_column,
                coluna_valor=value_column
            )
            disparities['indicadores_globais'] = indicadores_globais
        except Exception as e:
            print(f"Erro ao calcular indicadores globais: {e}")
        
        # Processar cada competência
        for competencia in competencias:
            df_comp = df_resultados[df_resultados['Competência'] == competencia]
            
            if len(df_comp) <= 1:
                continue
            
            competencia_metrics = self._process_competence_disparity(df_comp, category_column, value_column)
            disparities['disparidades_por_competencia'][competencia] = competencia_metrics
            
            # Atualizar maior e menor disparidade
            diferenca = competencia_metrics['diferenca']
            if diferenca > disparities['maior_disparidade']['diferenca']:
                disparities['maior_disparidade'] = {
                    'competencia': competencia,
                    'diferenca': diferenca,
                    **competencia_metrics
                }
            
            if diferenca < disparities['menor_disparidade']['diferenca'] and diferenca > 0:
                disparities['menor_disparidade'] = {
                    'competencia': competencia,
                    'diferenca': diferenca,
                    **competencia_metrics
                }
        
        # Ajustar menor disparidade se não foi encontrada
        if disparities['menor_disparidade']['diferenca'] == float('inf'):            disparities['menor_disparidade'] = {
                'competencia': None, 'diferenca': 0, 'categoria_max': None, 'categoria_min': None
            }
        
        return disparities

    def _process_competence_disparity(
        self, 
        df_comp: pd.DataFrame, 
        category_column: str, 
        value_column: str
    ) -> Dict[str, Any]:
        """Processa disparidade para uma competência específica."""
        max_valor = df_comp[value_column].max()
        min_valor = df_comp[value_column].min()
        
        try:
            categoria_max = df_comp.loc[df_comp[value_column].idxmax()][category_column]
            categoria_min = df_comp.loc[df_comp[value_column].idxmin()][category_column]
        except (KeyError, ValueError):
            # Método alternativo
            df_max = df_comp[df_comp[value_column] == max_valor].iloc[0]
            df_min = df_comp[df_comp[value_column] == min_valor].iloc[0]
            categoria_max = df_max[category_column]
            categoria_min = df_min[category_column]
        
        diferenca = max_valor - min_valor
        diferenca_percentual = (diferenca / min_valor * 100) if min_valor > 0 else 0
        
        # Calcular indicadores de desigualdade
        try:
            # Usar VariabilityAnalyzer para calcular indicadores
            variability_analyzer = VariabilityAnalyzer()
            indicadores = variability_analyzer.analyze_variability(
                df_comp
            )
        except Exception as e:
            print(f"Erro ao calcular indicadores: {e}")
            indicadores = {'razao_max_min': 0, 'coef_variacao': 0, 'range_percentual': 0}
        
        return {
            'diferenca': diferenca,
            'diferenca_percentual': diferenca_percentual,
            'categoria_max': categoria_max,
            'categoria_min': categoria_min,
            'valor_max': max_valor,
            'valor_min': min_valor,
            'razao_max_min': indicadores.get('razao_max_min', 0),
            'coef_variacao': indicadores.get('coef_variacao', 0)
        }
    
    def calculate_comparative_stats(
        self, 
        df_resultados: pd.DataFrame, 
        competencies: List[str]
    ) -> Dict[str, Any]:
        """
        Calcula estatísticas comparativas entre competências e categorias.
        
        Parâmetros:
        -----------
        df_resultados : DataFrame
            DataFrame com resultados por categoria
        competencies : List[str]
            Lista das competências para análise
            
        Retorna:
        --------
        Dict[str, Any]
            Dicionário com estatísticas comparativas
        """
        if not self.validator.validate(df_resultados, ['Categoria', 'Competência', 'Média']):
            return self.result_builder.build_empty_result("Dados inválidos para análise comparativa")
        
        try:
            comparative_results = {
                'disparidades_por_competencia': {},
                'ranking_competencias': {},
                'indicadores_globais': {},
                'maior_disparidade': {'competencia': None, 'diferenca': 0},
                'menor_disparidade': {'competencia': None, 'diferenca': float('inf')}
            }
            
            # Analisar cada competência
            for competencia in competencies:
                comp_data = df_resultados[df_resultados['Competência'] == competencia]
                
                if len(comp_data) >= 2:  # Pelo menos 2 categorias para comparar
                    comp_stats = self._process_competence_disparity(comp_data, 'Categoria', 'Média')
                    comparative_results['disparidades_por_competencia'][competencia] = comp_stats
                    
                    # Atualizar maior/menor disparidade
                    diferenca = comp_stats['diferenca']
                    if diferenca > comparative_results['maior_disparidade']['diferenca']:
                        comparative_results['maior_disparidade'] = {
                            'competencia': competencia,
                            'diferenca': diferenca,
                            **comp_stats
                        }
                    
                    if diferenca < comparative_results['menor_disparidade']['diferenca'] and diferenca > 0:
                        comparative_results['menor_disparidade'] = {
                            'competencia': competencia,
                            'diferenca': diferenca,
                            **comp_stats                        }
            
            # Calcular indicadores globais
            try:
                # Usar VariabilityAnalyzer para calcular indicadores
                variability_analyzer = VariabilityAnalyzer()
                indicadores_globais = variability_analyzer.analyze_variability(
                    df_resultados
                )
                comparative_results['indicadores_globais'] = indicadores_globais
            except Exception as e:
                print(f"Erro ao calcular indicadores globais: {e}")
                comparative_results['indicadores_globais'] = {}
            
            # Ajustar menor disparidade se não foi encontrada
            if comparative_results['menor_disparidade']['diferenca'] == float('inf'):
                comparative_results['menor_disparidade'] = {
                    'competencia': None, 'diferenca': 0, 'categoria_max': None, 'categoria_min': None
                }
            
            return comparative_results
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas comparativas: {e}")
            return self.result_builder.build_empty_result(f"Erro: {str(e)}")


class VariabilityAnalyzer:
    """
    Analisador de variabilidade entre categorias.
    Responsabilidade: Medir e classificar variabilidade de desempenho.
    """
    
    def __init__(self):
        mappings = get_mappings()
        self.limiares = mappings['limiares_estatisticos']
    
    def analyze_variability(
        self, 
        data: pd.DataFrame, 
        competencia: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analisa variabilidade entre categorias."""
        if data is None or data.empty:
            return self._empty_variability_result()
        
        # Filtrar por competência se especificada
        if competencia is not None:
            df_analise = data[data['Competência'] == competencia]
        else:
            df_analise = data
        
        if df_analise.empty:
            return self._empty_variability_result()
        
        try:
            return self._calculate_variability_metrics(df_analise)
        except Exception as e:
            print(f"Erro ao analisar variabilidade: {e}")
            return self._empty_variability_result()
    
    def _calculate_variability_metrics(self, df_analise: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas de variabilidade."""
        medias_por_categoria = df_analise.groupby('Categoria')['Média'].mean()
        
        media_geral = medias_por_categoria.mean()
        desvio_padrao = medias_por_categoria.std()
        variancia = medias_por_categoria.var()
        valor_min = medias_por_categoria.min()
        valor_max = medias_por_categoria.max()
        amplitude = valor_max - valor_min
        
        coef_variacao = (desvio_padrao / media_geral * 100) if media_geral > 0 else 0
        classificacao = self._classify_variability(coef_variacao)
        
        return {
            'coef_variacao': round(coef_variacao, 2),
            'amplitude': round(amplitude, 2),
            'desvio_padrao': round(desvio_padrao, 2),
            'variancia': round(variancia, 2),
            'media_geral': round(media_geral, 2),
            'valor_min': round(valor_min, 2),
            'valor_max': round(valor_max, 2),
            'classificacao': classificacao,
            'valido': True
        }
    
    def _classify_variability(self, coef_variacao: float) -> str:
        """Classifica o nível de variabilidade."""
        if coef_variacao < self.limiares['variabilidade_baixa']:
            return "Baixa variabilidade"
        elif coef_variacao < self.limiares['variabilidade_moderada']:
            return "Variabilidade moderada"
        else:
            return "Alta variabilidade"
    
    def _empty_variability_result(self) -> Dict[str, Any]:
        """Retorna resultado vazio para variabilidade."""
        return {
            'coef_variacao': 0, 'amplitude': 0, 'desvio_padrao': 0, 'variancia': 0,
            'media_geral': 0, 'valor_min': 0, 'valor_max': 0,
            'classificacao': 'Dados insuficientes', 'valido': False
        }


class PercentileCalculator:
    """
    Calculador de percentis de desempenho.
    Responsabilidade: Calcular percentis de forma segura e eficiente.
    """
    
    def calculate_percentiles(
        self, 
        data: pd.DataFrame, 
        coluna: str,
        percentis: List[float] = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
    ) -> Dict[str, float]:
        """Calcula percentis para uma coluna específica."""
        if data is None or data.empty or coluna not in data.columns:
            return {f"P{int(p*100)}": 0 for p in percentis}
        
        # Filtrar valores válidos
        valores = data[coluna].dropna()
        valores = valores[valores > 0]
        
        if len(valores) == 0:
            return {f"P{int(p*100)}": 0 for p in percentis}
        
        try:
            resultado = {}
            for p in percentis:
                valor_percentil = valores.quantile(p)
                resultado[f"P{int(p*100)}"] = round(valor_percentil, 2)
            
            return resultado
        
        except Exception as e:
            print(f"Erro ao calcular percentis: {e}")
            return {f"P{int(p*100)}": 0 for p in percentis}
