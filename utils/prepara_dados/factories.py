"""
Factory pattern para criação de processadores de dados.
Implementa o padrão Factory para centralizar a criação de objetos
e reduzir acoplamento entre componentes.
"""

from typing import Dict, Optional, Type, Any
from dataclasses import dataclass

from .interfaces import (
    DataValidator, MemoryManager, StatisticsCalculator,
    StateProcessor, RegionAggregator, DataFormatter,
    DataFilterStrategy
)
from .implementations import (
    DefaultDataValidator, DefaultMemoryManager, SafeStatisticsCalculator,
    DefaultRegionAggregator, BaseStateProcessor, VisualizationDataFormatter,
    ScoreFilterStrategy, DemographicFilterStrategy
)


@dataclass
class ProcessorConfig:
    """Configuração para criação de processadores."""
    batch_size: int = 5
    memory_threshold: float = 0.8
    cache_ttl: int = 3600
    enable_optimization: bool = True
    max_samples: int = 50000


class ComponentFactory:
    """Factory para criar componentes básicos."""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_validator(cls) -> DataValidator:
        """Retorna instância singleton do validador."""
        if 'validator' not in cls._instances:
            cls._instances['validator'] = DefaultDataValidator()
        return cls._instances['validator']
    
    @classmethod
    def get_memory_manager(cls) -> MemoryManager:
        """Retorna instância singleton do gerenciador de memória."""
        if 'memory_manager' not in cls._instances:
            cls._instances['memory_manager'] = DefaultMemoryManager()
        return cls._instances['memory_manager']
    
    @classmethod
    def get_stats_calculator(cls) -> StatisticsCalculator:
        """Retorna instância singleton do calculador de estatísticas."""
        if 'stats_calculator' not in cls._instances:
            cls._instances['stats_calculator'] = SafeStatisticsCalculator()
        return cls._instances['stats_calculator']
    
    @classmethod
    def get_region_aggregator(cls) -> RegionAggregator:
        """Retorna instância singleton do agregador de regiões."""
        if 'region_aggregator' not in cls._instances:
            cls._instances['region_aggregator'] = DefaultRegionAggregator()
        return cls._instances['region_aggregator']
    
    @classmethod
    def get_data_formatter(cls) -> DataFormatter:
        """Retorna instância do formatador de dados."""
        return VisualizationDataFormatter(cls.get_memory_manager())
    
    @classmethod
    def clear_instances(cls) -> None:
        """Limpa instâncias cached (útil para testes)."""
        cls._instances.clear()


class FilterStrategyFactory:
    """Factory para estratégias de filtro."""
    
    _strategies: Dict[str, DataFilterStrategy] = {}
    
    @classmethod
    def get_score_filter(cls) -> DataFilterStrategy:
        """Retorna estratégia de filtro por notas."""
        if 'score' not in cls._strategies:
            cls._strategies['score'] = ScoreFilterStrategy()
        return cls._strategies['score']
    
    @classmethod
    def get_demographic_filter(cls) -> DataFilterStrategy:
        """Retorna estratégia de filtro demográfico."""
        if 'demographic' not in cls._strategies:
            cls._strategies['demographic'] = DemographicFilterStrategy()
        return cls._strategies['demographic']
    
    @classmethod
    def create_combined_filter(cls, strategies: list) -> 'CombinedFilterStrategy':
        """Cria estratégia combinada de filtros."""
        return CombinedFilterStrategy(strategies)


class CombinedFilterStrategy:
    """Estratégia que combina múltiplos filtros."""
    
    def __init__(self, strategies: list):
        self.strategies = strategies
    
    def apply_filter(self, data, **criteria):
        """Aplica todos os filtros em sequência."""
        filtered_data = data
        
        for strategy in self.strategies:
            # Extrair critérios específicos para cada estratégia
            strategy_criteria = self._extract_criteria_for_strategy(strategy, criteria)
            filtered_data = strategy.apply_filter(filtered_data, **strategy_criteria)
        
        return filtered_data
    
    def _extract_criteria_for_strategy(self, strategy, all_criteria):
        """Extrai critérios específicos para uma estratégia."""
        if isinstance(strategy, ScoreFilterStrategy):
            return {k: v for k, v in all_criteria.items() 
                   if k in ['exclude_zero_scores', 'min_score', 'max_score', 'score_columns']}
        elif isinstance(strategy, DemographicFilterStrategy):
            return {k: v for k, v in all_criteria.items() 
                   if k in ['gender', 'school_type', 'race', 'income_bracket']}
        return {}


