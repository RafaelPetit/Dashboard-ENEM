"""
📊 Dashboard de Análise do ENEM 2023
Plataforma de Inteligência Educacional

Análise avançada e insights dos dados do Exame Nacional do Ensino Médio.
Desenvolvida com arquitetura enterprise para escalabilidade e performance.

Funcionalidades Principais:
- Processamento e visualização de dados em tempo real
- Análise interativa regional e demográfica  
- Insights de machine learning e análise preditiva
- Relatórios profissionais e capacidades de exportação

Desenvolvido como Projeto de Iniciação Científica
UNIP - Universidade Paulista | Campus Sorocaba
Curso de Ciência da Computação
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

# Core platform imports
from data.api import data_api
from utils.helpers.cache_utils import release_memory, clear_all_cache, check_memory_and_cleanup
from utils.page_utils import register_page_navigation, safe_page_execution
from utils.filters_utils import render_data_info_sidebar
from utils.mappings import get_mappings

# Premium UI components
from utils.ui_components import (
    render_premium_header,
    render_premium_footer,
    render_status_bar,
    render_metric_card,
    render_info_callout
)

# Analytics and visualization imports
from utils.tooltip import titulo_com_tooltip, custom_metric_with_tooltip
from utils.estatisticas import analisar_metricas_principais
from utils.explicacao import (
    get_tooltip_metricas_principais,
    get_tooltip_total_candidatos,
    get_tooltip_media_geral,
    get_tooltip_maior_media,
    get_tooltip_menor_media
)

# Configuração enterprise da página
st.set_page_config(
    page_title="Dashboard ENEM 2023 | Plataforma de Inteligência Educacional",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/seu-repo/enem-analytics',
        'Report a bug': 'https://github.com/seu-repo/enem-analytics/issues',
        'About': """
        ## Plataforma de Análise do ENEM 2023
        
        **Inteligência de Dados Educacionais Enterprise**
        
        Plataforma avançada de análise para dados do Exame Nacional do Ensino Médio.
        Construída com stack moderno de ciência de dados e arquitetura cloud-native.
        
        - **Volume de Dados:** 4M+ registros de estudantes
        - **Poder de Processamento:** Motor de análise em tempo real
        - **Cobertura:** Escopo nacional em todos os estados brasileiros
        - **Stack Tecnológico:** Python, Streamlit, Plotly, Pandas
        
        *Desenvolvido para pesquisa educacional e análise de políticas públicas*
        
        **Projeto de Iniciação Científica**
        UNIP - Universidade Paulista
        """
    }
)


def render_premium_sidebar() -> None:
    """Renderiza sidebar premium com informações do sistema."""
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 1rem; color: white;'>
        <h3 style='margin: 0; color: white;'>📊 Analytics ENEM</h3>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;'>Inteligência Educacional</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informações do dataset e filtros
    render_data_info_sidebar()

def render_navigation_guide() -> None:
    """Renderiza o guia de navegação."""
    st.markdown("### 🗺️ Guia de Navegação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Análise Geral**
        - Métricas principais do ENEM
        - Distribuições de notas
        - Análises regionais
        - Comparativo entre áreas
        - Análise de faltas
        """)
    
    with col2:
        st.markdown("""
        **👥 Aspectos Sociais**
        - Correlações entre variáveis
        - Distribuições socioeconômicas
        - Análises por estado/região
        - Impacto social no desempenho
        """)
    
    with col3:
        st.markdown("""
        **🎯 Desempenho**
        - Análise comparativa demográfica
        - Relação entre competências
        - Médias por estado/região
        - Dispersão de notas
        """)

def render_main_metrics() -> None:
    """Renderiza as métricas principais do dataset."""
    st.markdown("### 📊 Métricas Principais do ENEM 2023")
    
    # Carregar dados para métricas gerais (sem filtros)
    with st.spinner("Carregando dados principais..."):
        try:
            # Carregar dados mínimos para métricas principais
            microdados = data_api.load_data_for_tab("geral", apenas_filtros=False)
            
            if microdados.empty:
                st.warning("Não foi possível carregar os dados principais.")
                return
                
            # Estados brasileiros para contexto nacional
            estados_brasil = [
                'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
                'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
                'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
            ]
            
            # Colunas de notas
            colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
            
            # Calcular métricas principais
            metricas = analisar_metricas_principais(microdados, estados_brasil, colunas_notas)
            
            # Exibir métricas em cards
            render_metrics_cards(metricas)
            
        except Exception as e:
            st.error(f"Erro ao carregar métricas principais: {str(e)}")
        finally:
            # Liberar memória após uso
            release_memory(microdados)

