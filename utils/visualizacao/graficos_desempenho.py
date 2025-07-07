import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure
import pandas as pd
import numpy as np
from scipy import stats
import warnings
from typing import Dict, List, Optional, Union, Tuple, Any
from utils.visualizacao.config_graficos import aplicar_layout_padrao, cores_padrao
from utils.helpers.cache_utils import memory_intensive_function
from utils.mappings import get_mappings

# Suprimir warnings específicos que podem aparecer em cálculos estatísticos
warnings.filterwarnings('ignore', category=RuntimeWarning, module='scipy')
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')
warnings.filterwarnings('ignore', message='overflow encountered in scalar power')
warnings.filterwarnings('ignore', message='overflow encountered in reduce')
warnings.filterwarnings('ignore', message='invalid value encountered in scalar subtract')

# Obter configurações de mapeamentos centralizados
mappings = get_mappings()
CONFIG_VIZ = mappings['config_visualizacao']
MAPEAMENTO_FAIXAS = mappings['mapeamento_faixas_salariais']
LIMIARES = mappings['limiares']

# Constantes para configuração de gráficos (a partir de mapeamentos)
ANGULO_EIXO_X = CONFIG_VIZ['angulo_eixo_x']
TAMANHO_MARCADOR_PADRAO = CONFIG_VIZ['tamanho_marcador']
OPACIDADE_PADRAO = CONFIG_VIZ['opacidade_padrao']
MIN_PONTOS_REGRESSAO = LIMIARES['min_pontos_regressao']
MIN_VALORES_UNICOS = CONFIG_VIZ['min_valores_unicos']
LARGURA_LINHA = CONFIG_VIZ['largura_linha']

def criar_grafico_comparativo_barras(
    df_resultados: pd.DataFrame, 
    variavel_selecionada: str, 
    variaveis_categoricas: Dict[str, Dict[str, Any]], 
    competencia_mapping: Dict[str, str], 
    barmode: str = 'group'
) -> Figure:
    """
    Cria o gráfico de barras comparativo para desempenho por categoria.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com os resultados por categoria e competência
    variavel_selecionada: str
        Nome da variável categórica selecionada
    variaveis_categoricas: Dict
        Dicionário com metadados das variáveis categóricas
    competencia_mapping: Dict
        Dicionário mapeando códigos de competência para nomes legíveis
    barmode: str, default='group'
        Modo de exibição das barras ('group' ou 'stack')
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de barras
    """
    # Verificar dados de entrada
    if df_resultados is None or df_resultados.empty:
        return _criar_grafico_vazio("Sem dados disponíveis para visualização")
    
    # Verificar estrutura mínima do DataFrame
    colunas_necessarias = ['Categoria', 'Competência', 'Média']
    colunas_faltantes = [col for col in colunas_necessarias if col not in df_resultados.columns]
    if colunas_faltantes:
        return _criar_grafico_vazio(f"Estrutura de dados incorreta. Colunas faltantes: {colunas_faltantes}")
    
    # Verificar se a variável selecionada existe no dicionário
    if variavel_selecionada not in variaveis_categoricas:
        return _criar_grafico_vazio(f"Variável '{variavel_selecionada}' não encontrada nos metadados")
    
    # Verificar se temos dados suficientes
    if len(df_resultados) == 0:
        return _criar_grafico_vazio("Nenhum dado encontrado após filtros aplicados")
    
    try:
        # Determinar título e componentes do texto
        componentes_titulo = _obter_componentes_titulo_comparativo(
            df_resultados, variavel_selecionada, variaveis_categoricas
        )
        
        titulo = f"Desempenho por {componentes_titulo['nome_variavel']}{componentes_titulo['filtro']}{componentes_titulo['ordenacao']}"
        
        # Criar gráfico
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
        
        # Aplicar estilização padrão
        fig = aplicar_layout_padrao(fig, titulo)
        fig = _aplicar_estilizacao_eixos_e_legenda(fig)
        
        return fig
        
    except Exception as e:
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


