import streamlit as st
import pandas as pd
from utils.tooltip import titulo_com_tooltip

from utils.prepara_dados import (
    preparar_dados_correlacao,
    preparar_dados_distribuicao,
    contar_candidatos_por_categoria,
    ordenar_categorias,
    preparar_dados_heatmap,
    preparar_dados_barras_empilhadas,
    preparar_dados_sankey,
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
    analisar_distribuicao_regional
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

def render_aspectos_sociais(microdados_estados, estados_selecionados, locais_selecionados, variaveis_sociais):
    """
    Renderiza a aba de Aspectos Sociais com visualizações de correlações entre variáveis sociais.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados apenas dos estados selecionados
    estados_selecionados : list
        Lista com as siglas dos estados selecionados pelo usuário
    variaveis_sociais : dict
        Dicionário com as variáveis sociais disponíveis e seus mapeamentos
    """
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    mensagem = f"Analisando Desempenho para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(locais_selecionados)}"
    st.info(mensagem)
    
    # Permitir ao usuário selecionar a análise desejada
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Correlação entre Aspectos Sociais", "Distribuição de Aspectos Sociais", "Aspectos Sociais por Estado"],
        horizontal=True
    )
    
    # Renderizar apenas a seção selecionada
    if analise_selecionada == "Correlação entre Aspectos Sociais":
        exibir_correlacao_aspectos_sociais(microdados_estados, estados_selecionados, variaveis_sociais)
    elif analise_selecionada == "Distribuição de Aspectos Sociais":
        exibir_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais)
    else:  # "Aspectos Sociais por Estado"
        exibir_grafico_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais)


