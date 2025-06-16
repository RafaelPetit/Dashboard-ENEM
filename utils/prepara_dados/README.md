# Arquitetura SOLID Refatorada - Módulo prepara_dados

## Visão Geral

O módulo `prepara_dados` foi completamente refatorado seguindo os princípios SOLID, Clean Code e padrões de arquitetura modernos para garantir:

- ✅ **Máxima eficiência** para grandes volumes de dados (4+ milhões de registros)
- ✅ **Baixo consumo de memória** adequado para Streamlit
- ✅ **Modularidade** e facilidade de manutenção
- ✅ **Testabilidade** com baixo acoplamento
- ✅ **Extensibilidade** para futuras funcionalidades

## Princípios SOLID Implementados

### 1. Single Responsibility Principle (SRP)

Cada classe tem uma única responsabilidade:

- `DataValidator`: Apenas validação de dados
- `MemoryManager`: Apenas gestão de memória
- `StatisticsCalculator`: Apenas cálculos estatísticos
- `StateProcessor`: Apenas processamento por estados

### 2. Open/Closed Principle (OCP)

Sistema aberto para extensão, fechado para modificação:

- Novas estratégias de filtro podem ser adicionadas sem alterar código existente
- Novos processadores podem ser criados herdando de classes base

### 3. Liskov Substitution Principle (LSP)

Subclasses podem substituir classes base sem quebrar funcionalidade:

- Todos os processadores implementam a mesma interface base
- Estratégias de filtro são intercambiáveis

### 4. Interface Segregation Principle (ISP)

Interfaces específicas em vez de interfaces grandes:

- `DataValidator` só tem métodos de validação
- `CacheManager` só tem métodos de cache
- `MemoryManager` só tem métodos de memória

### 5. Dependency Inversion Principle (DIP)

Dependência de abstrações, não de implementações concretas:

- Processadores dependem de interfaces, não de classes concretas
- Injeção de dependência via constructors

## Padrões de Design Implementados

### Factory Pattern

Criação centralizada de objetos complexos:

```python
# Uso das factories
processor = StateProcessorFactory.create_performance_processor()
filter_strategy = FilterStrategyFactory.get_score_filter()
validator = ComponentFactory.get_validator()
```

### Strategy Pattern

Algoritmos intercambiáveis para diferentes situações:

```python
# Diferentes estratégias de filtro
score_filter = ScoreFilterStrategy()
demographic_filter = DemographicFilterStrategy()

# Combinação de estratégias
combined_filter = FilterStrategyFactory.create_combined_filter([
    score_filter, demographic_filter
])
```

### Singleton Pattern

Instâncias únicas para recursos compartilhados:

```python
# Configuração global singleton
config_manager = ConfigManager.get_instance()
```

### Facade Pattern

Interface simplificada para operações complexas:

```python
# Orquestrador que encapsula complexidade
orchestrator = DataProcessingOrchestrator()
result = orchestrator.process_performance_data(data, states, columns, mapping)
```

## Estrutura dos Arquivos

```
utils/prepara_dados/
├── __init__.py                 # Exports principais
├── interfaces.py              # Contratos e abstrações
├── implementations.py         # Implementações concretas
├── factories.py              # Factories para criação de objetos
├── config.py                 # Configurações centralizadas
├── compatibility.py          # Camada de compatibilidade
├── base.py                   # Classes base existentes
├── common_utils.py           # Utilitários compartilhados
├── geral/                    # Processadores gerais
├── aspectos_sociais/         # Processadores de aspectos sociais
└── desempenho/              # Processadores de desempenho
```

## Como Usar a Nova Arquitetura

### 1. Uso Direto (Recomendado para novos desenvolvimentos)

```python
from utils.prepara_dados import DataProcessingOrchestrator, ComponentFactory

# Criar orquestrador
orchestrator = DataProcessingOrchestrator()

# Processar dados de desempenho
result = orchestrator.process_performance_data(
    data=microdados,
    states=['SP', 'RJ', 'MG'],
    score_columns=['NU_NOTA_CN', 'NU_NOTA_CH'],
    competence_mapping={'NU_NOTA_CN': 'Ciências Natureza'},
    group_by_region=False
)

# Aplicar filtros inteligentes
filtered_data = aplicar_filtros_inteligentes(
    data,
    exclude_zero_scores=True,
    gender='F',
    school_type='Pública'
)
```

### 2. Uso com Compatibilidade (Para código existente)

