import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
import gc
from typing import Dict, List, Any, Optional, Tuple, Union

# Imports para tooltips e métricas
from utils.tooltip import titulo_com_tooltip, custom_metric_with_tooltip

# Imports para gerenciamento de memória
from utils.helpers.cache_utils import release_memory, optimized_cache

# Imports para carregamento de dados
from utils.data_loader import load_data_for_tab, filter_data_by_states
from utils.mappings import get_mappings

# Imports para preparação de dados
from utils.prepara_dados import (
    preparar_dados_histograma,
    preparar_dados_grafico_faltas,
    preparar_dados_media_geral_estados,
    preparar_dados_comparativo_areas,
    preparar_dados_evasao
)

# Imports para visualizações
from utils.visualizacao import (
    criar_histograma,
    criar_grafico_faltas,
    criar_grafico_media_por_estado,
    criar_grafico_comparativo_areas,
    criar_grafico_evasao
)

# Imports para explicações
from utils.explicacao import (
    get_tooltip_metricas_principais,
    get_tooltip_histograma,
    get_tooltip_faltas,
    get_tooltip_media_geral,
    get_tooltip_total_candidatos,
    get_tooltip_maior_media,
    get_tooltip_menor_media,
    get_tooltip_estado_maior_media,
    get_tooltip_media_por_regiao,
    get_tooltip_comparativo_areas,
    get_tooltip_evasao,
    get_explicacao_histograma,
    get_explicacao_faltas,
    get_explicacao_media_estados,
    get_explicacao_comparativo_areas,
    get_explicacao_evasao
)

# Imports para análises estatísticas
from utils.estatisticas import (
    analisar_metricas_principais,
    analisar_distribuicao_notas,
    analisar_faltas,
    analisar_desempenho_por_faixa_nota,
    analisar_metricas_por_regiao
)

# Imports para expanders
from utils.expander import (
    criar_expander_analise_histograma,
    criar_expander_analise_faltas,
    criar_expander_analise_faixas_desempenho,
    criar_expander_analise_regional,
    criar_expander_analise_comparativo_areas
)

# Configuração da página
st.set_page_config(
    page_title="ENEM - Análise Geral",
    page_icon="🏠",
    layout="wide"
)

def clear_geral_cache():
    """Limpa cache específico da página Geral"""
    st.session_state.current_page = "geral"
    
    # Limpar cache de outras páginas se necessário
    if hasattr(st.session_state, 'last_page') and st.session_state.last_page != "geral":
        st.cache_data.clear()
        gc.collect()
    
    st.session_state.last_page = "geral"

def init_geral_session_state():
    """Inicializa session_state específico para página Geral"""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()
    
    if 'estados_selecionados' not in st.session_state:
        st.session_state.estados_selecionados = []
        st.warning("⚠️ Nenhum estado selecionado. Volte à página inicial para configurar os filtros.")
        st.stop()
    
    if 'locais_selecionados' not in st.session_state:
        st.session_state.locais_selecionados = []

def get_cached_data_geral(estados_selecionados: List[str]):
    """Carrega dados otimizados para a página Geral"""
    
    @st.cache_data(ttl=600, max_entries=2, show_spinner=False)
    def _load_geral_data(estados_key: str):
        """Cache interno para dados da página Geral"""
        return load_data_for_tab("geral")
    
    # Usar string dos estados como chave para cache
    estados_key = "_".join(sorted(estados_selecionados))
    return _load_geral_data(estados_key)

def convert_pandas_to_polars_safe(df_pandas: pd.DataFrame) -> pl.DataFrame:
    """Converte DataFrame Pandas para Polars com tratamento de erro"""
    try:
        return pl.from_pandas(df_pandas)
    except Exception as e:
        st.warning(f"Aviso na conversão para Polars: {str(e)}")
        return None

