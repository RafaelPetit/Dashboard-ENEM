import streamlit as st
from typing import List, Tuple
from data.data_loader import load_data_for_tab, agrupar_estados_em_regioes
from utils.helpers.mappings import get_mappings

@st.cache_data(ttl=600, max_entries=1)
def load_filter_data():
    """Carrega dados apenas para filtros (otimizado)"""
    return load_data_for_tab("localizacao", apenas_filtros=True)

def render_sidebar_filters() -> Tuple[List[str], List[str]]:
    """
    Renderiza filtros laterais padronizados para todas as páginas
    
    Retorna:
    --------
    tuple: (estados_selecionados, locais_selecionados)
    """
    # Carregar dados para filtros
    with st.spinner("Carregando filtros..."):
        filtros_dados = load_filter_data()
    
    # Obter mapeamentos
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()
    
    mappings = st.session_state.mappings
    regioes_mapping = mappings['regioes_mapping']
    
    # ---------------------------- FILTROS SIDEBAR ----------------------------
    st.sidebar.header("🔧 Filtros de Seleção")
    
    # Obter lista de todos os estados disponíveis
    todos_estados = sorted(filtros_dados['SG_UF_PROVA'].unique())
    todas_regioes = sorted(regioes_mapping.keys())
    
    # Checkbox para selecionar todo o Brasil
    selecionar_brasil = st.sidebar.checkbox(
        "Sul, Sudeste e Centro-Oeste do Brasil (Todos os estados)", 
        value=True, 
        key="sidebar_brasil_checkbox"
    )
    
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
            key="sidebar_regioes_disabled",
            help="Selecione regiões específicas quando a opção Brasil estiver desmarcada"
        )
        
        st.sidebar.multiselect(
            "Estados selecionados:",
            options=todos_estados,
            default=todos_estados,
            disabled=True,
            key="sidebar_estados_disabled",
            help="Todos os estados estão selecionados. Desmarque 'Brasil' para selecionar estados específicos."
        )
    else:
        st.sidebar.markdown("#### 🗺️ Filtrar por região")
        
        regioes_selecionadas = st.sidebar.multiselect(
            "Selecione as regiões:",
            options=todas_regioes,
            default=[],
            key="sidebar_regioes_ativas",
            help="Selecionar uma região automaticamente seleciona todos os seus estados"
        )
        
        estados_das_regioes = get_estados_por_regiao(regioes_selecionadas)
        
        st.sidebar.markdown("#### 🏛️ Filtrar por estado")
        
        estados_adicionais = st.sidebar.multiselect(
            "Selecione estados específicos:",
            options=[e for e in todos_estados if e not in estados_das_regioes],
            default=[],
            key="sidebar_estados_adicionais",
            help="Selecione estados específicos além dos já incluídos pelas regiões selecionadas"
        )
        
        estados_selecionados = sorted(list(set(estados_das_regioes + estados_adicionais)))
        
        if not estados_selecionados:
            st.sidebar.warning("⚠️ Selecione pelo menos uma região ou estado, ou marque a opção Brasil.")
    
    # Gerar locais formatados
    locais_selecionados = agrupar_estados_em_regioes(estados_selecionados, regioes_mapping)
    
    # Atualizar session_state
    st.session_state.estados_selecionados = estados_selecionados
    st.session_state.locais_selecionados = locais_selecionados
    
    # Mostrar resumo dos filtros
    if estados_selecionados:
        if len(estados_selecionados) == len(todos_estados):
            st.sidebar.success("✅ Dados de todo o Sul, Sudeste e Centro-Oeste do Brasil selecionados")
        else:
            if regioes_selecionadas:
                st.sidebar.success(f"✅ Regiões: {', '.join(regioes_selecionadas)}")
            if 'estados_adicionais' in locals() and estados_adicionais and not selecionar_brasil:
                st.sidebar.success(f"✅ Estados adicionais: {', '.join(estados_adicionais)}")
            st.sidebar.info(f"📊 Total: {len(estados_selecionados)} estados selecionados")
    
    # Adicionar botão para ir ao Home
    st.sidebar.markdown("---")
    if st.sidebar.button("🏠 Voltar ao Home", use_container_width=True, key="sidebar_home_button"):
        st.switch_page("Página_Inicial.py")
    
    return estados_selecionados, locais_selecionados