"""
Gerenciador de dados para análises de desempenho.

Este módulo fornece uma interface unificada (Facade) para todas as operações
de preparação de dados relacionadas ao desempenho dos candidatos,
mantendo compatibilidade com o código existente.
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from .processors import (
    ComparativePerformanceProcessor,
    PerformanceDistributionProcessor,
    StatePerformanceProcessor,
    ScatterAnalysisProcessor
)
from ..common_utils import MappingManager, DataFilter
from ...helpers.cache_utils import optimized_cache


class PerformanceDataManager:
    """
    Gerenciador centralizado para preparação de dados de desempenho.
    
    Esta classe atua como um Facade, fornecendo uma interface simples
    para todas as operações relacionadas ao desempenho dos candidatos.
    """
    
    def __init__(self):
        self.comparative_processor = ComparativePerformanceProcessor()
        self.distribution_processor = PerformanceDistributionProcessor()
        self.state_processor = StatePerformanceProcessor()
        self.scatter_processor = ScatterAnalysisProcessor()
        self.mapping_manager = MappingManager()
        self.data_filter = DataFilter()
    
    def prepare_comparative_analysis(
        self,
        data: pd.DataFrame,
        variavel_selecionada: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]],
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Prepara análise comparativa de desempenho.
        
        Args:
            data: DataFrame com microdados
            variavel_selecionada: Variável categórica para análise
            variaveis_categoricas: Metadados das variáveis
            colunas_notas: Lista de colunas com notas
            competencia_mapping: Mapeamento de competências
            
        Returns:
            DataFrame com médias por categoria e competência
        """
        return self.comparative_processor.process(
            data=data,
            variavel_selecionada=variavel_selecionada,
            variaveis_categoricas=variaveis_categoricas,
            colunas_notas=colunas_notas,
            competencia_mapping=competencia_mapping
        )
    
    def prepare_line_chart_data(
        self,
        df_resultados: pd.DataFrame,
        competencia_ordenacao: Optional[str] = None,
        competencia_filtro: Optional[str] = None,
        ordenar_decrescente: bool = False
    ) -> pd.DataFrame:
        """
        Prepara dados para gráfico de linha.
        
        Args:
            df_resultados: DataFrame com resultados das médias
            competencia_ordenacao: Competência para ordenação
            competencia_filtro: Filtrar apenas esta competência
            ordenar_decrescente: Ordenar por valor decrescente
            
        Returns:
            DataFrame preparado para visualização em linha
        """
        return self.distribution_processor.process(
            data=df_resultados,
            competencia_ordenacao=competencia_ordenacao,
            competencia_filtro=competencia_filtro,
            ordenar_decrescente=ordenar_decrescente
        )
    
    def prepare_state_performance(
        self,
        data: pd.DataFrame,
        estados_selecionados: List[str],
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str],
        agrupar_por_regiao: bool = False
    ) -> pd.DataFrame:
        """
        Prepara dados de desempenho por estado/região.
        
        Args:
            data: DataFrame com microdados
            estados_selecionados: Estados para análise
            colunas_notas: Colunas com notas
            competencia_mapping: Mapeamento de competências
            agrupar_por_regiao: Agrupar por região
            
        Returns:
            DataFrame com desempenho por estado/região
        """
        return self.state_processor.process(
            data=data,
            estados_selecionados=estados_selecionados,
            colunas_notas=colunas_notas,
            competencia_mapping=competencia_mapping,
            agrupar_por_regiao=agrupar_por_regiao
        )
    
    def prepare_scatter_analysis(
        self,
        data: pd.DataFrame,
        eixo_x: str,
        eixo_y: str,
        filtro_sexo: Optional[str] = None,
        filtro_tipo_escola: Optional[str] = None,
        filtro_raca: Optional[str] = None,
        filtro_faixa_salarial: Optional[int] = None,
        excluir_notas_zero: bool = True,
        max_amostras: Optional[int] = None
    ) -> Tuple[pd.DataFrame, int]:
        """
        Prepara dados para análise de dispersão.
        
        Args:
            data: DataFrame com dados completos
            eixo_x: Coluna para eixo X
            eixo_y: Coluna para eixo Y
            filtro_sexo: Filtro por sexo
            filtro_tipo_escola: Filtro por tipo de escola
            filtro_raca: Filtro por raça/cor
            filtro_faixa_salarial: Filtro por faixa salarial
            excluir_notas_zero: Excluir notas zero
            max_amostras: Número máximo de amostras
              Returns:
            Tuple com DataFrame filtrado e registros removidos
        """
        print("[DEBUG] === prepare_scatter_analysis chamado ===")
        print(f"[DEBUG] Data shape: {data.shape if data is not None else 'None'}")
        print(f"[DEBUG] Parametros: eixo_x={eixo_x}, eixo_y={eixo_y}")
        
        try:
            resultado = self.scatter_processor.process(
                data=data,
                eixo_x=eixo_x,
                eixo_y=eixo_y,
                filtro_sexo=filtro_sexo,
                filtro_tipo_escola=filtro_tipo_escola,
                filtro_raca=filtro_raca,
                filtro_faixa_salarial=filtro_faixa_salarial,
                excluir_notas_zero=excluir_notas_zero,
                max_amostras=max_amostras
            )
            print(f"[DEBUG] scatter_processor.process retornou: tipo={type(resultado)}")
            return resultado
        except Exception as e:
            print(f"[DEBUG] ERRO em prepare_scatter_analysis: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def prepare_general_performance_data(
        self,
        data: pd.DataFrame,
        colunas_notas: List[str],
        desempenho_mapping: Dict[int, str]
    ) -> pd.DataFrame:
        """
        Prepara dados gerais de desempenho.
        
        Args:
            data: DataFrame com microdados originais
            colunas_notas: Lista de colunas de notas
            desempenho_mapping: Mapeamento de categorias de desempenho
            
        Returns:
            DataFrame com dados preparados e categoria de desempenho
        """
        if data.empty:
            return pd.DataFrame()
        
        # Colunas demográficas necessárias
        colunas_demograficas = [
            'TP_COR_RACA', 'TP_SEXO', 'TP_DEPENDENCIA_ADM_ESC', 
            'TP_FAIXA_ETARIA', 'Q001', 'Q002', 'Q005', 'Q006',
            'Q025', 'TP_FAIXA_SALARIAL', 'TP_ST_CONCLUSAO'
        ]
        
        # Determinar colunas necessárias
        colunas_necessarias = list(colunas_notas)
        
        # Adicionar colunas demográficas existentes
        for col in colunas_demograficas:
            if col in data.columns:
                colunas_necessarias.append(col)
        
        # Adicionar coluna de desempenho se existir
        if 'NU_DESEMPENHO' in data.columns:
            colunas_necessarias.append('NU_DESEMPENHO')
        
        # Criar cópia otimizada
        df_trabalho = data[colunas_necessarias].copy()
        
        # Adicionar categoria de desempenho
        if 'NU_DESEMPENHO' in df_trabalho.columns:
            df_trabalho['CATEGORIA_DESEMPENHO'] = df_trabalho['NU_DESEMPENHO'].map(desempenho_mapping)
            
            # Converter para categoria
            if not df_trabalho['CATEGORIA_DESEMPENHO'].isna().all():
                df_trabalho['CATEGORIA_DESEMPENHO'] = df_trabalho['CATEGORIA_DESEMPENHO'].astype('category')
        
        from data.data_loader import optimize_dtypes
        return optimize_dtypes(df_trabalho)


