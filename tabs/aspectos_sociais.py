import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_aspectos_sociais(microdados_estados, estados_selecionados, variaveis_sociais):
    """
    Renderiza a aba de Aspectos Sociais com visualizações de correlações entre variáveis sociais.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados apenas dos estados selecionados
    estados_selecionados : list
        Lista com as siglas dos estados selecionados pelo usuário
    variaveis_sociais : dict
        Dicionário com as variáveis sociais disponíveis e seus mapeamentos
    """
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Informar ao usuário quais estados estão sendo considerados
    mensagem = f"Analisando Aspectos Sociais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(estados_selecionados)}"
    st.info(mensagem)
    
    # Renderizar as duas seções principais
    exibir_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, variaveis_sociais)
    exibir_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais)


def exibir_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, variaveis_sociais):
    """
    Exibe gráficos de correlação entre dois aspectos sociais selecionados.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados dos estados selecionados
    estados_selecionados : list
        Lista de estados selecionados
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis sociais
    """
    st.header("Correlação entre Aspectos Sociais")
    
    # Seleção do tipo de visualização
    tipo_grafico = st.radio(
        "Escolha o tipo de visualização:",
        ["Heatmap", "Barras Empilhadas", "Sankey"],
        horizontal=True
    )
    
    # Seleção das variáveis para correlação
    col1, col2 = st.columns(2)
    with col1:
        var_x = st.selectbox(
            "Variável X (Linhas/Origem):", 
            options=list(variaveis_sociais.keys()),
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="var_x_social"
        )
    with col2:
        # Filtrar para não repetir a mesma variável
        opcoes_y = [k for k in variaveis_sociais.keys() if k != var_x]
        var_y = st.selectbox(
            "Variável Y (Colunas/Destino):", 
            options=opcoes_y,
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="var_y_social"
        )
    
    # Verificar se as variáveis selecionadas existem nos dados
    if var_x not in microdados_estados.columns or var_y not in microdados_estados.columns:
        st.warning(f"Uma ou ambas as variáveis selecionadas não estão disponíveis no conjunto de dados.")
        return
    
    # Preparar dados para visualização
    df_preparado, var_x_plot, var_y_plot = preparar_dados_correlacao(
        microdados_estados, var_x, var_y, variaveis_sociais
    )
    
    # Texto para indicar estados no título
    estados_texto = ', '.join(estados_selecionados) if len(estados_selecionados) <= 3 else f"{len(estados_selecionados)} estados selecionados"
    
    # Criar visualização com base na escolha do usuário
    if tipo_grafico == "Heatmap":
        fig, explicacao = criar_grafico_heatmap(df_preparado, var_x, var_y, 
                                              var_x_plot, var_y_plot, 
                                              variaveis_sociais, estados_texto)
        
    elif tipo_grafico == "Barras Empilhadas":
        fig, explicacao = criar_grafico_barras_empilhadas(df_preparado, var_x, var_y, 
                                                        var_x_plot, var_y_plot, 
                                                        variaveis_sociais, estados_texto)
        
    else:  # Sankey
        fig, explicacao = criar_grafico_sankey(df_preparado, var_x, var_y, 
                                             var_x_plot, var_y_plot, 
                                             variaveis_sociais, estados_texto)
    
    # Exibir o gráfico e explicação
    st.plotly_chart(fig, use_container_width=True)
    st.info(explicacao)


def preparar_dados_correlacao(microdados, var_x, var_y, variaveis_sociais):
    """
    Prepara os dados para análise de correlação entre duas variáveis.
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com os dados a serem analisados
    var_x, var_y : str
        Nomes das variáveis a serem correlacionadas
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis
        
    Retorna:
    --------
    tuple
        (DataFrame com dados preparados, nome da coluna X para plotar, nome da coluna Y para plotar)
    """
    df_correlacao = microdados.copy()
    
    # Aplicar mapeamentos para variável X
    if var_x in variaveis_sociais and df_correlacao[var_x].dtype != 'object':
        df_correlacao[f'{var_x}_NOME'] = df_correlacao[var_x].map(variaveis_sociais[var_x]["mapeamento"])
        var_x_plot = f'{var_x}_NOME'
    else:
        var_x_plot = var_x
        
    # Aplicar mapeamentos para variável Y
    if var_y in variaveis_sociais and df_correlacao[var_y].dtype != 'object':
        df_correlacao[f'{var_y}_NOME'] = df_correlacao[var_y].map(variaveis_sociais[var_y]["mapeamento"])
        var_y_plot = f'{var_y}_NOME'
    else:
        var_y_plot = var_y
    
    return df_correlacao, var_x_plot, var_y_plot


