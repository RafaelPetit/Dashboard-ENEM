"""
Pacote de preparação de dados do ENEM Dashboard - Versão Refatorada com SOLID.

Este pacote foi completamente refatorado seguindo princípios SOLID, Clean Code 
e padrões de arquitetura modernos para garantir máxima eficiência com grandes 
volumes de dados (4+ milhões de registros) e adequação aos limites de memória do Streamlit.

ARQUITETURA IMPLEMENTADA:
- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP) 
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)
- Factory Pattern para criação de objetos
- Strategy Pattern para algoritmos intercambiáveis
- Singleton Pattern para configurações globais
- Facade Pattern para interfaces simplificadas

USO RECOMENDADO:
- Para NOVOS desenvolvimentos: use funções *_otimizado
- Para código EXISTENTE: mantenha funções de compatibilidade
- Para operações COMPLEXAS: use DataProcessingOrchestrator
"""

# ========== CLASSES BASE ==========
from .base import (
    BaseDataProcessor,
    CacheableProcessor, 
    StateGroupedProcessor,
    ProcessorFactory
)

# ========== INTERFACES SOLID ==========
from .interfaces import (
    DataValidator,
    MemoryManager,
    StatisticsCalculator,
    StateProcessor,
    RegionAggregator,
    DataFormatter,
    DataFilterStrategy,
    ProcessingOrchestrator
)

# ========== IMPLEMENTAÇÕES ==========
from .implementations import (
    DefaultDataValidator,
    DefaultMemoryManager,
    SafeStatisticsCalculator,
    DefaultRegionAggregator,
    VisualizationDataFormatter,
    ScoreFilterStrategy,
    DemographicFilterStrategy
)

# ========== FACTORIES ==========
from .factories import (
    ComponentFactory,
    FilterStrategyFactory,
    StateProcessorFactory,
    DataProcessingOrchestrator
)

# ========== CONFIGURAÇÃO ==========
from .config import (
    get_config,
    get_legacy_config,
    update_config
)

# ========== UTILITÁRIOS ==========
from .common_utils import (
    MappingManager,
    StatisticalCalculator,
    DataAggregator,
    DataFilter,
    corrigir_tipos_notas_enem,
    preparar_dados_para_calculo
)

# ========== GERENCIADORES DE DOMÍNIO ==========
from .geral.data_manager import GeralDataManager
from .aspectos_sociais.data_manager import SocialDataManager  
from .desempenho.data_manager import PerformanceDataManager

# ========== FUNÇÕES DE COMPATIBILIDADE - GERAL ==========
from .geral.data_manager import (
    preparar_dados_histograma,
    preparar_dados_grafico_faltas,
    preparar_dados_metricas_principais,
    preparar_dados_media_geral_estados,
    preparar_dados_evasao,
    preparar_dados_comparativo_areas
)

# ========== FUNÇÕES DE COMPATIBILIDADE - ASPECTOS SOCIAIS ==========
from .aspectos_sociais.data_manager import (
    prepare_social_data,
    preparar_dados_aspecto_social,
    preparar_dados_comparacao_social,
    obter_estatisticas_aspecto_social
)

# Funções adicionais de aspectos sociais
from .aspectos_sociais.prepara_dados_aspectos_sociais import (
    preparar_dados_distribuicao,
    contar_candidatos_por_categoria,
    ordenar_categorias,
    preparar_dados_grafico_aspectos_por_estado,
    preparar_dados_heatmap
)

# ========== FUNÇÕES DE COMPATIBILIDADE - DESEMPENHO ==========
from .desempenho.data_manager import (
    prepare_performance_data,
    preparar_dados_comparativo,
    preparar_dados_grafico_linha,
    preparar_dados_desempenho_geral,
    filtrar_dados_scatter,
    preparar_dados_grafico_linha_desempenho,
    obter_ordem_categorias,
    calcular_estatisticas_desempenho
)

# ========== VALIDAÇÃO DE DADOS ==========
from .validacao_dados import (
    validar_completude_dados,
    verificar_outliers,
    validar_distribuicao_dados
)