# Instância global do gerenciador
_performance_data_manager = PerformanceDataManager()


# Funções de compatibilidade com a API existente
@optimized_cache(ttl=1800)
def prepare_performance_data(
    microdados_full: pd.DataFrame,
    variavel_selecionada: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]],
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Função principal para preparação de dados de desempenho.
    
    Esta função mantém compatibilidade com a API existente.
    
    Args:
        microdados_full: DataFrame com microdados completos
        variavel_selecionada: Variável categórica para análise
        variaveis_categoricas: Metadados das variáveis categóricas
        colunas_notas: Lista de colunas com notas
        competencia_mapping: Mapeamento de competências
        
    Returns:
        DataFrame preparado para visualização
    """
    return _performance_data_manager.prepare_comparative_analysis(
        data=microdados_full,
        variavel_selecionada=variavel_selecionada,
        variaveis_categoricas=variaveis_categoricas,
        colunas_notas=colunas_notas,
        competencia_mapping=competencia_mapping
    )


def preparar_dados_comparativo(
    microdados_full: pd.DataFrame,
    variavel_selecionada: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]],
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Função de compatibilidade para preparar dados comparativos.
    
    Mantém a interface da função original.
    """
    return prepare_performance_data(
        microdados_full=microdados_full,
        variavel_selecionada=variavel_selecionada,
        variaveis_categoricas=variaveis_categoricas,
        colunas_notas=colunas_notas,
        competencia_mapping=competencia_mapping
    )


def preparar_dados_grafico_linha(
    df_resultados: pd.DataFrame,
    competencia_ordenacao: Optional[str] = None,
    competencia_filtro: Optional[str] = None,
    ordenar_decrescente: bool = False
) -> pd.DataFrame:
    """
    Prepara dados para gráfico de linha de desempenho.
    
    Mantém compatibilidade com a função original.
    """
    return _performance_data_manager.prepare_line_chart_data(
        df_resultados=df_resultados,
        competencia_ordenacao=competencia_ordenacao,
        competencia_filtro=competencia_filtro,
        ordenar_decrescente=ordenar_decrescente
    )


def preparar_dados_desempenho_geral(
    microdados: pd.DataFrame,
    colunas_notas: List[str],
    desempenho_mapping: Dict[int, str]
) -> pd.DataFrame:
    """
    Prepara dados gerais de desempenho.
    
    Mantém compatibilidade com a função original.
    """
    return _performance_data_manager.prepare_general_performance_data(
        data=microdados,
        colunas_notas=colunas_notas,
        desempenho_mapping=desempenho_mapping
    )


