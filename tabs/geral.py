import streamlit as st
import numpy as np
import pandas as pd
from utils.tooltip import titulo_com_tooltip, custom_metric_with_tooltip

# Importações para preparação de dados
from utils.prepara_dados import (
    prepara_dados_histograma,
    prepara_dados_grafico_faltas
)

# Importações para visualizações
from utils.visualizacao import (
    criar_histograma,
    criar_grafico_faltas
)

# Importações para explicações
from utils.explicacao import (
    get_tooltip_metricas_principais,
    get_tooltip_histograma,
    get_tooltip_faltas,
    get_tooltip_media_geral,
    get_tooltip_total_candidatos,
    get_tooltip_maior_media,
    get_tooltip_menor_media,  # Nova importação
    get_explicacao_histograma,
    get_explicacao_faltas
)

# Importações para análises
from utils.estatisticas import (
    analisar_metricas_principais,
    analisar_distribuicao_notas,
    analisar_faltas
)

# Importações para expanders
from utils.expander import (
    criar_expander_analise_histograma,
    criar_expander_analise_faltas
)

# pd.options.display.float_format = "{:,.2f}".format

def render_geral(microdados_estados, estados_selecionados, locais_selecionados, colunas_notas, competencia_mapping):
    """
    Renderiza a aba Geral do dashboard com métricas e visualizações.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : list
        Lista com os estados selecionados para análise
    locais_selecionados : list
        Lista de regiões/estados formatada para exibição
    colunas_notas : list
        Lista com os nomes das colunas de notas
    competencia_mapping : dict
        Dicionário que mapeia códigos de competências para seus nomes
    """
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    mensagem = f"Analisando Dados Gerais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Exibir métricas principais (sempre visíveis)
    metricas = exibir_metricas_principais(microdados_estados, estados_selecionados, colunas_notas)
    
    # Permitir ao usuário selecionar a análise desejada
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Distribuição de Notas", "Análise de Faltas"],
        horizontal=True
    )
    
    # Mostrar apenas a análise selecionada
    if analise_selecionada == "Distribuição de Notas":
        exibir_histograma_notas(microdados_estados, colunas_notas, competencia_mapping)
    else:  # "Análise de Faltas"
        exibir_analise_faltas(microdados_estados, estados_selecionados)


def exibir_metricas_principais(microdados_estados, estados_selecionados, colunas_notas):
    """
    Calcula e exibe métricas principais em cards.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : list
        Lista com os estados selecionados para análise
    colunas_notas : list
        Lista com os nomes das colunas de notas
        
    Retorna:
    --------
    dict
        Métricas calculadas para uso em outras visualizações
    """
    # Título com tooltip
    titulo_com_tooltip("Métricas Principais", get_tooltip_metricas_principais(), "metricas_tooltip")
    
    # Calcular métricas principais
    metricas = analisar_metricas_principais(microdados_estados, estados_selecionados, colunas_notas)
    
    # Exibir as métricas em cards usando custom_metric_with_tooltip
    col1, col2, col3, col4 = st.columns(4)

    # Função para formatar números com vírgula como separador decimal
    def formatar_numero_br(valor, casas_decimais=2):
        formatado = f"{valor:,.{casas_decimais}f}"
        return formatado.replace(',', 'X').replace('.', ',').replace('X', '.')

    with col1:
        custom_metric_with_tooltip(
            label="Candidatos Inscritos",
            value=f"{metricas['total_candidatos']:,}".replace(',', '.'),
            explicacao=get_tooltip_total_candidatos(),
            key="1"
        )
    
    with col2:
        custom_metric_with_tooltip(
            label="Média Geral",
            value=formatar_numero_br(metricas['media_geral']),
            # value=metricas['media_geral'],
            explicacao=get_tooltip_media_geral(),
            key="2"
        )
        
    with col3:
        # Formatar maior média com o estado entre parênteses
        custom_metric_with_tooltip(
            label="Maior Média",
            value=f"{formatar_numero_br(metricas['valor_maior_media_estado'])} ({metricas['estado_maior_media']})",
            explicacao=get_tooltip_maior_media(),
            key="3"
        )
    
    with col4:
        # Substituir estado com maior média por menor média
        custom_metric_with_tooltip(
            label="Menor Média",
            value=f"{formatar_numero_br(metricas['valor_menor_media_estado'])} ({metricas['estado_menor_media']})",
            explicacao=get_tooltip_menor_media(),
            key="4",
        )
                
    return metricas