def exibir_correlacao_aspectos_sociais(microdados_estados, estados_selecionados,    variaveis_sociais):
    """
    Exibe gráficos de correlação entre dois aspectos sociais selecionados.
    """
    # Usar título com tooltip em vez de header simples
    titulo_com_tooltip(
        "Correlação entre Aspectos Sociais", 
        get_tooltip_correlacao_aspectos(), 
        "correlacao_aspectos_tooltip"
    )
    
    # Seleção do tipo de visualização
    tipo_grafico = st.radio(
        "Escolha o tipo de visualização:",
        ["Heatmap", "Barras Empilhadas", "Sankey"],
        horizontal=True
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

        # Armazenar a seleção atual como a anterior para o próximo ciclo
        st.session_state.var_y_previous = var_y
    
    # Verificar se as variáveis selecionadas existem nos dados
    if var_x not in microdados_estados.columns or var_y not in microdados_estados.columns:
        st.warning(f"Uma ou ambas as variáveis selecionadas não estão disponíveis no conjunto de dados.")
        return
    
    # Preparar dados para visualização
    with st.spinner("Preparando dados..."):
        df_preparado, var_x_plot, var_y_plot = preparar_dados_correlacao(
            microdados_estados, var_x, var_y, variaveis_sociais
        )
    
    # Texto para indicar estados no título
    estados_texto = ', '.join(estados_selecionados) if len(estados_selecionados) <= 3 else f"{len(estados_selecionados)} estados selecionados"
    
    # Criar visualização com base na escolha do usuário
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
    
    # Calcular métricas para análise
    metricas = analisar_correlacao_categorias(df_preparado, var_x_plot, var_y_plot)
    
    # Adicionar análise estatística usando o expander encapsulado
    criar_expander_analise_correlacao(df_preparado, var_x, var_y, var_x_plot, var_y_plot, variaveis_sociais, metricas)


def exibir_distribuicao_aspectos_sociais(microdados_estados, variaveis_sociais):
    """
    Exibe gráficos de distribuição para um aspecto social selecionado.
    """
    # Usar título com tooltip
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
        df_preparado, coluna_plot = preparar_dados_distribuicao(microdados_estados, aspecto_social, variaveis_sociais)
        
        # Contar candidatos por categoria
        contagem_aspecto = contar_candidatos_por_categoria(df_preparado, coluna_plot)
        
        # Ordenar os dados
        contagem_aspecto = ordenar_categorias(contagem_aspecto, aspecto_social, variaveis_sociais)
        
        # Calcular percentuais
        total = contagem_aspecto['Quantidade'].sum()
        contagem_aspecto['Percentual'] = (contagem_aspecto['Quantidade'] / total * 100).round(2)
    
    # Calcular estatísticas
    estatisticas = calcular_estatisticas_distribuicao(contagem_aspecto)
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
        fig = criar_grafico_distribuicao(contagem_aspecto, opcao_viz, aspecto_social, variaveis_sociais)
    
    # Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Adicionar explicação sobre o gráfico
    explicacao = get_explicacao_distribuicao(
        variaveis_sociais[aspecto_social]["nome"], 
        total, 
        categoria_mais_frequente
    )
    st.info(explicacao)
    
    # Usar o expander encapsulado para dados detalhados
    criar_expander_dados_distribuicao(contagem_aspecto, estatisticas, aspecto_social, variaveis_sociais)


def exibir_grafico_aspectos_por_estado(microdados_estados, estados_selecionados, variaveis_sociais):
    """
    Exibe gráfico de linha mostrando distribuição de aspectos sociais por estado.
    """
    # Usar título com tooltip
    titulo_com_tooltip(
        "Distribuição de Aspectos Sociais por Estado", 
        get_tooltip_aspectos_por_estado(), 
        "aspectos_por_estado_tooltip"
    )
    
    # Permitir ao usuário selecionar qual aspecto social visualizar
    aspecto_social = st.selectbox(
        "Selecione o aspecto social para análise por estado:",
        options=list(variaveis_sociais.keys()),
        format_func=lambda x: variaveis_sociais[x]["nome"],
        key="aspecto_por_estado"
    )
    
    # Verificar se a coluna existe nos dados
    if aspecto_social not in microdados_estados.columns:
        st.warning(f"A variável {variaveis_sociais[aspecto_social]['nome']} não está disponível no conjunto de dados.")
        return
    
    # Preparar dados para visualização
    with st.spinner("Preparando dados..."):
        df_por_estado = preparar_dados_grafico_aspectos_por_estado(
            microdados_estados, 
            aspecto_social, 
            estados_selecionados, 
            variaveis_sociais
        )
    
    if df_por_estado.empty:
        st.warning(f"Não há dados suficientes para mostrar a distribuição de {variaveis_sociais[aspecto_social]['nome']} por estado.")
        return
    
    # Interface para ordenação
    col1, col2 = st.columns([1, 2])
    with col1:
        ordenar_por_percentual = st.checkbox("Ordenar estados por percentual", value=False, key="ordenar_estados_percentual")
    
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
    
    # Criar uma cópia do DataFrame para não modificar o original
    df_plot = df_por_estado.copy()
    
    # Se o usuário escolheu ordenar, reorganizamos os dados
    if ordenar_por_percentual and categoria_selecionada:
        # Filtrar apenas os dados da categoria selecionada para ordenação
        percentual_por_estado = df_plot[df_plot['Categoria'] == categoria_selecionada].copy()
        
        # Criar um mapeamento da ordem dos estados com base na categoria selecionada
        ordem_estados = percentual_por_estado.sort_values('Percentual', ascending=False)['Estado'].tolist()
        
        # Reordenar o DataFrame usando o mapeamento
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        # Opcional: Filtrar para mostrar apenas a categoria selecionada
        if st.checkbox("Mostrar apenas a categoria selecionada", value=False, key="mostrar_apenas_categoria_estado"):
            df_plot = df_plot[df_plot['Categoria'] == categoria_selecionada]
    
    # Criar o gráfico
    with st.spinner("Gerando visualização..."):
        fig = criar_grafico_aspectos_por_estado(df_plot, aspecto_social, variaveis_sociais)
    
    # Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Texto explicativo
    explicacao = get_explicacao_aspectos_por_estado(variaveis_sociais[aspecto_social]['nome'])
    st.info(explicacao)
    
    # Adicionar análise estatística usando o expander encapsulado
    if categoria_selecionada:
        # Analisar a distribuição regional da categoria selecionada
        analise = analisar_distribuicao_regional(df_por_estado, aspecto_social, categoria_selecionada)
        
        # Usar o expander encapsulado para a análise regional
        criar_expander_analise_regional(df_por_estado, aspecto_social, categoria_selecionada, analise, variaveis_sociais)
    
    # Usar o expander encapsulado para dados completos
    criar_expander_dados_completos_estado(df_por_estado)