def filtrar_dados_scatter(
    dados: pd.DataFrame,
    filtro_sexo: Optional[str],
    filtro_tipo_escola: Optional[str],
    eixo_x: str,
    eixo_y: str,
    excluir_notas_zero: bool = True,
    filtro_raca: Optional[str] = None,
    filtro_faixa_salarial: Optional[int] = None,
    max_amostras: Optional[int] = None
) -> Tuple[pd.DataFrame, int]:
    """
    Filtra dados para visualização de gráfico de dispersão.
    
    Mantém compatibilidade com a função original.
    """
    print("[DEBUG] === INICIANDO filtrar_dados_scatter ===")
    print(f"[DEBUG] Dados input shape: {dados.shape if dados is not None else 'None'}")
    print(f"[DEBUG] Filtros: sexo={filtro_sexo}, escola={filtro_tipo_escola}, raca={filtro_raca}, faixa_salarial={filtro_faixa_salarial}")
    print(f"[DEBUG] Eixos: x={eixo_x}, y={eixo_y}")
    print(f"[DEBUG] Excluir notas zero: {excluir_notas_zero}")
    
    try:
        resultado = _performance_data_manager.prepare_scatter_analysis(
            data=dados,
            eixo_x=eixo_x,
            eixo_y=eixo_y,
            filtro_sexo=filtro_sexo,
            filtro_tipo_escola=filtro_tipo_escola,
            filtro_raca=filtro_raca,
            filtro_faixa_salarial=filtro_faixa_salarial,
            excluir_notas_zero=excluir_notas_zero,
            max_amostras=max_amostras
        )
        print(f"[DEBUG] Resultado obtido: tipo={type(resultado)}")
        if isinstance(resultado, tuple) and len(resultado) == 2:
            df_result, removed = resultado
            print(f"[DEBUG] DataFrame resultado shape: {df_result.shape if df_result is not None else 'None'}")
            print(f"[DEBUG] Registros removidos: {removed}")
        else:
            print(f"[DEBUG] Resultado inesperado: {resultado}")
        return resultado
    except Exception as e:
        print(f"[DEBUG] ERRO em filtrar_dados_scatter: {e}")
        import traceback
        traceback.print_exc()
        raise


def preparar_dados_grafico_linha_desempenho(
    microdados_estados: pd.DataFrame,
    estados_selecionados: List[str],
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str],
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Prepara dados para gráfico de linha de desempenho por estado.
    
    Mantém compatibilidade com a função original.
    """
    return _performance_data_manager.prepare_state_performance(
        data=microdados_estados,
        estados_selecionados=estados_selecionados,
        colunas_notas=colunas_notas,
        competencia_mapping=competencia_mapping,
        agrupar_por_regiao=agrupar_por_regiao
    )


def obter_ordem_categorias(
    df_resultados: pd.DataFrame,
    variavel_selecionada: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Determina a ordem das categorias para exibição no gráfico.
    
    Mantém compatibilidade com a função original.
    """
    if df_resultados.empty:
        return []
    
    categorias_unicas = df_resultados['Categoria'].unique()
    
    # Verificar se existe ordem predefinida
    if (variavel_selecionada in variaveis_categoricas and 
        'ordem' in variaveis_categoricas[variavel_selecionada]):
        
        ordem_definida = variaveis_categoricas[variavel_selecionada]['ordem']
        ordem_filtrada = [cat for cat in ordem_definida if cat in categorias_unicas]
        categorias_faltantes = [cat for cat in categorias_unicas if cat not in ordem_filtrada]
        return ordem_filtrada + sorted(categorias_faltantes)
    
    # Usar ordem alfabética como padrão
    return sorted(categorias_unicas)


def calcular_estatisticas_desempenho(
    df_resultados: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calcula estatísticas descritivas dos dados de desempenho.
    
    Args:
        df_resultados: DataFrame com resultados de desempenho
        
    Returns:
        Dicionário com estatísticas descritivas
    """
    if df_resultados.empty:
        return {}
    
    # Estatísticas básicas
    estatisticas = {
        'num_categorias': df_resultados['Categoria'].nunique(),
        'num_competencias': df_resultados['Competência'].nunique(),
        'media_geral': df_resultados['Média'].mean(),
        'mediana_geral': df_resultados['Média'].median(),
        'desvio_padrao': df_resultados['Média'].std(),
        'valor_minimo': df_resultados['Média'].min(),
        'valor_maximo': df_resultados['Média'].max()
    }
    
    # Estatísticas por competência
    estatisticas_por_competencia = df_resultados.groupby('Competência')['Média'].agg([
        'mean', 'median', 'std', 'min', 'max'
    ]).round(2).to_dict('index')
    
    estatisticas['por_competencia'] = estatisticas_por_competencia
    
    # Categoria com melhor e pior desempenho
    medias_por_categoria = df_resultados.groupby('Categoria')['Média'].mean()
    estatisticas['melhor_categoria'] = medias_por_categoria.idxmax()
    estatisticas['pior_categoria'] = medias_por_categoria.idxmin()
    
    return estatisticas
