import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable  # Adicionar esta linha
from utils.tooltip import titulo_com_tooltip
from utils.helpers.cache_utils import release_memory, optimized_cache
from functools import partial

from utils.prepara_dados import (
    preparar_dados_correlacao,
    preparar_dados_distribuicao,
    contar_candidatos_por_categoria,
    ordenar_categorias,
    preparar_dados_grafico_aspectos_por_estado
)

from utils.visualizacao import (
    criar_grafico_heatmap,
    criar_grafico_barras_empilhadas,
    criar_grafico_sankey,
    criar_grafico_distribuicao,
    criar_grafico_aspectos_por_estado
)

from utils.estatisticas import (
    calcular_estatisticas_distribuicao,
    analisar_correlacao_categorias,
    analisar_distribuicao_regional,
    calcular_estatisticas_por_categoria
)

from utils.explicacao import (
    get_tooltip_correlacao_aspectos,
    get_tooltip_distribuicao_aspectos,
    get_tooltip_aspectos_por_estado,
    get_explicacao_heatmap,
    get_explicacao_barras_empilhadas,
    get_explicacao_sankey,
    get_explicacao_distribuicao,
    get_explicacao_aspectos_por_estado
)

from utils.expander import (
    criar_expander_analise_correlacao,
    criar_expander_dados_distribuicao,
    criar_expander_analise_regional,
    criar_expander_dados_completos_estado
)

pd.options.display.float_format = '{:,.2f}'.format


def render_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais):
    """
    Renderiza a aba de Aspectos Sociais com diferentes análises baseadas na seleção do usuário.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados apenas dos estados selecionados
    estados_selecionados : list
        Lista com as siglas dos estados selecionados pelo usuário
    locais_selecionados : list
        Lista com os nomes dos estados/regiões selecionados para exibição
    variaveis_sociais : dict
        Dicionário com as variáveis sociais disponíveis e seus mapeamentos
    """
    # Verificar se existem estados selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Mensagem informativa sobre filtros aplicados
    mensagem = "Analisando Aspectos Sociais para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Permitir ao usuário selecionar a análise desejada
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Correlação entre Aspectos Sociais", "Distribuição de Aspectos Sociais", "Aspectos Sociais por Estado/Região"],
        horizontal=True
    )
    
    # Direcionar para a análise selecionada
    if analise_selecionada == "Correlação entre Aspectos Sociais":
        render_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais)
    elif analise_selecionada == "Distribuição de Aspectos Sociais":
        render_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais)
    else:  # "Aspectos Sociais por Estado/Região"
        render_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais)


