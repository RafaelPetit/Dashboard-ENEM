import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.graph_objs import Figure
from typing import Dict, Tuple, Any
from utils.visualizacao.config_graficos import cores_padrao
from utils.helpers.cache_utils import memory_intensive_function
from utils.helpers.mappings import get_mappings

# Obter configurações de mapeamentos centralizados
mappings = get_mappings()
CONFIG_VIZ = mappings.get('config_visualizacao', {})
LIMIARES_PROCESSAMENTO = mappings.get('limiares_processamento', {})

# Constantes para configuração de gráficos (a partir de mapeamentos)
ALTURA_PADRAO = CONFIG_VIZ.get('altura_padrao_grafico', 500)
OPACIDADE_PADRAO = CONFIG_VIZ.get('opacidade_padrao', 0.8)
ANGULO_EIXO_X = CONFIG_VIZ.get('angulo_eixo_x', -45)
MIN_AMOSTRAS_GRAFICO = LIMIARES_PROCESSAMENTO.get('min_amostras_grafico', 10)

@memory_intensive_function
def criar_grafico_heatmap(
    df_correlacao: pd.DataFrame, 
    var_x: str, 
    var_y: str, 
    var_x_plot: str, 
    var_y_plot: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    estados_texto: str
) -> Tuple[Figure, str]:
    """
    Cria um heatmap para visualizar a correlação entre duas variáveis sociais.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com os dados correlacionados
    var_x : str
        Código da variável para o eixo X
    var_y : str
        Código da variável para o eixo Y
    var_x_plot : str
        Nome da coluna para o eixo X (mapeada)
    var_y_plot : str
        Nome da coluna para o eixo Y (mapeada)
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
    estados_texto : str
        Texto descritivo dos estados incluídos na análise
        
    Retorna:
    --------
    Tuple[Figure, str]
        (Figura do gráfico, texto explicativo)
    """
    # Validação de dados
    if df_correlacao is None or df_correlacao.empty:
        return _criar_grafico_vazio("Dados insuficientes para análise de correlação"), ""
    
    # Verificar se as variáveis existem no dicionário de mapeamentos
    if var_x not in variaveis_sociais or var_y not in variaveis_sociais:
        return _criar_grafico_vazio("Variáveis não encontradas nos mapeamentos"), ""
    
    # Verificar se as colunas de plotagem existem no DataFrame
    if var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        return _criar_grafico_vazio(f"Colunas {var_x_plot} e/ou {var_y_plot} não encontradas nos dados"), ""
    
    try:
        # Usar a função de preparação de dados
        from utils.prepara_dados import preparar_dados_heatmap
        normalized_pivot = preparar_dados_heatmap(df_correlacao, var_x_plot, var_y_plot)
        
        # Verificar se temos um resultado válido
        if normalized_pivot is None or normalized_pivot.empty:
            return _criar_grafico_vazio("Não foi possível preparar os dados para o heatmap"), ""
        
        # Título formatado
        titulo = _formatar_titulo_correlacao(variaveis_sociais, var_x, var_y, estados_texto)
        
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
            title=titulo,
            text_auto='.1f'  # Mostrar valores com 1 casa decimal
        )
        
        # Ajustar layout
        fig.update_layout(
            height=ALTURA_PADRAO,
            xaxis={'side': 'bottom', 'tickangle': ANGULO_EIXO_X},
            coloraxis_colorbar=dict(title="Percentual (%)"),
            plot_bgcolor='white',
            font=dict(size=12)
        )
        
        # Importar texto explicativo
        from utils.explicacao.explicacao_aspectos_sociais import get_explicacao_heatmap
        explicacao = get_explicacao_heatmap(
            variaveis_sociais[var_x]['nome'], 
            variaveis_sociais[var_y]['nome']
        )
        
        return fig, explicacao
    
    except Exception as e:
        print(f"Erro ao criar heatmap: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}"), ""

# Corrigir a função criar_grafico_barras_empilhadas

