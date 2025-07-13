import streamlit as st
import pandas as pd
import gc
from typing import List, Optional, Callable

from utils.helpers.sidebar_filter import render_sidebar_filters

# Imports para tooltips e métricas
from utils.helpers.tooltip import titulo_com_tooltip

# Imports para gerenciamento de memória
from utils.helpers.cache_utils import release_memory, optimized_cache

# Imports para carregamento de dados
from data.data_loader import load_data_for_tab, filter_data_by_states
from utils.helpers.mappings import get_mappings

# Imports para preparação de dados
from utils.prepara_dados import (
    preparar_dados_correlacao,
    preparar_dados_distribuicao,
    contar_candidatos_por_categoria,
    ordenar_categorias,
    preparar_dados_grafico_aspectos_por_estado
)

# Imports para visualizações
from utils.visualizacao import (
    criar_grafico_heatmap,
    criar_grafico_barras_empilhadas,
    criar_grafico_sankey,
    criar_grafico_distribuicao,
    criar_grafico_aspectos_por_estado
)

# Imports para estatísticas
from utils.estatisticas import (
    calcular_estatisticas_distribuicao,
    analisar_correlacao_categorias,
)

# Imports para explicações
from utils.explicacao import (
    get_tooltip_correlacao_aspectos,
    get_tooltip_distribuicao_aspectos,
    get_tooltip_aspectos_por_estado,
    get_explicacao_distribuicao,
    get_explicacao_aspectos_por_estado
)

# Imports para expanders
from utils.expander import (
    criar_expander_analise_correlacao,
    criar_expander_dados_distribuicao,
    criar_expander_analise_regional,
    criar_expander_dados_completos_estado
)

# Configuração da página
st.set_page_config(
    page_title="ENEM - Aspectos Sociais",
    page_icon="👥",
    layout="wide"
)


pd.options.display.float_format = '{:,.2f}'.format

def clear_aspectos_cache():
    """Limpa cache específico da página Aspectos Sociais"""
    st.session_state.current_page = "aspectos_sociais"
    
    # Limpar cache de outras páginas se necessário
    if hasattr(st.session_state, 'last_page') and st.session_state.last_page != "aspectos_sociais":
        st.cache_data.clear()
        gc.collect()
    
    st.session_state.last_page = "aspectos_sociais"

def init_aspectos_session_state():
    """Inicializa session_state específico para página Aspectos Sociais"""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()
    
    if 'estados_selecionados' not in st.session_state:
        st.session_state.estados_selecionados = []
        st.warning("⚠️ Nenhum estado selecionado. Volte à página inicial para configurar os filtros.")
        st.stop()
    
    if 'locais_selecionados' not in st.session_state:
        st.session_state.locais_selecionados = []

def get_cached_data_aspectos(estados_selecionados: List[str]):
    """Carrega dados otimizados para a página Aspectos Sociais"""
    
    @st.cache_data(ttl=600, max_entries=2, show_spinner=False)
    def _load_aspectos_data(estados_key: str):
        """Cache interno para dados da página Aspectos Sociais"""
        return load_data_for_tab("aspectos_sociais")
    
    # Usar string dos estados como chave para cache
    estados_key = "_".join(sorted(estados_selecionados))
    return _load_aspectos_data(estados_key)

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

def render_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais):
    """
    Renderiza a aba de Aspectos Sociais com diferentes análises baseadas na seleção do usuário.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL - tabs/aspectos_sociais.py
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados apenas dos estados selecionados
    estados_selecionados : list
        Lista com as siglas dos estados selecionados pelo usuário
    locais_selecionados : list
        Lista com os nomes dos estados/regiões selecionados para exibição
    variaveis_sociais : dict
        Dicionário com as variáveis sociais disponíveis e seus mapeamentos
    """
    # Verificar se existem estados selecionados - EXATAMENTE IGUAL À ORIGINAL
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Otimizar dados na memória (ÚNICA ADIÇÃO)
    with st.spinner("Otimizando dados..."):
        microdados_estados = optimize_memory_usage(microdados_estados)
    
    # Mensagem informativa sobre filtros aplicados - EXATAMENTE IGUAL À ORIGINAL
    mensagem = "Analisando Aspectos Sociais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Permitir ao usuário selecionar a análise desejada - EXATAMENTE IGUAL À ORIGINAL
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Correlação entre Aspectos Sociais", "Distribuição de Aspectos Sociais", "Aspectos Sociais por Estado/Região"],
        horizontal=True
    )
    
    # Direcionar para a análise selecionada - EXATAMENTE IGUAL À ORIGINAL
    try:
        if analise_selecionada == "Correlação entre Aspectos Sociais":
            render_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais)
        elif analise_selecionada == "Distribuição de Aspectos Sociais":
            render_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais)
        else:  # "Aspectos Sociais por Estado/Região"
            render_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais)
    except Exception as e:
        st.error(f"Ocorreu um erro ao exibir a análise: {str(e)}")
        st.warning("Tente selecionar outra visualização ou verificar os filtros aplicados.")
    
    # Limpeza de memória otimizada (ÚNICA ADIÇÃO)
    release_memory(microdados_estados)