def render_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais):
    """
    Renderiza a análise de correlação entre dois aspectos sociais.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados dos estados selecionados
    estados_selecionados : list
        Lista com as siglas dos estados selecionados
    locais_selecionados : list
        Lista com os nomes dos estados/regiões selecionados
    variaveis_sociais : dict
        Dicionário com as variáveis sociais disponíveis e seus mapeamentos
    """
    # Título com tooltip
    titulo_com_tooltip(
        "Correlação entre Aspectos Sociais", 
        get_tooltip_correlacao_aspectos(), 
        "correlacao_aspectos_tooltip"
    )
    
    # Seleção do tipo de visualização
    tipo_grafico = st.radio(
        "Escolha o tipo de visualização:",
        ["Heatmap", "Barras Empilhadas", "Sankey"],
        horizontal=True,
        key="tipo_viz_correlacao"
    )
    
    # Seleção das variáveis para correlação
    col1, col2 = st.columns(2)

    # Inicializar session_state para var_y_previous se não existir
    if 'var_y_previous' not in st.session_state:
        st.session_state.var_y_previous = None

    with col1:
        var_x = st.selectbox(
            "Variável X:", 
            options=list(variaveis_sociais.keys()),
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="var_x_social"
        )

    with col2:
        # Filtrar para não repetir a mesma variável
        opcoes_y = [k for k in variaveis_sociais.keys() if k != var_x]

        # Determinar o índice inicial baseado na seleção anterior
        index = 0
        if st.session_state.var_y_previous in opcoes_y:
            index = opcoes_y.index(st.session_state.var_y_previous)

        var_y = st.selectbox(
            "Variável Y:", 
            options=opcoes_y,
            format_func=lambda x: variaveis_sociais[x]["nome"],
            index=index,
            key="var_y_social"
        )

        # Armazenar a seleção atual para o próximo ciclo
        st.session_state.var_y_previous = var_y
    
    # Verificar se ambas as variáveis existem nos dados
    colunas_ausentes = []
    if var_x not in microdados_estados.columns:
        colunas_ausentes.append(variaveis_sociais[var_x]["nome"])
    if var_y not in microdados_estados.columns:
        colunas_ausentes.append(variaveis_sociais[var_y]["nome"])
        
    if colunas_ausentes:
        st.warning(f"As seguintes variáveis não estão disponíveis nos dados: {', '.join(colunas_ausentes)}")
        return
    
    # Preparar dados para visualização
    with st.spinner("Preparando dados para análise..."):
        df_preparado, var_x_plot, var_y_plot = preparar_dados_correlacao(
            microdados_estados, var_x, var_y, variaveis_sociais
        )
    
    # Verificar se temos dados suficientes
    if df_preparado.empty:
        st.warning("Não há dados suficientes para analisar a correlação entre estas variáveis.")
        return
    
    # Calcular métricas para análise estatística
    with st.spinner("Calculando métricas estatísticas..."):
        metricas = analisar_correlacao_categorias(df_preparado, var_x_plot, var_y_plot)
    
    # Texto para indicar estados no título
    estados_texto = ', '.join(locais_selecionados) if len(locais_selecionados) <= 3 else f"{len(estados_selecionados)} estados selecionados"
    
    # Criar visualização apropriada com base na escolha do usuário
    with st.spinner("Gerando visualização..."):
        if tipo_grafico == "Heatmap":
            fig, explicacao = criar_grafico_heatmap(
                df_preparado, var_x, var_y, var_x_plot, var_y_plot, 
                variaveis_sociais, estados_texto
            )
            
        elif tipo_grafico == "Barras Empilhadas":
            fig, explicacao = criar_grafico_barras_empilhadas(
                df_preparado, var_x, var_y, var_x_plot, var_y_plot, 
                variaveis_sociais, estados_texto
            )
            
        else:  # Sankey
            fig, explicacao = criar_grafico_sankey(
                df_preparado, var_x, var_y, var_x_plot, var_y_plot, 
                variaveis_sociais, estados_texto
            )
    
    # Exibir o gráfico e explicação
    st.plotly_chart(fig, use_container_width=True)
    st.info(explicacao)
    
    # Adicionar análise estatística detalhada
    criar_expander_analise_correlacao(df_preparado, var_x, var_y, var_x_plot, var_y_plot, variaveis_sociais)
    
    # Liberar memória após uso
    release_memory(df_preparado)


