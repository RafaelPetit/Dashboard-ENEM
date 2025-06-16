"""
Utilitários comuns para preparação de dados.
Implementa operações frequentemente utilizadas nas classes de preparação.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass

try:
    from data import calcular_seguro
except ImportError:
    # Fallback para evitar erro de importação
    def calcular_seguro(df, percentile=0.95, max_samples=1000):
        """Função de fallback para calcular_seguro."""
        if len(df) <= max_samples:
            return df
        sample_size = int(len(df) * percentile)
        return df.sample(n=min(sample_size, max_samples), random_state=42)

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
    
    def get_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna os mapeamentos globais.
        
        Returns:
            Dicionário com mapeamentos de variáveis
        """
        # Adicionar configurações padrão se não existirem usando nova configuração
        if 'config_processamento' not in self._mappings:
            try:
                from .config import get_legacy_config
                self._mappings['config_processamento'] = get_legacy_config()
            except ImportError:
                # Fallback para valores padrão
                self._mappings['config_processamento'] = {
                    'max_amostras_scatter': 50000,
                    'max_categorias_alerta': 20,
                    'tamanho_lote_estados': 5,
                    'tamanho_lote': 1000,
                    'limiar_agrupamento': 10
                }
        
        return self._mappings
    
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


def optimize_dtypes(df: Union[pd.DataFrame, pd.Series]) -> Union[pd.DataFrame, pd.Series]:
    """
    Otimiza os tipos de dados de um DataFrame ou Series para economizar memória,
    mas mantém precisão para cálculos estatísticos.
    
    Args:
        df: DataFrame ou Series a otimizar
        
    Returns:
        DataFrame ou Series otimizado
    """
    if df is None:
        return df
    
    if isinstance(df, pd.Series):
        return _optimize_series_dtypes(df)
    
    if df.empty:
        return df
    
    try:
        df_optimized = df.copy()
        
        for col in df_optimized.columns:
            try:
                # Para colunas de notas ENEM, manter precisão
                if 'NOTA' in col.upper() or 'DESEMPENHO' in col.upper():
                    if df_optimized[col].dtype == 'float16':
                        # Converter float16 para float64 para evitar overflow
                        df_optimized[col] = df_optimized[col].astype('float64')
                    elif df_optimized[col].dtype == 'float32':
                        # Manter float32 ou promover para float64 se necessário
                        col_max = df_optimized[col].max()
                        if col_max > 1e6:  # Se valores muito grandes, usar float64
                            df_optimized[col] = df_optimized[col].astype('float64')
                    continue
                
                # Otimizar outras colunas numéricas
                if df_optimized[col].dtype in ['int64', 'int32']:
                    col_min = df_optimized[col].min()
                    col_max = df_optimized[col].max()
                    
                    if col_min >= 0:  # Unsigned
                        if col_max <= 255:
                            df_optimized[col] = df_optimized[col].astype('uint8')
                        elif col_max <= 65535:
                            df_optimized[col] = df_optimized[col].astype('uint16')
                        elif col_max <= 4294967295:
                            df_optimized[col] = df_optimized[col].astype('uint32')
                    else:  # Signed
                        if col_min >= -128 and col_max <= 127:
                            df_optimized[col] = df_optimized[col].astype('int8')
                        elif col_min >= -32768 and col_max <= 32767:
                            df_optimized[col] = df_optimized[col].astype('int16')
                        elif col_min >= -2147483648 and col_max <= 2147483647:
                            df_optimized[col] = df_optimized[col].astype('int32')
                
                elif df_optimized[col].dtype == 'float64':
                    # Para outras colunas float, verificar se pode usar float32
                    col_min = df_optimized[col].min()
                    col_max = df_optimized[col].max()
                    
                    # Usar float32 apenas se os valores cabem sem perda de precisão
                    if (col_min >= np.finfo(np.float32).min and 
                        col_max <= np.finfo(np.float32).max and
                        not ('NOTA' in col.upper() or 'DESEMPENHO' in col.upper())):
                        df_optimized[col] = df_optimized[col].astype('float32')
                
                elif df_optimized[col].dtype == 'object':
                    # Verificar se pode ser categoria
                    unique_count = df_optimized[col].nunique()
                    total_count = len(df_optimized[col])
                    
                    # Se menos de 50% de valores únicos, converter para categoria
                    if unique_count / total_count < 0.5:
                        df_optimized[col] = df_optimized[col].astype('category')
                        
            except Exception as e:
                # Se houver erro na otimização, manter tipo original
                print(f"Aviso: Não foi possível otimizar coluna {col}: {e}")
                continue
        
        return df_optimized
        
    except Exception as e:
        print(f"Erro na otimização de tipos: {e}")
        return df


def _optimize_series_dtypes(series: pd.Series) -> pd.Series:
    """Otimiza tipos de dados de uma Series."""
    try:
        if series.dtype in ['int64', 'int32']:
            return pd.to_numeric(series, downcast='integer')
        elif series.dtype == 'float64':
            return pd.to_numeric(series, downcast='float')
        elif series.dtype == 'object':
            unique_count = series.nunique()
            if unique_count / len(series) < 0.5:
                return series.astype('category')
        return series
    except Exception:
        return series