# ========== FUNÇÕES OTIMIZADAS (RECOMENDADAS) ==========
from .compatibility import (
    preparar_dados_comparativo_otimizado,
    preparar_dados_aspecto_social_otimizado,
    preparar_dados_desempenho_estados_otimizado,
    aplicar_filtros_inteligentes,
    exemplo_uso_nova_arquitetura
)

# ========== EXPORTS PÚBLICOS ==========
__all__ = [
    # Classes base
    'BaseDataProcessor',
    'CacheableProcessor', 
    'StateGroupedProcessor',
    'ProcessorFactory',
    
    # Interfaces SOLID
    'DataValidator',
    'MemoryManager',
    'StatisticsCalculator',
    'StateProcessor',
    'RegionAggregator',
    'DataFormatter',
    'DataFilterStrategy',
    'ProcessingOrchestrator',
    
    # Implementações
    'DefaultDataValidator',
    'DefaultMemoryManager',
    'SafeStatisticsCalculator',
    'DefaultRegionAggregator',
    'VisualizationDataFormatter',
    'ScoreFilterStrategy',
    'DemographicFilterStrategy',
    
    # Factories
    'ComponentFactory',
    'FilterStrategyFactory',
    'StateProcessorFactory',
    'DataProcessingOrchestrator',
    
    # Configuração
    'get_config',
    'get_legacy_config',
    'update_config',
    
    # Utilitários
    'MappingManager',
    'StatisticalCalculator',
    'DataAggregator',
    'DataFilter',
    'corrigir_tipos_notas_enem',
    'preparar_dados_para_calculo',
    
    # Gerenciadores de domínio
    'GeralDataManager',
    'SocialDataManager',
    'PerformanceDataManager',
    
    # Funções de compatibilidade - Geral
    'preparar_dados_histograma',
    'preparar_dados_grafico_faltas',
    'preparar_dados_metricas_principais',
    'preparar_dados_media_geral_estados',
    'preparar_dados_evasao',
    'preparar_dados_comparativo_areas',
      # Funções de compatibilidade - Aspectos Sociais
    'prepare_social_data',
    'preparar_dados_aspecto_social',
    'preparar_dados_comparacao_social',
    'obter_estatisticas_aspecto_social',    'preparar_dados_distribuicao',
    'contar_candidatos_por_categoria',
    'ordenar_categorias',
    'preparar_dados_grafico_aspectos_por_estado',
    'preparar_dados_heatmap',
    
    # Funções de compatibilidade - Desempenho
    'prepare_performance_data',
    'preparar_dados_comparativo',
    'preparar_dados_grafico_linha',
    'preparar_dados_desempenho_geral',
    'filtrar_dados_scatter',
    'preparar_dados_grafico_linha_desempenho',
    'obter_ordem_categorias',
    'calcular_estatisticas_desempenho',
    
    # Funções otimizadas (RECOMENDADAS para novos desenvolvimentos)
    'preparar_dados_comparativo_otimizado',
    'preparar_dados_aspecto_social_otimizado', 
    'preparar_dados_desempenho_estados_otimizado',
    'aplicar_filtros_inteligentes',
    'exemplo_uso_nova_arquitetura',
    
    # Validação de dados
    'validar_completude_dados',
    'verificar_outliers',
    'validar_distribuicao_dados'
]

# ========== IMPORTAÇÕES ADICIONAIS PARA COMPATIBILIDADE ==========
try:
    from .aspectos_sociais.prepara_dados_aspectos_sociais import preparar_dados_correlacao
    __all__.append('preparar_dados_correlacao')
except ImportError:
    pass

# ========== MENSAGEM INFORMATIVA ==========
print("✅ Módulo prepara_dados refatorado com arquitetura SOLID carregado!")
print("🚀 Para novos desenvolvimentos, use as funções *_otimizado")
print("🔧 Para código existente, mantenha as funções de compatibilidade")
print("📚 Leia o README.md para documentação completa da nova arquitetura")