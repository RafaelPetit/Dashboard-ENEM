# GUIA DE IMPLEMENTAÇÃO: REFATORAÇÃO DO MÓDULO ESTATÍSTICAS

## ARQUITETURA ALVO RECOMENDADA

```
utils/estatisticas/
├── core/
│   ├── interfaces.py              # Interfaces e abstrações
│   ├── base_analyzer.py           # Classe base para analisadores
│   ├── result.py                  # Classes para resultados padronizados
│   └── exceptions.py              # Exceções específicas do domínio
├── factories/
│   ├── analyzer_factory.py        # Factory para analisadores
│   ├── validator_factory.py       # Factory para validadores
│   └── result_builder_factory.py  # Factory para builders
├── analyzers/
│   ├── correlation/
│   │   ├── correlation_analyzer.py
│   │   ├── chi_square_calculator.py
│   │   └── mutual_info_calculator.py
│   ├── distribution/
│   │   ├── distribution_analyzer.py
│   │   ├── concentration_calculator.py
│   │   └── entropy_calculator.py
│   ├── performance/
│   │   ├── performance_analyzer.py
│   │   ├── state_comparator.py
│   │   └── competency_analyzer.py
│   └── social/
│       ├── social_analyzer.py
│       ├── demographic_analyzer.py
│       └── socioeconomic_analyzer.py
├── validators/
│   ├── data_validator.py          # Validação de dados de entrada
│   ├── statistical_validator.py   # Validação de premissas estatísticas
│   └── result_validator.py        # Validação de resultados
├── builders/
│   ├── result_builder.py          # Builder genérico para resultados
│   ├── metadata_builder.py        # Builder para metadata
│   └── interpretation_builder.py  # Builder para interpretações
├── interpreters/
│   ├── statistical_interpreter.py # Interpretações estatísticas
│   ├── context_interpreter.py     # Interpretações contextuais
│   └── trend_interpreter.py       # Interpretações de tendências
├── config/
│   ├── thresholds.py             # Constantes e thresholds
│   ├── mappings.py               # Mapeamentos de domínio
│   └── settings.py               # Configurações gerais
└── utils/
    ├── cache_manager.py          # Gerenciamento de cache
    ├── data_processor.py         # Processamento de dados
    └── math_utils.py             # Utilitários matemáticos
```

---

## PADRÕES DE DESIGN RECOMENDADOS

### 1. FACTORY PATTERN

```python
# analyzers/factories/analyzer_factory.py
from typing import Dict, Type
from ..core.interfaces import IAnalyzer
from ..analyzers.correlation.correlation_analyzer import CorrelationAnalyzer
from ..analyzers.distribution.distribution_analyzer import DistributionAnalyzer

class AnalyzerFactory:
    _analyzers: Dict[str, Type[IAnalyzer]] = {
        'correlation': CorrelationAnalyzer,
        'distribution': DistributionAnalyzer,
        'performance': PerformanceAnalyzer,
        'social': SocialAnalyzer
    }

    @classmethod
    def create(cls, analyzer_type: str) -> IAnalyzer:
        if analyzer_type not in cls._analyzers:
            raise ValueError(f"Analyzer type '{analyzer_type}' not supported")
        return cls._analyzers[analyzer_type]()

    @classmethod
    def register(cls, analyzer_type: str, analyzer_class: Type[IAnalyzer]):
        cls._analyzers[analyzer_type] = analyzer_class
```

### 2. STRATEGY PATTERN

```python
# analyzers/correlation/correlation_analyzer.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd

class CorrelationStrategy(ABC):
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        pass

class PearsonStrategy(CorrelationStrategy):
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Implementação específica para Pearson
        pass

class SpearmanStrategy(CorrelationStrategy):
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Implementação específica para Spearman
        pass

class CorrelationAnalyzer:
    def __init__(self, strategy: CorrelationStrategy):
        self._strategy = strategy

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        return self._strategy.calculate(data)
```

### 3. BUILDER PATTERN

```python
# builders/result_builder.py
from typing import Dict, Any, Optional
from ..core.result import StatisticalResult

class ResultBuilder:
    def __init__(self):
        self._result = StatisticalResult()

    def with_data(self, data: Dict[str, Any]) -> 'ResultBuilder':
        self._result.data = data
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> 'ResultBuilder':
        self._result.metadata = metadata
        return self

    def with_interpretation(self, interpretation: str) -> 'ResultBuilder':
        self._result.interpretation = interpretation
        return self

    def with_status(self, status: str) -> 'ResultBuilder':
        self._result.status = status
        return self

    def build(self) -> StatisticalResult:
        return self._result
```