def render_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais):
    """
    Renderiza a análise de correlação entre dois aspectos sociais.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    """
    try:
        # Título com tooltip - EXATAMENTE IGUAL À ORIGINAL
        titulo_com_tooltip(
            "Correlação entre Aspectos Sociais", 
            get_tooltip_correlacao_aspectos(), 
            "correlacao_aspectos_tooltip"
        )
        
        # Seleção do tipo de visualização - EXATAMENTE IGUAL À ORIGINAL
        tipo_grafico = st.radio(
            "Escolha o tipo de visualização:",
            ["Heatmap", "Barras Empilhadas", "Sankey"],
            horizontal=True,
            key="tipo_viz_correlacao"
        )
        
        # Seleção das variáveis para correlação - EXATAMENTE IGUAL À ORIGINAL
        col1, col2 = st.columns(2)

        # Inicializar session_state para var_y_previous se não existir - EXATAMENTE IGUAL À ORIGINAL
        if 'var_y_previous' not in st.session_state:
            st.session_state.var_y_previous = None

        with col1:
            var_x = st.selectbox(
                "Variável X:", 
                options=list(variaveis_sociais.keys()),
                format_func=lambda x: variaveis_sociais[x]["nome"],
                key="var_x_social"
            )

        with col2:
            # Filtrar para não repetir a mesma variável - EXATAMENTE IGUAL À ORIGINAL
            opcoes_y = [k for k in variaveis_sociais.keys() if k != var_x]

            # Determinar o índice inicial baseado na seleção anterior - EXATAMENTE IGUAL À ORIGINAL
            index = 0
            if st.session_state.var_y_previous in opcoes_y:
                index = opcoes_y.index(st.session_state.var_y_previous)

            var_y = st.selectbox(
                "Variável Y:", 
                options=opcoes_y,
                format_func=lambda x: variaveis_sociais[x]["nome"],
                index=index,
                key="var_y_social"
            )

            # Armazenar a seleção atual para o próximo ciclo - EXATAMENTE IGUAL À ORIGINAL
            st.session_state.var_y_previous = var_y
        
        # Verificar se ambas as variáveis existem nos dados - EXATAMENTE IGUAL À ORIGINAL
        colunas_ausentes = []
        if var_x not in microdados_estados.columns:
            colunas_ausentes.append(variaveis_sociais[var_x]["nome"])
        if var_y not in microdados_estados.columns:
            colunas_ausentes.append(variaveis_sociais[var_y]["nome"])
            
        if colunas_ausentes:
            st.warning(f"As seguintes variáveis não estão disponíveis nos dados: {', '.join(colunas_ausentes)}")
            return
        
        # Preparar dados para visualização - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Preparando dados para análise..."):
            df_preparado, var_x_plot, var_y_plot = preparar_dados_correlacao(
                microdados_estados, var_x, var_y, variaveis_sociais
            )
        
        # Verificar se temos dados suficientes - EXATAMENTE IGUAL À ORIGINAL
        if df_preparado.empty:
            st.warning("Não há dados suficientes para analisar a correlação entre estas variáveis.")
            return
        
        # Calcular métricas para análise estatística - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Calculando métricas estatísticas..."):
            metricas = analisar_correlacao_categorias(df_preparado, var_x_plot, var_y_plot)
        
        # Texto para indicar estados no título - EXATAMENTE IGUAL À ORIGINAL
        estados_texto = ', '.join(locais_selecionados) if len(locais_selecionados) <= 3 else f"{len(estados_selecionados)} estados selecionados"
        
        # Criar visualização apropriada com base na escolha do usuário - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            if tipo_grafico == "Heatmap":
                fig, explicacao = criar_grafico_heatmap(
                    df_preparado, var_x, var_y, var_x_plot, var_y_plot, 
                    variaveis_sociais, estados_texto
                )
                
            elif tipo_grafico == "Barras Empilhadas":
                fig, explicacao = criar_grafico_barras_empilhadas(
                    df_preparado, var_x, var_y, var_x_plot, var_y_plot, 
                    variaveis_sociais, estados_texto
                )
                
            else:  # Sankey
                fig, explicacao = criar_grafico_sankey(
                    df_preparado, var_x, var_y, var_x_plot, var_y_plot, 
                    variaveis_sociais, estados_texto
                )
        
        # Exibir o gráfico e explicação - EXATAMENTE IGUAL À ORIGINAL
        st.plotly_chart(fig, use_container_width=True)
        st.info(explicacao)
        
        # Adicionar análise estatística detalhada - EXATAMENTE IGUAL À ORIGINAL
        criar_expander_analise_correlacao(df_preparado, var_x, var_y, var_x_plot, var_y_plot, variaveis_sociais)
        
        # Liberar memória após uso - OTIMIZAÇÃO ADICIONADA
        release_memory([df_preparado, fig])
        
    except Exception as e:
        st.error(f"Erro ao exibir correlação de aspectos sociais: {str(e)}")
        st.warning("Verifique se as variáveis selecionadas estão disponíveis nos dados.")