def criar_grafico_linha_desempenho(
    df_linha: pd.DataFrame, 
    variavel_selecionada: str, 
    variaveis_categoricas: Dict[str, Dict[str, Any]], 
    competencia_filtro: Optional[str] = None, 
    ordenar_decrescente: bool = False
) -> Figure:
    """
    Cria o gráfico de linha para visualização do desempenho por categoria.
    
    Parâmetros:
    -----------
    df_linha: DataFrame
        DataFrame com os dados preparados para visualização
    variavel_selecionada: str
        Nome da variável categórica selecionada
    variaveis_categoricas: Dict
        Dicionário com metadados das variáveis categóricas
    competencia_filtro: str, opcional
        Nome da competência para filtrar
    ordenar_decrescente: bool, default=False
        Se True, indica que os dados estão ordenados por valor decrescente
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de linha
    """
    # Validação de dados de entrada
    if df_linha is None:
        return _criar_grafico_vazio("Erro: dados não fornecidos")
        
    if df_linha.empty:
        return _criar_grafico_vazio("Sem dados disponíveis para visualização")
    
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Categoria', 'Competência', 'Média']
    colunas_faltantes = [col for col in colunas_necessarias if col not in df_linha.columns]
    if colunas_faltantes:
        return _criar_grafico_vazio(f"Estrutura de dados incorreta. Colunas faltantes: {colunas_faltantes}")
    
    if variavel_selecionada not in variaveis_categoricas:
        return _criar_grafico_vazio(f"Variável '{variavel_selecionada}' não encontrada nos metadados")
    
    try:
        # Determinar título adequado
        ordenacao_texto = " (ordenado por valor decrescente)" if ordenar_decrescente else ""
        
        # Verificar competências disponíveis de forma segura
        competencias_unicas = []
        try:
            competencias_unicas = df_linha['Competência'].unique()
        except Exception as e:
            return _criar_grafico_vazio("Erro ao processar competências dos dados")
        
        filtro_texto = f" - {competencia_filtro}" if competencia_filtro and len(competencias_unicas) == 1 else ""
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
        
        # Configurar espessura da linha
        fig.update_traces(line=dict(width=LARGURA_LINHA))
        
        # Aplicar estilização padrão
        fig = aplicar_layout_padrao(fig, titulo)
        fig = _aplicar_estilizacao_eixos_e_legenda(fig)
        
        return fig
        
    except Exception as e:
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


def criar_grafico_linha_estados(
    df_plot: pd.DataFrame, 
    area_selecionada: Optional[str] = None, 
    ordenado: bool = False, 
    por_regiao: bool = False
) -> Figure:
    """
    Cria o gráfico de linha para visualização do desempenho por estado ou região.
    
    Parâmetros:
    -----------
    df_plot: DataFrame
        DataFrame com dados preparados para visualização
    area_selecionada: str, opcional
        Área de conhecimento selecionada para filtrar o gráfico
    ordenado: bool, default=False
        Indica se os dados estão ordenados por desempenho
    por_regiao: bool, default=False
        Indica se os dados estão agrupados por região
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de linha
    """
    # Validação de dados
    if df_plot is None or df_plot.empty:
        return _criar_grafico_vazio("Sem dados disponíveis para visualização")
    
    if 'Estado' not in df_plot.columns or 'Área' not in df_plot.columns or 'Média' not in df_plot.columns:
        return _criar_grafico_vazio("Estrutura de dados incorreta para este gráfico")
    
    try:
        # Determinar título adequado
        tipo_localidade = "Região" if por_regiao else "Estado"
        titulo_base = f'Médias de Desempenho por {tipo_localidade} e Área de Conhecimento'
        sufixo = f" (ordenado por {area_selecionada})" if ordenado and area_selecionada else ""
        titulo_completo = f"{titulo_base}{sufixo}"
        
        fig = px.line(
            df_plot,
            x='Estado',
            y='Média',
            color='Área',
            markers=True,
            title=titulo_completo,
            labels={'Média': 'Nota Média', 'Estado': tipo_localidade, 'Área': 'Área de Conhecimento'},
            color_discrete_sequence=cores_padrao()
        )
        
        # Configurar espessura da linha
        fig.update_traces(line=dict(width=LARGURA_LINHA))
        
        # Aplicar estilização padrão
        fig = aplicar_layout_padrao(fig, titulo_completo)
        fig = _aplicar_estilizacao_eixos_e_legenda(fig, legenda_titulo="Área de Conhecimento")
        
        return fig
        
    except Exception as e:
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


