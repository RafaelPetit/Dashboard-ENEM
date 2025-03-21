import streamlit as st
import plotly.express as px
import pandas as pd
from utils.tooltip import titulo_com_tooltip
from utils.prepara_dados.prepara_dados_desempenho import (
    preparar_dados_comparativo, 
    obter_ordem_categorias,
    preparar_dados_grafico_linha,
    preparar_dados_desempenho_geral,
    filtrar_dados_scatter,
    prepara_dados_grafico_linha_desempenho
)

def render_desempenho(microdados, microdados_estados, estados_selecionados, 
                     colunas_notas, competencia_mapping, race_mapping, 
                     variaveis_categoricas, desempenho_mapping):
    """
    Renderiza a aba de análise de desempenho no dashboard.
    """
    # Verificar se estados foram selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Mostrar informações sobre os estados selecionados
    mensagem = f"Analisando Desempenho para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(estados_selecionados)}"
    st.info(mensagem)
    
    # Preparar dados de desempenho geral
    microdados_full = preparar_dados_desempenho_geral(microdados_estados, colunas_notas, desempenho_mapping)
    
    # Menu para selecionar apenas a visualização desejada
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Análise Comparativa", "Relação entre Competências", "Médias por Estado"],
        horizontal=True
    )
    
    # Renderizar as seções principais
    exibir_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping)
    exibir_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping)
    exibir_grafico_linha_desempenho(microdados_estados, estados_selecionados, 
                                 colunas_notas, competencia_mapping)


