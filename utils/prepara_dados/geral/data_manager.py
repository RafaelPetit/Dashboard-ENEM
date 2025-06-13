"""
Interface unificada para processamento de dados gerais do ENEM.
Mantém compatibilidade com o código existente enquanto usa a nova arquitetura.
"""

from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

from .processors import (
    HistogramDataProcessor,
    AttendanceAnalysisProcessor,
    MainMetricsProcessor,
    StateAverageProcessor,
    ComparativeAnalysisProcessor
)
from ..base import ProcessingConfig
from ..common_utils import data_filter
from utils.mappings import get_mappings


class GeralDataManager:
    """
    Gerenciador principal para dados gerais do ENEM.
    Implementa padrão Facade para simplificar o uso dos processadores.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """
        Inicializa o gerenciador.
        
        Args:
            config: Configurações de processamento
        """
        self.config = config or ProcessingConfig()
        
        # Inicializar processadores
        self.histogram_processor = HistogramDataProcessor(self.config)
        self.attendance_processor = AttendanceAnalysisProcessor(self.config)
        self.metrics_processor = MainMetricsProcessor(self.config)
        self.state_average_processor = StateAverageProcessor(self.config)
        self.comparative_processor = ComparativeAnalysisProcessor(self.config)
        
        # Obter mapeamentos
        mappings = get_mappings()
        self.competencia_mapping = mappings['competencia_mapping']
        self.colunas_notas = mappings['colunas_notas']
    
    def preparar_dados_histograma(self, df: pd.DataFrame, coluna: str) -> Tuple[pd.DataFrame, str, str]:
        """
        Prepara dados para histograma de notas.
        Mantém compatibilidade com a função original.
        
        Args:
            df: DataFrame com dados dos candidatos
            coluna: Nome da coluna (área de conhecimento) a ser analisada
            
        Returns:
            Tuple com (DataFrame filtrado, nome da coluna, nome da área)
        """
        return self.histogram_processor.cached_process(df, coluna=coluna)
    
    def preparar_dados_grafico_faltas(self, microdados_estados: pd.DataFrame, 
                                    estados_selecionados: List[str]) -> pd.DataFrame:
        """
        Prepara dados para gráfico de faltas por estado.
        Mantém compatibilidade com a função original.
        
        Args:
            microdados_estados: DataFrame com microdados dos candidatos
            estados_selecionados: Lista de estados selecionados para análise
            
        Returns:
            DataFrame com dados de faltas por estado
        """
        return self.attendance_processor.cached_process(
            microdados_estados, 
            estados_selecionados=estados_selecionados
        )
    
    def preparar_dados_metricas_principais(self, microdados_estados: pd.DataFrame, 
                                         estados_selecionados: List[str]) -> Dict[str, Any]:
        """
        Prepara dados para métricas principais.
        Mantém compatibilidade com a função original.
        
        Args:
            microdados_estados: DataFrame com microdados filtrados por estado
            estados_selecionados: Lista de estados selecionados para análise
            
        Returns:
            Dicionário com métricas calculadas
        """
        return self.metrics_processor.cached_process(
            microdados_estados,
            estados_selecionados=estados_selecionados,
            colunas_notas=self.colunas_notas
        )
    
    def preparar_dados_media_geral_estados(self, microdados_estados: pd.DataFrame, 
                                         estados_selecionados: List[str],
                                         agrupar_por_regiao: bool = False) -> pd.DataFrame:
        """
        Prepara dados para visualização da média geral por estado ou região.
        Mantém compatibilidade com a função original.
        
        Args:
            microdados_estados: DataFrame com microdados filtrados por estado
            estados_selecionados: Lista de estados selecionados para análise
            agrupar_por_regiao: Se True, agrupa os dados por região
            
        Returns:
            DataFrame com dados de média geral por estado ou região
        """
        return self.state_average_processor.cached_process(
            microdados_estados,
            estados_selecionados=estados_selecionados,
            colunas_notas=self.colunas_notas,
            agrupar_por_regiao=agrupar_por_regiao
        )
    
    def preparar_dados_evasao(self, microdados_estados: pd.DataFrame, 
                            estados_selecionados: List[str]) -> pd.DataFrame:
        """
        Prepara dados de evasão (faltas) dos candidatos por estado.
        Versão simplificada que usa o processador de presença.
        
        Args:
            microdados_estados: DataFrame com microdados filtrados por estado
            estados_selecionados: Lista de estados selecionados para análise
            
        Returns:
            DataFrame com dados de evasão por estado
        """
        # Reusar o processador de presença com formato diferente
        attendance_data = self.attendance_processor.cached_process(
            microdados_estados,
            estados_selecionados=estados_selecionados
        )
        
        if attendance_data.empty:
            return pd.DataFrame(columns=['Estado', 'Métrica', 'Valor'])
        
        # Reformatar para incluir dados de presença também
        try:
            evasion_data = []
            
            for estado in estados_selecionados:
                state_data = microdados_estados[
                    microdados_estados['SG_UF_PROVA'] == estado
                ] if 'SG_UF_PROVA' in microdados_estados.columns else pd.DataFrame()
                
                if state_data.empty:
                    continue
                
                total = len(state_data)
                
                if 'TP_PRESENCA_GERAL' in state_data.columns:
                    presenca_counts = state_data['TP_PRESENCA_GERAL'].value_counts()
                    
                    # Presentes nos dois dias
                    presentes = presenca_counts.get(3, 0)
                    # Faltas por dia
                    faltas_dia1 = presenca_counts.get(2, 0)
                    faltas_dia2 = presenca_counts.get(1, 0)
                    faltas_ambos = presenca_counts.get(0, 0)
                    
                    # Calcular percentuais
                    if total > 0:
                        evasion_data.extend([
                            {
                                'Estado': estado,
                                'Métrica': 'Presentes',
                                'Valor': round((presentes / total) * 100, 2),
                                'Contagem': presentes
                            },
                            {
                                'Estado': estado,
                                'Métrica': 'Faltantes Dia 1',
                                'Valor': round((faltas_dia1 / total) * 100, 2),
                                'Contagem': faltas_dia1
                            },
                            {
                                'Estado': estado,
                                'Métrica': 'Faltantes Dia 2',
                                'Valor': round((faltas_dia2 / total) * 100, 2),
                                'Contagem': faltas_dia2
                            },
                            {
                                'Estado': estado,
                                'Métrica': 'Faltantes Ambos',
                                'Valor': round((faltas_ambos / total) * 100, 2),
                                'Contagem': faltas_ambos
                            }
                        ])
            
            return pd.DataFrame(evasion_data)
            
        except Exception as e:
            print(f"Erro ao preparar dados de evasão: {e}")
            return pd.DataFrame(columns=['Estado', 'Métrica', 'Valor'])
    
    def preparar_dados_comparativo_areas(self, microdados_estados: pd.DataFrame,
                                       estados_selecionados: List[str]) -> pd.DataFrame:
        """
        Prepara dados para comparativo de desempenho entre áreas.
        Mantém compatibilidade com a função original.
        
        Args:
            microdados_estados: DataFrame com microdados filtrados por estado
            estados_selecionados: Lista de estados selecionados para análise
            
        Returns:
            DataFrame com dados de desempenho médio por área
        """
        return self.comparative_processor.cached_process(
            microdados_estados,
            estados_selecionados=estados_selecionados,
            colunas_notas=self.colunas_notas
        )


# Instância global para compatibilidade
geral_data_manager = GeralDataManager()

# Funções de compatibilidade com a interface original
def preparar_dados_histograma(df: pd.DataFrame, coluna: str, 
                            competencia_mapping: Dict[str, str]) -> Tuple[pd.DataFrame, str, str]:
    """Função de compatibilidade para preparar dados de histograma."""
    return geral_data_manager.preparar_dados_histograma(df, coluna)


def preparar_dados_grafico_faltas(microdados_estados: pd.DataFrame, 
                                 estados_selecionados: List[str],
                                 colunas_presenca: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Função de compatibilidade para preparar dados de faltas."""
    return geral_data_manager.preparar_dados_grafico_faltas(microdados_estados, estados_selecionados)