### 4. COMMAND PATTERN

```python
# core/commands.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd

class AnalysisCommand(ABC):
    @abstractmethod
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        pass

class CorrelationAnalysisCommand(AnalysisCommand):
    def __init__(self, variables: List[str], method: str = 'pearson'):
        self.variables = variables
        self.method = method

    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        analyzer = AnalyzerFactory.create('correlation')
        return analyzer.analyze(data, variables=self.variables, method=self.method)

class AnalysisInvoker:
    def __init__(self):
        self._commands: List[AnalysisCommand] = []

    def add_command(self, command: AnalysisCommand):
        self._commands.append(command)

    def execute_all(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        return [cmd.execute(data) for cmd in self._commands]
```

---

## IMPLEMENTAÇÃO DE INTERFACES

### 1. INTERFACE BASE PARA ANALISADORES

```python
# core/interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd

class IAnalyzer(ABC):
    @abstractmethod
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Executa análise nos dados fornecidos."""
        pass

    @abstractmethod
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """Valida se os dados de entrada são adequados para análise."""
        pass

    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """Retorna colunas obrigatórias para a análise."""
        pass

class IValidator(ABC):
    @abstractmethod
    def validate(self, data: pd.DataFrame, **kwargs) -> bool:
        pass

    @abstractmethod
    def get_errors(self, data: pd.DataFrame, **kwargs) -> List[str]:
        pass

class IResultBuilder(ABC):
    @abstractmethod
    def build_result(self, calculations: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def build_empty_result(self, reason: str) -> Dict[str, Any]:
        pass

class IInterpreter(ABC):
    @abstractmethod
    def interpret(self, result: Dict[str, Any]) -> str:
        pass
```

### 2. CLASSE BASE PARA ANALISADORES

```python
# core/base_analyzer.py
from typing import Dict, Any, List
import pandas as pd
from .interfaces import IAnalyzer, IValidator, IResultBuilder
from ..validators.data_validator import DataValidator

class BaseAnalyzer(IAnalyzer):
    def __init__(self, validator: IValidator = None, result_builder: IResultBuilder = None):
        self.validator = validator or DataValidator()
        self.result_builder = result_builder
        self._cache_enabled = True

    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        # Validar entrada
        if not self.validate_input(data, **kwargs):
            return self.result_builder.build_empty_result("Dados inválidos")

        # Executar análise específica
        try:
            calculations = self._perform_analysis(data, **kwargs)
            return self.result_builder.build_result(calculations)
        except Exception as e:
            return self.result_builder.build_empty_result(f"Erro na análise: {str(e)}")

    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        required_columns = self.get_required_columns()
        return self.validator.validate(data, required_columns=required_columns, **kwargs)

    @abstractmethod
    def _perform_analysis(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Implementação específica da análise."""
        pass

    @abstractmethod
    def get_required_columns(self) -> List[str]:
        """Colunas necessárias para a análise."""
        pass
```

---

## SISTEMA DE CONFIGURAÇÃO

### 1. CONFIGURAÇÕES CENTRALIZADAS

```python
# config/thresholds.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CorrelationThresholds:
    VERY_WEAK: float = 0.1
    WEAK: float = 0.3
    MODERATE: float = 0.5
    STRONG: float = 0.7
    VERY_STRONG: float = 0.9

@dataclass
class VariabilityThresholds:
    LOW: float = 15.0
    MODERATE: float = 25.0
    HIGH: float = 40.0

@dataclass
class SampleSizeThresholds:
    MIN_CORRELATION: int = 30
    MIN_DISTRIBUTION: int = 50
    MIN_COMPARISON: int = 100

@dataclass
class StatisticalThresholds:
    correlation: CorrelationThresholds = CorrelationThresholds()
    variability: VariabilityThresholds = VariabilityThresholds()
    sample_size: SampleSizeThresholds = SampleSizeThresholds()

    SIGNIFICANCE_LEVEL: float = 0.05
    CONFIDENCE_LEVEL: float = 0.95

# Instância global das configurações
THRESHOLDS = StatisticalThresholds()
```

### 2. CARREGAMENTO DE CONFIGURAÇÕES