def exibir_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping):
    """
    Exibe a análise comparativa do desempenho por variáveis demográficas.
    
    Parâmetros:
    -----------
    microdados_full: DataFrame
        DataFrame com os dados dos candidatos
    variaveis_categoricas: dict
        Dicionário com informações sobre variáveis categóricas
    colunas_notas: list
        Lista de colunas contendo as notas de cada competência
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
    """
    # Texto explicativo para o tooltip
    explicacao_tooltip = """
    Esta seção permite comparar o desempenho médio entre diferentes grupos demográficos.
    
    O gráfico mostra:
    - Como cada grupo se compara aos demais nas diversas competências
    - Possíveis disparidades de desempenho relacionadas a características socioeconômicas
    - Padrões consistentes ou variações entre áreas de conhecimento
    
    As análises consideram todos os candidatos nos estados selecionados.
    """
    
    # Título com tooltip explicativo
    titulo_com_tooltip("Análise Comparativa do Desempenho por Variáveis Demográficas", 
                     explicacao_tooltip, "comparativo_desempenho_tooltip")
    
    # Seleção da variável
    variavel_selecionada = st.selectbox(
        "Selecione a variável para análise:",
        options=list(variaveis_categoricas.keys()),
        format_func=lambda x: variaveis_categoricas[x]["nome"]
    )

    # Verificar se a variável está presente nos dados
    if variavel_selecionada not in microdados_full.columns:
        st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} não está disponível no conjunto de dados.")
        return
    
    # Preparar os dados para análise
    df_resultados = preparar_dados_comparativo(microdados_full, variavel_selecionada, 
                                             variaveis_categoricas, colunas_notas, competencia_mapping)
    
    # Determinar a ordem das categorias
    ordem_categorias = obter_ordem_categorias(df_resultados, variavel_selecionada, variaveis_categoricas)
    
    # Adicionar seletor de tipo de gráfico
    tipo_grafico = st.radio(
        "Tipo de visualização:",
        ["Gráfico de Barras", "Gráfico de Linha"],
        horizontal=True,
        key="tipo_viz_desempenho"
    )
    
    # Configurações comuns para ambos os tipos de gráfico
    col1, col2 = st.columns([1, 2])
    
    with col1:
        ordenar_decrescente = st.checkbox("Ordenar por valor decrescente", 
                                       value=False, 
                                       key="ordenar_viz_desempenho")
        
        # Seletor de competência e checkbox de filtro apenas se a ordenação estiver ativada
        competencia_filtro = None
        mostrar_apenas_competencia = False
        
        if ordenar_decrescente:
            mostrar_apenas_competencia = st.checkbox(
                "Mostrar apenas uma competência", 
                value=False,
                key="mostrar_apenas_competencia"
            )
    
    # Seletor de competência na segunda coluna, mas só se ordenação estiver ativada
    if ordenar_decrescente:
        with col2:
            # Seletor de competência para ordenação
            competencias_disponiveis = df_resultados['Competência'].unique().tolist()
            competencia_filtro = st.selectbox(
                "Competência para ordenação:",
                options=competencias_disponiveis,
                key="competencia_filtro_desempenho"
            )
    
    # Preparar dados com base nas configurações escolhidas
    competencia_para_filtro = competencia_filtro if mostrar_apenas_competencia else None
    df_visualizacao = preparar_dados_grafico_linha(
        df_resultados, 
        competencia_filtro,  # Competência para ordenação
        competencia_para_filtro,  # Competência para filtro
        ordenar_decrescente
    )
    
    # Criar e exibir o gráfico apropriado
    if tipo_grafico == "Gráfico de Barras":
        # Configurações específicas para o barmode
        barmode = 'relative' if mostrar_apenas_competencia else 'group'
        
        fig = criar_grafico_comparativo(
            df_visualizacao, 
            variavel_selecionada, 
            variaveis_categoricas, 
            competencia_mapping,
            barmode=barmode
        )
        st.plotly_chart(fig, use_container_width=True)
        
        explicacao = f"""Este gráfico de barras apresenta a análise comparativa do desempenho dos estudantes agrupados por {variaveis_categoricas[variavel_selecionada]['nome']}. 
        As barras mostram a média aritmética das notas obtidas em cada competência para cada grupo demográfico. Esta visualização permite identificar possíveis disparidades de desempenho entre diferentes grupos sociais."""
    
    else:  # Gráfico de Linha
        fig = criar_grafico_linha_desempenho(
            df_visualizacao, 
            variavel_selecionada, 
            variaveis_categoricas, 
            competencia_filtro if mostrar_apenas_competencia else None,
            ordenar_decrescente
        )
        st.plotly_chart(fig, use_container_width=True)
        
        explicacao = f"""Este gráfico de linha apresenta o desempenho médio dos estudantes em cada competência, agrupados por {variaveis_categoricas[variavel_selecionada]['nome']}. 
        Cada linha corresponde a uma competência, e os pontos mostram a nota média obtida por cada grupo demográfico. Esta visualização permite comparar tendências de desempenho entre diferentes grupos sociais e identificar padrões mais facilmente."""
    
    # Exibir explicação
    st.info(explicacao)
    
    # Dados detalhados (opcional)
    with st.expander("Ver dados da análise"):
        pivot_df = df_resultados.pivot(index='Categoria', columns='Competência', values='Média').reset_index()
        st.dataframe(pivot_df, hide_index=True)

def criar_grafico_linha_desempenho(df_linha, variavel_selecionada, variaveis_categoricas, 
                                competencia_filtro, ordenar_decrescente):
    """
    Cria o gráfico de linha para visualização do desempenho por categoria.
    
    Parâmetros:
    -----------
    df_linha: DataFrame
        DataFrame preparado para o gráfico de linha
    variavel_selecionada: str
        Nome da variável categórica selecionada
    variaveis_categoricas: dict
        Dicionário com informações sobre variáveis categóricas
    competencia_filtro: str
        Competência selecionada para filtro/ordenação
    ordenar_decrescente: bool
        Indica se as categorias estão ordenadas por valor
        
    Retorna:
    --------
    figura: Objeto plotly.graph_objects.Figure
    """
    # Determinar título adequado
    ordenacao_texto = " (ordenado por valor decrescente)" if ordenar_decrescente else ""
    filtro_texto = f" - {competencia_filtro}" if len(df_linha['Competência'].unique()) == 1 else ""
    
    fig = px.line(
        df_linha,
        x='Categoria',
        y='Média',
        color='Competência',
        markers=True,
        title=f"Desempenho por {variaveis_categoricas[variavel_selecionada]['nome']}{filtro_texto}{ordenacao_texto}",
        labels={
            'Categoria': variaveis_categoricas[variavel_selecionada]['nome'],
            'Média': 'Nota Média',
            'Competência': 'Área de Conhecimento'
        },
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1, 
            title=dict(text="Área de Conhecimento <br><sup>Clique para filtrar</sup>"),
        )
    )
    
    return fig


