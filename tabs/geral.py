import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
from utils.tooltip import custom_metric_with_tooltip, titulo_com_tooltip
from utils.explicacaoes import criar_explicacao_grafico_faltas, criar_explicacao_grafico_linha, criar_explicacao_histograma
from utils.mappings import get_mappings
from utils.data_loader import calcular_seguro, criar_histograma, prepare_data_for_histogram,prepare_data_for_line_chart, prepare_data_for_absence_chart

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
    df_histograma = prepare_data_for_histogram(microdados_estados, colunas_notas[0], competencia_mapping)
    exibir_histograma_notas(df_histograma, microdados_estados, colunas_notas, competencia_mapping)
    
    # Exibir gráfico de linha de médias por estado e área
    df_grafico = prepare_data_for_line_chart(
        microdados_estados, estados_selecionados, colunas_notas, competencia_mapping
    )
    if len(df_grafico) > 0:
        exibir_grafico_linha(df_grafico, estados_selecionados, medias_estados, 
                           microdados_estados, colunas_notas, competencia_mapping)
        
    colunas_presenca = {
        'TP_PRESENCA_CN': 'Ciências da Natureza',
        'TP_PRESENCA_CH': 'Ciências Humanas',
        'TP_PRESENCA_LC': 'Linguagens e Códigos',
        'TP_PRESENCA_MT': 'Matemática',
        'TP_PRESENCA_REDACAO': 'Redação'
    }

    # Exibir gráfico de faltas
    df_faltas = prepare_data_for_absence_chart(
        microdados_estados, estados_selecionados, colunas_presenca
    )
    if len(df_faltas) > 0:
        exibir_grafico_faltas(df_faltas, estados_selecionados)


def exibir_metricas_principais(microdados_estados, estados_selecionados, colunas_notas):
    """Calcula e exibe métricas principais em cards."""
    # Título com tooltip
    explicacao_metricas = """
    Esta seção apresenta as principais métricas resumidas dos dados analisados.
    
    - As métricas são calculadas considerando apenas os estados selecionados no filtro lateral.
    - Os valores representam o panorama geral do desempenho dos candidatos.
    """
    titulo_com_tooltip("Métricas Principais", explicacao_metricas, "metricas_tooltip")
    
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
        
    # Explicações para tooltips
    explicacao_media_geral = """
    A Média Geral é calculada em duas etapas:
    
    1. Para cada estado selecionado, calcula-se a média de cada área de conhecimento 
       (Linguagens, Matemática, Ciências Humanas, Ciências da Natureza e Redação)
    
    2. A média geral é a média aritmética de todas essas médias parciais
    
    Este valor representa o desempenho médio dos candidatos considerando todas as competências e estados selecionados.
    """
    
    explicacao_total = """
    Número total de candidatos nos estados selecionados que realizaram a prova do ENEM 2023.
    
    Este valor considera apenas os registros válidos após aplicação dos filtros e exclusão de dados inconsistentes.
    """
    
    explicacao_maior_media = """
    A Maior Média representa o valor máximo encontrado entre todas as médias calculadas para cada combinação de estado e área de conhecimento.
    
    Este valor indica o melhor desempenho médio observado em qualquer área ou estado dentro da seleção atual.
    """
    
    explicacao_estado_maior = f"""
    Estado que apresenta a maior média geral entre todos os estados selecionados.
    
    Para cada estado, calcula-se a média de todas as áreas de conhecimento, e então identifica-se o estado com o maior valor.
    
    """

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        custom_metric_with_tooltip("Média Geral", f"{round(media_geral, 2)}", 
                                explicacao=explicacao_media_geral, key="col1_media_geral")
    
    with col2:
        custom_metric_with_tooltip("Total de Candidatos", f"{microdados_estados.shape[0]:,}", 
                                explicacao=explicacao_total, key="col2_total")
        
    with col3:
        maior_media = np.max(media_por_estado) if media_por_estado else 0.0
        custom_metric_with_tooltip("Maior Média", f"{round(maior_media, 2)}", 
                                explicacao=explicacao_maior_media, key="col3_maior_media")
        
    with col4:
        custom_metric_with_tooltip("Estado com Maior Média", f"{estado_maior_media}", 
                                explicacao=explicacao_estado_maior, key="col4_estado_maior")
                
    return medias_estados
        

