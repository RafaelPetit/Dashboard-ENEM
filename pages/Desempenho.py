"""
Página de Análise de Desempenho do ENEM 2023

Esta página contém análises relacionadas ao desempenho dos candidatos:
- Análise comparativa por variáveis demográficas
- Relação entre competências (dispersão)
- Médias por estado/região
- Análises de correlação entre notas
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import partial

# Imports para carregamento de dados
from data.api import data_api
from utils.helpers.cache_utils import release_memory, clear_all_cache, check_memory_and_cleanup
from utils.page_utils import register_page_navigation, safe_page_execution
from utils.filters_utils import render_state_filters, render_data_info_sidebar
from utils.mappings import get_mappings

# Imports para tooltips
from utils.tooltip import titulo_com_tooltip

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

# Imports para análises estatísticas
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

# Imports para filtros
# Imports para filtros - removidos temporariamente

# Configuração da página
st.set_page_config(
    page_title="Desempenho - ENEM 2023",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração do pandas
pd.options.display.float_format = '{:,.2f}'.format



def load_data_and_filters() -> Tuple[pd.DataFrame, List[str], List[str], List[str], Dict[str, str], Dict[str, str], Dict[str, Any], Dict[str, str]]:
    """
    Carrega dados e filtros necessários para a página.
    
    Returns:
        Tuple contendo: microdados_estados, estados_selecionados, locais_selecionados, 
                       colunas_notas, competencia_mapping, race_mapping, variaveis_categoricas, desempenho_mapping
    """
    try:
        # Renderizar filtros laterais
        estados_selecionados, locais_selecionados = render_state_filters()
        render_data_info_sidebar()
        
        # Carregar dados para desempenho
        microdados = data_api.load_data_for_tab("desempenho", apenas_filtros=False)
        
        if microdados.empty:
            st.warning("Não foi possível carregar os dados.")
            return pd.DataFrame(), [], [], [], {}, {}, {}, {}
          # Filtrar dados por estados selecionados
        microdados_estados = data_api.filter_data_by_states(microdados, estados_selecionados)
        
        # Carregar mapeamentos completos
        mappings = get_mappings()
        
        # Definir colunas de notas e mapeamentos
        colunas_notas = mappings['colunas_notas']
        competencia_mapping = mappings['competencia_mapping']
        race_mapping = mappings['race_mapping']
        variaveis_categoricas = mappings['variaveis_categoricas']
        desempenho_mapping = mappings['desempenho_mapping']
        
        return (microdados_estados, estados_selecionados, locais_selecionados, 
                colunas_notas, competencia_mapping, race_mapping, variaveis_categoricas, desempenho_mapping)
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(), [], [], [], {}, {}, {}, {}

def render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping):
    """Renderiza a análise comparativa de desempenho por variável demográfica."""
    titulo_com_tooltip(
        "Análise Comparativa do Desempenho por Variáveis Demográficas", 
        get_tooltip_analise_comparativa(), 
        "comparativo_desempenho_tooltip"
    )
    
    variavel_selecionada = st.selectbox(
        "Selecione a variável para análise:",
        options=list(variaveis_categoricas.keys()),
        format_func=lambda x: variaveis_categoricas[x]["nome"],
        key="variavel_comparativa_desempenho"
    )

    if variavel_selecionada not in microdados_full.columns:
        st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} (código: {variavel_selecionada}) não está disponível no conjunto de dados.")
        return
    
    with st.spinner("Processando dados para análise comparativa..."):
        df_resultados = preparar_dados_comparativo(
            microdados_full, 
            variavel_selecionada, 
            variaveis_categoricas, 
            colunas_notas, 
            competencia_mapping
        )
    
    config_filtros = criar_filtros_comparativo(df_resultados, variaveis_categoricas, variavel_selecionada)
    
    competencia_para_filtro = config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None
    df_visualizacao = preparar_dados_grafico_linha(
        df_resultados, 
        config_filtros['competencia_filtro'],
        competencia_para_filtro,
        config_filtros['ordenar_decrescente']
    )
    
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
    
    st.info(explicacao)
    criar_expander_analise_comparativa(df_resultados, variavel_selecionada, variaveis_categoricas, competencia_mapping, config_filtros)
    
    release_memory([df_resultados, df_visualizacao])

def render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping):
    """Renderiza a análise de relação entre competências usando gráfico de dispersão."""
    try:
        titulo_com_tooltip(
            "Relação entre Competências", 
            get_tooltip_relacao_competencias(), 
            "relacao_competencias_tooltip"
        )
        
        config_filtros = criar_filtros_dispersao(colunas_notas, competencia_mapping)
        
        with st.spinner("Processando dados para o gráfico de dispersão..."):
            dados_filtrados, registros_removidos = filtrar_dados_scatter(
                microdados_estados, 
                config_filtros['sexo'], 
                config_filtros['tipo_escola'], 
                config_filtros['eixo_x'], 
                config_filtros['eixo_y'], 
                config_filtros['excluir_notas_zero'], 
                None,  # Não aplicar filtro de raça específico
                None   # Não aplicar filtro de faixa salarial específico
            )
            
            correlacao, interpretacao = calcular_correlacao_competencias(
                dados_filtrados, 
                config_filtros['eixo_x'], 
                config_filtros['eixo_y']
            )
        
        if config_filtros['excluir_notas_zero'] and registros_removidos > 0:
            st.info(f"Foram desconsiderados {registros_removidos:,} registros com nota zero.")
        
        with st.spinner("Gerando visualização de dispersão..."):
            fig = criar_grafico_scatter(
                dados_filtrados, 
                config_filtros['eixo_x'], 
                config_filtros['eixo_y'], 
                competencia_mapping,
                config_filtros['colorir_por_faixa']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        eixo_x_nome = competencia_mapping[config_filtros['eixo_x']]
        eixo_y_nome = competencia_mapping[config_filtros['eixo_y']]
        explicacao = get_explicacao_dispersao(eixo_x_nome, eixo_y_nome, correlacao)
        
        st.info(explicacao)
        criar_expander_relacao_competencias(dados_filtrados, config_filtros, competencia_mapping, correlacao, interpretacao)
        
        release_memory(dados_filtrados)
        
    except Exception as e:
        st.error(f"Erro ao processar gráfico de relação entre competências: {e}")
        return

def render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """Renderiza a análise de desempenho médio por estado ou região."""
    titulo_com_tooltip(
        "Médias por Estado/Região e Área de Conhecimento", 
        get_tooltip_desempenho_estados(), 
        "grafico_linha_desempenho_tooltip"
    )
    
    col1, col2 = st.columns([1, 2])
    with col1:
        agrupar_por_regiao = st.radio(
            "Visualizar por:",
            ["Estados", "Regiões"],
            horizontal=True,
            key="agrupar_desempenho_regiao_desempenho"
        ) == "Regiões"
    
    with st.spinner("Processando dados..."):
        df_grafico = preparar_dados_grafico_linha_desempenho(
            microdados_estados, 
            estados_selecionados, 
            colunas_notas, 
            competencia_mapping,
            agrupar_por_regiao
        )
    
    if df_grafico.empty:
        st.warning("Não há dados suficientes para mostrar o desempenho com os filtros aplicados.")
        return
    
    config_filtros = criar_filtros_estados(df_grafico)
    
    df_plot = preparar_dados_estados_para_visualizacao(
        df_grafico, 
        config_filtros['area_selecionada'],
        config_filtros['ordenar_por_nota'],
        config_filtros['mostrar_apenas_area']
    )
    
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_linha_estados(
            df_plot, 
            config_filtros['area_selecionada'] if config_filtros['mostrar_apenas_area'] else None,
            config_filtros['ordenar_por_nota'],
            por_regiao=agrupar_por_regiao
        )
        st.plotly_chart(fig, use_container_width=True)
    
    area_texto = f" em {config_filtros['area_selecionada']}" if config_filtros.get('area_selecionada') and config_filtros.get('mostrar_apenas_area') else " nas diversas áreas de conhecimento"
    
    area_analise = config_filtros.get('area_selecionada') if config_filtros.get('mostrar_apenas_area') and config_filtros.get('area_selecionada') else "Média Geral"
    
    analise = analisar_desempenho_por_estado(df_grafico, area_analise)
    
    melhor_estado = analise['melhor_estado']['Estado'] if analise['melhor_estado'] is not None else ""
    pior_estado = analise['pior_estado']['Estado'] if analise['pior_estado'] is not None else ""
    desvio_padrao = analise['desvio_padrao']
    
    variabilidade = determinar_variabilidade(desvio_padrao, config_filtros.get('mostrar_apenas_area', False))
    
    tipo_localidade = "região" if agrupar_por_regiao else "estado"
    
    explicacao = get_explicacao_desempenho_estados(area_texto, melhor_estado, pior_estado, variabilidade, tipo_localidade)
    st.info(explicacao)
    criar_expander_desempenho_estados(df_grafico, area_analise, analise, tipo_localidade)
    
    if id(df_plot) != id(df_grafico):
        release_memory(df_plot)

def preparar_dados_estados_para_visualizacao(df_grafico, area_selecionada, ordenar_por_nota, mostrar_apenas_area):
    """Prepara os dados de estados/regiões para visualização, aplicando filtros e ordenação."""
    if ordenar_por_nota and area_selecionada:
        df_plot = df_grafico.copy()
        
        media_por_estado = df_plot[df_plot['Área'] == area_selecionada]
        ordem_estados = media_por_estado.sort_values('Média', ascending=False)['Estado'].tolist()
        
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        if mostrar_apenas_area:
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    else:
        df_plot = df_grafico
        
        if mostrar_apenas_area and area_selecionada:
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    
    return df_plot

def determinar_variabilidade(desvio_padrao, mostrar_apenas_area):
    """Determina a classificação de variabilidade com base no desvio padrão."""
    if not mostrar_apenas_area:
        return "variável"
    
    if desvio_padrao > 15:
        return "alta"
    elif desvio_padrao > 8:
        return "moderada"
    else:
        return "baixa"

def main() -> None:
    """Função principal da página de Desempenho."""
    safe_page_execution("Desempenho", _main_content)

def _main_content() -> None:
    """Conteúdo principal da página de Desempenho."""
    st.title("🎯 Análise de Desempenho do ENEM 2023")
    st.markdown("---")
    
    # Carregar dados e filtros
    (microdados_estados, estados_selecionados, locais_selecionados, 
     colunas_notas, competencia_mapping, race_mapping, variaveis_categoricas, desempenho_mapping) = load_data_and_filters()
    
    if microdados_estados.empty:
        st.warning("Não foi possível carregar os dados. Verifique sua conexão e tente novamente.")
        return
    
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    mensagem = f"Analisando Desempenho para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Usamos um placeholder para microdados_full que só será carregado se necessário
    microdados_full = None    
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Análise Comparativa", "Relação entre Competências", "Médias por Estado"],
        horizontal=True
    )
    
    try:
        if analise_selecionada == "Análise Comparativa":
            # Carrega microdados_full apenas quando necessário
            with st.spinner("Preparando dados para análise comparativa..."):
                microdados_full = preparar_dados_desempenho_geral(microdados_estados, colunas_notas, desempenho_mapping)
            render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping)
            release_memory(microdados_full)  # Libera memória após uso
        elif analise_selecionada == "Relação entre Competências":
            render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping)
        else:
            render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping)
    except Exception as e:
        st.error(f"Ocorreu um erro ao exibir a análise: {str(e)}")
        st.warning("Tente selecionar outra análise ou verificar os filtros aplicados.")
    finally:
        # Liberar memória dos dados carregados
        release_memory(microdados_estados)

if __name__ == "__main__":
    main()
