import streamlit as st
import gc
from utils.mappings import get_mappings
from utils.data_loader import load_data_for_tab, agrupar_estados_em_regioes, release_memory

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
    
    if 'estados_selecionados' not in st.session_state:
        st.session_state.estados_selecionados = []
    
    if 'locais_selecionados' not in st.session_state:
        st.session_state.locais_selecionados = []

# Função para limpar cache e memória entre navegações
def clear_page_memory():
    """Limpa cache específico de páginas"""
    # Limpar apenas cache relacionado a dados específicos de páginas
    if hasattr(st.cache_data, 'clear'):
        st.cache_data.clear()
    gc.collect()

# Inicializar session state
init_session_state()

# Título principal
st.title("📊 Dashboard de Análise do ENEM - 2023")

# Carregar dados para filtros (apenas uma vez)
@st.cache_data(ttl=600, max_entries=1)
def load_filter_data():
    return load_data_for_tab("geral", apenas_filtros=True)

# Carregar filtros
with st.spinner("Carregando filtros..."):
    filtros_dados = load_filter_data()

# Obter mapeamentos
mappings = st.session_state.mappings
regioes_mapping = mappings['regioes_mapping']

# ---------------------------- FILTROS E CONTROLES ----------------------------
st.sidebar.header("🔧 Filtros de Seleção")

# Obter lista de todos os estados disponíveis
todos_estados = sorted(filtros_dados['SG_UF_PROVA'].unique())
todas_regioes = sorted(regioes_mapping.keys())

# Checkbox para selecionar todo o Brasil
selecionar_brasil = st.sidebar.checkbox("🇧🇷 Brasil (todos os estados)", value=True)

# Função para converter seleção de regiões em lista de estados
def get_estados_por_regiao(regioes_selecionadas):
    estados = []
    for regiao in regioes_selecionadas:
        estados.extend(regioes_mapping[regiao])
    return sorted(list(set(estados)))

# Lógica de seleção de estados
if selecionar_brasil:
    estados_selecionados = todos_estados
    regioes_selecionadas = todas_regioes
    
    st.sidebar.multiselect(
        "Regiões selecionadas:",
        options=todas_regioes,
        default=todas_regioes,
        disabled=True,
        help="Selecione regiões específicas quando a opção Brasil estiver desmarcada"
    )
    
    st.sidebar.multiselect(
        "Estados selecionados:",
        options=todos_estados,
        default=todos_estados,
        disabled=True,
        help="Todos os estados estão selecionados. Desmarque 'Brasil' para selecionar estados específicos."
    )
else:
    st.sidebar.markdown("#### 🗺️ Filtrar por região")
    
    regioes_selecionadas = st.sidebar.multiselect(
        "Selecione as regiões:",
        options=todas_regioes,
        default=[],
        help="Selecionar uma região automaticamente seleciona todos os seus estados"
    )
    
    estados_das_regioes = get_estados_por_regiao(regioes_selecionadas)
    
    st.sidebar.markdown("#### 🏛️ Filtrar por estado")
    
    estados_adicionais = st.sidebar.multiselect(
        "Selecione estados específicos:",
        options=[e for e in todos_estados if e not in estados_das_regioes],
        default=[],
        help="Selecione estados específicos além dos já incluídos pelas regiões selecionadas"
    )
    
    estados_selecionados = sorted(list(set(estados_das_regioes + estados_adicionais)))
    
    if not estados_selecionados:
        st.sidebar.warning("⚠️ Selecione pelo menos uma região ou estado, ou marque a opção Brasil.")

# Atualizar session_state com as seleções atuais
st.session_state.estados_selecionados = estados_selecionados
st.session_state.locais_selecionados = agrupar_estados_em_regioes(estados_selecionados, regioes_mapping)

# Mostrar resumo dos filtros
if estados_selecionados:
    if len(estados_selecionados) == len(todos_estados):
        st.sidebar.success("✅ Dados de todo o Brasil")
    else:
        if regioes_selecionadas:
            st.sidebar.success(f"✅ Regiões: {', '.join(regioes_selecionadas)}")
        if 'estados_adicionais' in locals() and estados_adicionais and not selecionar_brasil:
            st.sidebar.success(f"✅ Estados adicionais: {', '.join(estados_adicionais)}")
        st.sidebar.info(f"📊 Total: {len(estados_selecionados)} estados selecionados")

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
    
    if estados_selecionados:
        if len(estados_selecionados) == len(todos_estados):
            st.info("🇧🇷 **Escopo**: Todo o Brasil")
        else:
            st.info(f"📊 **Estados selecionados**: {len(estados_selecionados)}")
            
            # Mostrar detalhes da seleção
            if len(st.session_state.locais_selecionados) <= 5:
                for local in st.session_state.locais_selecionados:
                    st.write(f"• {local}")
            else:
                st.write(f"• {st.session_state.locais_selecionados[0]}")
                st.write(f"• {st.session_state.locais_selecionados[1]}")
                st.write(f"• ... e mais {len(st.session_state.locais_selecionados)-2}")
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
release_memory(filtros_dados)
gc.collect()