def render_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais):
    """
    Renderiza a análise de distribuição de um aspecto social.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados dos estados selecionados
    variaveis_sociais : dict
        Dicionário com as variáveis sociais disponíveis e seus mapeamentos
    """
    # Título com tooltip
    titulo_com_tooltip(
        "Distribuição de Aspectos Sociais", 
        get_tooltip_distribuicao_aspectos(), 
        "distribuicao_aspectos_tooltip"
    )
    
    # Permitir ao usuário selecionar qual aspecto social visualizar
    aspecto_social = st.selectbox(
        "Selecione o aspecto social para análise:",
        options=list(variaveis_sociais.keys()),
        format_func=lambda x: variaveis_sociais[x]["nome"],
        key="aspecto_dist"
    )
    
    # Verificar se a coluna existe nos dados
    if aspecto_social not in microdados_estados.columns:
        st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
        return
    
    # Preparar dados para visualização
    with st.spinner("Preparando dados..."):
        df_preparado, coluna_plot = preparar_dados_distribuicao(
            microdados_estados, 
            aspecto_social, 
            variaveis_sociais
        )
        
        # Verificar se temos dados suficientes
        if df_preparado.empty:
            st.warning(f"Não há dados suficientes para analisar a distribuição de {variaveis_sociais[aspecto_social]['nome']}.")
            return
        
        # Contar candidatos por categoria
        contagem_aspecto = contar_candidatos_por_categoria(df_preparado, coluna_plot)
        
        # Verificar se temos categorias
        if contagem_aspecto.empty:
            st.warning(f"Não foram encontradas categorias para {variaveis_sociais[aspecto_social]['nome']}.")
            return
        
        # Ordenar os dados
        contagem_aspecto = ordenar_categorias(contagem_aspecto, aspecto_social, variaveis_sociais)
    
    # Calcular estatísticas
    with st.spinner("Calculando estatísticas..."):
        estatisticas = calcular_estatisticas_distribuicao(contagem_aspecto)
        
    # Obter informações para explicação
    total = estatisticas['total']
    categoria_mais_frequente = estatisticas['categoria_mais_frequente']
    
    # Criar opções de visualização
    opcao_viz = st.radio(
        "Tipo de visualização:",
        ["Gráfico de Barras", "Gráfico de Linha", "Gráfico de Pizza"],
        horizontal=True,
        key="viz_tipo_dist"
    )
    
    # Criar visualização com base na escolha do usuário
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_distribuicao(
            contagem_aspecto, 
            opcao_viz, 
            aspecto_social, 
            variaveis_sociais
        )
    
    # Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar explicação sobre o gráfico
    explicacao = get_explicacao_distribuicao(
        variaveis_sociais[aspecto_social]["nome"], 
        total, 
        categoria_mais_frequente
    )
    st.info(explicacao)
    
    # Usar o expander para dados detalhados
    criar_expander_dados_distribuicao(contagem_aspecto, aspecto_social, variaveis_sociais)
    
    # Liberar memória após uso
    release_memory([df_preparado, contagem_aspecto])


def render_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais):
    """
    Renderiza a análise de distribuição de aspectos sociais por estado ou região.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados dos estados selecionados
    estados_selecionados : list
        Lista com as siglas dos estados selecionados
    variaveis_sociais : dict
        Dicionário com as variáveis sociais disponíveis e seus mapeamentos
    """
    # Título com tooltip
    titulo_com_tooltip(
        "Distribuição de Aspectos Sociais por Estado/Região", 
        get_tooltip_aspectos_por_estado(), 
        "aspectos_por_estado_tooltip"
    )
    
    # Permitir ao usuário selecionar qual aspecto social visualizar
    aspecto_social = st.selectbox(
        "Selecione o aspecto social para análise por estado/região:",
        options=list(variaveis_sociais.keys()),
        format_func=lambda x: variaveis_sociais[x]["nome"],
        key="aspecto_por_estado"
    )
    
    # Verificar se a coluna existe nos dados
    if aspecto_social not in microdados_estados.columns:
        st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
        return
    
    # Adicionar opção para agrupar por região
    col1, col2 = st.columns([1, 2])
    with col1:
        agrupar_por_regiao = st.radio(
            "Visualizar por:",
            ["Estados", "Regiões"],
            horizontal=True,
            key="agrupar_aspectos_regiao"
        ) == "Regiões"
    
    # Preparar dados para visualização
    with st.spinner("Preparando dados..."):
        df_por_estado = preparar_dados_grafico_aspectos_por_estado(
            microdados_estados, 
            aspecto_social, 
            estados_selecionados, 
            variaveis_sociais,
            agrupar_por_regiao
        )
    
    # Verificar se temos dados suficientes
    if df_por_estado.empty:
        tipo_localidade = "região" if agrupar_por_regiao else "estado"
        st.warning(f"Não há dados suficientes para mostrar a distribuição de {variaveis_sociais[aspecto_social]['nome']} por {tipo_localidade}.")
        return
    
    # Interface para ordenação e filtragem
    col1, col2 = st.columns([1, 2])
    
    with col1:
        ordenar_por_percentual = st.checkbox(
            "Ordenar por percentual", 
            value=False, 
            key="ordenar_estados_percentual"
        )
    
    # Mostrar seletor de categoria apenas se o usuário escolheu ordenar
    categoria_selecionada = None
    if ordenar_por_percentual:
        with col2:
            categorias_disponiveis = sorted(df_por_estado['Categoria'].unique().tolist())
            categoria_selecionada = st.selectbox(
                "Ordenar por categoria:",
                options=categorias_disponiveis,
                key="categoria_ordenacao"
            )
    
    # Criar uma cópia do DataFrame para processamento
    df_plot = df_por_estado.copy()
    
    # Se o usuário escolheu ordenar, reorganizamos os dados
    if ordenar_por_percentual and categoria_selecionada:
        df_plot = _ordenar_dados_por_categoria(df_plot, categoria_selecionada)
        
        # Opcional: Filtrar para mostrar apenas a categoria selecionada
        mostrar_apenas_categoria = st.checkbox(
            "Mostrar apenas a categoria selecionada", 
            value=False, 
            key="mostrar_apenas_categoria_estado"
        )
        
        if mostrar_apenas_categoria:
            df_plot = df_plot[df_plot['Categoria'] == categoria_selecionada]
    
    # Criar o gráfico
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_aspectos_por_estado(
            df_plot, 
            aspecto_social, 
            variaveis_sociais, 
            por_regiao=agrupar_por_regiao
        )
    
    # Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar explicação contextualizada
    tipo_localidade = "região" if agrupar_por_regiao else "estado"
    explicacao = get_explicacao_aspectos_por_estado(
        variaveis_sociais[aspecto_social]['nome'], 
        categoria_selecionada,
        tipo_localidade
    )
    st.info(explicacao)
    
    # Adicionar análise estatística detalhada se uma categoria foi selecionada
    if categoria_selecionada:
        criar_expander_analise_regional(
            df_por_estado, 
            aspecto_social, 
            categoria_selecionada, 
            variaveis_sociais, 
            tipo_localidade
        )
    
    # Adicionar tabela completa de dados
    criar_expander_dados_completos_estado(df_por_estado, tipo_localidade)
    
    # Liberar memória
    release_memory([df_por_estado, df_plot])


