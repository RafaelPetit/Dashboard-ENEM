import streamlit as st
import pandas as pd
import numpy as np

def criar_expander_analise_comparativa(df_resultados, variavel_selecionada, variaveis_categoricas, competencia_mapping, config_filtros):
    """
    Cria um expander com análise detalhada dos dados comparativos por variável demográfica.
    
    Parâmetros:
    -----------
    df_resultados : DataFrame
        DataFrame com os dados de médias por categoria e competência
    variavel_selecionada : str
        Nome da variável demográfica selecionada
    variaveis_categoricas : dict
        Dicionário com informações sobre as variáveis categóricas
    competencia_mapping : dict
        Dicionário mapeando códigos de competência para nomes legíveis
    config_filtros : dict
        Configurações de filtros selecionadas pelo usuário
    """
    with st.expander("Ver análise detalhada por categoria", ):
        # Variável nome para exibição
        variavel_nome = variaveis_categoricas[variavel_selecionada]['nome']
        
        # Calcular diferenças e estatísticas importantes
        analise_geral = calcular_estatisticas_comparativas(df_resultados, variavel_selecionada)
        
        # Definir qual competência analisar em detalhe
        if config_filtros['mostrar_apenas_competencia']:
            competencias_analise = [config_filtros['competencia_filtro']]
            titulo_comp = f"em {config_filtros['competencia_filtro']}"
        else:
            competencias_analise = df_resultados['Competência'].unique().tolist()
            titulo_comp = "nas diversas competências"
        
        # Título principal da análise
        st.write(f"### Análise do desempenho por {variavel_nome} {titulo_comp}")
        
        # Desempenho comparativo entre categorias
        st.write("#### Disparidades entre categorias:")
        
        for competencia in competencias_analise:
            df_comp = df_resultados[df_resultados['Competência'] == competencia].copy()
            
            # Calcular estatísticas para esta competência
            media_geral = df_comp['Média'].mean()
            categoria_max = df_comp.loc[df_comp['Média'].idxmax()]
            categoria_min = df_comp.loc[df_comp['Média'].idxmin()]
            diferenca_max_min = categoria_max['Média'] - categoria_min['Média']
            
            # Exibir estatísticas da competência
            if len(competencias_analise) > 1:
                st.write(f"**{competencia}:**")
            
            st.write(f"• **Maior média:** {categoria_max['Categoria']} ({categoria_max['Média']:.1f} pontos)")
            st.write(f"• **Menor média:** {categoria_min['Categoria']} ({categoria_min['Média']:.1f} pontos)")
            st.write(f"• **Diferença:** {diferenca_max_min:.1f} pontos ({(diferenca_max_min/categoria_min['Média']*100):.1f}% superior)")
            
            if len(competencias_analise) > 1:
                st.write("---")
        
        # Análise global das disparidades
        st.write("#### Análise global:")
        st.write(f"• **Maior disparidade:** {analise_geral['maior_disparidade']['competencia']} ({analise_geral['maior_disparidade']['diferenca']:.1f} pontos)")
        st.write(f"• **Menor disparidade:** {analise_geral['menor_disparidade']['competencia']} ({analise_geral['menor_disparidade']['diferenca']:.1f} pontos)")
        
        # Desvio padrão entre categorias
        st.write("#### Variabilidade entre categorias:")
        for competencia in competencias_analise:
            df_comp = df_resultados[df_resultados['Competência'] == competencia].copy()
            desvio = df_comp['Média'].std()
            media = df_comp['Média'].mean()
            coef_var = (desvio / media * 100) if media > 0 else 0
            
            if len(competencias_analise) > 1:
                st.write(f"**{competencia}:**")
            
            st.write(f"• **Desvio padrão:** {desvio:.2f} pontos")
            st.write(f"• **Coeficiente de variação:** {coef_var:.2f}%")
            
            # Interpretação da variabilidade
            if coef_var > 15:
                interpretacao = "Alta variabilidade, indicando forte influência da variável demográfica"
            elif coef_var > 8:
                interpretacao = "Variabilidade moderada, sugerindo influência significativa da variável demográfica"
            else:
                interpretacao = "Baixa variabilidade, indicando influência limitada da variável demográfica"
            
            st.write(f"• **Interpretação:** {interpretacao}")
            
            if len(competencias_analise) > 1:
                st.write("---")
        

