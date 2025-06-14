"""
Pacote de preparação de dados do ENEM Dashboard.

Este pacote contém toda a lógica de preparação e processamento de dados
para as diferentes análises do dashboard do ENEM. Foi refatorado seguindo
princípios SOLID e Clean Code para melhor manutenibilidade e performance.

Estrutura:
- base: Classes base e interfaces comuns
- common_utils: Utilitários compartilhados entre módulos
- geral: Processadores para análises gerais
- aspectos_sociais: Processadores para aspectos socioeconômicos
- desempenho: Processadores para análises de desempenho

Classes principais:
- BaseDataProcessor: Classe base para todos os processadores
- CacheableProcessor: Processador com cache automático
- StateGroupedProcessor: Processador para análises por estado
- MappingManager: Gerenciador de mapeamentos
- StatisticalCalculator: Calculadora de estatísticas
- DataAggregator: Agregador de dados
- DataFilter: Filtro de dados
"""

# Importar classes base e utilitários
from .base import (
    BaseDataProcessor,
    CacheableProcessor, 
    StateGroupedProcessor,
    ProcessorFactory
)

from .common_utils import (
    MappingManager,
    StatisticalCalculator,
    DataAggregator,
    DataFilter
)

# Importar gerenciadores de cada domínio
from .geral.data_manager import GeralDataManager
from .aspectos_sociais.data_manager import SocialDataManager  
from .desempenho.data_manager import PerformanceDataManager

# Importar funções de compatibilidade principais - Geral
from .geral.data_manager import (
    preparar_dados_histograma,
    preparar_dados_grafico_faltas,
    preparar_dados_metricas_principais,
    preparar_dados_media_geral_estados,
    preparar_dados_evasao,
    preparar_dados_comparativo_areas
)

# Importar funções de compatibilidade - Aspectos Sociais
from .aspectos_sociais.data_manager import (
    prepare_social_data,
    preparar_dados_aspecto_social,
    preparar_dados_comparacao_social,
    obter_estatisticas_aspecto_social,
    preparar_dados_correlacao
)

# Importar funções de compatibilidade - Desempenho
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

# Importar validação de dados (mantido para compatibilidade)
from .validacao_dados import (
    validar_completude_dados,
    verificar_outliers,
    validar_distribuicao_dados
)

# Importações legadas mantidas para compatibilidade (DEPRECATED)
# Estas funções ainda estão disponíveis mas recomenda-se usar as novas APIs
try:
    from .geral.prepara_dados_geral import (
        preparar_dados_grafico_faltas,
        preparar_dados_media_geral_estados,
        preparar_dados_comparativo_areas,
        preparar_dados_evasao
    )
except ImportError:
    # Fallback caso os arquivos antigos não existam
    pass

# Comentado temporariamente durante refatoração
# Importações diretas do arquivo original para manter compatibilidade temporária
try:
    from .aspectos_sociais.prepara_dados_aspectos_sociais import (
        preparar_dados_distribuicao,
        contar_candidatos_por_categoria,
        ordenar_categorias,
        preparar_dados_grafico_aspectos_por_estado,
        preparar_dados_heatmap,
        preparar_dados_barras_empilhadas,
        preparar_dados_sankey
    )
except ImportError:
    # Fallback caso haja algum problema
    pass

__all__ = [
    # Classes base
    'BaseDataProcessor',
    'CacheableProcessor',
    'StateGroupedProcessor', 
    'ProcessorFactory',
    
    # Utilitários comuns
    'MappingManager',
    'StatisticalCalculator',
    'DataAggregator',
    'DataFilter',
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
    'preparar_dados_aspecto_social',    'preparar_dados_comparacao_social',
    'obter_estatisticas_aspecto_social',
    'preparar_dados_correlacao',    'preparar_dados_distribuicao',
    'contar_candidatos_por_categoria', 
    'ordenar_categorias',
    'preparar_dados_grafico_aspectos_por_estado',
    'preparar_dados_heatmap',
    'preparar_dados_barras_empilhadas',
    'preparar_dados_sankey',
    
    # Funções de compatibilidade - Desempenho
    'prepare_performance_data',
    'preparar_dados_comparativo',
    'preparar_dados_grafico_linha',
    'preparar_dados_desempenho_geral',
    'filtrar_dados_scatter',
    'preparar_dados_grafico_linha_desempenho',
    'obter_ordem_categorias',
    'calcular_estatisticas_desempenho',
    
    # Validação de dados
    'validar_completude_dados',
    'verificar_outliers',
    'validar_distribuicao_dados'
]