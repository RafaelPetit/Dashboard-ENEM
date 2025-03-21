import streamlit as st
import pandas as pd
import numpy as np

def criar_expander_analise_correlacao(df_preparado, var_x, var_y, var_x_plot, var_y_plot, variaveis_sociais, metricas):
    """
    Cria um expander com análise estatística detalhada da correlação entre dois aspectos sociais.
    
    Parâmetros:
    -----------
    df_preparado : DataFrame
        DataFrame com dados correlacionados
    var_x, var_y : str
        Nomes das variáveis originais para correlação
    var_x_plot, var_y_plot : str
        Nomes das variáveis de plotagem (podem incluir sufixo _NOME)
    variaveis_sociais : dict
        Dicionário com informações sobre as variáveis sociais
    metricas : dict
        Dicionário com métricas de correlação calculadas
    """
    with st.expander("Ver análise estatística detalhada"):
        # Título principal
        st.write(f"### Análise de associação entre {variaveis_sociais[var_x]['nome']} e {variaveis_sociais[var_y]['nome']}")
        
        # Bloco de métricas principais
        st.write(f"• **Força da associação:** {metricas['interpretacao']}")
        st.write(f"• **Coeficiente de contingência:** {metricas['coeficiente']:.4f}")
        
        # Significância estatística
        if metricas['significativo']:
            st.write("• **Significância estatística:** Há evidência de associação significativa entre estas variáveis")
        else:
            st.write("• **Significância estatística:** Não há evidência estatística suficiente para confirmar associação")
        
        # Análise detalhada
        st.write("#### Estatísticas adicionais:")
        st.write(f"• **Estatística qui-quadrado:** {metricas['qui_quadrado']:.2f}")
        st.write(f"• **Graus de liberdade:** {metricas['gl']}")
        st.write(f"• **Valor p:** {metricas['valor_p']:.5f}")
        st.write(f"• **V de Cramer:** {metricas['v_cramer']:.4f}")
        
        # Interpretação da força da associação
        st.write("#### Interpretação da força:")
        st.write(f"• **Interpretação contextualizada:** {metricas['contexto']}")
        
        # Análise por categorias
        st.write("#### Destaques por categoria:")
        
        # Obter categorias para análise
        categorias_x = df_preparado[var_x_plot].unique()
        categorias_y = df_preparado[var_y_plot].unique()
        
        # Tabela cruzada com contagem
        tabela_cruzada = pd.crosstab(df_preparado[var_x_plot], df_preparado[var_y_plot], normalize='index')*100
        
        # Destacar combinações mais notáveis
        max_valores = {}
        for cat_x in categorias_x:
            # Encontrar a categoria_y com maior associação
            if cat_x in tabela_cruzada.index:
                max_cat_y = tabela_cruzada.loc[cat_x].idxmax()
                max_valor = tabela_cruzada.loc[cat_x, max_cat_y]
                max_valores[cat_x] = (max_cat_y, max_valor)
        
        # Mostrar as 3 associações mais fortes
        sorted_cats = sorted(max_valores.items(), key=lambda x: x[1][1], reverse=True)[:3]
        
        for cat_x, (cat_y, valor) in sorted_cats:
            st.write(f"• **{cat_x}**: {valor:.1f}% estão na categoria **{cat_y}** de {variaveis_sociais[var_y]['nome']}")
        
        # Tabela completa
        st.write("#### Tabela de contingência (percentuais por linha):")
        st.dataframe(tabela_cruzada.round(1))


