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


def get_cached_data(tab_name: str) -> pd.DataFrame:
    """
    Carrega dados para uma página específica.
    Delega diretamente para load_data_for_tab que já tem @st.cache_data(ttl=3600).

    Parâmetros:
    -----------
    tab_name : str
        Nome da aba/tab ('geral', 'desempenho', 'aspectos_sociais')

    Retorna:
    --------
    DataFrame: Dados carregados
    """
    return load_data_for_tab(tab_name)


def get_all_cached_data(tab_name: str) -> pd.DataFrame:
    """
    Carrega todos os dados para uma página.
    Delega diretamente para load_data_for_tab que já tem @st.cache_data(ttl=3600).
    Eliminada a camada extra de cache que duplicava dados em memória (fix P2.1).

    Parâmetros:
    -----------
    tab_name : str
        Nome da aba/tab ('geral', 'desempenho', 'aspectos_sociais')

    Retorna:
    --------
    DataFrame: Todos os dados carregados
    """
    return load_data_for_tab(tab_name)
