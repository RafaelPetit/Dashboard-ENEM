import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
from plotly.graph_objs import Figure

# Paletas de cores padrão
CORES_PRIMARIAS = px.colors.qualitative.Bold
CORES_SECUNDARIAS = px.colors.qualitative.Pastel

def aplicar_layout_padrao(
    fig: Figure, 
    titulo: str, 
    altura: int = 500, 
    legenda_horizontal: bool = True
) -> Figure:
    """
    Aplica um layout padrão a um gráfico Plotly.
    
    Parâmetros:
    -----------
    fig: Figure
        Gráfico a ser configurado
    titulo: str
        Título do gráfico
    altura: int, default=500
        Altura do gráfico em pixels
    legenda_horizontal: bool, default=True
        Se True, posiciona a legenda horizontalmente no topo do gráfico
        
    Retorna:
    --------
    Figure: Objeto Figure do Plotly configurado
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


def cores_padrao() -> List[str]:
    """
    Retorna a paleta de cores padrão para os gráficos do dashboard.
    
    Retorna:
    --------
    List[str]: Lista de códigos de cores hexadecimais
    """
    return CORES_PRIMARIAS


def aplicar_tema_grafico(
    fig: Figure, 
    titulo: Optional[str] = None, 
    eixo_x_angulo: int = -45
) -> Figure:
    """
    Aplica tema completo ao gráfico, incluindo estilização específica para eixos.
    
    Parâmetros:
    -----------
    fig: Figure
        Gráfico a ser configurado
    titulo: str, opcional
        Título do gráfico (se diferente do atual)
    eixo_x_angulo: int, default=-45
        Ângulo de rotação para os rótulos do eixo X
        
    Retorna:
    --------
    Figure: Objeto Figure do Plotly configurado
    """
    # Usar título existente se nenhum for fornecido
    titulo_final = titulo if titulo is not None else fig.layout.title.text
    
    # Aplicar layout padrão
    fig = aplicar_layout_padrao(fig, titulo_final)
    
    # Configurações adicionais específicas
    fig.update_layout(
        xaxis_tickangle=eixo_x_angulo,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig