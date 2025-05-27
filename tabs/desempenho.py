import streamlit as st
import pandas as pd
from utils.tooltip import titulo_com_tooltip
from utils.helpers.cache_utils import release_memory
from functools import partial

from utils.prepara_dados import (
    preparar_dados_comparativo, 
    obter_ordem_categorias,
    preparar_dados_grafico_linha,
    preparar_dados_desempenho_geral,
    filtrar_dados_scatter,
    prepara_dados_grafico_linha_desempenho
)

from utils.visualizacao import (
    criar_grafico_comparativo_barras,
    criar_grafico_linha_desempenho,
    criar_grafico_scatter,
    criar_grafico_linha_estados,
    criar_filtros_comparativo,
    criar_filtros_dispersao,
    criar_filtros_estados
)

from utils.estatisticas import (
    calcular_correlacao_competencias,
    gerar_estatisticas_descritivas,
    analisar_desempenho_por_estado
)

from utils.explicacao import (
    get_tooltip_analise_comparativa,
    get_tooltip_relacao_competencias,
    get_tooltip_desempenho_estados,
    get_explicacao_barras_comparativo,
    get_explicacao_linhas_comparativo,
    get_explicacao_dispersao,
    get_explicacao_desempenho_estados
)

from utils.expander.expander_desempenho import (
    criar_expander_analise_comparativa,
    criar_expander_relacao_competencias,
    criar_expander_desempenho_estados
)

pd.options.display.float_format = '{:,.2f}'.format


def exibir_secao_visualizacao(titulo, tooltip_text, tooltip_id, processar_func, exibir_func, explicacao_func, expander_func=None, **kwargs):
    """
    Função auxiliar para exibir uma seção de visualização padronizada com spinner, explicação e expander opcional.
    
    Parâmetros:
    -----------
    titulo : str
        Título da seção
    tooltip_text : str 
        Texto do tooltip
    tooltip_id : str
        ID do tooltip
    processar_func : function
        Função para processamento de dados
    exibir_func : function
        Função para exibir visualização
    explicacao_func : function
        Função para obter o texto de explicação
    expander_func : function, opcional
        Função para criar o expander com análise detalhada
    kwargs : dict
        Argumentos adicionais para as funções
    """
    titulo_com_tooltip(titulo, tooltip_text, tooltip_id)
    
    with st.spinner("Processando dados..."):
        dados_processados = processar_func(**kwargs)
    
    with st.spinner("Gerando visualização..."):
        fig = exibir_func(dados_processados, **kwargs)
        st.plotly_chart(fig, use_container_width=True)
    
    explicacao = explicacao_func(**kwargs)
    st.info(explicacao)
    
    if expander_func:
        expander_func(dados_processados, **kwargs)


def render_desempenho(microdados, microdados_estados, estados_selecionados, 
                     locais_selecionados, colunas_notas, competencia_mapping, race_mapping, 
                     variaveis_categoricas, desempenho_mapping):
    """
    Renderiza a aba de Desempenho com diferentes análises baseadas na seleção do usuário.
    """
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    mensagem = f"Analisando Desempenho para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Usamos um placeholder para microdados_full que só será carregado se necessário
    microdados_full = None
    
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Análise Comparativa", "Relação entre Competências", "Médias por Estado"],
        horizontal=True
    )
    
    if analise_selecionada == "Análise Comparativa":
        # Carrega microdados_full apenas quando necessário
        with st.spinner("Preparando dados para análise comparativa..."):
            microdados_full = preparar_dados_desempenho_geral(microdados_estados, colunas_notas, desempenho_mapping)
        render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping)
        release_memory(microdados_full)  # Libera memória após uso
    elif analise_selecionada == "Relação entre Competências":
        render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping)
    else:
        render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping)


