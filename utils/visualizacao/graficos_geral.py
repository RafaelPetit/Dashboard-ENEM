import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
from utils.visualizacao.config_graficos import aplicar_layout_padrao, cores_padrao, aplicar_tema_grafico
from utils.helpers.cache_utils import memory_intensive_function, release_memory
from utils.mappings import get_mappings

# Obter mapeamentos e constantes
mappings = get_mappings()
CONFIG_VIZ = mappings.get('config_visualizacao', {})
LIMIARES_ESTATISTICOS = mappings.get('limiares_estatisticos', {})

@memory_intensive_function
def criar_histograma(
    df: pd.DataFrame, 
    coluna: str, 
    nome_area: str, 
    estatisticas: Dict[str, Any]
) -> go.Figure:
    """
    Cria um histograma formatado com informações estatísticas para distribuição de notas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados para análise
    coluna : str
        Nome da coluna com as notas
    nome_area : str
        Nome formatado da área de conhecimento
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o histograma formatado
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or coluna not in df.columns:
        return _criar_grafico_vazio(f"Dados insuficientes para criar histograma de {nome_area}")
    
    try:
        # Extrair estatísticas principais com valores padrão em caso de ausência
        media = estatisticas.get('media', 0)
        mediana = estatisticas.get('mediana', 0)
        min_valor = estatisticas.get('min_valor', 0)
        max_valor = estatisticas.get('max_valor', 0)
        desvio_padrao = estatisticas.get('desvio_padrao', 0)
        curtose = estatisticas.get('curtose', 0)
        assimetria = estatisticas.get('assimetria', 0)
        total_valido = estatisticas.get('total_valido', 0)
        
        # Verificar se temos estatísticas válidas
        if media == 0 and mediana == 0 and min_valor == 0 and max_valor == 0:
            return _criar_grafico_vazio(f"Estatísticas insuficientes para criar histograma de {nome_area}")

        # Criar histograma
        fig = px.histogram(
            df,
            x=coluna,
            nbins=30,
            histnorm='percent',
            title=f"Distribuição de Notas - {nome_area}",
            labels={coluna: f"Nota ({nome_area})"},
            opacity=0.7,
            color_discrete_sequence=['#3366CC']
        )
        
        # Adicionar linhas de média e mediana
        fig.add_vline(x=media, line_dash="dash", line_color="red")
        fig.add_vline(x=mediana, line_dash="dash", line_color="green")
        
        # Aplicar layout padrão
        fig = _aplicar_layout_histograma(fig, nome_area)
        
        # Adicionar caixa de estatísticas
        fig = _adicionar_caixa_estatisticas(fig, estatisticas)
        
        # Adicionar legenda para as linhas
        fig = _adicionar_legenda_linhas(fig)
        
        # Adicionar classificação das notas
        if 'faixas' in estatisticas and estatisticas['faixas']:
            fig = _adicionar_classificacao_notas(fig, estatisticas['faixas'])
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar histograma: {e}")
        return _criar_grafico_vazio(f"Erro ao criar histograma: {str(e)}")
    finally:
        # Liberar memória
        release_memory(df)


@memory_intensive_function
def criar_grafico_faltas(
    df_faltas: pd.DataFrame, 
    order_by_area: Optional[str] = None, 
    order_ascending: bool = False, 
    filtro_area: Optional[str] = None
) -> go.Figure:
    """
    Cria gráfico de linha para análise de faltas por estado e dia de prova.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame com dados de faltas preparados
    order_by_area : str, opcional
        Tipo de falta para ordenar os estados
    order_ascending : bool, default=False
        Se a ordenação deve ser ascendente
    filtro_area : str, opcional
        Filtrar para mostrar apenas um tipo específico de falta
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de linha
    """
    # Verificar se temos dados válidos
    if df_faltas is None or df_faltas.empty:
        print("Erro: DataFrame de faltas vazio")
        return _criar_grafico_vazio("Sem dados disponíveis para análise de faltas")
    
    # Verificar estrutura mínima necessária
    colunas_necessarias = ['Estado', 'Tipo de Falta', 'Percentual de Faltas']
    colunas_faltantes = [col for col in colunas_necessarias if col not in df_faltas.columns]
    if colunas_faltantes:
        print(f"Erro: Colunas faltantes no DataFrame de faltas: {colunas_faltantes}")
        print(f"Colunas disponíveis: {list(df_faltas.columns)}")
        return _criar_grafico_vazio(f"Estrutura de dados incorreta. Colunas faltantes: {colunas_faltantes}")
    
    # Verificar se temos dados suficientes
    if len(df_faltas) == 0:
        print("Erro: DataFrame de faltas não contém nenhuma linha")
        return _criar_grafico_vazio("Nenhum dado de faltas encontrado")
    
    print(f"Criando gráfico de faltas com {len(df_faltas)} linhas de dados")
    
    try:
        # Criar uma cópia para não modificar o DataFrame original
        df_plot = df_faltas.copy()
        
        # Remover linhas que contenham "Total de faltas" no Tipo de Falta
        if 'Tipo de Falta' in df_plot.columns:
            df_plot = df_plot[~df_plot['Tipo de Falta'].str.contains('Total de faltas', case=False, na=False)]
        
        # Aplicar ordenação se solicitado
        if order_by_area is not None:
            df_plot = _ordenar_estados_por_falta(df_plot, order_by_area, order_ascending)
        
        # Aplicar filtro se solicitado
        if filtro_area is not None:
            df_plot = df_plot[df_plot['Tipo de Falta'] == filtro_area]
            
        # Verificar novamente se ainda temos dados após filtragem
        if df_plot.empty:
            return _criar_grafico_vazio("Sem dados disponíveis após aplicação de filtros")
        
        # Criar gráfico de linha
        fig = _criar_grafico_linha_faltas(df_plot)
        
        # Aplicar layout específico para faltas
        fig = _aplicar_layout_faltas(fig, filtro_area)
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de faltas: {e}")
        return _criar_grafico_vazio(f"Erro ao criar análise de faltas: {str(e)}")
    finally:
        # Liberar memória
        release_memory(df_faltas)


def criar_grafico_media_por_estado(
    df_medias: pd.DataFrame, 
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str],
    por_regiao: bool = False,
    destacar_maior: bool = True,
    destacar_menor: bool = True
) -> go.Figure:
    """
    Cria gráfico de barras com médias por estado ou região.
    
    Parâmetros:
    -----------
    df_medias : DataFrame
        DataFrame com as médias por estado/região
    colunas_notas : List[str]
        Lista de colunas de notas disponíveis
    competencia_mapping : Dict[str, str]
        Mapeamento entre códigos de competência e nomes legíveis
    por_regiao : bool, default=False
        Indica se os dados estão agrupados por região
    destacar_maior : bool, default=True
        Se deve destacar o estado/região com maior média
    destacar_menor : bool, default=True
        Se deve destacar o estado/região com menor média
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de barras
    """
    # Verificar se temos dados válidos
    if df_medias is None or df_medias.empty:
        return _criar_grafico_vazio("Sem dados disponíveis para médias por estado/região")
    
    # Verificar estrutura mínima necessária
    if 'Local' not in df_medias.columns or 'Média Geral' not in df_medias.columns:
        return _criar_grafico_vazio("Estrutura de dados incorreta para médias por estado/região")
    
    try:
        # Preparar o título
        tipo_localidade = "Região" if por_regiao else "Estado"
        titulo = f"Média Geral por {tipo_localidade}"
        
        # Ordenar por média decrescente
        df_plot = df_medias.sort_values('Média Geral', ascending=False)
        
        # Criar cores para destaque
        cores = ['#3366CC'] * len(df_plot)
        
        # Destacar maior e menor valor se solicitado
        if destacar_maior and len(df_plot) > 0:
            cores[0] = '#2CA02C'  # Verde para o maior
            
        if destacar_menor and len(df_plot) > 1:
            cores[-1] = '#FF7F0E'  # Laranja para o menor
        
        # Criar gráfico de barras
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=df_plot['Local'],
                y=df_plot['Média Geral'],
                marker_color=cores,
                text=df_plot['Média Geral'].round(1),
                textposition='auto'
            )
        )
        
        # Aplicar layout padrão
        fig.update_layout(
            title=titulo,
            xaxis_title=tipo_localidade,
            yaxis_title="Média Geral",
            xaxis=dict(tickangle=-45),
            height=500,
            # yaxis=dict(
            #     range=[
            #         max(0, df_plot['Média Geral'].min() - 50),  # Garantir que comece em 0 ou um pouco abaixo do mínimo
            #         min(1000, df_plot['Média Geral'].max() + 50)  # Limitar a 1000 (nota máxima)
            #     ]
            # )
        )
        
        # Adicionar legenda para cores destacadas
        if destacar_maior or destacar_menor:
            anotacoes = []
            
            if destacar_maior:
                anotacoes.append(f"■ <b>{df_plot.iloc[0]['Local']}</b>: Maior média ({df_plot.iloc[0]['Média Geral']:.1f})")
                
            if destacar_menor:
                anotacoes.append(f"■ <b>{df_plot.iloc[-1]['Local']}</b>: Menor média ({df_plot.iloc[-1]['Média Geral']:.1f})")
            
            fig.add_annotation(
                x=0.98, y=0.98,
                xref="paper", yref="paper",
                text="<br>".join(anotacoes),
                showarrow=False,
                font=dict(size=12),
                align="right",
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
                borderpad=4
            )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de médias por estado: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


def criar_grafico_comparativo_areas(
    df_areas: pd.DataFrame, 
    tipo_grafico: str = "barras", 
    mostrar_dispersao: bool = True
) -> go.Figure:
    """
    Cria gráfico comparativo entre áreas de conhecimento.
    
    Parâmetros:
    -----------
    df_areas : DataFrame
        DataFrame com dados comparativos entre áreas
    tipo_grafico : str, default="barras"
        Tipo de gráfico a ser criado ("barras", "radar", "linha")
    mostrar_dispersao : bool, default=True
        Se deve mostrar indicadores de dispersão (desvio padrão)
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico comparativo
    """
    # Verificar se temos dados válidos
    if df_areas is None or df_areas.empty:
        return _criar_grafico_vazio("Sem dados disponíveis para comparação entre áreas")
    
    # Verificar estrutura mínima necessária
    colunas_necessarias = ['Area', 'Media']
    if not all(col in df_areas.columns for col in colunas_necessarias):
        return _criar_grafico_vazio("Estrutura de dados incorreta para comparação entre áreas")
    
    try:
        # Preparar o título
        titulo = "Comparativo de Desempenho entre Áreas de Conhecimento"
        
        # Escolher o tipo de gráfico apropriado
        if tipo_grafico == "radar":
            fig = _criar_grafico_radar_areas(df_areas)
        elif tipo_grafico == "linha":
            fig = _criar_grafico_linha_areas(df_areas, mostrar_dispersao)
        else:  # "barras" como padrão
            # Passar explicitamente o parâmetro mostrar_dispersao
            fig = _criar_grafico_barras_areas(df_areas, mostrar_dispersao)
        
        # Aplicar layout padrão
        fig = aplicar_layout_padrao(fig, titulo)
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico comparativo entre áreas: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


def criar_grafico_evasao(
    df_evasao: pd.DataFrame,
    tipo_grafico: str = "barras",
    ordenar_por: Optional[str] = None,
    ordem_crescente: bool = False
) -> go.Figure:
    """
    Cria gráfico para análise de evasão (faltas) por estado.
    
    Parâmetros:
    -----------
    df_evasao : DataFrame
        DataFrame com dados de evasão por estado
    tipo_grafico : str, default="barras"
        Tipo de gráfico a ser criado ("barras", "mapa_calor", "pizza")
    ordenar_por : str, opcional
        Métrica para ordenar os estados
    ordem_crescente : bool, default=False
        Se a ordenação deve ser crescente
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de evasão
    """
    # Verificar se temos dados válidos
    if df_evasao is None or df_evasao.empty:
        return _criar_grafico_vazio("Sem dados disponíveis para análise de evasão")
    
    # Verificar estrutura mínima necessária
    colunas_necessarias = ['Estado', 'Métrica', 'Valor']
    if not all(col in df_evasao.columns for col in colunas_necessarias):
        return _criar_grafico_vazio("Estrutura de dados incorreta para análise de evasão")
    
    try:
        # Preparar o título
        titulo = "Análise de Evasão por Estado"
        
        # Ordenar dados se solicitado
        if ordenar_por is not None:
            df_evasao = _ordenar_dados_evasao(df_evasao, ordenar_por, ordem_crescente)
        
        # Escolher o tipo de gráfico apropriado
        if tipo_grafico == "mapa_calor":
            fig = _criar_mapa_calor_evasao(df_evasao)
        elif tipo_grafico == "pizza":
            fig = _criar_grafico_pizza_evasao(df_evasao)
        else:  # "barras" como padrão
            fig = _criar_grafico_barras_evasao(df_evasao)
        
        # Aplicar layout padrão
        fig = aplicar_layout_padrao(fig, titulo)
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de evasão: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


# Funções auxiliares

def _criar_grafico_vazio(mensagem: str = "Dados insuficientes para criar visualização") -> go.Figure:
    """
    Cria um gráfico vazio com uma mensagem explicativa.
    
    Parâmetros:
    -----------
    mensagem: str, default="Dados insuficientes para criar visualização"
        Mensagem a ser exibida no gráfico vazio
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com mensagem de erro
    """
    fig = go.Figure()
    
    fig.update_layout(
        title=mensagem,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text=mensagem,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16)
            )
        ],
        height=400
    )
    
    return fig


def _aplicar_layout_histograma(fig: go.Figure, nome_area: str) -> go.Figure:
    """
    Aplica layout padronizado para histograma.
    
    Parâmetros:
    -----------
    fig : Figure
        Figura Plotly a ser formatada
    nome_area : str
        Nome da área de conhecimento
        
    Retorna:
    --------
    Figure: Figura Plotly formatada
    """
    fig.update_layout(
        height=500,
        bargap=0.1,
        xaxis_title=f"Nota ({nome_area})",
        yaxis_title="Porcentagem (%)",
        xaxis=dict(tickmode='auto', nticks=15, showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        showlegend=False
    )
    
    return fig


def _adicionar_caixa_estatisticas(fig: go.Figure, estatisticas: Dict[str, Any]) -> go.Figure:
    """
    Adiciona caixa com estatísticas ao histograma.
    
    Parâmetros:
    -----------
    fig : Figure
        Figura Plotly a ser modificada
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
        
    Retorna:
    --------
    Figure: Figura Plotly com anotação adicionada
    """
    # Extrair apenas as estatísticas básicas necessárias
    media = estatisticas.get('media', 0)
    mediana = estatisticas.get('mediana', 0)
    min_valor = estatisticas.get('min_valor', 0)
    max_valor = estatisticas.get('max_valor', 0)
    total_candidatos = estatisticas.get('total_candidatos', 0)  # Total real incluindo ausentes
    
    # Montar texto simplificado
    stats_text = f"""
    <b>Estatísticas:</b><br>
    Total de Candidatos: {total_candidatos:,}<br>
    Média: {media:.2f}<br>
    Mediana: {mediana:.2f}<br>
    Mínimo: {min_valor:.2f}<br>
    Máximo: {max_valor:.2f}
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
    
    return fig


