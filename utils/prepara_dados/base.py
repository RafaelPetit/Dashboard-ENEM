"""
Classes base genéricas para preparação de dados do Dashboard ENEM.
Implementa padrões SOLID, Clean Code e otimizações de performance.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union, TypeVar, Generic
from dataclasses import dataclass
import pandas as pd
import numpy as np

from data.data_loader import calcular_seguro, optimize_dtypes
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from utils.prepara_dados.validacao_dados import validar_completude_dados
from utils.helpers.regiao_utils import obter_regiao_do_estado
from utils.mappings import get_mappings

# Type variables
T = TypeVar('T')
DataFrameType = pd.DataFrame
ResultType = TypeVar('ResultType')

# Obter configurações globais
mappings = get_mappings()
CONFIG_PROCESSAMENTO = mappings.get('config_processamento', {})
LIMIARES_PROCESSAMENTO = mappings.get('limiares_processamento', {})


@dataclass(frozen=True)
class ProcessingConfig:
    """Configurações para processamento de dados."""
    
    # Cache
    cache_ttl: int = 1800  # 30 minutos
    cache_max_entries: int = 100
    
    # Performance
    batch_size: int = 1000
    memory_limit_mb: int = 500
    
    # Validação
    min_completude: float = 0.7
    min_valores_unicos: int = 5
    
    # Otimização
    optimize_dtypes: bool = True
    use_categoricals: bool = True


class BaseDataProcessor(ABC, Generic[T]):
    """
    Classe base abstrata para processadores de dados.
    Implementa padrão Template Method e Strategy.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """
        Inicializa o processador.
        
        Args:
            config: Configurações de processamento
        """
        self.config = config or ProcessingConfig()
        self._mappings = get_mappings()
        
    @abstractmethod
    def process(self, data: DataFrameType, **kwargs) -> T:
        """
        Método principal de processamento (Template Method).
        
        Args:
            data: DataFrame a ser processado
            **kwargs: Argumentos específicos do processador
            
        Returns:
            Resultado processado
        """
        pass
    
    def validate_input(self, data: DataFrameType, required_columns: List[str]) -> bool:
        """
        Valida dados de entrada.
        
        Args:
            data: DataFrame a validar
            required_columns: Colunas obrigatórias
            
        Returns:
            True se dados são válidos
        """
        if data is None or data.empty:
            return False
            
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            print(f"Aviso: Colunas faltantes: {missing_columns}")
            return False
            
        # Validar completude dos dados
        dados_validos, taxas_completude = validar_completude_dados(
            data, required_columns, self.config.min_completude
        )
        
        if not dados_validos:
            problemas = [f"{col}: {taxa:.1%}" for col, taxa in taxas_completude.items() 
                        if taxa < self.config.min_completude]
            print(f"Aviso: Baixa completude - {problemas}")
            
        return True
    
    def optimize_dataframe(self, df: DataFrameType) -> DataFrameType:
        """
        Otimiza DataFrame para economia de memória.
        
        Args:
            df: DataFrame a otimizar
            
        Returns:
            DataFrame otimizado
        """
        if not self.config.optimize_dtypes or df.empty:
            return df
            
        try:
            return optimize_dtypes(df)
        except Exception as e:
            print(f"Aviso: Erro na otimização de tipos: {e}")
            return df
    
    def apply_categorical_optimization(self, df: DataFrameType, 
                                     categorical_columns: List[str]) -> DataFrameType:
        """
        Aplica otimização categórica a colunas específicas.
        
        Args:
            df: DataFrame a otimizar
            categorical_columns: Colunas para converter em categóricas
            
        Returns:
            DataFrame com colunas categóricas otimizadas
        """
        if not self.config.use_categoricals or df.empty:
            return df
            
        df_optimized = df.copy()
        
        for col in categorical_columns:
            if col in df_optimized.columns:
                try:
                    unique_values = df_optimized[col].nunique()
                    total_values = len(df_optimized[col])
                    
                    # Converter para categórica se for eficiente
                    if unique_values < total_values * 0.5:  # Menos de 50% de valores únicos
                        df_optimized[col] = pd.Categorical(df_optimized[col])
                except Exception as e:
                    print(f"Aviso: Erro ao categorizar coluna {col}: {e}")
                    
        return df_optimized
    
    def process_in_batches(self, data: DataFrameType, 
                          batch_processor: callable, 
                          **kwargs) -> List[Any]:
        """
        Processa dados em lotes para economia de memória.
        
        Args:
            data: DataFrame a processar
            batch_processor: Função para processar cada lote
            **kwargs: Argumentos para o processador
            
        Returns:
            Lista de resultados processados
        """
        if data.empty:
            return []
            
        results = []
        batch_size = self.config.batch_size
        
        for i in range(0, len(data), batch_size):
            batch = data.iloc[i:i + batch_size]
            
            try:
                with ContextTimer(performance_monitor, f"batch_process_{i//batch_size}"):
                    result = batch_processor(batch, **kwargs)
                    results.append(result)
            except Exception as e:
                print(f"Erro no lote {i//batch_size}: {e}")
                continue
                
        return results