def optimize_memory_usage(microdados_estados: pd.DataFrame) -> pd.DataFrame:
    """Otimiza uso de memória do DataFrame usando Polars quando possível"""
    try:
        # Converter para Polars para otimizações
        df_polars = convert_pandas_to_polars_safe(microdados_estados)
        if df_polars is not None:
            # Otimizar tipos de dados
            for col in df_polars.columns:
                dtype = df_polars[col].dtype
                
                if dtype == pl.Int64:
                    max_val = df_polars[col].max()
                    min_val = df_polars[col].min()
                    
                    if max_val <= 127 and min_val >= -128:
                        df_polars = df_polars.with_columns(pl.col(col).cast(pl.Int8))
                    elif max_val <= 32767 and min_val >= -32768:
                        df_polars = df_polars.with_columns(pl.col(col).cast(pl.Int16))
                    elif max_val <= 2147483647 and min_val >= -2147483648:
                        df_polars = df_polars.with_columns(pl.col(col).cast(pl.Int32))
                
                elif dtype == pl.Float64:
                    df_polars = df_polars.with_columns(pl.col(col).cast(pl.Float32))
            
            # Converter de volta para pandas
            return df_polars.to_pandas()
        
        return microdados_estados
    except Exception as e:
        st.warning(f"Não foi possível otimizar memória: {str(e)}")
        return microdados_estados

def render_geral(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    locais_selecionados: List[str], 
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> None:
    """
    Renderiza a aba Geral do dashboard com métricas e visualizações interativas.
    MANTÉM FUNCIONALIDADE IDÊNTICA À VERSÃO ORIGINAL COM OTIMIZAÇÕES DE PERFORMANCE
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos filtrado por estados
    estados_selecionados : List[str]
        Lista com os estados selecionados para análise
    locais_selecionados : List[str]
        Lista de regiões/estados formatada para exibição
    colunas_notas : List[str]
        Lista com os nomes das colunas de notas
    competencia_mapping : Dict[str, str]
        Dicionário que mapeia códigos de competências para seus nomes
    """
    # Verificar se temos estados selecionados - IGUAL À ORIGINAL
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Otimizar dados na memória
    with st.spinner("Otimizando dados..."):
        microdados_estados = optimize_memory_usage(microdados_estados)
    
    # Mostrar mensagem sobre os filtros aplicados - IGUAL À ORIGINAL
    mensagem = f"Analisando Dados Gerais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Exibir métricas principais (sempre visíveis) - IGUAL À ORIGINAL
    metricas = exibir_metricas_principais(microdados_estados, estados_selecionados, colunas_notas)
    
    # Permitir ao usuário selecionar a análise desejada - IGUAL À ORIGINAL
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Distribuição de Notas", "Análise por Região/Estado", "Comparativo entre Áreas", "Análise de Faltas"],
        horizontal=True
    )
    
    # Exibir a visualização selecionada - IGUAL À ORIGINAL
    try:
        if analise_selecionada == "Distribuição de Notas":
            exibir_histograma_notas(microdados_estados, colunas_notas, competencia_mapping)
        elif analise_selecionada == "Análise por Região/Estado":
            exibir_analise_regional(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping)
        elif analise_selecionada == "Comparativo entre Áreas":
            exibir_comparativo_areas(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping)
        else:  # "Análise de Faltas"
            exibir_analise_faltas(microdados_estados, estados_selecionados)
    except Exception as e:
        st.error(f"Ocorreu um erro ao exibir a análise: {str(e)}")
        st.warning("Tente selecionar outra visualização ou verificar os filtros aplicados.")
    
    # Limpeza de memória otimizada
    release_memory(microdados_estados)

def exibir_metricas_principais(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    colunas_notas: List[str]
) -> Dict[str, Any]:
    """
    Calcula e exibe métricas principais em cards.
    MANTÉM FUNCIONALIDADE IDÊNTICA À VERSÃO ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : List[str]
        Lista com os estados selecionados para análise
    colunas_notas : List[str]
        Lista com os nomes das colunas de notas
        
    Retorna:
    --------
    Dict[str, Any]
        Métricas calculadas para uso em outras visualizações
    """
    # Título com tooltip explicativo - IGUAL À ORIGINAL
    titulo_com_tooltip("Métricas Principais", get_tooltip_metricas_principais(), "metricas_tooltip")
    
    # Calcular métricas principais com spinner para indicar processamento - IGUAL À ORIGINAL
    with st.spinner("Calculando métricas principais..."):
        metricas = analisar_metricas_principais(microdados_estados, estados_selecionados, colunas_notas)
    
    # Função para formatar números com vírgula como separador decimal - IGUAL À ORIGINAL
    def formatar_numero_br(valor: float, casas_decimais: int = 2) -> str:
        formatado = f"{valor:,.{casas_decimais}f}"
        return formatado.replace(',', 'X').replace('.', ',').replace('X', '.')

    # Exibir as métricas em cards usando custom_metric_with_tooltip - IGUAL À ORIGINAL
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        custom_metric_with_tooltip(
            label="Candidatos Inscritos",
            value=f"{metricas['total_candidatos']:,}".replace(',', '.'),
            explicacao=get_tooltip_total_candidatos(),
            key="metrica_candidatos"
        )
    
    with col2:
        custom_metric_with_tooltip(
            label="Média Geral",
            value=formatar_numero_br(metricas['media_geral']),
            explicacao=get_tooltip_media_geral(),
            key="metrica_media_geral"
        )
        
    with col3:
        # Formatar maior média com o estado entre parênteses - IGUAL À ORIGINAL
        custom_metric_with_tooltip(
            label="Maior Média",
            value=f"{formatar_numero_br(metricas['valor_maior_media_estado'])} ({metricas['estado_maior_media']})",
            explicacao=get_tooltip_maior_media(),
            key="metrica_maior_media"
        )
    
    with col4:
        # Menor média com o estado entre parênteses - IGUAL À ORIGINAL
        custom_metric_with_tooltip(
            label="Menor Média",
            value=f"{formatar_numero_br(metricas['valor_menor_media_estado'])} ({metricas['estado_menor_media']})",
            explicacao=get_tooltip_menor_media(),
            key="metrica_menor_media",
        )
                
    return metricas