def criar_expander_relacao_competencias(dados_filtrados, config_filtros, competencia_mapping, correlacao, interpretacao):
    """
    Cria um expander com análise detalhada da relação entre duas competências.
    
    Parâmetros:
    -----------
    dados_filtrados : DataFrame
        DataFrame com os dados filtrados para análise
    config_filtros : dict
        Configurações de filtros selecionadas pelo usuário
    competencia_mapping : dict
        Dicionário mapeando códigos de competência para nomes legíveis
    correlacao : float
        Coeficiente de correlação calculado
    interpretacao : str
        Interpretação do coeficiente de correlação
    """
    with st.expander("Ver análise detalhada da correlação", ):
        eixo_x = config_filtros['eixo_x']
        eixo_y = config_filtros['eixo_y']
        eixo_x_nome = competencia_mapping[eixo_x]
        eixo_y_nome = competencia_mapping[eixo_y]
        
        # Título da análise
        st.write(f"### Análise da relação entre {eixo_x_nome} e {eixo_y_nome}")
        
        # Estatísticas de correlação
        st.write("#### Correlação:")
        st.write(f"• **Coeficiente de Pearson:** {correlacao:.4f}")
        st.write(f"• **Interpretação:** {interpretacao}")
        st.write(f"• **Coeficiente determinação (r²):** {correlacao**2:.4f} ({(correlacao**2*100):.1f}% da variação pode ser explicada)")
        
        # Interpretação contextualizada
        st.write("#### Significado educacional:")
        if correlacao > 0.7:
            contexto = f"Existe uma forte associação entre as competências, sugerindo que habilidades e conhecimentos semelhantes são necessários para ambas as áreas. Estudantes com bom desempenho em {eixo_x_nome} muito provavelmente também terão bom desempenho em {eixo_y_nome}."
        elif correlacao > 0.4:
            contexto = f"Há uma associação moderada entre as competências, indicando que algumas habilidades se sobrepõem, mas cada área também exige conhecimentos específicos. Muitos estudantes com bom desempenho em {eixo_x_nome} também terão bom desempenho em {eixo_y_nome}, mas há exceções significativas."
        elif correlacao > 0.2:
            contexto = f"A associação fraca sugere que as competências compartilham algumas habilidades básicas, mas são amplamente distintas em seus requisitos. O desempenho em {eixo_x_nome} é apenas um preditor limitado do desempenho em {eixo_y_nome}."
        else:
            contexto = f"Há pouca ou nenhuma associação linear entre as competências, indicando que são áreas de conhecimento e habilidades distintas. O desempenho em {eixo_x_nome} não permite prever o desempenho em {eixo_y_nome}."
        
        st.write(contexto)
        
        # Estatísticas comparativas por competência
        col1, col2 = st.columns(2)
        with col1:
            # Estatísticas para eixo X
            df_stats_x = calcular_estatisticas_competencia(dados_filtrados, eixo_x)
            st.write(f"#### Estatísticas: {eixo_x_nome}")
            st.write(f"• **Média:** {df_stats_x['média']:.2f} pontos")
            st.write(f"• **Mediana:** {df_stats_x['mediana']:.2f} pontos")
            st.write(f"• **Desvio padrão:** {df_stats_x['desvio_padrão']:.2f}")
            st.write(f"• **Coef. variação:** {df_stats_x['coef_variação']:.2f}%")
            st.write(f"• **Mínimo:** {df_stats_x['mínimo']:.2f} pontos")
            st.write(f"• **Máximo:** {df_stats_x['máximo']:.2f} pontos")
            
        with col2:
            # Estatísticas para eixo Y
            df_stats_y = calcular_estatisticas_competencia(dados_filtrados, eixo_y)
            st.write(f"#### Estatísticas: {eixo_y_nome}")
            st.write(f"• **Média:** {df_stats_y['média']:.2f} pontos")
            st.write(f"• **Mediana:** {df_stats_y['mediana']:.2f} pontos")
            st.write(f"• **Desvio padrão:** {df_stats_y['desvio_padrão']:.2f}")
            st.write(f"• **Coef. variação:** {df_stats_y['coef_variação']:.2f}%")
            st.write(f"• **Mínimo:** {df_stats_y['mínimo']:.2f} pontos")
            st.write(f"• **Máximo:** {df_stats_y['máximo']:.2f} pontos")
        
        # Análise comparativa entre competências
        st.write("#### Comparação entre as competências:")
        media_x = df_stats_x['média']
        media_y = df_stats_y['média']
        diff_percent = ((media_x - media_y) / media_y * 100) if media_y != 0 else 0
        
        if abs(diff_percent) < 1:
            comparacao = f"As médias de desempenho são praticamente iguais (diferença de apenas {abs(diff_percent):.2f}%)."
        else:
            comp_maior = eixo_x_nome if media_x > media_y else eixo_y_nome
            comp_menor = eixo_y_nome if media_x > media_y else eixo_x_nome
            diff_abs = abs(media_x - media_y)
            diff_perc = abs(diff_percent)
            comparacao = f"A média em {comp_maior} é {diff_perc:.2f}% maior que em {comp_menor} (diferença de {diff_abs:.2f} pontos)."
        
        st.write(f"• {comparacao}")
        
        # Variabilidade comparativa
        var_x = df_stats_x['coef_variação']
        var_y = df_stats_y['coef_variação']
        
        if abs(var_x - var_y) < 5:
            var_comp = "Ambas as competências apresentam níveis similares de variabilidade nos resultados."
        else:
            comp_mais_var = eixo_x_nome if var_x > var_y else eixo_y_nome
            comp_menos_var = eixo_y_nome if var_x > var_y else eixo_x_nome
            var_comp = f"{comp_mais_var} apresenta maior variabilidade nos resultados que {comp_menos_var}, indicando maior heterogeneidade no desempenho dos estudantes."
        
        st.write(f"• {var_comp}")
        
        # Informação sobre os filtros aplicados
        st.write("#### Filtros aplicados na análise:")
        filtros_texto = []
        if config_filtros['sexo'] != "Todos":
            filtros_texto.append(f"Sexo: {config_filtros['sexo']}")
        if config_filtros['tipo_escola'] != "Todas":
            filtros_texto.append(f"Tipo de escola: {config_filtros['tipo_escola']}")
        if config_filtros['excluir_notas_zero']:
            filtros_texto.append("Excluindo notas zero")
        
        if filtros_texto:
            for filtro in filtros_texto:
                st.write(f"• {filtro}")
        else:
            st.write("• Sem filtros ativos (todos os dados)")