def release_memory(obj: Optional[Any] = None) -> None:
    """
    Libera memória de objetos específicos ou executa coleta de lixo geral.
    
    Args:
        obj: Objeto específico a ser marcado para coleta de lixo (opcional)
    """
    import gc
    
    if obj is not None:
        try:
            del obj
        except Exception:
            pass
    
    # Executar coleta de lixo
    collected = gc.collect()
    
    # Força limpeza adicional se necessário
    if collected > 0:
        gc.collect()


def get_memory_usage() -> Dict[str, Any]:
    """
    Retorna informações sobre o uso atual de memória.
    
    Returns:
        Dicionário com informações de memória
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available
        }
    except ImportError:
        # Fallback se psutil não estiver disponível
        import sys
        return {
            'objects_count': len(gc.get_objects()),
            'python_version': sys.version,
            'available': 'N/A'
        }


def memory_usage_check(threshold_percent: float = 80.0) -> bool:
    """
    Verifica se o uso de memória está acima do limite.
    
    Args:
        threshold_percent: Limite percentual de memória
        
    Returns:
        True se memória está acima do limite
    """
    try:
        memory_info = get_memory_usage()
        if 'percent' in memory_info:
            return memory_info['percent'] > threshold_percent
        return False
    except Exception:
        return False


# Instâncias globais para uso nas classes especializadas
mapping_manager = MappingManager()
statistical_calculator = StatisticalCalculator()
data_aggregator = DataAggregator()
data_filter = DataFilter()


def aplicar_mapeamento(
    df: pd.DataFrame, 
    variavel: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> str:
    """
    Aplica mapeamento a uma variável se necessário e retorna o nome da coluna para uso em gráficos.
    
    Args:
        df: DataFrame com os dados
        variavel: Nome da variável a ser mapeada
        variaveis_sociais: Dicionário com mapeamentos
        
    Returns:
        Nome da coluna a ser usada para plotagem
    """
    # Verificar se a variável existe no DataFrame e no dicionário de mapeamentos
    if variavel not in df.columns:
        print(f"Aviso: Variável '{variavel}' não encontrada no DataFrame")
        return variavel
    
    if variavel not in variaveis_sociais:
        print(f"Aviso: Variável '{variavel}' não encontrada no dicionário de mapeamentos")
        return variavel
    
    # Verificar se precisamos aplicar mapeamento (se não for já do tipo object/string)
    if "mapeamento" in variaveis_sociais[variavel] and df[variavel].dtype != 'object':
        try:
            mapeamento = variaveis_sociais[variavel]["mapeamento"]
            # Aplicar mapeamento criando nova coluna
            coluna_mapeada = f"{variavel}_mapped"
            df[coluna_mapeada] = df[variavel].map(mapeamento).fillna(df[variavel].astype(str))
            return coluna_mapeada
        except Exception as e:
            print(f"Erro ao aplicar mapeamento para {variavel}: {e}")
            return variavel
    
    return variavel


def corrigir_tipos_notas_enem(df):
    """
    Corrige especificamente os tipos de dados das colunas de notas do ENEM
    para evitar overflow em cálculos estatísticos.
    
    Args:
        df: DataFrame com dados do ENEM
        
    Returns:
        DataFrame com tipos corrigidos
    """
    try:
        if df is None or df.empty:
            return df
            
        df_corrigido = df.copy()
        
        # Identificar colunas de notas
        colunas_notas = [col for col in df.columns if 'NOTA' in col.upper()]
        
        for col in colunas_notas:
            # Converter float16 para float64 para evitar overflow
            if df_corrigido[col].dtype == 'float16':
                print(f"Convertendo {col} de float16 para float64")
                df_corrigido[col] = df_corrigido[col].astype('float64')
            
            # Verificar e limpar valores extremos
            serie = df_corrigido[col]
            valores_extremos = (serie > 2000) | (serie < -10)
            if valores_extremos.any():
                print(f"Encontrados {valores_extremos.sum()} valores extremos em {col}")
                # Substituir valores extremos por NaN
                df_corrigido.loc[valores_extremos, col] = np.nan
        
        return df_corrigido
        
    except Exception as e:
        print(f"Erro ao corrigir tipos de notas: {e}")
        return df


def preparar_dados_para_calculo(df, colunas_notas=None):
    """
    Prepara dados para cálculos estatísticos seguros.
    
    Args:
        df: DataFrame com os dados
        colunas_notas: Lista de colunas de notas (auto-detecta se None)
        
    Returns:
        DataFrame preparado
    """
    try:
        if df is None or df.empty:
            return df
            
        df_preparado = df.copy()
        
        # Auto-detectar colunas de notas se não fornecidas
        if colunas_notas is None:
            colunas_notas = [col for col in df.columns if 'NOTA' in col.upper()]
        
        # Corrigir tipos de dados
        df_preparado = corrigir_tipos_notas_enem(df_preparado)
        
        # Otimizar outros tipos mantendo precisão das notas
        df_preparado = optimize_dtypes(df_preparado)
        
        return df_preparado
        
    except Exception as e:
        print(f"Erro na preparação de dados: {e}")
        return df
