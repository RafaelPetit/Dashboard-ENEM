"""
Implementações concretas das interfaces para o módulo prepara_dados.
Implementa os princípios SOLID com baixo acoplamento e alta coesão.
"""

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from functools import lru_cache

from .interfaces import (
    DataValidator, CacheManager, MemoryManager, 
    StateProcessor, RegionAggregator, DataFormatter,
    StatisticsCalculator, DataFilterStrategy
)
from .common_utils import optimize_dtypes, release_memory
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function

# Import data functions
try:
    from data import calcular_seguro
except ImportError:
    # Fallback robusto para cálculos seguros
    def calcular_seguro(values, operation):
        import numpy as np
        import warnings
        
        try:
            # Converter para array numpy
            if hasattr(values, 'values'):
                arr = values.values
            else:
                arr = np.asarray(values)
            
            # Converter para dtype mais preciso se necessário
            if arr.dtype in [np.float16, np.int8, np.int16]:
                arr = arr.astype(np.float64)
            
            # Filtrar valores válidos
            mask = np.isfinite(arr) & (arr >= -1) & (arr <= 2000)  # Para notas ENEM
            if not np.any(mask):
                return 0.0
                
            valid_data = arr[mask]
            
            # Para cálculos estatísticos, usar apenas valores >= 0 (excluir -1 de ausência)
            if operation in ['media', 'desvio']:
                valid_data = valid_data[valid_data >= 0]
                if len(valid_data) == 0:
                    return 0.0
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                
                if operation == 'media':
                    # Para datasets grandes, calcular em chunks
                    if len(valid_data) > 1000000:
                        chunk_size = 100000
                        chunks = [valid_data[i:i+chunk_size] for i in range(0, len(valid_data), chunk_size)]
                        chunk_means = [np.mean(chunk.astype(np.float64)) for chunk in chunks]
                        chunk_sizes = [len(chunk) for chunk in chunks]
                        result = np.average(chunk_means, weights=chunk_sizes)
                    else:
                        result = np.mean(valid_data.astype(np.float64))
                    return float(result) if np.isfinite(result) else 0.0
                    
                elif operation == 'mediana':
                    # Para datasets grandes, usar amostragem
                    if len(valid_data) > 1000000:
                        sample_size = min(100000, len(valid_data))
                        sample_data = np.random.choice(valid_data, size=sample_size, replace=False)
                        result = np.median(sample_data)
                    else:
                        result = np.median(valid_data)
                    return float(result) if np.isfinite(result) else 0.0
                    
                elif operation == 'desvio':
                    if len(valid_data) < 2:
                        return 0.0
                    result = np.std(valid_data.astype(np.float64), ddof=1)
                    return float(result) if np.isfinite(result) else 0.0
                    
                elif operation == 'min':
                    result = np.min(valid_data)
                    return float(result) if np.isfinite(result) else 0.0
                    
                elif operation == 'max':
                    result = np.max(valid_data)
                    return float(result) if np.isfinite(result) else 0.0
                    
                elif operation == 'curtose':
                    try:
                        from scipy import stats
                        if len(valid_data) > 3:
                            # Para dados de notas, usar apenas valores >= 0
                            calc_data = valid_data[valid_data >= 0] if len(valid_data) > 1000 else valid_data
                            if len(calc_data) > 3:
                                result = stats.kurtosis(calc_data.astype(np.float64), nan_policy='omit')
                                return float(result) if np.isfinite(result) else 0.0
                    except Exception:
                        pass
                    return 0.0
                    
                elif operation == 'assimetria':
                    try:
                        from scipy import stats
                        if len(valid_data) > 2:
                            # Para dados de notas, usar apenas valores >= 0
                            calc_data = valid_data[valid_data >= 0] if len(valid_data) > 1000 else valid_data
                            if len(calc_data) > 2:
                                result = stats.skew(calc_data.astype(np.float64), nan_policy='omit')
                                return float(result) if np.isfinite(result) else 0.0
                    except Exception:
                        pass
                    return 0.0
                    
                else:
                    return 0.0
                    
        except Exception as e:
            print(f"Erro no cálculo seguro de {operation}: {e}")
            return 0.0