def criar_grafico_heatmap(df_correlacao, var_x, var_y, var_x_plot, var_y_plot, 
                        variaveis_sociais, estados_texto):
    """
    Cria um heatmap para visualizar a correlação entre duas variáveis.
    
    Retorna:
    --------
    tuple
        (figura do gráfico, texto explicativo)
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Calcular percentuais (normalização)
    contagem_pivot = contagem.pivot(index=var_x_plot, columns=var_y_plot, values='Contagem')
    
    # Substituir NaN por 0
    contagem_pivot = contagem_pivot.fillna(0)
    
    # Normalizar por linha (para mostrar distribuição percentual)
    normalized_pivot = contagem_pivot.div(contagem_pivot.sum(axis=1), axis=0) * 100
    
    # Criar heatmap
    fig = px.imshow(
        normalized_pivot,
        labels=dict(
            x=variaveis_sociais[var_y]["nome"],
            y=variaveis_sociais[var_x]["nome"],
            color="Percentagem (%)"
        ),
        x=normalized_pivot.columns,
        y=normalized_pivot.index,
        color_continuous_scale='YlGnBu',
        title=f"Relação entre {variaveis_sociais[var_x]['nome']} e {variaveis_sociais[var_y]['nome']}",
        text_auto='.1f'  # Mostrar valores com 1 casa decimal
    )
    
    # Ajustar layout
    fig.update_layout(
        height=500,
        xaxis={'side': 'bottom', 'tickangle': -45},
        coloraxis_colorbar=dict(title="Percentual (%)"),
        plot_bgcolor='white',
        font=dict(size=12)
    )
    
    # Texto explicativo
    explicacao = f"""
        Este heatmap mostra a distribuição percentual de {variaveis_sociais[var_y]['nome']} para cada categoria de {variaveis_sociais[var_x]['nome']}.
        As cores mais escuras indicam maior concentração percentual, e os valores mostrados são percentuais por linha.
    """
    
    return fig, explicacao


def criar_grafico_barras_empilhadas(df_correlacao, var_x, var_y, var_x_plot, var_y_plot, 
                                  variaveis_sociais, estados_texto):
    """
    Cria um gráfico de barras empilhadas para visualizar a correlação entre duas variáveis.
    
    Retorna:
    --------
    tuple
        (figura do gráfico, texto explicativo)
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Preparar dados para barras empilhadas
    df_barras = contagem.copy()
    df_barras['Percentual'] = 0.0
    
    # Calcular percentual por categoria X
    for idx, row in df_barras.iterrows():
        total = df_barras[df_barras[var_x_plot] == row[var_x_plot]]['Contagem'].sum()
        df_barras.at[idx, 'Percentual'] = (row['Contagem'] / total * 100) if total > 0 else 0
    
    # Criar gráfico de barras empilhadas
    fig = px.bar(
        df_barras,
        x=var_x_plot,
        y='Percentual',
        color=var_y_plot,
        title=f"Distribuição de {variaveis_sociais[var_y]['nome']} por {variaveis_sociais[var_x]['nome']} ({estados_texto})",
        labels={
            var_x_plot: variaveis_sociais[var_x]['nome'],
            'Percentual': 'Percentual (%)',
            var_y_plot: variaveis_sociais[var_y]['nome']
        },
        text_auto='.1f',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Ajustar layout para barras empilhadas com legenda interativa
    fig.update_layout(
        height=500,
        xaxis={'tickangle': -45},
        plot_bgcolor='white',
        barmode='stack',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        # Configuração de legenda otimizada para muitas categorias
        legend=dict(
            title=dict(text=f"{variaveis_sociais[var_y]['nome']} <br><sup>Clique para filtrar</sup>"),
            orientation="v",  # Muda para vertical (lado direito)
            yanchor="top",    # Ancora no topo
            y=1.0,           # Posição Y no topo
            xanchor="left",   # Ancora à esquerda da posição
            x=1.02,          # Posição X ligeiramente fora do gráfico
            itemsizing="constant",  # Mantém tamanho constante dos itens
            # Definir número máximo de itens por coluna
            entrywidth=70,
            entrywidthmode="fraction",
            traceorder="normal",
        )
    )
    
    # Texto explicativo
    explicacao = f"""
        Este gráfico de barras empilhadas mostra a distribuição percentual de {variaveis_sociais[var_y]['nome']} 
        para cada categoria de {variaveis_sociais[var_x]['nome']}. Cada cor representa uma categoria de {variaveis_sociais[var_y]['nome']},
        e a altura da barra indica o percentual dentro de cada categoria de {variaveis_sociais[var_x]['nome']}.
    """
    
    return fig, explicacao


def criar_grafico_sankey(df_correlacao, var_x, var_y, var_x_plot, var_y_plot, 
                       variaveis_sociais, estados_texto):
    """
    Cria um diagrama de Sankey para visualizar o fluxo entre duas variáveis.
    
    Retorna:
    --------
    tuple
        (figura do gráfico, texto explicativo)
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Criar listas para o diagrama Sankey
    labels = list(contagem[var_x_plot].unique()) + list(contagem[var_y_plot].unique())
    
    # Mapear valores para índices
    source_indices = {val: i for i, val in enumerate(contagem[var_x_plot].unique())}
    target_offset = len(source_indices)
    target_indices = {val: i + target_offset for i, val in enumerate(contagem[var_y_plot].unique())}
    
    # Criar listas de source, target e value
    source = [source_indices[s] for s in contagem[var_x_plot]]
    target = [target_indices[t] for t in contagem[var_y_plot]]
    value = contagem['Contagem'].tolist()
    
    # Criar cores para nós
    node_colors = (
        px.colors.qualitative.Pastel[:len(source_indices)] + 
        px.colors.qualitative.Bold[:len(target_indices)]
    )
    
    # Criar diagrama Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors,
            hovertemplate='%{label}: %{value}<extra></extra>'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            hovertemplate='%{source.label} → %{target.label}: %{value}<extra></extra>'
        )
    )])
    
    # Ajustar layout
    fig.update_layout(
        title=f"Fluxo entre {variaveis_sociais[var_x]['nome']} e {variaveis_sociais[var_y]['nome']} ({estados_texto})",
        height=600,
        font=dict(size=12)
    )
    
    # Texto explicativo
    explicacao = f"""
        Este diagrama de Sankey mostra o fluxo de registros entre as categorias de {variaveis_sociais[var_x]['nome']} (origem) e 
        {variaveis_sociais[var_y]['nome']} (destino). A largura de cada ligação representa a quantidade de registros que 
        compartilham essas características.
    """
    
    return fig, explicacao


def exibir_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais):
    """
    Exibe gráficos de distribuição para um aspecto social selecionado.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados dos estados selecionados
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis sociais
    """
    st.header("Distribuição de Aspectos Sociais")
    
    # Permitir ao usuário selecionar qual aspecto social visualizar
    aspecto_social = st.selectbox(
        "Selecione o aspecto social para análise:",
        options=list(variaveis_sociais.keys()),
        format_func=lambda x: variaveis_sociais[x]["nome"],
        key="aspecto_dist"
    )
    
    # Verificar se a coluna existe nos dados
    if aspecto_social not in microdados_estados.columns:
        st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
        return
    
    # Preparar dados para visualização
    df_preparado, coluna_plot = preparar_dados_distribuicao(microdados_estados, aspecto_social, variaveis_sociais)
    
    # Contar candidatos por categoria
    contagem_aspecto = contar_candidatos_por_categoria(df_preparado, coluna_plot)
    
    # Ordenar os dados
    contagem_aspecto = ordenar_categorias(contagem_aspecto, aspecto_social, variaveis_sociais)
    
    # Calcular percentuais
    total = contagem_aspecto['Quantidade'].sum()
    contagem_aspecto['Percentual'] = (contagem_aspecto['Quantidade'] / total * 100).round(2)
    
    # Encontrar as categorias com maior e menor quantidade
    categoria_mais_frequente = contagem_aspecto.loc[contagem_aspecto['Quantidade'].idxmax()]
    categoria_menos_frequente = contagem_aspecto.loc[contagem_aspecto['Quantidade'].idxmin()]
    
    # Criar opções de visualização
    opcao_viz = st.radio(
        "Tipo de visualização:",
        ["Gráfico de Barras", "Gráfico de Linha", "Gráfico de Pizza"],
        horizontal=True,
        key="viz_tipo_dist"
    )
    
    # Criar visualização com base na escolha do usuário
    fig = criar_grafico_distribuicao(contagem_aspecto, opcao_viz, aspecto_social, variaveis_sociais)
    
    # Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Dados detalhados
    exibir_dados_detalhados(contagem_aspecto, total, categoria_mais_frequente, categoria_menos_frequente)
    
    # Adicionar explicação sobre o gráfico
    exibir_explicacao_distribuicao(aspecto_social, variaveis_sociais, total, 
                                 contagem_aspecto, categoria_mais_frequente)


def preparar_dados_distribuicao(microdados, aspecto_social, variaveis_sociais):
    """
    Prepara os dados para análise de distribuição de um aspecto social.
    
    Retorna:
    --------
    tuple
        (DataFrame preparado, nome da coluna para plotar)
    """
    df_dist = microdados.copy()
    
    if df_dist[aspecto_social].dtype != 'object':
        df_dist[f'{aspecto_social}_NOME'] = df_dist[aspecto_social].map(
            variaveis_sociais[aspecto_social]["mapeamento"]
        )
        coluna_plot = f'{aspecto_social}_NOME'
    else:
        coluna_plot = aspecto_social
        
    return df_dist, coluna_plot


def contar_candidatos_por_categoria(df, coluna_plot):
    """
    Conta o número de candidatos em cada categoria de um aspecto social.
    
    Retorna:
    --------
    DataFrame
        DataFrame com contagem de candidatos por categoria
    """
    contagem = df[coluna_plot].value_counts().reset_index()
    contagem.columns = ['Categoria', 'Quantidade']
    return contagem


def ordenar_categorias(contagem_aspecto, aspecto_social, variaveis_sociais):
    """
    Ordena as categorias de acordo com a configuração do aspecto social.
    
    Retorna:
    --------
    DataFrame
        DataFrame ordenado
    """
    if "ordem" in variaveis_sociais[aspecto_social]:
        # Usar ordem explicitamente definida
        ordem_categorias = variaveis_sociais[aspecto_social]["ordem"]
        contagem_aspecto['Categoria'] = pd.Categorical(
            contagem_aspecto['Categoria'], 
            categories=ordem_categorias, 
            ordered=True
        )
        return contagem_aspecto.sort_values('Categoria')
    
    elif "mapeamento" in variaveis_sociais[aspecto_social]:
        # Usar a ordem do mapeamento original
        mapeamento = variaveis_sociais[aspecto_social]["mapeamento"]
        
        # Obter valores do mapeamento na ordem original das chaves
        valores_ordenados = list(mapeamento.values())
        
        # Filtrar para incluir apenas categorias presentes nos dados
        categorias_presentes = set(contagem_aspecto['Categoria'])
        categorias_ordenadas = [categoria for categoria in valores_ordenados if categoria in categorias_presentes]
        
        # Aplicar ordenação categórica
        contagem_aspecto['Categoria'] = pd.Categorical(
            contagem_aspecto['Categoria'],
            categories=categorias_ordenadas,
            ordered=True
        )
        return contagem_aspecto.sort_values('Categoria')
    
    else:
        # Se não houver ordem nem mapeamento, ordenar por quantidade
        return contagem_aspecto.sort_values('Quantidade', ascending=False)


def criar_grafico_distribuicao(contagem_aspecto, opcao_viz, aspecto_social, variaveis_sociais):
    """
    Cria um gráfico de distribuição baseado no tipo selecionado pelo usuário.
    
    Retorna:
    --------
    figura
        Objeto plotly.graph_objects.Figure
    """
    if opcao_viz == "Gráfico de Barras":
        fig = px.bar(
            contagem_aspecto,
            x='Categoria',
            y='Quantidade',
            text='Quantidade',
            title=f'Distribuição de {variaveis_sociais[aspecto_social]["nome"]}',
            labels={
                'Categoria': variaveis_sociais[aspecto_social]["nome"],
                'Quantidade': 'Número de Candidatos'
            },
            color='Quantidade',
            category_orders={"Categoria": list(contagem_aspecto['Categoria'])}
        )
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        
    elif opcao_viz == "Gráfico de Linha":
        fig = px.line(
            contagem_aspecto,
            x='Categoria',
            y='Quantidade',
            markers=True,
            title=f'Distribuição de {variaveis_sociais[aspecto_social]["nome"]}',
            labels={
                'Categoria': variaveis_sociais[aspecto_social]["nome"],
                'Quantidade': 'Número de Candidatos'
            },
            color_discrete_sequence=['#3366CC'],
            category_orders={"Categoria": list(contagem_aspecto['Categoria'])}
        )
        
    else:  # Gráfico de Pizza
        fig = px.pie(
            contagem_aspecto,
            names='Categoria',
            values='Quantidade',
            title=f'Distribuição de {variaveis_sociais[aspecto_social]["nome"]}',
            hover_data=['Percentual'],
            labels={'Quantidade': 'Número de Candidatos'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_traces(textinfo='percent+label', sort=False)
    
    # Ajustar layout comum
    configurar_layout_grafico(fig, opcao_viz, contagem_aspecto, aspecto_social, variaveis_sociais)
    
    return fig


def configurar_layout_grafico(fig, opcao_viz, contagem_aspecto, aspecto_social, variaveis_sociais):
    """
    Configura o layout do gráfico de distribuição.
    
    Parâmetros:
    -----------
    fig : figura
        Objeto figura do plotly
    opcao_viz : str
        Tipo de visualização selecionada
    contagem_aspecto : DataFrame
        DataFrame com os dados de contagem
    aspecto_social : str
        Nome do aspecto social selecionado
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis sociais
    """
    if opcao_viz != "Gráfico de Pizza":
        fig.update_layout(
            height=500,
            xaxis=dict(tickangle=-45, categoryorder='array', categoryarray=list(contagem_aspecto['Categoria'])),
            plot_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            yaxis=dict(title="Número de Candidatos"),
        )
    else:  # Gráfico de Pizza
        fig.update_layout(
            height=500,
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(
                title=dict(text=f"{variaveis_sociais[aspecto_social]['nome']} <br><sup>Clique para filtrar</sup>"),
                traceorder="normal"
            )
        )


def exibir_dados_detalhados(contagem_aspecto, total, categoria_mais_frequente, categoria_menos_frequente):
    """
    Exibe dados detalhados sobre a distribuição em um expander.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com os dados de contagem
    total : int
        Total de candidatos
    categoria_mais_frequente : Series
        Série com dados da categoria mais frequente
    categoria_menos_frequente : Series
        Série com dados da categoria menos frequente
    """
    with st.expander("Ver dados detalhados"):
        # Estatísticas descritivas
        stats = {
            "Total de candidatos": f"{total:,}",
            "Categoria mais frequente": (f"{categoria_mais_frequente['Categoria']} "
                                        f"({categoria_mais_frequente['Quantidade']:,} candidatos - "
                                        f"{categoria_mais_frequente['Percentual']:.1f}%)"),
            "Categoria menos frequente": (f"{categoria_menos_frequente['Categoria']} "
                                         f"({categoria_menos_frequente['Quantidade']:,} candidatos - "
                                         f"{categoria_menos_frequente['Percentual']:.1f}%)"),
        }
        
        st.write("### Estatísticas")
        for key, val in stats.items():
            st.write(f"**{key}:** {val}")
            
        # Opção para exibir a tabela completa
        if st.checkbox("Mostrar tabela completa", key="show_full_table"):
            st.write(contagem_aspecto)


def exibir_explicacao_distribuicao(aspecto_social, variaveis_sociais, 
                                 total, contagem_aspecto, categoria_mais_frequente):
    """
    Exibe explicação sobre o gráfico de distribuição.
    
    Parâmetros:
    -----------
    aspecto_social : str
        Nome do aspecto social selecionado
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis sociais
    total : int
        Total de candidatos
    contagem_aspecto : DataFrame
        DataFrame com os dados de contagem
    categoria_mais_frequente : Series
        Série com dados da categoria mais frequente
    """
    explicacao_dist = f"""
        Este gráfico mostra a distribuição de candidatos por {variaveis_sociais[aspecto_social]["nome"].lower()}.
        No total, há {total:,} candidatos distribuídos entre {len(contagem_aspecto)} categorias diferentes.
        
        A categoria mais comum é "{categoria_mais_frequente['Categoria']}", que representa {categoria_mais_frequente['Percentual']:.1f}% do total.
    """
    st.info(explicacao_dist)