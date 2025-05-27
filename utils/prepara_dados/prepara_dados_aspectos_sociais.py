import pandas as pd
import numpy as np
from utils.helpers.cache_utils import optimized_cache

@optimized_cache()
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
    var_x_plot = aplicar_mapeamento(df_correlacao, var_x, variaveis_sociais)
        
    # Aplicar mapeamentos para variável Y
    var_y_plot = aplicar_mapeamento(df_correlacao, var_y, variaveis_sociais)
    
    return df_correlacao, var_x_plot, var_y_plot


def aplicar_mapeamento(df, variavel, variaveis_sociais):
    """
    Aplica mapeamento a uma variável se necessário e retorna o nome da coluna para uso em gráficos.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    variavel : str
        Nome da variável a ser mapeada
    variaveis_sociais : dict
        Dicionário com mapeamentos
        
    Retorna:
    --------
    str
        Nome da coluna a ser usada para plotagem
    """
    if variavel in variaveis_sociais and df[variavel].dtype != 'object':
        coluna_nome = f'{variavel}_NOME'
        df[coluna_nome] = df[variavel].map(variaveis_sociais[variavel]["mapeamento"])
        return coluna_nome
    return variavel


@optimized_cache()
def preparar_dados_distribuicao(microdados, aspecto_social, variaveis_sociais):
    """
    Prepara os dados para análise de distribuição de um aspecto social.
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com os microdados
    aspecto_social : str
        Nome do aspecto social a ser analisado
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações
        
    Retorna:
    --------
    tuple
        (DataFrame preparado, nome da coluna para plotar)
    """
    df_dist = microdados.copy()
    coluna_plot = aplicar_mapeamento(df_dist, aspecto_social, variaveis_sociais)
    return df_dist, coluna_plot


def contar_candidatos_por_categoria(df, coluna_plot):
    """
    Conta o número de candidatos em cada categoria de um aspecto social.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    coluna_plot : str
        Nome da coluna a ser contabilizada
        
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
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com contagem de candidatos por categoria
    aspecto_social : str
        Nome do aspecto social
    variaveis_sociais : dict
        Dicionário com configurações
        
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


def preparar_dados_heatmap(df_correlacao, var_x_plot, var_y_plot):
    """
    Prepara dados para visualização em heatmap.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com dados correlacionados
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    DataFrame
        DataFrame normalizado para heatmap
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Calcular percentuais (normalização)
    contagem_pivot = contagem.pivot(index=var_x_plot, columns=var_y_plot, values='Contagem')
    
    # Substituir NaN por 0
    contagem_pivot = contagem_pivot.fillna(0)
    
    # Normalizar por linha (para mostrar distribuição percentual)
    row_sums = contagem_pivot.sum(axis=1)
    normalized_pivot = contagem_pivot.div(row_sums, axis=0) * 100
    
    return normalized_pivot


def preparar_dados_barras_empilhadas(df_correlacao, var_x_plot, var_y_plot):
    """
    Prepara dados para visualização em barras empilhadas.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com dados correlacionados
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    DataFrame
        DataFrame formatado para barras empilhadas
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Preparar dados para barras empilhadas
    df_barras = contagem.copy()
    
    # Calcular totais por categoria X
    totais = df_barras.groupby(var_x_plot)['Contagem'].sum().to_dict()
    
    # Calcular percentual para cada combinação
    df_barras['Percentual'] = df_barras.apply(
        lambda row: (row['Contagem'] / totais[row[var_x_plot]] * 100) if totais[row[var_x_plot]] > 0 else 0, 
        axis=1
    )
        
    return df_barras


def preparar_dados_sankey(df_correlacao, var_x_plot, var_y_plot):
    """
    Prepara dados para visualização em diagrama de Sankey.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com dados correlacionados
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    tuple
        (labels, source, target, value) - dados para o diagrama Sankey
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Criar listas para o diagrama Sankey
    categorias_x = contagem[var_x_plot].unique()
    categorias_y = contagem[var_y_plot].unique()
    labels = list(categorias_x) + list(categorias_y)
    
    # Mapear valores para índices
    source_indices = {val: i for i, val in enumerate(categorias_x)}
    target_offset = len(source_indices)
    target_indices = {val: i + target_offset for i, val in enumerate(categorias_y)}
    
    # Criar listas de source, target e value
    source = [source_indices[s] for s in contagem[var_x_plot]]
    target = [target_indices[t] for t in contagem[var_y_plot]]
    value = contagem['Contagem'].tolist()
    
    return labels, source, target, value


@optimized_cache()
def preparar_dados_grafico_aspectos_por_estado(microdados_estados, aspecto_social, estados_selecionados, variaveis_sociais, agrupar_por_regiao=False):
    """
    Prepara os dados para o gráfico de distribuição de aspectos sociais por estado ou região.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados dos estados selecionados
    aspecto_social : str
        Nome do aspecto social a ser analisado
    estados_selecionados : list
        Lista de estados selecionados para análise
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis sociais
    agrupar_por_regiao : bool, default=False
        Se True, agrupa os dados por região em vez de mostrar por estado
    
    Retorna:
    --------
    DataFrame
        DataFrame formatado para o gráfico de linha por estado/região
    """
    # Verificar se a coluna existe nos dados
    if aspecto_social not in microdados_estados.columns:
        return pd.DataFrame()
    
    # Criar cópia para não modificar o DataFrame original
    df = microdados_estados.copy()
    
    # Aplicar mapeamento se disponível
    coluna_plot = aplicar_mapeamento(df, aspecto_social, variaveis_sociais)
    
    # Obter lista de todas as categorias possíveis para o aspecto social
    if "mapeamento" in variaveis_sociais[aspecto_social]:
        categorias = list(variaveis_sociais[aspecto_social]["mapeamento"].values())
    else:
        categorias = df[coluna_plot].unique().tolist()
    
    # Otimização: Pré-calcular a contagem para todos os estados de uma vez
    agrupado = df.groupby(['SG_UF_PROVA', coluna_plot]).size().reset_index(name='Quantidade')
    
    # Calcular totais por estado
    totais_por_estado = df.groupby('SG_UF_PROVA').size().reset_index(name='Total')
    
    # Mesclar para obter totais
    agrupado = agrupado.merge(totais_por_estado, on='SG_UF_PROVA', how='left')
    
    # Calcular percentuais
    agrupado['Percentual'] = (agrupado['Quantidade'] / agrupado['Total'] * 100).round(2)
    
    # Filtrar apenas para estados selecionados
    agrupado = agrupado[agrupado['SG_UF_PROVA'].isin(estados_selecionados)]
    
    # Renomear colunas para o formato esperado
    agrupado = agrupado.rename(columns={'SG_UF_PROVA': 'Estado', coluna_plot: 'Categoria'})
    
    # Selecionar apenas as colunas necessárias
    resultado = agrupado[['Estado', 'Categoria', 'Quantidade', 'Percentual']]
    
    # Se o DataFrame estiver vazio, retorna um DataFrame vazio
    if len(resultado) == 0:
        return pd.DataFrame()
    
    # Agrupar por região se solicitado
    if agrupar_por_regiao:
        from utils.helpers.regiao_utils import agrupar_por_regiao as agrupar_regiao
        resultado = agrupar_regiao(resultado, coluna_estado='Estado', coluna_valores='Percentual')
        
        # Converter a coluna Estado para categórico
        regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
        resultado['Estado'] = pd.Categorical(resultado['Estado'], categories=regioes)
    
    # Ordenar resultado para garantir consistência na visualização
    resultado = resultado.sort_values(['Estado', 'Categoria'])
        
    return resultado