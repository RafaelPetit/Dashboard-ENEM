"""
Processadores especializados para análise de aspectos sociais.

Este módulo contém classes que implementam diferentes tipos de análises
sobre os aspectos sociais dos candidatos do ENEM, utilizando os padrões
estabelecidos nas classes base.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from ..base import BaseDataProcessor, CacheableProcessor, StateGroupedProcessor
from ..common_utils import MappingManager, StatisticalCalculator, DataAggregator, DataFilter
from ...helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from data.data_loader import optimize_dtypes


class SocioeconomicAnalysisProcessor(CacheableProcessor):
    """
    Processador para análise de aspectos socioeconômicos dos candidatos.
    
    Responsável por preparar dados relacionados à escolaridade dos pais,
    renda familiar, e outras características socioeconômicas.
    """
    
    def __init__(self):
        super().__init__("socioeconomic_analysis", ttl=1800)
        self.mapping_manager = MappingManager()
        self.stats_calculator = StatisticalCalculator()
        self.data_aggregator = DataAggregator()
        self.data_filter = DataFilter()
    
    def _process_internal(
        self, 
        data: pd.DataFrame, 
        aspecto_social: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]],
        **kwargs
    ) -> pd.DataFrame:
        """
        Processa dados de aspectos socioeconômicos.
        
        Args:
            data: DataFrame com microdados
            aspecto_social: Nome do aspecto social a analisar
            variaveis_categoricas: Metadados das variáveis
            
        Returns:
            DataFrame com dados processados para análise socioeconômica
        """
        # Validar dados de entrada
        self._validate_input(data, required_columns=[aspecto_social])
        
        # Obter mapeamentos necessários
        mappings = self.mapping_manager.get_mappings()
        
        # Determinar colunas necessárias
        colunas_necessarias = self._determinar_colunas_necessarias(
            aspecto_social, variaveis_categoricas
        )
        
        # Filtrar dados válidos
        df_trabalho = self.data_filter.filter_valid_data(
            data[colunas_necessarias].copy(),
            required_columns=[aspecto_social]
        )
        
        # Aplicar mapeamento se disponível
        mapeamento = self._obter_mapeamento_aspecto(aspecto_social, variaveis_categoricas)
        if mapeamento:
            df_trabalho = self.mapping_manager.apply_mapping(
                df_trabalho, aspecto_social, mapeamento
            )
        
        # Preparar dados para análise
        resultados = self._preparar_dados_socioeconomicos(
            df_trabalho, aspecto_social, mappings
        )
        
        # Otimizar tipos de dados
        return optimize_dtypes(pd.DataFrame(resultados))
    
    def _determinar_colunas_necessarias(
        self, 
        aspecto_social: str, 
        variaveis_categoricas: Dict
    ) -> List[str]:
        """Determina quais colunas são necessárias para a análise."""
        colunas = [aspecto_social]
        
        # Adicionar colunas demográficas relevantes
        colunas_demograficas = [
            'SG_UF_PROVA', 'TP_COR_RACA', 'TP_SEXO', 
            'TP_DEPENDENCIA_ADM_ESC', 'TP_FAIXA_ETARIA'
        ]
        
        return colunas + colunas_demograficas
    
    def _obter_mapeamento_aspecto(
        self, 
        aspecto_social: str, 
        variaveis_categoricas: Dict
    ) -> Optional[Dict]:
        """Obtém o mapeamento para o aspecto social especificado."""
        if (aspecto_social in variaveis_categoricas and 
            "mapeamento" in variaveis_categoricas[aspecto_social]):
            return variaveis_categoricas[aspecto_social]["mapeamento"]
        return None
    
    @memory_intensive_function
    def _preparar_dados_socioeconomicos(
        self, 
        df: pd.DataFrame, 
        aspecto_social: str, 
        mappings: Dict
    ) -> List[Dict[str, Any]]:
        """Prepara dados socioeconômicos com cálculos estatísticos."""
        resultados = []
        
        # Agrupar por estado para processamento eficiente
        grupos_estado = df.groupby('SG_UF_PROVA', observed=True)
        
        for estado, dados_estado in grupos_estado:
            if len(dados_estado) == 0:
                continue
                
            # Calcular distribuição das categorias
            distribuicao = dados_estado[aspecto_social].value_counts()
            total_estado = len(dados_estado)
            
            for categoria, quantidade in distribuicao.items():
                percentual = (quantidade / total_estado * 100) if total_estado > 0 else 0
                
                resultados.append({
                    'Estado': estado,
                    'Aspecto': aspecto_social,
                    'Categoria': categoria,
                    'Quantidade': quantidade,
                    'Percentual': round(percentual, 2),
                    'Total_Estado': total_estado
                })
        
        return resultados


class SocialDistributionProcessor(StateGroupedProcessor):
    """
    Processador para análise de distribuição de características sociais.
    
    Especializado em calcular distribuições percentuais de categorias
    sociais por estado ou região.
    """
    
    def __init__(self):
        super().__init__("social_distribution", ttl=1800)
        self.mapping_manager = MappingManager()
        self.data_aggregator = DataAggregator()
    
    def _process_internal(
        self, 
        data: pd.DataFrame, 
        aspecto_social: str,
        categorias_interesse: Optional[List[str]] = None,
        agrupar_por_regiao: bool = False,
        **kwargs
    ) -> pd.DataFrame:
        """
        Processa distribuição de características sociais.
        
        Args:
            data: DataFrame com microdados
            aspecto_social: Nome da característica social
            categorias_interesse: Lista de categorias específicas
            agrupar_por_regiao: Se deve agrupar por região
            
        Returns:
            DataFrame com distribuição social processada
        """
        # Validar entrada
        self._validate_input(data, required_columns=[aspecto_social, 'SG_UF_PROVA'])
        
        # Filtrar dados válidos
        df_trabalho = data[[aspecto_social, 'SG_UF_PROVA']].dropna()
        
        # Determinar categorias a processar
        if categorias_interesse is None:
            categorias_interesse = df_trabalho[aspecto_social].unique().tolist()
        
        # Processar distribuição por estado
        resultados = self._calcular_distribuicao_estados(
            df_trabalho, aspecto_social, categorias_interesse
        )
        
        df_resultado = pd.DataFrame(resultados)
        
        # Agrupar por região se solicitado
        if agrupar_por_regiao and not df_resultado.empty:
            df_resultado = self._agrupar_por_regiao(df_resultado)
        
        return optimize_dtypes(df_resultado)
    
    @memory_intensive_function
    def _calcular_distribuicao_estados(
        self, 
        df: pd.DataFrame, 
        coluna_aspecto: str, 
        categorias: List[str]
    ) -> List[Dict[str, Any]]:
        """Calcula distribuição de categorias por estado."""
        resultados = []
        
        # Processar cada estado
        estados_unicos = df['SG_UF_PROVA'].unique()
        
        for i, estado in enumerate(estados_unicos):
            dados_estado = df[df['SG_UF_PROVA'] == estado]
            
            if len(dados_estado) == 0:
                continue
            
            total_estado = len(dados_estado)
            contagem_categorias = dados_estado[coluna_aspecto].value_counts()
            contagem_dict = contagem_categorias.to_dict()
            
            # Processar cada categoria
            for categoria in categorias:
                quantidade = contagem_dict.get(categoria, 0)
                percentual = (quantidade / total_estado * 100) if total_estado > 0 else 0
                
                resultados.append({
                    'Estado': estado,
                    'Categoria': categoria,
                    'Quantidade': quantidade,
                    'Percentual': round(percentual, 2)
                })
            
            # Liberar memória periodicamente
            if (i+1) % 10 == 0:
                release_memory()
        
        return resultados
    
    def _agrupar_por_regiao(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrupa dados por região."""
        from ...mappings import get_mappings
        
        mappings = get_mappings()
        regioes_mapping = mappings['regioes_mapping']
        
        if df.empty:
            return df
        
        try:
            # Criar mapeamento estado -> região
            estado_para_regiao = {
                estado: regiao 
                for regiao, estados in regioes_mapping.items() 
                for estado in estados
            }
            
            # Adicionar coluna de região
            df_com_regiao = df.copy()
            df_com_regiao['Região'] = df_com_regiao['Estado'].map(estado_para_regiao)
            
            # Agrupar por região e categoria
            df_agrupado = df_com_regiao.groupby(['Região', 'Categoria'])['Percentual'].mean().reset_index()
            
            # Calcular quantidades
            quantidades = df_com_regiao.groupby(['Região', 'Categoria'])['Quantidade'].sum().reset_index()
            
            # Juntar dados
            df_agrupado = df_agrupado.merge(quantidades, on=['Região', 'Categoria'])
            df_agrupado = df_agrupado.rename(columns={'Região': 'Estado'})
            
            # Otimizar tipos
            regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
            df_agrupado['Estado'] = pd.Categorical(df_agrupado['Estado'], categories=regioes)
            df_agrupado['Percentual'] = df_agrupado['Percentual'].round(2)
            
            return df_agrupado
        
        except Exception as e:
            print(f"Erro ao agrupar por região: {e}")
            return df