def _adicionar_legenda_linhas(fig: go.Figure) -> go.Figure:
    """
    Adiciona legenda para as linhas de média e mediana.
    
    Parâmetros:
    -----------
    fig : Figure
        Figura Plotly a ser modificada
        
    Retorna:
    --------
    Figure: Figura Plotly com legenda adicionada
    """
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


def _adicionar_classificacao_notas(fig: go.Figure, faixas: Dict[str, float]) -> go.Figure:
    """
    Adiciona classificação das notas ao histograma.
    
    Parâmetros:
    -----------
    fig : Figure
        Figura Plotly a ser modificada
    faixas : Dict[str, float]
        Dicionário com percentuais por faixa
        
    Retorna:
    --------
    Figure: Figura Plotly com classificação adicionada
    """
    # Criar texto com classificação
    faixas_ordenadas = [
        'Abaixo de 300', '300 a 500', '500 a 700', 
        '700 a 900', '900 ou mais'
    ]
    
    # Filtrar apenas faixas que existem no dicionário
    faixas_disponiveis = [f for f in faixas_ordenadas if f in faixas]
    
    if not faixas_disponiveis:
        return fig
    
    # Criar texto com as faixas disponíveis
    texto_faixas = "<b>Classificação:</b><br>"
    for faixa in faixas_disponiveis:
        percentual = faixas.get(faixa, 0)
        texto_faixas += f"{faixa}: {percentual:.1f}%<br>"
    
    # Adicionar a anotação no canto inferior direito
    fig.add_annotation(
        x=0.98, y=0.02,
        xref="paper", yref="paper",
        text=texto_faixas,
        showarrow=False,
        font=dict(size=12),
        align="right",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4
    )
    
    return fig