class CacheableProcessor(BaseDataProcessor[T]):
    """
    Processador com capacidades de cache automático.
    Implementa padrão Decorator para cache.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None, 
                 cache_key_prefix: str = "processor"):
        """
        Inicializa processador com cache.
        
        Args:
            config: Configurações de processamento
            cache_key_prefix: Prefixo para chaves de cache
        """
        super().__init__(config)
        self.cache_prefix = cache_key_prefix
    
    def _generate_cache_key(self, data: DataFrameType, **kwargs) -> str:
        """
        Gera chave única para cache baseada nos dados e parâmetros.
        
        Args:
            data: DataFrame de entrada
            **kwargs: Parâmetros adicionais
            
        Returns:
            Chave de cache única
        """
        # Usar hash do shape, colunas e parâmetros
        data_hash = hash((
            data.shape,
            tuple(data.columns),
            tuple(sorted(kwargs.items()))
        ))
        
        return f"{self.cache_prefix}_{abs(data_hash)}"
    
    def cached_process(self, data: DataFrameType, **kwargs) -> T:
        """
        Processa com cache automático.
        
        Args:
            data: DataFrame a processar
            **kwargs: Argumentos específicos
            
        Returns:
            Resultado processado (do cache ou novo)
        """
        cache_key = self._generate_cache_key(data, **kwargs)
        
        # Tentar obter do cache
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            performance_monitor.record_cache_hit()
            return cached_result
        
        # Processar e armazenar no cache
        performance_monitor.record_cache_miss()
        
        with ContextTimer(performance_monitor, "data_processing"):
            result = self.process(data, **kwargs)
            
        cache_manager.set(cache_key, result, ttl=self.config.cache_ttl)
        
        return result


class StateGroupedProcessor(CacheableProcessor[T]):
    """
    Processador especializado em agrupamento por estados.
    Implementa Strategy Pattern para diferentes tipos de agrupamento.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """Inicializa processador de estados."""
        super().__init__(config, "state_processor")
        self.state_column = "SG_UF_PROVA"
    
    def group_by_states(self, data: DataFrameType, 
                       states: List[str]) -> pd.core.groupby.DataFrameGroupBy:
        """
        Agrupa dados por estados de forma otimizada.
        
        Args:
            data: DataFrame com dados
            states: Lista de estados
            
        Returns:
            GroupBy object para processamento eficiente
        """
        if self.state_column not in data.columns:
            raise ValueError(f"Coluna {self.state_column} não encontrada")
            
        # Filtrar apenas estados necessários para economia de memória
        data_filtered = data[data[self.state_column].isin(states)]
        
        return data_filtered.groupby(self.state_column, observed=True)
    
    def process_states_in_parallel(self, data: DataFrameType, states: List[str],
                                 state_processor: callable, **kwargs) -> List[Dict[str, Any]]:
        """
        Processa estados em paralelo com controle de memória.
        
        Args:
            data: DataFrame com dados
            states: Lista de estados a processar
            state_processor: Função para processar cada estado
            **kwargs: Argumentos para o processador
            
        Returns:
            Lista de resultados por estado
        """
        try:
            grouped = self.group_by_states(data, states)
            results = []
            
            for state in states:
                try:
                    state_data = grouped.get_group(state)
                    
                    with ContextTimer(performance_monitor, f"process_state_{state}"):
                        result = state_processor(state_data, state=state, **kwargs)
                        results.append(result)
                        
                except KeyError:
                    # Estado não encontrado, continuar
                    continue
                except Exception as e:
                    print(f"Erro ao processar estado {state}: {e}")
                    continue
                    
            return results
            
        except Exception as e:
            print(f"Erro no processamento por estados: {e}")
            return []
    
    def aggregate_by_regions(self, state_results: List[Dict[str, Any]], 
                           value_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Agrega resultados por região.
        
        Args:
            state_results: Resultados por estado
            value_columns: Colunas com valores numéricos para agregar
            
        Returns:
            Resultados agregados por região
        """
        if not state_results:
            return []
            
        # Converter para DataFrame para facilitar agregação
        df_results = pd.DataFrame(state_results)
        
        if 'Estado' not in df_results.columns:
            return state_results
        
        try:
            # Adicionar coluna de região
            df_results['Regiao'] = df_results['Estado'].apply(obter_regiao_do_estado)
            
            # Agrupar por região
            region_groups = df_results.groupby('Regiao')
            
            region_results = []
            for region, group in region_groups:
                if not region:  # Ignorar regiões vazias
                    continue
                    
                region_data = {'Estado': region}  # Usar região como "estado"
                
                # Calcular médias para colunas numéricas
                for col in value_columns:
                    if col in group.columns:
                        region_data[col] = group[col].mean()
                
                # Manter outras colunas (primeira ocorrência)
                for col in group.columns:
                    if col not in value_columns + ['Estado', 'Regiao']:
                        region_data[col] = group[col].iloc[0]
                
                region_results.append(region_data)
            
            return region_results
            
        except Exception as e:
            print(f"Erro na agregação por regiões: {e}")
            return state_results


# Factory para criar processadores
class DataProcessorFactory:
    """Factory para criar diferentes tipos de processadores."""
    
    @staticmethod
    def create_basic_processor(config: Optional[ProcessingConfig] = None) -> BaseDataProcessor:
        """Cria processador básico."""
        return CacheableProcessor(config)
    
    @staticmethod
    def create_state_processor(config: Optional[ProcessingConfig] = None) -> StateGroupedProcessor:
        """Cria processador de estados."""
        return StateGroupedProcessor(config)
    
    @staticmethod
    def create_custom_processor(processor_class: type, 
                              config: Optional[ProcessingConfig] = None) -> BaseDataProcessor:
        """Cria processador customizado."""
        return processor_class(config)


# Alias para compatibilidade
ProcessorFactory = DataProcessorFactory