class ComparativeSocialProcessor(CacheableProcessor):
    """
    Processador para análises comparativas entre diferentes grupos sociais.
    
    Permite comparar características sociais entre diferentes segmentos
    da população de candidatos.
    """
    
    def __init__(self):
        super().__init__("comparative_social", ttl=1800)
        self.mapping_manager = MappingManager()
        self.stats_calculator = StatisticalCalculator()
    
    def _process_internal(
        self, 
        data: pd.DataFrame, 
        aspecto_primario: str,
        aspecto_secundario: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]],
        **kwargs
    ) -> pd.DataFrame:
        """
        Processa análise comparativa entre aspectos sociais.
        
        Args:
            data: DataFrame com microdados
            aspecto_primario: Aspecto social principal
            aspecto_secundario: Aspecto social para comparação
            variaveis_categoricas: Metadados das variáveis
            
        Returns:
            DataFrame com análise comparativa
        """
        # Validar entrada
        required_cols = [aspecto_primario, aspecto_secundario]
        self._validate_input(data, required_columns=required_cols)
        
        # Filtrar dados válidos
        df_trabalho = data[required_cols].dropna()
        
        # Calcular análise cruzada
        resultados = self._calcular_analise_cruzada(
            df_trabalho, aspecto_primario, aspecto_secundario
        )
        
        return optimize_dtypes(pd.DataFrame(resultados))
    
    @memory_intensive_function
    def _calcular_analise_cruzada(
        self, 
        df: pd.DataFrame, 
        aspecto1: str, 
        aspecto2: str
    ) -> List[Dict[str, Any]]:
        """Calcula análise cruzada entre dois aspectos sociais."""
        resultados = []
        
        # Criar tabela cruzada
        tabela_cruzada = pd.crosstab(df[aspecto1], df[aspecto2], normalize='index') * 100
        
        # Converter para formato longo
        for idx in tabela_cruzada.index:
            for col in tabela_cruzada.columns:
                percentual = tabela_cruzada.loc[idx, col]
                
                resultados.append({
                    'Aspecto_Primario': aspecto1,
                    'Categoria_Primaria': idx,
                    'Aspecto_Secundario': aspecto2,
                    'Categoria_Secundaria': col,
                    'Percentual': round(percentual, 2)
                })
        
        return resultados
