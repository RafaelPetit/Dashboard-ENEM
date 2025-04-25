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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        eixo_x = st.selectbox('Eixo X:', colunas_notas, format_func=lambda x: competencia_mapping[x])
    with col2:
        eixo_y = st.selectbox('Eixo Y:', [col for col in colunas_notas if col != eixo_x], 
                            format_func=lambda x: competencia_mapping[x])
    with col3:
        excluir_notas_zero = st.checkbox('Excluir notas zero', value=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sexo = st.selectbox('Filtrar por gênero:', ['Todos', 'M', 'F'], 
                        format_func=lambda x: 'Todos' if x == 'Todos' else 'Masculino' if x == 'M' else 'Feminino')
    with col2:
        tipo_escola = st.selectbox('Filtrar por tipo de escola:', ['Todos', 'Pública', 'Privada'])
    
    # Novo filtro para faixa salarial
    with col3:
        # Definir as opções de faixa salarial com labels amigáveis
        faixa_salarial_opcoes = {
            'Todas': None, 
            'Nenhuma Renda': 0,
            'Até 1 Salário Mínimo': 1,
            '1 a 2 Salários Mínimos': 2,
            '2 a 3 Salários Mínimos': 3,
            '3 a 5 Salários Mínimos': 4,
            '5 a 10 Salários Mínimos': 5, 
            '10 a 20 Salários Mínimos': 6,
            'Mais de 20 Salários Mínimos': 7
        }
        
        faixa_salarial_label = st.selectbox('Filtrar por faixa salarial:', list(faixa_salarial_opcoes.keys()))
        faixa_salarial = faixa_salarial_opcoes[faixa_salarial_label]
    
    # Novo filtro para colorir por faixa salarial
    col1, col2 = st.columns(2)
    with col1:
        colorir_por_faixa = st.checkbox('Colorir por faixa salarial', value=False)
    
    return {
        'eixo_x': eixo_x,
        'eixo_y': eixo_y,
        'excluir_notas_zero': excluir_notas_zero,
        'sexo': None if sexo == 'Todos' else sexo,
        'tipo_escola': None if tipo_escola == 'Todos' else tipo_escola,
        'faixa_salarial': faixa_salarial,  # Novo campo
        'colorir_por_faixa': colorir_por_faixa  # Novo campo
    }


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