def _ordenar_estados_por_falta(
    df: pd.DataFrame, 
    tipo_falta: str, 
    ordem_ascendente: bool
) -> pd.DataFrame:
    """
    Ordena os estados com base no percentual de um tipo específico de falta.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados de faltas
    tipo_falta : str
        Tipo de falta a ser usado como critério de ordenação
    ordem_ascendente : bool
        Se a ordenação deve ser ascendente
        
    Retorna:
    --------
    DataFrame: DataFrame ordenado
    """
    try:
        # Filtrar para o tipo de falta selecionado
        df_filtrado = df[df['Tipo de Falta'] == tipo_falta]
        
        if df_filtrado.empty:
            return df  # Retornar o DataFrame original se não encontrar o tipo de falta
        
        # Obter a ordem dos estados
        ordem_estados = df_filtrado.sort_values(
            'Percentual de Faltas', 
            ascending=ordem_ascendente
        )['Estado'].unique().tolist()
        
        # Aplicar ordenação categórica
        df_ordenado = df.copy()
        df_ordenado['Estado'] = pd.Categorical(
            df_ordenado['Estado'], 
            categories=ordem_estados, 
            ordered=True
        )
        
        return df_ordenado.sort_values('Estado')
        
    except Exception as e:
        print(f"Erro ao ordenar estados por falta: {e}")
        return df  # Retornar o DataFrame original em caso de erro