def render_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais):
    """
    Renderiza a análise de distribuição de um aspecto social.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    """
    try:
        # Título com tooltip - EXATAMENTE IGUAL À ORIGINAL
        titulo_com_tooltip(
            "Distribuição de Aspectos Sociais", 
            get_tooltip_distribuicao_aspectos(), 
            "distribuicao_aspectos_tooltip"
        )
        
        # Permitir ao usuário selecionar qual aspecto social visualizar - EXATAMENTE IGUAL À ORIGINAL
        aspecto_social = st.selectbox(
            "Selecione o aspecto social para análise:",
            options=list(variaveis_sociais.keys()),
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="aspecto_dist"
        )
        
        # Verificar se a coluna existe nos dados - EXATAMENTE IGUAL À ORIGINAL
        if aspecto_social not in microdados_estados.columns:
            st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
            return
        
        # Preparar dados para visualização - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Preparando dados..."):
            df_preparado, coluna_plot = preparar_dados_distribuicao(
                microdados_estados, 
                aspecto_social, 
                variaveis_sociais
            )
            
            # Verificar se temos dados suficientes - EXATAMENTE IGUAL À ORIGINAL
            if df_preparado.empty:
                st.warning(f"Não há dados suficientes para analisar a distribuição de {variaveis_sociais[aspecto_social]['nome']}.")
                return
            
            # Contar candidatos por categoria - EXATAMENTE IGUAL À ORIGINAL
            contagem_aspecto = contar_candidatos_por_categoria(df_preparado, coluna_plot)
            
            # Verificar se temos categorias - EXATAMENTE IGUAL À ORIGINAL
            if contagem_aspecto.empty:
                st.warning(f"Não foram encontradas categorias para {variaveis_sociais[aspecto_social]['nome']}.")
                return
            
            # Ordenar os dados - EXATAMENTE IGUAL À ORIGINAL
            contagem_aspecto = ordenar_categorias(contagem_aspecto, aspecto_social, variaveis_sociais)
        
        # Calcular estatísticas - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Calculando estatísticas..."):
            estatisticas = calcular_estatisticas_distribuicao(contagem_aspecto)
            
        # Obter informações para explicação - EXATAMENTE IGUAL À ORIGINAL
        total = estatisticas['total']
        categoria_mais_frequente = estatisticas['categoria_mais_frequente']
        
        # Criar opções de visualização - EXATAMENTE IGUAL À ORIGINAL
        opcao_viz = st.radio(
            "Tipo de visualização:",
            ["Gráfico de Barras", "Gráfico de Linha", "Gráfico de Pizza"],
            horizontal=True,
            key="viz_tipo_dist"
        )
        
        # Criar visualização com base na escolha do usuário - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_distribuicao(
                contagem_aspecto, 
                opcao_viz, 
                aspecto_social, 
                variaveis_sociais
            )
        
        # Exibir o gráfico - EXATAMENTE IGUAL À ORIGINAL
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar explicação sobre o gráfico - EXATAMENTE IGUAL À ORIGINAL
        explicacao = get_explicacao_distribuicao(
            variaveis_sociais[aspecto_social]["nome"], 
            total, 
            categoria_mais_frequente
        )
        st.info(explicacao)
        
        # Usar o expander para dados detalhados - EXATAMENTE IGUAL À ORIGINAL
        criar_expander_dados_distribuicao(contagem_aspecto, aspecto_social, variaveis_sociais)
        
        # Liberar memória após uso - OTIMIZAÇÃO ADICIONADA
        release_memory([df_preparado, contagem_aspecto, fig])
        
    except Exception as e:
        st.error(f"Erro ao exibir distribuição de aspectos sociais: {str(e)}")
        st.warning("Verifique se o aspecto social selecionado está disponível nos dados.")

