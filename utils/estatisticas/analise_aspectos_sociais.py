import pandas as pd
import numpy as np

def calcular_estatisticas_distribuicao(contagem_aspecto):
    """
    Calcula estatísticas básicas sobre a distribuição de um aspecto social.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com a contagem de ocorrências por categoria
        
    Retorna:
    --------
    dict
        Dicionário com estatísticas calculadas
    """
    # Calcular total
    total = contagem_aspecto['Quantidade'].sum()
    
    # Encontrar categorias com maior e menor quantidade
    categoria_mais_frequente = contagem_aspecto.loc[contagem_aspecto['Quantidade'].idxmax()]
    categoria_menos_frequente = contagem_aspecto.loc[contagem_aspecto['Quantidade'].idxmin()]
    
    # Calcular média e mediana
    media = contagem_aspecto['Quantidade'].mean()
    mediana = contagem_aspecto['Quantidade'].median()
    
    # Calcular o índice de concentração (Gini simplificado)
    # Quanto mais próximo de 1, mais desigual a distribuição
    proporcoes = contagem_aspecto['Quantidade'] / total
    indice_concentracao = 1 - (1 / len(contagem_aspecto)) * (proporcoes**2).sum() * len(contagem_aspecto)
    
    # Retornar estatísticas em um dicionário
    return {
        'total': total,
        'categoria_mais_frequente': categoria_mais_frequente,
        'categoria_menos_frequente': categoria_menos_frequente,
        'num_categorias': len(contagem_aspecto),
        'media': media,
        'mediana': mediana,
        'indice_concentracao': indice_concentracao
    }


def analisar_correlacao_categorias(df_correlacao, var_x_plot, var_y_plot):
    """
    Analisa a correlação entre duas variáveis categóricas.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com os dados para análise
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    dict
        Dicionário com métricas de correlação
    """
    # Criar tabela de contingência
    tabela_contingencia = pd.crosstab(df_correlacao[var_x_plot], df_correlacao[var_y_plot])
    
    # Calcular qui-quadrado e coeficiente de contingência
    from scipy.stats import chi2_contingency
    chi2, p_valor, gl, _ = chi2_contingency(tabela_contingencia)
    
    # Coeficiente de contingência normalizado (0 a 1)
    n = tabela_contingencia.sum().sum()
    coef_contingencia = np.sqrt(chi2 / (chi2 + n))
    
    # Valor máximo do coeficiente (para normalização)
    k = min(len(tabela_contingencia), len(tabela_contingencia.columns))
    c_max = np.sqrt((k - 1) / k)
    
    # Coeficiente normalizado
    coef_normalizado = coef_contingencia / c_max
    
    # Calcular V de Cramer
    v_cramer = np.sqrt(chi2 / (n * min(tabela_contingencia.shape[0] - 1, tabela_contingencia.shape[1] - 1)))
    
    # Interpretar a força da associação
    if coef_normalizado < 0.2:
        interpretacao = "associação muito fraca"
    elif coef_normalizado < 0.4:
        interpretacao = "associação fraca"
    elif coef_normalizado < 0.6:
        interpretacao = "associação moderada"
    elif coef_normalizado < 0.8:
        interpretacao = "associação forte"
    else:
        interpretacao = "associação muito forte"
    
    # Interpretar V de Cramer
    if v_cramer < 0.1:
        contexto = "Associação negligenciável, indicando que estas características são praticamente independentes"
    elif v_cramer < 0.2:
        contexto = "Associação fraca, sugerindo que estas características compartilham uma pequena sobreposição"
    elif v_cramer < 0.3:
        contexto = "Associação moderada, indicando algum grau de relação entre estas características"
    else:
        contexto = "Associação forte, sugerindo uma importante conexão entre estas características sociais"
    
    # Retornar métricas com nomes padronizados
    return {
        'qui_quadrado': chi2,
        'gl': gl,
        'valor_p': p_valor,
        'coeficiente': coef_normalizado,
        'v_cramer': v_cramer,
        'interpretacao': interpretacao,
        'contexto': contexto,
        'significativo': p_valor < 0.05,
        'tabela_contingencia': tabela_contingencia
    }


def analisar_distribuicao_regional(df_por_estado, aspecto_social, categoria=None):
    """
    Analisa como um aspecto social se distribui regionalmente.
    
    Parâmetros:
    -----------
    df_por_estado : DataFrame
        DataFrame com dados por estado
    aspecto_social : str
        Nome do aspecto social analisado
    categoria : str, opcional
        Categoria específica para análise
        
    Retorna:
    --------
    dict
        Dicionário com análise regional
    """
    # Filtrar para uma categoria específica se solicitado
    if categoria:
        df_analise = df_por_estado[df_por_estado['Categoria'] == categoria].copy()
    else:
        # Se não houver categoria específica, usamos todo o dataframe
        df_analise = df_por_estado.copy()
    
    # Calcular estatísticas básicas
    percentual_medio = df_analise['Percentual'].mean()
    desvio_padrao = df_analise['Percentual'].std()
    coef_variacao = (desvio_padrao / percentual_medio) * 100 if percentual_medio > 0 else 0
    
    # Identificar estados com valores extremos
    maior_percentual = df_analise.loc[df_analise['Percentual'].idxmax()]
    menor_percentual = df_analise.loc[df_analise['Percentual'].idxmin()]
    
    # Verificar a magnitude da variabilidade
    if coef_variacao < 15:
        variabilidade = "Baixa variabilidade, indicando relativa homogeneidade regional"
    elif coef_variacao < 30:
        variabilidade = "Variabilidade moderada, sugerindo diferenças regionais significativas"
    else:
        variabilidade = "Alta variabilidade, mostrando importantes disparidades regionais"
    
    # Retornar análise
    return {
        'percentual_medio': percentual_medio,
        'desvio_padrao': desvio_padrao,
        'coef_variacao': coef_variacao,
        'maior_percentual': maior_percentual,
        'menor_percentual': menor_percentual,
        'variabilidade': variabilidade
    }