def exibir_histograma_notas(microdados_estados, colunas_notas, competencia_mapping):
    """
    Exibe um histograma interativo da distribuição de notas.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    colunas_notas : list
        Lista com os nomes das colunas de notas
    competencia_mapping : dict
        Dicionário que mapeia códigos de competências para seus nomes
    """
    # Título com tooltip explicativo
    titulo_com_tooltip("Histograma das Notas", get_tooltip_histograma(), "hist_tooltip")
    
    # Seleção da área de conhecimento
    area_conhecimento = st.selectbox(
        "Selecione a área de conhecimento ou redação:",
        options=colunas_notas,
        format_func=lambda x: competencia_mapping[x]
    )
    
    # Preparar dados para o histograma
    with st.spinner("Processando dados para o histograma..."):
        # Esta função retorna uma tupla (df, coluna, nome_area)
        df_valido, coluna_hist, nome_area_hist = prepara_dados_histograma(microdados_estados, area_conhecimento, competencia_mapping)
        estatisticas = analisar_distribuicao_notas(df_valido, area_conhecimento)
    
    # Criar e exibir o histograma
    with st.spinner("Gerando visualização..."):
        # CORREÇÃO: Passar o DataFrame diretamente em vez do dicionário
        fig_hist = criar_histograma(
            df_valido,  # Passar o DataFrame diretamente
            coluna_hist,
            nome_area_hist,
            estatisticas
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Explicação do histograma
    explicacao = get_explicacao_histograma(
        nome_area_hist,
        estatisticas['media'],
        estatisticas['mediana'],
        estatisticas['assimetria'],
        estatisticas['curtose']
    )
    st.info(explicacao)
    
    # Adicionar expander com análise detalhada
    criar_expander_analise_histograma(df_valido, coluna_hist, nome_area_hist, estatisticas)


def exibir_analise_faltas(microdados_estados, estados_selecionados):
    """
    Exibe análise de faltas por estado e dia de prova.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : list
        Lista com os estados selecionados para análise
    """
    # Definir mapeamento das colunas de presença (mantido para compatibilidade)
    colunas_presenca = {
        'TP_PRESENCA_CN': 'Ciências da Natureza',
        'TP_PRESENCA_CH': 'Ciências Humanas',
        'TP_PRESENCA_LC': 'Linguagens e Códigos',
        'TP_PRESENCA_MT': 'Matemática',
        'TP_PRESENCA_REDACAO': 'Redação'
    }
    
    # Título com tooltip
    titulo_com_tooltip("Análise de Faltas por Dia de Prova", get_tooltip_faltas(), "faltas_tooltip")
    
    # Preparar dados para o gráfico de faltas
    with st.spinner("Processando dados para análise de faltas..."):
        df_faltas = prepara_dados_grafico_faltas(microdados_estados, estados_selecionados, colunas_presenca)
        
        if df_faltas.empty:
            st.warning("Não há dados suficientes para análise de faltas com os filtros aplicados.")
            return
    
    # Interface para ordenação
    col1, col2 = st.columns([1, 2])
    with col1:
        ordenar_por_faltas = st.checkbox("Ordenar estados por % de faltas", value=False)
    
    # Mostrar seletor de tipo de falta apenas se o usuário escolheu ordenar
    tipo_selecionado = None
    if ordenar_por_faltas:
        with col2:
            tipos_disponiveis = df_faltas['Tipo de Falta'].unique().tolist()
            # Remover qualquer tipo que contenha "Total de faltas"
            tipos_disponiveis = [tipo for tipo in tipos_disponiveis if "Total de faltas" not in tipo]
            tipo_selecionado = st.selectbox(
                "Ordenar por tipo de falta:",
                options=tipos_disponiveis
            )
    
    # Criar o gráfico
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_faltas(
            df_faltas, 
            order_by_area=tipo_selecionado if ordenar_por_faltas else None,
            order_ascending=False,
            filtro_area=tipo_selecionado if (ordenar_por_faltas and st.checkbox("Mostrar apenas o tipo de falta selecionado", value=False)) else None
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Calcular análise completa das faltas
    analise_faltas_dados = analisar_faltas(df_faltas)
    
    # Extrair os dados necessários para a explicação
    taxa_media_geral = analise_faltas_dados['taxa_media_geral']
    tipo_mais_comum = analise_faltas_dados['tipo_mais_comum']
    
    # Verificar se os dados de estado estão disponíveis
    estado_maior_falta = "N/A"
    if analise_faltas_dados['estado_maior_falta'] is not None:
        estado_maior_falta = analise_faltas_dados['estado_maior_falta']['Estado']
    
    estado_menor_falta = "N/A"
    if analise_faltas_dados['estado_menor_falta'] is not None:
        estado_menor_falta = analise_faltas_dados['estado_menor_falta']['Estado']
    
    # Explicação com os argumentos corretos
    explicacao = get_explicacao_faltas(
        taxa_media_geral,
        tipo_mais_comum,
        estado_maior_falta,
        estado_menor_falta
    )
    st.info(explicacao)
    
    # Adicionar expander com análise detalhada
    criar_expander_analise_faltas(df_faltas, analise_faltas_dados)