def exibir_histograma_notas(df_histograma, microdados_estados, colunas_notas, competencia_mapping):
    """Exibe um histograma interativo da distribuição de notas."""
    # Título com tooltip explicativo
    explicacao_tooltip = """
    Este gráfico mostra como as notas dos candidatos estão distribuídas em determinada área de conhecimento.
    
    - As barras representam o percentual de candidatos em cada faixa de nota
    - A linha vermelha vertical indica a média das notas
    - A linha verde vertical indica a mediana
    - Os valores estatísticos (min, max, média, mediana, desvio padrão, skillness e curtose) são mostrados na caixa no canto superior esquerdo

    Um histograma com média maior que a mediana indica mais candidatos com notas acima da média.
    """
    titulo_com_tooltip("Histograma das Notas", explicacao_tooltip, "hist_tooltip")
    
    # Seleção da área de conhecimento
    area_conhecimento = st.selectbox(
        "Selecione a área de conhecimento ou redação:",
        options=colunas_notas,
        format_func=lambda x: competencia_mapping[x]
    )
    
    # Obter dados preparados - usar os dados iniciais se a área selecionada for a mesma, senão preparar novos dados
    if df_histograma and df_histograma['coluna'] == area_conhecimento:
        dados_histograma = df_histograma
    else:
        dados_histograma = prepare_data_for_histogram(microdados_estados, area_conhecimento, competencia_mapping)
    # Criar e exibir o histograma
    fig_hist = criar_histograma(dados_histograma)
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # Explicação do histograma
    estatisticas = dados_histograma['estatisticas']
    explicacao_hist = criar_explicacao_histograma(
        dados_histograma['df'], 
        area_conhecimento, 
        dados_histograma['nome_area'],
        estatisticas['media'],
        estatisticas['mediana'],
        estatisticas['min_valor'],
        estatisticas['max_valor']
    )
    st.info(explicacao_hist)