class DefaultDataValidator:
    """Implementação padrão do validador de dados."""
    
    def validate(self, data: Union[pd.DataFrame, pd.Series], required_columns: List[str]) -> bool:
        """
        Valida se os dados atendem aos requisitos básicos.
        
        Args:
            data: DataFrame ou Series a validar
            required_columns: Colunas obrigatórias
            
        Returns:
            True se válido, False caso contrário
        """
        if data is None:
            return False
            
        if isinstance(data, pd.Series):
            return not data.empty
            
        if data.empty:
            return False
            
        # Verificar se todas as colunas obrigatórias existem
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            print(f"Colunas ausentes: {missing_columns}")
            return False
            
        return True


class DefaultMemoryManager:
    """Implementação padrão do gerenciador de memória."""
    
    def release(self) -> None:
        """Libera memória não utilizada."""
        release_memory()
    
    def optimize_dtypes(self, df: Union[pd.DataFrame, pd.Series]) -> Union[pd.DataFrame, pd.Series]:
        """Otimiza tipos de dados para economizar memória."""
        return optimize_dtypes(df)


class SafeStatisticsCalculator:
    """Calculadora segura de estatísticas."""
    
    def calculate_mean(self, values: List[float]) -> float:
        """Calcula média de forma segura."""
        if not values:
            return 0.0
        return calcular_seguro(values, 'media')
    
    def calculate_median(self, values: List[float]) -> float:
        """Calcula mediana de forma segura."""
        if not values:
            return 0.0
        return calcular_seguro(values, 'mediana')
    
    def calculate_std(self, values: List[float]) -> float:
        """Calcula desvio padrão de forma segura."""
        if not values:
            return 0.0
        return calcular_seguro(values, 'desvio')
    
    def calculate_safe(self, values, operation: str) -> float:
        """
        Método genérico para cálculos seguros de estatísticas.
        
        Args:
            values: Array ou Series com os dados
            operation: Tipo de operação ('media', 'mediana', 'desvio', 'curtose', 'assimetria', etc.)
            
        Returns:
            Resultado da operação ou 0.0 se erro
        """
        try:
            if operation == 'curtose':
                return calcular_seguro(values, 'curtose')
            elif operation == 'assimetria':
                return calcular_seguro(values, 'assimetria')
            elif operation == 'media':
                return calcular_seguro(values, 'media')
            elif operation == 'mediana':
                return calcular_seguro(values, 'mediana')
            elif operation == 'desvio':
                return calcular_seguro(values, 'desvio')
            elif operation == 'min':
                return calcular_seguro(values, 'min')
            elif operation == 'max':
                return calcular_seguro(values, 'max')
            else:
                return calcular_seguro(values, operation)
        except Exception as e:
            print(f"Erro no cálculo seguro de {operation}: {e}")
            return 0.0