def criar_expander_dados_distribuicao(contagem_aspecto, estatisticas, aspecto_social, variaveis_sociais):
    """
    Cria um expander com dados detalhados sobre a distribuição de um aspecto social.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com contagem de candidatos por categoria
    estatisticas : dict
        Dicionário com estatísticas calculadas
    aspecto_social : str
        Nome do aspecto social analisado
    variaveis_sociais : dict
        Dicionário com informações sobre variáveis sociais
    """
    with st.expander("Ver dados detalhados"):
        # Título principal
        st.write("### Estatísticas")
        
        # Estatísticas gerais
        st.write(f"**Total de candidatos:** {estatisticas['total']:,}")
        
        # Categoria mais frequente
        st.write(f"**Categoria mais frequente:** {estatisticas['categoria_mais_frequente']['Categoria']} " + 
                 f"({estatisticas['categoria_mais_frequente']['Quantidade']:,} candidatos - " + 
                 f"{estatisticas['categoria_mais_frequente']['Percentual']:.1f}%)")
        
        # Categoria menos frequente
        st.write(f"**Categoria menos frequente:** {estatisticas['categoria_menos_frequente']['Categoria']} " + 
                 f"({estatisticas['categoria_menos_frequente']['Quantidade']:,} candidatos - " + 
                 f"{estatisticas['categoria_menos_frequente']['Percentual']:.1f}%)")
        
        # Número de categorias
        st.write(f"**Número de categorias:** {estatisticas['num_categorias']}")
        
        # Índice de concentração
        st.write(f"**Índice de concentração:** {estatisticas['indice_concentracao']:.4f}")
        st.write("*Valores próximos a 1 indicam distribuição mais desigual entre as categorias*")
        
        # Análise adicional da distribuição
        st.write("### Análise de distribuição")
        
        # Análise de equidade
        razao_max_min = (estatisticas['categoria_mais_frequente']['Quantidade'] / 
                          estatisticas['categoria_menos_frequente']['Quantidade'])
        
        st.write(f"**Razão entre maior e menor categoria:** {razao_max_min:.1f}x")
        
        if razao_max_min > 10:
            equidade = "Distribuição altamente desigual, com forte predominância de uma categoria"
        elif razao_max_min > 5:
            equidade = "Distribuição moderadamente desigual"
        elif razao_max_min > 2:
            equidade = "Distribuição com desigualdade moderada"
        else:
            equidade = "Distribuição relativamente equilibrada entre as categorias"
        
        st.write(f"**Avaliação de equidade:** {equidade}")
        
        # Percentual acumulado
        if len(contagem_aspecto) > 1:
            contagem_sorted = contagem_aspecto.sort_values('Quantidade', ascending=False).copy()
            contagem_sorted['Percentual Acumulado'] = contagem_sorted['Percentual'].cumsum()
            
            # Encontrar concentração em 50% e 80%
            percentual_50 = next((i+1 for i, val in enumerate(contagem_sorted['Percentual Acumulado']) 
                                if val >= 50), len(contagem_sorted))
            percentual_80 = next((i+1 for i, val in enumerate(contagem_sorted['Percentual Acumulado']) 
                                if val >= 80), len(contagem_sorted))
            
            # Análise de concentração
            st.write(f"**Concentração de candidatos:**")
            st.write(f"• {percentual_50} de {len(contagem_sorted)} categorias representam 50% dos candidatos")
            st.write(f"• {percentual_80} de {len(contagem_sorted)} categorias representam 80% dos candidatos")
        
        # Opção para exibir tabela completa
        if st.checkbox("Mostrar tabela completa", key="show_full_table"):
            st.write("### Tabela completa")
            st.dataframe(contagem_aspecto)


