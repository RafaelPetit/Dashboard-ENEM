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


def criar_grafico_scatter(dados_filtrados, eixo_x, eixo_y, competencia_mapping):
    """
    Cria o gráfico de dispersão para análise da relação entre competências.
    Versão otimizada sem linhas de tendência para melhorar performance.
    """
    # Limitar número de pontos para desempenho
    amostra_dados = dados_filtrados
    max_points = 10000
    
    if len(dados_filtrados) > max_points:
        amostra_dados = dados_filtrados.sample(n=max_points, random_state=42)
    
    # Criar figura usando plotly express diretamente (mais simples e eficiente)
    fig = px.scatter(
        amostra_dados,
        x=eixo_x,
        y=eixo_y,
        color='RACA_COR',
        opacity=0.5,
        title=f"Relação entre {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}",
        labels={
            eixo_x: competencia_mapping[eixo_x],
            eixo_y: competencia_mapping[eixo_y],
            'RACA_COR': 'COR/RAÇA'
        },
        color_discrete_sequence=cores_padrao()
    )
    
    # Configurar layout do gráfico
    fig = aplicar_layout_padrao(fig, f"Relação entre {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}")
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(legend_title=dict(text="COR/RAÇA<br><sup>Clique para filtrar</sup>"))
    
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