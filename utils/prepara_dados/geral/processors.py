"""
Processadores especializados para dados gerais do ENEM.
Implementa diferentes aspectos da análise geral de forma modular.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import pandas as pd
import numpy as np

from ..base import StateGroupedProcessor, CacheableProcessor, ProcessingConfig
from ..common_utils import (
    mapping_manager, statistical_calculator, 
    data_aggregator, data_filter, StatisticalSummary
)
from data import calcular_seguro
from utils.mappings import get_mappings
from utils.helpers.regiao_utils import obter_regiao_do_estado


class HistogramDataProcessor(StateGroupedProcessor[Tuple[pd.DataFrame, str, str]]):
    """Processador para dados de histograma de notas."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self._competencia_mapping = get_mappings()['competencia_mapping']
    
    def process(self, data: pd.DataFrame, coluna: str) -> Tuple[pd.DataFrame, str, str]:
        """
        Prepara dados para histograma de notas.
        
        Args:
            data: DataFrame com dados dos candidatos
            coluna: Coluna (área de conhecimento) a analisar
            
        Returns:
            Tuple com (DataFrame filtrado, nome da coluna, nome da área)
        """
        # Validar entrada
        if not self.validate_input(data, [coluna]):
            nome_area = self._competencia_mapping.get(coluna, coluna)
            return pd.DataFrame(), coluna, nome_area
        
        try:
            # Filtrar valores válidos (notas > 0)
            df_valid = data_filter.filter_valid_scores(data, [coluna])
            
            if df_valid.empty:
                nome_area = self._competencia_mapping.get(coluna, coluna)
                return pd.DataFrame(), coluna, nome_area
            
            # Otimizar tipos
            df_optimized = self.optimize_dataframe(df_valid)
            
            # Obter nome da área
            nome_area = self._competencia_mapping.get(coluna, coluna)
            
            return df_optimized, coluna, nome_area
            
        except Exception as e:
            print(f"Erro ao preparar dados para histograma: {e}")
            nome_area = self._competencia_mapping.get(coluna, coluna)
            return pd.DataFrame(), coluna, nome_area