def exibir_histograma_notas(
    microdados_estados: pd.DataFrame, 
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> None:
    """
    Exibe um histograma interativo da distribuição de notas com análise estatística.
    MANTÉM FUNCIONALIDADE IDÊNTICA À VERSÃO ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    colunas_notas : List[str]
        Lista com os nomes das colunas de notas
    competencia_mapping : Dict[str, str]
        Dicionário que mapeia códigos de competências para seus nomes
    """
    try:
        # Título com tooltip explicativo - IGUAL À ORIGINAL
        titulo_com_tooltip("Histograma das Notas", get_tooltip_histograma(), "hist_tooltip")
        
        # Seleção da área de conhecimento - IGUAL À ORIGINAL
        area_conhecimento = st.selectbox(
            "Selecione a área de conhecimento ou redação:",
            options=colunas_notas,
            format_func=lambda x: competencia_mapping[x],
            key="selectbox_area_histograma"
        )
        
        # Preparar dados para o histograma - IGUAL À ORIGINAL
        with st.spinner("Processando dados para o histograma..."):
            df_valido, coluna_hist, nome_area_hist = preparar_dados_histograma(
                microdados_estados, 
                area_conhecimento, 
                competencia_mapping
            )
            
            # Verificar se temos dados válidos - IGUAL À ORIGINAL
            if df_valido.empty:
                st.warning(f"Não há dados válidos para {nome_area_hist} com os filtros aplicados.")
                return
                
            # Calcular estatísticas para a coluna selecionada - IGUAL À ORIGINAL
            estatisticas = analisar_distribuicao_notas(df_valido, coluna_hist)
        
        # Criar e exibir o histograma - IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            fig_hist = criar_histograma(
                df_valido,
                coluna_hist,
                nome_area_hist,
                estatisticas
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Liberar memória do gráfico - OTIMIZADO
            release_memory(fig_hist)
        
        # Exibir explicação contextualizada do histograma - IGUAL À ORIGINAL
        explicacao = get_explicacao_histograma(
            nome_area_hist,
            estatisticas['media'],
            estatisticas['mediana'],
            estatisticas['assimetria'],
            estatisticas['curtose']
        )
        st.info(explicacao)
        
        # Adicionar expanders com análises detalhadas - IGUAL À ORIGINAL
        criar_expander_analise_histograma(df_valido, coluna_hist, nome_area_hist, estatisticas)
        criar_expander_analise_faixas_desempenho(df_valido, coluna_hist, nome_area_hist)
        
        # Liberar memória - OTIMIZADO
        release_memory([df_valido, estatisticas])
        
    except Exception as e:
        st.error(f"Erro ao exibir histograma: {str(e)}")
        st.warning("Verifique se há dados válidos para a área de conhecimento selecionada.")

def exibir_analise_faltas(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str]
) -> None:
    """
    Exibe análise de faltas por estado e dia de prova com gráficos interativos.
    MANTÉM FUNCIONALIDADE IDÊNTICA À VERSÃO ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : List[str]
        Lista com os estados selecionados para análise
    """
    try:
        # Definir mapeamento das colunas de presença - IGUAL À ORIGINAL
        colunas_presenca = {
            'TP_PRESENCA_CN': 'Ciências da Natureza',
            'TP_PRESENCA_CH': 'Ciências Humanas',
            'TP_PRESENCA_LC': 'Linguagens e Códigos',
            'TP_PRESENCA_MT': 'Matemática',
            'TP_PRESENCA_REDACAO': 'Redação'
        }
        
        # Título com tooltip - IGUAL À ORIGINAL
        titulo_com_tooltip("Análise de Faltas por Dia de Prova", get_tooltip_faltas(), "faltas_tooltip")
        
        # Preparar dados para o gráfico de faltas - IGUAL À ORIGINAL
        with st.spinner("Processando dados para análise de faltas..."):
            df_faltas = preparar_dados_grafico_faltas(microdados_estados, estados_selecionados, colunas_presenca)
            
            if df_faltas.empty:
                st.warning("Não há dados suficientes para análise de faltas com os filtros aplicados.")
                return
            
            # Calcular análise completa das faltas (uma vez só) - IGUAL À ORIGINAL
            analise_faltas_dados = analisar_faltas(df_faltas)
        
        # Controles de interface para personalização do gráfico - IGUAL À ORIGINAL
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            ordenar_por_faltas = st.checkbox(
                "Ordenar estados por % de faltas", 
                value=False,
                key="checkbox_ordenar_faltas"
            )
        
        # Tipo de falta para ordenação - IGUAL À ORIGINAL
        tipo_selecionado = None
        if ordenar_por_faltas:
            with col2:
                tipos_disponiveis = df_faltas['Tipo de Falta'].unique().tolist()
                # Remover tipos inválidos - IGUAL À ORIGINAL
                tipos_disponiveis = [tipo for tipo in tipos_disponiveis if "Total de faltas" not in tipo]
                tipo_selecionado = st.selectbox(
                    "Ordenar por tipo de falta:",
                    options=tipos_disponiveis,
                    key="selectbox_tipo_falta"
                )
        
        # Opção para filtrar apenas um tipo de falta - IGUAL À ORIGINAL
        filtrar_tipo = False
        if ordenar_por_faltas and tipo_selecionado:
            with col3:
                filtrar_tipo = st.checkbox(
                    "Mostrar apenas este tipo de falta", 
                    value=False,
                    key="checkbox_filtrar_tipo"
                )
        
        # Criar visualização do gráfico de faltas - IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_faltas(
                df_faltas, 
                order_by_area=tipo_selecionado if ordenar_por_faltas else None,
                order_ascending=False,
                filtro_area=tipo_selecionado if (filtrar_tipo) else None
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Liberar memória do gráfico - OTIMIZADO
            release_memory(fig)
        
        # Extrair dados para explicação - IGUAL À ORIGINAL
        taxa_media_geral = analise_faltas_dados['taxa_media_geral']
        tipo_mais_comum = analise_faltas_dados['tipo_mais_comum']
        
        # Extrair estados com maior e menor faltas - IGUAL À ORIGINAL
        estado_maior_falta = "N/A"
        if analise_faltas_dados['estado_maior_falta'] is not None:
            estado_maior_falta = analise_faltas_dados['estado_maior_falta']['Estado']
        
        estado_menor_falta = "N/A"
        if analise_faltas_dados['estado_menor_falta'] is not None:
            estado_menor_falta = analise_faltas_dados['estado_menor_falta']['Estado']
        
        # Exibir explicação contextualizada - IGUAL À ORIGINAL
        explicacao = get_explicacao_faltas(
            taxa_media_geral,
            tipo_mais_comum,
            estado_maior_falta,
            estado_menor_falta
        )
        st.info(explicacao)
        
        # Adicionar expander com análise detalhada - IGUAL À ORIGINAL
        criar_expander_analise_faltas(df_faltas, analise_faltas_dados)
        
        # Opção para visualizar evasão por tipo de presença - IGUAL À ORIGINAL
        if st.checkbox("Visualizar análise detalhada de evasão por tipo de presença", key="checkbox_evasao"):
            exibir_analise_evasao(microdados_estados, estados_selecionados)
        
        # Liberar memória - OTIMIZADO
        release_memory([df_faltas, analise_faltas_dados])
        
    except Exception as e:
        st.error(f"Erro ao exibir análise de faltas: {str(e)}")
        st.warning("Verifique se os dados de presença estão disponíveis para os estados selecionados.")

