import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def render_desempenho(microdados, microdados_estados, estados_selecionados, 
                     colunas_notas, competencia_mapping, race_mapping, 
                     variaveis_categoricas, desempenho_mapping):
    """
    Renderiza a aba de análise de desempenho no dashboard.
    
    Parâmetros:
    -----------
    microdados: DataFrame
        DataFrame completo com todos os dados
    microdados_estados: DataFrame
        DataFrame filtrado pelos estados selecionados
    estados_selecionados: list
        Lista de estados selecionados pelo usuário
    colunas_notas: list
        Lista de colunas contendo as notas de cada competência
    competencia_mapping: dict
        Mapeamento de códigos para nomes de competências
    race_mapping: dict
        Mapeamento de códigos para categorias de raça/cor
    variaveis_categoricas: dict
        Dicionário com informações sobre variáveis categóricas
    desempenho_mapping: dict
        Mapeamento de valores numéricos para categorias de desempenho
    """
    # Verificar se estados foram selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Mostrar informações sobre os estados selecionados
    mensagem = f"Analisando Desempenho para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(estados_selecionados)}"
    st.info(mensagem)
    
    # Criar cópia do DataFrame para trabalhar
    microdados_full = microdados_estados.copy()
    microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].map(desempenho_mapping)
    
    # Renderizar as seções principais
    exibir_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping)
    exibir_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping)


def calcular_seguro(serie, operacao='media'):
    """
    Calcula estatísticas de forma segura, tratando valores ausentes.
    
    Parâmetros:
    -----------
    serie: pandas.Series
        Série com os dados para cálculo
    operacao: str
        Tipo de operação ('media', 'mediana', 'min', 'max')
    
    Retorna:
    --------
    float: Resultado da operação ou 0 se não for possível calcular
    """
    if serie.empty:
        return 0
        
    if operacao == 'media':
        return serie.mean() if not pd.isna(serie.mean()) else 0
    elif operacao == 'mediana':
        return serie.median() if not pd.isna(serie.median()) else 0
    elif operacao == 'min':
        return serie.min() if not pd.isna(serie.min()) else 0
    elif operacao == 'max':
        return serie.max() if not pd.isna(serie.max()) else 0
    else:
        return 0


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
    st.markdown("### Análise Comparativa do Desempenho por Variáveis Demográficas")
    
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
    categorias_unicas = df_resultados['Categoria'].unique()
    ordem_categorias = variaveis_categoricas[variavel_selecionada].get('ordem')
    if not ordem_categorias:
        # Se não há ordem específica definida, usar ordem alfabética
        ordem_categorias = sorted(categorias_unicas)
    
    # Criar e exibir o gráfico
    fig = criar_grafico_comparativo(df_resultados, variavel_selecionada, variaveis_categoricas, 
                                    competencia_mapping, ordem_categorias)
    st.plotly_chart(fig, use_container_width=True)
    
    # Texto explicativo
    explicacao = f"""Este gráfico de barras apresenta a análise comparativa do desempenho dos estudantes agrupados por {variaveis_categoricas[variavel_selecionada]['nome']}. 

As barras mostram a média aritmética das notas obtidas em cada competência para cada grupo demográfico. Esta visualização permite identificar possíveis disparidades de desempenho entre diferentes grupos sociais."""
    st.info(explicacao)
    
    # Dados detalhados (opcional)
    with st.expander("Ver dados da análise"):
        pivot_df = df_resultados.pivot(index='Categoria', columns='Competência', values='Média').reset_index()
        st.dataframe(pivot_df, hide_index=True)


def preparar_dados_comparativo(microdados_full, variavel_selecionada, variaveis_categoricas, 
                               colunas_notas, competencia_mapping):
    """
    Prepara os dados para análise comparativa.
    
    Retorna:
    --------
    DataFrame: DataFrame com resultados para visualização
    """
    # Criar uma coluna com os valores mapeados
    nome_coluna_mapeada = f"{variavel_selecionada}_NOME"
    mapeamento = variaveis_categoricas[variavel_selecionada]["mapeamento"]
    
    # Aplicar mapeamento tratando valores NaN e garantindo strings
    microdados_full[nome_coluna_mapeada] = microdados_full[variavel_selecionada].apply(
        lambda x: str(mapeamento.get(x, f"Outro ({x})")) if pd.notna(x) else "Não informado"
    )
    
    # Calcular médias por categoria
    resultados = []
    categorias_unicas = microdados_full[nome_coluna_mapeada].unique()
    
    for categoria in categorias_unicas:
        dados_categoria = microdados_full[microdados_full[nome_coluna_mapeada] == categoria]
        for competencia in colunas_notas:
            media_comp = calcular_seguro(dados_categoria[competencia])
            resultados.append({
                'Categoria': categoria,
                'Competência': competencia_mapping[competencia],
                'Média': round(media_comp, 2)
            })
    
    # Criar DataFrame para visualização
    return pd.DataFrame(resultados)