class DefaultRegionAggregator:
    """Agregador padrão por regiões."""
    
    def __init__(self):
        # Lazy import para evitar dependência circular
        self._region_mapper = None
    
    @property
    def region_mapper(self):
        """Carrega mapeamento de regiões sob demanda."""
        if self._region_mapper is None:
            from utils.helpers.regiao_utils import obter_regiao_do_estado
            self._region_mapper = obter_regiao_do_estado
        return self._region_mapper
    
    def group_by_region(self, state_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Agrupa dados de estados por região.
        
        Args:
            state_data: Lista de dicionários com dados por estado
            
        Returns:
            Lista de dicionários com dados agrupados por região
        """
        if not state_data:
            return []
        
        try:
            # Converter para DataFrame para facilitar agregação
            df = pd.DataFrame(state_data)
            
            if 'Estado' not in df.columns:
                return state_data
            
            # Adicionar coluna de região
            df['Regiao'] = df['Estado'].apply(self.region_mapper)
            
            # Remover estados sem região
            df = df[df['Regiao'] != ""]
            
            # Identificar colunas numéricas para agregação
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Agrupar por região
            result = []
            for region, group in df.groupby('Regiao'):
                region_data = {'Estado': region}  # Usar região como "estado"
                
                # Calcular médias para colunas numéricas
                for col in numeric_columns:
                    if col in group.columns:
                        region_data[col] = round(group[col].mean(), 2)
                
                # Manter outras colunas (primeira ocorrência)
                for col in group.columns:
                    if col not in numeric_columns + ['Estado', 'Regiao']:
                        region_data[col] = group[col].iloc[0]
                
                result.append(region_data)
            
            return result
            
        except Exception as e:
            print(f"Erro na agregação por regiões: {e}")
            return state_data


class ScoreFilterStrategy:
    """Strategy para filtrar dados por notas."""
    
    def apply_filter(self, data: pd.DataFrame, 
                    exclude_zero_scores: bool = True,
                    min_score: Optional[float] = None,
                    max_score: Optional[float] = None,
                    score_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Aplica filtros relacionados a notas.
        
        Args:
            data: DataFrame a filtrar
            exclude_zero_scores: Se True, exclui notas zero
            min_score: Nota mínima (opcional)
            max_score: Nota máxima (opcional)
            score_columns: Colunas de notas a considerar
            
        Returns:
            DataFrame filtrado
        """
        if data.empty:
            return data
        
        filtered_data = data.copy()
        
        if score_columns is None:
            # Detectar colunas de notas automaticamente
            score_columns = [col for col in data.columns if 'NU_NOTA' in col or 'NOTA' in col]
        
        # Aplicar filtros por coluna de nota
        for col in score_columns:
            if col not in filtered_data.columns:
                continue
                
            if exclude_zero_scores:
                filtered_data = filtered_data[filtered_data[col] > 0]
            
            if min_score is not None:
                filtered_data = filtered_data[filtered_data[col] >= min_score]
            
            if max_score is not None:
                filtered_data = filtered_data[filtered_data[col] <= max_score]
        
        return filtered_data


class DemographicFilterStrategy:
    """Strategy para filtrar dados demográficos."""
    
    def apply_filter(self, data: pd.DataFrame,
                    gender: Optional[str] = None,
                    school_type: Optional[str] = None,
                    race: Optional[str] = None,
                    income_bracket: Optional[int] = None) -> pd.DataFrame:
        """
        Aplica filtros demográficos.
        
        Args:
            data: DataFrame a filtrar
            gender: Filtro por sexo ('M' ou 'F')
            school_type: Filtro por tipo de escola ('Pública' ou 'Privada')
            race: Filtro por raça/cor
            income_bracket: Filtro por faixa de renda
            
        Returns:
            DataFrame filtrado
        """
        if data.empty:
            return data
        
        filtered_data = data.copy()
        
        # Filtro por sexo
        if gender and 'TP_SEXO' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['TP_SEXO'] == gender]
        
        # Filtro por tipo de escola
        if school_type and 'TP_DEPENDENCIA_ADM_ESC' in filtered_data.columns:
            if school_type == 'Pública':
                filtered_data = filtered_data[filtered_data['TP_DEPENDENCIA_ADM_ESC'].isin(['1', '2', '3'])]
            elif school_type == 'Privada':
                filtered_data = filtered_data[filtered_data['TP_DEPENDENCIA_ADM_ESC'] == '4']
        
        # Filtro por raça/cor
        if race and 'TP_COR_RACA' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['TP_COR_RACA'] == race]
        
        # Filtro por faixa de renda
        if income_bracket is not None and 'TP_FAIXA_SALARIAL' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['TP_FAIXA_SALARIAL'] == income_bracket]
        
        return filtered_data


