import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from utils.visualizacao.config_graficos import aplicar_layout_padrao, cores_padrao

def criar_grafico_comparativo_barras(df_resultados, variavel_selecionada, variaveis_categoricas, 
                                    competencia_mapping, barmode='group'):
    """
    Cria o gráfico de barras comparativo para desempenho por categoria.
    """
    # Determinar título adequado
    ordenacao_texto = ""
    filtro_texto = ""
    
    # Verificar se estamos usando ordenação
    competencias_unicas = df_resultados['Competência'].unique()
    if isinstance(df_resultados['Categoria'].dtype, pd.CategoricalDtype) and df_resultados['Categoria'].dtype.ordered:
        ordenacao_texto = " (ordenado por valor decrescente)"
    
    # Verificar se estamos filtrando por competência
    if len(competencias_unicas) == 1:
        filtro_texto = f" - {competencias_unicas[0]}"
    
    # Criar gráfico
    titulo = f"Desempenho por {variaveis_categoricas[variavel_selecionada]['nome']}{filtro_texto}{ordenacao_texto}"
    
    fig = px.bar(
        df_resultados,
        x='Categoria',
        y='Média',
        color='Competência',
        title=titulo,
        labels={
            'Categoria': variaveis_categoricas[variavel_selecionada]['nome'],
            'Média': 'Nota Média',
            'Competência': 'Área de Conhecimento'
        },
        barmode=barmode,
        color_discrete_sequence=cores_padrao()
    )
    
    # Aplicar layout padrão
    fig = aplicar_layout_padrao(fig, titulo)
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_layout(legend_title=dict(text="Área de Conhecimento <br><sup>Clique para filtrar</sup>"))
    
    return fig


def criar_grafico_linha_desempenho(df_linha, variavel_selecionada, variaveis_categoricas, 
                                competencia_filtro, ordenar_decrescente):
    """
    Cria o gráfico de linha para visualização do desempenho por categoria.
    """
    # Determinar título adequado
    ordenacao_texto = " (ordenado por valor decrescente)" if ordenar_decrescente else ""
    filtro_texto = f" - {competencia_filtro}" if len(df_linha['Competência'].unique()) == 1 else ""
    titulo = f"Desempenho por {variaveis_categoricas[variavel_selecionada]['nome']}{filtro_texto}{ordenacao_texto}"
    
    fig = px.line(
        df_linha,
        x='Categoria',
        y='Média',
        color='Competência',
        markers=True,
        title=titulo,
        labels={
            'Categoria': variaveis_categoricas[variavel_selecionada]['nome'],
            'Média': 'Nota Média',
            'Competência': 'Área de Conhecimento'
        },
        color_discrete_sequence=cores_padrao()
    )
    
    # Aplicar layout padrão
    fig = aplicar_layout_padrao(fig, titulo)
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_layout(legend_title=dict(text="Área de Conhecimento <br><sup>Clique para filtrar</sup>"))
    
    return fig


def criar_grafico_linha_estados(df_plot, area_selecionada=None, ordenado=False):
    """
    Cria o gráfico de linha para visualização do desempenho por estado.
    """
    # Determinar título adequado
    titulo_base = 'Médias de Desempenho por Estado e Área de Conhecimento'
    sufixo = ""
    if ordenado and area_selecionada:
        sufixo = f" (ordenado por {area_selecionada})"
    
    fig = px.line(
        df_plot,
        x='Estado',
        y='Média',
        color='Área',
        markers=True,
        title=f"{titulo_base}{sufixo}",
        labels={'Média': 'Nota Média', 'Estado': 'Estado', 'Área': 'Área de Conhecimento'},
        color_discrete_sequence=cores_padrao()
    )
    
    # Aplicar layout padrão
    fig = aplicar_layout_padrao(fig, f"{titulo_base}{sufixo}")
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_layout(legend_title=dict(text="Área de Conhecimento<br><sup>Clique para filtrar</sup>"))
    
    return fig


