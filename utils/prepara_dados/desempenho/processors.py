"""
Processadores especializados para análise de desempenho.

Este módulo contém classes que implementam diferentes tipos de análises
sobre o desempenho dos candidatos do ENEM, utilizando os padrões
estabelecidos nas classes base.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from ..base import BaseDataProcessor, CacheableProcessor, StateGroupedProcessor, ProcessingConfig
from ..common_utils import MappingManager, StatisticalCalculator, DataAggregator, DataFilter
from ...helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from data.data_loader import calcular_seguro, optimize_dtypes


class ComparativePerformanceProcessor(CacheableProcessor):
    """
    Processador para análise comparativa de desempenho por variável categórica.
    
    Responsável por calcular médias de desempenho segmentadas por diferentes    características dos candidatos (sexo, tipo de escola, etc.).
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config, cache_key_prefix="comparative_performance")
        self.mapping_manager = MappingManager()
        self.stats_calculator = StatisticalCalculator()
        self.data_filter = DataFilter()
    
    def _process_internal(
        self,
        data: pd.DataFrame,
        variavel_selecionada: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]],
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str],
        **kwargs
    ) -> pd.DataFrame:
        """
        Processa análise comparativa de desempenho.
        
        Args:
            data: DataFrame com microdados
            variavel_selecionada: Variável categórica para análise
            variaveis_categoricas: Metadados das variáveis
            colunas_notas: Lista de colunas com notas
            competencia_mapping: Mapeamento de competências
            
        Returns:
            DataFrame com médias por categoria e competência
        """        # Validar dados de entrada
        # Verificar se colunas_notas é lista ou dicionário e converter se necessário
        if isinstance(colunas_notas, dict):
            colunas_notas = list(colunas_notas.keys())
        elif not isinstance(colunas_notas, list):
            colunas_notas = list(colunas_notas)
            
        colunas_necessarias = [variavel_selecionada] + colunas_notas
        self._validate_input(data, required_columns=colunas_necessarias)
        
        # Filtrar dados válidos
        df_trabalho = self.data_filter.filter_valid_scores(
            data[colunas_necessarias].copy(),
            score_columns=colunas_notas
        )
        
        # Determinar mapeamento para a variável
        mapeamento = self._obter_mapeamento_variavel(
            variavel_selecionada, variaveis_categoricas
        )
        
        # Calcular médias por categoria
        resultados = self._calcular_medias_por_categoria(
            df_trabalho,
            variavel_selecionada,
            colunas_notas,
            competencia_mapping,
            mapeamento
        )
        
        df_resultados = pd.DataFrame(resultados)
        
        # Aplicar ordem categórica se disponível
        df_resultados = self._aplicar_ordem_categorica(
            df_resultados, variavel_selecionada, variaveis_categoricas
        )
        
        return optimize_dtypes(df_resultados)
    
    def _obter_mapeamento_variavel(
        self, 
        variavel: str, 
        variaveis_categoricas: Dict
    ) -> Optional[Dict]:
        """Obtém mapeamento para a variável especificada."""
        if (variavel in variaveis_categoricas and 
            "mapeamento" in variaveis_categoricas[variavel]):
            return variaveis_categoricas[variavel]["mapeamento"]
        return None
    
    @memory_intensive_function
    def _calcular_medias_por_categoria(
        self,
        df: pd.DataFrame,
        coluna_categoria: str,
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str],
        mapeamento: Optional[Dict[Any, str]] = None
    ) -> List[Dict[str, Any]]:
        """Calcula médias de desempenho por categoria e competência."""
        resultados = []        # Obter categorias únicas
        if coluna_categoria not in df.columns:
            raise ValueError(f"Coluna '{coluna_categoria}' não encontrada no DataFrame")
        
        # Debug: verificar o tipo do resultado
        coluna_data = df[coluna_categoria]
        if isinstance(coluna_data, pd.DataFrame):
            # Se for DataFrame, pegar a primeira coluna
            categorias_unicas = coluna_data.iloc[:, 0].unique()
        else:
            # Se for Series, usar normalmente
            categorias_unicas = coluna_data.unique()
            
        total_categorias = len(categorias_unicas)
        
        # Verificar limites de processamento
        mappings = self.mapping_manager.get_mappings()
        config = mappings.get('config_processamento', {})
        if total_categorias > config.get('max_categorias_alerta', 20):
            print(f"Alerta: {total_categorias} categorias. Isso pode afetar performance.")
        
        # Processamento eficiente com agrupamento
        if total_categorias <= config['limiar_agrupamento']:
            df_agrupado = df.groupby(coluna_categoria)
            
            for categoria in categorias_unicas:
                categoria_exibicao = (mapeamento.get(categoria, str(categoria)) 
                                    if mapeamento else str(categoria))
                
                try:
                    dados_categoria = df_agrupado.get_group(categoria)
                    
                    for competencia in colunas_notas:
                        notas_validas = dados_categoria[
                            dados_categoria[competencia] > 0
                        ][competencia]
                        
                        media_comp = calcular_seguro(notas_validas, 'media')
                        
                        resultados.append({
                            'Categoria': categoria_exibicao,
                            'Competência': competencia_mapping[competencia],
                            'Média': round(media_comp, 2)
                        })
                except KeyError:
                    continue
        else:
            # Processamento em lotes para muitas categorias
            for i, categoria in enumerate(categorias_unicas):
                dados_categoria = df[df[coluna_categoria] == categoria]
                categoria_exibicao = (mapeamento.get(categoria, str(categoria)) 
                                    if mapeamento else str(categoria))
                
                for competencia in colunas_notas:
                    notas_validas = dados_categoria[
                        dados_categoria[competencia] > 0
                    ][competencia]
                    
                    media_comp = calcular_seguro(notas_validas, 'media')
                    
                    resultados.append({
                        'Categoria': categoria_exibicao,
                        'Competência': competencia_mapping[competencia],
                        'Média': round(media_comp, 2)
                    })
                
                # Liberar memória periodicamente
                if (i+1) % config['tamanho_lote'] == 0:
                    release_memory()
        
        return resultados
    
    def _aplicar_ordem_categorica(
        self,
        df: pd.DataFrame,
        variavel_selecionada: str,
        variaveis_categoricas: Dict
    ) -> pd.DataFrame:
        """Aplica ordem categórica se definida."""
        if (variavel_selecionada in variaveis_categoricas and 
            "ordem" in variaveis_categoricas[variavel_selecionada]):
            
            ordem = variaveis_categoricas[variavel_selecionada]["ordem"]
            categorias_presentes = df['Categoria'].unique()
            ordem_filtrada = [cat for cat in ordem if cat in categorias_presentes]
            categorias_nao_mapeadas = [cat for cat in categorias_presentes 
                                     if cat not in ordem_filtrada]
            ordem_final = ordem_filtrada + sorted(categorias_nao_mapeadas)
            
            df['Categoria'] = pd.Categorical(
                df['Categoria'],
                categories=ordem_final,
                ordered=True
            )
            df = df.sort_values('Categoria')
        
        return df


