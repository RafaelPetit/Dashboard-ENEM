"""
Configurações centralizadas para o módulo prepara_dados.
Implementa o padrão Singleton para configurações globais.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MemoryConfig:
    """Configurações de gestão de memória."""
    max_memory_usage_percent: float = 80.0
    batch_size_states: int = 5
    batch_size_general: int = 1000
    enable_garbage_collection: bool = True
    optimize_dtypes: bool = True
    max_samples_scatter: int = 50000
    memory_check_interval: int = 10


@dataclass
class CacheConfig:
    """Configurações de cache."""
    default_ttl: int = 3600  # 1 hora
    performance_ttl: int = 1800  # 30 minutos
    social_aspects_ttl: int = 1800  # 30 minutos
    general_ttl: int = 3600  # 1 hora
    enable_cache: bool = True
    max_cache_size: int = 1000


@dataclass
class ProcessingConfig:
    """Configurações de processamento."""
    max_categories_alert: int = 50
    grouping_threshold: int = 10
    parallel_processing: bool = False
    max_workers: int = 4
    chunk_size: int = 10000
    enable_progress_bar: bool = True


@dataclass
class ValidationConfig:
    """Configurações de validação."""
    strict_validation: bool = True
    allow_empty_data: bool = False
    required_columns_check: bool = True
    data_type_validation: bool = True
    min_sample_size: int = 10


@dataclass
class VisualizationConfig:
    """Configurações para dados de visualização."""
    max_categories_display: int = 20
    default_chart_height: int = 400
    default_chart_width: int = 800
    color_palette: str = "viridis"
    decimal_places: int = 2


@dataclass
class AppConfig:
    """Configuração principal da aplicação."""
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Configurações do ambiente
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # Caminhos de arquivos
    data_path: Optional[Path] = None
    cache_path: Optional[Path] = None
    log_path: Optional[Path] = None
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        if self.data_path is None:
            self.data_path = Path(__file__).parent.parent.parent
        
        if self.cache_path is None:
            self.cache_path = self.data_path / ".cache"
        
        if self.log_path is None:
            self.log_path = self.data_path / "logs"
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Cria configuração a partir de variáveis de ambiente."""
        config = cls()
        
        # Configurações de ambiente
        config.environment = os.getenv('APP_ENV', 'development')
        config.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        config.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Configurações de memória
        config.memory.max_memory_usage_percent = float(
            os.getenv('MAX_MEMORY_PERCENT', '80.0')
        )
        config.memory.batch_size_states = int(
            os.getenv('BATCH_SIZE_STATES', '5')
        )
        config.memory.max_samples_scatter = int(
            os.getenv('MAX_SAMPLES_SCATTER', '50000')
        )
        
        # Configurações de cache
        config.cache.enable_cache = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
        config.cache.default_ttl = int(os.getenv('CACHE_TTL', '3600'))
        
        # Configurações de processamento
        config.processing.parallel_processing = os.getenv(
            'PARALLEL_PROCESSING', 'false'
        ).lower() == 'true'
        config.processing.max_workers = int(os.getenv('MAX_WORKERS', '4'))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configuração para dicionário."""
        return {
            'memory': {
                'max_memory_usage_percent': self.memory.max_memory_usage_percent,
                'batch_size_states': self.memory.batch_size_states,
                'batch_size_general': self.memory.batch_size_general,
                'enable_garbage_collection': self.memory.enable_garbage_collection,
                'optimize_dtypes': self.memory.optimize_dtypes,
                'max_samples_scatter': self.memory.max_samples_scatter,
                'memory_check_interval': self.memory.memory_check_interval,
            },
            'cache': {
                'default_ttl': self.cache.default_ttl,
                'performance_ttl': self.cache.performance_ttl,
                'social_aspects_ttl': self.cache.social_aspects_ttl,
                'general_ttl': self.cache.general_ttl,
                'enable_cache': self.cache.enable_cache,
                'max_cache_size': self.cache.max_cache_size,
            },
            'processing': {
                'max_categories_alert': self.processing.max_categories_alert,
                'grouping_threshold': self.processing.grouping_threshold,
                'parallel_processing': self.processing.parallel_processing,
                'max_workers': self.processing.max_workers,
                'chunk_size': self.processing.chunk_size,
                'enable_progress_bar': self.processing.enable_progress_bar,
            },
            'validation': {
                'strict_validation': self.validation.strict_validation,
                'allow_empty_data': self.validation.allow_empty_data,
                'required_columns_check': self.validation.required_columns_check,
                'data_type_validation': self.validation.data_type_validation,
                'min_sample_size': self.validation.min_sample_size,
            },
            'visualization': {
                'max_categories_display': self.visualization.max_categories_display,
                'default_chart_height': self.visualization.default_chart_height,
                'default_chart_width': self.visualization.default_chart_width,
                'color_palette': self.visualization.color_palette,
                'decimal_places': self.visualization.decimal_places,
            }
        }


class ConfigManager:
    """Gerenciador singleton de configurações."""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        """Implementa padrão Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o gerenciador de configurações."""
        if self._config is None:
            self._config = AppConfig.from_env()
    
    @property
    def config(self) -> AppConfig:
        """Retorna a configuração atual."""
        if self._config is None:
            self._config = AppConfig.from_env()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Atualiza configurações específicas."""
        if self._config is None:
            self._config = AppConfig.from_env()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def get_memory_config(self) -> MemoryConfig:
        """Retorna configurações de memória."""
        return self.config.memory
    
    def get_cache_config(self) -> CacheConfig:
        """Retorna configurações de cache."""
        return self.config.cache
    
    def get_processing_config(self) -> ProcessingConfig:
        """Retorna configurações de processamento."""
        return self.config.processing
    
    def get_validation_config(self) -> ValidationConfig:
        """Retorna configurações de validação."""
        return self.config.validation
    
    def get_visualization_config(self) -> VisualizationConfig:
        """Retorna configurações de visualização."""
        return self.config.visualization
    
    def get_legacy_config_dict(self) -> Dict[str, Any]:
        """
        Retorna dicionário de configuração no formato legado
        para compatibilidade com código existente.
        """
        return {
            'tamanho_lote_estados': self.config.memory.batch_size_states,
            'tamanho_lote': self.config.memory.batch_size_general,
            'max_categorias_alerta': self.config.processing.max_categories_alert,
            'limiar_agrupamento': self.config.processing.grouping_threshold,
            'max_amostras_scatter': self.config.memory.max_samples_scatter,
            'enable_cache': self.config.cache.enable_cache,
            'cache_ttl': self.config.cache.default_ttl,
        }
    
    def reset_to_defaults(self) -> None:
        """Reseta configurações para os valores padrão."""
        self._config = AppConfig()
    
    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """Retorna a instância singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Instância global do gerenciador de configurações
config_manager = ConfigManager.get_instance()


def get_config() -> AppConfig:
    """Função de conveniência para obter configuração atual."""
    return config_manager.config


def get_legacy_config() -> Dict[str, Any]:
    """
    Função de conveniência para obter configuração no formato legado.
    Usada para manter compatibilidade com código existente.
    """
    return config_manager.get_legacy_config_dict()


def update_config(**kwargs) -> None:
    """Função de conveniência para atualizar configurações."""
    config_manager.update_config(**kwargs)
