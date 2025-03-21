import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def criar_grafico_heatmap(df_correlacao, var_x, var_y, var_x_plot, var_y_plot, 
                       variaveis_sociais, estados_texto):
    """
    Cria um heatmap para visualizar a correlação entre duas variáveis.
    
    Retorna:
    --------
    tuple
        (figura do gráfico, texto explicativo)
    """
    # Usar a função de preparação de dados
    from utils.prepara_dados import preparar_dados_heatmap
    normalized_pivot = preparar_dados_heatmap(df_correlacao, var_x_plot, var_y_plot)
    
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
    
    # Importar texto explicativo
    from utils.explicacao import get_explicacao_heatmap
    explicacao = get_explicacao_heatmap(variaveis_sociais[var_x]['nome'], variaveis_sociais[var_y]['nome'])
    
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
    # Usar a função de preparação de dados
    from utils.prepara_dados import preparar_dados_barras_empilhadas
    df_barras = preparar_dados_barras_empilhadas(df_correlacao, var_x_plot, var_y_plot)
    
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
    
    # Importar texto explicativo
    from utils.explicacao import get_explicacao_barras_empilhadas
    explicacao = get_explicacao_barras_empilhadas(variaveis_sociais[var_x]['nome'], variaveis_sociais[var_y]['nome'])
    
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
    # Usar a função de preparação de dados
    from utils.prepara_dados import preparar_dados_sankey
    labels, source, target, value = preparar_dados_sankey(df_correlacao, var_x_plot, var_y_plot)
    
    # Criar cores para nós
    node_colors = (
        px.colors.qualitative.Pastel[:len(set(source))] + 
        px.colors.qualitative.Bold[:len(set(target))]
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
    
    # Importar texto explicativo
    from utils.explicacao import get_explicacao_sankey
    explicacao = get_explicacao_sankey(variaveis_sociais[var_x]['nome'], variaveis_sociais[var_y]['nome'])
    
    return fig, explicacao


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


def criar_grafico_aspectos_por_estado(df_plot, aspecto_social, variaveis_sociais):
    """
    Cria um gráfico de linha mostrando a distribuição de aspectos sociais por estado.
    
    Parâmetros:
    -----------
    df_plot : DataFrame
        DataFrame com os dados preparados
    aspecto_social : str
        Nome do aspecto social a ser analisado
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis sociais
        
    Retorna:
    --------
    figura
        Objeto plotly.graph_objects.Figure
    """
    # Criar o gráfico
    fig = px.line(
        df_plot,
        x='Estado',
        y='Percentual',
        color='Categoria',
        markers=True,
        title=f'Distribuição de {variaveis_sociais[aspecto_social]["nome"]} por Estado',
        labels={
            'Estado': 'Estado',
            'Percentual': 'Percentual (%)',
            'Categoria': variaveis_sociais[aspecto_social]["nome"]
        },
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Configurar layout do gráfico
    fig.update_layout(
        height=500,
        xaxis_title="Estado",
        yaxis_title="Percentual (%)",
        yaxis=dict(ticksuffix="%"),
        legend_title=variaveis_sociais[aspecto_social]["nome"],
        xaxis=dict(tickangle=-45),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=dict(
            title=dict(text=f"{variaveis_sociais[aspecto_social]['nome']}<br><sup>Clique para filtrar</sup>"),
        )
    )
    
    return fig