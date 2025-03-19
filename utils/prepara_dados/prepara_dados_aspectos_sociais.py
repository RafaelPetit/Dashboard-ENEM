import pandas as pd
import numpy as np

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
    if var_x in variaveis_sociais and df_correlacao[var_x].dtype != 'object':
        df_correlacao[f'{var_x}_NOME'] = df_correlacao[var_x].map(variaveis_sociais[var_x]["mapeamento"])
        var_x_plot = f'{var_x}_NOME'
    else:
        var_x_plot = var_x
        
    # Aplicar mapeamentos para variável Y
    if var_y in variaveis_sociais and df_correlacao[var_y].dtype != 'object':
        df_correlacao[f'{var_y}_NOME'] = df_correlacao[var_y].map(variaveis_sociais[var_y]["mapeamento"])
        var_y_plot = f'{var_y}_NOME'
    else:
        var_y_plot = var_y
    
    return df_correlacao, var_x_plot, var_y_plot


def preparar_dados_distribuicao(microdados, aspecto_social, variaveis_sociais):
    """
    Prepara os dados para análise de distribuição de um aspecto social.
    
    Retorna:
    --------
    tuple
        (DataFrame preparado, nome da coluna para plotar)
    """
    df_dist = microdados.copy()
    
    if df_dist[aspecto_social].dtype != 'object':
        df_dist[f'{aspecto_social}_NOME'] = df_dist[aspecto_social].map(
            variaveis_sociais[aspecto_social]["mapeamento"]
        )
        coluna_plot = f'{aspecto_social}_NOME'
    else:
        coluna_plot = aspecto_social
        
    return df_dist, coluna_plot


def contar_candidatos_por_categoria(df, coluna_plot):
    """
    Conta o número de candidatos em cada categoria de um aspecto social.
    
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
        DataFrame com os dados preparados para heatmap
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Calcular percentuais (normalização)
    contagem_pivot = contagem.pivot(index=var_x_plot, columns=var_y_plot, values='Contagem')
    
    # Substituir NaN por 0
    contagem_pivot = contagem_pivot.fillna(0)
    
    # Normalizar por linha (para mostrar distribuição percentual)
    normalized_pivot = contagem_pivot.div(contagem_pivot.sum(axis=1), axis=0) * 100
    
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
        DataFrame com os dados preparados para barras empilhadas
    """
    # Contar ocorrências para cada combinação
    contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
    
    # Preparar dados para barras empilhadas
    df_barras = contagem.copy()
    df_barras['Percentual'] = 0.0
    
    # Calcular percentual por categoria X
    for idx, row in df_barras.iterrows():
        total = df_barras[df_barras[var_x_plot] == row[var_x_plot]]['Contagem'].sum()
        df_barras.at[idx, 'Percentual'] = (row['Contagem'] / total * 100) if total > 0 else 0
        
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
    labels = list(contagem[var_x_plot].unique()) + list(contagem[var_y_plot].unique())
    
    # Mapear valores para índices
    source_indices = {val: i for i, val in enumerate(contagem[var_x_plot].unique())}
    target_offset = len(source_indices)
    target_indices = {val: i + target_offset for i, val in enumerate(contagem[var_y_plot].unique())}
    
    # Criar listas de source, target e value
    source = [source_indices[s] for s in contagem[var_x_plot]]
    target = [target_indices[t] for t in contagem[var_y_plot]]
    value = contagem['Contagem'].tolist()
    
    return labels, source, target, value

def preparar_dados_grafico_aspectos_por_estado(microdados_estados, aspecto_social, estados_selecionados, variaveis_sociais):
    """
    Prepara os dados para o gráfico de distribuição de aspectos sociais por estado.
    
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
    
    Retorna:
    --------
    DataFrame
        DataFrame formatado para o gráfico de linha por estado
    """
    # Criar cópia para não modificar o DataFrame original
    df = microdados_estados.copy()
    
    # Verificar se a coluna existe nos dados
    if aspecto_social not in df.columns:
        return pd.DataFrame()
    
    # Aplicar mapeamento se disponível
    if "mapeamento" in variaveis_sociais[aspecto_social]:
        mapeamento = variaveis_sociais[aspecto_social]["mapeamento"]
        df[f'{aspecto_social}_NOME'] = df[aspecto_social].map(mapeamento)
        coluna_plot = f'{aspecto_social}_NOME'
    else:
        coluna_plot = aspecto_social
    
    # Obter lista de todas as categorias possíveis para o aspecto social
    if "mapeamento" in variaveis_sociais[aspecto_social]:
        categorias = list(variaveis_sociais[aspecto_social]["mapeamento"].values())
    else:
        categorias = df[coluna_plot].unique().tolist()
    
    # Criar DataFrame para armazenar resultados
    resultados = []
    
    # Para cada estado, calcular a distribuição do aspecto social
    for estado in estados_selecionados:
        estado_df = df[df['SG_UF_PROVA'] == estado]
        
        if len(estado_df) == 0:
            continue
            
        # Contar frequência de cada categoria
        contagem = estado_df[coluna_plot].value_counts().reset_index()
        contagem.columns = ['Categoria', 'Quantidade']
        total_estado = contagem['Quantidade'].sum()
        
        # Calcular percentual para cada categoria
        for categoria in categorias:
            cat_row = contagem[contagem['Categoria'] == categoria]
            if len(cat_row) > 0:
                quantidade = cat_row['Quantidade'].values[0]
                percentual = (quantidade / total_estado * 100).round(2)
            else:
                quantidade = 0
                percentual = 0.0
                
            resultados.append({
                'Estado': estado,
                'Categoria': categoria,
                'Quantidade': quantidade,
                'Percentual': percentual
            })
    
    # Criar DataFrame com todos os resultados
    df_resultados = pd.DataFrame(resultados)
    
    # Se o DataFrame estiver vazio, retorna um DataFrame vazio
    if len(df_resultados) == 0:
        return pd.DataFrame()
        
    return df_resultados