def _criar_grafico_linha_faltas(df: pd.DataFrame) -> go.Figure:
    """
    Cria o gráfico de linha base para análise de faltas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados de faltas
        
    Retorna:
    --------
    Figure: Figura Plotly com gráfico de linha
    """
    # Criar figura com dados
    fig = px.line(
        df,
        x='Estado',
        y='Percentual de Faltas',
        color='Tipo de Falta',
        markers=True,
        labels={
            'Percentual de Faltas': '% de Candidatos Ausentes', 
            'Estado': 'Estado', 
            'Tipo de Falta': 'Padrão de Ausência'
        },
        color_discrete_sequence=cores_padrao()
    )
    
    # Aumentar espessura das linhas
    fig.update_traces(line=dict(width=2))
    
    return fig


def _aplicar_layout_faltas(fig: go.Figure, filtro_area: Optional[str] = None) -> go.Figure:
    """
    Aplica layout específico para o gráfico de faltas.
    
    Parâmetros:
    -----------
    fig : Figure
        Figura Plotly a ser formatada
    filtro_area : str, opcional
        Tipo de falta usado como filtro
        
    Retorna:
    --------
    Figure: Figura Plotly formatada
    """
    # Determinar título apropriado
    titulo_base = "Análise de Ausências por Estado"
    if filtro_area:
        titulo = f"{titulo_base} - {filtro_area}"
    else:
        titulo = titulo_base
    
    # Atualizar layout
    fig.update_layout(
        title=titulo,
        height=500,
        xaxis_title="Estado",
        yaxis_title="% de Candidatos Ausentes",
        legend_title="Padrão de Ausência",
        xaxis=dict(tickangle=-45),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=dict(
            title=dict(text="Padrão de Ausência<br><sup>Clique para comparar padrões específicos</sup>"),
        ),
        yaxis=dict(
            ticksuffix="%",  # Adicionar símbolo % aos valores do eixo Y
            # range=[0, fig.data[0].y.max() * 1.1 if len(fig.data) > 0 and len(fig.data[0].y) > 0 else 100]  # Margem superior para visualização
        )
    )
    
    return fig


