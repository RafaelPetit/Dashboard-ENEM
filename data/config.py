"""
Configurações centralizadas para o módulo de dados.
Centraliza caminhos, nomes de arquivos e configurações do sistema.
"""

from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path


@dataclass(frozen=True)
class DataConfig:
    """Configurações imutáveis para carregamento de dados."""
    
    # Caminhos dos arquivos
    GENERIC_FILE: str = "sample_gerenico.parquet"
    
    # Mapeamento de abas para arquivos específicos
    TAB_FILE_MAPPING: Dict[str, str] = None
    
    # Configurações de cache
    CACHE_TTL: int = 3600
    
    # Colunas essenciais
    STATE_COLUMN: str = "SG_UF_PROVA"
    
    # Configurações de otimização
    CATEGORY_THRESHOLD_ABSOLUTE: int = 100
    CATEGORY_THRESHOLD_RELATIVE: float = 0.1
    
    def __post_init__(self):
        if self.TAB_FILE_MAPPING is None:
            object.__setattr__(self, 'TAB_FILE_MAPPING', {
                'geral': 'sample_geral.parquet',
                'aspectos_sociais': 'sample_aspectos_sociais.parquet',
                'desempenho': 'sample_desempenho.parquet'
            })
    
    def get_tab_file_path(self, tab_name: str) -> str:
        """Retorna o caminho do arquivo para uma aba específica."""
        return self.TAB_FILE_MAPPING.get(tab_name.lower(), "")
    
    def validate_tab_name(self, tab_name: str) -> bool:
        """Valida se o nome da aba é suportado."""
        return tab_name.lower() in self.TAB_FILE_MAPPING


@dataclass(frozen=True)
class StatisticsConfig:
    """Configurações para cálculos estatísticos."""
    SUPPORTED_OPERATIONS: List[str] = None
    DEFAULT_OPERATION: str = "media"
    
    def __post_init__(self):
        if self.SUPPORTED_OPERATIONS is None:
            object.__setattr__(self, 'SUPPORTED_OPERATIONS', [
                'media', 'mediana', 'min', 'max', 'std', 'curtose', 'assimetria'
            ])
    
    def is_valid_operation(self, operation: str) -> bool:
        """Verifica se a operação estatística é válida."""
        return operation in self.SUPPORTED_OPERATIONS


# Instâncias globais das configurações
DATA_CONFIG = DataConfig()
STATS_CONFIG = StatisticsConfig()
