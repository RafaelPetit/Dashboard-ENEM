import streamlit as st
import pandas as pd
import numpy as np
import gc
from typing import Dict, List, Any, Optional, Union, Tuple

from utils.helpers.sidebar_filter import render_sidebar_filters

# Imports para tooltips e métricas
from utils.tooltip import titulo_com_tooltip

# Imports para gerenciamento de memória
from utils.helpers.cache_utils import release_memory, optimized_cache

# Imports para carregamento de dados
from utils.data_loader import load_data_for_tab, filter_data_by_states
from utils.mappings import get_mappings

# Imports para preparação de dados
from utils.prepara_dados import (
    preparar_dados_comparativo, 
    obter_ordem_categorias,
    preparar_dados_grafico_linha,
    preparar_dados_desempenho_geral,
    filtrar_dados_scatter,
    preparar_dados_grafico_linha_desempenho
)

# Imports para visualizações
from utils.visualizacao import (
    criar_grafico_comparativo_barras,
    criar_grafico_linha_desempenho,
    criar_grafico_scatter,
    criar_grafico_linha_estados,
    criar_filtros_comparativo,
    criar_filtros_dispersao,
    criar_filtros_estados
)

# Imports para estatísticas
from utils.estatisticas import (
    calcular_correlacao_competencias,
    gerar_estatisticas_descritivas,
    analisar_desempenho_por_estado,
    calcular_estatisticas_comparativas
)

# Imports para explicações
from utils.explicacao import (
    get_tooltip_analise_comparativa,
    get_tooltip_relacao_competencias,
    get_tooltip_desempenho_estados,
    get_explicacao_barras_comparativo,
    get_explicacao_linhas_comparativo,
    get_explicacao_dispersao,
    get_explicacao_desempenho_estados
)

# Imports para expanders
from utils.expander.expander_desempenho import (
    criar_expander_analise_comparativa,
    criar_expander_relacao_competencias,
    criar_expander_desempenho_estados
)

# Configuração da página
st.set_page_config(
    page_title="ENEM - Análise de Desempenho",
    page_icon="📊",
    layout="wide"
)

pd.options.display.float_format = '{:,.2f}'.format

def clear_desempenho_cache():
    """Limpa cache específico da página Desempenho"""
    st.session_state.current_page = "desempenho"
    
    # Limpar cache de outras páginas se necessário
    if hasattr(st.session_state, 'last_page') and st.session_state.last_page != "desempenho":
        st.cache_data.clear()
        gc.collect()
    
    st.session_state.last_page = "desempenho"

def init_desempenho_session_state():
    """Inicializa session_state específico para página Desempenho"""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()
    
    if 'estados_selecionados' not in st.session_state:
        st.session_state.estados_selecionados = []
        st.warning("⚠️ Nenhum estado selecionado. Volte à página inicial para configurar os filtros.")
        st.stop()
    
    if 'locais_selecionados' not in st.session_state:
        st.session_state.locais_selecionados = []

def get_cached_data_desempenho(estados_selecionados: List[str]):
    """Carrega dados otimizados para a página Desempenho"""
    
    @st.cache_data(ttl=600, max_entries=2, show_spinner=False)
    def _load_desempenho_data(estados_key: str):
        """Cache interno para dados da página Desempenho - carrega múltiplas fontes"""
        try:
            # Carregar dados principais de desempenho
            dados_desempenho = load_data_for_tab("desempenho")
            
            # Para análise comparativa que precisa de mais variáveis, carregar dados de aspectos sociais
            dados_aspectos = load_data_for_tab("aspectos_sociais")
            
            # Verificar se precisamos combinar dados
            # Se desempenho não tem todas as colunas necessárias, tentar merge
            colunas_demograficas_extras = ['TP_ESCOLA', 'TP_ESTADO_CIVIL', 'TP_ENSINO']
            colunas_extras_disponiveis = [col for col in colunas_demograficas_extras 
                                        if col in dados_aspectos.columns and col not in dados_desempenho.columns]
            
            if colunas_extras_disponiveis and not dados_aspectos.empty:
                # Fazer merge para obter colunas extras (se possível)
                colunas_merge = ['SG_UF_PROVA', 'TP_SEXO', 'TP_COR_RACA'] + colunas_extras_disponiveis
                colunas_merge_disponiveis = [col for col in colunas_merge if col in dados_aspectos.columns]
                
                if len(colunas_merge_disponiveis) >= 3:  # Pelo menos 3 colunas para merge seguro
                    try:
                        dados_aspectos_limitados = dados_aspectos[colunas_merge_disponiveis].drop_duplicates()
                        dados_combinados = dados_desempenho.merge(
                            dados_aspectos_limitados, 
                            on=['SG_UF_PROVA', 'TP_SEXO', 'TP_COR_RACA'], 
                            how='left'
                        )
                        print(f"✅ Dados combinados: {len(dados_combinados)} registros com {len(colunas_extras_disponiveis)} colunas extras")
                        return dados_combinados
                    except Exception as e:
                        print(f"⚠️ Erro ao combinar dados, usando apenas desempenho: {e}")
            
            return dados_desempenho
            
        except Exception as e:
            print(f"Erro ao carregar dados de desempenho: {e}")
            return pd.DataFrame()
    
    # Usar string dos estados como chave para cache
    estados_key = "_".join(sorted(estados_selecionados))
    return _load_desempenho_data(estados_key)