@memory_intensive_function
def criar_grafico_barras_empilhadas(
    df_correlacao: pd.DataFrame, 
    var_x: str, 
    var_y: str, 
    var_x_plot: str, 
    var_y_plot: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    estados_texto: str
) -> Tuple[Figure, str]:
    """
    Cria um gráfico de barras empilhadas para visualizar a correlação entre duas variáveis sociais.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com os dados correlacionados
    var_x : str
        Código da variável para o eixo X
    var_y : str
        Código da variável para o eixo Y
    var_x_plot : str
        Nome da coluna para o eixo X (mapeada)
    var_y_plot : str
        Nome da coluna para o eixo Y (mapeada)
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
    estados_texto : str
        Texto descritivo dos estados incluídos na análise
        
    Retorna:
    --------
    Tuple[Figure, str]
        (Figura do gráfico, texto explicativo)
    """
    # Validação de dados
    if df_correlacao is None or df_correlacao.empty:
        return _criar_grafico_vazio("Dados insuficientes para análise de correlação"), ""
    
    # Verificar se as variáveis existem no dicionário de mapeamentos
    if var_x not in variaveis_sociais or var_y not in variaveis_sociais:
        return _criar_grafico_vazio("Variáveis não encontradas nos mapeamentos"), ""
    
    # Verificar se as colunas de plotagem existem no DataFrame
    if var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        return _criar_grafico_vazio(f"Colunas {var_x_plot} e/ou {var_y_plot} não encontradas nos dados"), ""
    
    try:
        # Usar a função de preparação de dados
        from utils.prepara_dados import preparar_dados_barras_empilhadas
        df_barras = preparar_dados_barras_empilhadas(df_correlacao, var_x_plot, var_y_plot)
        
        # Verificar se temos um resultado válido
        if df_barras is None or df_barras.empty:
            return _criar_grafico_vazio("Não foi possível preparar os dados para o gráfico de barras"), ""
        
        # Título formatado
        titulo = f"Distribuição de {variaveis_sociais[var_y]['nome']} por {variaveis_sociais[var_x]['nome']} ({estados_texto})"
        
        # Criar gráfico de barras empilhadas
        fig = px.bar(
            df_barras,
            x=var_x_plot,
            y='Percentual',
            color=var_y_plot,
            title=titulo,
            labels={
                var_x_plot: variaveis_sociais[var_x]['nome'],
                'Percentual': 'Percentual (%)',
                var_y_plot: variaveis_sociais[var_y]['nome']
            },
            text_auto='.1f',
            color_discrete_sequence=cores_padrao()
        )
        
        # Ajustar layout para barras empilhadas com legenda interativa
        fig = _configurar_layout_barras_empilhadas(fig, variaveis_sociais[var_y]['nome'])
        
        # Importar texto explicativo
        from utils.explicacao.explicacao_aspectos_sociais import get_explicacao_barras_empilhadas
        explicacao = get_explicacao_barras_empilhadas(
            variaveis_sociais[var_x]['nome'], 
            variaveis_sociais[var_y]['nome']
        )
        
        return fig, explicacao
    
    except Exception as e:
        print(f"Erro ao criar gráfico de barras empilhadas: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}"), ""

@memory_intensive_function
def criar_grafico_sankey(
    df_correlacao: pd.DataFrame, 
    var_x: str, 
    var_y: str, 
    var_x_plot: str, 
    var_y_plot: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    estados_texto: str
) -> Tuple[Figure, str]:
    """
    Cria um diagrama de Sankey para visualizar o fluxo entre duas variáveis sociais.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com os dados correlacionados
    var_x : str
        Código da variável para o eixo X
    var_y : str
        Código da variável para o eixo Y
    var_x_plot : str
        Nome da coluna para o eixo X (mapeada)
    var_y_plot : str
        Nome da coluna para o eixo Y (mapeada)
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
    estados_texto : str
        Texto descritivo dos estados incluídos na análise
        
    Retorna:
    --------
    Tuple[Figure, str]
        (Figura do gráfico, texto explicativo)
    """
    # Validação de dados
    if df_correlacao is None or df_correlacao.empty:
        return _criar_grafico_vazio("Dados insuficientes para análise de fluxo"), ""
    
    # Verificar se as variáveis existem no dicionário de mapeamentos
    if var_x not in variaveis_sociais or var_y not in variaveis_sociais:
        return _criar_grafico_vazio("Variáveis não encontradas nos mapeamentos"), ""
    
    # Verificar se as colunas de plotagem existem no DataFrame
    if var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        return _criar_grafico_vazio(f"Colunas {var_x_plot} e/ou {var_y_plot} não encontradas nos dados"), ""
    
    try:
        # Usar a função de preparação de dados
        from utils.prepara_dados import preparar_dados_sankey
        labels, source, target, value = preparar_dados_sankey(df_correlacao, var_x_plot, var_y_plot)
        
        # Verificar se temos dados válidos
        if not labels or not source or not target or not value:
            return _criar_grafico_vazio("Não foi possível preparar os dados para o diagrama Sankey"), ""
        
        if len(labels) < 3 or len(source) < 2:  # Mínimo para um diagrama Sankey útil
            return _criar_grafico_vazio("Dados insuficientes para um diagrama Sankey significativo"), ""
        
        # Criar cores para nós (com verificação de limites)
        cores_primarias = px.colors.qualitative.Pastel
        cores_secundarias = px.colors.qualitative.Bold
        
        node_colors = (
            cores_primarias[:min(len(set(source)), len(cores_primarias))] + 
            cores_secundarias[:min(len(set(target)), len(cores_secundarias))]
        )
        
        # Título formatado
        titulo = f"Fluxo entre {variaveis_sociais[var_x]['nome']} e {variaveis_sociais[var_y]['nome']} ({estados_texto})"
        
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
            title=titulo,
            height=600,
            font=dict(size=12),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Importar texto explicativo
        from utils.explicacao.explicacao_aspectos_sociais import get_explicacao_sankey
        explicacao = get_explicacao_sankey(
            variaveis_sociais[var_x]['nome'], 
            variaveis_sociais[var_y]['nome']
        )
        
        return fig, explicacao
    
    except Exception as e:
        print(f"Erro ao criar diagrama Sankey: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}"), ""