```python
# config/settings.py
import json
from pathlib import Path
from typing import Dict, Any

class ConfigurationManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/statistical_config.json"
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Carrega configurações do arquivo JSON."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            self._config = self._get_default_config()
            self.save_config()

    def save_config(self):
        """Salva configurações no arquivo JSON."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor da configuração."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default

    def set(self, key: str, value: Any):
        """Define valor da configuração."""
        keys = key.split('.')
        config_ref = self._config
        for k in keys[:-1]:
            config_ref = config_ref.setdefault(k, {})
        config_ref[keys[-1]] = value

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "thresholds": {
                "correlation": {
                    "very_weak": 0.1,
                    "weak": 0.3,
                    "moderate": 0.5,
                    "strong": 0.7,
                    "very_strong": 0.9
                },
                "variability": {
                    "low": 15.0,
                    "moderate": 25.0,
                    "high": 40.0
                },
                "sample_size": {
                    "min_correlation": 30,
                    "min_distribution": 50,
                    "min_comparison": 100
                }
            },
            "cache": {
                "enabled": True,
                "ttl": 1800,
                "max_size": 1000
            },
            "performance": {
                "parallel_processing": True,
                "chunk_size": 10000,
                "memory_limit_mb": 512
            }
        }

# Instância global do gerenciador de configuração
CONFIG = ConfigurationManager()
```

---

## SISTEMA DE CACHE INTELIGENTE

```python
# utils/cache_manager.py
import hashlib
import pickle
from typing import Any, Dict, Optional, Callable
from functools import wraps
import time

class CacheManager:
    def __init__(self, ttl: int = 1800, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl
        self._max_size = max_size

    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Gera chave única para cache baseada nos parâmetros."""
        key_data = f"{func_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache se válido."""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry['timestamp'] < self._ttl:
                entry['hits'] += 1
                return entry['value']
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """Armazena valor no cache."""
        # Remover entradas antigas se necessário
        if len(self._cache) >= self._max_size:
            self._cleanup_cache()

        self._cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'hits': 0
        }

    def _cleanup_cache(self):
        """Remove entradas mais antigas e menos usadas."""
        # Ordenar por hits e timestamp
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: (x[1]['hits'], x[1]['timestamp'])
        )

        # Remover 25% das entradas menos utilizadas
        remove_count = max(1, len(sorted_entries) // 4)
        for i in range(remove_count):
            key = sorted_entries[i][0]
            del self._cache[key]

    def clear(self):
        """Limpa todo o cache."""
        self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_hits = sum(entry['hits'] for entry in self._cache.values())
        return {
            'entries': len(self._cache),
            'total_hits': total_hits,
            'avg_hits': total_hits / len(self._cache) if self._cache else 0,
            'memory_usage_mb': len(pickle.dumps(self._cache)) / (1024 * 1024)
        }

# Instância global do gerenciador de cache
CACHE = CacheManager()

def cached(ttl: int = None):
    """Decorator para cache automático de funções."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = CACHE._generate_key(func.__name__, *args, **kwargs)

            # Tentar obter do cache
            cached_result = CACHE.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            CACHE.set(cache_key, result)
            return result

        return wrapper
    return decorator
```

---

## EXEMPLO DE IMPLEMENTAÇÃO COMPLETA

### 1. ANALISADOR DE CORRELAÇÃO REFATORADO