def preparar_dados_metricas_principais(microdados_estados: pd.DataFrame, 
                                     estados_selecionados: List[str],
                                     colunas_notas: List[str]) -> Dict[str, Any]:
    """Função de compatibilidade para métricas principais."""
    return geral_data_manager.preparar_dados_metricas_principais(microdados_estados, estados_selecionados)


def preparar_dados_media_geral_estados(microdados_estados: pd.DataFrame, 
                                     estados_selecionados: List[str],
                                     colunas_notas: List[str],
                                     agrupar_por_regiao: bool = False) -> pd.DataFrame:
    """Função de compatibilidade para médias por estado."""
    return geral_data_manager.preparar_dados_media_geral_estados(
        microdados_estados, estados_selecionados, agrupar_por_regiao
    )


def preparar_dados_evasao(microdados_estados: pd.DataFrame, 
                        estados_selecionados: List[str]) -> pd.DataFrame:
    """Função de compatibilidade para dados de evasão."""
    return geral_data_manager.preparar_dados_evasao(microdados_estados, estados_selecionados)


def preparar_dados_comparativo_areas(microdados_estados: pd.DataFrame,
                                   estados_selecionados: List[str],
                                   colunas_notas: List[str],
                                   competencia_mapping: Dict[str, str]) -> pd.DataFrame:
    """Função de compatibilidade para análise comparativa."""
    return geral_data_manager.preparar_dados_comparativo_areas(microdados_estados, estados_selecionados)