def criar_grafico_scatter(df, eixo_x, eixo_y, competencia_mapping, colorir_por_faixa=False):
    """
    Cria um gráfico de dispersão para mostrar a relação entre duas competências.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados filtrados
    eixo_x : str
        Nome da coluna para o eixo X
    eixo_y : str
        Nome da coluna para o eixo Y
    competencia_mapping : dict
        Mapeamento das colunas para nomes legíveis
    colorir_por_faixa : bool, default=False
        Se True, colore os pontos por faixa salarial
        
    Retorna:
    --------
    Figure: Objeto figura do Plotly
    """
    # Adicionar labels para faixa salarial se necessário
    if colorir_por_faixa and 'TP_FAIXA_SALARIAL' in df.columns:
        # Criar mapeamento para nomes descritivos das faixas
        faixa_labels = {
            0: "Nenhuma Renda",
            1: "Até 1 Salário Mínimo",
            2: "1 a 2 Salários Mínimos",
            3: "2 a 3 Salários Mínimos",
            4: "3 a 5 Salários Mínimos",
            5: "5 a 10 Salários Mínimos",
            6: "10 a 20 Salários Mínimos",
            7: "Mais de 20 Salários Mínimos"
        }
        
        # Converter para string para melhor exibição
        df['Faixa Salarial'] = df['TP_FAIXA_SALARIAL'].map(faixa_labels)
        
        fig = px.scatter(
            df, 
            x=eixo_x, 
            y=eixo_y, 
            color='Faixa Salarial',
            labels={
                eixo_x: competencia_mapping[eixo_x], 
                eixo_y: competencia_mapping[eixo_y],
                'Faixa Salarial': 'Faixa Salarial'
            },
            opacity=0.7,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
    else:
        # Gráfico padrão sem coloração por faixa salarial
        fig = px.scatter(
            df, 
            x=eixo_x, 
            y=eixo_y, 
            labels={
                eixo_x: competencia_mapping[eixo_x], 
                eixo_y: competencia_mapping[eixo_y]
            },
            opacity=0.7,
            color_discrete_sequence=['#3366CC']
        )
    
    # Adicionar linha de tendência
    fig.update_traces(marker=dict(size=6))
    
    x = df[eixo_x].values
    y = df[eixo_y].values
    
    if len(x) > 1 and len(y) > 1:  # Verificar se há dados suficientes
        # Calcular linha de tendência
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        # Adicionar linha com um estilo translúcido
        fig.add_trace(
            go.Scatter(
                x=[min(x), max(x)], 
                y=[p(min(x)), p(max(x))], 
                mode='lines', 
                name='Tendência',
                line=dict(color='red', dash='dash', width=2),
                opacity=0.7
            )
        )
    
    # Estilização do gráfico
    fig.update_layout(
        height=500,
        xaxis_title=competencia_mapping[eixo_x],
        yaxis_title=competencia_mapping[eixo_y],
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
    )
    
    return fig


def adicionar_linha_tendencia(fig, df, eixo_x, eixo_y, nome):
    """
    Adiciona uma linha de tendência a um gráfico de dispersão.
    """
    # Remover valores NaN para o cálculo da regressão
    dados_validos = df.dropna(subset=[eixo_x, eixo_y])
    
    # Verificar se temos pontos suficientes para uma regressão significativa
    if len(dados_validos) < 10:
        return
    
    # Calcular a regressão linear
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        dados_validos[eixo_x], dados_validos[eixo_y]
    )
    
    # Criar os pontos da linha
    x_range = np.linspace(
        dados_validos[eixo_x].min(), 
        dados_validos[eixo_x].max(), 
        100
    )
    y_pred = slope * x_range + intercept
    
    # Definir a formatação da linha de tendência
    if nome == 'Brasil':
        cor_linha = '#FF4B4B'  # Vermelho para Brasil
        largura_linha = 3
        tracado = 'solid'
    else:
        cor_linha = '#1f77b4'  # Azul para estados individuais
        largura_linha = 1.5
        tracado = 'dash'
    
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_pred,
            mode='lines',
            name=f'Tendência {nome} (r={r_value:.2f})',
            line=dict(color=cor_linha, width=largura_linha, dash=tracado),
            hoverinfo='text',
            hovertext=f'Correlação: {r_value:.4f} | y = {slope:.2f}x + {intercept:.2f}'
        )
    )