```python
# analyzers/correlation/correlation_analyzer.py
from typing import Dict, Any, List
import pandas as pd
from scipy import stats
from ...core.base_analyzer import BaseAnalyzer
from ...validators.correlation_validator import CorrelationValidator
from ...builders.correlation_result_builder import CorrelationResultBuilder
from ...interpreters.correlation_interpreter import CorrelationInterpreter
from ...utils.cache_manager import cached

class CorrelationAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(
            validator=CorrelationValidator(),
            result_builder=CorrelationResultBuilder()
        )
        self.interpreter = CorrelationInterpreter()

    def get_required_columns(self) -> List[str]:
        return ['variable_x', 'variable_y']  # Serão definidas dinamicamente

    @cached(ttl=1800)
    def _perform_analysis(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        var_x = kwargs.get('variable_x')
        var_y = kwargs.get('variable_y')
        method = kwargs.get('method', 'pearson')

        if method == 'pearson':
            return self._calculate_pearson(data, var_x, var_y)
        elif method == 'spearman':
            return self._calculate_spearman(data, var_x, var_y)
        elif method == 'chi_square':
            return self._calculate_chi_square(data, var_x, var_y)
        else:
            raise ValueError(f"Método não suportado: {method}")

    def _calculate_pearson(self, data: pd.DataFrame, var_x: str, var_y: str) -> Dict[str, Any]:
        correlation, p_value = stats.pearsonr(data[var_x], data[var_y])

        return {
            'correlation_coefficient': correlation,
            'p_value': p_value,
            'method': 'pearson',
            'sample_size': len(data),
            'interpretation': self.interpreter.interpret_correlation(correlation),
            'significance': p_value < 0.05
        }

    def _calculate_spearman(self, data: pd.DataFrame, var_x: str, var_y: str) -> Dict[str, Any]:
        correlation, p_value = stats.spearmanr(data[var_x], data[var_y])

        return {
            'correlation_coefficient': correlation,
            'p_value': p_value,
            'method': 'spearman',
            'sample_size': len(data),
            'interpretation': self.interpreter.interpret_correlation(correlation),
            'significance': p_value < 0.05
        }

    def _calculate_chi_square(self, data: pd.DataFrame, var_x: str, var_y: str) -> Dict[str, Any]:
        contingency_table = pd.crosstab(data[var_x], data[var_y])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        # Calcular V de Cramer
        n = contingency_table.sum().sum()
        cramers_v = np.sqrt(chi2 / (n * min(contingency_table.shape) - 1))

        return {
            'chi_square': chi2,
            'p_value': p_value,
            'degrees_freedom': dof,
            'cramers_v': cramers_v,
            'method': 'chi_square',
            'sample_size': n,
            'contingency_table': contingency_table,
            'interpretation': self.interpreter.interpret_cramers_v(cramers_v),
            'significance': p_value < 0.05
        }
```

### 2. VALIDADOR ESPECÍFICO

```python
# validators/correlation_validator.py
from typing import List
import pandas as pd
from ..core.interfaces import IValidator

class CorrelationValidator(IValidator):
    def __init__(self, min_samples: int = 30):
        self.min_samples = min_samples

    def validate(self, data: pd.DataFrame, **kwargs) -> bool:
        errors = self.get_errors(data, **kwargs)
        return len(errors) == 0

    def get_errors(self, data: pd.DataFrame, **kwargs) -> List[str]:
        errors = []

        # Validações básicas
        if data is None or data.empty:
            errors.append("DataFrame está vazio ou é None")
            return errors

        # Validar colunas requeridas
        var_x = kwargs.get('variable_x')
        var_y = kwargs.get('variable_y')

        if not var_x or not var_y:
            errors.append("Variáveis X e Y devem ser especificadas")
            return errors

        if var_x not in data.columns:
            errors.append(f"Variável X '{var_x}' não encontrada no DataFrame")

        if var_y not in data.columns:
            errors.append(f"Variável Y '{var_y}' não encontrada no DataFrame")

        if errors:  # Se já temos erros de coluna, não continuar
            return errors

        # Validar tamanho da amostra
        valid_data = data[[var_x, var_y]].dropna()
        if len(valid_data) < self.min_samples:
            errors.append(f"Amostras insuficientes: {len(valid_data)} < {self.min_samples}")

        # Validar variabilidade
        if data[var_x].nunique() < 2:
            errors.append(f"Variável X '{var_x}' não possui variabilidade suficiente")

        if data[var_y].nunique() < 2:
            errors.append(f"Variável Y '{var_y}' não possui variabilidade suficiente")

        return errors
```

---

## CHECKLIST DE QUALIDADE

### ✅ SOLID PRINCIPLES

- [ ] Single Responsibility: Uma classe, uma responsabilidade
- [ ] Open/Closed: Extensível sem modificação
- [ ] Liskov Substitution: Subclasses substituíveis
- [ ] Interface Segregation: Interfaces específicas
- [ ] Dependency Inversion: Dependências abstratas

### ✅ CLEAN CODE

- [ ] Funções pequenas (< 20 linhas)
- [ ] Nomes descritivos
- [ ] Sem magic numbers
- [ ] Tratamento adequado de erros
- [ ] Comentários apenas quando necessário

### ✅ ARCHITECTURE

- [ ] Baixo acoplamento
- [ ] Alta coesão
- [ ] Separação de responsabilidades
- [ ] Padrões de design adequados
- [ ] Testabilidade

### ✅ PERFORMANCE

- [ ] Cache implementado
- [ ] Operações otimizadas
- [ ] Memory management adequado
- [ ] Paralelização onde possível

---

_Guia de implementação v1.0 - 2025-01-14_
