# PROMPT PARA REFATORAÇÃO COMPLETA DO MÓDULO DE ESTATÍSTICAS

## CONTEXTO DO PROJETO

Preciso de uma **refatoração completa e profissional** do módulo de estatísticas de um dashboard Streamlit para análise de dados do ENEM. O módulo atual está em estado crítico com violações graves dos princípios SOLID e Clean Code, afetando manutenibilidade, escalabilidade e produtividade da equipe.

## ESTADO ATUAL DO PROBLEMA

### Estrutura Atual Problemática:
```
utils/estatisticas/
├── geral/analise_geral.py (1.194 linhas - CRÍTICO)
├── aspectos_sociais/analise_aspectos_sociais.py (1.019 linhas - CRÍTICO)
├── desempenho/analise_desempenho.py (complexo - CRÍTICO)
├── validators.py (319 linhas - moderado)
├── result_builders.py (342 linhas - moderado)
├── interpreters.py (392 linhas - moderado)
├── interfaces.py (adequado)
├── calculators.py (adequado)
└── outros arquivos menores
```

### Principais Problemas Identificados:

1. **SOLID Violations**:
   - SRP: Arquivos gigantes com múltiplas responsabilidades
   - OCP: Estruturas rígidas com múltiplos if/elif
   - LSP: Hierarquias mal definidas
   - ISP: Interfaces grandes com métodos não relacionados
   - DIP: Acoplamento direto a implementações concretas

2. **Clean Code Violations**:
   - Funções massivas (100-150+ linhas)
   - Magic numbers espalhados (0.05, 0.1, 1000, etc.)
   - Duplicação excessiva de código
   - Nomenclatura inadequada (df, resultado, temp)
   - Tratamento genérico de exceções

3. **Arquitetura Problemática**:
   - Alta complexidade ciclomática (>20 em várias funções)
   - Baixa coesão e alto acoplamento
   - Falta de padrões de design
   - Ausência de abstrações adequadas

## OBJETIVO DA REFATORAÇÃO

Transformar o módulo em uma **solução de classe empresarial** que seja:
- ✅ **Altamente mantível**: Mudanças fáceis e seguras
- ✅ **Escalável**: Suporte a novos tipos de análise sem reescrita
- ✅ **Testável**: 100% de cobertura de testes possível
- ✅ **Performante**: Cache inteligente e otimizações
- ✅ **Documentada**: Código auto-explicativo com documentação técnica

## ARQUITETURA ALVO DESEJADA

### Nova Estrutura Proposta:
```
utils/estatisticas/
├── core/
│   ├── interfaces.py              # Contratos e abstrações
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

## PADRÕES DE DESIGN OBRIGATÓRIOS

### 1. Factory Pattern
- Para criação de analisadores específicos
- Registro dinâmico de novos tipos
- Configuração centralizada

### 2. Strategy Pattern
- Para diferentes algoritmos de correlação (Pearson, Spearman, Chi-quadrado)
- Para diferentes métodos de interpretação
- Para diferentes estratégias de cache

### 3. Builder Pattern
- Para construção de resultados complexos
- Para metadata estruturada
- Para interpretações contextuais

### 4. Command Pattern
- Para operações de análise compostas
- Para pipeline de processamento
- Para undo/redo se necessário

### 5. Observer Pattern (opcional)
- Para notificações de progresso
- Para logging estruturado
- Para métricas de performance

## REQUISITOS TÉCNICOS ESPECÍFICOS

### 1. Interfaces Obrigatórias:
```python
class IAnalyzer(ABC):
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool
    def get_required_columns(self) -> List[str]

class IValidator(ABC):
    def validate(self, data: pd.DataFrame, **kwargs) -> bool
    def get_errors(self, data: pd.DataFrame, **kwargs) -> List[str]

class IResultBuilder(ABC):
    def build_result(self, calculations: Dict[str, Any]) -> Dict[str, Any]
    def build_empty_result(self, reason: str) -> Dict[str, Any]
