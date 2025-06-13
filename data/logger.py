"""
Utilitários de logging para o módulo de dados.
Fornece logging estruturado e configurável.
"""

import logging
import sys
from typing import Optional
from pathlib import Path


class DataLogger:
    """Logger configurado para o módulo de dados."""
    
    _instance: Optional['DataLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'DataLogger':
        """Implementa padrão Singleton para o logger."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self) -> None:
        """Configura o logger com formatação adequada."""
        self._logger = logging.getLogger('data_module')
        
        if not self._logger.handlers:
            # Configurar handler para console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Configurar formatação
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self._logger.addHandler(console_handler)
            self._logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs) -> None:
        """Log de informação."""
        self._logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log de aviso."""
        self._logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log de erro."""
        self._logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log de debug."""
        self._logger.debug(message, extra=kwargs)
    
    def set_level(self, level: str) -> None:
        """Define o nível de logging."""
        level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_mapping:
            self._logger.setLevel(level_mapping[level.upper()])


# Instância global do logger
logger = DataLogger()