def exibir_analise_regional(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str],
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> None:
    """
    Exibe análise de médias por estado ou região do Brasil.
    MANTÉM FUNCIONALIDADE IDÊNTICA À VERSÃO ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : List[str]
        Lista com os estados selecionados para análise
    colunas_notas : List[str]
        Lista com os nomes das colunas de notas
    competencia_mapping : Dict[str, str]
        Dicionário que mapeia códigos de competências para seus nomes
    """
    try:
        # Título com tooltip - IGUAL À ORIGINAL
        titulo_com_tooltip("Médias por Estado/Região", get_tooltip_media_por_regiao(), "media_regional_tooltip")
        
        # Opção para agrupar por região - IGUAL À ORIGINAL
        agrupar_por_regiao = st.checkbox(
            "Agrupar por região", 
            value=False,
            help="Agrupa os estados por região geográfica do Brasil",
            key="checkbox_agrupar_regiao"
        )
        
        # Opções de destaque - IGUAL À ORIGINAL
        col1, col2 = st.columns(2)
        with col1:
            destacar_maior = st.checkbox(
                "Destacar maior média", 
                value=True,
                key="checkbox_destacar_maior"
            )
        with col2:
            destacar_menor = st.checkbox(
                "Destacar menor média", 
                value=True,
                key="checkbox_destacar_menor"
            )
        
        # Preparar dados para o gráfico - IGUAL À ORIGINAL
        with st.spinner("Processando dados para análise regional..."):
            df_medias = preparar_dados_media_geral_estados(
                microdados_estados, 
                estados_selecionados, 
                colunas_notas, 
                agrupar_por_regiao
            )
            
            if df_medias.empty:
                st.warning("Não há dados suficientes para análise regional com os filtros aplicados.")
                return
        
        # Criar visualização do gráfico de médias por estado/região - IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_media_por_estado(
                df_medias, 
                colunas_notas, 
                competencia_mapping,
                por_regiao=agrupar_por_regiao,
                destacar_maior=destacar_maior,
                destacar_menor=destacar_menor
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Liberar memória do gráfico - OTIMIZADO
            release_memory(fig)
        
        # Preparar dados para explicação - IGUAL À ORIGINAL
        tipo_localidade = "região" if agrupar_por_regiao else "estado"
        maior_local = df_medias.sort_values('Média Geral', ascending=False).iloc[0]['Local']
        maior_valor = df_medias.sort_values('Média Geral', ascending=False).iloc[0]['Média Geral']
        menor_local = df_medias.sort_values('Média Geral', ascending=True).iloc[0]['Local']
        menor_valor = df_medias.sort_values('Média Geral', ascending=True).iloc[0]['Média Geral']
        
        # Calcular diferença percentual - IGUAL À ORIGINAL
        if menor_valor > 0:
            diferenca_percentual = ((maior_valor - menor_valor) / menor_valor) * 100
        else:
            diferenca_percentual = 0
        
        media_geral = df_medias['Média Geral'].mean()
        
        # Exibir explicação contextualizada - IGUAL À ORIGINAL
        explicacao = get_explicacao_media_estados(
            media_geral,
            maior_local,
            maior_valor,
            menor_local,
            menor_valor,
            diferenca_percentual,
            agrupar_por_regiao
        )
        st.info(explicacao)
        
        # Adicionar expander com análise detalhada por região - IGUAL À ORIGINAL
        criar_expander_analise_regional(microdados_estados, colunas_notas, competencia_mapping)
        
        # Liberar memória - OTIMIZADO
        release_memory(df_medias)
        
    except Exception as e:
        st.error(f"Erro ao exibir análise regional: {str(e)}")
        st.warning("Verifique se há dados válidos para os estados selecionados.")