def criar_expander_desempenho_estados(df_grafico, area_analise, analise):
    """
    Cria um expander com análise regional detalhada do desempenho por estado.
    
    Parâmetros:
    -----------
    df_grafico : DataFrame
        DataFrame com os dados de desempenho por estado
    area_analise : str
        Área de conhecimento selecionada para análise
    analise : dict
        Dicionário com resultados da análise de desempenho por estado
    """
    with st.expander("Ver análise regional detalhada", ):
        # Calcular métricas adicionais
        media_geral = analise['media_geral']
        desvio_padrao = analise['desvio_padrao']
        coef_variacao = (desvio_padrao / media_geral * 100) if media_geral > 0 else 0
        
        # Determinar nível de variabilidade
        if coef_variacao > 15:
            variabilidade_texto = "alta"
            variabilidade_explicacao = "indicando grandes disparidades regionais no desempenho educacional"
        elif coef_variacao > 8:
            variabilidade_texto = "moderada"
            variabilidade_explicacao = "sugerindo diferenças regionais importantes, mas não extremas"
        else:
            variabilidade_texto = "baixa"
            variabilidade_explicacao = "indicando relativa homogeneidade no desempenho entre os sistemas educacionais regionais"
        
        # Formatação do título
        titulo_analise = f"Análise regional de desempenho em {area_analise}"
        if area_analise == "Média Geral":
            titulo_analise = "Análise regional do desempenho geral"
            if not area_analise:
                st.info("Selecione uma área específica no filtro de ordenação para ver análise detalhada por área.")
        
        st.write(f"### {titulo_analise}")
        
        # Desempenho comparativo entre estados
        st.write("#### Comparativo entre estados:")
        st.write(f"• **Melhor desempenho:** {analise['melhor_estado']['Estado']} ({analise['melhor_estado']['Média']:.1f} pontos)")
        st.write(f"• **Pior desempenho:** {analise['pior_estado']['Estado']} ({analise['pior_estado']['Média']:.1f} pontos)")
        st.write(f"• **Diferença entre extremos:** {analise['melhor_estado']['Média'] - analise['pior_estado']['Média']:.1f} pontos")
        
        # Estatísticas descritivas
        st.write("#### Estatísticas gerais:")
        st.write(f"• **Média nacional:** {analise['media_geral']:.1f} pontos")
        st.write(f"• **Desvio padrão:** {desvio_padrao:.2f} pontos")
        st.write(f"• **Coeficiente de variação:** {coef_variacao:.2f}%")
        st.write(f"• **Variabilidade:** {variabilidade_texto} ({variabilidade_explicacao})")
        
        # Estados acima/abaixo da média
        acima_da_media = df_grafico[(df_grafico['Área'] == area_analise) & (df_grafico['Média'] > media_geral)]
        abaixo_da_media = df_grafico[(df_grafico['Área'] == area_analise) & (df_grafico['Média'] < media_geral)]
        
        # Contagem de estados acima/abaixo da média
        st.write("#### Distribuição em relação à média nacional:")
        st.write(f"• **Estados acima da média:** {len(acima_da_media)} estados")
        st.write(f"• **Estados abaixo da média:** {len(abaixo_da_media)} estados")
        
        # Análise regional
        st.write("#### Análise por região:")
        df_regioes = adicionar_regiao_aos_estados(df_grafico)
        medias_por_regiao = df_regioes[df_regioes['Área'] == area_analise].groupby('Região')['Média'].mean().reset_index()
        medias_por_regiao = medias_por_regiao.sort_values('Média', ascending=False)
        
        for i, row in medias_por_regiao.iterrows():
            st.write(f"• **{row['Região']}:** {row['Média']:.1f} pontos")
        
        # Opção para ver lista completa ordenada
        if st.checkbox("Ver ranking completo de estados", key="ver_ranking_completo"):
            ranking = df_grafico[df_grafico['Área'] == area_analise].sort_values('Média', ascending=False)
            ranking = ranking[['Estado', 'Média']].reset_index(drop=True)
            ranking.index = ranking.index + 1  # Iniciar índice em 1
            st.dataframe(ranking, column_config={"Média": st.column_config.NumberColumn("Média", format="%.1f")})