class BaseStateProcessor:
    """Implementação base para processamento por estados."""
    
    def __init__(self, 
                 validator: DataValidator,
                 memory_manager: MemoryManager,
                 stats_calculator: StatisticsCalculator):
        self.validator = validator
        self.memory_manager = memory_manager
        self.stats_calculator = stats_calculator
        self.state_column = "SG_UF_PROVA"
    
    def validate_input(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """Valida dados de entrada."""
        return self.validator.validate(data, required_columns + [self.state_column])
    
    def group_by_states(self, data: pd.DataFrame, states: List[str]) -> pd.core.groupby.DataFrameGroupBy:
        """
        Agrupa dados por estados de forma otimizada.
        
        Args:
            data: DataFrame com dados
            states: Lista de estados
            
        Returns:
            GroupBy object
        """
        if self.state_column not in data.columns:
            raise ValueError(f"Coluna {self.state_column} não encontrada")
        
        # Filtrar apenas estados necessários
        filtered_data = data[data[self.state_column].isin(states)]
        return filtered_data.groupby(self.state_column, observed=True)
    
    @memory_intensive_function
    def process_states_batch(self, data: pd.DataFrame, states: List[str], 
                           batch_size: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Processa estados em lotes com controle de memória.
        
        Args:
            data: DataFrame com dados
            states: Lista de estados
            batch_size: Tamanho do lote
            **kwargs: Argumentos específicos
            
        Returns:
            Lista de resultados
        """
        if not self.validate_input(data, kwargs.get('required_columns', [])):
            return []
        
        try:
            grouped = self.group_by_states(data, states)
            results = []
            
            for i, state in enumerate(states):
                try:
                    state_data = grouped.get_group(state)
                    result = self.process_single_state(state_data, state, **kwargs)
                    if result:
                        results.append(result)
                    
                    # Liberar memória a cada lote
                    if (i + 1) % batch_size == 0:
                        self.memory_manager.release()
                        
                except KeyError:
                    continue  # Estado não encontrado
                except Exception as e:
                    print(f"Erro ao processar estado {state}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Erro no processamento em lotes: {e}")
            return []
    
    def process_single_state(self, data: pd.DataFrame, state: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Método base para processar um único estado.
        Deve ser sobrescrito pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar process_single_state")


class VisualizationDataFormatter:
    """Formatador de dados para visualização."""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
    
    def format_for_line_chart(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Formata dados para gráfico de linha.
        
        Args:
            data: Lista de dados por estado/categoria
            
        Returns:
            DataFrame formatado
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Otimizar tipos
        df = self.memory_manager.optimize_dtypes(df)
        
        return df
    
    def format_for_bar_chart(self, data: List[Dict[str, Any]], 
                           group_column: str, value_column: str) -> pd.DataFrame:
        """
        Formata dados para gráfico de barras.
        
        Args:
            data: Lista de dados
            group_column: Coluna de agrupamento
            value_column: Coluna de valores
            
        Returns:
            DataFrame formatado
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Verificar se as colunas existem
        if group_column not in df.columns or value_column not in df.columns:
            return df
        
        # Pivotar dados se necessário
        if len(df.columns) > 2:
            try:
                df_pivot = df.pivot_table(
                    index=group_column, 
                    values=value_column, 
                    aggfunc='mean'
                ).reset_index()
                df = df_pivot
            except Exception as e:
                print(f"Erro ao pivotar dados: {e}")
        
        # Otimizar tipos
        df = self.memory_manager.optimize_dtypes(df)
        
        return df
    
    def format_for_scatter_plot(self, data: pd.DataFrame, 
                              x_column: str, y_column: str,
                              max_samples: int = 50000) -> pd.DataFrame:
        """
        Formata dados para gráfico de dispersão.
        
        Args:
            data: DataFrame com dados
            x_column: Coluna do eixo X
            y_column: Coluna do eixo Y
            max_samples: Número máximo de amostras
            
        Returns:
            DataFrame formatado
        """
        if data.empty or x_column not in data.columns or y_column not in data.columns:
            return pd.DataFrame()
        
        # Selecionar apenas colunas necessárias
        columns_needed = [x_column, y_column]
        df = data[columns_needed].copy()
        
        # Remover valores nulos
        df = df.dropna()
        
        # Limitar amostras para performance
        if len(df) > max_samples:
            df = df.sample(n=max_samples, random_state=42)
        
        # Otimizar tipos
        df = self.memory_manager.optimize_dtypes(df)
        
        return df