def exibir_comparativo_areas(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str],
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> None:
    """
    Exibe comparativo entre áreas de conhecimento.
    MANTÉM FUNCIONALIDADE IDÊNTICA À VERSÃO ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : List[str]
        Lista com os estados selecionados para análise
    colunas_notas : List[str]
        Lista com os nomes das colunas de notas
    competencia_mapping : Dict[str, str]
        Dicionário que mapeia códigos de competências para seus nomes
    """
    try:
        # Título com tooltip - IGUAL À ORIGINAL
        titulo_com_tooltip("Comparativo entre Áreas de Conhecimento", get_tooltip_comparativo_areas(), "comparativo_areas_tooltip")
        
        # Opções de visualização - IGUAL À ORIGINAL
        col1, col2 = st.columns(2)
        with col1:
            tipo_grafico = st.selectbox(
                "Tipo de visualização:",
                options=["barras", "radar", "linha"],
                format_func=lambda x: x.capitalize(),
                key="selectbox_tipo_grafico_areas"
            )
        with col2:
            mostrar_dispersao = st.checkbox(
                "Mostrar dispersão (desvio padrão)", 
                value=True,
                key="checkbox_mostrar_dispersao"
            )
        
        # Preparar dados para o gráfico - IGUAL À ORIGINAL
        with st.spinner("Processando dados para comparativo entre áreas..."):
            df_areas = preparar_dados_comparativo_areas(
                microdados_estados,
                estados_selecionados,
                colunas_notas,
                competencia_mapping
            )
            
            if df_areas.empty:
                st.warning("Não há dados suficientes para comparativo entre áreas com os filtros aplicados.")
                return
        
        # Criar visualização do gráfico comparativo - IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_comparativo_areas(
                df_areas, 
                tipo_grafico=tipo_grafico, 
                mostrar_dispersao=mostrar_dispersao
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Liberar memória do gráfico - OTIMIZADO
            release_memory(fig)
        
        # Identificar áreas com melhor e pior desempenho - IGUAL À ORIGINAL
        df_sorted = df_areas.sort_values('Media', ascending=False)
        melhor_area = df_sorted.iloc[0]['Area']
        melhor_media = df_sorted.iloc[0]['Media']
        pior_area = df_sorted.iloc[-1]['Area']
        pior_media = df_sorted.iloc[-1]['Media']
        
        # Identificar áreas com maior e menor variabilidade - IGUAL À ORIGINAL
        if 'DesvioPadrao' in df_areas.columns:
            maior_variabilidade = df_areas.sort_values('DesvioPadrao', ascending=False).iloc[0]['Area']
            menor_variabilidade = df_areas.sort_values('DesvioPadrao', ascending=True).iloc[0]['Area']
        else:
            maior_variabilidade = "Não disponível"
            menor_variabilidade = "Não disponível"
        
        # Exibir explicação contextualizada - IGUAL À ORIGINAL
        explicacao = get_explicacao_comparativo_areas(
            melhor_area,
            melhor_media,
            pior_area,
            pior_media,
            maior_variabilidade,
            menor_variabilidade
        )
        st.info(explicacao)
        
        # Adicionar expander com análise detalhada - IGUAL À ORIGINAL
        criar_expander_analise_comparativo_areas(df_areas)
        
        # Liberar memória - OTIMIZADO
        release_memory(df_areas)
        
    except Exception as e:
        st.error(f"Erro ao exibir comparativo entre áreas: {str(e)}")
        st.warning("Verifique se há dados válidos para as áreas de conhecimento nos estados selecionados.")

