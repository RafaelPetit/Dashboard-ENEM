import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def criar_histograma(df, coluna, nome_area, estatisticas):
    """
    Cria um histograma formatado com informações estatísticas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados para análise
    coluna : str
        Nome da coluna com as notas
    nome_area : str
        Nome formatado da área de conhecimento
    estatisticas : dict
        Dicionário com estatísticas calculadas
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o histograma formatado
    """
    # Extrair estatísticas principais
    media = estatisticas['media']
    mediana = estatisticas['mediana']
    min_valor = estatisticas['min_valor']
    max_valor = estatisticas['max_valor']
    desvio_padrao = estatisticas['desvio_padrao']
    curtose = estatisticas['curtose']
    assimetria = estatisticas['assimetria']

    # Criar histograma
    fig = px.histogram(
        df,
        x=coluna,
        nbins=30,
        histnorm='percent',
        title=f"Histograma das notas - {nome_area}",
        labels={coluna: f"Nota ({nome_area})"},
        opacity=0.7,
        color_discrete_sequence=['#3366CC']
    )
    
    # Adicionar linhas de média e mediana
    fig.add_vline(x=media, line_dash="dash", line_color="red")
    fig.add_vline(x=mediana, line_dash="dash", line_color="green")
    
    # Formatação do layout
    fig.update_layout(
        height=400,
        bargap=0.1,
        xaxis_title=f"Nota ({nome_area})",
        yaxis_title="Porcentagem (%)",
        xaxis=dict(tickmode='auto', nticks=15, showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        showlegend=False
    )
    
    # Adicionar caixa de estatísticas
    stats_text = f"""
    <b>Estatísticas:</b><br>
    Média: {media:.2f}<br>
    Mediana: {mediana:.2f}<br>
    Mínimo: {min_valor:.2f}<br>
    Máximo: {max_valor:.2f}<br>
    Desvio Padrão: {desvio_padrao:.2f}<br>
    Curtose: {curtose:.2f}<br>
    Assimetria: {assimetria:.2f}
    """

    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=stats_text,
        showarrow=False,
        font=dict(size=12),
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4
    )
    
    # Legenda para as linhas
    fig.add_annotation(
        x=0.98, y=0.98,
        xref="paper", yref="paper",
        text="<b>Legenda:</b><br>— Média (vermelho)<br>— Mediana (verde)",
        showarrow=False,
        font=dict(size=12),
        align="right",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4
    )
    
    return fig

def criar_grafico_faltas(df_faltas, order_by_area=None, order_ascending=False, filtro_area=None):
    """
    Cria gráfico de linha para análise de faltas.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame com dados de faltas preparados
    order_by_area : str, optional
        Área para ordenar os estados
    order_ascending : bool, default=False
        Se a ordenação deve ser ascendente
    filtro_area : str, optional
        Filtrar para mostrar apenas uma área específica
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de linha
    """
    # Criar uma cópia para não modificar o DataFrame original
    df_plot = df_faltas.copy()
    
    # Aplicar ordenação se solicitado
    if order_by_area is not None:
        # Filtrar para a área selecionada
        ordem_estados = df_plot[df_plot['Área'] == order_by_area].sort_values(
            'Percentual de Faltas', ascending=order_ascending)['Estado'].tolist()
        
        # Criar categoria ordenada
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
    
    # Aplicar filtro de área se solicitado
    if filtro_area is not None:
        df_plot = df_plot[df_plot['Área'] == filtro_area]
    
    # Criar gráfico de linha
    fig = px.line(
        df_plot,
        x='Estado',
        y='Percentual de Faltas',
        color='Área',
        markers=True,
        labels={
            'Percentual de Faltas': '% de Candidatos Ausentes', 
            'Estado': 'Estado', 
            'Área': 'Área de Conhecimento'
        },
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Estado",
        yaxis_title="% de Candidatos Ausentes",
        legend_title="Área de Conhecimento",
        xaxis=dict(tickangle=-45),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=dict(
            title=dict(text="Área de Conhecimento<br><sup>Clique para comparar áreas específicas</sup>"),
        ),
        yaxis=dict(
            ticksuffix="%",  # Adicionar símbolo % aos valores do eixo Y
            range=[0, df_faltas['Percentual de Faltas'].max() * 1.1]  # Margem superior para visualização
        )
    )
    
    return fig