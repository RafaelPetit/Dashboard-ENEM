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
    if len(estados_selecionados) <= 5:
        st.info(f"Dados de desempenho para: {', '.join(estados_selecionados)}")
    else:
        st.info(f"Analisando desempenho para {len(estados_selecionados)} estados selecionados")
    
    # Criar cópia do DataFrame para trabalhar
    microdados_full = microdados_estados.copy()
    microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].map(desempenho_mapping)
    # ====================== SEÇÃO 1: DESEMPENHO POR RAÇA ======================
    st.markdown("### Desempenho por Raça")
    
    # Calcular desempenho (assumindo que já temos a coluna 'NU_DESEMPENHO' e 'CATEGORIA_DESEMPENHO')
    # Se não existir, é necessário calcular como no código original
    
    # Adicionar nome da raça
    microdados_full['Raça'] = microdados_full['TP_COR_RACA'].map(race_mapping)
    
    # Agrupar por raça e categoria de desempenho
    raca_desempenho = microdados_full.groupby(['TP_COR_RACA', 'CATEGORIA_DESEMPENHO']).size().reset_index(name='count')
    raca_total = microdados_full.groupby('TP_COR_RACA').size().reset_index(name='total')
    
    # Calcular percentuais
    raca_desempenho = raca_desempenho.merge(raca_total, on='TP_COR_RACA')
    raca_desempenho['percentual'] = (raca_desempenho['count'] / raca_desempenho['total']) * 100
    raca_desempenho['Raça'] = raca_desempenho['TP_COR_RACA'].map(race_mapping)
    
    # Criar gráfico como no código original
    fig_raca = px.bar(
        raca_desempenho, 
        x='Raça', 
        y='percentual', 
        color='CATEGORIA_DESEMPENHO',
        title='Distribuição de Desempenho por Raça', 
        labels={'percentual': 'Percentual (%)', 'Raça': 'Raça/Cor', 'CATEGORIA_DESEMPENHO': 'Desempenho'},
        category_orders={
        'CATEGORIA_DESEMPENHO': ['Desempenho Alto', 'Desempenho Médio', 'Desempenho Baixo']
        },
        color_discrete_map={'Desempenho Alto': '#99CC99', 
                            'Desempenho Médio': '#FFCC99', 
                            'Desempenho Baixo': '#FF9999'
        }
    )
    fig_raca.update_layout(
        height=400,
        bargap=0.2,
        barmode='group',
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        xaxis=dict(tickangle=-45)
    )
    st.plotly_chart(fig_raca, use_container_width=True)

    # ====================== SEÇÃO 2: ANÁLISE COMPARATIVA POR VARIÁVEIS DEMOGRÁFICAS ======================
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
        microdados_full[nome_coluna_mapeada] = microdados_full[variavel_selecionada].map(
            variaveis_categoricas[variavel_selecionada]["mapeamento"]
        )
        
        # Calcular médias por categoria
        resultados = []
        for categoria in microdados_full[nome_coluna_mapeada].unique():
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
                'Categoria': variaveis_categoricas[variavel_selecionada].get('ordem', sorted(microdados_full[nome_coluna_mapeada].unique())),
                'Competência': list(competencia_mapping.values())
            }
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            plot_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Dados detalhados
        with st.expander("Ver dados da análise"):
            st.dataframe(
                df_resultados.pivot(index='Categoria', columns='Competência', values='Média').reset_index(),
                hide_index=True
            )
    else:
        st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} não está disponível no conjunto de dados.")

    # ====================== SEÇÃO 3: RELAÇÃO ENTRE COMPETÊNCIAS (SCATTER PLOT) ======================
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
    with col2:
        tipo_escola = st.selectbox("Tipo de Escola:", options=["Todos", "Federal", "Estadual", "Municipal", "Privada"])

    # Preparação dos dados filtrados
    dados_filtrados = microdados_estados.copy()
    if sexo != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['TP_SEXO'] == sexo]
    if tipo_escola != "Todos":
        tipo_map = {"Federal": 1, "Estadual": 2, "Municipal": 3, "Privada": 4}
        dados_filtrados = dados_filtrados[dados_filtrados['TP_DEPENDENCIA_ADM_ESC'] == tipo_map[tipo_escola]]

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
    
    st.plotly_chart(fig, use_container_width=True)