def exibir_analise_evasao(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str]
) -> None:
    """
    Exibe análise de evasão (presença/ausência) por estado.
    MANTÉM FUNCIONALIDADE IDÊNTICA À VERSÃO ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : List[str]
        Lista com os estados selecionados para análise
    """
    try:
        # Título com tooltip - IGUAL À ORIGINAL
        titulo_com_tooltip("Análise de Evasão por Estado", get_tooltip_evasao(), "evasao_tooltip")
        
        # Opções de visualização - IGUAL À ORIGINAL
        col1, col2 = st.columns(2)
        with col1:
            tipo_grafico = st.selectbox(
                "Tipo de visualização:",
                options=["barras", "mapa_calor", "pizza"],
                format_func=lambda x: "Barras" if x == "barras" else "Mapa de Calor" if x == "mapa_calor" else "Pizza",
                key="selectbox_tipo_grafico_evasao"
            )
        
        # Opções de ordenação - IGUAL À ORIGINAL
        metrica_ordenacao = None
        if tipo_grafico in ["barras", "mapa_calor"]:
            with col2:
                ordenar = st.checkbox(
                    "Ordenar estados", 
                    value=False,
                    key="checkbox_ordenar_evasao"
                )
                
                if ordenar:
                    metricas_opcoes = ["Presentes", "Faltantes Dia 1", "Faltantes Dia 2", "Faltantes Ambos"]
                    metrica_ordenacao = st.selectbox(
                        "Ordenar por:",
                        options=metricas_opcoes,
                        key="selectbox_metrica_ordenacao"
                    )
        
        # Preparar dados para o gráfico - IGUAL À ORIGINAL
        with st.spinner("Processando dados para análise de evasão..."):
            df_evasao = preparar_dados_evasao(microdados_estados, estados_selecionados)
            
            if df_evasao.empty:
                st.warning("Não há dados suficientes para análise de evasão com os filtros aplicados.")
                return
        
        # Criar visualização do gráfico de evasão - IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_evasao(
                df_evasao, 
                tipo_grafico=tipo_grafico,
                ordenar_por=metrica_ordenacao,
                ordem_crescente=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Liberar memória do gráfico - OTIMIZADO
            release_memory(fig)
        
        # Calcular métricas para explicação - IGUAL À ORIGINAL
        taxa_media_presenca = df_evasao[df_evasao['Métrica'] == 'Presentes']['Valor'].mean()
        taxa_media_ausencia_total = df_evasao[df_evasao['Métrica'] == 'Faltantes Ambos']['Valor'].mean()
        
        # Estados com maior e menor presença - IGUAL À ORIGINAL
        maior_presenca_df = df_evasao[df_evasao['Métrica'] == 'Presentes'].sort_values('Valor', ascending=False)
        menor_presenca_df = df_evasao[df_evasao['Métrica'] == 'Presentes'].sort_values('Valor', ascending=True)
        
        estado_maior_presenca = maior_presenca_df.iloc[0]['Estado'] if not maior_presenca_df.empty else "N/A"
        estado_menor_presenca = menor_presenca_df.iloc[0]['Estado'] if not menor_presenca_df.empty else "N/A"
        
        # Diferença entre dias - IGUAL À ORIGINAL
        media_dia1 = df_evasao[df_evasao['Métrica'] == 'Faltantes Dia 1']['Valor'].mean()
        media_dia2 = df_evasao[df_evasao['Métrica'] == 'Faltantes Dia 2']['Valor'].mean()
        diferenca_dia1_dia2 = media_dia2 - media_dia1
        
        # Exibir explicação contextualizada - IGUAL À ORIGINAL
        explicacao = get_explicacao_evasao(
            taxa_media_presenca,
            taxa_media_ausencia_total,
            estado_maior_presenca,
            estado_menor_presenca,
            diferenca_dia1_dia2
        )
        st.info(explicacao)
        
        # Liberar memória - OTIMIZADO
        release_memory(df_evasao)
        
    except Exception as e:
        st.error(f"Erro ao exibir análise de evasão: {str(e)}")
        st.warning("Verifique se os dados de presença estão disponíveis para os estados selecionados.")

