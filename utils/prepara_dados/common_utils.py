"""
Utilitários comuns para preparação de dados.
Implementa operações frequentemente utilizadas nas classes de preparação.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass

from data import calcular_seguro
from utils.mappings import get_mappings
from .base import ProcessingConfig


@dataclass
class StatisticalSummary:
    """Sumário estatístico padronizado."""
    
    count: int
    mean: float
    median: float
    std: float
    min_val: float
    max_val: float
    percentiles: Dict[str, float]


class MappingManager:
    """Gerenciador de mapeamentos de variáveis."""
    
    def __init__(self):
        """Inicializa com mapeamentos globais."""
        self._mappings = get_mappings()
    
    def apply_mapping(self, df: pd.DataFrame, variable: str, 
                     mappings_dict: Dict[str, Dict[str, Any]]) -> Tuple[pd.DataFrame, str]:
        """
        Aplica mapeamento a uma variável e retorna o nome da coluna mapeada.
        
        Args:
            df: DataFrame com os dados
            variable: Nome da variável a mapear
            mappings_dict: Dicionário com mapeamentos
            
        Returns:
            Tuple com DataFrame modificado e nome da coluna mapeada
        """
        if variable not in df.columns:
            print(f"Aviso: Variável '{variable}' não encontrada no DataFrame")
            return df.copy(), variable
        
        if variable not in mappings_dict:
            print(f"Aviso: Variável '{variable}' não encontrada nos mapeamentos")
            return df.copy(), variable
        
        df_result = df.copy()
        
        # Verificar se precisa aplicar mapeamento
        if "mapeamento" in mappings_dict[variable] and df[variable].dtype != 'object':
            mapped_column = f'{variable}_MAPPED'
            
            try:
                mapping = mappings_dict[variable]["mapeamento"]
                df_result[mapped_column] = df_result[variable].map(mapping)
                
                # Converter para categoria se eficiente
                if len(mapping) < len(df_result) * 0.5:
                    categories = list(mapping.values())
                    df_result[mapped_column] = pd.Categorical(
                        df_result[mapped_column], 
                        categories=categories
                    )
                
                return df_result, mapped_column
                
            except Exception as e:
                print(f"Erro ao aplicar mapeamento para '{variable}': {e}")
                return df_result, variable
        
        return df_result, variable
    
    def get_ordered_categories(self, variable: str, 
                             mappings_dict: Dict[str, Dict[str, Any]], 
                             data_categories: List[str]) -> List[str]:
        """
        Obtém categorias ordenadas para uma variável.
        
        Args:
            variable: Nome da variável
            mappings_dict: Dicionário com mapeamentos
            data_categories: Categorias presentes nos dados
            
        Returns:
            Lista de categorias ordenadas
        """
        if variable not in mappings_dict:
            return sorted(data_categories)
        
        var_config = mappings_dict[variable]
        
        # Usar ordem explícita se definida
        if "ordem" in var_config:
            explicit_order = var_config["ordem"]
            present_categories = [cat for cat in explicit_order if cat in data_categories]
            missing_categories = [cat for cat in data_categories if cat not in present_categories]
            return present_categories + sorted(missing_categories)
        
        # Usar ordem do mapeamento se disponível
        if "mapeamento" in var_config:
            mapping_order = list(var_config["mapeamento"].values())
            present_categories = [cat for cat in mapping_order if cat in data_categories]
            missing_categories = [cat for cat in data_categories if cat not in present_categories]
            return present_categories + sorted(missing_categories)
        
        # Ordem alfabética como fallback
        return sorted(data_categories)


class StatisticalCalculator:
    """Calculadora de estatísticas padronizada."""
    
    @staticmethod
    def calculate_summary(data: pd.Series, percentiles: List[float] = None) -> StatisticalSummary:
        """
        Calcula sumário estatístico completo.
        
        Args:
            data: Série de dados
            percentiles: Lista de percentis a calcular
            
        Returns:
            Sumário estatístico
        """
        if percentiles is None:
            percentiles = [25, 50, 75, 90, 95]
        
        # Filtrar valores válidos
        valid_data = data.dropna()
        
        if valid_data.empty:
            return StatisticalSummary(
                count=0, mean=0, median=0, std=0, 
                min_val=0, max_val=0, percentiles={}
            )
        
        try:
            # Calcular estatísticas básicas
            summary = StatisticalSummary(
                count=len(valid_data),
                mean=calcular_seguro(valid_data, 'media'),
                median=calcular_seguro(valid_data, 'mediana'),
                std=calcular_seguro(valid_data, 'std'),
                min_val=calcular_seguro(valid_data, 'min'),
                max_val=calcular_seguro(valid_data, 'max'),
                percentiles={}
            )
            
            # Calcular percentis
            for p in percentiles:
                try:
                    summary.percentiles[f'p{p}'] = float(valid_data.quantile(p/100))
                except:
                    summary.percentiles[f'p{p}'] = 0.0
            
            return summary
            
        except Exception as e:
            print(f"Erro no cálculo estatístico: {e}")
            return StatisticalSummary(
                count=len(valid_data), mean=0, median=0, std=0,
                min_val=0, max_val=0, percentiles={}
            )
    
    @staticmethod
    def calculate_group_statistics(df: pd.DataFrame, group_column: str, 
                                 value_columns: List[str]) -> pd.DataFrame:
        """
        Calcula estatísticas por grupo.
        
        Args:
            df: DataFrame com dados
            group_column: Coluna para agrupamento
            value_columns: Colunas com valores para calcular estatísticas
            
        Returns:
            DataFrame com estatísticas por grupo
        """
        if df.empty or group_column not in df.columns:
            return pd.DataFrame()
        
        try:
            results = []
            
            for group_value, group_data in df.groupby(group_column, observed=True):
                group_stats = {'grupo': group_value}
                
                for col in value_columns:
                    if col in group_data.columns:
                        valid_data = group_data[group_data[col] > 0][col]
                        
                        if not valid_data.empty:
                            group_stats[f'{col}_media'] = calcular_seguro(valid_data, 'media')
                            group_stats[f'{col}_mediana'] = calcular_seguro(valid_data, 'mediana')
                            group_stats[f'{col}_std'] = calcular_seguro(valid_data, 'std')
                            group_stats[f'{col}_count'] = len(valid_data)
                        else:
                            group_stats[f'{col}_media'] = 0
                            group_stats[f'{col}_mediana'] = 0
                            group_stats[f'{col}_std'] = 0
                            group_stats[f'{col}_count'] = 0
                
                results.append(group_stats)
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Erro no cálculo de estatísticas por grupo: {e}")
            return pd.DataFrame()


class DataAggregator:
    """Agregador de dados com diferentes estratégias."""
    
    @staticmethod
    def aggregate_by_category(df: pd.DataFrame, category_column: str, 
                            agg_functions: Dict[str, str]) -> pd.DataFrame:
        """
        Agrega dados por categoria.
        
        Args:
            df: DataFrame com dados
            category_column: Coluna para categorização
            agg_functions: Dicionário com funções de agregação por coluna
            
        Returns:
            DataFrame agregado
        """
        if df.empty or category_column not in df.columns:
            return pd.DataFrame()
        
        try:
            return df.groupby(category_column, observed=True).agg(agg_functions).reset_index()
        except Exception as e:
            print(f"Erro na agregação por categoria: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def calculate_percentages(df: pd.DataFrame, group_column: str, 
                            count_column: str) -> pd.DataFrame:
        """
        Calcula percentuais dentro de grupos.
        
        Args:
            df: DataFrame com dados
            group_column: Coluna para agrupamento
            count_column: Coluna com contagens
            
        Returns:
            DataFrame com percentuais calculados
        """
        if df.empty or group_column not in df.columns or count_column not in df.columns:
            return df.copy()
        
        try:
            df_result = df.copy()
            
            # Calcular totais por grupo
            totals = df_result.groupby(group_column)[count_column].sum()
            
            # Mapear totais de volta ao DataFrame
            df_result['total_grupo'] = df_result[group_column].map(totals)
            
            # Calcular percentuais
            df_result['percentual'] = (
                df_result[count_column] / df_result['total_grupo'] * 100
            ).round(2)
            
            # Remover coluna temporária
            df_result = df_result.drop('total_grupo', axis=1)
            
            return df_result
            
        except Exception as e:
            print(f"Erro no cálculo de percentuais: {e}")
            return df.copy()


class DataFilter:
    """Filtrador de dados com validações."""
    
    @staticmethod
    def filter_valid_scores(df: pd.DataFrame, score_columns: List[str], 
                          min_score: float = 0) -> pd.DataFrame:
        """
        Filtra registros com notas válidas.
        
        Args:
            df: DataFrame com dados
            score_columns: Colunas com notas
            min_score: Nota mínima válida
            
        Returns:
            DataFrame filtrado
        """
        if df.empty:
            return df.copy()
        
        df_filtered = df.copy()
        
        for col in score_columns:
            if col in df_filtered.columns:
                df_filtered = df_filtered[
                    (df_filtered[col] > min_score) & 
                    (df_filtered[col].notna())
                ]
        
        return df_filtered
    
    @staticmethod
    def filter_by_states(df: pd.DataFrame, states: List[str], 
                        state_column: str = 'SG_UF_PROVA') -> pd.DataFrame:
        """
        Filtra dados por estados.
        
        Args:
            df: DataFrame com dados
            states: Lista de estados
            state_column: Nome da coluna com estados
            
        Returns:
            DataFrame filtrado
        """
        if df.empty or state_column not in df.columns:
            return df.copy()
        
        return df[df[state_column].isin(states)].copy()
    
    @staticmethod
    def remove_outliers(df: pd.DataFrame, columns: List[str], 
                       method: str = 'iqr', factor: float = 1.5) -> pd.DataFrame:
        """
        Remove outliers dos dados.
        
        Args:
            df: DataFrame com dados
            columns: Colunas para detectar outliers
            method: Método de detecção ('iqr' ou 'zscore')
            factor: Fator multiplicativo para detecção
            
        Returns:
            DataFrame sem outliers
        """
        if df.empty:
            return df.copy()
        
        df_clean = df.copy()
        
        for col in columns:
            if col not in df_clean.columns:
                continue
            
            try:
                if method == 'iqr':
                    Q1 = df_clean[col].quantile(0.25)
                    Q3 = df_clean[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - factor * IQR
                    upper_bound = Q3 + factor * IQR
                    
                    df_clean = df_clean[
                        (df_clean[col] >= lower_bound) & 
                        (df_clean[col] <= upper_bound)
                    ]
                
                elif method == 'zscore':
                    z_scores = np.abs(
                        (df_clean[col] - df_clean[col].mean()) / df_clean[col].std()
                    )
                    df_clean = df_clean[z_scores <= factor]
                
            except Exception as e:
                print(f"Erro ao remover outliers da coluna {col}: {e}")
                continue
        
        return df_clean


# Instâncias globais para uso nas classes especializadas
mapping_manager = MappingManager()
statistical_calculator = StatisticalCalculator()
data_aggregator = DataAggregator()
data_filter = DataFilter()
