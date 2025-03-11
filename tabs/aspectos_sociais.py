import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_aspectos_sociais(microdados_estados, estados_selecionados, variaveis_sociais):
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
    
    # GRÁFICO: Correlação entre Aspectos Sociais
    st.markdown("### Correlação entre Aspectos Sociais")
    
    # Verificar se há estados selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
        return
    
    # Informar ao usuário quais estados estão sendo considerados
    if len(estados_selecionados) <= 5:
        st.info(f"Dados filtrados para: {', '.join(estados_selecionados)}")
    else:
        st.info(f"Filtro aplicado: {len(estados_selecionados)} estados selecionados")
    
    # Seleção do tipo de visualização
    tipo_grafico = st.radio(
        "Escolha o tipo de visualização:",
        ["Heatmap", "Barras Empilhadas", "Sankey"],
        horizontal=True
    )
    
    # Seleção das variáveis para correlação
    col1, col2 = st.columns(2)
    with col1:
        var_x = st.selectbox(
            "Variável X (Linhas/Origem):", 
            options=list(variaveis_sociais.keys()),
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="var_x_social"
        )
    with col2:
        # Filtrar para não repetir a mesma variável
        opcoes_y = [k for k in variaveis_sociais.keys() if k != var_x]
        var_y = st.selectbox(
            "Variável Y (Colunas/Destino):", 
            options=opcoes_y,
            format_func=lambda x: variaveis_sociais[x]["nome"],
            key="var_y_social"
        )
    
    # Preparar dados para visualização
    if var_x in microdados_estados.columns and var_y in microdados_estados.columns:
        # Criar colunas mapeadas para nomes legíveis
        df_correlacao = microdados_estados.copy()
        
        # Aplicar mapeamentos
        if var_x in variaveis_sociais and df_correlacao[var_x].dtype != 'object':
            df_correlacao[f'{var_x}_NOME'] = df_correlacao[var_x].map(variaveis_sociais[var_x]["mapeamento"])
            var_x_plot = f'{var_x}_NOME'
        else:
            var_x_plot = var_x
            
        if var_y in variaveis_sociais and df_correlacao[var_y].dtype != 'object':
            df_correlacao[f'{var_y}_NOME'] = df_correlacao[var_y].map(variaveis_sociais[var_y]["mapeamento"])
            var_y_plot = f'{var_y}_NOME'
        else:
            var_y_plot = var_y
        
        # Contar ocorrências para cada combinação
        contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
        
        # Calcular percentuais (normalização)
        total_por_x = df_correlacao.groupby(var_x_plot).size()
        contagem_pivot = contagem.pivot(index=var_x_plot, columns=var_y_plot, values='Contagem')
        
        # Substituir NaN por 0
        contagem_pivot = contagem_pivot.fillna(0)
        
        # Normalizar por linha (para mostrar distribuição percentual)
        normalized_pivot = contagem_pivot.div(contagem_pivot.sum(axis=1), axis=0) * 100
        
        # Texto para indicar estados no título
        estados_texto = ', '.join(estados_selecionados) if len(estados_selecionados) <= 3 else f"{len(estados_selecionados)} estados selecionados"
        
        # Criar visualização com base na escolha do usuário
        if tipo_grafico == "Heatmap":
            # Criar heatmap
            fig = px.imshow(
                normalized_pivot,
                labels=dict(
                    x=variaveis_sociais[var_y]["nome"],
                    y=variaveis_sociais[var_x]["nome"],
                    color="Percentagem (%)"
                ),
                x=normalized_pivot.columns,
                y=normalized_pivot.index,
                color_continuous_scale='YlGnBu',
                title=f"Relação entre {variaveis_sociais[var_x]['nome']} e {variaveis_sociais[var_y]['nome']} ({estados_texto})",
                text_auto='.1f'  # Mostrar valores com 1 casa decimal
            )
            
            # Ajustar layout
            fig.update_layout(
                height=500,
                xaxis={'side': 'bottom', 'tickangle': -45},
                coloraxis_colorbar=dict(title="Percentual (%)"),
                plot_bgcolor='white',
                font=dict(size=12)
            )
            
            # Texto explicativo
            explicacao = f"""
                Este heatmap mostra a distribuição percentual de {variaveis_sociais[var_y]['nome']} para cada categoria de {variaveis_sociais[var_x]['nome']}.
                As cores mais escuras indicam maior concentração percentual, e os valores mostrados são percentuais por linha.
            """
            
        elif tipo_grafico == "Barras Empilhadas":
            # Preparar dados para barras empilhadas
            df_barras = contagem.copy()
            df_barras['Percentual'] = 0.0
            
            # Calcular percentual por categoria X
            for idx, row in df_barras.iterrows():
                total = df_barras[df_barras[var_x_plot] == row[var_x_plot]]['Contagem'].sum()
                df_barras.at[idx, 'Percentual'] = (row['Contagem'] / total * 100) if total > 0 else 0
            
            # Criar gráfico de barras empilhadas
            fig = px.bar(
                df_barras,
                x=var_x_plot,
                y='Percentual',
                color=var_y_plot,
                title=f"Distribuição de {variaveis_sociais[var_y]['nome']} por {variaveis_sociais[var_x]['nome']} ({estados_texto})",
                labels={
                    var_x_plot: variaveis_sociais[var_x]['nome'],
                    'Percentual': 'Percentual (%)',
                    var_y_plot: variaveis_sociais[var_y]['nome']
                },
                text_auto='.1f',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            # Ajustar layout
            fig.update_layout(
                height=500,
                xaxis={'tickangle': -45},
                plot_bgcolor='white',
                barmode='stack',
                hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
                legend=dict(title=variaveis_sociais[var_y]['nome'], orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # Texto explicativo
            explicacao = f"""
                Este gráfico de barras empilhadas mostra a distribuição percentual de {variaveis_sociais[var_y]['nome']} 
                para cada categoria de {variaveis_sociais[var_x]['nome']}. Cada cor representa uma categoria de {variaveis_sociais[var_y]['nome']},
                e a altura da barra indica o percentual dentro de cada categoria de {variaveis_sociais[var_x]['nome']}.
            """
            
        else:  # Sankey
            # Preparar dados para Sankey
            df_sankey = contagem.copy()
            
            # Criar listas para o diagrama Sankey
            labels = list(df_sankey[var_x_plot].unique()) + list(df_sankey[var_y_plot].unique())
            
            # Mapear valores para índices
            source_indices = {val: i for i, val in enumerate(df_sankey[var_x_plot].unique())}
            target_offset = len(source_indices)
            target_indices = {val: i + target_offset for i, val in enumerate(df_sankey[var_y_plot].unique())}
            
            # Criar listas de source, target e value
            source = [source_indices[s] for s in df_sankey[var_x_plot]]
            target = [target_indices[t] for t in df_sankey[var_y_plot]]
            value = df_sankey['Contagem'].tolist()
            
            # Criar cores para nós
            node_colors = (
                px.colors.qualitative.Pastel[:len(source_indices)] + 
                px.colors.qualitative.Bold[:len(target_indices)]
            )
            
            # Criar diagrama Sankey
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color=node_colors,
                    hovertemplate='%{label}: %{value}<extra></extra>'
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    hovertemplate='%{source.label} → %{target.label}: %{value}<extra></extra>'
                )
            )])
            
            # Ajustar layout
            fig.update_layout(
                title=f"Fluxo entre {variaveis_sociais[var_x]['nome']} e {variaveis_sociais[var_y]['nome']} ({estados_texto})",
                height=600,
                font=dict(size=12)
            )
            
            # Texto explicativo
            explicacao = f"""
                Este diagrama de Sankey mostra o fluxo de registros entre as categorias de {variaveis_sociais[var_x]['nome']} (origem) e 
                {variaveis_sociais[var_y]['nome']} (destino). A largura de cada ligação representa a quantidade de registros que 
                compartilham essas características.
            """
        
        # Exibir o gráfico e explicação
        st.plotly_chart(fig, use_container_width=True)
        st.info(explicacao)
        
        # Mostrar dados brutos em um expander
        with st.expander("Ver dados da correlação"):
            # Tabela de contagem
            st.write("#### Contagem de registros")
            st.dataframe(contagem_pivot)
            
            # Tabela de percentuais
            st.write("#### Percentuais por linha")
            st.dataframe(normalized_pivot.round(2))
    else:
        st.warning(f"Uma ou ambas as variáveis selecionadas não estão disponíveis no conjunto de dados.")