def criar_grafico_comparativo(df_resultados, variavel_selecionada, variaveis_categoricas, 
                            competencia_mapping, barmode='group'):
    """
    Cria o gráfico de barras comparativo.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame preparado com os resultados para visualização
    variavel_selecionada: str
        Nome da variável categórica selecionada
    variaveis_categoricas: dict
        Dicionário com informações sobre variáveis categóricas
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
    barmode: str
        Modo de exibição das barras ('group' ou 'relative')
        
    Retorna:
    --------
    figura: Objeto plotly.graph_objects.Figure
    """
    # Determinar título adequado
    ordenacao_texto = ""
    filtro_texto = ""
    
    # Verificar se estamos usando ordenação (pelo formato do DataFrame)
    competencias_unicas = df_resultados['Competência'].unique()
    if isinstance(df_resultados['Categoria'].dtype, pd.CategoricalDtype) and df_resultados['Categoria'].dtype.ordered:
        ordenacao_texto = " (ordenado por valor decrescente)"
    
    # Verificar se estamos filtrando por competência
    if len(competencias_unicas) == 1:
        filtro_texto = f" - {competencias_unicas[0]}"
    
    # Criar gráfico
    fig = px.bar(
        df_resultados,
        x='Categoria',
        y='Média',
        color='Competência',
        title=f"Desempenho por {variaveis_categoricas[variavel_selecionada]['nome']}{filtro_texto}{ordenacao_texto}",
        labels={
            'Categoria': variaveis_categoricas[variavel_selecionada]['nome'],
            'Média': 'Nota Média',
            'Competência': 'Área de Conhecimento'
        },
        barmode=barmode,  # Usar o modo especificado
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1, 
            title=dict(text="Área de Conhecimento <br><sup>Clique para filtrar</sup>"),
        )
    )
    
    return fig


