import gc
import streamlit as st
from typing import List, Tuple
import pandas as pd

from data.data_loader import load_data_for_tab
from utils.helpers.mappings import get_mappings


def clear_page_cache(page_name: str) -> None:
    """
    Limpa cache ao trocar de página.

    Parâmetros:
    -----------
    page_name : str
        Identificador da página atual ('geral', 'desempenho', 'aspectos_sociais')
    """
    st.session_state.current_page = page_name

    if hasattr(st.session_state, 'last_page') and st.session_state.last_page != page_name:
        st.cache_data.clear()
        gc.collect()

    st.session_state.last_page = page_name


def init_page_session_state() -> None:
    """Inicializa session_state comum para todas as páginas."""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()

    if 'estados_selecionados' not in st.session_state:
        st.session_state.estados_selecionados = []
        st.warning("⚠️ Nenhum estado selecionado. Volte à página inicial para configurar os filtros.")
        st.stop()

    if 'locais_selecionados' not in st.session_state:
        st.session_state.locais_selecionados = []


def get_cached_data(tab_name: str, estados_selecionados: List[str]) -> pd.DataFrame:
    """
    Carrega dados otimizados para uma página específica com cache.

    Parâmetros:
    -----------
    tab_name : str
        Nome da aba/tab ('geral', 'desempenho', 'aspectos_sociais')
    estados_selecionados : List[str]
        Lista de estados selecionados (usada como chave de cache)

    Retorna:
    --------
    DataFrame: Dados carregados
    """
    @st.cache_data(ttl=600, max_entries=2, show_spinner=False)
    def _load_data(tab: str, estados_key: str):
        return load_data_for_tab(tab)

    estados_key = "_".join(sorted(estados_selecionados))
    return _load_data(tab_name, estados_key)


def get_all_cached_data(tab_name: str) -> pd.DataFrame:
    """
    Carrega TODOS os dados (não filtrados) para uma página com cache.

    Parâmetros:
    -----------
    tab_name : str
        Nome da aba/tab ('geral', 'desempenho', 'aspectos_sociais')

    Retorna:
    --------
    DataFrame: Todos os dados carregados
    """
    @st.cache_data(ttl=600, max_entries=1, show_spinner=False)
    def _load_all_data(tab: str):
        return load_data_for_tab(tab)

    return _load_all_data(tab_name)