def optimize_memory_usage(microdados_estados: pd.DataFrame) -> pd.DataFrame:
    """
    Otimização de memória usando APENAS pandas - versão ultra-segura
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame original a ser otimizado
        
    Retorna:
    --------
    DataFrame: DataFrame com tipos otimizados
    """
    try:
        # Verificação básica
        if microdados_estados is None or microdados_estados.empty:
            return microdados_estados
        
        # Criar cópia para não modificar o original
        df_optimized = microdados_estados.copy()
        
        # Otimizações seguras coluna por coluna
        for col in df_optimized.columns:
            try:
                dtype_original = df_optimized[col].dtype
                
                # Otimizar colunas categóricas (object)
                if dtype_original == 'object':
                    # Verificar se vale a pena converter para category
                    unique_ratio = len(df_optimized[col].unique()) / len(df_optimized)
                    if unique_ratio < 0.5:  # Se menos de 50% valores únicos
                        df_optimized[col] = df_optimized[col].astype('category')
                
                # Otimizar inteiros
                elif dtype_original in ['int64', 'Int64']:
                    # Verificar se temos valores válidos
                    if not df_optimized[col].isna().all():
                        max_val = df_optimized[col].max()
                        min_val = df_optimized[col].min()
                        
                        if pd.notna(max_val) and pd.notna(min_val):
                            # Escolher tipo menor possível
                            if max_val <= 127 and min_val >= -128:
                                df_optimized[col] = df_optimized[col].astype('int8')
                            elif max_val <= 32767 and min_val >= -32768:
                                df_optimized[col] = df_optimized[col].astype('int16')
                            elif max_val <= 2147483647 and min_val >= -2147483648:
                                df_optimized[col] = df_optimized[col].astype('int32')
                
                # Otimizar floats
                elif dtype_original == 'float64':
                    # Usar downcast do pandas (mais seguro)
                    df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
                    
            except Exception as col_error:
                # Se erro em coluna específica, manter tipo original
                continue
        
        return df_optimized
        
    except Exception as e:
        # Se qualquer erro geral, retornar DataFrame original
        return microdados_estados

def exibir_secao_visualizacao(titulo, tooltip_text, tooltip_id, processar_func, exibir_func, explicacao_func, expander_func=None, **kwargs):
    """
    Função auxiliar para exibir uma seção de visualização padronizada com spinner, explicação e expander opcional.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL - tabs/desempenho.py
    
    Parâmetros:
    -----------
    titulo : str
        Título da seção
    tooltip_text : str 
        Texto do tooltip
    tooltip_id : str
        ID do tooltip
    processar_func : function
        Função para processamento de dados
    exibir_func : function
        Função para exibir visualização
    explicacao_func : function
        Função para obter o texto de explicação
    expander_func : function, opcional
        Função para criar o expander com análise detalhada
    kwargs : dict
        Argumentos adicionais para as funções
    """
    titulo_com_tooltip(titulo, tooltip_text, tooltip_id)
    
    with st.spinner("Processando dados..."):
        dados_processados = processar_func(**kwargs)
    
    with st.spinner("Gerando visualização..."):
        fig = exibir_func(dados_processados, **kwargs)
        st.plotly_chart(fig, use_container_width=True)
    
    explicacao = explicacao_func(**kwargs)
    st.info(explicacao)
    
    if expander_func:
        expander_func(dados_processados, **kwargs)
    
    # Limpeza de memória otimizada (OTIMIZAÇÃO ADICIONADA)
    release_memory([dados_processados, fig])