@memory_intensive_function
def criar_grafico_scatter(
    df: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str, 
    competencia_mapping: Dict[str, str], 
    colorir_por_faixa: bool = False
) -> Figure:
    """
    Cria um gráfico de dispersão para mostrar a relação entre duas competências.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com os dados para visualização
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
    competencia_mapping: Dict
        Dicionário mapeando códigos de competência para nomes legíveis
    colorir_por_faixa: bool, default=False
        Se True, colorir pontos por faixa salarial
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o gráfico de dispersão
    """
    # Validação de dados
    if df is None or df.empty:
        return _criar_grafico_vazio("Sem dados disponíveis para visualização")
    
    
    if eixo_x not in df.columns or eixo_y not in df.columns:
        return _criar_grafico_vazio(f"Colunas de eixo não encontradas nos dados")
    
    if eixo_x not in competencia_mapping or eixo_y not in competencia_mapping:
        return _criar_grafico_vazio(f"Mapeamento de competências não encontrado")
    
    try:
        # Filtrar dados válidos
        df_valido = _filtrar_dados_validos_scatter(df, eixo_x, eixo_y)
        
        # Verificar se ainda temos dados suficientes após filtragem
        if len(df_valido) < 10:
            return _criar_grafico_vazio("Dados insuficientes para criar o gráfico de dispersão")
        
        # Criar gráfico básico
        fig = _criar_scatter_base(df_valido, eixo_x, eixo_y, competencia_mapping, colorir_por_faixa)
        
        # Adicionar linha de tendência
        fig = _adicionar_linha_tendencia_scatter(fig, df_valido, eixo_x, eixo_y)
        
        # Estilizar gráfico
        fig = _estilizar_grafico_scatter(fig, competencia_mapping, eixo_x, eixo_y)
        
        return fig
        
    except Exception as e:
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


def adicionar_linha_tendencia(
    fig: Figure, 
    df: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str, 
    nome: str
) -> Figure:
    """
    Adiciona uma linha de tendência a um gráfico de dispersão existente.
    
    Parâmetros:
    -----------
    fig: Figure
        Figura Plotly à qual adicionar a linha de tendência
    df: DataFrame
        DataFrame com os dados para calcular a tendência
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
    nome: str
        Nome para identificar a linha de tendência na legenda
        
    Retorna:
    --------
    Figure: Figura Plotly com a linha de tendência adicionada
    """
    # Validação de entrada
    if fig is None:
        return fig
        
    if df is None or df.empty or eixo_x not in df.columns or eixo_y not in df.columns:
        return fig
    
    # Remover valores NaN e verificar se temos dados suficientes
    df_valido = df.dropna(subset=[eixo_x, eixo_y])
    df_valido = df_valido[(df_valido[eixo_x] > 0) & (df_valido[eixo_y] > 0)]
    
    if len(df_valido) < MIN_PONTOS_REGRESSAO:
        return fig
    
    try:
        # Calcular a regressão linear
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df_valido[eixo_x], df_valido[eixo_y]
        )
        
        # Verificar se os resultados são válidos
        if np.isnan(slope) or np.isnan(intercept):
            return fig
        
        # Criar os pontos da linha
        x_range = np.linspace(
            df_valido[eixo_x].min(), 
            df_valido[eixo_x].max(), 
            100
        )
        y_pred = slope * x_range + intercept
        
        # Definir estilo da linha com base no nome
        estilo_linha = _definir_estilo_linha_tendencia(nome)
        
        # Adicionar linha de tendência
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=y_pred,
                mode='lines',
                name=f'Tendência {nome} (r={r_value:.2f})',
                line=dict(
                    color=estilo_linha['cor'], 
                    width=estilo_linha['largura'], 
                    dash=estilo_linha['tracado']
                ),
                hoverinfo='text',
                hovertext=f'Correlação: {r_value:.4f} | y = {slope:.2f}x + {intercept:.2f}'
            )
        )
        
        return fig
        
    except Exception as e:
        return fig


# Funções auxiliares

def _criar_grafico_vazio(mensagem: str = "Dados insuficientes para criar visualização") -> Figure:
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


def _obter_componentes_titulo_comparativo(
    df_resultados: pd.DataFrame, 
    variavel_selecionada: str, 
    variaveis_categoricas: Dict[str, Dict[str, Any]]
) -> Dict[str, str]:
    """
    Extrai componentes para construção do título do gráfico comparativo.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com resultados para visualização
    variavel_selecionada: str
        Nome da variável categórica selecionada
    variaveis_categoricas: Dict
        Dicionário com metadados das variáveis categóricas
        
    Retorna:
    --------
    Dict[str, str]: Dicionário com componentes do título
    """
    # Valor padrão caso não encontre a variável
    nome_variavel = variaveis_categoricas.get(
        variavel_selecionada, 
        {"nome": variavel_selecionada}
    ).get("nome", variavel_selecionada)
    
    ordenacao = ""
    filtro = ""
    
    # Verificar se estamos usando ordenação
    if 'Categoria' in df_resultados.columns:
        if isinstance(df_resultados['Categoria'].dtype, pd.CategoricalDtype) and df_resultados['Categoria'].dtype.ordered:
            ordenacao = " (ordenado por valor decrescente)"
    
    # Verificar se estamos filtrando por competência
    if 'Competência' in df_resultados.columns:
        competencias_unicas = df_resultados['Competência'].unique()
        if len(competencias_unicas) == 1:
            filtro = f" - {competencias_unicas[0]}"
    
    return {
        'nome_variavel': nome_variavel,
        'ordenacao': ordenacao,
        'filtro': filtro
    }