def criar_grafico_comparativo(df_resultados, variavel_selecionada, variaveis_categoricas, 
                             competencia_mapping, ordem_categorias):
    """
    Cria o gráfico de barras comparativo.
    
    Retorna:
    --------
    figura: Objeto plotly.graph_objects.Figure
    """
    fig = px.bar(
        df_resultados,
        x='Categoria',
        y='Média',
        color='Competência',
        title=f"Desempenho por {variaveis_categoricas[variavel_selecionada]['nome']}",
        labels={
            'Categoria': variaveis_categoricas[variavel_selecionada]['nome'],
            'Média': 'Nota Média',
            'Competência': 'Área de Conhecimento'
        },
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Bold,
        category_orders={
            'Categoria': ordem_categorias,
            'Competência': list(competencia_mapping.values())
        }
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
    st.markdown("### Relação entre Competências")
    
    # Interface de controle com colunas para organização
    col1, col2 = st.columns(2)
    
    # Controles de seleção
    with col1:
        eixo_x = st.selectbox("Eixo X:", options=colunas_notas, 
                              format_func=lambda x: competencia_mapping[x])
        sexo = st.selectbox("Sexo:", options=["Todos", "M", "F"])
        excluir_notas_zero = st.checkbox("Desconsiderar notas zero", value=True)
    
    with col2:
        eixo_y = st.selectbox("Eixo Y:", options=colunas_notas, 
                              format_func=lambda x: competencia_mapping[x])
        tipo_escola = st.selectbox("Tipo de Escola:", 
                                   options=["Todos", "Federal", "Estadual", "Municipal", "Privada"])
    
    # Filtrar dados conforme seleções
    dados_filtrados = filtrar_dados_scatter(microdados_estados, sexo, tipo_escola, 
                                         eixo_x, eixo_y, excluir_notas_zero, race_mapping)
    
    # Criar e exibir gráfico
    fig = criar_grafico_scatter(dados_filtrados, eixo_x, eixo_y, competencia_mapping)
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicação do gráfico
    explicacao = f"""Este gráfico de dispersão mostra a relação entre as notas de {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}. 
    
Cada ponto representa um estudante, com sua posição indicando a pontuação obtida em cada uma das competências. As cores representam diferentes categorias de raça/cor, permitindo identificar padrões de desempenho entre grupos demográficos."""
    st.info(explicacao)


def filtrar_dados_scatter(microdados_estados, sexo, tipo_escola, eixo_x, eixo_y, 
                        excluir_notas_zero, race_mapping):
    """
    Filtra os dados para o gráfico de dispersão com base nas seleções do usuário.
    
    Retorna:
    --------
    DataFrame: DataFrame filtrado para visualização
    """
    # Cópia para evitar modificações no DataFrame original
    dados_filtrados = microdados_estados.copy()
    
    # Aplicar filtros demográficos
    if sexo != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['TP_SEXO'] == sexo]
    
    if tipo_escola != "Todos":
        tipo_map = {"Federal": 1, "Estadual": 2, "Municipal": 3, "Privada": 4}
        dados_filtrados = dados_filtrados[dados_filtrados['TP_DEPENDENCIA_ADM_ESC'] == tipo_map[tipo_escola]]
    
    # Guardar total após filtros demográficos
    total_apos_filtros = len(dados_filtrados)
    
    # Aplicar filtro de notas zero se solicitado
    if excluir_notas_zero:
        dados_filtrados = dados_filtrados[(dados_filtrados[eixo_x] > 0) & (dados_filtrados[eixo_y] > 0)]
        
        # Informar quantos registros foram removidos pelo filtro de notas zero
        registros_removidos = total_apos_filtros - len(dados_filtrados)
        if registros_removidos > 0:
            st.info(f"Foram desconsiderados {registros_removidos:,} registros com nota zero.")
    
    # Aplicar mapeamento para raça/cor
    dados_filtrados['RACA_COR'] = dados_filtrados['TP_COR_RACA'].map(race_mapping)
    
    return dados_filtrados


def criar_grafico_scatter(dados_filtrados, eixo_x, eixo_y, competencia_mapping):
    """
    Cria o gráfico de dispersão para análise da relação entre competências.
    
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
    
    # Opcional: adicionar linha de tendência global
    # fig.update_traces(mode='markers+lines')
    
    return fig