def render_desempenho(microdados, microdados_estados, estados_selecionados, 
                     locais_selecionados, colunas_notas, competencia_mapping, race_mapping, 
                     variaveis_categoricas, desempenho_mapping):
    """
    Renderiza a aba de Desempenho com diferentes análises baseadas na seleção do usuário.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL - tabs/desempenho.py
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com dados originais
    microdados_estados : DataFrame
        DataFrame com dados filtrados por estado
    estados_selecionados : list
        Lista de estados selecionados pelo usuário
    locais_selecionados : list
        Lista de nomes de locais selecionados
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
    race_mapping : dict
        Mapeamento de códigos para raça/cor
    variaveis_categoricas : dict
        Dicionário com metadados das variáveis categóricas
    desempenho_mapping : dict
        Mapeamento de códigos para categorias de desempenho
    """
    # Verificar se existem estados selecionados - EXATAMENTE IGUAL À ORIGINAL
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Otimizar dados na memória (ÚNICA ADIÇÃO)
    with st.spinner("Otimizando dados..."):
        microdados_estados = optimize_memory_usage(microdados_estados)
    
    # Mensagem informativa sobre filtros aplicados - EXATAMENTE IGUAL À ORIGINAL
    mensagem = f"Analisando Desempenho para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Usamos um placeholder para microdados_full que só será carregado se necessário - EXATAMENTE IGUAL À ORIGINAL
    microdados_full = None
    
    # Permitir ao usuário selecionar a análise desejada - EXATAMENTE IGUAL À ORIGINAL
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Análise Comparativa", "Relação entre Competências", "Médias por Estado"],
        horizontal=True
    )
    
    # Direcionar para a análise selecionada - EXATAMENTE IGUAL À ORIGINAL
    try:
        if analise_selecionada == "Análise Comparativa":
            # Carrega microdados_full apenas quando necessário - EXATAMENTE IGUAL À ORIGINAL
            with st.spinner("Preparando dados para análise comparativa..."):
                microdados_full = preparar_dados_desempenho_geral(microdados_estados, colunas_notas, desempenho_mapping)
            render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping)
            release_memory(microdados_full)  # Libera memória após uso - EXATAMENTE IGUAL À ORIGINAL
        elif analise_selecionada == "Relação entre Competências":
            render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping)
        else:
            render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping)
    except Exception as e:
        st.error(f"Ocorreu um erro ao exibir a análise: {str(e)}")
        st.warning("Tente selecionar outra visualização ou verificar os filtros aplicados.")
    
    # Limpeza de memória otimizada (ÚNICA ADIÇÃO)
    release_memory(microdados_estados)

def render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping):
    """
    Renderiza a análise comparativa de desempenho por variável demográfica.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    
    Parâmetros:
    -----------
    microdados_full : DataFrame
        DataFrame com dados preparados
    variaveis_categoricas : dict
        Dicionário com metadados das variáveis categóricas
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
    """
    titulo_com_tooltip(
        "Análise Comparativa do Desempenho por Variáveis Demográficas", 
        get_tooltip_analise_comparativa(), 
        "comparativo_desempenho_tooltip"
    )
    
    # Seleção da variável para análise - EXATAMENTE IGUAL À ORIGINAL
    variavel_selecionada = st.selectbox(
        "Selecione a variável para análise:",
        options=list(variaveis_categoricas.keys()),
        format_func=lambda x: variaveis_categoricas[x]["nome"]
    )

    # Verificação mais robusta com feedback detalhado - EXATAMENTE IGUAL À ORIGINAL
    if variavel_selecionada not in microdados_full.columns:
        colunas_disponiveis = ", ".join(microdados_full.columns.tolist())
        st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} (código: {variavel_selecionada}) não está disponível no conjunto de dados.")
        st.info(f"Você pode verificar se esta variável está presente nos dados originais ou se o nome da coluna está correto no mapeamento.")
        return
    
    # Processamento dos dados em um único bloco para evitar redundâncias - EXATAMENTE IGUAL À ORIGINAL
    with st.spinner("Processando dados para análise comparativa..."):
        df_resultados = preparar_dados_comparativo(
            microdados_full, 
            variavel_selecionada, 
            variaveis_categoricas, 
            colunas_notas, 
            competencia_mapping
        )
    
    # Configuração dos filtros - EXATAMENTE IGUAL À ORIGINAL
    config_filtros = criar_filtros_comparativo(df_resultados, variaveis_categoricas, variavel_selecionada)
    
    # Preparação dos dados para visualização - EXATAMENTE IGUAL À ORIGINAL
    competencia_para_filtro = config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None
    df_visualizacao = preparar_dados_grafico_linha(
        df_resultados, 
        config_filtros['competencia_filtro'],
        competencia_para_filtro,
        config_filtros['ordenar_decrescente']
    )
    
    # Exibição do gráfico apropriado - EXATAMENTE IGUAL À ORIGINAL
    with st.spinner("Gerando visualização..."):
        variavel_nome = variaveis_categoricas[variavel_selecionada]['nome']
        
        if config_filtros['tipo_grafico'] == "Gráfico de Barras":
            barmode = 'relative' if config_filtros['mostrar_apenas_competencia'] else 'group'
            fig = criar_grafico_comparativo_barras(
                df_visualizacao, variavel_selecionada, variaveis_categoricas, 
                competencia_mapping, barmode=barmode
            )
            explicacao = get_explicacao_barras_comparativo(variavel_nome)
        else:
            fig = criar_grafico_linha_desempenho(
                df_visualizacao, variavel_selecionada, variaveis_categoricas,
                config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None,
                config_filtros['ordenar_decrescente']
            )
            explicacao = get_explicacao_linhas_comparativo(variavel_nome)
            
        st.plotly_chart(fig, use_container_width=True)
    
    # Exibição da explicação e análise detalhada - EXATAMENTE IGUAL À ORIGINAL
    st.info(explicacao)
    criar_expander_analise_comparativa(df_resultados, variavel_selecionada, variaveis_categoricas, competencia_mapping, config_filtros)
    
    # Liberar memória (OTIMIZAÇÃO ADICIONADA)
    release_memory([df_resultados, df_visualizacao, fig])

