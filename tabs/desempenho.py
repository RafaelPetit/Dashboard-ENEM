import streamlit as st
import pandas as pd
import plotly.express as px

def calcular_seguro(serie):
    """Calcula a média de uma série de forma segura, evitando erros com NaN"""
    return serie.mean() if not pd.isna(serie.mean()) else 0

def render_desempenho(microdados, microdados_estados, estados_selecionados, 
                     colunas_notas, competencia_mapping, race_mapping, 
                     variaveis_categoricas, desempenho_mapping):
    """
    Renderiza a aba de análise de desempenho no dashboard.
    """

    

    # Verificar se estados foram selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Mostrar informações sobre os estados selecionados
    if len(estados_selecionados) == 27:
        st.info(f"Analisando Aspectos Sociais para todo o Brasil") 
    else:
        st.info(f"Dados filtrados para: {', '.join(estados_selecionados)}")
    
    # Criar cópia do DataFrame para trabalhar
    microdados_full = microdados_estados.copy()
    microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].map(desempenho_mapping)
    # # ====================== SEÇÃO 1: DESEMPENHO POR RAÇA ======================
    # st.markdown("### Desempenho por Raça")
    
    # # Calcular desempenho (assumindo que já temos a coluna 'NU_DESEMPENHO' e 'CATEGORIA_DESEMPENHO')
    # # Se não existir, é necessário calcular como no código original
    
    # # Adicionar nome da raça
    # microdados_full['Raça'] = microdados_full['TP_COR_RACA'].map(race_mapping)
    
    # # Agrupar por raça e categoria de desempenho
    # raca_desempenho = microdados_full.groupby(['TP_COR_RACA', 'CATEGORIA_DESEMPENHO']).size().reset_index(name='count')
    # raca_total = microdados_full.groupby('TP_COR_RACA').size().reset_index(name='total')
    
    # # Calcular percentuais
    # raca_desempenho = raca_desempenho.merge(raca_total, on='TP_COR_RACA')
    # raca_desempenho['percentual'] = (raca_desempenho['count'] / raca_desempenho['total']) * 100
    # raca_desempenho['Raça'] = raca_desempenho['TP_COR_RACA'].map(race_mapping)
    
    # # Criar gráfico como no código original
    # fig_raca = px.bar(
    #     raca_desempenho, 
    #     x='Raça', 
    #     y='percentual', 
    #     color='CATEGORIA_DESEMPENHO',
    #     title='Distribuição de Desempenho por Raça', 
    #     labels={'percentual': 'Percentual (%)', 'Raça': 'Raça/Cor', 'CATEGORIA_DESEMPENHO': 'Desempenho'},
    #     category_orders={
    #     'CATEGORIA_DESEMPENHO': ['Desempenho Alto', 'Desempenho Médio', 'Desempenho Baixo']
    #     },
    #     color_discrete_map={'Desempenho Alto': '#99CC99', 
    #                         'Desempenho Médio': '#FFCC99', 
    #                         'Desempenho Baixo': '#FF9999'
    #     }
    # )
    # fig_raca.update_layout(
    #     height=400,
    #     bargap=0.2,
    #     barmode='group',
    #     plot_bgcolor='white',
    #     hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
    #     legend_title_text="Desempenho (clicável)",
    #     legend=dict(
    #         title=dict(text="Área de Conhecimento <br><sup>Clique para filtrar</sup>"),
    #         itemclick="toggleothers"
    #     ),
    #     xaxis=dict(tickangle=-45)
    # )

    # st.plotly_chart(fig_raca, use_container_width=True)

    # ====================== SEÇÃO 1: ANÁLISE COMPARATIVA POR VARIÁVEIS DEMOGRÁFICAS ======================
    st.markdown("### Análise Comparativa do Desempenho por  Variáveis Demográficas")
    
    # Seleção da variável
    variavel_selecionada = st.selectbox(
        "Selecione a variável para análise:",
        options=list(variaveis_categoricas.keys()),
        format_func=lambda x: variaveis_categoricas[x]["nome"]
    )

     # Preparação dos dados
    if variavel_selecionada in microdados_full.columns:
        # Criar uma coluna com os valores mapeados
        nome_coluna_mapeada = f"{variavel_selecionada}_NOME"
        
        # Garantir que todos os valores sejam strings para evitar problema de comparação
        mapeamento = variaveis_categoricas[variavel_selecionada]["mapeamento"]
        
        # Aplicar mapeamento tratando valores NaN e garantindo strings
        microdados_full[nome_coluna_mapeada] = microdados_full[variavel_selecionada].apply(
            lambda x: str(mapeamento.get(x, f"Outro ({x})")) if pd.notna(x) else "Não informado"
        )
        
        # Calcular médias por categoria
        resultados = []
        categorias_unicas = microdados_full[nome_coluna_mapeada].unique()
        
        for categoria in categorias_unicas:
            dados_categoria = microdados_full[microdados_full[nome_coluna_mapeada] == categoria]
            for competencia in colunas_notas:
                media_comp = calcular_seguro(dados_categoria[competencia])
                resultados.append({
                    'Categoria': categoria,
                    'Competência': competencia_mapping[competencia],
                    'Média': round(media_comp, 2)
                })
        
        # Criar DataFrame para visualização
        df_resultados = pd.DataFrame(resultados)
        
        # Determinar a ordem das categorias corretamente
        ordem_categorias = variaveis_categoricas[variavel_selecionada].get('ordem')
        if not ordem_categorias:
            # Se não há ordem específica definida, usar ordem alfabética de strings
            ordem_categorias = sorted(categorias_unicas)
        
        # Visualização do gráfico de barras
        fig = px.bar(
            df_resultados,
            x='Categoria',
            y='Média',
            color='Competência',
            title=f"Desempenho por {variaveis_categoricas[variavel_selecionada]['nome']}",
            labels={
                'Categoria': variaveis_categoricas[variavel_selecionada]['nome'],
                'Média': 'Nota Média',
                'Competência': 'Área de Conhecimento'
            },
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Bold,
            category_orders={
                'Categoria': ordem_categorias,
                'Competência': list(competencia_mapping.values())
            }
        )
        
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            plot_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(orientation="h", 
                        yanchor="bottom", 
                        y=1.02, xanchor="right", 
                        x=1, 
                        title=dict(text="Área de Conhecimento <br><sup>Clique para filtrar</sup>"),
                        itemclick="toggleothers")
                    )
        
        st.plotly_chart(fig, use_container_width=True)

        explicacao_comparativo = f"""Este gráfico de barras apresenta a análise comparativa do desempenho dos estudantes agrupados por {variaveis_categoricas[variavel_selecionada]['nome']}. 

As barras mostram a média aritmética das notas obtidas em cada competência para cada grupo demográfico. Esta visualização permite identificar possíveis disparidades de desempenho entre diferentes grupos sociais.
"""

        st.info(explicacao_comparativo)


    #     # Dados detalhados
    #     with st.expander("Ver dados da análise"):
    #         st.dataframe(
    #             df_resultados.pivot(index='Categoria', columns='Competência', values='Média').reset_index(),
    #             hide_index=True
    #         )
    # else:
    #     st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} não está disponível no conjunto de dados.")

    

    # ====================== SEÇÃO 2: RELAÇÃO ENTRE COMPETÊNCIAS (SCATTER PLOT) ======================
    st.markdown("### Relação entre Competências")
    col1, col2 = st.columns(2)
    
    # Controles de seleção
    with col1:
        eixo_x = st.selectbox("Eixo X:", options=colunas_notas, format_func=lambda x: competencia_mapping[x], placeholder="Selecione uma competência")
    with col2:
        eixo_y = st.selectbox("Eixo Y:", options=colunas_notas, format_func=lambda x: competencia_mapping[x], placeholder="Selecione uma competência")

    # Filtros adicionais
    with col1:
        sexo = st.selectbox("Sexo:", options=["Todos", "M", "F"])
        # Adição da opção para excluir notas zero - marcado por padrão
        excluir_notas_zero = st.checkbox("Desconsiderar notas zero", value=True)
    with col2:
        tipo_escola = st.selectbox("Tipo de Escola:", options=["Todos", "Federal", "Estadual", "Municipal", "Privada"])

    # Preparação dos dados filtrados - aplicar primeiro os filtros demográficos
    dados_filtrados = microdados_estados.copy()
    if sexo != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['TP_SEXO'] == sexo]
    if tipo_escola != "Todos":
        tipo_map = {"Federal": 1, "Estadual": 2, "Municipal": 3, "Privada": 4}
        dados_filtrados = dados_filtrados[dados_filtrados['TP_DEPENDENCIA_ADM_ESC'] == tipo_map[tipo_escola]]
    
    # Guardar o total após filtros demográficos para comparação posterior
    total_apos_filtros_demograficos = len(dados_filtrados)
    
    # Aplicar filtro de notas zero separadamente
    if excluir_notas_zero:
        dados_filtrados = dados_filtrados[(dados_filtrados[eixo_x] > 0) & (dados_filtrados[eixo_y] > 0)]
        
        # Calcular quantos registros foram removidos APENAS pelo filtro de notas zero
        registros_removidos_por_nota_zero = total_apos_filtros_demograficos - len(dados_filtrados)
        if registros_removidos_por_nota_zero > 0:
            st.info(f"Foram desconsiderados {registros_removidos_por_nota_zero} registros com nota zero.")

    # Aplicar mapeamento para raça/cor
    dados_filtrados['RACA_COR'] = dados_filtrados['TP_COR_RACA'].map(race_mapping)

    # Visualização do gráfico de dispersão
    fig = px.scatter(
        dados_filtrados, 
        x=eixo_x, 
        y=eixo_y,
        title=f"Relação entre {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}",
        labels={
            eixo_x: competencia_mapping[eixo_x], 
            eixo_y: competencia_mapping[eixo_y],
            'RACA_COR': 'COR/RAÇA'
        },
        opacity=0.5,
        color="RACA_COR",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_layout(
        legend_title_text="COR/RAÇA (clicável)",
        legend=dict(
            title=dict(text="COR/RAÇA<br><sup>Clique para filtrar</sup>"),
            itemclick="toggleothers"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

    explicacao = f"""Este gráfico de dispersão mostra a relação entre as notas de {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}. Cada ponto representa um estudante, com sua posição indicando a pontuação obtida em cada uma das competências. As cores representam diferentes categorias de raça/cor, permitindo identificar padrões de desempenho entre grupos demográficos."""
    
    st.info(explicacao)