def _aplicar_estilizacao_eixos_e_legenda(
    fig: Figure, 
    legenda_titulo: str = "Área de Conhecimento"
) -> Figure:
    """
    Aplica estilização padrão aos eixos e legenda.
    
    Parâmetros:
    -----------
    fig: Figure
        Figura Plotly a ser estilizada
    legenda_titulo: str, default="Área de Conhecimento"
        Título a ser usado na legenda
        
    Retorna:
    --------
    Figure: Figura Plotly estilizada
    """
    if fig is None:
        return fig
        
    fig.update_layout(
        xaxis_tickangle=ANGULO_EIXO_X,
        legend_title=dict(text=f"{legenda_titulo}<br><sup>Clique para filtrar</sup>")
    )
    
    # Melhorar formato dos valores no eixo Y
    fig.update_yaxes(tickformat=".1f")
    
    return fig


def _filtrar_dados_validos_scatter(
    df: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str
) -> pd.DataFrame:
    """
    Filtra dados válidos para o gráfico de dispersão.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com dados para visualização
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
        
    Retorna:
    --------
    DataFrame: DataFrame com dados filtrados
    """
    try:
        # Filtrar dados válidos (remover zeros, NaN e valores extremos)
        df_filtrado = df[
            (df[eixo_x] > 0) & (df[eixo_y] > 0) & 
            (df[eixo_x] < 1000) & (df[eixo_y] < 1000) &  # Limitar valores extremos
            (~df[eixo_x].isna()) & (~df[eixo_y].isna()) &
            np.isfinite(df[eixo_x]) & np.isfinite(df[eixo_y])  # Garantir valores finitos
        ].copy()
        
        # Verificar se há outliers extremos que possam distorcer o gráfico
        if len(df_filtrado) > 0:
            try:
                q1_x, q3_x = df_filtrado[eixo_x].quantile([0.01, 0.99])
                q1_y, q3_y = df_filtrado[eixo_y].quantile([0.01, 0.99])
                
                # Verificar se os quantis são válidos
                if np.isfinite(q1_x) and np.isfinite(q3_x) and np.isfinite(q1_y) and np.isfinite(q3_y):
                    # Opcional: filtrar outliers extremos se necessário
                    pass
            except Exception:
                # Se houver erro no cálculo de quantis, continuar sem filtrar outliers
                pass
        
        # Remover outliers extremos (opcional - comentado por padrão)
        # df_filtrado = df_filtrado[(df_filtrado[eixo_x] >= q1_x) & (df_filtrado[eixo_x] <= q3_x) &
        #                           (df_filtrado[eixo_y] >= q1_y) & (df_filtrado[eixo_y] <= q3_y)]
        
        return df_filtrado
        
    except Exception as e:
        # Retornar dataframe vazio em caso de erro, mas manter as colunas originais
        try:
            return pd.DataFrame(columns=df.columns)
        except:
            return pd.DataFrame(columns=[eixo_x, eixo_y])


def _criar_scatter_base(
    df_valido: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str, 
    competencia_mapping: Dict[str, str], 
    colorir_por_faixa: bool
) -> Figure:
    """
    Cria o gráfico de dispersão base com as configurações apropriadas.
    
    Parâmetros:
    -----------
    df_valido: DataFrame
        DataFrame com dados válidos para visualização
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
    competencia_mapping: Dict
        Dicionário mapeando códigos de competência para nomes legíveis
    colorir_por_faixa: bool
        Se True, colorir pontos por faixa salarial
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly base
    """
    if colorir_por_faixa and 'TP_FAIXA_SALARIAL' in df_valido.columns:
        return _criar_scatter_colorido_por_faixa(df_valido, eixo_x, eixo_y, competencia_mapping)
    else:
        return _criar_scatter_simples(df_valido, eixo_x, eixo_y, competencia_mapping)