```

### 2. Sistema de Configuração:
- Arquivo JSON para thresholds configuráveis
- Dataclasses para tipagem forte
- Carregamento dinâmico de configurações
- Validação de configurações

### 3. Cache Inteligente:
- Cache baseado em hash dos parâmetros
- TTL configurável por tipo de análise
- Cleanup automático de entradas antigas
- Métricas de hit/miss ratio

### 4. Tratamento de Erros:
- Exceções específicas por tipo de erro
- Logging estruturado
- Fallback gracioso para casos de erro
- Validação em múltiplas camadas

## FUNCIONALIDADES REQUERIDAS

### 1. Análises de Correlação:
- Pearson, Spearman, Kendall
- Chi-quadrado para categóricas
- Mutual Information
- V de Cramer
- Interpretação automática de força

### 2. Análises de Distribuição:
- Estatísticas descritivas completas
- Índices de concentração (Gini, Entropy)
- Classificação automática de variabilidade
- Detecção de outliers

### 3. Análises de Desempenho:
- Comparação entre estados/regiões
- Ranking automático
- Gaps de performance
- Tendências temporais

### 4. Análises Sociais:
- Cruzamento de variáveis demográficas
- Análise de disparidades
- Segmentação automática
- Correlações sociodemográficas

## REQUISITOS DE QUALIDADE

### 1. Métricas de Código:
- **Complexidade ciclomática**: máx 10 por função
- **Linhas por função**: máx 20 linhas
- **Linhas por arquivo**: máx 300 linhas
- **Cobertura de testes**: mín 90%

### 2. Performance:
- **Cache hit ratio**: mín 70%
- **Tempo de resposta**: máx 2s para análises complexas
- **Memory usage**: máx 512MB por análise
- **Paralelização**: para operações independentes

### 3. Manutenibilidade:
- **Documentação**: docstrings completas
- **Type hints**: 100% das assinaturas
- **Testes unitários**: para cada componente
- **Testes de integração**: para workflows completos

## EXEMPLOS DE USO ESPERADOS

### Uso Simples:
```python
# Análise de correlação
analyzer = AnalyzerFactory.create('correlation')
result = analyzer.analyze(
    data=df, 
    variable_x='renda_familiar', 
    variable_y='nota_matematica',
    method='pearson'
)

# Análise de distribuição
analyzer = AnalyzerFactory.create('distribution')
result = analyzer.analyze(
    data=df,
    variable='tipo_escola',
    include_concentration=True
)
```

### Uso Avançado:
```python
# Pipeline de análises
pipeline = AnalysisPipeline()
pipeline.add_analysis('correlation', var_x='renda', var_y='nota')
pipeline.add_analysis('distribution', variable='regiao')
pipeline.add_analysis('performance', group_by='estado')

results = pipeline.execute(df)
```

### Configuração Flexível:
```python
# Configuração de thresholds
config = ConfigurationManager()
config.set('thresholds.correlation.strong', 0.8)
config.set('cache.ttl', 3600)

# Uso com configuração personalizada
analyzer = CorrelationAnalyzer(config=config)
```

## TESTES REQUERIDOS

### 1. Testes Unitários:
- Cada classe/função isoladamente
- Mocks para dependências externas
- Coverage mínimo de 90%
- Casos edge testados

### 2. Testes de Integração:
- Workflows completos end-to-end
- Integração entre componentes
- Performance sob carga
- Validação de resultados

### 3. Testes de Regressão:
- Comparação com resultados atuais
- Validação de compatibilidade
- Testes de migração
- Benchmarks de performance

## DOCUMENTAÇÃO NECESSÁRIA

### 1. Documentação Técnica:
- Arquitetura detalhada
- Diagramas UML/C4
- Guias de desenvolvimento
- API reference completa

### 2. Documentação de Usuário:
- Guias de uso
- Exemplos práticos
- Troubleshooting
- FAQ técnico

### 3. Documentação de Migração:
- Plano de migração step-by-step
- Compatibilidade backwards
- Breaking changes documentadas
- Rollback procedures

## CRITÉRIOS DE ACEITE

### ✅ Funcionalidade:
- [ ] Todas as análises atuais funcionando
- [ ] Novos recursos implementados
- [ ] Performance melhorada ou mantida
- [ ] Compatibilidade com dados existentes

### ✅ Qualidade:
- [ ] Complexidade ciclomática < 10
- [ ] Cobertura de testes > 90%
- [ ] Sem code smells críticos
- [ ] Documentação completa

### ✅ Arquitetura:
- [ ] SOLID principles seguidos
- [ ] Design patterns implementados
- [ ] Baixo acoplamento
- [ ] Alta coesão

### ✅ Manutenibilidade:
- [ ] Fácil adicionar novos tipos de análise
- [ ] Configuração flexível
- [ ] Logs e monitoramento
- [ ] Debugging facilitado

## RECURSOS DISPONÍVEIS

### Código Base Atual:
- Localização: `c:\Users\user\Documents\Faculdade\Streamlit\utils\estatisticas\`
- Arquivos de referência já analisados
- Exemplo de boa prática: `analise_desempenho_clean.py`
- Relatórios de análise detalhados já gerados

### Documentos de Apoio:
- `RELATORIO_FINAL_QUALIDADE_MODULO_ESTATISTICAS.md`
- `GUIA_IMPLEMENTACAO_REFATORACAO.md`
- `ANALISE_QUALIDADE_CODIGO_CRITICA.md`

### Tecnologias Utilizadas:
- Python 3.8+
- Pandas, NumPy, SciPy
- Streamlit
- Cache utilities existentes

## PERGUNTA FINAL

**Você pode implementar essa refatoração completa seguindo rigorosamente todos os requisitos acima?** 

Preciso de uma solução que transforme este módulo problemático em um exemplo de excelência em engenharia de software, seguindo as melhores práticas da indústria e garantindo que nunca mais tenhamos problemas de manutenibilidade, escalabilidade ou qualidade de código.

A refatoração deve ser **profissional, completa e sustentável**, servindo como referência para outros módulos do projeto.
