import streamlit as st
import pandas as pd
import numpy as np
from utils.tooltip import titulo_com_tooltip
from utils.helpers.cache_utils import release_memory, optimized_cache
from functools import partial

from utils.prepara_dados import (
    preparar_dados_comparativo, 
    obter_ordem_categorias,
    preparar_dados_grafico_linha,
    preparar_dados_desempenho_geral,
    filtrar_dados_scatter,
    preparar_dados_grafico_linha_desempenho
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
    analisar_desempenho_por_estado,
    calcular_estatisticas_comparativas
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

from utils.helpers.regiao_utils import obter_regiao_do_estado

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
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com dados originais
    microdados_estados : DataFrame
        DataFrame com dados filtrados por estado
    estados_selecionados : list
        Lista de estados selecionados pelo usuário
    locais_selecionados : list
        Lista de nomes de locais selecionados
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
    race_mapping : dict
        Mapeamento de códigos para raça/cor
    variaveis_categoricas : dict
        Dicionário com metadados das variáveis categóricas
    desempenho_mapping : dict
        Mapeamento de códigos para categorias de desempenho
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
    
    Parâmetros:
    -----------
    microdados_full : DataFrame
        DataFrame com dados preparados
    variaveis_categoricas : dict
        Dicionário com metadados das variáveis categóricas
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
    """
    # Verificar se temos dados de entrada válidos
    if microdados_full is None or microdados_full.empty:
        st.error("❌ Nenhum dado disponível para análise comparativa.")
        st.info("Verifique se os estados selecionados possuem dados ou tente recarregar a página.")
        return
    
    # Verificar se temos variáveis categóricas disponíveis
    if not variaveis_categoricas:
        st.error("❌ Nenhuma variável categórica disponível para análise.")
        return
    
    # Verificar se temos colunas de notas
    if not colunas_notas:
        st.error("❌ Nenhuma coluna de notas disponível para análise.")
        return
    
    # Exibir informações de debug sobre os dados
    with st.expander("🔍 Informações dos Dados", expanded=False):
        st.write(f"📊 Total de registros: {len(microdados_full):,}")
        st.write(f"📋 Colunas disponíveis: {len(microdados_full.columns)}")
        st.write(f"🏷️ Variáveis categóricas: {len(variaveis_categoricas)}")
        st.write(f"📝 Colunas de notas: {len(colunas_notas)}")
        
        # Mostrar algumas colunas para debug
        colunas_importantes = ['SG_UF_PROVA', 'TP_SEXO', 'TP_COR_RACA', 'TP_ESCOLA']
        colunas_presentes = [col for col in colunas_importantes if col in microdados_full.columns]
        if colunas_presentes:
            st.write(f"✅ Colunas importantes presentes: {colunas_presentes}")
        else:
            st.write("⚠️ Nenhuma coluna importante encontrada")
    
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

    # Verificação robusta de dados válidos
    if microdados_full is None or microdados_full.empty:
        st.warning("Não há dados suficientes para análise comparativa com os filtros aplicados.")
        return
    
    # Verificação mais robusta com feedback detalhado
    if variavel_selecionada not in microdados_full.columns:
        colunas_disponiveis = ", ".join(microdados_full.columns.tolist())
        st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} (código: {variavel_selecionada}) não está disponível no conjunto de dados.")
        st.info(f"Você pode verificar se esta variável está presente nos dados originais ou se o nome da coluna está correto no mapeamento.")
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
        
        # Verificação robusta para dados válidos
        if df_resultados is None or df_resultados.empty:
            st.error("❌ Não foi possível processar os dados para análise comparativa.")
            st.info("Possíveis causas: dados insuficientes, variável não encontrada, ou problema no processamento.")
            return
        
        # Verificar estrutura do DataFrame
        colunas_esperadas = ['Categoria', 'Competência', 'Média']
        colunas_faltantes = [col for col in colunas_esperadas if col not in df_resultados.columns]
        if colunas_faltantes:
            st.error(f"❌ Estrutura de dados incorreta. Colunas faltantes: {colunas_faltantes}")
            return
        
        st.success(f"✅ Dados processados com sucesso: {len(df_resultados)} registros encontrados")
    
    # Configuração dos filtros
    config_filtros = criar_filtros_comparativo(df_resultados, variaveis_categoricas, variavel_selecionada)
    
    # Verificar se os filtros foram criados corretamente
    if config_filtros is None:
        st.error("❌ Erro ao criar filtros de configuração.")
        return
    
    # Preparação dos dados para visualização
    competencia_para_filtro = config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None
    
    with st.spinner("Preparando dados para visualização..."):
        try:
            df_visualizacao = preparar_dados_grafico_linha(
                df_resultados, 
                config_filtros['competencia_filtro'],
                competencia_para_filtro,
                config_filtros['ordenar_decrescente']
            )
            
        except Exception as e:
            st.error(f"❌ Erro durante a preparação de dados: {str(e)}")
            st.write("Debug do erro:")
            import traceback
            st.text(traceback.format_exc())
            return
        
        # Verificar se a preparação dos dados foi bem-sucedida
        if df_visualizacao is None:
            st.error("❌ Erro na preparação de dados para visualização: função retornou None.")
            st.info("Possível causa: erro interno na função de preparação de dados.")
            return
        
        if df_visualizacao.empty:
            st.warning("⚠️ Nenhum dado disponível após aplicação dos filtros.")
            st.info("Tente ajustar os filtros ou verificar se há dados disponíveis para a combinação selecionada.")
            return
        
        st.success(f"✅ Dados de visualização preparados: {len(df_visualizacao)} registros")
    
    # Exibição do gráfico apropriado
    with st.spinner("Gerando visualização..."):
        try:
            # Verificar se temos dados válidos para criar o gráfico
            if df_visualizacao is None or df_visualizacao.empty:
                st.error("❌ Não há dados válidos para criar a visualização.")
                return
            
            # Verificar se as colunas necessárias estão presentes
            colunas_necessarias = ['Categoria', 'Competência', 'Média']
            if not all(col in df_visualizacao.columns for col in colunas_necessarias):
                st.error(f"❌ Estrutura de dados inválida. Colunas necessárias: {colunas_necessarias}")
                st.write(f"Colunas disponíveis: {list(df_visualizacao.columns)}")
                return
            
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
            
            # Verificar se o gráfico foi criado com sucesso
            if fig is None:
                st.error("❌ Erro ao criar o gráfico de visualização.")
                return
                
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar visualização: {str(e)}")
            import traceback
            st.text(traceback.format_exc())
            return
    
    # Exibição da explicação e análise detalhada
    st.info(explicacao)
    criar_expander_analise_comparativa(df_resultados, variavel_selecionada, variaveis_categoricas, competencia_mapping, config_filtros)
    
    # Liberar memória
    release_memory([df_resultados, df_visualizacao])


def render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping):
    """
    Renderiza a análise de relação entre competências usando gráfico de dispersão.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com dados filtrados por estado
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
    race_mapping : dict
        Mapeamento de códigos para raça/cor
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
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com dados filtrados por estado
    estados_selecionados : list
        Lista de estados selecionados pelo usuário
    colunas_notas : list
        Lista de colunas com notas a analisar
    competencia_mapping : dict
        Mapeamento de códigos para nomes de competências
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
        df_grafico = preparar_dados_grafico_linha_desempenho(
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
    
    # Preparação dos dados para visualização
    df_plot = preparar_dados_estados_para_visualizacao(
        df_grafico, 
        config_filtros['area_selecionada'],
        config_filtros['ordenar_por_nota'],
        config_filtros['mostrar_apenas_area']
    )
    
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
    melhor_estado = analise['melhor_estado']['Estado'] if analise['melhor_estado'] is not None else ""
    pior_estado = analise['pior_estado']['Estado'] if analise['pior_estado'] is not None else ""
    desvio_padrao = analise['desvio_padrao']
    
    # Determinar variabilidade para explicação
    variabilidade = determinar_variabilidade(desvio_padrao, config_filtros.get('mostrar_apenas_area', False))
    
    # Texto de localidade baseado no modo de visualização
    tipo_localidade = "região" if agrupar_por_regiao else "estado"
    
    # Exibição da explicação e análise detalhada
    explicacao = get_explicacao_desempenho_estados(area_texto, melhor_estado, pior_estado, variabilidade, tipo_localidade)
    st.info(explicacao)
    criar_expander_desempenho_estados(df_grafico, area_analise, analise, tipo_localidade)
    
    # Liberar memória se não é uma referência ao original
    if id(df_plot) != id(df_grafico):
        release_memory(df_plot)


def preparar_dados_estados_para_visualizacao(df_grafico, area_selecionada, ordenar_por_nota, mostrar_apenas_area):
    """
    Prepara os dados de estados/regiões para visualização, aplicando filtros e ordenação.
    
    Parâmetros:
    -----------
    df_grafico : DataFrame
        DataFrame com dados de desempenho por estado/região
    area_selecionada : str
        Área de conhecimento selecionada
    ordenar_por_nota : bool
        Indica se deve ordenar por nota
    mostrar_apenas_area : bool
        Indica se deve mostrar apenas a área selecionada
        
    Retorna:
    --------
    DataFrame: DataFrame preparado para visualização
    """
    # Otimização: evita cópia desnecessária se não precisar ordenar
    if ordenar_por_nota and area_selecionada:
        # Aplicar ordenação e filtro
        df_plot = df_grafico.copy()
        
        # Obter ordem dos estados/regiões pela área selecionada
        media_por_estado = df_plot[df_plot['Área'] == area_selecionada]
        ordem_estados = media_por_estado.sort_values('Média', ascending=False)['Estado'].tolist()
        
        # Aplicar ordenação como categoria
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        # Filtrar para mostrar apenas a área selecionada se solicitado
        if mostrar_apenas_area:
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    else:
        # Se não precisar ordenar, usa o DataFrame original sem cópia
        df_plot = df_grafico
        
        # Filtrar para mostrar apenas a área selecionada se solicitado
        if mostrar_apenas_area and area_selecionada:
            df_plot = df_plot[df_plot['Área'] == area_selecionada]
    
    return df_plot


def determinar_variabilidade(desvio_padrao, mostrar_apenas_area):
    """
    Determina a classificação de variabilidade com base no desvio padrão.
    
    Parâmetros:
    -----------
    desvio_padrao : float
        Valor do desvio padrão
    mostrar_apenas_area : bool
        Indica se está mostrando apenas uma área específica
        
    Retorna:
    --------
    str: Classificação de variabilidade
    """
    if not mostrar_apenas_area:
        return "variável"
    
    if desvio_padrao > 15:
        return "alta"
    elif desvio_padrao > 8:
        return "moderada"
    else:
        return "baixa"