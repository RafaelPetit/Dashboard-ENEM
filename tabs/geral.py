import streamlit as st
import plotly.express as px
import numpy as np
from utils.data_loader import calcular_seguro, prepare_data_for_line_chart

def render_geral(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """Renderiza a aba Geral do dashboard."""
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
        
    # Informar ao usuário quais estados estão sendo considerados
    if len(estados_selecionados) == 27:
        st.info(f"Analisando Dados Gerais para todo o Brasil") 
    else:
        st.info(f"Dados filtrados para: {', '.join(estados_selecionados)}")
    
    # Métricas Principais
    st.header("Métricas Principais")
    
    # Calcular médias por estado
    media_por_estado = []
    medias_estados = {}
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        medias_estado_atual = []       
        for col in colunas_notas:
            media = calcular_seguro(dados_estado[col])
            media_por_estado.append(media)
            medias_estado_atual.append(media)

         # Calcular média geral do estado (média de todas as competências)
        if medias_estado_atual:
            medias_estados[estado] = np.mean(medias_estado_atual)
    
    # Métricas gerais
    media_geral = np.mean(media_por_estado) if media_por_estado else 0.0
    maior_media = np.max(media_por_estado) if media_por_estado else 0.0
    
    # Encontrar o estado com a maior média
    estado_maior_media = max(medias_estados.items(), key=lambda x: x[1])[0] if medias_estados else "N/A"
    valor_maior_media_estado = medias_estados.get(estado_maior_media, 0.0)

    # Dados para gráfico de linhas
    df_grafico = prepare_data_for_line_chart(
        microdados_estados, estados_selecionados, colunas_notas, competencia_mapping
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Média Geral", f"{round(media_geral, 2)}")
    with col2:
        st.metric("Total de Candidatos", f"{microdados_estados.shape[0]:,}")
    with col3:
        st.metric("Maior Média", f"{round(maior_media, 2)}")
    with col4:
        st.metric("Estado com Maior Média", f"{estado_maior_media}")
    
    # Histograma e Linha
    st.subheader("Distribuição das Notas")
    area_conhecimento = st.selectbox(
        "Selecione a área de conhecimento:",
        options=colunas_notas,
        format_func=lambda x: competencia_mapping[x]
    )
    nome_area = competencia_mapping[area_conhecimento]
    
    media = calcular_seguro(microdados_estados[area_conhecimento])
    mediana = calcular_seguro(microdados_estados[area_conhecimento], 'mediana')
    min_valor = calcular_seguro(microdados_estados[area_conhecimento], 'min')
    max_valor = calcular_seguro(microdados_estados[area_conhecimento], 'max')
    
    # col1_hist, col2_hist = st.columns(2)
    # with col1_hist:
        # Gráfico de Histograma
    fig_hist = px.histogram(
        microdados_estados,
        x=area_conhecimento,
        nbins=30,
        histnorm='percent',
        title=f"Distribuição das notas - {nome_area}",
        labels={area_conhecimento: f"Nota ({nome_area})"},
        opacity=0.7,
        color_discrete_sequence=['#3366CC']
    )
    fig_hist.add_vline(x=media, line_dash="dash", line_color="red", 
                        annotation_text=f"Média: {media:.2f}")
    fig_hist.add_vline(x=mediana, line_dash="dash", line_color="green", 
                        annotation_text=f"Mediana: {mediana:.2f}")
    fig_hist.update_layout(
        height=400,
        bargap=0.1,
        xaxis_title=f"Nota ({nome_area})",
        yaxis_title="Porcentagem (%)",
        xaxis=dict(tickmode='auto', nticks=15, showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        showlegend=False
    )
    stats_text = f"""
    <b>Estatísticas:</b><br>
    Média: {media:.2f}<br>
    Mediana: {mediana:.2f}<br>
    Mínimo: {min_valor:.2f}<br>
    Máximo: {max_valor:.2f}
    """
    fig_hist.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=stats_text,
        showarrow=False,
        font=dict(size=12),
        align="left",
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # with col2_hist:
        # Gráfico de Linha
    if len(df_grafico) > 0:
        fig_linha = px.line(
            df_grafico,
            x='Estado',
            y='Média',
            color='Área',
            markers=True,
            title='Médias por Estado e Área de Conhecimento',
            labels={'Média': 'Nota Média', 'Estado': 'Estado', 'Área': 'Área de Conhecimento'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_linha.update_layout(
            height=400,
            xaxis_title="Estado",
            yaxis_title="Nota Média",
            legend_title="Área de Conhecimento",
            xaxis=dict(tickangle=-45),
            plot_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(
            title=dict(text="Área de Conhecimento<br><sup>Clique para filtrar</sup>"),
            itemclick="toggleothers"
        )
        )
        st.plotly_chart(fig_linha, use_container_width=True)

# # Dados Detalhados
#         with st.expander("Ver dados detalhados"):  
#             st.dataframe(
#                 microdados_estados,
#                 column_config={
#                     "SG_UF_PROVA": "Estado",
#                     "NU_NOTA_CN": "Ciências da Natureza",
#                     "NU_NOTA_CH": "Ciências Humanas",
#                     "NU_NOTA_LC": "Linguagens e Códigos",
#                     "NU_NOTA_MT": "Matemática",
#                     "NU_NOTA_REDACAO": "Redação"
#                 }, 
#                 hide_index=True
#             )
#             st.info(f"""
#                 A distribuição mostra a frequência das notas em {nome_area}.
#                 A média é {media:.2f} e a mediana {mediana:.2f}, o que indica que
#                 {'a distribuição tem um viés positivo' if media > mediana else 'a distribuição tem um viés negativo' if media < mediana else 'a distribuição é aproximadamente simétrica'}.
#             """)