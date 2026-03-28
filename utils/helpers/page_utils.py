import streamlit as st
from typing import List
import pandas as pd

from data.data_loader import load_data_for_tab
from utils.helpers.mappings import get_mappings


def clear_page_cache(page_name: str) -> None:
    """
    Registra a página atual no session_state.
    Não limpa cache — o Streamlit gerencia TTL e max_entries automaticamente.

    Parâmetros:
    -----------
    page_name : str
        Identificador da página atual ('geral', 'desempenho', 'aspectos_sociais')
    """
    st.session_state.current_page = page_name
    st.session_state.last_page = page_name


def init_page_session_state() -> None:
    """Inicializa session_state comum para todas as páginas."""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()

    if 'estados_selecionados' not in st.session_state:
        st.session_state.estados_selecionados = []

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
        Lista de estados selecionados (não usada para cache — dados são filtrados depois)

    Retorna:
    --------
    DataFrame: Dados carregados
    """
    @st.cache_data(ttl=600, max_entries=3, show_spinner=False)
    def _load_data(tab: str):
        return load_data_for_tab(tab)

    return _load_data(tab_name)


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
