"""
Módulo para preparação de dados de aspectos sociais do ENEM.

Este subpacote contém classes especializadas para processamento e análise
de aspectos sociais dos candidatos, incluindo escolaridade dos pais,
renda familiar, e outras características socioeconômicas.

Classes principais:
- SocioeconomicAnalysisProcessor: Análise de aspectos socioeconômicos
- SocialDistributionProcessor: Distribuição de características sociais
- ComparativeSocialProcessor: Análise comparativa entre diferentes grupos
"""

# Importar processadores principais
from .processors import (
    SocioeconomicAnalysisProcessor,
    SocialDistributionProcessor,
    ComparativeSocialProcessor,
    SocialCorrelationProcessor
)

# Importar gerenciador de dados
from .data_manager import SocialDataManager, prepare_social_data

__all__ = [
    'SocioeconomicAnalysisProcessor',
    'SocialDistributionProcessor',
    'ComparativeSocialProcessor',
    'SocialCorrelationProcessor',
    'SocialDataManager',
    'prepare_social_data'
]
