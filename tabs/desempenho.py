import streamlit as st
import pandas as pd
from utils.tooltip import titulo_com_tooltip

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

def render_desempenho(microdados, microdados_estados, estados_selecionados, 
                     colunas_notas, competencia_mapping, race_mapping, 
                     variaveis_categoricas, desempenho_mapping):
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    mensagem = f"Analisando Desempenho para todo o Brasil" if len(estados_selecionados) == 27 else f"Dados filtrados para: {', '.join(estados_selecionados)}"
    st.info(mensagem)
    
    microdados_full = preparar_dados_desempenho_geral(microdados_estados, colunas_notas, desempenho_mapping)
    
    analise_selecionada = st.radio(
        "Selecione a análise desejada:",
        ["Análise Comparativa", "Relação entre Competências", "Médias por Estado"],
        horizontal=True
    )
    
    if analise_selecionada == "Análise Comparativa":
        render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping)
    elif analise_selecionada == "Relação entre Competências":
        render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping)
    else:
        render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping)


def render_analise_comparativa(microdados_full, variaveis_categoricas, colunas_notas, competencia_mapping):
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
    
    with st.spinner("Processando dados para análise comparativa..."):
        df_resultados = preparar_dados_comparativo(
            microdados_full, 
            variavel_selecionada, 
            variaveis_categoricas, 
            colunas_notas, 
            competencia_mapping
        )
        
        ordem_categorias = obter_ordem_categorias(df_resultados, variavel_selecionada, variaveis_categoricas)
    
    config_filtros = criar_filtros_comparativo(df_resultados, variaveis_categoricas, variavel_selecionada)
    
    competencia_para_filtro = config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None
    
    df_visualizacao = preparar_dados_grafico_linha(
        df_resultados, 
        config_filtros['competencia_filtro'],
        competencia_para_filtro,
        config_filtros['ordenar_decrescente']
    )
    
    with st.spinner("Gerando visualização..."):
        if config_filtros['tipo_grafico'] == "Gráfico de Barras":
            barmode = 'relative' if config_filtros['mostrar_apenas_competencia'] else 'group'
            
            fig = criar_grafico_comparativo_barras(
                df_visualizacao, 
                variavel_selecionada, 
                variaveis_categoricas, 
                competencia_mapping,
                barmode=barmode
            )
            st.plotly_chart(fig, use_container_width=True)
            
            variavel_nome = variaveis_categoricas[variavel_selecionada]['nome']
            explicacao = get_explicacao_barras_comparativo(variavel_nome)
        
        else:
            fig = criar_grafico_linha_desempenho(
                df_visualizacao, 
                variavel_selecionada, 
                variaveis_categoricas, 
                config_filtros['competencia_filtro'] if config_filtros['mostrar_apenas_competencia'] else None,
                config_filtros['ordenar_decrescente']
            )
            st.plotly_chart(fig, use_container_width=True)
            
            variavel_nome = variaveis_categoricas[variavel_selecionada]['nome']
            explicacao = get_explicacao_linhas_comparativo(variavel_nome)
    
    st.info(explicacao)
    
    with st.expander("Ver dados da análise"):
        pivot_df = df_resultados.pivot(index='Categoria', columns='Competência', values='Média').reset_index()
        st.dataframe(pivot_df, hide_index=True)