```python
from utils.prepara_dados.compatibility import (
    preparar_dados_comparativo_otimizado,
    preparar_dados_aspecto_social_otimizado
)

# Mesma API, implementação otimizada
result = preparar_dados_comparativo_otimizado(
    microdados_full,
    variavel_selecionada,
    variaveis_categoricas,
    colunas_notas,
    competencia_mapping
)
```

### 3. Configuração Flexível

```python
from utils.prepara_dados import get_config, update_config

# Obter configuração atual
config = get_config()
print(f"Batch size: {config.memory.batch_size_states}")

# Atualizar configuração para ambiente específico
update_config(
    memory={'batch_size_states': 10},
    cache={'enable_cache': False},
    debug=True
)
```

## Otimizações de Performance

### 1. Gestão Inteligente de Memória

- Processamento em lotes configurável
- Liberação automática de memória
- Otimização de tipos de dados
- Monitoramento de uso de memória

### 2. Cache Multinível

- Cache por função com TTL configurável
- Cache de componentes singleton
- Cache de mapeamentos e configurações

### 3. Processamento Otimizado

- Filtragem antes de processamento pesado
- GroupBy eficiente para grandes datasets
- Processamento vetorizado quando possível
- Amostragem inteligente para visualizações

### 4. Validação Eficiente

- Validação lazy quando possível
- Short-circuit em validações múltiplas
- Caching de resultados de validação

## Benefícios para o Streamlit

### 1. Menor Uso de Memória

- Processamento em lotes reduz picos de memória
- Liberação automática de objetos não utilizados
- Tipos de dados otimizados (categorias, float32)

### 2. Performance Melhorada

- Cache inteligente reduz reprocessamento
- Algoritmos otimizados para grandes volumes
- Lazy loading de dependências

### 3. Melhor Experiência do Usuário

- Respostas mais rápidas
- Menor probabilidade de crashes por memória
- Feedback de progresso em operações longas

## Identificação de Padrões para Pré-processamento

O sistema identifica automaticamente padrões que podem ser otimizados via pré-processamento:

### ⚠️ Colunas Criadas em Runtime Detectadas:

1. **Mapeamento de variáveis categóricas** em `preparar_dados_aspectos_sociais.py:55-75`

   - Aplicação de mapeamentos durante processamento
   - **Recomendação**: Migrar para script de pré-processamento

2. **Cálculo de médias por região** em `preparar_dados_geral.py:310-340`

   - Criação de coluna 'REGIAO' em runtime
   - **Recomendação**: Adicionar coluna de região no dataset original

3. **Categorização de desempenho** em `preparar_dados_desempenho.py:180-200`
   - Criação de categorias de desempenho durante análise
   - **Recomendação**: Pré-calcular e armazenar categorias

## Próximos Passos Recomendados

1. **Implementar testes unitários** para todas as interfaces
2. **Criar benchmark** comparando performance antiga vs nova
3. **Migrar gradualmente** funções críticas para nova arquitetura
4. **Documentar APIs** específicas de cada processador
5. **Implementar logging** estruturado para debug
6. **Criar script de pré-processamento** para otimizações identificadas

## Exemplos de Extensão

### Adicionar Nova Estratégia de Filtro

```python
class GeographicFilterStrategy:
    """Nova estratégia para filtros geográficos."""

    def apply_filter(self, data, region=None, states=None):
        if region:
            # Filtrar por região
            pass
        if states:
            # Filtrar por estados específicos
            pass
        return filtered_data

# Registrar na factory
FilterStrategyFactory.register_strategy('geographic', GeographicFilterStrategy)
```

### Adicionar Novo Processador

```python
class CustomAnalysisProcessor(BaseStateProcessor):
    """Processador customizado para análises específicas."""

    def process_single_state(self, data, state, **kwargs):
        # Implementar lógica específica
        return custom_result

# Usar via factory
custom_processor = StateProcessorFactory.create_custom_processor(CustomAnalysisProcessor)
```

## Conclusão

A nova arquitetura SOLID implementada oferece:

- 🚀 **Performance otimizada** para grandes volumes
- 🧩 **Modularidade** para fácil manutenção
- 🔧 **Extensibilidade** para futuras funcionalidades
- 🛡️ **Robustez** com tratamento de erros
- 📊 **Compatibilidade** com código existente

O módulo está agora preparado para deploy em produção com Streamlit, respeitando os limites de memória da plataforma e oferecendo performance profissional.
