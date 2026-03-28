import streamlit as st
from typing import Any


def exibir_estatistica(
    titulo: str,
    valor: Any,
    prefixo: str = "• "
) -> None:
    """
    Exibe um item de estatística no formato padrão.
    Função compartilhada por todos os expanders.

    Parâmetros:
    -----------
    titulo : str
        Rótulo da estatística (ex: "Média", "Desvio Padrão")
    valor : Any
        Valor a ser exibido
    prefixo : str, default="• "
        Prefixo visual antes do texto
    """
    if titulo:
        st.write(f"{prefixo}**{titulo}:** {valor}")
    else:
        st.write(f"{prefixo}{valor}")
