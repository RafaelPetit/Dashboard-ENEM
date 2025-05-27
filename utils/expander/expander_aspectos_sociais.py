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


def criar_expander_analise_regional(df_dados, aspecto_social, categoria_selecionada, analise, variaveis_sociais, tipo_localidade="estado"):
    """
    Cria um expander com análise detalhada da distribuição regional de uma categoria específica.
    
    Parâmetros:
    -----------
    df_dados : DataFrame
        DataFrame com os dados da análise
    aspecto_social : str
        Nome do aspecto social analisado
    categoria_selecionada : str
        Nome da categoria selecionada para análise
    analise : dict
        Dicionário com os resultados da análise estatística
    variaveis_sociais : dict
        Dicionário com mapeamentos e configurações das variáveis sociais
    tipo_localidade : str, default="estado"
        Tipo de localidade (estado ou região)
    """
    with st.expander(f"Ver análise detalhada da categoria '{categoria_selecionada}'"):
        st.write(f"### Análise da categoria '{categoria_selecionada}' por {tipo_localidade}")
        
        # Filtrar dados para a categoria selecionada
        df_categoria = df_dados[df_dados['Categoria'] == categoria_selecionada]
        
        # Exibir estatísticas
        st.write("#### Estatísticas gerais")
        media = analise['media']
        mediana = analise['mediana']
        desvio = analise['desvio']
        maximo = analise['maximo']
        minimo = analise['minimo']
        amplitude = analise['amplitude']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Média nacional", f"{media:.1f}%")
            st.metric("Desvio padrão", f"{desvio:.1f}%")
            st.metric("Amplitude", f"{amplitude:.1f}%")
        
        with col2:
            st.metric("Mediana", f"{mediana:.1f}%")
            st.metric("Valor máximo", f"{maximo:.1f}%")
            st.metric("Valor mínimo", f"{minimo:.1f}%")
        
        # Exibir análise de distribuição
        st.write(f"#### Variação por {tipo_localidade}")
        
        if desvio > 10:
            nivel_variacao = "**Alta variação**"
            descricao = f"Existe uma diferença significativa na distribuição de '{categoria_selecionada}' entre os {tipo_localidade}s."
        elif desvio > 5:
            nivel_variacao = "**Variação moderada**" 
            descricao = f"Há alguma diferença na distribuição de '{categoria_selecionada}' entre os {tipo_localidade}s."
        else:
            nivel_variacao = "**Baixa variação**"
            descricao = f"A distribuição de '{categoria_selecionada}' é relativamente uniforme entre os {tipo_localidade}s."
        
        st.write(f"**Nível de variação:** {nivel_variacao}")
        st.write(descricao)
        
        # Criação da tabela ordenada
        st.write(f"#### Ranking de {tipo_localidade}s")
        df_ranking = df_categoria.sort_values('Percentual', ascending=False)[['Estado', 'Percentual']]
        
        # Adicionar classificação relativa à média
        df_ranking['Comparação à média'] = df_ranking['Percentual'].apply(
            lambda x: "Acima da média" if x > media else ("Na média" if abs(x - media) < 1 else "Abaixo da média")
        )
        
        # Renomear colunas para melhor legibilidade
        df_ranking = df_ranking.rename(columns={
            'Estado': tipo_localidade.capitalize(),
            'Percentual': 'Percentual (%)'
        })
        
        # Adicionar índice a partir de 1
        df_ranking = df_ranking.reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        
        # Exibir o ranking
        st.dataframe(
            df_ranking,
            column_config={
                'Percentual (%)': st.column_config.NumberColumn(
                    'Percentual (%)',
                    format="%.1f%%"
                ),
                'Comparação à média': st.column_config.TextColumn(
                    'Comparação à média',
                    width="medium"
                )
            },
            hide_index=False
        )
        
        # Se for por estado, adicionar análise por região
        if tipo_localidade == "estado" and len(df_categoria) > 5:
            st.write("#### Análise por região")
            
            # Adicionar informação de região
            from utils.helpers.regiao_utils import obter_mapa_regioes
            mapa_regioes = obter_mapa_regioes()
            
            df_regioes = df_categoria.copy()
            df_regioes['Região'] = df_regioes['Estado'].map(mapa_regioes)
            
            # Agrupar por região
            df_por_regiao = df_regioes.groupby('Região')['Percentual'].mean().reset_index()
            df_por_regiao = df_por_regiao.sort_values('Percentual', ascending=False)
            
            # Gráfico de barras por região
            fig = px.bar(
                df_por_regiao,
                x='Região',
                y='Percentual',
                text_auto='.1f',
                title=f"Média de '{categoria_selecionada}' por região",
                labels={'Percentual': 'Percentual (%)', 'Região': 'Região'},
                color_discrete_sequence=['#3366CC']
            )
            
            fig.update_layout(
                yaxis=dict(ticksuffix='%'),
                plot_bgcolor='white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Análise textual da distribuição regional
            maior_regiao = df_por_regiao.iloc[0]['Região']
            menor_regiao = df_por_regiao.iloc[-1]['Região']
            
            st.write(f"**Maior concentração:** {maior_regiao} ({df_por_regiao.iloc[0]['Percentual']:.1f}%)")
            st.write(f"**Menor concentração:** {menor_regiao} ({df_por_regiao.iloc[-1]['Percentual']:.1f}%)")

def criar_expander_dados_completos_estado(df_dados, tipo_localidade="estado"):
    """
    Cria um expander com tabela completa de dados por estado/região.
    
    Parâmetros:
    -----------
    df_dados : DataFrame
        DataFrame com os dados para a tabela
    tipo_localidade : str, default="estado"
        Tipo de localidade (estado ou região)
    """
    with st.expander(f"Ver tabela completa de dados por {tipo_localidade}"):
        # Usar pivot_table em vez de pivot para lidar com valores duplicados
        df_pivot = df_dados.pivot_table(
            index='Estado', 
            columns='Categoria', 
            values='Percentual',
            aggfunc='mean'  # Calcula a média quando há valores duplicados
        ).reset_index()
        
        # Renomear o índice para o tipo de localidade
        df_pivot = df_pivot.rename(columns={'Estado': tipo_localidade.capitalize()})
        
        # Expandir colunas para formato adequado
        df_pivot = df_pivot.round(1)
        
        # Exibir tabela
        st.dataframe(
            df_pivot,
            column_config={col: st.column_config.NumberColumn(col, format="%.1f%%") 
                          for col in df_pivot.columns if col != tipo_localidade.capitalize()},
            height=400
        )
        
        # Opção para download
        csv = df_pivot.to_csv(index=False).encode('utf-8')
        st.download_button(
            f"Download dos dados por {tipo_localidade} (CSV)",
            csv,
            f"aspectos_sociais_por_{tipo_localidade}.csv",
            "text/csv",
            key=f'download_{tipo_localidade}_csv'
        )
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