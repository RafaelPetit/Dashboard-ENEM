import plotly.graph_objects as go
import plotly.express as px

def aplicar_layout_padrao(fig, titulo, altura=500, legenda_horizontal=True):
    """
    Aplica um layout padrão a um gráfico Plotly.
    
    Parâmetros:
    -----------
    fig: objeto Figure do Plotly
        Gráfico a ser configurado
    titulo: str
        Título do gráfico
    altura: int
        Altura do gráfico em pixels
    legenda_horizontal: bool
        Se True, posiciona a legenda horizontalmente no topo do gráfico
        
    Retorna:
    --------
    objeto Figure do Plotly configurado
    """
    # Definir parâmetros de layout baseados na orientação da legenda
    if legenda_horizontal:
        legend_dict = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    else:
        legend_dict = dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="right",
            x=1.05
        )
    
    # Aplicar layout padrão
    fig.update_layout(
        title=titulo,
        height=altura,
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=legend_dict
    )
    
    # Configurar grid e linhas de referência
    fig.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(220,220,220,0.5)'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(220,220,220,0.5)'
    )
    
    return fig

def cores_padrao():
    """
    Retorna a paleta de cores padrão para os gráficos do dashboard
    """
    return px.colors.qualitative.Bold