class AttendanceAnalysisProcessor(StateGroupedProcessor[pd.DataFrame]):
    """Processador para análise de faltas por estado."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self.attendance_column = 'TP_PRESENCA_GERAL'
        self.attendance_categories = {
            0: 'Faltou nos dois dias',
            1: 'Faltou no segundo dia', 
            2: 'Faltou no primeiro dia',
            3: 'Presente nos dois dias'
        }
    
    def process(self, data: pd.DataFrame, estados_selecionados: List[str]) -> pd.DataFrame:
        """
        Prepara dados para gráfico de faltas por estado.
        
        Args:
            data: DataFrame com microdados
            estados_selecionados: Lista de estados para análise
            
        Returns:
            DataFrame com dados de faltas por estado
        """
        required_columns = [self.state_column, self.attendance_column]
        
        if not self.validate_input(data, required_columns):
            return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
        
        try:
            return self._calculate_attendance_by_state(data, estados_selecionados)
        except Exception as e:
            print(f"Erro ao processar dados de faltas: {e}")
            return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
    
    def _calculate_attendance_by_state(self, data: pd.DataFrame, 
                                     states: List[str]) -> pd.DataFrame:
        """Calcula percentuais de faltas por estado."""
        
        def process_state_attendance(state_data: pd.DataFrame, state: str) -> Dict[str, Any]:
            """Processa dados de presença para um estado."""
            total_candidates = len(state_data)
            
            if total_candidates == 0:
                return []
            
            # Contar por categoria de presença
            attendance_counts = state_data[self.attendance_column].value_counts()
            
            state_results = []
            for code, category_name in self.attendance_categories.items():
                if code in [0, 1, 2]:  # Apenas categorias de falta
                    count = attendance_counts.get(code, 0)
                    percentage = (count / total_candidates * 100) if total_candidates > 0 else 0
                    
                    state_results.append({
                        'Estado': state,
                        'Tipo de Falta': category_name,
                        'Percentual de Faltas': round(percentage, 2),
                        'Contagem': count,
                        'Total': total_candidates
                    })
            
            return state_results
        
        # Processar estados em paralelo
        all_results = self.process_states_in_parallel(
            data, states, process_state_attendance
        )
        
        # Achatar resultados
        flattened_results = []
        for state_result in all_results:
            if isinstance(state_result, list):
                flattened_results.extend(state_result)
            else:
                flattened_results.append(state_result)
        
        # Criar DataFrame otimizado
        df_result = pd.DataFrame(flattened_results)
        
        if not df_result.empty:
            # Aplicar otimizações categóricas
            categorical_columns = ['Estado', 'Tipo de Falta']
            df_result = self.apply_categorical_optimization(df_result, categorical_columns)
        
        return df_result


class MainMetricsProcessor(StateGroupedProcessor[Dict[str, Any]]):
    """Processador para métricas principais da aba geral."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self.attendance_column = 'TP_PRESENCA_GERAL'
    
    def process(self, data: pd.DataFrame, estados_selecionados: List[str], 
               colunas_notas: List[str]) -> Dict[str, Any]:
        """
        Calcula métricas principais para exibição.
        
        Args:
            data: DataFrame com microdados
            estados_selecionados: Estados selecionados
            colunas_notas: Colunas com notas
            
        Returns:
            Dicionário com métricas calculadas
        """
        if not self.validate_input(data, colunas_notas + [self.attendance_column]):
            return self._generate_empty_metrics(colunas_notas)
        
        try:
            metrics = {}
            
            # Métricas básicas
            metrics['total_candidatos'] = len(data)
            
            # Calcular faltas
            attendance_metrics = self._calculate_attendance_metrics(data)
            metrics.update(attendance_metrics)
            
            # Calcular médias por área
            score_metrics = self._calculate_score_metrics(data, colunas_notas)
            metrics.update(score_metrics)
            
            # Calcular desempenho por regiões
            region_metrics = self._calculate_regional_performance(
                data, estados_selecionados, colunas_notas
            )
            metrics['desempenho_regioes'] = region_metrics
            
            return metrics
            
        except Exception as e:
            print(f"Erro ao calcular métricas principais: {e}")
            return self._generate_empty_metrics(colunas_notas)
    
    def _calculate_attendance_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas de presença."""
        total_candidates = len(data)
        
        if self.attendance_column not in data.columns:
            return {'faltas_totais': 0, 'percentual_faltas': 0}
        
        # Candidatos que faltaram nos dois dias (código 0)
        faltas_totais = len(data[data[self.attendance_column] == 0])
        percentual_faltas = (faltas_totais / total_candidates * 100) if total_candidates > 0 else 0
        
        return {
            'faltas_totais': faltas_totais,
            'percentual_faltas': round(percentual_faltas, 2)
        }
    
    def _calculate_score_metrics(self, data: pd.DataFrame, colunas_notas: List[str]) -> Dict[str, Any]:
        """Calcula métricas de desempenho."""
        from data.data_loader import calcular_seguro
        
        medias = {}
        for coluna in colunas_notas:
            if coluna in data.columns:
                # Filtrar notas válidas (> 0)
                notas_validas = data[data[coluna] > 0][coluna]
                if not notas_validas.empty:
                    media = calcular_seguro(notas_validas, 'media')
                    medias[coluna] = round(media, 2)
                else:
                    medias[coluna] = None
            else:
                medias[coluna] = None
        
        # Calcular média geral
        medias_validas = [v for v in medias.values() if v is not None]
        media_geral = round(sum(medias_validas) / len(medias_validas), 2) if medias_validas else 0
        
        return {
            'medias': medias,
            'media_geral': media_geral
        }
    
    def _calculate_regional_performance(self, data: pd.DataFrame, 
                                      estados: List[str], 
                                      colunas_notas: List[str]) -> Dict[str, Any]:
        """Calcula desempenho por regiões."""
        from data.data_loader import calcular_seguro
        
        regional_data = {}
        
        # Agrupar por região usando função helper
        for estado in estados:
            estado_data = data[data[self.state_column] == estado]
            
            if estado_data.empty:
                continue
            
            # Obter região do estado
            regiao = obter_regiao_do_estado(estado)
            
            if regiao not in regional_data:
                regional_data[regiao] = {
                    'estados': [],
                    'total_candidatos': 0,
                    'medias': {coluna: [] for coluna in colunas_notas}
                }
            
            regional_data[regiao]['estados'].append(estado)
            regional_data[regiao]['total_candidatos'] += len(estado_data)
            
            # Calcular médias por competência para este estado
            for coluna in colunas_notas:
                if coluna in estado_data.columns:
                    notas_validas = estado_data[estado_data[coluna] > 0][coluna]
                    if not notas_validas.empty:
                        media = calcular_seguro(notas_validas, 'media')
                        regional_data[regiao]['medias'][coluna].append(media)
        
        # Calcular médias regionais finais
        for regiao_info in regional_data.values():
            for coluna in colunas_notas:
                medias_coluna = regiao_info['medias'][coluna]
                if medias_coluna:
                    regiao_info['medias'][coluna] = round(
                        sum(medias_coluna) / len(medias_coluna), 2
                    )
                else:
                    regiao_info['medias'][coluna] = None
        
        return regional_data
    
    def _generate_empty_metrics(self, colunas_notas: List[str]) -> Dict[str, Any]:
        """Gera métricas vazias quando não há dados."""
        return {
            'total_candidatos': 0,
            'faltas_totais': 0,
            'percentual_faltas': 0,
            'medias': {coluna: None for coluna in colunas_notas},
            'media_geral': 0,
            'desempenho_regioes': {}
        }


class StateAverageProcessor(StateGroupedProcessor[pd.DataFrame]):
    """Processador para médias gerais por estado."""
    
    def process(self, data: pd.DataFrame, estados_selecionados: List[str], 
               colunas_notas: List[str], agrupar_por_regiao: bool = False) -> pd.DataFrame:
        """
        Calcula médias gerais por estado ou região.
        
        Args:
            data: DataFrame com microdados
            estados_selecionados: Estados para análise
            colunas_notas: Colunas com notas
            agrupar_por_regiao: Se deve agrupar por região
            
        Returns:
            DataFrame com médias por estado/região
        """
        if not self.validate_input(data, [self.state_column] + colunas_notas):
            return pd.DataFrame(columns=['Local', 'Média Geral'])
        
        try:
            def calculate_state_average(state_data: pd.DataFrame, state: str) -> Dict[str, Any]:
                """Calcula média geral para um estado."""
                state_means = []
                
                for column in colunas_notas:
                    if column in state_data.columns:
                        valid_scores = state_data[state_data[column] > 0][column]
                        if not valid_scores.empty:
                            mean_score = calcular_seguro(valid_scores, 'media')
                            state_means.append(mean_score)
                
                if state_means:
                    overall_mean = sum(state_means) / len(state_means)
                    return {
                        'Local': state,
                        'Média Geral': round(overall_mean, 2)
                    }
                
                return None
            
            # Processar estados
            results = self.process_states_in_parallel(
                data, estados_selecionados, calculate_state_average
            )
            
            # Filtrar resultados válidos
            valid_results = [r for r in results if r is not None]
            
            if not valid_results:
                return pd.DataFrame(columns=['Local', 'Média Geral'])
            
            df_result = pd.DataFrame(valid_results)
            
            # Agrupar por região se solicitado
            if agrupar_por_regiao and not df_result.empty:
                df_result = self._aggregate_by_regions(df_result)
            
            return self.optimize_dataframe(df_result)
            
        except Exception as e:
            print(f"Erro ao calcular médias por estado: {e}")
            return pd.DataFrame(columns=['Local', 'Média Geral'])
    
    def _aggregate_by_regions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega resultados por região."""
        if 'Local' not in df.columns:
            return df
        
        try:
            # Adicionar coluna de região
            df_with_region = df.copy()
            df_with_region['Regiao'] = df_with_region['Local'].apply(obter_regiao_do_estado)
            
            # Filtrar regiões válidas
            df_with_region = df_with_region[df_with_region['Regiao'] != ""]
            
            # Agrupar por região
            numeric_columns = df_with_region.select_dtypes(include='number').columns
            aggregated = df_with_region.groupby('Regiao')[numeric_columns].mean().reset_index()
            
            # Renomear coluna
            aggregated = aggregated.rename(columns={'Regiao': 'Local'})
            
            # Arredondar valores
            for col in numeric_columns:
                aggregated[col] = aggregated[col].round(2)
            
            return aggregated
            
        except Exception as e:
            print(f"Erro na agregação por regiões: {e}")
            return df