def render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping):
    """
    Renderiza a análise comparativa de desempenho por variável demográfica.
    """
    titulo_com_tooltip(
        "Análise Comparativa do Desempenho por Variáveis Demográficas", 
        get_tooltip_analise_comparativa(), 
        "comparativo_desempenho_tooltip"
    )
    
    variavel_selecionada = st.selectbox(
        "Selecione a variável para análise:",
        options=list(variaveis_categoricas.keys()),
        format_func=lambda x: variaveis_categoricas[x]["nome"]
    )

    if variavel_selecionada not in microdados_full.columns:
        st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} não está disponível no conjunto de dados.")
        return
    
    # Processamento dos dados em um único bloco para evitar redundâncias
    with st.spinner("Processando dados para análise comparativa..."):
        df_resultados = preparar_dados_comparativo(
            microdados_full, 
            variavel_selecionada, 
            variaveis_categoricas, 
            colunas_notas, 
            competencia_mapping
        )
    
    # Configuração dos filtros
    config_filtros = criar_filtros_comparativo(df_resultados, variaveis_categoricas, variavel_selecionada)
    
    # Preparação dos dados para visualização
    competencia_para_filtro = config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None
    df_visualizacao = preparar_dados_grafico_linha(
        df_resultados, 
        config_filtros['competencia_filtro'],
        competencia_para_filtro,
        config_filtros['ordenar_decrescente']
    )
    
    # Exibição do gráfico apropriado
    with st.spinner("Gerando visualização..."):
        variavel_nome = variaveis_categoricas[variavel_selecionada]['nome']
        
        if config_filtros['tipo_grafico'] == "Gráfico de Barras":
            barmode = 'relative' if config_filtros['mostrar_apenas_competencia'] else 'group'
            fig = criar_grafico_comparativo_barras(
                df_visualizacao, variavel_selecionada, variaveis_categoricas, 
                competencia_mapping, barmode=barmode
            )
            explicacao = get_explicacao_barras_comparativo(variavel_nome)
        else:
            fig = criar_grafico_linha_desempenho(
                df_visualizacao, variavel_selecionada, variaveis_categoricas,
                config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None,
                config_filtros['ordenar_decrescente']
            )
            explicacao = get_explicacao_linhas_comparativo(variavel_nome)
            
        st.plotly_chart(fig, use_container_width=True)
    
    # Exibição da explicação e análise detalhada
    st.info(explicacao)
    criar_expander_analise_comparativa(df_resultados, variavel_selecionada, variaveis_categoricas, competencia_mapping, config_filtros)
    
    # Liberar memória
    release_memory([df_resultados, df_visualizacao])