def render_metrics_cards(metricas: Dict[str, Any]) -> None:
    """Renderiza os cards com as métricas principais."""
    
    # Função para formatar números com vírgula como separador decimal
    def formatar_numero_br(valor: float, casas_decimais: int = 2) -> str:
        formatado = f"{valor:,.{casas_decimais}f}"
        return formatado.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        custom_metric_with_tooltip(
            label="Total de Candidatos",
            value=f"{metricas['total_candidatos']:,}".replace(',', '.'),
            explicacao=get_tooltip_total_candidatos(),
            key="metrica_candidatos_home"
        )
    
    with col2:
        custom_metric_with_tooltip(
            label="Média Geral Nacional",
            value=formatar_numero_br(metricas['media_geral']),
            explicacao=get_tooltip_media_geral(),
            key="metrica_media_geral_home"
        )
        
    with col3:
        custom_metric_with_tooltip(
            label="Maior Média Estadual",
            value=f"{formatar_numero_br(metricas['valor_maior_media_estado'])} ({metricas['estado_maior_media']})",
            explicacao=get_tooltip_maior_media(),
            key="metrica_maior_media_home"
        )
    
    with col4:
        custom_metric_with_tooltip(
            label="Menor Média Estadual",
            value=f"{formatar_numero_br(metricas['valor_menor_media_estado'])} ({metricas['estado_menor_media']})",
            explicacao=get_tooltip_menor_media(),
            key="metrica_menor_media_home"
        )

def render_instructions() -> None:
    """Renderiza instruções de uso da plataforma."""
    st.markdown("### 📋 Como usar esta plataforma")
    
    with st.expander("Instruções detalhadas", expanded=False):
        st.markdown("""
        **1. Filtros na barra lateral:**
        - Use os filtros de estado/região para focar sua análise
        - Os filtros se aplicam a todas as páginas da plataforma
        
        **2. Navegação entre páginas:**
        - Use o menu lateral para navegar entre as diferentes análises
        - Cada página oferece visualizações específicas e análises detalhadas
        
        **3. Interatividade dos gráficos:**
        - Todos os gráficos são interativos (zoom, hover, seleção)
        - Use os controles específicos de cada visualização
        
        **4. Análises detalhadas:**
        - Clique nos expanders para ver análises estatísticas detalhadas
        - Use os tooltips (?) para entender melhor cada métrica
        
        **5. Performance:**
        - A plataforma limpa automaticamente o cache ao trocar de páginas
        - Para melhor performance, evite manter muitas páginas abertas simultaneamente
        """)

def render_institutional_footer() -> None:
    """Renderiza o rodapé institucional da UNIP com informações do projeto."""
    st.markdown("---")
    
    # Layout do rodapé em 3 colunas
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])

    with footer_col1:
        # Coluna da instituição
        try:
            logo = "Logo.jpg"  # Caminho para o logo
            st.image(logo, width=100)
        except:
            st.write("**UNIP - Universidade Paulista**")
        
        st.markdown("""
        <div style='color: #636363; margin-top: 10px;'>
            <p><b>Universidade Paulista</b></p>
            <p style='font-size: 13px;'>Campus Sorocaba</p>
            <p style='font-size: 12px;'>Curso de Ciência da Computação</p>
        </div>
        """, unsafe_allow_html=True)

    with footer_col2:
        # Informações sobre o projeto (centralizado)
        st.markdown("""
        <div style='text-align: center; color: #636363;'>
            <p style='font-size: 16px;'><b>Dashboard de Análise do ENEM 2023</b></p>
            <br>
            <p style='font-size: 14px;'>Projeto de Iniciação Científica</p>
            <hr style='margin: 10px 0; border-color: #e0e0e0;'>
            <p style='font-size: 12px;'>© 2025 - Todos os direitos reservados</p>
            <p style='font-size: 11px; margin-top: 10px;'>v2.0.0 - Atualizado em 20/06/2025</p>
        </div>
        """, unsafe_allow_html=True)

    with footer_col3:
        # Coluna da equipe (desenvolvedor e orientador)
        st.markdown("""
        <div style='text-align: right; color: #636363;'>
            <p style='font-size: 15px;'><b>Equipe</b></p>
            <p style='font-size: 14px; margin-bottom: 2px;'><b>Desenvolvedor:</b></p>
            <p style='font-size: 13px; margin-top: 0;'>Rafael Petit <br> rpetit.dev@gmail.com</p>
            <p style='font-size: 14px; margin-bottom: 2px; margin-top: 15px;'><b>Orientador:</b></p>
            <p style='font-size: 13px; margin-top: 0;'>Prof. Dr. César C. Xavier <br> cesarcx@gmail.com</p>
        </div>
        """, unsafe_allow_html=True)

def main() -> None:
    """Função principal da página."""
    safe_page_execution("Dashboard", _main_content)

def _main_content() -> None:
    """Conteúdo principal da página Dashboard."""
    # Renderizar sidebar premium
    render_premium_sidebar()
    
    # Renderizar componentes da página usando componentes premium
    render_premium_header(
        page_title="📊 Analytics ENEM",
        subtitle="Plataforma de Análise de Dados do ENEM 2023"
    )
    
    # Status bar do sistema
    render_status_bar()
    
    # Guia de navegação e métricas
    render_navigation_guide()
    render_main_metrics()
    render_instructions()
    
    # Footer institucional
    render_institutional_footer()

if __name__ == "__main__":
    main()
