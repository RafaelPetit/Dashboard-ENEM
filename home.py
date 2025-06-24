import streamlit as st
import gc
from utils.mappings import get_mappings
from utils.data_loader import load_data_for_tab, agrupar_estados_em_regioes, release_memory
from utils.helpers.sidebar_filter import render_sidebar_filters

# Configuração inicial da página
st.set_page_config(
    page_title="Dashboard ENEM", 
    page_icon="📚", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para inicializar session_state
def init_session_state():
    """Inicializa variáveis do session_state se não existirem"""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()
    
    # if 'estados_selecionados' not in st.session_state:
    #     st.session_state.estados_selecionados = []
    
    # if 'locais_selecionados' not in st.session_state:
    #     st.session_state.locais_selecionados = []

# Função para limpar cache e memória entre navegações
def clear_page_memory():
    """Limpa cache específico de páginas"""
    # Limpar apenas cache relacionado a dados específicos de páginas
    if hasattr(st.cache_data, 'clear'):
        st.cache_data.clear()
    gc.collect()

# Inicializar session state
init_session_state()

# Renderizar filtros laterais centralizados (remove duplicidade)
estados_selecionados, locais_selecionados = render_sidebar_filters()

# Título principal
st.title("📊 Dashboard de Análise do ENEM - 2023")

# ---------------------------- CONTEÚDO PRINCIPAL ----------------------------
st.markdown("## 🎯 Bem-vindo ao Dashboard ENEM 2023")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 📈 Análises Disponíveis
    
    Este dashboard oferece análises abrangentes dos dados do ENEM 2023:
    
    - **🏠 Geral**: Métricas principais, distribuição de notas, análise regional e comparativos
    - **👥 Aspectos Sociais**: Correlações entre variáveis socioeconômicas e desempenho
    - **📊 Desempenho**: Análises comparativas, relação entre competências e médias por estado
    
    ### 🚀 Como usar:
    1. **Configure os filtros** na barra lateral (regiões/estados)
    2. **Navegue pelas páginas** usando o menu lateral
    3. **Explore as visualizações** interativas em cada seção
    """)

with col2:
    # Mostrar informações sobre a seleção atual
    st.markdown("### 📍 Filtros Atuais")
    
    # Cargar dados dos filtros para obter todos os estados
    filtros_dados = load_data_for_tab("localizacao", apenas_filtros=True)
    todos_estados = sorted(filtros_dados['SG_UF_PROVA'].unique())
    
    if estados_selecionados:
        if len(estados_selecionados) == len(todos_estados):
            st.info("🇧🇷 **Escopo**: Todo o Brasil")
        else:
            st.info(f"📊 **Estados selecionados**: {len(estados_selecionados)}")
            
            # Mostrar detalhes da seleção
            if len(locais_selecionados) <= 5:
                for local in locais_selecionados:
                    st.write(f"• {local}")
            else:
                st.write(f"• {locais_selecionados[0]}")
                st.write(f"• {locais_selecionados[1]}")
                st.write(f"• ... e mais {len(locais_selecionados)-2}")
    else:
        st.warning("⚠️ Nenhum estado selecionado")

# Informações sobre o dataset
st.markdown("---")
st.markdown("### 📊 Sobre o Dataset")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.metric("Total de Registros", "4.000.000+", help="Número aproximado de candidatos no dataset")

with info_col2:
    st.metric("Estados Cobertos", "27", help="Todos os estados do Brasil + DF")

with info_col3:
    st.metric("Variáveis Analisadas", "16", help="Colunas principais para análise")

# Rodapé
st.markdown("---")

# Layout do rodapé
footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])

with footer_col1:
    try:
        logo = "Logo.jpg"
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
    st.markdown("""
    <div style='text-align: center; color: #636363;'>
        <p style='font-size: 16px;'><b>Dashboard de Análise do ENEM 2023</b></p>
        <br>
        <p style='font-size: 14px;'>Projeto de Iniciação Científica</p>
        <hr style='margin: 10px 0; border-color: #e0e0e0;'>
        <p style='font-size: 12px;'>© 2025 - Todos os direitos reservados</p>
        <p style='font-size: 11px; margin-top: 10px;'>v2.0.0 - Pages Migration</p>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    st.markdown("""
    <div style='text-align: right; color: #636363;'>
        <p style='font-size: 15px;'><b>Equipe</b></p>
        <p style='font-size: 14px; margin-bottom: 2px;'><b>Desenvolvedor:</b></p>
        <p style='font-size: 13px; margin-top: 0;'>Rafael Petit <br> rpetit.dev@gmail.com</p>
        <p style='font-size: 14px; margin-bottom: 2px; margin-top: 15px;'><b>Orientador:</b></p>
        <p style='font-size: 13px; margin-top: 0;'>Prof. Dr. César C. Xavier <br> cesarcx@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)

# Limpeza de memória
gc.collect()