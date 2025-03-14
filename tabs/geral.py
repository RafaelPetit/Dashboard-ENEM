import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
from utils.data_loader import calcular_seguro, prepare_data_for_line_chart

def render_geral(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """Renderiza a aba Geral do dashboard com métricas e visualizações."""
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
        
    # Informar ao usuário quais estados estão sendo considerados
    mensagem = f"Analisando Dados Gerais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(estados_selecionados)}"
    st.info(mensagem)
    
    # Calcular e exibir métricas principais
    medias_estados = exibir_metricas_principais(microdados_estados, estados_selecionados, colunas_notas)
    
    # Exibir histograma de distribuição de notas
    exibir_histograma_notas(microdados_estados, colunas_notas, competencia_mapping)
    
    # Exibir gráfico de linha de médias por estado e área
    df_grafico = prepare_data_for_line_chart(
        microdados_estados, estados_selecionados, colunas_notas, competencia_mapping
    )
    if len(df_grafico) > 0:
        exibir_grafico_linha(df_grafico, estados_selecionados, medias_estados, 
                           microdados_estados, colunas_notas, competencia_mapping)


def exibir_metricas_principais(microdados_estados, estados_selecionados, colunas_notas):
    """Calcula e exibe métricas principais em cards."""
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
    
    # Encontrar o estado com a maior média
    estado_maior_media = "N/A"
    valor_maior_media_estado = 0.0
    if medias_estados:
        estado_maior_media, valor_maior_media_estado = max(medias_estados.items(), key=lambda x: x[1])
        
    # Exibir métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Média Geral", f"{round(media_geral, 2)}")
    with col2:
        st.metric("Total de Candidatos", f"{microdados_estados.shape[0]:,}")
    with col3:
        maior_media = np.max(media_por_estado) if media_por_estado else 0.0
        st.metric("Maior Média", f"{round(maior_media, 2)}")
    with col4:
        st.metric("Estado com Maior Média", f"{estado_maior_media}")
        
    return medias_estados


def exibir_histograma_notas(microdados_estados, colunas_notas, competencia_mapping):
    """Exibe um histograma interativo da distribuição de notas."""
    st.subheader("Distribuição das Notas")
    
    # Seleção da área de conhecimento
    area_conhecimento = st.selectbox(
        "Selecione a área de conhecimento:",
        options=colunas_notas,
        format_func=lambda x: competencia_mapping[x]
    )
    nome_area = competencia_mapping[area_conhecimento]
    
    # Cálculo das estatísticas
    media = calcular_seguro(microdados_estados[area_conhecimento])
    mediana = calcular_seguro(microdados_estados[area_conhecimento], 'mediana')
    min_valor = calcular_seguro(microdados_estados[area_conhecimento], 'min')
    max_valor = calcular_seguro(microdados_estados[area_conhecimento], 'max')
    
    # Criação do histograma
    fig_hist = criar_histograma(microdados_estados, area_conhecimento, nome_area, 
                              media, mediana, min_valor, max_valor)
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # Explicação do histograma
    explicacao_hist = criar_explicacao_histograma(microdados_estados, area_conhecimento, 
                                               nome_area, media, mediana, min_valor, max_valor)
    st.info(explicacao_hist)


def criar_histograma(df, coluna, nome_area, media, mediana, min_valor, max_valor):
    """Cria um histograma formatado com informações estatísticas."""
    fig = px.histogram(
        df,
        x=coluna,
        nbins=30,
        histnorm='percent',
        title=f"Distribuição das notas - {nome_area}",
        labels={coluna: f"Nota ({nome_area})"},
        opacity=0.7,
        color_discrete_sequence=['#3366CC']
    )
    
    # Adicionar linhas de média e mediana
    fig.add_vline(x=media, line_dash="dash", line_color="red", 
                  annotation_text=f"Média: {media:.2f}")
    fig.add_vline(x=mediana, line_dash="dash", line_color="green", 
                  annotation_text=f"Mediana: {mediana:.2f}")
    
    # Formatação do layout
    fig.update_layout(
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
    
    # Adicionar caixa de estatísticas
    stats_text = f"""
    <b>Estatísticas:</b><br>
    Média: {media:.2f}<br>
    Mediana: {mediana:.2f}<br>
    Mínimo: {min_valor:.2f}<br>
    Máximo: {max_valor:.2f}
    """
    fig.add_annotation(
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
    
    return fig


def criar_explicacao_histograma(df, coluna, nome_area, media, mediana, min_valor, max_valor):
    """Cria texto explicativo para o histograma."""
    candidatos_total = len(df)
    acima_media = len(df[df[coluna] > media])
    percentual_acima = (acima_media / candidatos_total * 100) if candidatos_total > 0 else 0
    
    # Determinar a faixa mais comum
    bin_width = (max_valor - min_valor) / 30  # usando o mesmo nbins do histograma
    faixa_mais_comum = int(mediana // bin_width) * bin_width
    
    # Determinar a tendência da distribuição
    if media > mediana:
        tendencia = "A distribuição apresenta um viés para notas mais altas."
    elif media < mediana:
        tendencia = "A distribuição apresenta um viés para notas mais baixas."
    else:
        tendencia = "A distribuição é aproximadamente simétrica."
    
    return f"""
        Este histograma mostra a distribuição das notas de {nome_area}.
        A média é {media:.2f} e a mediana é {mediana:.2f}, com notas variando de {min_valor:.1f} a {max_valor:.1f}.
        
        {acima_media:,} candidatos ({percentual_acima:.1f}%) obtiveram notas acima da média.
        A faixa de notas mais comum está em torno de {faixa_mais_comum:.0f} pontos.
        
        {tendencia}
    """


def exibir_grafico_linha(df_grafico, estados_selecionados, medias_estados, 
                       microdados_estados, colunas_notas, competencia_mapping):
    """Exibe gráfico de linha das médias por estado e área de conhecimento."""
    st.subheader("Médias por Estado e Área de Conhecimento")
    
    fig = px.line(
        df_grafico,
        x='Estado',
        y='Média',
        color='Área',
        markers=True,
        title='Médias por Estado e Área de Conhecimento',
        labels={'Média': 'Nota Média', 'Estado': 'Estado', 'Área': 'Área de Conhecimento'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
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
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicação para o gráfico de linha
    explicacao = criar_explicacao_grafico_linha(estados_selecionados, medias_estados, 
                                             microdados_estados, colunas_notas, competencia_mapping)
    st.info(explicacao)


def criar_explicacao_grafico_linha(estados_selecionados, medias_estados, 
                                 microdados_estados, colunas_notas, competencia_mapping):
    """Cria texto explicativo para o gráfico de linha."""
    # Identificar melhor e pior estado
    melhor_estado = None
    pior_estado = None
    melhor_media = 0
    pior_media = float('inf')
    
    for estado, media_estado in medias_estados.items():
        if media_estado > melhor_media:
            melhor_media = media_estado
            melhor_estado = estado
        if media_estado < pior_media:
            pior_media = media_estado
            pior_estado = estado
    
    # Calcular médias por área de conhecimento
    medias_por_area = {}
    for col in colunas_notas:
        area_nome = competencia_mapping[col]
        medias_por_area[area_nome] = calcular_seguro(microdados_estados[col])
    
    # Encontrar área com melhor e pior desempenho
    melhor_area = max(medias_por_area.items(), key=lambda x: x[1])[0]
    melhor_media_area = medias_por_area[melhor_area]
    
    pior_area = min(medias_por_area.items(), key=lambda x: x[1])[0]
    pior_media_area = medias_por_area[pior_area]
    
    return f"""
        Este gráfico mostra as médias de desempenho por estado e área de conhecimento.
        
        Entre os {len(estados_selecionados)} estados analisados, {melhor_estado} apresenta a maior média geral ({melhor_media:.1f} pontos),
        enquanto {pior_estado} tem a menor média ({pior_media:.1f} pontos).
        
        A área com melhor desempenho médio é {melhor_area}, com média de {melhor_media_area:.1f} pontos.
        A área com menor desempenho médio é {pior_area}, com média de {pior_media_area:.1f} pontos.
    """