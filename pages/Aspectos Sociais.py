"""
Página de Análise de Aspectos Sociais do ENEM 2023

Esta página contém análises relacionadas aos aspectos socioeconômicos dos candidatos:
- Correlações entre aspectos sociais
- Distribuições de variáveis socioeconômicas
- Análises por estado/região
- Impacto social no desempenho
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from functools import partial

# Imports para carregamento de dados
from data.api import data_api
from utils.helpers.cache_utils import release_memory, clear_all_cache
from utils.page_utils import register_page_navigation, safe_page_execution
from utils.filters_utils import render_state_filters, render_data_info_sidebar
from utils.mappings import get_mappings

# Imports para tooltips
from utils.tooltip import titulo_com_tooltip

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

# Imports para análises estatísticas
from utils.estatisticas import (
    calcular_estatisticas_distribuicao,
    analisar_correlacao_categorias,
    analisar_distribuicao_regional,
    calcular_estatisticas_por_categoria
)

# Imports para explicações
from utils.explicacao import (
    get_tooltip_correlacao_aspectos,
    get_tooltip_distribuicao_aspectos,
    get_tooltip_aspectos_por_estado,
    get_explicacao_heatmap,
    get_explicacao_barras_empilhadas,
    get_explicacao_sankey,
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
    page_title="Aspectos Sociais - ENEM 2023",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração do pandas
pd.options.display.float_format = '{:,.2f}'.format



def load_data_and_filters() -> Tuple[pd.DataFrame, List[str], List[str], Dict[str, Any]]:
    """
    Carrega dados e filtros necessários para a página.
    
    Returns:
        Tuple contendo: microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais
    """
    try:
        # Renderizar filtros laterais
        estados_selecionados, locais_selecionados = render_state_filters()
        render_data_info_sidebar()
        
        # Carregar dados para aspectos sociais
        microdados = data_api.load_data_for_tab("aspectos_sociais", apenas_filtros=False)
        
        if microdados.empty:
            st.warning("Não foi possível carregar os dados.")
            return pd.DataFrame(), [], [], {}
          # Filtrar dados por estados selecionados
        microdados_estados = data_api.filter_data_by_states(microdados, estados_selecionados)
        
        # Carregar mapeamentos completos
        mappings = get_mappings()
        variaveis_sociais = mappings['variaveis_sociais']
        
        return microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(), [], [], {}

def render_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais):
    """Renderiza a análise de correlação entre dois aspectos sociais."""
    titulo_com_tooltip(
        "Correlação entre Aspectos Sociais", 
        get_tooltip_correlacao_aspectos(), 
        "correlacao_aspectos_tooltip"
    )
    
    tipo_grafico = st.radio(
        "Escolha o tipo de visualização:",
        ["Heatmap", "Barras Empilhadas", "Sankey"],
        horizontal=True,
        key="tipo_viz_correlacao_social"
    )
    
    col1, col2 = st.columns(2)

    if 'var_y_previous_social' not in st.session_state:
        st.session_state.var_y_previous_social = None

    with col1:
        var_x = st.selectbox(
            "Variável X:", 
            options=list(variaveis_sociais.keys()),
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="var_x_social"
        )

    with col2:
        opcoes_y = [k for k in variaveis_sociais.keys() if k != var_x]

        index = 0
        if st.session_state.var_y_previous_social in opcoes_y:
            index = opcoes_y.index(st.session_state.var_y_previous_social)

        var_y = st.selectbox(
            "Variável Y:", 
            options=opcoes_y,
            format_func=lambda x: variaveis_sociais[x]["nome"],
            index=index,
            key="var_y_social"
        )

        st.session_state.var_y_previous_social = var_y
    
    colunas_ausentes = []
    if var_x not in microdados_estados.columns:
        colunas_ausentes.append(variaveis_sociais[var_x]["nome"])
    if var_y not in microdados_estados.columns:
        colunas_ausentes.append(variaveis_sociais[var_y]["nome"])
        
    if colunas_ausentes:
        st.warning(f"As seguintes variáveis não estão disponíveis nos dados: {', '.join(colunas_ausentes)}")
        return
    
    with st.spinner("Preparando dados para análise..."):
        df_preparado, var_x_plot, var_y_plot = preparar_dados_correlacao(
            microdados_estados, var_x, var_y, variaveis_sociais
        )
    
    if df_preparado.empty:
        st.warning("Não há dados suficientes para analisar a correlação entre estas variáveis.")
        return
    
    with st.spinner("Calculando métricas estatísticas..."):
        metricas = analisar_correlacao_categorias(df_preparado, var_x_plot, var_y_plot)
    
    estados_texto = ', '.join(locais_selecionados) if len(locais_selecionados) <= 3 else f"{len(estados_selecionados)} estados selecionados"
    
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
    
    st.plotly_chart(fig, use_container_width=True)
    st.info(explicacao)
    
    criar_expander_analise_correlacao(df_preparado, var_x, var_y, var_x_plot, var_y_plot, variaveis_sociais)
    
    release_memory(df_preparado)

def render_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais):
    """Renderiza a análise de distribuição de um aspecto social."""
    titulo_com_tooltip(
        "Distribuição de Aspectos Sociais", 
        get_tooltip_distribuicao_aspectos(), 
        "distribuicao_aspectos_tooltip"
    )
    
    aspecto_social = st.selectbox(
        "Selecione o aspecto social para análise:",
        options=list(variaveis_sociais.keys()),
        format_func=lambda x: variaveis_sociais[x]["nome"],
        key="aspecto_dist_social"
    )
    
    if aspecto_social not in microdados_estados.columns:
        st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
        return
    
    with st.spinner("Preparando dados..."):
        df_preparado, coluna_plot = preparar_dados_distribuicao(
            microdados_estados, 
            aspecto_social, 
            variaveis_sociais
        )
        
        if df_preparado.empty:
            st.warning(f"Não há dados suficientes para analisar a distribuição de {variaveis_sociais[aspecto_social]['nome']}.")
            return
        
        contagem_aspecto = contar_candidatos_por_categoria(df_preparado, coluna_plot)
        
        if contagem_aspecto.empty:
            st.warning(f"Não foram encontradas categorias para {variaveis_sociais[aspecto_social]['nome']}.")
            return
        
        contagem_aspecto = ordenar_categorias(contagem_aspecto, aspecto_social, variaveis_sociais)
    
    with st.spinner("Calculando estatísticas..."):
        estatisticas = calcular_estatisticas_distribuicao(contagem_aspecto)
        
    total = estatisticas['total']
    categoria_mais_frequente = estatisticas.get('categories_stats', {}).get('most_frequent', {})
    
    opcao_viz = st.radio(
        "Tipo de visualização:",
        ["Gráfico de Barras", "Gráfico de Linha", "Gráfico de Pizza"],
        horizontal=True,
        key="viz_tipo_dist_social"
    )
    
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_distribuicao(
            contagem_aspecto, 
            opcao_viz, 
            aspecto_social, 
            variaveis_sociais
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    explicacao = get_explicacao_distribuicao(
        variaveis_sociais[aspecto_social]["nome"], 
        total, 
        categoria_mais_frequente
    )
    st.info(explicacao)
    
    criar_expander_dados_distribuicao(contagem_aspecto, aspecto_social, variaveis_sociais)
    
    release_memory([df_preparado, contagem_aspecto])

def render_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais):
    """Renderiza a análise de distribuição de aspectos sociais por estado ou região."""
    titulo_com_tooltip(
        "Distribuição de Aspectos Sociais por Estado/Região", 
        get_tooltip_aspectos_por_estado(), 
        "aspectos_por_estado_tooltip"
    )
    
    aspecto_social = st.selectbox(
        "Selecione o aspecto social para análise por estado/região:",
        options=list(variaveis_sociais.keys()),
        format_func=lambda x: variaveis_sociais[x]["nome"],
        key="aspecto_por_estado_social"
    )
    
    if aspecto_social not in microdados_estados.columns:
        st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
        return
    
    col1, col2 = st.columns([1, 2])
    with col1:
        agrupar_por_regiao = st.radio(
            "Visualizar por:",
            ["Estados", "Regiões"],
            horizontal=True,
            key="agrupar_aspectos_regiao_social"
        ) == "Regiões"
    
    with st.spinner("Preparando dados..."):
        df_por_estado = preparar_dados_grafico_aspectos_por_estado(
            microdados_estados, 
            aspecto_social, 
            estados_selecionados, 
            variaveis_sociais,
            agrupar_por_regiao
        )
    
    if df_por_estado.empty:
        tipo_localidade = "região" if agrupar_por_regiao else "estado"
        st.warning(f"Não há dados suficientes para mostrar a distribuição de {variaveis_sociais[aspecto_social]['nome']} por {tipo_localidade}.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        ordenar_por_percentual = st.checkbox(
            "Ordenar por percentual", 
            value=False, 
            key="ordenar_estados_percentual_social"
        )
    
    categoria_selecionada = None
    if ordenar_por_percentual:
        with col2:
            categorias_disponiveis = sorted(df_por_estado['Categoria'].unique().tolist())
            categoria_selecionada = st.selectbox(
                "Ordenar por categoria:",
                options=categorias_disponiveis,
                key="categoria_ordenacao_social"
            )
    
    df_plot = df_por_estado.copy()
    
    if ordenar_por_percentual and categoria_selecionada:
        df_plot = _ordenar_dados_por_categoria(df_plot, categoria_selecionada)
        
        mostrar_apenas_categoria = st.checkbox(
            "Mostrar apenas a categoria selecionada", 
            value=False, 
            key="mostrar_apenas_categoria_estado_social"
        )
        
        if mostrar_apenas_categoria:
            df_plot = df_plot[df_plot['Categoria'] == categoria_selecionada]
    
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_aspectos_por_estado(
            df_plot, 
            aspecto_social, 
            variaveis_sociais, 
            por_regiao=agrupar_por_regiao
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    tipo_localidade = "região" if agrupar_por_regiao else "estado"
    explicacao = get_explicacao_aspectos_por_estado(
        variaveis_sociais[aspecto_social]['nome'], 
        categoria_selecionada,
        tipo_localidade
    )
    st.info(explicacao)
    
    if categoria_selecionada:
        criar_expander_analise_regional(
            df_por_estado, 
            aspecto_social, 
            categoria_selecionada, 
            variaveis_sociais, 
            tipo_localidade
        )
    
    criar_expander_dados_completos_estado(df_por_estado, tipo_localidade)
    
    release_memory([df_por_estado, df_plot])

def _ordenar_dados_por_categoria(df: pd.DataFrame, categoria: str) -> pd.DataFrame:
    """Ordena o DataFrame com base nos percentuais de uma categoria específica."""
    try:
        percentual_por_estado = df[df['Categoria'] == categoria].copy()
        
        if percentual_por_estado.empty:
            return df
            
        ordem_estados = percentual_por_estado.sort_values('Percentual', ascending=False)['Estado'].tolist()
        
        df_ordenado = df.copy()
        df_ordenado['Estado'] = pd.Categorical(df_ordenado['Estado'], categories=ordem_estados, ordered=True)
        return df_ordenado.sort_values('Estado')
    
    except Exception as e:
        print(f"Erro ao ordenar dados por categoria: {e}")
        return df

def main() -> None:
    """Função principal da página de Aspectos Sociais."""
    safe_page_execution("Aspectos Sociais", _main_content)

def _main_content() -> None:
    """Conteúdo principal da página de Aspectos Sociais."""
    st.title("👥 Aspectos Sociais do ENEM 2023")
    st.markdown("---")
    
    # Carregar dados e filtros
    microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais = load_data_and_filters()
    
    if microdados_estados.empty:
        st.warning("Não foi possível carregar os dados. Verifique sua conexão e tente novamente.")
        return
    
    # Verificar se existem estados selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Mensagem informativa sobre filtros aplicados
    mensagem = "Analisando Aspectos Sociais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Permitir ao usuário selecionar a análise desejada
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Correlação entre Aspectos Sociais", "Distribuição de Aspectos Sociais", "Aspectos Sociais por Estado/Região"],
        horizontal=True
    )
    
    # Direcionar para a análise selecionada
    try:
        if analise_selecionada == "Correlação entre Aspectos Sociais":
            render_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais)
        elif analise_selecionada == "Distribuição de Aspectos Sociais":
            render_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais)
        else:  # "Aspectos Sociais por Estado/Região"
            render_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais)
    except Exception as e:
        st.error(f"Ocorreu um erro ao exibir a análise: {str(e)}")
        st.warning("Tente selecionar outra análise ou verificar os filtros aplicados.")
    finally:
        # Liberar memória dos dados carregados
        release_memory(microdados_estados)

if __name__ == "__main__":
    main()
