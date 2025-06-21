"""
Página de Análise Geral do ENEM 2023

Esta página contém análises gerais dos dados do ENEM, incluindo:
- Métricas principais
- Distribuição de notas
- Análises regionais e por estado
- Comparativo entre áreas de conhecimento
- Análise de faltas
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union

# Imports para carregamento de dados
from data.api import data_api
from utils.helpers.cache_utils import release_memory, clear_all_cache
from utils.page_utils import register_page_navigation, safe_page_execution
from utils.filters_utils import render_state_filters, render_data_info_sidebar
from utils.mappings import get_mappings

# Imports para tooltips e métricas
from utils.tooltip import titulo_com_tooltip, custom_metric_with_tooltip

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
    page_title="Análise Geral - ENEM 2023",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)



def load_data_and_filters() -> Tuple[pd.DataFrame, List[str], List[str], List[str], Dict[str, str]]:
    """
    Carrega dados e filtros necessários para a página.
    
    Returns:
        Tuple contendo: microdados_estados, estados_selecionados, locais_selecionados, 
                       colunas_notas, competencia_mapping
    """
    try:
        # Renderizar filtros laterais
        estados_selecionados, locais_selecionados = render_state_filters()
        render_data_info_sidebar()
        
        # Carregar dados para a aba geral
        microdados = data_api.load_data_for_tab("geral", apenas_filtros=False)
        
        if microdados.empty:
            st.warning("Não foi possível carregar os dados.")
            return pd.DataFrame(), [], [], [], {}
          # Filtrar dados por estados selecionados
        microdados_estados = data_api.filter_data_by_states(microdados, estados_selecionados)
        
        # Carregar mapeamentos completos
        mappings = get_mappings()
        
        # Definir colunas de notas e mapeamento
        colunas_notas = mappings['colunas_notas']
        competencia_mapping = mappings['competencia_mapping']
        
        return microdados_estados, estados_selecionados, locais_selecionados, colunas_notas, competencia_mapping
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(), [], [], [], {}

def exibir_metricas_principais(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    colunas_notas: List[str]
) -> Dict[str, Any]:
    """
    Calcula e exibe métricas principais em cards.
    """
    titulo_com_tooltip("Métricas Principais", get_tooltip_metricas_principais(), "metricas_tooltip")
    
    with st.spinner("Calculando métricas principais..."):
        metricas = analisar_metricas_principais(microdados_estados, estados_selecionados, colunas_notas)
    
    col1, col2, col3, col4 = st.columns(4)

    def formatar_numero_br(valor: float, casas_decimais: int = 2) -> str:
        formatado = f"{valor:,.{casas_decimais}f}"
        return formatado.replace(',', 'X').replace('.', ',').replace('X', '.')

    with col1:
        custom_metric_with_tooltip(
            label="Candidatos Inscritos",
            value=f"{metricas['total_candidatos']:,}".replace(',', '.'),
            explicacao=get_tooltip_total_candidatos(),
            key="metrica_candidatos_geral"
        )
    
    with col2:
        custom_metric_with_tooltip(
            label="Média Geral",
            value=formatar_numero_br(metricas['media_geral']),
            explicacao=get_tooltip_media_geral(),
            key="metrica_media_geral_geral"
        )
        
    with col3:
        custom_metric_with_tooltip(
            label="Maior Média",
            value=f"{formatar_numero_br(metricas['valor_maior_media_estado'])} ({metricas['estado_maior_media']})",
            explicacao=get_tooltip_maior_media(),
            key="metrica_maior_media_geral"
        )
    
    with col4:
        custom_metric_with_tooltip(
            label="Menor Média",
            value=f"{formatar_numero_br(metricas['valor_menor_media_estado'])} ({metricas['estado_menor_media']})",
            explicacao=get_tooltip_menor_media(),
            key="metrica_menor_media_geral"
        )
                
    return metricas

def exibir_histograma_notas(
    microdados_estados: pd.DataFrame, 
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> None:
    """Exibe um histograma interativo da distribuição de notas com análise estatística."""
    try:
        titulo_com_tooltip("Histograma das Notas", get_tooltip_histograma(), "hist_tooltip")
        
        area_conhecimento = st.selectbox(
            "Selecione a área de conhecimento ou redação:",
            options=colunas_notas,
            format_func=lambda x: competencia_mapping[x],
            key="selectbox_area_histograma_geral"
        )
        
        with st.spinner("Processando dados para o histograma..."):
            df_valido, coluna_hist, nome_area_hist = preparar_dados_histograma(
                microdados_estados, 
                area_conhecimento, 
                competencia_mapping
            )
            
            if df_valido.empty:
                st.warning(f"Não há dados válidos para {nome_area_hist} com os filtros aplicados.")
                return
                
            estatisticas = analisar_distribuicao_notas(df_valido, coluna_hist)
        
        with st.spinner("Gerando visualização..."):
            fig_hist = criar_histograma(
                df_valido,
                coluna_hist,
                nome_area_hist,
                estatisticas
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            release_memory(fig_hist)
        
        explicacao = get_explicacao_histograma(
            nome_area_hist,
            estatisticas['media'],
            estatisticas['mediana'],
            estatisticas['assimetria'],
            estatisticas['curtose']
        )
        st.info(explicacao)
        
        criar_expander_analise_histograma(df_valido, coluna_hist, nome_area_hist, estatisticas)
        criar_expander_analise_faixas_desempenho(df_valido, coluna_hist, nome_area_hist)
        
        release_memory([df_valido, estatisticas])
        
    except Exception as e:
        st.error(f"Erro ao exibir histograma: {str(e)}")

def exibir_analise_faltas(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str]
) -> None:
    """Exibe análise de faltas por estado e dia de prova com gráficos interativos."""
    try:
        colunas_presenca = {
            'TP_PRESENCA_CN': 'Ciências da Natureza',
            'TP_PRESENCA_CH': 'Ciências Humanas',
            'TP_PRESENCA_LC': 'Linguagens e Códigos',
            'TP_PRESENCA_MT': 'Matemática',
            'TP_PRESENCA_REDACAO': 'Redação'
        }
        
        titulo_com_tooltip("Análise de Faltas por Dia de Prova", get_tooltip_faltas(), "faltas_tooltip")
        
        with st.spinner("Processando dados para análise de faltas..."):
            df_faltas = preparar_dados_grafico_faltas(microdados_estados, estados_selecionados, colunas_presenca)
            
            if df_faltas.empty:
                st.warning("Não há dados suficientes para análise de faltas com os filtros aplicados.")
                return
            
            analise_faltas_dados = analisar_faltas(df_faltas)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            ordenar_por_faltas = st.checkbox(
                "Ordenar estados por % de faltas", 
                value=False,
                key="checkbox_ordenar_faltas_geral"
            )
        
        tipo_selecionado = None
        if ordenar_por_faltas:
            with col2:
                tipos_disponiveis = df_faltas['Tipo de Falta'].unique().tolist()
                tipos_disponiveis = [tipo for tipo in tipos_disponiveis if "Total de faltas" not in tipo]
                tipo_selecionado = st.selectbox(
                    "Ordenar por tipo de falta:",
                    options=tipos_disponiveis,
                    key="selectbox_tipo_falta_geral"
                )
        
        filtrar_tipo = False
        if ordenar_por_faltas and tipo_selecionado:
            with col3:
                filtrar_tipo = st.checkbox(
                    "Mostrar apenas este tipo de falta", 
                    value=False,
                    key="checkbox_filtrar_tipo_geral"
                )
        
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_faltas(
                df_faltas, 
                order_by_area=tipo_selecionado if ordenar_por_faltas else None,
                order_ascending=False,
                filtro_area=tipo_selecionado if (filtrar_tipo) else None
            )
            st.plotly_chart(fig, use_container_width=True)
            release_memory(fig)
        
        taxa_media_geral = analise_faltas_dados['taxa_media_geral']
        tipo_mais_comum = analise_faltas_dados['tipo_mais_comum']
        
        estado_maior_falta = "N/A"
        if analise_faltas_dados['estado_maior_falta'] is not None:
            estado_maior_falta = analise_faltas_dados['estado_maior_falta']['Estado']
        
        estado_menor_falta = "N/A"
        if analise_faltas_dados['estado_menor_falta'] is not None:
            estado_menor_falta = analise_faltas_dados['estado_menor_falta']['Estado']
        
        explicacao = get_explicacao_faltas(
            taxa_media_geral,
            tipo_mais_comum,
            estado_maior_falta,
            estado_menor_falta
        )
        st.info(explicacao)
        
        criar_expander_analise_faltas(df_faltas, analise_faltas_dados)
        
        if st.checkbox("Visualizar análise detalhada de evasão por tipo de presença", key="checkbox_evasao_geral"):
            exibir_analise_evasao(microdados_estados, estados_selecionados)
        
        release_memory([df_faltas, analise_faltas_dados])
        
    except Exception as e:
        st.error(f"Erro ao exibir análise de faltas: {str(e)}")

def exibir_analise_regional(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str],
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> None:
    """Exibe análise de médias por estado ou região do Brasil."""
    try:
        titulo_com_tooltip("Médias por Estado/Região", get_tooltip_media_por_regiao(), "media_regional_tooltip")
        
        agrupar_por_regiao = st.checkbox(
            "Agrupar por região", 
            value=False,
            help="Agrupa os estados por região geográfica do Brasil",
            key="checkbox_agrupar_regiao_geral"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            destacar_maior = st.checkbox(
                "Destacar maior média", 
                value=True,
                key="checkbox_destacar_maior_geral"
            )
        with col2:
            destacar_menor = st.checkbox(
                "Destacar menor média", 
                value=True,
                key="checkbox_destacar_menor_geral"
            )
        
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
            release_memory(fig)
        
        tipo_localidade = "região" if agrupar_por_regiao else "estado"
        maior_local = df_medias.sort_values('Média Geral', ascending=False).iloc[0]['Local']
        maior_valor = df_medias.sort_values('Média Geral', ascending=False).iloc[0]['Média Geral']
        menor_local = df_medias.sort_values('Média Geral', ascending=True).iloc[0]['Local']
        menor_valor = df_medias.sort_values('Média Geral', ascending=True).iloc[0]['Média Geral']
        
        if menor_valor > 0:
            diferenca_percentual = ((maior_valor - menor_valor) / menor_valor) * 100
        else:
            diferenca_percentual = 0
        
        media_geral = df_medias['Média Geral'].mean()
        
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
        
        criar_expander_analise_regional(microdados_estados, colunas_notas, competencia_mapping)
        
        release_memory(df_medias)
        
    except Exception as e:
        st.error(f"Erro ao exibir análise regional: {str(e)}")

def exibir_comparativo_areas(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str],
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> None:
    """Exibe comparativo entre áreas de conhecimento."""
    try:
        titulo_com_tooltip("Comparativo entre Áreas de Conhecimento", get_tooltip_comparativo_areas(), "comparativo_areas_tooltip")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_grafico = st.selectbox(
                "Tipo de visualização:",
                options=["barras", "radar", "linha"],
                format_func=lambda x: x.capitalize(),
                key="selectbox_tipo_grafico_areas_geral"
            )
        with col2:
            mostrar_dispersao = st.checkbox(
                "Mostrar dispersão (desvio padrão)", 
                value=True,
                key="checkbox_mostrar_dispersao_geral"
            )
        
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
        
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_comparativo_areas(
                df_areas, 
                tipo_grafico=tipo_grafico, 
                mostrar_dispersao=mostrar_dispersao
            )
            st.plotly_chart(fig, use_container_width=True)
            release_memory(fig)
        
        df_sorted = df_areas.sort_values('Media', ascending=False)
        melhor_area = df_sorted.iloc[0]['Area']
        melhor_media = df_sorted.iloc[0]['Media']
        pior_area = df_sorted.iloc[-1]['Area']
        pior_media = df_sorted.iloc[-1]['Media']
        
        if 'DesvioPadrao' in df_areas.columns:
            maior_variabilidade = df_areas.sort_values('DesvioPadrao', ascending=False).iloc[0]['Area']
            menor_variabilidade = df_areas.sort_values('DesvioPadrao', ascending=True).iloc[0]['Area']
        else:
            maior_variabilidade = "Não disponível"
            menor_variabilidade = "Não disponível"
        
        explicacao = get_explicacao_comparativo_areas(
            melhor_area,
            melhor_media,
            pior_area,
            pior_media,
            maior_variabilidade,
            menor_variabilidade
        )
        st.info(explicacao)
        
        criar_expander_analise_comparativo_areas(df_areas)
        
        release_memory(df_areas)
        
    except Exception as e:
        st.error(f"Erro ao exibir comparativo entre áreas: {str(e)}")

def exibir_analise_evasao(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str]
) -> None:
    """Exibe análise de evasão (presença/ausência) por estado."""
    try:
        titulo_com_tooltip("Análise de Evasão por Estado", get_tooltip_evasao(), "evasao_tooltip")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_grafico = st.selectbox(
                "Tipo de visualização:",
                options=["barras", "mapa_calor", "pizza"],
                format_func=lambda x: "Barras" if x == "barras" else "Mapa de Calor" if x == "mapa_calor" else "Pizza",
                key="selectbox_tipo_grafico_evasao_geral"
            )
        
        metrica_ordenacao = None
        if tipo_grafico in ["barras", "mapa_calor"]:
            with col2:
                ordenar = st.checkbox(
                    "Ordenar estados", 
                    value=False,
                    key="checkbox_ordenar_evasao_geral"
                )
                
                if ordenar:
                    metricas_opcoes = ["Presentes", "Faltantes Dia 1", "Faltantes Dia 2", "Faltantes Ambos"]
                    metrica_ordenacao = st.selectbox(
                        "Ordenar por:",
                        options=metricas_opcoes,
                        key="selectbox_metrica_ordenacao_geral"
                    )
        
        with st.spinner("Processando dados para análise de evasão..."):
            df_evasao = preparar_dados_evasao(microdados_estados, estados_selecionados)
            
            if df_evasao.empty:
                st.warning("Não há dados suficientes para análise de evasão com os filtros aplicados.")
                return
        
        with st.spinner("Gerando visualização..."):
            fig = criar_grafico_evasao(
                df_evasao, 
                tipo_grafico=tipo_grafico,
                ordenar_por=metrica_ordenacao,
                ordem_crescente=False
            )
            st.plotly_chart(fig, use_container_width=True)
            release_memory(fig)
        
        taxa_media_presenca = df_evasao[df_evasao['Métrica'] == 'Presentes']['Valor'].mean()
        taxa_media_ausencia_total = df_evasao[df_evasao['Métrica'] == 'Faltantes Ambos']['Valor'].mean()
        
        maior_presenca_df = df_evasao[df_evasao['Métrica'] == 'Presentes'].sort_values('Valor', ascending=False)
        menor_presenca_df = df_evasao[df_evasao['Métrica'] == 'Presentes'].sort_values('Valor', ascending=True)
        
        estado_maior_presenca = maior_presenca_df.iloc[0]['Estado'] if not maior_presenca_df.empty else "N/A"
        estado_menor_presenca = menor_presenca_df.iloc[0]['Estado'] if not menor_presenca_df.empty else "N/A"
        
        media_dia1 = df_evasao[df_evasao['Métrica'] == 'Faltantes Dia 1']['Valor'].mean()
        media_dia2 = df_evasao[df_evasao['Métrica'] == 'Faltantes Dia 2']['Valor'].mean()
        diferenca_dia1_dia2 = media_dia2 - media_dia1
        
        explicacao = get_explicacao_evasao(
            taxa_media_presenca,
            taxa_media_ausencia_total,
            estado_maior_presenca,
            estado_menor_presenca,
            diferenca_dia1_dia2
        )
        st.info(explicacao)
        
        release_memory(df_evasao)
        
    except Exception as e:
        st.error(f"Erro ao exibir análise de evasão: {str(e)}")

def main() -> None:
    """Função principal da página de Análise Geral."""
    safe_page_execution("Análise Geral", _main_content)

def _main_content() -> None:
    """Conteúdo principal da página de Análise Geral."""
    st.title("📈 Análise Geral do ENEM 2023")
    st.markdown("---")
    
    # Carregar dados e filtros
    microdados_estados, estados_selecionados, locais_selecionados, colunas_notas, competencia_mapping = load_data_and_filters()
    
    if microdados_estados.empty:
        st.warning("Não foi possível carregar os dados. Verifique sua conexão e tente novamente.")
        return
    
    # Verificar se temos estados selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Mostrar mensagem sobre os filtros aplicados
    mensagem = f"Analisando Dados Gerais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Exibir métricas principais (sempre visíveis)
    metricas = exibir_metricas_principais(microdados_estados, estados_selecionados, colunas_notas)
    
    # Permitir ao usuário selecionar a análise desejada
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Distribuição de Notas", "Análise por Região/Estado", "Comparativo entre Áreas", "Análise de Faltas"],
        horizontal=True
    )
    
    # Exibir a visualização selecionada
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
    finally:
        # Liberar memória dos dados carregados
        release_memory([microdados_estados, metricas])

if __name__ == "__main__":
    main()