class StateProcessorFactory:
    """Factory específica para processadores de estados."""
    
    @staticmethod
    def create_performance_processor(config: Optional[ProcessorConfig] = None) -> 'PerformanceStateProcessor':
        """Cria processador de desempenho por estados."""
        if config is None:
            config = ProcessorConfig()
        
        return PerformanceStateProcessor(
            validator=ComponentFactory.get_validator(),
            memory_manager=ComponentFactory.get_memory_manager(),
            stats_calculator=ComponentFactory.get_stats_calculator(),
            config=config
        )
    
    @staticmethod
    def create_social_processor(config: Optional[ProcessorConfig] = None) -> 'SocialAspectsStateProcessor':
        """Cria processador de aspectos sociais por estados."""
        if config is None:
            config = ProcessorConfig()
        
        return SocialAspectsStateProcessor(
            validator=ComponentFactory.get_validator(),
            memory_manager=ComponentFactory.get_memory_manager(),
            stats_calculator=ComponentFactory.get_stats_calculator(),
            config=config
        )
    
    @staticmethod
    def create_general_processor(config: Optional[ProcessorConfig] = None) -> 'GeneralStateProcessor':
        """Cria processador geral por estados."""
        if config is None:
            config = ProcessorConfig()
        
        return GeneralStateProcessor(
            validator=ComponentFactory.get_validator(),
            memory_manager=ComponentFactory.get_memory_manager(),
            stats_calculator=ComponentFactory.get_stats_calculator(),
            config=config
        )


# Implementações específicas dos processadores
class PerformanceStateProcessor(BaseStateProcessor):
    """Processador específico para dados de desempenho."""
    
    def __init__(self, validator, memory_manager, stats_calculator, config: ProcessorConfig):
        super().__init__(validator, memory_manager, stats_calculator)
        self.config = config
    
    def process_single_state(self, data, state: str, **kwargs):
        """Processa dados de desempenho de um estado."""
        score_columns = kwargs.get('score_columns', [])
        competence_mapping = kwargs.get('competence_mapping', {})
        
        if not score_columns:
            return None
        
        results = []
        state_means = []
        
        for column in score_columns:
            if column not in data.columns:
                continue
            
            # Filtrar notas válidas
            valid_scores = data[data[column] > 0][column]
            
            if len(valid_scores) > 0:
                mean_score = self.stats_calculator.calculate_mean(valid_scores.tolist())
                area_name = competence_mapping.get(column, column)
                
                results.append({
                    'Estado': state,
                    'Area': area_name,
                    'Media': round(mean_score, 2)
                })
                state_means.append(mean_score)
        
        # Adicionar média geral
        if state_means:
            general_mean = sum(state_means) / len(state_means)
            results.append({
                'Estado': state,
                'Area': 'Média Geral',
                'Media': round(general_mean, 2)
            })
        
        return results


class SocialAspectsStateProcessor(BaseStateProcessor):
    """Processador específico para aspectos sociais."""
    
    def __init__(self, validator, memory_manager, stats_calculator, config: ProcessorConfig):
        super().__init__(validator, memory_manager, stats_calculator)
        self.config = config
    
    def process_single_state(self, data, state: str, **kwargs):
        """Processa aspectos sociais de um estado."""
        social_aspect = kwargs.get('social_aspect')
        social_variables = kwargs.get('social_variables', {})
        
        if not social_aspect or social_aspect not in data.columns:
            return None
          # Aplicar mapeamento se necessário - implementação básica
        plot_column = social_aspect
        if social_aspect in social_variables:
            if "mapeamento" in social_variables[social_aspect] and data[social_aspect].dtype != 'object':
                # Aplicar mapeamento simples
                mapping = social_variables[social_aspect]["mapeamento"]
                data_copy = data.copy()
                data_copy[f"{social_aspect}_mapped"] = data_copy[social_aspect].map(mapping).fillna(data_copy[social_aspect])
                plot_column = f"{social_aspect}_mapped"
                data = data_copy
        
        # Contar categorias
        total_state = len(data)
        category_counts = data[plot_column].value_counts()
        
        # Obter categorias possíveis
        if "mapeamento" in social_variables.get(social_aspect, {}):
            categories = list(social_variables[social_aspect]["mapeamento"].values())
        else:
            categories = data[plot_column].unique().tolist()
        
        results = []
        for category in categories:
            count = category_counts.get(category, 0)
            percentage = (count / total_state * 100) if total_state > 0 else 0
            
            results.append({
                'Estado': state,
                'Categoria': category,
                'Quantidade': count,
                'Percentual': round(percentage, 2)
            })
        
        return results