class ComparativeAnalysisProcessor(StateGroupedProcessor[pd.DataFrame]):
    """Processador para análise comparativa entre áreas."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self._competencia_mapping = get_mappings()['competencia_mapping']
    
    def process(self, data: pd.DataFrame, estados_selecionados: List[str],
               colunas_notas: List[str]) -> pd.DataFrame:
        """
        Prepara dados comparativos entre áreas de conhecimento.
        
        Args:
            data: DataFrame com microdados
            estados_selecionados: Estados selecionados
            colunas_notas: Colunas com notas
            
        Returns:
            DataFrame com estatísticas por área
        """
        if not self.validate_input(data, colunas_notas):
            return pd.DataFrame(columns=['Area', 'Media', 'DesvioPadrao', 'Mediana'])
        
        try:
            results = []
            
            for column in colunas_notas:
                if column not in data.columns:
                    continue
                
                # Filtrar notas válidas
                valid_scores = data[data[column] > 0][column]
                
                if valid_scores.empty:
                    continue
                
                # Calcular estatísticas usando o calculador comum
                summary = statistical_calculator.calculate_summary(valid_scores)
                
                # Obter nome da área
                area_name = self._competencia_mapping.get(column, column)
                
                results.append({
                    'Area': area_name,
                    'Media': round(summary.mean, 2),
                    'DesvioPadrao': round(summary.std, 2),
                    'Mediana': round(summary.median, 2),
                    'Minimo': round(summary.min_val, 2),
                    'Maximo': round(summary.max_val, 2),
                    'Contagem': summary.count
                })
            
            # Criar e ordenar DataFrame
            df_result = pd.DataFrame(results)
            
            if not df_result.empty:
                df_result = df_result.sort_values('Media', ascending=False)
            
            return self.optimize_dataframe(df_result)
            
        except Exception as e:
            print(f"Erro na análise comparativa: {e}")
            return pd.DataFrame(columns=['Area', 'Media', 'DesvioPadrao', 'Mediana'])


class CorrelationAnalysisProcessor(CacheableProcessor[pd.DataFrame]):
    """Processador para análise de correlação entre competências."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config)
        self._competencia_mapping = get_mappings()['competencia_mapping']
    
    def process(self, data: pd.DataFrame, colunas_notas: List[str]) -> pd.DataFrame:
        """
        Calcula matriz de correlação entre competências.
        
        Args:
            data: DataFrame com microdados
            colunas_notas: Colunas com notas para correlação
            
        Returns:
            DataFrame com matriz de correlação formatada
        """
        if not self.validate_input(data, colunas_notas):
            # Retornar matriz vazia mas válida
            return pd.DataFrame(
                index=[self._competencia_mapping.get(col, col) for col in colunas_notas],
                columns=[self._competencia_mapping.get(col, col) for col in colunas_notas],
                data=0.0
            )
        
        try:
            # Filtrar apenas notas válidas (> 0)
            df_valid = data_filter.filter_valid_scores(data, colunas_notas)
            
            if df_valid.empty:
                return self._generate_empty_correlation_matrix(colunas_notas)
            
            # Calcular correlação
            correlation_matrix = df_valid[colunas_notas].corr()
            
            # Renomear índices e colunas para nomes amigáveis
            friendly_names = {col: self._competencia_mapping.get(col, col) for col in colunas_notas}
            correlation_matrix = correlation_matrix.rename(index=friendly_names, columns=friendly_names)
            
            # Arredondar valores
            correlation_matrix = correlation_matrix.round(3)
            
            return correlation_matrix
            
        except Exception as e:
            print(f"Erro ao calcular correlação: {e}")
            return self._generate_empty_correlation_matrix(colunas_notas)
    
    def _generate_empty_correlation_matrix(self, colunas_notas: List[str]) -> pd.DataFrame:
        """Gera matriz de correlação vazia."""
        friendly_names = [self._competencia_mapping.get(col, col) for col in colunas_notas]
        return pd.DataFrame(
            index=friendly_names,
            columns=friendly_names,
            data=0.0
        )