def exibir_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping):
    """
    Exibe o gráfico de dispersão para análise da relação entre competências.
    
    Parâmetros:
    -----------
    microdados_estados: DataFrame
        DataFrame filtrado pelos estados selecionados
    colunas_notas: list
        Lista de colunas contendo as notas de cada competência
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
    race_mapping: dict
        Mapeamento de códigos para categorias de raça/cor
    """
    # Texto explicativo para o tooltip
    explicacao_tooltip = """
    Esta visualização permite analisar a correlação entre o desempenho em diferentes competências.
    
    Cada ponto no gráfico representa um candidato, com suas coordenadas determinadas pelas notas nas 
    duas competências selecionadas. As cores indicam a raça/cor autodeclarada.
    
    Você pode:
    - Selecionar quais competências comparar (eixos X e Y)
    - Filtrar por sexo e tipo de escola
    - Remover candidatos com nota zero (frequentemente ausentes na prova)
    
    Padrões de dispersão e agrupamentos podem revelar relações entre habilidades e desigualdades 
    educacionais entre diferentes grupos demográficos.
    """
    
    # Título com tooltip explicativo
    titulo_com_tooltip("Relação entre Competências", explicacao_tooltip, "relacao_competencias_tooltip")
    
    # Interface de controle com colunas para organização
    col1, col2 = st.columns(2)
    
    # Controles de seleção
    with col1:
        eixo_x = st.selectbox("Eixo X:", options=colunas_notas, 
                             format_func=lambda x: competencia_mapping[x],
                             key="scatter_eixo_x")
        sexo = st.selectbox("Sexo:", options=["Todos", "M", "F"], key="scatter_sexo")
        excluir_notas_zero = st.checkbox("Desconsiderar notas zero", value=True, key="scatter_excluir_zeros")
    
    with col2:
        eixo_y = st.selectbox("Eixo Y:", options=colunas_notas, 
                             format_func=lambda x: competencia_mapping[x],
                             key="scatter_eixo_y")
        tipo_escola = st.selectbox("Tipo de Escola:", 
                                  options=["Todos", "Federal", "Estadual", "Municipal", "Privada"],
                                  key="scatter_tipo_escola")
    
    # Filtrar dados conforme seleções
    dados_filtrados, registros_removidos = filtrar_dados_scatter(
        microdados_estados, sexo, tipo_escola, eixo_x, eixo_y, 
        excluir_notas_zero, race_mapping
    )
    
    # Informar quantos registros foram removidos pelo filtro de notas zero
    if excluir_notas_zero and registros_removidos > 0:
        st.info(f"Foram desconsiderados {registros_removidos:,} registros com nota zero.")
    
    # Criar e exibir gráfico
    fig = criar_grafico_scatter(dados_filtrados, eixo_x, eixo_y, competencia_mapping)
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicação do gráfico
    explicacao = f"""Este gráfico de dispersão mostra a relação entre as notas de {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}. 
    
Cada ponto representa um estudante, com sua posição indicando a pontuação obtida em cada uma das competências. As cores representam diferentes categorias de raça/cor, permitindo identificar padrões de desempenho entre grupos demográficos."""
    st.info(explicacao)
    
    # Adicionar métricas estatísticas
    with st.expander("Ver estatísticas detalhadas"):
        # Calcular correlação de Pearson entre as competências
        correlacao = dados_filtrados[eixo_x].corr(dados_filtrados[eixo_y])
        
        # Exibir coeficiente de correlação
        st.write(f"**Coeficiente de correlação de Pearson:** {correlacao:.4f}")
        st.write("""
        Interpretação:
        - Próximo a 1: Forte correlação positiva (quando uma nota aumenta, a outra tende a aumentar)
        - Próximo a 0: Ausência de correlação linear
        - Próximo a -1: Forte correlação negativa (quando uma nota aumenta, a outra tende a diminuir)
        """)
        
        # Estatísticas descritivas das duas competências
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Estatísticas para {competencia_mapping[eixo_x]}:**")
            stats_x = dados_filtrados[eixo_x].describe().round(2)
            st.dataframe(stats_x)
            
        with col2:
            st.write(f"**Estatísticas para {competencia_mapping[eixo_y]}:**")
            stats_y = dados_filtrados[eixo_y].describe().round(2)
            st.dataframe(stats_y)