# Funções auxiliares para cálculos

def calcular_estatisticas_comparativas(df_resultados, variavel_selecionada):
    """
    Calcula estatísticas para análise comparativa entre categorias.
    
    Parâmetros:
    -----------
    df_resultados : DataFrame
        DataFrame com os resultados
    variavel_selecionada : str
        Nome da variável categórica
        
    Retorna:
    --------
    dict
        Dicionário com estatísticas calculadas
    """
    # Inicializar dicionário de resultados
    resultados = {
        'maior_disparidade': {'competencia': None, 'diferenca': 0},
        'menor_disparidade': {'competencia': None, 'diferenca': float('inf')},
    }
    
    # Calcular para cada competência
    for competencia in df_resultados['Competência'].unique():
        df_comp = df_resultados[df_resultados['Competência'] == competencia]
        max_valor = df_comp['Média'].max()
        min_valor = df_comp['Média'].min()
        diferenca = max_valor - min_valor
        
        # Atualizar maior disparidade
        if diferenca > resultados['maior_disparidade']['diferenca']:
            resultados['maior_disparidade'] = {
                'competencia': competencia,
                'diferenca': diferenca
            }
        
        # Atualizar menor disparidade
        if diferenca < resultados['menor_disparidade']['diferenca']:
            resultados['menor_disparidade'] = {
                'competencia': competencia,
                'diferenca': diferenca
            }
    
    return resultados


def calcular_estatisticas_competencia(dados, coluna):
    """
    Calcula estatísticas descritivas para uma competência.
    
    Parâmetros:
    -----------
    dados : DataFrame
        DataFrame com os dados
    coluna : str
        Nome da coluna com as notas
        
    Retorna:
    --------
    dict
        Dicionário com estatísticas calculadas
    """
    media = dados[coluna].mean()
    desvio = dados[coluna].std()
    
    return {
        'média': media,
        'mediana': dados[coluna].median(),
        'desvio_padrão': desvio,
        'coef_variação': (desvio / media * 100) if media > 0 else 0,
        'mínimo': dados[coluna].min(),
        'máximo': dados[coluna].max(),
        'q25': dados[coluna].quantile(0.25),
        'q75': dados[coluna].quantile(0.75)
    }


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