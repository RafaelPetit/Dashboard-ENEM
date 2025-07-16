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
    
    st.sidebar.header("🔧 Filtros de Seleção")
    
    # Obter lista de todos os estados disponíveis
    todos_estados = sorted(filtros_dados['SG_UF_PROVA'].unique())
    todas_regioes = sorted(regioes_mapping.keys())

    # Função para converter seleção de regiões em lista de estados
    def get_estados_por_regiao(regioes_selecionadas):
        estados = []
        for regiao in regioes_selecionadas:
            estados.extend(regioes_mapping[regiao])
        return sorted(list(set(estados)))

    st.sidebar.markdown("#### 🗺️ Filtrar por região")
    regioes_selecionadas = st.sidebar.multiselect(
        "Selecione as regiões:",
        options=todas_regioes,
        default=[],
        key="sidebar_regioes_ativas",
        help="Selecione uma ou mais regiões para filtrar os estados disponíveis"
    )

    # Lógica: se nenhuma região for selecionada, mostra todos os estados.
    # Se uma ou mais regiões forem selecionadas, mostra apenas os estados dessas regiões.
    if not regioes_selecionadas:
        estados_disponiveis = todos_estados
    else:
        estados_disponiveis = get_estados_por_regiao(regioes_selecionadas)

    # Recupera seleção anterior de estados (se houver)
    estados_selecionados_anteriores = st.session_state.get("sidebar_estados_ativos", [])

    # Mantém selecionados apenas os estados ainda disponíveis
    if not regioes_selecionadas:
        estados_default = todos_estados
    else:
        estados_default = estados_disponiveis

    st.sidebar.markdown("#### 🏛️ Filtrar por estado")
    estados_selecionados = st.sidebar.multiselect(
        "Selecione os estados:",
        options=estados_disponiveis,
        default=estados_default,
        key="sidebar_estados_ativos",
        help="Selecione os estados que deseja analisar"
    )


    if not estados_selecionados:
        st.sidebar.warning("⚠️ Selecione pelo menos um estado para continuar.")

    # Gerar locais formatados
    locais_selecionados = agrupar_estados_em_regioes(estados_selecionados, regioes_mapping)

    # Atualizar session_state
    st.session_state.estados_selecionados = estados_selecionados
    st.session_state.locais_selecionados = locais_selecionados

    # Mostrar resumo dos filtros
    if estados_selecionados:
        if len(estados_selecionados) == len(todos_estados):
            st.sidebar.success("✅ Todos os estados selecionados")
        else:
            if regioes_selecionadas:
                st.sidebar.success(f"✅ Regiões filtradas: {', '.join(regioes_selecionadas)}")
            st.sidebar.info(f"📊 Total: {len(estados_selecionados)} estados selecionados")

    st.sidebar.markdown("---")
    if st.sidebar.button("🏠 Voltar a Página Inicial", use_container_width=True, key="sidebar_home_button"):
        st.switch_page("Página_Inicial.py")
    
    return estados_selecionados, locais_selecionados