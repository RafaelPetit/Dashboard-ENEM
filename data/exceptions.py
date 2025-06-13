"""
Exceções customizadas para o módulo de dados.
Fornece tratamento de erro específico e informativo.
"""


class DataModuleError(Exception):
    """Exceção base para o módulo de dados."""
    pass


class DataLoadError(DataModuleError):
    """Erro durante carregamento de dados."""
    
    def __init__(self, source: str, message: str):
        self.source = source
        super().__init__(f"Erro ao carregar dados de '{source}': {message}")


class DataValidationError(DataModuleError):
    """Erro de validação de dados."""
    
    def __init__(self, field: str, value: str, expected: str):
        self.field = field
        self.value = value
        self.expected = expected
        super().__init__(
            f"Valor inválido para '{field}': '{value}'. Esperado: {expected}"
        )


class DataProcessingError(DataModuleError):
    """Erro durante processamento de dados."""
    
    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Erro na operação '{operation}': {message}")


class MemoryOptimizationError(DataModuleError):
    """Erro durante otimização de memória."""
    
    def __init__(self, message: str):
        super().__init__(f"Erro na otimização de memória: {message}")


class StatisticsCalculationError(DataModuleError):
    """Erro durante cálculo de estatísticas."""
    
    def __init__(self, operation: str, message: str):
        self.operation = operation
        super().__init__(f"Erro no cálculo de '{operation}': {message}")


class UnsupportedOperationError(DataModuleError):
    """Erro para operações não suportadas."""
    
    def __init__(self, operation: str, supported_ops: list):
        self.operation = operation
        self.supported_ops = supported_ops
        super().__init__(
            f"Operação '{operation}' não suportada. "
            f"Operações disponíveis: {', '.join(supported_ops)}"
        )