def criar_expander_analise_regional(df_por_estado, aspecto_social, categoria_selecionada, analise, variaveis_sociais):
    """
    Cria um expander com análise regional detalhada de aspectos sociais por estado.
    
    Parâmetros:
    -----------
    df_por_estado : DataFrame
        DataFrame com dados por estado
    aspecto_social : str
        Nome do aspecto social analisado
    categoria_selecionada : str
        Categoria selecionada para análise
    analise : dict
        Dicionário com métricas da análise regional
    variaveis_sociais : dict
        Dicionário com informações sobre variáveis sociais
    """
    with st.expander("Ver análise regional detalhada"):
        # Título da análise
        st.write(f"### Análise regional de {categoria_selecionada}")
        
        # Métricas gerais
        st.write(f"• **Percentual médio:** {analise['percentual_medio']:.2f}%")
        st.write(f"• **Desvio padrão:** {analise['desvio_padrao']:.2f} pontos percentuais")
        st.write(f"• **Coeficiente de variação:** {analise['coef_variacao']:.2f}%")
        st.write(f"• **Maior percentual:** {analise['maior_percentual']['Estado']} ({analise['maior_percentual']['Percentual']:.2f}%)")
        st.write(f"• **Menor percentual:** {analise['menor_percentual']['Estado']} ({analise['menor_percentual']['Percentual']:.2f}%)")
        st.write(f"• **Variabilidade regional:** {analise['variabilidade']}")
        
        # Análise por região geográfica
        st.write("#### Análise por região geográfica:")
        
        # Adicionar informação regional ao DataFrame
        df_regioes = adicionar_regiao_aos_estados(df_por_estado)
        
        # Filtrar apenas para a categoria selecionada
        df_categoria = df_regioes[df_regioes['Categoria'] == categoria_selecionada]
        
        # Calcular médias por região
        medias_por_regiao = df_categoria.groupby('Região')['Percentual'].mean().reset_index()
        medias_por_regiao = medias_por_regiao.sort_values('Percentual', ascending=False)
        
        # Exibir percentuais médios por região
        for i, row in medias_por_regiao.iterrows():
            st.write(f"• **{row['Região']}:** {row['Percentual']:.2f}% em média")
        
        # Análise de distribuição
        st.write("#### Distribuição em relação à média nacional:")
        
        # Calcular quantos estados estão acima e abaixo da média
        media_nacional = analise['percentual_medio']
        acima_da_media = df_categoria[df_categoria['Percentual'] > media_nacional]
        abaixo_da_media = df_categoria[df_categoria['Percentual'] < media_nacional]
        
        st.write(f"• **Estados acima da média nacional:** {len(acima_da_media)}")
        st.write(f"• **Estados abaixo da média nacional:** {len(abaixo_da_media)}")
        
        # Análise de extremos
        diferenca_extremos = analise['maior_percentual']['Percentual'] - analise['menor_percentual']['Percentual']
        st.write(f"• **Diferença entre extremos:** {diferenca_extremos:.2f} pontos percentuais")
        
        # Interpretação adicional
        st.write("#### Interpretação da variabilidade:")
        if analise['coef_variacao'] > 40:
            interpretacao = "Extremamente alta variabilidade, indicando profundas diferenças regionais"
        elif analise['coef_variacao'] > 25:
            interpretacao = "Alta variabilidade, mostrando importantes disparidades regionais"
        elif analise['coef_variacao'] > 15:
            interpretacao = "Variabilidade moderada, sugerindo diferenças regionais significativas"
        else:
            interpretacao = "Baixa variabilidade, indicando relativa homogeneidade regional"
        
        st.write(f"• {interpretacao}")
        
        # Opção para ver ranking completo
        if st.checkbox("Ver ranking completo de estados", key="ver_ranking_categoria_estado"):
            ranking = df_categoria.sort_values('Percentual', ascending=False)[['Estado', 'Percentual']]
            st.dataframe(ranking, column_config={"Percentual": st.column_config.NumberColumn(format="%.2f%%")})


def criar_expander_dados_completos_estado(df_por_estado):
    """
    Cria um expander com dados completos por estado para todas as categorias.
    
    Parâmetros:
    -----------
    df_por_estado : DataFrame
        DataFrame com dados por estado e categoria
    """
    with st.expander("Ver dados completos por estado"):
        # Criar tabela pivot com estados nas linhas e categorias nas colunas
        pivot_df = df_por_estado.pivot(index='Estado', columns='Categoria', values='Percentual').reset_index()
        
        # Configurar formatação para percentuais
        column_config = {"Estado": st.column_config.TextColumn("Estado")}
        for col in pivot_df.columns:
            if col != "Estado":
                column_config[col] = st.column_config.NumberColumn(col, format="%.2f%%")
        
        # Exibir dataframe com formatação
        st.dataframe(pivot_df, column_config=column_config, hide_index=True)


# Funções auxiliares

def adicionar_regiao_aos_estados(df):
    """
    Adiciona a informação de região para cada estado.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com coluna 'Estado'
        
    Retorna:
    --------
    DataFrame
        DataFrame com coluna 'Região' adicionada
    """
    # Mapeamento de estados para regiões
    regioes = {
        'Norte': ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO'],
        'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
        'Centro-Oeste': ['DF', 'GO', 'MS', 'MT'],
        'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
        'Sul': ['PR', 'RS', 'SC']
    }
    
    # Criar mapeamento invertido (de estado para região)
    estado_para_regiao = {}
    for regiao, estados in regioes.items():
        for estado in estados:
            estado_para_regiao[estado] = regiao
    
    # Copiar o DataFrame para não modificar o original
    df_com_regiao = df.copy()
    
    # Adicionar coluna de região
    df_com_regiao['Região'] = df_com_regiao['Estado'].map(estado_para_regiao)
    
    return df_com_regiao