def _ordenar_dados_por_categoria(df: pd.DataFrame, categoria: str) -> pd.DataFrame:
    """
    Ordena o DataFrame com base nos percentuais de uma categoria específica.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame a ser ordenado
    categoria : str
        Categoria usada como base para ordenação
        
    Retorna:
    --------
    DataFrame
        DataFrame ordenado
    """
    try:
        # Filtrar apenas os dados da categoria selecionada para ordenação
        percentual_por_estado = df[df['Categoria'] == categoria].copy()
        
        # Verificar se temos dados para esta categoria
        if percentual_por_estado.empty:
            return df
            
        # Criar um mapeamento da ordem dos estados com base na categoria selecionada
        ordem_estados = percentual_por_estado.sort_values('Percentual', ascending=False)['Estado'].tolist()
        
        # Reordenar o DataFrame usando o mapeamento
        df_ordenado = df.copy()
        df_ordenado['Estado'] = pd.Categorical(df_ordenado['Estado'], categories=ordem_estados, ordered=True)
        return df_ordenado.sort_values('Estado')
    
    except Exception as e:
        print(f"Erro ao ordenar dados por categoria: {e}")
        return df  # Retornar DataFrame original em caso de erro


def exibir_secao_visualizacao(
    titulo: str, 
    tooltip_text: str, 
    tooltip_id: str, 
    processar_func: Callable, 
    exibir_func: Callable, 
    explicacao_func: Callable, 
    expander_func: Optional[Callable] = None, 
    **kwargs
) -> None:
    """
    Função auxiliar para exibir uma seção de visualização padronizada.
    
    Parâmetros:
    -----------
    titulo : str
        Título da seção
    tooltip_text : str 
        Texto do tooltip
    tooltip_id : str
        ID do tooltip
    processar_func : callable
        Função para processamento de dados
    exibir_func : callable
        Função para exibir visualização
    explicacao_func : callable
        Função para obter o texto de explicação
    expander_func : callable, opcional
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