def exibir_grafico_linha(df_grafico, estados_selecionados, medias_estados, 
                       microdados_estados, colunas_notas, competencia_mapping):
    """Exibe gráfico de linha das médias por estado e área de conhecimento."""
    # Texto explicativo para o tooltip do título
    explicacao_tooltip = """
    Este gráfico compara as médias de desempenho dos candidatos por estado e área de conhecimento.
    
    - Cada linha colorida representa uma área de conhecimento diferente
    - Cada ponto mostra a média para um estado específico naquela área
    - Os estados são exibidos no eixo X, e as médias no eixo Y
    - É possível filtrar áreas específicas clicando nas legendas
    
    Utilize este gráfico para identificar:
    • Quais estados têm melhor desempenho em cada área
    • Quais áreas de conhecimento apresentam maiores variações entre estados
    • Padrões regionais de desempenho acadêmico
    """
    
    # Usar título com tooltip em vez de subheader
    titulo_com_tooltip("Médias por Estado e Área de Conhecimento", explicacao_tooltip, "grafico_linha_tooltip")
    
    # Obter todas as áreas disponíveis no DataFrame
    areas_disponiveis = df_grafico['Área'].unique().tolist()
    
    # Interface para ordenação
    col1, col2 = st.columns([1, 2])
    with col1:
        ordenar_por_nota = st.checkbox("Ordenar estados por nota", value=False, key="ordenar_estados_notas")
    
    # Mostrar seletor de área apenas se o usuário escolheu ordenar
    area_selecionada = None
    if ordenar_por_nota:
        with col2:
            area_selecionada = st.selectbox(
                "Ordenar por área:",
                options=["Média Geral"] + areas_disponiveis,
                key="area_ordenacao"
            )
    
    # Criar uma cópia do DataFrame para não modificar o original
    df_plot = df_grafico.copy()
    
    # Se o usuário escolheu ordenar, reorganizamos os dados
    if ordenar_por_nota:
        if area_selecionada == "Média Geral":
            # Verificar se temos a coluna "Média Geral" no DataFrame
            if "Média Geral" in areas_disponiveis:
                # Usar a média geral para ordenação
                media_por_estado = df_plot[df_plot['Área'] == 'Média Geral'].copy()
            else:
                # Calcular a média geral para cada estado
                media_por_estado = df_plot.groupby('Estado')['Média'].mean().reset_index()
        else:
            # Usar a área selecionada para ordenação
            media_por_estado = df_plot[df_plot['Área'] == area_selecionada].copy()
            
        # Criar um mapeamento da ordem dos estados com base na área selecionada
        ordem_estados = media_por_estado.sort_values('Média', ascending=False)['Estado'].tolist()
        
        # Reordenar o DataFrame usando o mapeamento
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        # Opcional: Filtrar para mostrar apenas a área selecionada se não for "Média Geral"
        if area_selecionada != "Média Geral" and st.checkbox("Mostrar apenas a área selecionada", value=False):
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    
    # Criar o gráfico com os dados ordenados
    fig = px.line(
        df_plot,
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
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicação para o gráfico de linha
    explicacao = criar_explicacao_grafico_linha(estados_selecionados, medias_estados, 
                                             microdados_estados, colunas_notas, competencia_mapping)
    st.info(explicacao)

def exibir_grafico_faltas(df_faltas, estados_selecionados):
    """
    Exibe gráfico de linha mostrando percentual de faltas por estado e área de conhecimento.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame com os dados de faltas preparados
    estados_selecionados : lista
        Lista de estados selecionados para análise
    """
    # Texto explicativo para o tooltip do título
    explicacao_tooltip = """
    Este gráfico mostra o percentual de candidatos que faltaram em cada área de conhecimento por estado.

    - Cada linha colorida representa uma área de conhecimento diferente
    - A linha "Geral (qualquer prova)" representa candidatos que faltaram em pelo menos uma das provas
    - Os pontos mostram o percentual de faltas para um estado específico naquela área

    Importante: O ENEM é realizado em dois dias, com as seguintes provas:
    - 1º dia: Linguagens e Códigos + Ciências Humanas
    - 2º dia: Ciências da Natureza + Matemática

    Como a presença é registrada por dia de prova, as áreas do mesmo dia apresentam percentuais idênticos de faltas.
    """
    
    # Usar título com tooltip
    titulo_com_tooltip("Percentual de Faltas por Estado e Área de Conhecimento", 
                     explicacao_tooltip, "grafico_faltas_tooltip")
    
    # Obter todas as áreas disponíveis no DataFrame
    areas_disponiveis = df_faltas['Área'].unique().tolist()
    
    # Interface para ordenação
    col1, col2 = st.columns([1, 2])
    with col1:
        ordenar_por_faltas = st.checkbox("Ordenar estados por % de faltas", value=False, key="ordenar_estados_faltas")
    
    # Mostrar seletor de área apenas se o usuário escolheu ordenar
    area_selecionada_faltas = None
    if ordenar_por_faltas:
        with col2:
            area_selecionada_faltas = st.selectbox(
                "Ordenar por área:",
                options=["Geral (qualquer prova)"] + [a for a in areas_disponiveis if a != "Geral (qualquer prova)"],
                key="area_ordenacao_faltas"
            )
    
    # Criar uma cópia do DataFrame para não modificar o original
    df_plot_faltas = df_faltas.copy()
    
    # Se o usuário escolheu ordenar, reorganizamos os dados
    if ordenar_por_faltas:
        # Filtrar pelo critério selecionado
        faltas_por_estado = df_plot_faltas[df_plot_faltas['Área'] == area_selecionada_faltas].copy()
            
        # Criar um mapeamento da ordem dos estados com base na área selecionada
        # Ordem decrescente para mostrar primeiro os estados com maior % de faltas
        ordem_estados = faltas_por_estado.sort_values('Percentual de Faltas', ascending=False)['Estado'].tolist()
        
        # Reordenar o DataFrame usando o mapeamento
        df_plot_faltas['Estado'] = pd.Categorical(df_plot_faltas['Estado'], categories=ordem_estados, ordered=True)
        df_plot_faltas = df_plot_faltas.sort_values('Estado')
        
        # Opcional: Filtrar para mostrar apenas a área selecionada
        if st.checkbox("Mostrar apenas a área selecionada", value=False, key="mostrar_apenas_area_faltas"):
            df_plot_faltas = df_plot_faltas[df_plot_faltas['Área'] == area_selecionada_faltas]
    
    fig = px.line(
        df_plot_faltas,
        x='Estado',
        y='Percentual de Faltas',
        color='Área',
        markers=True,
        labels={
            'Percentual de Faltas': '% de Candidatos Ausentes', 
            'Estado': 'Estado', 
            'Área': 'Área de Conhecimento'
        },
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Estado",
        yaxis_title="% de Candidatos Ausentes",
        legend_title="Área de Conhecimento",
        xaxis=dict(tickangle=-45),
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        legend=dict(
            title=dict(text="Área de Conhecimento<br><sup>Clique para comparar áreas específicas</sup>"),
        ),
        yaxis=dict(
            ticksuffix="%",  # Adicionar símbolo % aos valores do eixo Y
            range=[0, df_faltas['Percentual de Faltas'].max() * 1.1]  # Margem superior para visualização
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Explicação para o gráfico de faltas
    explicacao = criar_explicacao_grafico_faltas(df_faltas, estados_selecionados)
    st.info(explicacao)