def _criar_grafico_barras_areas(df: pd.DataFrame, mostrar_dispersao: bool = True) -> go.Figure:
    """
    Cria gráfico de barras para comparação entre áreas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados por área
    mostrar_dispersao : bool
        Se deve mostrar barras de erro com desvio padrão
        
    Retorna:
    --------
    Figure: Figura Plotly com gráfico de barras
    """
    # Verificar se temos dados de dispersão
    tem_desvio = 'DesvioPadrao' in df.columns and mostrar_dispersao
    
    # Inicializar figura
    fig = go.Figure()
    
    # Preparar dados para barra de erro
    error_y_config = None
    if tem_desvio:
        error_y_config = dict(
            type='data',
            array=df['DesvioPadrao'],
            visible=True,
            thickness=2,
            width=4,
            color='rgba(68, 68, 68, 0.8)'
        )
    
    # Adicionar uma única trace com todas as barras
    fig.add_trace(
        go.Bar(
            x=df['Area'],
            y=df['Media'],
            name='Média das Notas',
            text=[f"{val:.1f}" for val in df['Media']],
            textposition='auto',
            error_y=error_y_config,
            marker=dict(
                color='rgba(55, 128, 191, 0.8)',
                line=dict(
                    color='rgba(55, 128, 191, 1.0)',
                    width=1
                )
            )
        )
    )
    
    # Atualizar layout
    fig.update_layout(
        title="Comparativo de Desempenho entre Áreas de Conhecimento",
        xaxis_title="Área de Conhecimento",
        yaxis_title="Nota Média",
        showlegend=False,
        height=500,
        # yaxis=dict(
        #     range=[
        #         max(0, df['Media'].min() - 50),  # Garantir que comece em 0 ou um pouco abaixo do mínimo
        #         min(1000, df['Media'].max() + 50)  # Limitar a 1000 (nota máxima)
        #     ]
        # )
    )
    
    return fig