class GeneralStateProcessor(BaseStateProcessor):
    """Processador geral para dados diversos."""
    
    def __init__(self, validator, memory_manager, stats_calculator, config: ProcessorConfig):
        super().__init__(validator, memory_manager, stats_calculator)
        self.config = config
    
    def process_single_state(self, data, state: str, **kwargs):
        """Processa dados gerais de um estado."""
        metric_type = kwargs.get('metric_type', 'mean')
        columns = kwargs.get('columns', [])
        
        if not columns:
            return None
        
        result = {'Estado': state}
        
        for column in columns:
            if column not in data.columns:
                continue
            
            valid_data = data[data[column].notna()]
            
            if len(valid_data) > 0:
                if metric_type == 'mean':
                    value = self.stats_calculator.calculate_mean(valid_data[column].tolist())
                elif metric_type == 'median':
                    value = self.stats_calculator.calculate_median(valid_data[column].tolist())
                elif metric_type == 'count':
                    value = len(valid_data)
                else:
                    value = self.stats_calculator.calculate_mean(valid_data[column].tolist())
                
                result[column] = round(value, 2) if isinstance(value, float) else value
        
        return result if len(result) > 1 else None


class DataProcessingOrchestrator:
    """Orquestrador principal para processamento de dados."""
    
    def __init__(self):
        self.validator = ComponentFactory.get_validator()
        self.memory_manager = ComponentFactory.get_memory_manager()
        self.region_aggregator = ComponentFactory.get_region_aggregator()
        self.data_formatter = ComponentFactory.get_data_formatter()
    
    def process_performance_data(self, data, states: list, score_columns: list, 
                               competence_mapping: dict, group_by_region: bool = False):
        """Processa dados de desempenho completos."""
        processor = StateProcessorFactory.create_performance_processor()
        
        # Processar por estados
        results = processor.process_states_batch(
            data, states,
            score_columns=score_columns,
            competence_mapping=competence_mapping,
            required_columns=score_columns
        )
        
        # Flatten results (cada estado retorna uma lista)
        flattened_results = []
        for state_results in results:
            if isinstance(state_results, list):
                flattened_results.extend(state_results)
            elif state_results:
                flattened_results.append(state_results)
        
        # Agrupar por região se solicitado
        if group_by_region:
            flattened_results = self.region_aggregator.group_by_region(flattened_results)
        
        # Formatar para visualização
        return self.data_formatter.format_for_line_chart(flattened_results)
    
    def process_social_aspects_data(self, data, states: list, social_aspect: str,
                                  social_variables: dict, group_by_region: bool = False):
        """Processa dados de aspectos sociais completos."""
        processor = StateProcessorFactory.create_social_processor()
        
        # Processar por estados
        results = processor.process_states_batch(
            data, states,
            social_aspect=social_aspect,
            social_variables=social_variables,
            required_columns=[social_aspect]
        )
        
        # Flatten results
        flattened_results = []
        for state_results in results:
            if isinstance(state_results, list):
                flattened_results.extend(state_results)
            elif state_results:
                flattened_results.append(state_results)
        
        # Agrupar por região se solicitado
        if group_by_region:
            flattened_results = self.region_aggregator.group_by_region(flattened_results)
        
        # Formatar para visualização
        return self.data_formatter.format_for_line_chart(flattened_results)