# ===================== MAIN - EXECUÇÃO DA PÁGINA =====================

def main():
    """Função principal da página Geral"""
    
    # Limpeza de cache
    clear_geral_cache()
    
    # Inicializar session state
    init_geral_session_state()
    
    # Título da página
    st.title("🏠 Análise Geral - ENEM 2023")
    
    # Obter dados do session state
    estados_selecionados = st.session_state.estados_selecionados
    locais_selecionados = st.session_state.locais_selecionados
    mappings = st.session_state.mappings
    
    # Extrair mapeamentos necessários
    colunas_notas = mappings['colunas_notas']
    competencia_mapping = mappings['competencia_mapping']
    
    try:
        # Carregar dados para estados selecionados
        with st.spinner("Carregando dados da análise geral..."):
            microdados_completos = get_cached_data_geral(estados_selecionados)
            
            # Filtrar dados pelos estados selecionados
            microdados_estados = filter_data_by_states(microdados_completos, estados_selecionados)
        
        if microdados_estados.empty:
            st.error("❌ Nenhum dado encontrado para os estados selecionados.")
            return
        
        # Renderizar análise geral (MANTÉM FUNCIONALIDADE ORIGINAL)
        render_geral(
            microdados_estados, 
            estados_selecionados, 
            locais_selecionados, 
            colunas_notas, 
            competencia_mapping
        )
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.info("💡 Tente recarregar a página ou verifique se os dados estão disponíveis.")
    
    finally:
        # Limpeza final de memória
        if 'microdados_completos' in locals():
            release_memory(microdados_completos)
        if 'microdados_estados' in locals():
            release_memory(microdados_estados)
        gc.collect()

# Executar página
if __name__ == "__main__":
    main()