def render_relacao_competencias(microdados_estados, colunas_notas, competencia_mapping, race_mapping):
    titulo_com_tooltip(
        "Relação entre Competências", 
        get_tooltip_relacao_competencias(), 
        "relacao_competencias_tooltip"
    )
    
    config_filtros = criar_filtros_dispersao(colunas_notas, competencia_mapping)
    
    with st.spinner("Processando dados para o gráfico de dispersão..."):
        dados_filtrados, registros_removidos = filtrar_dados_scatter(
            microdados_estados, 
            config_filtros['sexo'], 
            config_filtros['tipo_escola'], 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y'], 
            config_filtros['excluir_notas_zero'], 
            race_mapping
        )
    
    if config_filtros['excluir_notas_zero'] and registros_removidos > 0:
        st.info(f"Foram desconsiderados {registros_removidos:,} registros com nota zero.")
    
    with st.spinner("Gerando visualização de dispersão..."):
        fig = criar_grafico_scatter(
            dados_filtrados, 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y'], 
            competencia_mapping
        )
        st.plotly_chart(fig, use_container_width=True)
    
    eixo_x_nome = competencia_mapping[config_filtros['eixo_x']]
    eixo_y_nome = competencia_mapping[config_filtros['eixo_y']]
    
    correlacao, _ = calcular_correlacao_competencias(
        dados_filtrados, 
        config_filtros['eixo_x'], 
        config_filtros['eixo_y']
    )
    
    explicacao = get_explicacao_dispersao(eixo_x_nome, eixo_y_nome, correlacao)
    st.info(explicacao)
    
    with st.expander("Ver estatísticas detalhadas"):
        correlacao, interpretacao = calcular_correlacao_competencias(
            dados_filtrados, 
            config_filtros['eixo_x'], 
            config_filtros['eixo_y']
        )
        
        st.write(f"**Coeficiente de correlação de Pearson:** {correlacao:.4f} ({interpretacao})")
        st.write("""
        Interpretação:
        - Próximo a 1: Forte correlação positiva (quando uma nota aumenta, a outra tende a aumentar)
        - Próximo a 0: Ausência de correlação linear
        - Próximo a -1: Forte correlação negativa (quando uma nota aumenta, a outra tende a diminuir)
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Estatísticas para {competencia_mapping[config_filtros['eixo_x']]}:**")
            stats_x = gerar_estatisticas_descritivas(dados_filtrados, config_filtros['eixo_x'])
            st.dataframe(stats_x)
            
        with col2:
            st.write(f"**Estatísticas para {competencia_mapping[config_filtros['eixo_y']]}:**")
            stats_y = gerar_estatisticas_descritivas(dados_filtrados, config_filtros['eixo_y'])
            st.dataframe(stats_y)


def render_desempenho_estados(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    titulo_com_tooltip(
        "Médias por Estado e Área de Conhecimento", 
        get_tooltip_desempenho_estados(), 
        "grafico_linha_desempenho_tooltip"
    )
    
    with st.spinner("Processando dados por estado..."):
        df_grafico = prepara_dados_grafico_linha_desempenho(
            microdados_estados, 
            estados_selecionados, 
            colunas_notas, 
            competencia_mapping
        )
    
    config_filtros = criar_filtros_estados(df_grafico)
    df_plot = df_grafico.copy()
    
    if config_filtros['ordenar_por_nota'] and config_filtros['area_selecionada']:
        media_por_estado = df_plot[df_plot['Área'] == config_filtros['area_selecionada']].copy()
        ordem_estados = media_por_estado.sort_values('Média', ascending=False)['Estado'].tolist()
        df_plot['Estado'] = pd.Categorical(df_plot['Estado'], categories=ordem_estados, ordered=True)
        df_plot = df_plot.sort_values('Estado')
        
        if config_filtros['mostrar_apenas_area']:
            df_plot = df_plot[df_plot['Área'] == config_filtros['area_selecionada']]
    
    with st.spinner("Gerando visualização por estado..."):
        fig = criar_grafico_linha_estados(
            df_plot, 
            config_filtros['area_selecionada'] if config_filtros['mostrar_apenas_area'] else None,
            config_filtros['ordenar_por_nota']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    area_texto = f" em {config_filtros['area_selecionada']}" if config_filtros.get('area_selecionada') and config_filtros.get('mostrar_apenas_area') else " nas diversas áreas de conhecimento"
    
    if config_filtros.get('area_selecionada'):
        analise = analisar_desempenho_por_estado(df_grafico, config_filtros['area_selecionada'])
        melhor_estado = analise['melhor_estado']['Estado']
        pior_estado = analise['pior_estado']['Estado']
        desvio_padrao = analise['desvio_padrao']
        variabilidade = "alta" if desvio_padrao > 15 else "moderada" if desvio_padrao > 8 else "baixa"
    else:
        analise = analisar_desempenho_por_estado(df_grafico, "Média Geral")
        melhor_estado = analise['melhor_estado']['Estado']
        pior_estado = analise['pior_estado']['Estado']
        variabilidade = "variável"
    
    explicacao = get_explicacao_desempenho_estados(area_texto, melhor_estado, pior_estado, variabilidade)
    st.info(explicacao)
    
    if config_filtros['area_selecionada']:
        with st.expander("Ver análise automática"):
            area_analise = config_filtros['area_selecionada']
            analise = analisar_desempenho_por_estado(df_grafico, area_analise)
            
            st.write(f"#### Análise de desempenho para {area_analise}")
            st.write(f"• **Melhor desempenho**: {analise['melhor_estado']['Estado']} ({analise['melhor_estado']['Média']:.1f} pontos)")
            st.write(f"• **Pior desempenho**: {analise['pior_estado']['Estado']} ({analise['pior_estado']['Média']:.1f} pontos)")
            st.write(f"• **Média nacional**: {analise['media_geral']:.1f} pontos")
            st.write(f"• **Desvio padrão entre estados**: {analise['desvio_padrao']:.2f} pontos")
    
    with st.expander("Ver dados detalhados"):
        pivot_df = df_grafico.pivot(index='Estado', columns='Área', values='Média').reset_index()
        st.dataframe(pivot_df, hide_index=True)

if __name__ == "__main__":
    st.title("Visualização de Desempenho")
    st.write("Esta é uma versão de teste da aba de desempenho.")