def render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping):
    """
    Renderiza a análise de relação entre competências usando gráfico de dispersão.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com dados filtrados por estado
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
    race_mapping : dict
        Mapeamento de códigos para raça/cor
    """
    titulo_com_tooltip(
        "Relação entre Competências", 
        get_tooltip_relacao_competencias(), 
        "relacao_competencias_tooltip"
    )
    
    # Configuração dos filtros - EXATAMENTE IGUAL À ORIGINAL
    config_filtros = criar_filtros_dispersao(colunas_notas, competencia_mapping)
    
    # Filtragem e processamento dos dados - CORRIGIDO
    with st.spinner("Processando dados para o gráfico de dispersão..."):
        dados_filtrados, registros_removidos = filtrar_dados_scatter(
            microdados_estados, 
            config_filtros['sexo'] if config_filtros['sexo'] != 'Todos' else None,
            config_filtros['tipo_escola'] if config_filtros['tipo_escola'] != 'Todos' else None,
            config_filtros['eixo_x'], 
            config_filtros['eixo_y'], 
            config_filtros['excluir_notas_zero'],
            filtro_raca=None,  # Não usar filtro de raça
            filtro_faixa_salarial=config_filtros['faixa_salarial']  # Passar lista completa
        )
        
        # Calcular correlação apenas uma vez e reutilizar - EXATAMENTE IGUAL À ORIGINAL
        correlacao, interpretacao = calcular_correlacao_competencias(
            dados_filtrados, 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y']
        )
    
    # Informações sobre registros removidos foram removidas conforme solicitado
    # (Não exibir mais a mensagem sobre exclusão de notas zero)
    
    # Exibição do gráfico de dispersão - EXATAMENTE IGUAL À ORIGINAL
    with st.spinner("Gerando visualização de dispersão..."):
        fig = criar_grafico_scatter(
            dados_filtrados, 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y'], 
            competencia_mapping,
            config_filtros['colorir_por_faixa']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Preparação da explicação - EXATAMENTE IGUAL À ORIGINAL
    eixo_x_nome = competencia_mapping[config_filtros['eixo_x']]
    eixo_y_nome = competencia_mapping[config_filtros['eixo_y']]
    explicacao = get_explicacao_dispersao(eixo_x_nome, eixo_y_nome, correlacao)
    
    # Exibição da explicação e análise detalhada - EXATAMENTE IGUAL À ORIGINAL
    st.info(explicacao)
    criar_expander_relacao_competencias(dados_filtrados, config_filtros, competencia_mapping, correlacao, interpretacao)
    
    # Liberar memória (OTIMIZAÇÃO ADICIONADA)
    release_memory([dados_filtrados, fig])

def render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """
    Renderiza a análise de desempenho médio por estado ou região.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com dados filtrados por estado
    estados_selecionados : list
        Lista de estados selecionados pelo usuário
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
    """
    titulo_com_tooltip(
        "Médias por Estado/Região e Área de Conhecimento", 
        get_tooltip_desempenho_estados(), 
        "grafico_linha_desempenho_tooltip"
    )
    
    # Adicionar opção para agrupar por região - EXATAMENTE IGUAL À ORIGINAL
    col1, col2 = st.columns([1, 2])
    with col1:
        agrupar_por_regiao = st.radio(
            "Visualizar por:",
            ["Estados", "Regiões"],
            horizontal=True,
            key="agrupar_desempenho_regiao"
        ) == "Regiões"
    
    # Processamento dos dados - EXATAMENTE IGUAL À ORIGINAL
    with st.spinner("Processando dados..."):
        df_grafico = preparar_dados_grafico_linha_desempenho(
            microdados_estados, 
            estados_selecionados, 
            colunas_notas, 
            competencia_mapping,
            agrupar_por_regiao
        )
    
    # Verificar se temos dados suficientes - CORRIGIDO para tratar None
    if df_grafico is None or df_grafico.empty:
        st.warning("Não há dados suficientes para mostrar o desempenho com os filtros aplicados.")
        return
    
    # Configuração dos filtros - EXATAMENTE IGUAL À ORIGINAL
    config_filtros = criar_filtros_estados(df_grafico)
    
    # Preparação dos dados para visualização - EXATAMENTE IGUAL À ORIGINAL
    df_plot = preparar_dados_estados_para_visualizacao(
        df_grafico, 
        config_filtros['area_selecionada'],
        config_filtros['ordenar_por_nota'],
        config_filtros['mostrar_apenas_area']
    )
    
    # Exibição do gráfico - EXATAMENTE IGUAL À ORIGINAL
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_linha_estados(
            df_plot, 
            config_filtros['area_selecionada'] if config_filtros['mostrar_apenas_area'] else None,
            config_filtros['ordenar_por_nota'],
            por_regiao=agrupar_por_regiao
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Preparação para explicação e análise - EXATAMENTE IGUAL À ORIGINAL
    area_texto = f" em {config_filtros['area_selecionada']}" if config_filtros.get('area_selecionada') and config_filtros.get('mostrar_apenas_area') else " nas diversas áreas de conhecimento"
    
    # Determinar área para análise (usar área específica se selecionada, senão usar Média Geral) - EXATAMENTE IGUAL À ORIGINAL
    area_analise = config_filtros.get('area_selecionada') if config_filtros.get('mostrar_apenas_area') and config_filtros.get('area_selecionada') else "Média Geral"
    
    # Análise de desempenho por estado/região - EXATAMENTE IGUAL À ORIGINAL
    analise = analisar_desempenho_por_estado(df_grafico, area_analise)
    
    # Preparação da explicação - EXATAMENTE IGUAL À ORIGINAL
    melhor_estado = analise['melhor_estado']['Estado'] if analise['melhor_estado'] is not None else ""
    pior_estado = analise['pior_estado']['Estado'] if analise['pior_estado'] is not None else ""
    desvio_padrao = analise['desvio_padrao']
    
    # Determinar variabilidade para explicação - EXATAMENTE IGUAL À ORIGINAL
    variabilidade = determinar_variabilidade(desvio_padrao, config_filtros.get('mostrar_apenas_area', False))
    
    # Texto de localidade baseado no modo de visualização - EXATAMENTE IGUAL À ORIGINAL
    tipo_localidade = "região" if agrupar_por_regiao else "estado"
    
    # Exibição da explicação e análise detalhada - EXATAMENTE IGUAL À ORIGINAL
    explicacao = get_explicacao_desempenho_estados(area_texto, melhor_estado, pior_estado, variabilidade, tipo_localidade)
    st.info(explicacao)
    criar_expander_desempenho_estados(df_grafico, area_analise, analise, tipo_localidade)
    
    # Liberar memória se não é uma referência ao original (OTIMIZAÇÃO ADICIONADA)
    if id(df_plot) != id(df_grafico):
        release_memory(df_plot)
    release_memory([df_grafico, fig])

def preparar_dados_estados_para_visualizacao(df_grafico, area_selecionada, ordenar_por_nota, mostrar_apenas_area):
    """
    Prepara os dados de estados/regiões para visualização, aplicando filtros e ordenação.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    
    Parâmetros:
    -----------
    df_grafico : DataFrame
        DataFrame com dados de desempenho por estado/região
    area_selecionada : str
        Área de conhecimento selecionada
    ordenar_por_nota : bool
        Indica se deve ordenar por nota
    mostrar_apenas_area : bool
        Indica se deve mostrar apenas a área selecionada
        
    Retorna:
    --------
    DataFrame: DataFrame preparado para visualização
    """
    # Otimização: evita cópia desnecessária se não precisar ordenar - EXATAMENTE IGUAL À ORIGINAL
    if ordenar_por_nota and area_selecionada:
        # Aplicar ordenação e filtro - EXATAMENTE IGUAL À ORIGINAL
        df_plot = df_grafico.copy()
        
        # Obter ordem dos estados/regiões pela área selecionada - EXATAMENTE IGUAL À ORIGINAL
        media_por_estado = df_plot[df_plot['Área'] == area_selecionada]
        ordem_estados = media_por_estado.sort_values('Média', ascending=False)['Estado'].tolist()
        
        # Aplicar ordenação como categoria - EXATAMENTE IGUAL À ORIGINAL
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        # Filtrar para mostrar apenas a área selecionada se solicitado - EXATAMENTE IGUAL À ORIGINAL
        if mostrar_apenas_area:
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    else:
        # Se não precisar ordenar, usa o DataFrame original sem cópia - EXATAMENTE IGUAL À ORIGINAL
        df_plot = df_grafico
        
        # Filtrar para mostrar apenas a área selecionada se solicitado - EXATAMENTE IGUAL À ORIGINAL
        if mostrar_apenas_area and area_selecionada:
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    
    return df_plot

def determinar_variabilidade(desvio_padrao, mostrar_apenas_area):
    """
    Determina a classificação de variabilidade com base no desvio padrão.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    
    Parâmetros:
    -----------
    desvio_padrao : float
        Valor do desvio padrão
    mostrar_apenas_area : bool
        Indica se está mostrando apenas uma área específica
        
    Retorna:
    --------
    str: Classificação de variabilidade
    """
    if not mostrar_apenas_area:
        return "variável"
    
    if desvio_padrao > 15:
        return "alta"
    elif desvio_padrao > 8:
        return "moderada"
    else:
        return "baixa"

# ===================== MAIN - EXECUÇÃO DA PÁGINA =====================

def main():
    """Função principal da página Desempenho"""
    
    # Limpeza de cache
    clear_desempenho_cache()
    
    # Inicializar session state
    init_desempenho_session_state()

    estados_selecionados, locais_selecionados = render_sidebar_filters()
    
    # Título da página
    st.title("📊 Análise de Desempenho - ENEM 2023")

    
    # ✅ VERIFICAR SE HÁ ESTADOS SELECIONADOS (NOVO)
    if not estados_selecionados:
        st.warning("⚠️ Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return 
        
    # Obter dados do session state
    # estados_selecionados = st.session_state.estados_selecionados
    # locais_selecionados = st.session_state.locais_selecionados
    mappings = st.session_state.mappings
    
    # Extrair mapeamentos necessários
    colunas_notas = mappings['colunas_notas']
    competencia_mapping = mappings['competencia_mapping']
    race_mapping = mappings['race_mapping']
    variaveis_categoricas = mappings['variaveis_categoricas']
    desempenho_mapping = mappings['desempenho_mapping']
    
    try:
        # Carregar dados para estados selecionados
        with st.spinner("Carregando dados de desempenho..."):
            microdados_completos = get_cached_data_desempenho(estados_selecionados)
            
            # Filtrar dados pelos estados selecionados
            microdados_estados = filter_data_by_states(microdados_completos, estados_selecionados)
            
            # Para análise comparativa, pode precisar de dados adicionais
            # Vamos usar os dados completos como entrada para o comparativo
            # pois ele precisa de todo o dataset para fazer a análise correta
        
        if microdados_estados.empty:
            st.error("❌ Nenhum dado encontrado para os estados selecionados.")
            return
        
        # Renderizar análise de desempenho (MANTÉM FUNCIONALIDADE 100% ORIGINAL)
        render_desempenho(
            microdados_completos,  # dados completos para análise comparativa
            microdados_estados,    # dados filtrados por estado
            estados_selecionados, 
            locais_selecionados, 
            colunas_notas, 
            competencia_mapping, 
            race_mapping,
            variaveis_categoricas,
            desempenho_mapping
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
main()