@memory_intensive_function
def criar_grafico_distribuicao(
    contagem_aspecto: pd.DataFrame, 
    opcao_viz: str, 
    aspecto_social: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> Figure:
    """
    Cria um gráfico de distribuição baseado no tipo selecionado pelo usuário.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com a contagem de ocorrências por categoria
    opcao_viz : str
        Tipo de visualização selecionada ('Gráfico de Barras', 'Gráfico de Linha', 'Gráfico de Pizza')
    aspecto_social : str
        Código do aspecto social analisado
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
        
    Retorna:
    --------
    Figure
        Objeto plotly.graph_objects.Figure
    """
    # Validação de dados
    if contagem_aspecto is None or contagem_aspecto.empty:
        return _criar_grafico_vazio("Dados insuficientes para visualização de distribuição")
    
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Categoria', 'Quantidade', 'Percentual']
    if not all(col in contagem_aspecto.columns for col in colunas_necessarias):
        return _criar_grafico_vazio("Estrutura de dados incorreta para visualização")
    
    # Verificar se o aspecto social existe no dicionário
    if aspecto_social not in variaveis_sociais:
        return _criar_grafico_vazio(f"Aspecto social '{aspecto_social}' não encontrado nos mapeamentos")
    
    try:
        # Nome formatado do aspecto social
        nome_aspecto = variaveis_sociais[aspecto_social]["nome"]
        
        # Título do gráfico
        titulo = f'Distribuição de {nome_aspecto}'
        
        # Verificar tipo de visualização e criar gráfico correspondente
        if opcao_viz == "Gráfico de Barras":
            fig = _criar_grafico_barras_distribuicao(contagem_aspecto, titulo, nome_aspecto)
        elif opcao_viz == "Gráfico de Linha":
            fig = _criar_grafico_linha_distribuicao(contagem_aspecto, titulo, nome_aspecto)
        else:  # Gráfico de Pizza
            fig = _criar_grafico_pizza_distribuicao(contagem_aspecto, titulo, nome_aspecto)
        
        # Configurar layout específico para cada tipo de gráfico
        fig = _configurar_layout_grafico_distribuicao(
            fig, opcao_viz, contagem_aspecto, aspecto_social, variaveis_sociais
        )
        
        return fig
    
    except Exception as e:
        print(f"Erro ao criar gráfico de distribuição: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


@memory_intensive_function
def criar_grafico_aspectos_por_estado(
    df_plot: pd.DataFrame, 
    aspecto_social: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    por_regiao: bool = False
) -> Figure:
    """
    Cria um gráfico de linha para visualizar a distribuição de um aspecto social por estado ou região.
    
    Parâmetros:
    -----------
    df_plot : DataFrame
        DataFrame formatado com os dados para visualização
    aspecto_social : str
        Código do aspecto social a ser visualizado
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
    por_regiao : bool, default=False
        Se True, os dados estão agrupados por região
        
    Retorna:
    --------
    Figure
        Objeto plotly.graph_objects.Figure
    """
    # Validação de dados
    if df_plot is None or df_plot.empty:
        return _criar_grafico_vazio("Dados insuficientes para visualização por estado/região")
    
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Estado', 'Categoria', 'Percentual']
    if not all(col in df_plot.columns for col in colunas_necessarias):
        return _criar_grafico_vazio("Estrutura de dados incorreta para visualização por estado/região")
    
    # Verificar se o aspecto social existe no dicionário
    if aspecto_social not in variaveis_sociais:
        return _criar_grafico_vazio(f"Aspecto social '{aspecto_social}' não encontrado nos mapeamentos")
    
    try:
        # Determinar tipo de localidade para rótulos
        tipo_localidade = "Região" if por_regiao else "Estado"
        
        # Nome formatado do aspecto social
        nome_aspecto = variaveis_sociais[aspecto_social]["nome"]
        
        # Título do gráfico
        titulo = f'Distribuição de {nome_aspecto} por {tipo_localidade}'
        
        # Criar gráfico de linha
        fig = px.line(
            df_plot,
            x='Estado',
            y='Percentual',
            color='Categoria',
            markers=True,
            labels={
                'Estado': tipo_localidade,
                'Percentual': 'Percentual (%)',
                'Categoria': nome_aspecto
            },
            color_discrete_sequence=cores_padrao()
        )
        
        # Configurar layout do gráfico
        fig.update_layout(
            title=titulo,
            height=ALTURA_PADRAO,
            xaxis_title=tipo_localidade,
            yaxis_title="Percentual (%)",
            yaxis=dict(ticksuffix="%"),
            legend_title=nome_aspecto,
            xaxis=dict(tickangle=ANGULO_EIXO_X),
            plot_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(
                title=dict(text=f"{nome_aspecto}<br><sup>Clique para filtrar</sup>"),
            )
        )
        
        # Configurar linhas (espessura e marcadores)
        fig.update_traces(
            line=dict(width=2),
            marker=dict(size=8),
            mode='lines+markers'
        )
        
        return fig
    
    except Exception as e:
        print(f"Erro ao criar gráfico por estado/região: {e}")
        return _criar_grafico_vazio(f"Erro ao criar visualização: {str(e)}")


# Funções auxiliares para formatação de gráficos

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


def _formatar_titulo_correlacao(
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    var_x: str, 
    var_y: str, 
    estados_texto: str
) -> str:
    """
    Formata o título para gráficos de correlação.
    
    Parâmetros:
    -----------
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
    var_x : str
        Código da variável para o eixo X
    var_y : str
        Código da variável para o eixo Y
    estados_texto : str
        Texto descritivo dos estados incluídos na análise
        
    Retorna:
    --------
    str
        Título formatado
    """
    # Obter nomes amigáveis das variáveis
    nome_x = variaveis_sociais.get(var_x, {}).get('nome', var_x)
    nome_y = variaveis_sociais.get(var_y, {}).get('nome', var_y)
    
    # Adicionar informação dos estados se disponível
    sufixo = f" ({estados_texto})" if estados_texto else ""
    
    return f"Relação entre {nome_x} e {nome_y}{sufixo}"


def _configurar_layout_barras_empilhadas(fig: Figure, nome_variavel_y: str) -> Figure:
    """
    Configura o layout específico para gráficos de barras empilhadas.
    
    Parâmetros:
    -----------
    fig : Figure
        Figura Plotly a ser configurada
    nome_variavel_y : str
        Nome da variável no eixo Y
        
    Retorna:
    --------
    Figure
        Figura configurada
    """
    fig.update_layout(
        height=ALTURA_PADRAO,
        xaxis={'tickangle': ANGULO_EIXO_X},
        plot_bgcolor='white',
        barmode='stack',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        # Configuração de legenda otimizada para muitas categorias
        legend=dict(
            title=dict(text=f"{nome_variavel_y} <br><sup>Clique para filtrar</sup>"),
            orientation="v",  # Vertical (lado direito)
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
    
    return fig


def _criar_grafico_barras_distribuicao(
    contagem_aspecto: pd.DataFrame, 
    titulo: str, 
    nome_aspecto: str
) -> Figure:
    """
    Cria um gráfico de barras para visualização de distribuição.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com contagem por categoria
    titulo : str
        Título do gráfico
    nome_aspecto : str
        Nome do aspecto social
        
    Retorna:
    --------
    Figure
        Figura Plotly
    """
    fig = px.bar(
        contagem_aspecto,
        x='Categoria',
        y='Quantidade',
        text='Quantidade',
        title=titulo,
        labels={
            'Categoria': nome_aspecto,
            'Quantidade': 'Número de Candidatos'
        },
        color='Quantidade',
        color_continuous_scale='Blues',
        category_orders={"Categoria": list(contagem_aspecto['Categoria'])}
    )
    
    # Configurar formato dos números (sem casas decimais)
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    
    return fig


def _criar_grafico_linha_distribuicao(
    contagem_aspecto: pd.DataFrame, 
    titulo: str, 
    nome_aspecto: str
) -> Figure:
    """
    Cria um gráfico de linha para visualização de distribuição.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com contagem por categoria
    titulo : str
        Título do gráfico
    nome_aspecto : str
        Nome do aspecto social
        
    Retorna:
    --------
    Figure
        Figura Plotly
    """
    fig = px.line(
        contagem_aspecto,
        x='Categoria',
        y='Quantidade',
        markers=True,
        title=titulo,
        labels={
            'Categoria': nome_aspecto,
            'Quantidade': 'Número de Candidatos'
        },
        color_discrete_sequence=['#3366CC'],
        category_orders={"Categoria": list(contagem_aspecto['Categoria'])}
    )
    
    # Configurar espessura da linha e tamanho dos marcadores
    fig.update_traces(
        line=dict(width=2),
        marker=dict(size=8),
        mode='lines+markers'
    )
    
    return fig


def _criar_grafico_pizza_distribuicao(
    contagem_aspecto: pd.DataFrame, 
    titulo: str, 
    nome_aspecto: str
) -> Figure:
    """
    Cria um gráfico de pizza para visualização de distribuição.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com contagem por categoria
    titulo : str
        Título do gráfico
    nome_aspecto : str
        Nome do aspecto social
        
    Retorna:
    --------
    Figure
        Figura Plotly
    """
    fig = px.pie(
        contagem_aspecto,
        names='Categoria',
        values='Quantidade',
        title=titulo,
        hover_data=['Percentual'],
        labels={'Quantidade': 'Número de Candidatos'},
        color_discrete_sequence=cores_padrao()
    )
    
    # Configurar exibição de texto nos setores
    fig.update_traces(
        textinfo='percent+label', 
        sort=False,
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value:,.0f}<br>Percentual: %{customdata[0]:.2f}%<extra></extra>'
    )
    
    return fig


def _configurar_layout_grafico_distribuicao(
    fig: Figure, 
    opcao_viz: str, 
    contagem_aspecto: pd.DataFrame, 
    aspecto_social: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> Figure:
    """
    Configura o layout do gráfico de distribuição.
    
    Parâmetros:
    -----------
    fig : Figure
        Objeto figura do plotly
    opcao_viz : str
        Tipo de visualização selecionada
    contagem_aspecto : DataFrame
        DataFrame com os dados de contagem
    aspecto_social : str
        Código do aspecto social selecionado
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
        
    Retorna:
    --------
    Figure
        Figura configurada
    """
    # Nome amigável do aspecto social
    nome_aspecto = variaveis_sociais.get(aspecto_social, {}).get('nome', aspecto_social)
    
    if opcao_viz != "Gráfico de Pizza":
        # Configuração para gráficos de barras e linha
        fig.update_layout(
            height=ALTURA_PADRAO,
            xaxis=dict(
                tickangle=ANGULO_EIXO_X, 
                categoryorder='array', 
                categoryarray=list(contagem_aspecto['Categoria'])
            ),
            plot_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            yaxis=dict(
                title="Número de Candidatos",
                tickformat=",d"  # Formato de números inteiros com separador de milhares
            ),
            margin=dict(l=50, r=50, t=80, b=80)  # Ajustar margens
        )
    else:  
        # Configuração específica para gráfico de pizza
        fig.update_layout(
            height=ALTURA_PADRAO,
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(
                title=dict(text=f"{nome_aspecto} <br><sup>Clique para filtrar</sup>"),
                traceorder="normal"
            ),
            margin=dict(l=20, r=20, t=80, b=20)  # Margens reduzidas para pizza
        )
    
    return fig