class PerformanceDistributionProcessor(CacheableProcessor):
    """
    Processador para análise de distribuição de desempenho.
      Responsável por preparar dados para gráficos de linha e    análises de distribuição de notas.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config, cache_key_prefix="performance_distribution")
        self.mapping_manager = MappingManager()
    
    def _process_internal(
        self,
        data: pd.DataFrame,
        competencia_ordenacao: Optional[str] = None,
        competencia_filtro: Optional[str] = None,
        ordenar_decrescente: bool = False,
        **kwargs
    ) -> pd.DataFrame:
        """
        Processa dados para gráfico de linha de desempenho.
        
        Args:
            data: DataFrame com resultados das médias
            competencia_ordenacao: Competência para ordenação
            competencia_filtro: Filtrar apenas esta competência
            ordenar_decrescente: Ordenar por valor decrescente
            
        Returns:
            DataFrame preparado para visualização
        """
        if data.empty:
            return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
        
        df_linha = data.copy()
        
        # Filtrar por competência específica
        if competencia_filtro is not None:
            df_linha = df_linha[df_linha['Competência'] == competencia_filtro]
        
        # Aplicar ordenação por valor
        if ordenar_decrescente:
            df_linha = self._aplicar_ordenacao_decrescente(
                df_linha, data, competencia_ordenacao, competencia_filtro
            )
        
        return df_linha
    
    def _aplicar_ordenacao_decrescente(
        self,
        df_linha: pd.DataFrame,
        df_original: pd.DataFrame,
        competencia_ordenacao: Optional[str],
        competencia_filtro: Optional[str]
    ) -> pd.DataFrame:
        """Aplica ordenação decrescente por competência."""
        # Determinar competência de ordenação
        if competencia_ordenacao is None:
            if competencia_filtro is not None:
                competencia_ordenacao = competencia_filtro
            else:
                competencias_disponiveis = df_original['Competência'].unique()
                if len(competencias_disponiveis) > 0:
                    competencia_ordenacao = competencias_disponiveis[0]
        
        # Aplicar ordenação se temos competência válida
        if competencia_ordenacao is not None:
            df_ordem = df_original[df_original['Competência'] == competencia_ordenacao]
            
            if not df_ordem.empty:
                ordem_categorias = df_ordem.sort_values(
                    'Média', ascending=False
                )['Categoria'].unique().tolist()
                
                df_linha['Categoria'] = pd.Categorical(
                    df_linha['Categoria'],
                    categories=ordem_categorias,
                    ordered=True
                )
                df_linha = df_linha.sort_values('Categoria')
                df_linha.attrs['ordenado'] = True
        
        return df_linha


class StatePerformanceProcessor(StateGroupedProcessor):
    """
    Processador para análise de desempenho por estado/região.
      Especializado em calcular médias de desempenho agrupadas    por unidade federativa ou região.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__("state_performance", config)
        self.mapping_manager = MappingManager()
        self.stats_calculator = StatisticalCalculator()
    
    def _process_internal(
        self,
        data: pd.DataFrame,
        estados_selecionados: List[str],
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str],
        agrupar_por_regiao: bool = False,
        **kwargs
    ) -> pd.DataFrame:
        """
        Processa dados de desempenho por estado.
        
        Args:
            data: DataFrame com microdados
            estados_selecionados: Estados para análise
            colunas_notas: Colunas com notas
            competencia_mapping: Mapeamento de competências
            agrupar_por_regiao: Agrupar por região
            
        Returns:
            DataFrame com desempenho por estado/região
        """
        # Validar entrada
        self._validate_input(data, required_columns=['SG_UF_PROVA'] + colunas_notas)
        
        if not estados_selecionados:
            return pd.DataFrame()
        
        # Processar estados em lotes
        resultados = self._processar_estados_em_lotes(
            data, estados_selecionados, colunas_notas, competencia_mapping
        )
        
        df_final = pd.DataFrame(resultados)
        
        if df_final.empty:
            return df_final
        
        # Otimizar tipos de dados
        df_final = self._otimizar_tipos_dados(
            df_final, estados_selecionados, competencia_mapping
        )
        
        # Agrupar por região se solicitado
        if agrupar_por_regiao:
            df_final = self._agrupar_por_regiao(df_final)
        
        return df_final
    
    @memory_intensive_function
    def _processar_estados_em_lotes(
        self,
        data: pd.DataFrame,
        estados: List[str],
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Processa estados em lotes para calcular médias."""
        resultados = []
        
        try:
            grupos_estado = data.groupby('SG_UF_PROVA', observed=True)
        except Exception as e:
            print(f"Erro ao agrupar por estado: {e}")
            return resultados
        
        # Processar cada estado
        for i, estado in enumerate(estados):
            try:
                dados_estado = grupos_estado.get_group(estado)
            except KeyError:
                continue
            
            if len(dados_estado) == 0:
                continue
            
            medias_estado = []
            
            # Calcular média para cada área
            for area in colunas_notas:
                if area not in dados_estado.columns:
                    continue
                
                notas = dados_estado[area].values
                notas_validas = notas[notas > 0]
                
                media_area = calcular_seguro(notas_validas, 'media')
                media_area = round(media_area, 2)
                
                resultados.append({
                    'Estado': estado,
                    'Área': competencia_mapping[area],
                    'Média': media_area
                })
                
                medias_estado.append(media_area)
            
            # Adicionar média geral
            if medias_estado:
                resultados.append({
                    'Estado': estado,
                    'Área': 'Média Geral',
                    'Média': round(sum(medias_estado) / len(medias_estado), 2)
                })
              # Liberar memória periodicamente
            config = self.mapping_manager.get_mappings().get('config_processamento', {})
            if (i+1) % config.get('tamanho_lote_estados', 5) == 0:
                release_memory()
        
        return resultados
    
    def _otimizar_tipos_dados(
        self,
        df: pd.DataFrame,
        estados: List[str],
        competencia_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """Otimiza tipos de dados do DataFrame."""
        areas_unicas = list(competencia_mapping.values()) + ['Média Geral']
        
        try:
            df['Área'] = pd.Categorical(df['Área'], categories=areas_unicas)
            df['Estado'] = pd.Categorical(df['Estado'], categories=estados)
            df['Média'] = df['Média'].astype('float32')
        except Exception as e:
            print(f"Erro ao otimizar tipos: {e}")
        
        return df
    
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
            
            # Agrupar por região e área
            df_agrupado = df_com_regiao.groupby(['Região', 'Área'])['Média'].mean().reset_index()
            df_agrupado = df_agrupado.rename(columns={'Região': 'Estado'})
            
            # Otimizar tipos
            regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
            df_agrupado['Estado'] = pd.Categorical(df_agrupado['Estado'], categories=regioes)
            
            return df_agrupado
        except Exception as e:
            print(f"Erro ao agrupar por região: {e}")
            return df


class ScatterAnalysisProcessor(CacheableProcessor):
    """
    Processador para análise de correlação em gráficos de dispersão.
      Especializado em filtrar e preparar dados para análises de correlação entre diferentes competências.
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        super().__init__(config, cache_key_prefix="scatter_analysis")
        self.mapping_manager = MappingManager()
        self.data_filter = DataFilter()

    def _process_internal(
        self,
        data: pd.DataFrame,
        eixo_x: str,
        eixo_y: str,
        filtro_sexo: Optional[str] = None,
        filtro_tipo_escola: Optional[str] = None,
        filtro_raca: Optional[str] = None,
        filtro_faixa_salarial: Optional[int] = None,
        excluir_notas_zero: bool = True,
        max_amostras: Optional[int] = None,
        **kwargs
    ) -> Tuple[pd.DataFrame, int]:
        """
        Processa dados para análise de dispersão.
        
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
        print("[DEBUG] === _process_internal ScatterAnalysisProcessor ===")
        print(f"[DEBUG] Data shape: {data.shape if data is not None else 'None'}")
        print(f"[DEBUG] Eixos: x={eixo_x}, y={eixo_y}")
        print(f"[DEBUG] Filtros: sexo={filtro_sexo}, escola={filtro_tipo_escola}, raca={filtro_raca}, faixa_salarial={filtro_faixa_salarial}")
        
        # Validar entrada
        if data.empty or eixo_x not in data.columns or eixo_y not in data.columns:
            print(f"[DEBUG] Dados inválidos: empty={data.empty}, eixo_x_existe={eixo_x in data.columns if not data.empty else False}, eixo_y_existe={eixo_y in data.columns if not data.empty else False}")
            return pd.DataFrame(), 0
        
        print("[DEBUG] Validação inicial passou")
        
        # Obter configurações
        mappings = self.mapping_manager.get_mappings()
        config = mappings.get('config_processamento', {})
        if max_amostras is None:
            max_amostras = config.get('max_amostras_scatter', 50000)
        
        print(f"[DEBUG] Max amostras: {max_amostras}")
        
        # Determinar colunas necessárias
        print("[DEBUG] Determinando colunas necessárias...")
        colunas_necessarias = self._determinar_colunas_necessarias(
            eixo_x, eixo_y, filtro_sexo, filtro_tipo_escola, 
            filtro_raca, filtro_faixa_salarial, data.columns
        )
        
        print(f"[DEBUG] Colunas necessárias: {colunas_necessarias}")
          # Criar cópia dos dados
        df = data[colunas_necessarias].copy()
        tamanho_inicial = len(df)
        
        print(f"[DEBUG] DataFrame copiado, tamanho inicial: {tamanho_inicial}")
        
        # Aplicar filtros
        print("[DEBUG] Aplicando filtros...")
        df = self._aplicar_filtros(
            df, eixo_x, eixo_y, filtro_sexo, filtro_tipo_escola,
            filtro_raca, filtro_faixa_salarial, excluir_notas_zero
        )
        
        print(f"[DEBUG] Após aplicar filtros: {len(df)} registros")
        
        # Remover valores NaN
        df = df.dropna(subset=[eixo_x, eixo_y])
        
        print(f"[DEBUG] Após remover NaN: {len(df)} registros")
        
        # Calcular registros removidos até aqui
        registros_removidos = tamanho_inicial - len(df)
        
        # Limitar amostras para performance
        if len(df) > max_amostras:
            df = df.sample(n=max_amostras, random_state=42)
            print(f"[DEBUG] Amostragem aplicada: {len(df)} registros")          
            registros_removidos = tamanho_inicial - len(df)
        
        print(f"[DEBUG] _process_internal concluído: {len(df)} registros finais, {registros_removidos} removidos")
        
        return df, registros_removidos
    
    def _determinar_colunas_necessarias(
        self,
        eixo_x: str,
        eixo_y: str,
        filtro_sexo: Optional[str],
        filtro_tipo_escola: Optional[str],
        filtro_raca: Optional[str],
        filtro_faixa_salarial: Optional[int],
        colunas_disponiveis: pd.Index
    ) -> List[str]:        
        """Determina quais colunas são necessárias."""
        print(f"[DEBUG] _determinar_colunas_necessarias chamada")
        print(f"[DEBUG] Filtros: sexo={filtro_sexo}, escola={filtro_tipo_escola}, raca={filtro_raca}, faixa_salarial={filtro_faixa_salarial}")
        print(f"[DEBUG] Colunas disponíveis: {list(colunas_disponiveis)}")
        
        colunas_necessarias = [eixo_x, eixo_y]
        print(f"[DEBUG] Colunas base: {colunas_necessarias}")
        
        filtros_colunas = [
            ('TP_SEXO', filtro_sexo),
            ('TP_DEPENDENCIA_ADM_ESC', filtro_tipo_escola),
            ('TP_COR_RACA', filtro_raca),
            ('TP_FAIXA_SALARIAL', filtro_faixa_salarial)
        ]
        
        for coluna, filtro in filtros_colunas:
            if filtro is not None and coluna in colunas_disponiveis:
                colunas_necessarias.append(coluna)
                print(f"[DEBUG] Adicionando coluna {coluna} por filtro {filtro}")
        
        # Sempre incluir TP_FAIXA_SALARIAL se disponível (para coloração do gráfico)
        if 'TP_FAIXA_SALARIAL' in colunas_disponiveis and 'TP_FAIXA_SALARIAL' not in colunas_necessarias:
            colunas_necessarias.append('TP_FAIXA_SALARIAL')
            print(f"[DEBUG] Adicionando TP_FAIXA_SALARIAL para coloração")
        elif 'TP_FAIXA_SALARIAL' in colunas_necessarias:
            print(f"[DEBUG] TP_FAIXA_SALARIAL já estava nas colunas necessárias")
        else:
            print(f"[DEBUG] TP_FAIXA_SALARIAL não disponível nas colunas")
            
        print(f"[DEBUG] Colunas necessárias finais: {colunas_necessarias}")
        return colunas_necessarias
    
    def _aplicar_filtros(
        self,
        df: pd.DataFrame,
        eixo_x: str,
        eixo_y: str,
        filtro_sexo: Optional[str],
        filtro_tipo_escola: Optional[str],
        filtro_raca: Optional[str],
        filtro_faixa_salarial: Optional[int],
        excluir_notas_zero: bool
    ) -> pd.DataFrame:
        """Aplica todos os filtros de uma vez usando método manual (mais robusto)."""
        print(f"[DEBUG] _aplicar_filtros - shape inicial: {df.shape}")
        print(f"[DEBUG] Filtros recebidos: sexo={filtro_sexo}, escola={filtro_tipo_escola}, raca={filtro_raca}, faixa_salarial={filtro_faixa_salarial}")
        print(f"[DEBUG] excluir_notas_zero: {excluir_notas_zero}")
        print(f"[DEBUG] Colunas disponíveis: {list(df.columns)}")
        
        df_filtrado = df.copy()
        
        # Filtros de notas válidas
        if excluir_notas_zero and len(df_filtrado) > 0:
            if eixo_x in df_filtrado.columns and eixo_y in df_filtrado.columns:
                antes = len(df_filtrado)
                df_filtrado = df_filtrado[(df_filtrado[eixo_x] > 0) & (df_filtrado[eixo_y] > 0)]
                print(f"[DEBUG] Filtro notas zero: {antes} -> {len(df_filtrado)} registros")
          # Filtros demográficos usando métodos manuais (mais robustos que query)
        # Verificar se DataFrame não está vazio antes de cada filtro
        if filtro_sexo and filtro_sexo != "Todos" and len(df_filtrado) > 0 and 'TP_SEXO' in df_filtrado.columns:
            antes = len(df_filtrado)
            print(f"[DEBUG] Valores únicos TP_SEXO: {df_filtrado['TP_SEXO'].unique()}")
            df_filtrado = df_filtrado[df_filtrado['TP_SEXO'] == filtro_sexo]
            print(f"[DEBUG] Filtro sexo ({filtro_sexo}): {antes} -> {len(df_filtrado)} registros")
        
        if filtro_tipo_escola and filtro_tipo_escola != "Todos" and len(df_filtrado) > 0 and 'TP_DEPENDENCIA_ADM_ESC' in df_filtrado.columns:
            antes = len(df_filtrado)
            print(f"[DEBUG] Valores únicos TP_DEPENDENCIA_ADM_ESC: {df_filtrado['TP_DEPENDENCIA_ADM_ESC'].unique()}")
            if filtro_tipo_escola == 'Pública':
                # Aceitar tanto strings quanto números para escolas públicas (códigos 1, 2, 3)
                df_filtrado = df_filtrado[df_filtrado['TP_DEPENDENCIA_ADM_ESC'].isin([1, 2, 3, '1', '2', '3', 1.0, 2.0, 3.0])]
            elif filtro_tipo_escola == 'Privada':
                # Aceitar tanto strings quanto números para escolas privadas (código 4)
                df_filtrado = df_filtrado[df_filtrado['TP_DEPENDENCIA_ADM_ESC'].isin([4, '4', 4.0])]
            print(f"[DEBUG] Filtro tipo escola ({filtro_tipo_escola}): {antes} -> {len(df_filtrado)} registros")
        
        if filtro_raca and len(df_filtrado) > 0 and 'TP_COR_RACA' in df_filtrado.columns:
            antes = len(df_filtrado)
            print(f"[DEBUG] Valores únicos TP_COR_RACA: {df_filtrado['TP_COR_RACA'].unique()}")
            df_filtrado = df_filtrado[df_filtrado['TP_COR_RACA'] == filtro_raca]
            print(f"[DEBUG] Filtro raça ({filtro_raca}): {antes} -> {len(df_filtrado)} registros")
        
        if filtro_faixa_salarial is not None and len(df_filtrado) > 0 and 'TP_FAIXA_SALARIAL' in df_filtrado.columns:
            antes = len(df_filtrado)
            print(f"[DEBUG] Valores únicos TP_FAIXA_SALARIAL: {df_filtrado['TP_FAIXA_SALARIAL'].unique()}")
            df_filtrado = df_filtrado[df_filtrado['TP_FAIXA_SALARIAL'] == filtro_faixa_salarial]
            print(f"[DEBUG] Filtro faixa salarial ({filtro_faixa_salarial}): {antes} -> {len(df_filtrado)} registros")
        
        print(f"[DEBUG] _aplicar_filtros - shape final: {df_filtrado.shape}")
        return df_filtrado