def _criar_scatter_colorido_por_faixa(
    df_valido: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str, 
    competencia_mapping: Dict[str, str]
) -> Figure:
    """
    Cria gráfico de dispersão colorido por faixa salarial.
    
    Parâmetros:
    -----------
    df_valido: DataFrame
        DataFrame com dados válidos para visualização
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
    competencia_mapping: Dict
        Dicionário mapeando códigos de competência para nomes legíveis
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly
    """
    try:
        # Garantir que temos dados para processar
        if df_valido.empty:
            return _criar_grafico_vazio("Dados insuficientes após filtragem")
            
        # Criar cópia para evitar SettingWithCopyWarning
        df_plot = df_valido.copy()
        
        # Converter para string para exibição
        df_plot['Faixa Salarial'] = df_plot['TP_FAIXA_SALARIAL'].map(MAPEAMENTO_FAIXAS)
        
        # Garantir ordem categórica
        ordem_categorias = [MAPEAMENTO_FAIXAS[i] for i in sorted(MAPEAMENTO_FAIXAS.keys())]
        df_plot['Faixa Salarial'] = pd.Categorical(
            df_plot['Faixa Salarial'],
            categories=ordem_categorias,
            ordered=True
        )
        
        # Título do gráfico
        titulo = f"Relação entre {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]} por Faixa Salarial"
        
        # Criar gráfico com coloração por faixa salarial
        fig = px.scatter(
            df_plot, 
            x=eixo_x, 
            y=eixo_y, 
            color='Faixa Salarial',
            labels={
                eixo_x: competencia_mapping[eixo_x], 
                eixo_y: competencia_mapping[eixo_y],
                'Faixa Salarial': 'Faixa Salarial'
            },
            title=titulo,
            opacity=OPACIDADE_PADRAO,
            color_discrete_sequence=px.colors.qualitative.Bold,
            category_orders={'Faixa Salarial': ordem_categorias}
        )
        
        # Aplicar layout padrão
        fig = aplicar_layout_padrao(fig, titulo)
        
        return fig
        
    except Exception as e:
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


def _criar_scatter_simples(
    df_valido: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str, 
    competencia_mapping: Dict[str, str]
) -> Figure:
    """
    Cria gráfico de dispersão simples sem coloração por categoria.
    
    Parâmetros:
    -----------
    df_valido: DataFrame
        DataFrame com dados válidos para visualização
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
    competencia_mapping: Dict
        Dicionário mapeando códigos de competência para nomes legíveis
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly
    """
    try:
        # Garantir que temos dados para processar
        if df_valido.empty:
            return _criar_grafico_vazio("Dados insuficientes após filtragem")
            
        # Título do gráfico
        titulo = f"Relação entre {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}"
        
        fig = px.scatter(
            df_valido, 
            x=eixo_x, 
            y=eixo_y, 
            labels={
                eixo_x: competencia_mapping[eixo_x], 
                eixo_y: competencia_mapping[eixo_y]
            },
            title=titulo,
            opacity=OPACIDADE_PADRAO,
            color_discrete_sequence=['#3366CC']
        )
        
        # Aplicar layout padrão
        fig = aplicar_layout_padrao(fig, titulo)
        
        return fig
        
    except Exception as e:
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