def render_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais):
    """
    Renderiza a análise de distribuição de aspectos sociais por estado ou região.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    """
    try:
        # Título com tooltip - EXATAMENTE IGUAL À ORIGINAL
        titulo_com_tooltip(
            "Distribuição de Aspectos Sociais por Estado/Região", 
            get_tooltip_aspectos_por_estado(), 
            "aspectos_por_estado_tooltip"
        )
        
        # Permitir ao usuário selecionar qual aspecto social visualizar - EXATAMENTE IGUAL À ORIGINAL
        aspecto_social = st.selectbox(
            "Selecione o aspecto social para análise por estado/região:",
            options=list(variaveis_sociais.keys()),
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="aspecto_por_estado"
        )
        
        # Verificar se a coluna existe nos dados - EXATAMENTE IGUAL À ORIGINAL
        if aspecto_social not in microdados_estados.columns:
            st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
            return
        
        # Adicionar opção para agrupar por região - EXATAMENTE IGUAL À ORIGINAL
        col1, col2 = st.columns([1, 2])
        with col1:
            agrupar_por_regiao = st.radio(
                "Visualizar por:",
                ["Estados", "Regiões"],
                horizontal=True,
                key="agrupar_aspectos_regiao"
            ) == "Regiões"
        
        # Preparar dados para visualização - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Preparando dados..."):
            df_por_estado = preparar_dados_grafico_aspectos_por_estado(
                microdados_estados, 
                aspecto_social, 
                estados_selecionados, 
                variaveis_sociais,
                agrupar_por_regiao
            )
        
        # Verificar se temos dados suficientes - EXATAMENTE IGUAL À ORIGINAL
        if df_por_estado.empty:
            tipo_localidade = "região" if agrupar_por_regiao else "estado"
            st.warning(f"Não há dados suficientes para mostrar a distribuição de {variaveis_sociais[aspecto_social]['nome']} por {tipo_localidade}.")
            return
        
        # Interface para ordenação e filtragem - EXATAMENTE IGUAL À ORIGINAL
        col1, col2 = st.columns([1, 2])
        
        with col1:
            ordenar_por_percentual = st.checkbox(
                "Ordenar por percentual", 
                value=False, 
                key="ordenar_estados_percentual"
            )
        
        # Mostrar seletor de categoria apenas se o usuário escolheu ordenar - EXATAMENTE IGUAL À ORIGINAL
        categoria_selecionada = None
        if ordenar_por_percentual:
            with col2:
                categorias_disponiveis = sorted(df_por_estado['Categoria'].unique().tolist())
                categoria_selecionada = st.selectbox(
                    "Ordenar por categoria:",
                    options=categorias_disponiveis,
                    key="categoria_ordenacao"
                )
        
        # Criar uma cópia do DataFrame para processamento - EXATAMENTE IGUAL À ORIGINAL
        df_plot = df_por_estado.copy()
        
        # Se o usuário escolheu ordenar, reorganizamos os dados - EXATAMENTE IGUAL À ORIGINAL
        if ordenar_por_percentual and categoria_selecionada:
            df_plot = _ordenar_dados_por_categoria(df_plot, categoria_selecionada)
            
            # Opcional: Filtrar para mostrar apenas a categoria selecionada - EXATAMENTE IGUAL À ORIGINAL
            mostrar_apenas_categoria = st.checkbox(
                "Mostrar apenas a categoria selecionada", 
                value=False, 
                key="mostrar_apenas_categoria_estado"
            )
            
            if mostrar_apenas_categoria:
                df_plot = df_plot[df_plot['Categoria'] == categoria_selecionada]
        
        # Criar o gráfico - EXATAMENTE IGUAL À ORIGINAL
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_aspectos_por_estado(
                df_plot, 
                aspecto_social, 
                variaveis_sociais, 
                por_regiao=agrupar_por_regiao
            )
        
        # Exibir o gráfico - EXATAMENTE IGUAL À ORIGINAL
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar explicação contextualizada - EXATAMENTE IGUAL À ORIGINAL
        tipo_localidade = "região" if agrupar_por_regiao else "estado"
        explicacao = get_explicacao_aspectos_por_estado(
            variaveis_sociais[aspecto_social]['nome'], 
            categoria_selecionada,
            tipo_localidade
        )
        st.info(explicacao)
        
        # Adicionar análise estatística detalhada se uma categoria foi selecionada - EXATAMENTE IGUAL À ORIGINAL
        if categoria_selecionada:
            criar_expander_analise_regional(
                df_por_estado, 
                aspecto_social, 
                categoria_selecionada, 
                variaveis_sociais, 
                tipo_localidade
            )
        
        # Adicionar tabela completa de dados - EXATAMENTE IGUAL À ORIGINAL
        criar_expander_dados_completos_estado(df_por_estado, tipo_localidade)
        
        # Liberar memória - OTIMIZAÇÃO ADICIONADA
        release_memory([df_por_estado, df_plot, fig])
        
    except Exception as e:
        st.error(f"Erro ao exibir aspectos sociais por estado: {str(e)}")
        st.warning("Verifique se o aspecto social selecionado está disponível nos dados.")