def criar_grafico_scatter(dados_filtrados, eixo_x, eixo_y, competencia_mapping):
    """
    Cria o gráfico de dispersão para análise da relação entre competências.
    
    Parâmetros:
    -----------
    dados_filtrados: DataFrame
        DataFrame filtrado com os dados a serem plotados
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
        
    Retorna:
    --------
    figura: Objeto plotly.graph_objects.Figure
    """
    fig = px.scatter(
        dados_filtrados, 
        x=eixo_x, 
        y=eixo_y,
        title=f"Relação entre {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}",
        labels={
            eixo_x: competencia_mapping[eixo_x], 
            eixo_y: competencia_mapping[eixo_y],
            'RACA_COR': 'COR/RAÇA'
        },
        opacity=0.5,
        color="RACA_COR",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # Adicionar linha de tendência (regressão linear)
    fig.update_layout(
        height=500,
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend_title_text="COR/RAÇA",
        legend=dict(
            title=dict(text="COR/RAÇA<br><sup>Clique para filtrar</sup>"),
        )
    )
    
    # Adicionar linha de tendência
    fig.update_traces(mode='markers')
    
    return fig

def exibir_grafico_linha_desempenho(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """
    Exibe gráfico de linha mostrando o desempenho médio por estado.
    
    Parâmetros:
    -----------
    microdados_estados: DataFrame
        DataFrame com os dados filtrados pelos estados selecionados
    estados_selecionados: list
        Lista de siglas dos estados selecionados
    colunas_notas: list
        Lista de colunas contendo as notas de cada competência
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
    """
    # Texto explicativo para o tooltip do título
    explicacao_tooltip = """
    Este gráfico compara as médias de desempenho dos candidatos por estado e área de conhecimento.
    
    Você pode:
    • Visualizar as médias de cada área de conhecimento em todos os estados selecionados
    • Ordenar os estados em ordem decrescente de desempenho
    • Analisar apenas uma área específica se desejar
    
    As médias são calculadas considerando apenas notas válidas (maiores que zero).
    A linha "Média Geral" mostra a média aritmética de todas as áreas para cada estado.
    """
    
    # Usar título com tooltip em vez de subheader
    titulo_com_tooltip("Médias por Estado e Área de Conhecimento", explicacao_tooltip, "grafico_linha_desempenho_tooltip")
    
    # Preparar os dados para o gráfico
    df_grafico = prepara_dados_grafico_linha_desempenho(
        microdados_estados, 
        estados_selecionados, 
        colunas_notas, 
        competencia_mapping
    )
    
    # Obter todas as áreas disponíveis no DataFrame
    areas_disponiveis = df_grafico['Área'].unique().tolist()
    
    # Interface para ordenação
    col1, col2 = st.columns([1, 2])
    with col1:
        ordenar_por_nota = st.checkbox("Ordenar estados por desempenho", value=False, key="ordenar_estados_desempenho")
    
    # Mostrar seletor de área apenas se o usuário escolheu ordenar
    area_selecionada = None
    mostrar_apenas_area = False
    
    if ordenar_por_nota:
        with col2:
            area_selecionada = st.selectbox(
                "Ordenar por área:",
                options=areas_disponiveis,
                key="area_ordenacao_desempenho"
            )
            
            # Opção para mostrar apenas a área selecionada
            mostrar_apenas_area = st.checkbox(
                "Mostrar apenas esta área", 
                value=False,
                key="mostrar_apenas_area_desempenho"
            )
    
    # Criar uma cópia do DataFrame para não modificar o original
    df_plot = df_grafico.copy()
    
    # Se o usuário escolheu ordenar, reorganizamos os dados
    if ordenar_por_nota and area_selecionada:
        # Usar a área selecionada para ordenação
        media_por_estado = df_plot[df_plot['Área'] == area_selecionada].copy()
            
        # Criar um mapeamento da ordem dos estados com base na área selecionada
        ordem_estados = media_por_estado.sort_values('Média', ascending=False)['Estado'].tolist()
        
        # Reordenar o DataFrame usando o mapeamento
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        # Filtrar para mostrar apenas a área selecionada se solicitado
        if mostrar_apenas_area:
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    
    # Criar o gráfico com os dados preparados
    fig = px.line(
        df_plot,
        x='Estado',
        y='Média',
        color='Área',
        markers=True,
        title='Médias de Desempenho por Estado e Área de Conhecimento',
        labels={'Média': 'Nota Média', 'Estado': 'Estado', 'Área': 'Área de Conhecimento'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Estado",
        yaxis_title="Nota Média",
        legend_title="Área de Conhecimento",
        xaxis=dict(tickangle=-45),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=dict(text="Área de Conhecimento<br><sup>Clique para filtrar</sup>"),
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicação para o gráfico de linha
    explicacao = f"""
    Este gráfico mostra a média de desempenho de cada estado nas diferentes áreas de conhecimento. 
    
    Cada linha colorida representa uma área de conhecimento, e os pontos mostram a média de notas para cada estado naquela área. A linha "Média Geral" (se visível) representa a média de todas as áreas combinadas.
    
    Esta visualização permite identificar facilmente:
    Estados com melhor desempenho geral, possíveis disparidades regionais em áreas específicas, padrões de consistência ou variação no desempenho por área
    """
    st.info(explicacao)
    
    # Dados detalhados (opcional)
    with st.expander("Ver dados detalhados"):
        pivot_df = df_grafico.pivot(index='Estado', columns='Área', values='Média').reset_index()
        st.dataframe(pivot_df, hide_index=True)