def _adicionar_linha_tendencia_scatter(
    fig: Figure, 
    df_valido: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str
) -> Figure:
    """
    Adiciona linha de tendência ao gráfico de dispersão.
    
    Parâmetros:
    -----------
    fig: Figure
        Figura Plotly base
    df_valido: DataFrame
        DataFrame com dados válidos para cálculo
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
        
    Retorna:
    --------
    Figure: Figura Plotly com linha de tendência adicionada
    """
    # Validação básica
    if fig is None or df_valido.empty:
        return fig
    
    try:
        x = df_valido[eixo_x].values
        y = df_valido[eixo_y].values
        
        # Verificações adicionais para garantir que podemos fazer uma regressão confiável
        if len(x) > MIN_PONTOS_REGRESSAO and len(np.unique(x)) > MIN_VALORES_UNICOS:
            # Validar dados antes da regressão para evitar overflow
            x_valid = x[(x > 0) & (x < 1000) & np.isfinite(x)]
            y_valid = y[(y > 0) & (y < 1000) & np.isfinite(y)]
            
            # Garantir que temos o mesmo número de pontos válidos
            if len(x_valid) == len(y_valid) and len(x_valid) > MIN_PONTOS_REGRESSAO:
                # Usar scipy.stats para maior robustez com tratamento de erro
                try:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, y_valid)
                    
                    # Verificar se o cálculo foi bem-sucedido e valores são finitos
                    if (not np.isnan(slope) and not np.isnan(intercept) and 
                        not np.isnan(r_value) and np.isfinite(slope) and 
                        np.isfinite(intercept) and np.isfinite(r_value)):
                        
                        # Criar pontos para a linha de tendência
                        x_min, x_max = np.min(x_valid), np.max(x_valid)
                        x_trend = np.array([x_min, x_max])
                        y_trend = slope * x_trend + intercept
                        
                        # Verificar se os valores da linha são válidos
                        if np.all(np.isfinite(y_trend)) and np.all(y_trend > 0) and np.all(y_trend < 1000):
                            # Adicionar linha com detalhes da correlação
                            fig.add_trace(
                                go.Scatter(
                                    x=x_trend,
                                    y=y_trend,
                                    mode='lines', 
                                    name=f'Tendência (r={r_value:.2f})',
                                    line=dict(color='red', dash='dash', width=2),
                                    opacity=OPACIDADE_PADRAO,
                                    hoverinfo='text',
                                    hovertext=f'Correlação: {r_value:.4f}<br>y = {slope:.2f}x + {intercept:.2f}'
                                )
                            )
                            
                            # Adicionar anotação com valor da correlação
                            fig.add_annotation(
                                x=0.95,
                                y=0.05,
                                xref='paper',
                                yref='paper',
                                text=f'Correlação (r): {r_value:.3f}',
                                showarrow=False,
                                font=dict(size=12),
                                bgcolor='rgba(255, 255, 255, 0.8)',
                                bordercolor='gray',
                                borderwidth=1,
                                borderpad=4
                            )
                except (ValueError, RuntimeWarning, OverflowError) as e:
                    # Silenciosamente falhar se houver problemas matemáticos
                    pass
        
        return fig
        
    except Exception as e:
        return fig


def _estilizar_grafico_scatter(
    fig: Figure, 
    competencia_mapping: Dict[str, str], 
    eixo_x: str, 
    eixo_y: str
) -> Figure:
    """
    Aplica estilização padrão ao gráfico de dispersão.
    
    Parâmetros:
    -----------
    fig: Figure
        Figura Plotly a ser estilizada
    competencia_mapping: Dict
        Dicionário mapeando códigos de competência para nomes legíveis
    eixo_x: str
        Nome da coluna para o eixo X
    eixo_y: str
        Nome da coluna para o eixo Y
        
    Retorna:
    --------
    Figure: Figura Plotly estilizada
    """
    # Validação básica
    if fig is None:
        return fig
    
    # Ajustar tamanho dos marcadores
    fig.update_traces(
        marker=dict(
            size=TAMANHO_MARCADOR_PADRAO,
            line=dict(width=0.5, color='DarkSlateGrey')
        ),
        selector=dict(mode='markers')
    )
    
    # Estilização do gráfico
    fig.update_layout(
        height=CONFIG_VIZ['altura_padrao_grafico'],
        xaxis_title=competencia_mapping.get(eixo_x, eixo_x),
        yaxis_title=competencia_mapping.get(eixo_y, eixo_y),
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)',
            tickformat='.0f'
        ),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)',
            tickformat='.0f'
        ),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white", 
            font_size=12, 
            font_family="Arial"
        )
    )
    
    return fig


def _definir_estilo_linha_tendencia(nome: str) -> Dict[str, Any]:
    """
    Define o estilo da linha de tendência com base no nome.
    
    Parâmetros:
    -----------
    nome: str
        Nome identificador da linha
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com atributos de estilo
    """
    # Estilo específico para Brasil (linha principal)
    if nome == 'Brasil':
        return {
            'cor': '#FF4B4B',  # Vermelho para Brasil
            'largura': 3,
            'tracado': 'solid'
        }
    # Estilo para linha de estados individuais
    elif nome.startswith('Estado'):
        return {
            'cor': '#1f77b4',  # Azul para estados
            'largura': 1.5,
            'tracado': 'dash'
        }
    # Estilo para linha de regiões - SUDESTE REMOVIDO
    elif nome in ['Norte', 'Nordeste', 'Centro-Oeste', 'Sul']:
        return {
            'cor': '#2CA02C',  # Verde para regiões
            'largura': 2,
            'tracado': 'dashdot'
        }
    # Estilo padrão para outros casos
    else:
        return {
            'cor': '#9467BD',  # Roxo para outros
            'largura': 1.5,
            'tracado': 'dot'
        }