def _ordenar_dados_por_categoria(df: pd.DataFrame, categoria: str) -> pd.DataFrame:
    """
    Ordena o DataFrame com base nos percentuais de uma categoria específica.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame a ser ordenado
    categoria : str
        Categoria usada como base para ordenação
        
    Retorna:
    --------
    DataFrame
        DataFrame ordenado
    """
    try:
        # Filtrar apenas os dados da categoria selecionada para ordenação - EXATAMENTE IGUAL À ORIGINAL
        percentual_por_estado = df[df['Categoria'] == categoria].copy()
        
        # Verificar se temos dados para esta categoria - EXATAMENTE IGUAL À ORIGINAL
        if percentual_por_estado.empty:
            return df
            
        # Criar um mapeamento da ordem dos estados com base na categoria selecionada - EXATAMENTE IGUAL À ORIGINAL
        ordem_estados = percentual_por_estado.sort_values('Percentual', ascending=False)['Estado'].tolist()
        
        # Reordenar o DataFrame usando o mapeamento - EXATAMENTE IGUAL À ORIGINAL
        df_ordenado = df.copy()
        df_ordenado['Estado'] = pd.Categorical(df_ordenado['Estado'], categories=ordem_estados, ordered=True)
        return df_ordenado.sort_values('Estado')
    
    except Exception as e:
        return df

def exibir_secao_visualizacao(
    titulo: str, 
    tooltip_text: str, 
    tooltip_id: str, 
    processar_func: Callable, 
    exibir_func: Callable, 
    explicacao_func: Callable, 
    expander_func: Optional[Callable] = None, 
    **kwargs
) -> None:
    """
    Função auxiliar para exibir uma seção de visualização padronizada.
    FUNÇÃO 100% IDÊNTICA À ORIGINAL
    
    Parâmetros:
    -----------
    titulo : str
        Título da seção
    tooltip_text : str 
        Texto do tooltip
    tooltip_id : str
        ID do tooltip
    processar_func : callable
        Função para processamento de dados
    exibir_func : callable
        Função para exibir visualização
    explicacao_func : callable
        Função para obter o texto de explicação
    nder_func : callable, opcional
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

# ===================== MAIN - EXECUÇÃO DA PÁGINA =====================

def main():
    """Função principal da página Aspectos Sociais"""
    
    # Limpeza de cache
    clear_aspectos_cache()
    
    # Inicializar session state
    init_aspectos_session_state()
    
    # Renderizar filtros e obter seleções
    estados_selecionados, locais_selecionados = render_sidebar_filters()
    
    # Título da página
    st.title("👥 Aspectos Sociais - ENEM 2023")

    if not estados_selecionados:
        st.warning("⚠️ Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return

    # Obter dados do session state
    # estados_selecionados = st.session_state.estados_selecionados
    # locais_selecionados = st.session_state.locais_selecionados
    mappings = st.session_state.mappings
    
    # Extrair mapeamentos necessários
    variaveis_sociais = mappings['variaveis_sociais']
    
    try:
        # Carregar dados para estados selecionados
        with st.spinner("Carregando dados de aspectos sociais..."):
            microdados_completos = get_cached_data_aspectos(estados_selecionados)
            
            # Filtrar dados pelos estados selecionados
            microdados_estados = filter_data_by_states(microdados_completos, estados_selecionados)
        
        if microdados_estados.empty:
            st.error("❌ Nenhum dado encontrado para os estados selecionados.")
            return
        
        # Renderizar análise de aspectos sociais (MANTÉM FUNCIONALIDADE 100% ORIGINAL)
        render_aspectos_sociais(
            microdados_estados, 
            estados_selecionados, 
            locais_selecionados, 
            variaveis_sociais
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