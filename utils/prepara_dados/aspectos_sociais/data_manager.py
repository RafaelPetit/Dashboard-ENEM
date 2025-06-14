"""
Gerenciador de dados para aspectos sociais.

Este módulo fornece uma interface unificada (Facade) para todas as operações
de preparação de dados relacionadas aos aspectos sociais dos candidatos,
mantendo compatibilidade com o código existente.
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from .processors import (
    SocioeconomicAnalysisProcessor,
    SocialDistributionProcessor,
    ComparativeSocialProcessor,
    SocialCorrelationProcessor
)
from ..common_utils import MappingManager, DataFilter
from ...helpers.cache_utils import optimized_cache


class SocialDataManager:
    """
    Gerenciador centralizado para preparação de dados de aspectos sociais.
    
    Esta classe atua como um Facade, fornecendo uma interface simples    para todas as operações relacionadas aos aspectos sociais.
    """
    
    def __init__(self):
        self.socioeconomic_processor = SocioeconomicAnalysisProcessor()
        self.distribution_processor = SocialDistributionProcessor()
        self.comparative_processor = ComparativeSocialProcessor()
        self.correlation_processor = SocialCorrelationProcessor()
        self.mapping_manager = MappingManager()
        self.data_filter = DataFilter()
    
    def prepare_socioeconomic_analysis(
        self,
        data: pd.DataFrame,
        aspecto_social: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Prepara dados para análise socioeconômica.
        
        Args:
            data: DataFrame com microdados
            aspecto_social: Nome do aspecto social a analisar
            variaveis_categoricas: Metadados das variáveis
            
        Returns:
            DataFrame com dados preparados para análise
        """
        return self.socioeconomic_processor.process(
            data=data,
            aspecto_social=aspecto_social,
            variaveis_categoricas=variaveis_categoricas
        )
    
    def prepare_social_distribution(
        self,
        data: pd.DataFrame,
        aspecto_social: str,
        categorias_interesse: Optional[List[str]] = None,
        agrupar_por_regiao: bool = False
    ) -> pd.DataFrame:
        """
        Prepara dados de distribuição social.
        
        Args:
            data: DataFrame com microdados
            aspecto_social: Nome da característica social
            categorias_interesse: Lista de categorias específicas
            agrupar_por_regiao: Se deve agrupar por região
            
        Returns:
            DataFrame com distribuição preparada
        """
        return self.distribution_processor.process(
            data=data,
            aspecto_social=aspecto_social,
            categorias_interesse=categorias_interesse,
            agrupar_por_regiao=agrupar_por_regiao
        )
    
    def prepare_comparative_analysis(
        self,
        data: pd.DataFrame,
        aspecto_primario: str,
        aspecto_secundario: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Prepara análise comparativa entre aspectos sociais.
        
        Args:
            data: DataFrame com microdados
            aspecto_primario: Aspecto social principal
            aspecto_secundario: Aspecto social para comparação
            variaveis_categoricas: Metadados das variáveis
            
        Returns:
            DataFrame com análise comparativa
        """
        return self.comparative_processor.process(
            data=data,
            aspecto_primario=aspecto_primario,
            aspecto_secundario=aspecto_secundario,
            variaveis_categoricas=variaveis_categoricas
        )


# Instância global do gerenciador
_social_data_manager = SocialDataManager()


# Funções de compatibilidade com a API existente
@optimized_cache(ttl=1800)
def prepare_social_data(
    microdados_full: pd.DataFrame,
    aspecto_social: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]],
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Função principal para preparação de dados de aspectos sociais.
    
    Esta função mantém compatibilidade com a API existente while leveraging
    the new modular architecture.
    
    Args:
        microdados_full: DataFrame com microdados completos
        aspecto_social: Nome do aspecto social a analisar
        variaveis_categoricas: Metadados das variáveis categóricas
        agrupar_por_regiao: Se deve agrupar por região
        
    Returns:
        DataFrame preparado para visualização
    """
    return _social_data_manager.prepare_social_distribution(
        data=microdados_full,
        aspecto_social=aspecto_social,
        agrupar_por_regiao=agrupar_por_regiao
    )


def preparar_dados_aspecto_social(
    microdados_full: pd.DataFrame,
    aspecto_social: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]],
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Função de compatibilidade para preparar dados de aspecto social.
    
    Mantém a interface da função original enquanto usa a nova arquitetura.
    """
    return prepare_social_data(
        microdados_full=microdados_full,
        aspecto_social=aspecto_social,
        variaveis_categoricas=variaveis_categoricas,
        agrupar_por_regiao=agrupar_por_regiao
    )


def preparar_dados_comparacao_social(
    microdados_full: pd.DataFrame,
    aspecto_primario: str,
    aspecto_secundario: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """
    Prepara dados para comparação entre dois aspectos sociais.
    
    Args:
        microdados_full: DataFrame com microdados completos
        aspecto_primario: Primeiro aspecto social
        aspecto_secundario: Segundo aspecto social
        variaveis_categoricas: Metadados das variáveis
        
    Returns:
        DataFrame com análise comparativa
    """
    return _social_data_manager.prepare_comparative_analysis(
        data=microdados_full,
        aspecto_primario=aspecto_primario,
        aspecto_secundario=aspecto_secundario,
        variaveis_categoricas=variaveis_categoricas
    )


def obter_estatisticas_aspecto_social(
    microdados_full: pd.DataFrame,
    aspecto_social: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Obtém estatísticas descritivas de um aspecto social.
    
    Args:
        microdados_full: DataFrame com microdados completos
        aspecto_social: Nome do aspecto social
        variaveis_categoricas: Metadados das variáveis
        
    Returns:
        Dicionário com estatísticas descritivas
    """
    # Preparar dados
    df_prepared = _social_data_manager.prepare_socioeconomic_analysis(
        data=microdados_full,
        aspecto_social=aspecto_social,
        variaveis_categoricas=variaveis_categoricas
    )
    
    if df_prepared.empty:
        return {}
    
    # Calcular estatísticas
    total_registros = df_prepared['Quantidade'].sum()
    num_categorias = df_prepared['Categoria'].nunique()
    num_estados = df_prepared['Estado'].nunique()
    
    # Distribuição percentual geral
    distribuicao_geral = df_prepared.groupby('Categoria')['Quantidade'].sum()
    distribuicao_percentual = (distribuicao_geral / total_registros * 100).round(2)
    
    return {
        'total_registros': total_registros,
        'num_categorias': num_categorias,
        'num_estados': num_estados,
        'distribuicao_percentual': distribuicao_percentual.to_dict(),
        'categoria_mais_frequente': distribuicao_percentual.idxmax(),
        'categoria_menos_frequente': distribuicao_percentual.idxmin()
    }


@optimized_cache(ttl=1800)
def preparar_dados_correlacao(
    microdados: pd.DataFrame, 
    var_x: str, 
    var_y: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> Tuple[pd.DataFrame, str, str]:
    """
    Função de compatibilidade para preparar dados de correlação.
    
    Mantém a mesma interface da função original mas usa o novo
    SocialCorrelationProcessor internamente.
    
    Args:
        microdados: DataFrame com microdados
        var_x: Nome da primeira variável
        var_y: Nome da segunda variável
        variaveis_sociais: Dicionário com mapeamentos das variáveis
        
    Returns:
        Tuple com (DataFrame preparado, nome da coluna X, nome da coluna Y)
    """
    return _social_data_manager.correlation_processor.process(
        data=microdados,
        var_x=var_x,
        var_y=var_y,
        variaveis_sociais=variaveis_sociais
    )
