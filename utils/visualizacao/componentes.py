import streamlit as st

def criar_filtros_comparativo(df_resultados, variaveis_categoricas, variavel_selecionada):
    """
    Cria e gerencia os filtros para a análise comparativa.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com resultados para visualização
    variaveis_categoricas: dict
        Dicionário com informações sobre variáveis categóricas
    variavel_selecionada: str
        Variável categórica selecionada
        
    Retorna:
    --------
    dict: Configurações dos filtros selecionados
    """
    # Configurar layout dos filtros em colunas
    col1, col2 = st.columns([1, 2])
    
    # Inicializar variáveis de configuração
    config = {
        'ordenar_decrescente': False,
        'mostrar_apenas_competencia': False,
        'competencia_filtro': None,
        'tipo_grafico': 'Gráfico de Barras'
    }
    
    # Seletor de tipo de gráfico
    config['tipo_grafico'] = st.radio(
        "Tipo de visualização:",
        ["Gráfico de Barras", "Gráfico de Linha"],
        horizontal=True,
        key="tipo_viz_desempenho"
    )
    
    # Primeira coluna: checkboxes
    with col1:
        config['ordenar_decrescente'] = st.checkbox(
            "Ordenar por valor decrescente", 
            value=False, 
            key="ordenar_viz_desempenho"
        )
        
        # Checkbox adicional condicionado ao primeiro
        if config['ordenar_decrescente']:
            config['mostrar_apenas_competencia'] = st.checkbox(
                "Mostrar apenas uma competência", 
                value=False,
                key="mostrar_apenas_competencia"
            )
    
    # Segunda coluna: seletor de competência (se necessário)
    if config['ordenar_decrescente']:
        with col2:
            competencias_disponiveis = df_resultados['Competência'].unique().tolist()
            config['competencia_filtro'] = st.selectbox(
                "Competência para ordenação:",
                options=competencias_disponiveis,
                key="competencia_filtro_desempenho"
            )
    
    return config


def criar_filtros_dispersao(colunas_notas, competencia_mapping):
    """
    Cria e gerencia os filtros para o gráfico de dispersão.
    
    Parâmetros:
    -----------
    colunas_notas: list
        Lista de colunas de notas
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
        
    Retorna:
    --------
    dict: Configurações dos filtros selecionados
    """
    # Configurar layout dos filtros em colunas
    col1, col2 = st.columns(2)
    
    # Inicializar configurações
    config = {
        'eixo_x': None,
        'eixo_y': None,
        'sexo': 'Todos',
        'tipo_escola': 'Todos',
        'excluir_notas_zero': True
    }
    
    # Primeira coluna de filtros
    with col1:
        config['eixo_x'] = st.selectbox(
            "Eixo X:", 
            options=colunas_notas, 
            format_func=lambda x: competencia_mapping[x],
            key="scatter_eixo_x"
        )
        config['sexo'] = st.selectbox(
            "Sexo:", 
            options=["Todos", "M", "F"], 
            key="scatter_sexo"
        )
        config['excluir_notas_zero'] = st.checkbox(
            "Desconsiderar notas zero", 
            value=True, 
            key="scatter_excluir_zeros"
        )
    
    # Segunda coluna de filtros
    with col2:
        config['eixo_y'] = st.selectbox(
            "Eixo Y:", 
            options=colunas_notas, 
            format_func=lambda x: competencia_mapping[x],
            key="scatter_eixo_y"
        )
        config['tipo_escola'] = st.selectbox(
            "Tipo de Escola:", 
            options=["Todos", "Federal", "Estadual", "Municipal", "Privada"],
            key="scatter_tipo_escola"
        )
    
    return config


def criar_filtros_estados(df_grafico):
    """
    Cria e gerencia os filtros para o gráfico de desempenho por estado.
    
    Parâmetros:
    -----------
    df_grafico: DataFrame
        DataFrame com dados para o gráfico
        
    Retorna:
    --------
    dict: Configurações dos filtros selecionados
    """
    # Configurar layout dos filtros em colunas
    col1, col2 = st.columns([1, 2])
    
    # Inicializar configurações
    config = {
        'ordenar_por_nota': False,
        'area_selecionada': None,
        'mostrar_apenas_area': False
    }
    
    # Primeira coluna: checkbox de ordenação
    with col1:
        config['ordenar_por_nota'] = st.checkbox(
            "Ordenar estados por desempenho", 
            value=False, 
            key="ordenar_estados_desempenho"
        )
    
    # Segunda coluna: filtros condicionais
    if config['ordenar_por_nota']:
        with col2:
            areas_disponiveis = df_grafico['Área'].unique().tolist()
            config['area_selecionada'] = st.selectbox(
                "Ordenar por área:",
                options=areas_disponiveis,
                key="area_ordenacao_desempenho"
            )
            
            config['mostrar_apenas_area'] = st.checkbox(
                "Mostrar apenas esta área", 
                value=False,
                key="mostrar_apenas_area_desempenho"
            )
    
    return config