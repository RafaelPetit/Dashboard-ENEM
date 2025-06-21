"""
Utilitários para filtros simplificados nas páginas.
"""

import streamlit as st
from typing import List, Dict, Tuple


def get_brazil_states() -> List[str]:
    """Retorna lista de todos os estados brasileiros."""
    return [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
        'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
        'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]


def get_regions_mapping() -> Dict[str, List[str]]:
    """Retorna mapeamento de regiões para estados."""
    return {
        'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
        'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
        'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
        'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
        'Sul': ['PR', 'RS', 'SC']
    }


def get_state_names() -> Dict[str, str]:
    """Retorna mapeamento de siglas para nomes dos estados."""
    return {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
        'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
        'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }


def render_state_filters() -> Tuple[List[str], List[str]]:
    """
    Renderiza filtros de estado na sidebar.
    
    Returns:
        Tuple contendo: (estados_selecionados, locais_selecionados_para_exibicao)
    """
    st.sidebar.markdown("## 🗺️ Filtros por Localização")
    
    # Checkbox para selecionar todo o Brasil
    todo_brasil = st.sidebar.checkbox(
        "Brasil (todos os estados)",
        value=True,
        key="brasil_checkbox",
        help="Marque para incluir dados de todos os estados brasileiros"
    )
    
    if todo_brasil:
        # Se todo Brasil está selecionado, mostrar seletores desabilitados
        regioes = list(get_regions_mapping().keys())
        estados = get_brazil_states()
        
        st.sidebar.multiselect(
            "Regiões selecionadas:",
            options=regioes,
            default=regioes,
            disabled=True,
            help="Todas as regiões estão incluídas",
            key="regions_disabled"
        )
        
        st.sidebar.multiselect(
            "Estados selecionados:",
            options=estados,
            default=estados,
            disabled=True,
            help="Todos os estados estão incluídos. Desmarque 'Brasil' para selecionar específicos.",
            key="states_disabled"
        )
        
        st.sidebar.success("✅ Dados de todo o Brasil")
        
        return estados, ["Todo o Brasil"]
    
    else:
        # Permitir seleção específica
        regions_mapping = get_regions_mapping()
        state_names = get_state_names()
        
        # Seletor de regiões
        st.sidebar.markdown("#### Filtrar por região")
        regioes_selecionadas = st.sidebar.multiselect(
            "Selecione as regiões:",
            options=list(regions_mapping.keys()),
            default=[],
            help="Selecionar uma região automaticamente inclui todos os seus estados",
            key="regions_selector"
        )
        
        # Obter estados das regiões selecionadas
        estados_das_regioes = []
        for regiao in regioes_selecionadas:
            estados_das_regioes.extend(regions_mapping[regiao])
        
        # Seletor de estados individuais
        st.sidebar.markdown("#### Filtrar por estado")
        estados_disponiveis = [estado for estado in get_brazil_states() if estado not in estados_das_regioes]
        
        if estados_das_regioes:
            st.sidebar.markdown(
                f"<p style='font-size:12px; color:#666;'>Estados das regiões selecionadas: {', '.join(estados_das_regioes)}</p>",
                unsafe_allow_html=True
            )
        
        estados_adicionais = st.sidebar.multiselect(
            "Selecione estados específicos:",
            options=estados_disponiveis,
            default=[],
            help="Selecione estados específicos além dos já incluídos pelas regiões",
            key="additional_states"
        )
        
        # Combinar todos os estados selecionados
        todos_estados_selecionados = sorted(list(set(estados_das_regioes + estados_adicionais)))
        
        # Validação
        if not todos_estados_selecionados:
            st.sidebar.warning("⚠️ Selecione pelo menos uma região ou estado, ou marque a opção Brasil.")
            return get_brazil_states(), ["Todo o Brasil"]  # Fallback para todo o Brasil
        
        # Mostrar resumo da seleção
        locais_para_exibicao = []
        
        if regioes_selecionadas:
            st.sidebar.success(f"✅ Regiões: {', '.join(regioes_selecionadas)}")
            locais_para_exibicao.extend(regioes_selecionadas)
        
        if estados_adicionais:
            nomes_estados_adicionais = [state_names[estado] for estado in estados_adicionais]
            st.sidebar.success(f"✅ Estados adicionais: {', '.join(nomes_estados_adicionais)}")
            locais_para_exibicao.extend(nomes_estados_adicionais)
        
        st.sidebar.info(f"Total: {len(todos_estados_selecionados)} estados selecionados")
        
        return todos_estados_selecionados, locais_para_exibicao


def render_data_info_sidebar() -> None:
    """Renderiza informações sobre os dados na sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ℹ️ Informações dos Dados")
    st.sidebar.markdown("""
    - **Fonte:** ENEM 2023
    - **Registros:** ~100k (amostra)
    - **Última atualização:** Jun 2025
    """)
    
    # Adicionar link para mais informações
    st.sidebar.markdown("---")
    with st.sidebar.expander("📚 Sobre o Dashboard"):
        st.markdown("""
        Este dashboard oferece análises interativas dos dados do ENEM 2023:
        
        - **Análise Geral:** Distribuições, médias e comparativos
        - **Aspectos Sociais:** Correlações socioeconômicas  
        - **Desempenho:** Análises por variáveis demográficas
        
        Navegue pelas páginas usando o menu lateral.
        """)