def render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping):
    """
    Renderiza a análise de relação entre competências usando gráfico de dispersão.
    """
    titulo_com_tooltip(
        "Relação entre Competências", 
        get_tooltip_relacao_competencias(), 
        "relacao_competencias_tooltip"
    )
    
    # Configuração dos filtros
    config_filtros = criar_filtros_dispersao(colunas_notas, competencia_mapping)
    
    # Filtragem e processamento dos dados
    with st.spinner("Processando dados para o gráfico de dispersão..."):
        dados_filtrados, registros_removidos = filtrar_dados_scatter(
            microdados_estados, 
            config_filtros['sexo'], 
            config_filtros['tipo_escola'], 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y'], 
            config_filtros['excluir_notas_zero'], 
            race_mapping,
            config_filtros['faixa_salarial']
        )
        
        # Calcular correlação apenas uma vez e reutilizar
        correlacao, interpretacao = calcular_correlacao_competencias(
            dados_filtrados, 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y']
        )
    
    # Informações sobre registros removidos
    if config_filtros['excluir_notas_zero'] and registros_removidos > 0:
        st.info(f"Foram desconsiderados {registros_removidos:,} registros com nota zero.")
    
    # Exibição do gráfico de dispersão
    with st.spinner("Gerando visualização de dispersão..."):
        fig = criar_grafico_scatter(
            dados_filtrados, 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y'], 
            competencia_mapping,
            config_filtros['colorir_por_faixa']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Preparação da explicação
    eixo_x_nome = competencia_mapping[config_filtros['eixo_x']]
    eixo_y_nome = competencia_mapping[config_filtros['eixo_y']]
    explicacao = get_explicacao_dispersao(eixo_x_nome, eixo_y_nome, correlacao)
    
    # Exibição da explicação e análise detalhada
    st.info(explicacao)
    criar_expander_relacao_competencias(dados_filtrados, config_filtros, competencia_mapping, correlacao, interpretacao)
    
    # Liberar memória
    release_memory(dados_filtrados)


def render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """
    Renderiza a análise de desempenho médio por estado ou região.
    """
    titulo_com_tooltip(
        "Médias por Estado/Região e Área de Conhecimento", 
        get_tooltip_desempenho_estados(), 
        "grafico_linha_desempenho_tooltip"
    )
    
    # Adicionar opção para agrupar por região
    col1, col2 = st.columns([1, 2])
    with col1:
        agrupar_por_regiao = st.radio(
            "Visualizar por:",
            ["Estados", "Regiões"],
            horizontal=True,
            key="agrupar_desempenho_regiao"
        ) == "Regiões"
    
    # Processamento dos dados
    with st.spinner("Processando dados..."):
        df_grafico = prepara_dados_grafico_linha_desempenho(
            microdados_estados, 
            estados_selecionados, 
            colunas_notas, 
            competencia_mapping,
            agrupar_por_regiao
        )
    
    # Verificar se temos dados suficientes
    if df_grafico.empty:
        st.warning("Não há dados suficientes para mostrar o desempenho com os filtros aplicados.")
        return
    
    # Configuração dos filtros
    config_filtros = criar_filtros_estados(df_grafico)
    
    # Otimização: evita cópia desnecessária se não precisar ordernar
    if config_filtros['ordenar_por_nota'] and config_filtros['area_selecionada']:
        # Aplicar ordenação e filtro
        df_plot = df_grafico.copy()
        
        # Obter ordem dos estados/regiões pela área selecionada
        media_por_estado = df_plot[df_plot['Área'] == config_filtros['area_selecionada']]
        ordem_estados = media_por_estado.sort_values('Média', ascending=False)['Estado'].tolist()
        
        # Aplicar ordenação como categoria
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        # Filtrar para mostrar apenas a área selecionada se solicitado
        if config_filtros['mostrar_apenas_area']:
            df_plot = df_plot[df_plot['Área'] == config_filtros['area_selecionada']]
    else:
        # Se não precisar ordenar, usa o DataFrame original sem cópia
        df_plot = df_grafico
    
    # Exibição do gráfico
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_linha_estados(
            df_plot, 
            config_filtros['area_selecionada'] if config_filtros['mostrar_apenas_area'] else None,
            config_filtros['ordenar_por_nota'],
            por_regiao=agrupar_por_regiao
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Preparação para explicação e análise
    area_texto = f" em {config_filtros['area_selecionada']}" if config_filtros.get('area_selecionada') and config_filtros.get('mostrar_apenas_area') else " nas diversas áreas de conhecimento"
    
    # Determinar área para análise (usar área específica se selecionada, senão usar Média Geral)
    area_analise = config_filtros.get('area_selecionada') if config_filtros.get('mostrar_apenas_area') and config_filtros.get('area_selecionada') else "Média Geral"
    
    # Análise de desempenho por estado/região
    analise = analisar_desempenho_por_estado(df_grafico, area_analise)
    
    # Preparação da explicação
    melhor_estado = analise['melhor_estado']['Estado']
    pior_estado = analise['pior_estado']['Estado']
    desvio_padrao = analise['desvio_padrao']
    
    # Determinar variabilidade para explicação
    variabilidade = "alta" if desvio_padrao > 15 else "moderada" if desvio_padrao > 8 else "baixa"
    if not config_filtros.get('mostrar_apenas_area'):
        variabilidade = "variável"
    
    # Texto de localidade baseado no modo de visualização
    tipo_localidade = "região" if agrupar_por_regiao else "estado"
    
    # Exibição da explicação e análise detalhada
    explicacao = get_explicacao_desempenho_estados(area_texto, melhor_estado, pior_estado, variabilidade, tipo_localidade)
    st.info(explicacao)
    criar_expander_desempenho_estados(df_grafico, area_analise, analise, tipo_localidade)
    
    # Liberar memória se criamos uma cópia
    if config_filtros['ordenar_por_nota'] and config_filtros['area_selecionada'] and id(df_plot) != id(df_grafico):
        release_memory(df_plot)