def _criar_grafico_radar_areas(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de radar para comparação entre áreas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados por área
        
    Retorna:
    --------
    Figure: Figura Plotly com gráfico de radar
    """
    # Inicializar figura
    fig = go.Figure()
    
    # Adicionar o radar
    fig.add_trace(
        go.Scatterpolar(
            r=df['Media'].tolist(),
            theta=df['Area'].tolist(),
            fill='toself',
            name='Média',
            line=dict(color='#3366CC')
        )
    )
    
    # Adicionar mediana se disponível
    if 'Mediana' in df.columns:
        fig.add_trace(
            go.Scatterpolar(
                r=df['Mediana'].tolist(),
                theta=df['Area'].tolist(),
                fill='none',
                name='Mediana',
                line=dict(color='#FF7F0E', dash='dash')
            )
        )
    
    # Configurar layout
    fig.update_layout(
        title="Comparativo de Desempenho entre Áreas (Radar)",
        polar=dict(
            radialaxis=dict(
                visible=True,
                # range=[0, max(1000, df['Media'].max() * 1.1)]
            )
        ),
        showlegend=True,
        height=600
    )
    
    return fig


def _criar_grafico_linha_areas(df: pd.DataFrame, mostrar_dispersao: bool = False) -> go.Figure:
    """
    Cria gráfico de linha para comparação entre áreas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados por área
    mostrar_dispersao : bool
        Se deve mostrar barras de erro com desvio padrão
        
    Retorna:
    --------
    Figure: Figura Plotly com gráfico de linha
    """
    # Inicializar figura
    fig = go.Figure()
    
    # Verificar se temos dados de dispersão
    tem_desvio = 'DesvioPadrao' in df.columns and mostrar_dispersao
    
    # Preparar dados para barra de erro
    error_y_config = None
    if tem_desvio:
        error_y_config = dict(
            type='data',
            array=df['DesvioPadrao'],
            visible=True,
            thickness=2,
            width=4,
            color='rgba(68, 68, 68, 0.8)'
        )
    
    # Adicionar linha conectando os pontos
    fig.add_trace(
        go.Scatter(
            x=df['Area'].tolist(),
            y=df['Media'].tolist(),
            mode='lines+markers+text',
            name='Média',
            text=df['Media'].round(1).tolist(),
            textposition='top center',
            line=dict(color='#3366CC', width=3),
            marker=dict(size=8, color='#3366CC'),
            error_y=error_y_config
        )
    )
    
    # Configurar layout
    fig.update_layout(
        title="Tendência de Desempenho entre Áreas de Conhecimento",
        xaxis_title="Área de Conhecimento",
        yaxis_title="Nota Média",
        height=500,
        xaxis=dict(tickangle=-45),
        yaxis=dict(
            range=[
                max(0, df['Media'].min() - 50),  # Garantir que comece em 0 ou um pouco abaixo do mínimo
                min(1000, df['Media'].max() + 50)  # Limitar a 1000 (nota máxima)
            ]
        )
    )
    
    return fig


def _ordenar_dados_evasao(
    df: pd.DataFrame, 
    metrica: str, 
    ordem_crescente: bool
) -> pd.DataFrame:
    """
    Ordena os dados de evasão com base em uma métrica específica.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados de evasão
    metrica : str
        Métrica a ser usada como critério de ordenação
    ordem_crescente : bool
        Se a ordenação deve ser crescente
        
    Retorna:
    --------
    DataFrame: DataFrame ordenado
    """
    try:
        # Filtrar para a métrica selecionada
        df_filtrado = df[df['Métrica'] == metrica]
        
        if df_filtrado.empty:
            return df  # Retornar o DataFrame original se não encontrar a métrica
        
        # Obter a ordem dos estados
        ordem_estados = df_filtrado.sort_values(
            'Valor', 
            ascending=ordem_crescente
        )['Estado'].unique().tolist()
        
        # Aplicar ordenação categórica
        df_ordenado = df.copy()
        df_ordenado['Estado'] = pd.Categorical(
            df_ordenado['Estado'], 
            categories=ordem_estados, 
            ordered=True
        )
        
        return df_ordenado.sort_values('Estado')
        
    except Exception as e:
        print(f"Erro ao ordenar dados de evasão: {e}")
        return df  # Retornar o DataFrame original em caso de erro


def _criar_mapa_calor_evasao(df: pd.DataFrame) -> go.Figure:
    """
    Cria mapa de calor para análise de evasão por estado.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados de evasão
        
    Retorna:
    --------
    Figure: Figura Plotly com mapa de calor
    """
    # Pivotar o DataFrame para formato matriz
    df_pivot = df.pivot(index='Estado', columns='Métrica', values='Valor')
    
    # Criar mapa de calor
    fig = px.imshow(
        df_pivot,
        labels=dict(x="Métrica", y="Estado", color="Percentual (%)"),
        x=df_pivot.columns,
        y=df_pivot.index,
        color_continuous_scale='RdYlGn_r',  # Vermelho para valores altos (mais faltas), verde para baixos
        text_auto='.1f',
        aspect="auto"
    )
    
    # Configurar layout
    fig.update_layout(
        title="Mapa de Calor de Evasão por Estado",
        height=600,
        coloraxis_colorbar=dict(
            title="Percentual (%)",
            ticksuffix="%"
        )
    )
    
    return fig


def _criar_grafico_barras_evasao(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de barras para análise de evasão por estado.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados de evasão
        
    Retorna:
    --------
    Figure: Figura Plotly com gráfico de barras
    """
    # Criar gráfico de barras
    fig = px.bar(
        df,
        x='Estado',
        y='Valor',
        color='Métrica',
        labels={
            'Valor': 'Percentual (%)', 
            'Estado': 'Estado', 
            'Métrica': 'Tipo de Presença'
        },
        text_auto='.1f',
        barmode='group',
        color_discrete_sequence=cores_padrao()
    )
    
    # Configurar layout
    fig.update_layout(
        title="Análise de Presença e Evasão por Estado",
        xaxis_title="Estado",
        yaxis_title="Percentual (%)",
        xaxis=dict(tickangle=-45),
        yaxis=dict(ticksuffix="%"),
        height=500,
        legend=dict(
            title=dict(text="Tipo de Presença<br><sup>Clique para comparar tipos específicos</sup>"),
        )
    )
    
    return fig


def _criar_grafico_pizza_evasao(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de pizza para análise de distribuição de evasão.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados de evasão
        
    Retorna:
    --------
    Figure: Figura Plotly com gráfico de pizza
    """
    # Calcular média por métrica
    df_media = df.groupby('Métrica')['Valor'].mean().reset_index()
    
    # Criar gráfico de pizza
    fig = px.pie(
        df_media,
        values='Valor',
        names='Métrica',
        title="Distribuição Média de Presença e Evasão",
        hole=0.4,
        color_discrete_sequence=cores_padrao()
    )
    
    # Configurar layout
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}: %{value:.1f}%'
    )
    
    fig.update_layout(
        height=500,
        legend=dict(
            title=dict(text="Tipo de Presença"),
        )
    )
    
    return fig