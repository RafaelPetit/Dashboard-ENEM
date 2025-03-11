import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# ---------------------------- CONFIGURAÇÃO INICIAL ----------------------------
st.set_page_config(
    page_title="Dashboard ENEM",
    page_icon="📚",
    layout="wide"
)
st.title("📊 Dashboard de Análise do ENEM - 2023")
st.markdown("### Análise das notas por estado e área de conhecimento")

# ---------------------------- DEFINIÇÃO DE CONSTANTES E MAPEAMENTOS ----------------------------
# Definir colunas de notas (usado em várias partes do código)
colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

# Mapeamentos (usados em várias partes do código)
competencia_mapping = {
    'NU_NOTA_CN': 'Ciências da Natureza',
    'NU_NOTA_CH': 'Ciências Humanas',
    'NU_NOTA_LC': 'Linguagens e Códigos',
    'NU_NOTA_MT': 'Matemática',
    'NU_NOTA_REDACAO': 'Redação'
}

dependencia_escola_mapping = {
    1: 'Federal',
    2: 'Estadual',
    3: 'Municipal',
    4: 'Privada'
}

sexo_mapping = {
    'M': 'Masculino',
    'F': 'Feminino'
}

race_mapping = {
    0: 'Não declarado',
    1: 'Branca',
    2: 'Preta',
    3: 'Parda',
    4: 'Amarela',
    5: 'Indígena',
    6: 'Não dispõe da informação'
}

desempenho_mapping = {
    1: 'Desempenho Alto',
    2: 'Desempenho Médio',
    3: 'Desempenho Baixo',
}

infraestrutura_mapping = {
    1: 'Infraestrutura Alta',
    2: 'Infraestrutura Média',
    3: 'Infraestrutura Baixa',
}

faixa_etaria_mapping = {
    1: '< 17',
    2: '17',
    3: '18',
    4: '19',
    5: '20',
    6: '21',
    7: '22',
    8: '23',
    9: '24',
    10: '25',
    11: '26 < 30',
    12: '31 < 35',
    13: '36 < 40',
    14: '41 < 45',
    15: '46 < 50',
    16: '51 < 55',
    17: '56 < 60',
    18: '61 < 65',
    19: '66 < 70',
    20: '> 70'
}

escolaridade_pai_mae_mapping = {
    'A': 'Nunca estudou',
    'B': 'Fundamental incompleto',
    'C': 'Fundamental completo',
    'D': 'Médio incompleto',
    'E': 'Médio Completo',
    'F': 'Superior Completo',    
    'G': 'Pós-graduação Completo',
    'H': 'Não sei'
}

variaveis_categoricas = {
    "TP_COR_RACA": {
        "nome": "Raça/Cor",
        "mapeamento": race_mapping,
        "ordem": list(race_mapping.values())
    },
    "TP_SEXO": {
        "nome": "Sexo", 
        "mapeamento": sexo_mapping,
        "ordem": list(sexo_mapping.values())
    },
    "TP_DEPENDENCIA_ADM_ESC": {
        "nome": "Dependência Administrativa", 
        "mapeamento": dependencia_escola_mapping,
        "ordem": list(dependencia_escola_mapping.values())
    },
    "Q001": {
        "nome": "Escolaridade do Pai", 
        "mapeamento": escolaridade_pai_mae_mapping,
        "ordem": list(escolaridade_pai_mae_mapping.values())
    },
    "Q002": {
        "nome": "Escolaridade da Mãe", 
        "mapeamento": escolaridade_pai_mae_mapping,
        "ordem": list(escolaridade_pai_mae_mapping.values())
    },
    "TP_FAIXA_ETARIA": {
        "nome": "Faixa Etária", 
        "mapeamento": faixa_etaria_mapping,
        "ordem": list(faixa_etaria_mapping.values())
    }
}

# ---------------------------- FUNÇÕES DE UTILIDADE ----------------------------
def calcular_seguro(serie_dados, operacao='media'):
    """
    Calcula estatísticas de forma segura, lidando com valores missing ou inválidos.
    """
    try:
        if len(serie_dados) == 0:
            return 0.0
        array_dados = np.array(serie_dados, dtype=np.float64)
        array_limpa = array_dados[np.isfinite(array_dados)]
        if len(array_limpa) == 0:
            return 0.0
        if operacao == 'media':
            resultado = np.mean(array_limpa)
        elif operacao == 'mediana':
            resultado = np.median(array_limpa)
        elif operacao == 'min':
            resultado = np.min(array_limpa)
        elif operacao == 'max':
            resultado = np.max(array_limpa)
        else:
            return 0.0
        return float(resultado) if np.isfinite(resultado) else 0.0
    except Exception as e:
        print(f"Erro no cálculo: {e}")
        return 0.0

# ---------------------------- CARREGAMENTO DE DADOS ----------------------------
@st.cache_data
def load_data():
    microdados = pd.DataFrame(pd.read_csv('sample.csv', sep=';', encoding='ISO-8859-1'))
    dtypes = pd.read_json("dtypes.json", typ='series')
    dados = microdados.astype(dtypes)
    # Converter todas as colunas de notas para float64
    for col in colunas_notas:
        dados[col] = dados[col].astype('float64')
    return dados

# Carregar dados uma única vez
microdados = load_data()

# ---------------------------- FILTROS E CONTROLES ----------------------------
st.sidebar.header("Filtros")

# Obter lista de todos os estados disponíveis
todos_estados = sorted(microdados['SG_UF_PROVA'].unique())

# Adicionar checkbox para selecionar todo o Brasil
selecionar_brasil = st.sidebar.checkbox("Brasil (todos os estados)", value=True)

# Condicionar o multiselect ao estado do checkbox
if selecionar_brasil:
    estados_selecionados = todos_estados
    # Mostrar o multiselect como desativado para indicar a seleção automática
    st.sidebar.multiselect(
        "Estados selecionados:",
        options=todos_estados,
        default=todos_estados,
        disabled=True
    )
else:
    # Permitir seleção manual quando "Brasil" não estiver selecionado
    estados_selecionados = st.sidebar.multiselect(
        "Selecione os Estados:",
        options=todos_estados,
        default=[]
    )
    # Verificar se pelo menos um estado foi selecionado
    if not estados_selecionados:
        st.sidebar.warning("Selecione pelo menos um estado ou marque a opção Brasil.")

# ---------------------------- PROCESSAMENTO DE DADOS ----------------------------
# 1. Preparação de dados para a Aba Geral (Estados)
if estados_selecionados:
    microdados_estados = microdados[microdados['SG_UF_PROVA'].isin(estados_selecionados)].copy()
    
    # Calcular médias por estado
    media_por_estado = []
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        for col in colunas_notas:
            media = calcular_seguro(dados_estado[col])
            media_por_estado.append(media)
    
    # Métricas gerais
    media_geral = np.mean(media_por_estado) if media_por_estado else 0.0
    maior_media = np.max(media_por_estado) if media_por_estado else 0.0
    
    # Dados para gráfico de linhas
    dados_grafico = []
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        for area in colunas_notas:
            media_area = round(calcular_seguro(dados_estado[area]), 2)
            dados_grafico.append({
                'Estado': estado,
                'Área': competencia_mapping[area],
                'Média': media_area
            })
    df_grafico = pd.DataFrame(dados_grafico)
else:
    microdados_estados = pd.DataFrame(columns=microdados.columns)
    media_geral = 0.0
    maior_media = 0.0
    df_grafico = pd.DataFrame(columns=['Estado', 'Área', 'Média'])

# 2. Preparação de dados para a Aba Infraestrutura
microdados_full = microdados.copy()

# Dados para Infraestrutura por Raça
infra_desempenho = microdados_full.groupby(['TP_COR_RACA', 'NU_INFRAESTRUTURA']).size().reset_index(name='count')
raca_total = microdados_full.groupby('TP_COR_RACA').size().reset_index(name='total')
infra_desempenho = infra_desempenho.merge(raca_total, on='TP_COR_RACA')
infra_desempenho['percentual'] = (infra_desempenho['count'] / infra_desempenho['total']) * 100
infra_desempenho['Raça'] = infra_desempenho['TP_COR_RACA'].map(race_mapping)
infra_desempenho['infraestrutura'] = infra_desempenho['NU_INFRAESTRUTURA'].map(infraestrutura_mapping)

# 3. Preparação de dados para a Aba Desempenho
# 3.1 Dados para Desempenho por Raça
microdados_full['TP_COR_RACA'] = microdados_full['TP_COR_RACA'].astype('category')
microdados_full['NU_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].astype(int)
microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].map(desempenho_mapping)

raca_desempenho = microdados_full.groupby(['TP_COR_RACA', 'CATEGORIA_DESEMPENHO']).size().reset_index(name='count')
raca_total = microdados_full.groupby('TP_COR_RACA').size().reset_index(name='total')
raca_desempenho = raca_desempenho.merge(raca_total, on='TP_COR_RACA')
raca_desempenho['percentual'] = (raca_desempenho['count'] / raca_desempenho['total']) * 100
raca_desempenho['Raça'] = raca_desempenho['TP_COR_RACA'].map(race_mapping)

# 3.2 Pré-processamento para grafico comparativo (calculado durante a renderização)
# 3.3 Pré-processamento para scatter plot (calculado durante a renderização)

# ---------------------------- VISUALIZAÇÃO (ABAS E GRÁFICOS) ----------------------------
abas = st.tabs(["Geral", "Aspectos Sociais", "Desempenho"])

# ---------------------- ABA 1: GERAL (ESTADOS) ----------------------
with abas[0]:
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
    else:
        # Métricas Principais
        st.subheader("Métricas Principais")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Média Geral", f"{round(media_geral, 2)}")
        with col2:
            st.metric("Total de Candidatos", f"{microdados_estados.shape[0]:,}")
        with col3:
            st.metric("Maior Média", f"{round(maior_media, 2)}")
        
        # Histograma e Linha
        st.markdown("### Distribuição das Notas")
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
        
        col1_hist, col2_hist = st.columns(2)
        with col1_hist:
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
        
        with col1_hist:
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
                    hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
                )
                st.plotly_chart(fig_linha, use_container_width=True)

        # Dados Detalhados
        with st.expander("Ver dados detalhados"):  
            st.dataframe(
                microdados_estados,
                column_config={
                    "SG_UF_PROVA": "Estado",
                    "NU_NOTA_CN": "Ciências da Natureza",
                    "NU_NOTA_CH": "Ciências Humanas",
                    "NU_NOTA_LC": "Linguagens e Códigos",
                    "NU_NOTA_MT": "Matemática",
                    "NU_NOTA_REDACAO": "Redação"
                }, 
                hide_index=True
            )
            st.info(f"""
                A distribuição mostra a frequência das notas em {nome_area}.
                A média é {media:.2f} e a mediana {mediana:.2f}, o que indica que
                {'a distribuição tem um viés positivo' if media > mediana else 'a distribuição tem um viés negativo' if media < mediana else 'a distribuição é aproximadamente simétrica'}.
            """)

# ---------------------- ABA 2: Aspectos Sociais ----------------------
# ---------------------- ABA 2: Aspectos Sociais ----------------------
with abas[1]:
    # GRÁFICO: Correlação entre Aspectos Sociais
    st.markdown("### Correlação entre Aspectos Sociais")

    variaveis_sociais = {
    # Variáveis já existentes
    "TP_COR_RACA": {"nome": "Raça/Cor", "mapeamento": race_mapping},
    "TP_SEXO": {"nome": "Sexo", "mapeamento": sexo_mapping},
    "TP_DEPENDENCIA_ADM_ESC": {"nome": "Tipo de Escola", "mapeamento": dependencia_escola_mapping},
    "TP_FAIXA_ETARIA": {"nome": "Faixa Etária", "mapeamento": faixa_etaria_mapping},
    "Q001": {"nome": "Escolaridade do Pai", "mapeamento": escolaridade_pai_mae_mapping},
    "Q002": {"nome": "Escolaridade da Mãe", "mapeamento": escolaridade_pai_mae_mapping},
    
    # Novas variáveis recomendadas
    "Q006": {"nome": "Renda Familiar", "mapeamento": {
        "A": "Nenhuma Renda",
        "B": "Até R$ 1.320,00",
        "C": "De R$ 1.320,01 até R$ 1.980,00",
        "D": "De R$ 1.980,01 até R$ 2.640,00",
        "E": "De R$ 2.640,01 até R$ 3.300,00",
        "F": "De R$ 3.300,01 até R$ 3.960,00",
        "G": "De R$ 3.960,01 até R$ 5.280,00",
        "H": "De R$ 5.280,01 até R$ 6.600,00",
        "I": "De R$ 6.600,01 até R$ 7.920,00",
        "J": "De R$ 7.920,01 até R$ 9240,00",
        "K": "De R$ 9.240,01 até R$ 10.560,00",
        "L": "De R$ 10.560,01 até R$ 11.880,00",
        "M": "De R$ 11.880,01 até R$ 13.200,00",
        "N": "De R$ 13.200,01 até R$ 15.840,00",
        "O": "De R$ 15.840,01 até R$19.800,00",
        "P": "De R$ 19.800,01 até R$ 26.400,00",
        "Q": "Acima de R$ 26.400,00"
    }},
    "Q005": {"nome": "Pessoas na Residência", "mapeamento": {
        str(i): str(i) for i in range(1, 21)
    }},
    "TP_ESCOLA": {"nome": "Instituição", "mapeamento": {
        1: "Não Respondeu",
        2: "Pública",
        3: "Privada"
    }},
    "TP_ST_CONCLUSAO": {"nome": "Situação do Ensino Médio", "mapeamento": {
        1: "Já concluí o Ensino Médio",
        2: "Concluirei em 2023",
        3: "Concluirei após 2023",
        4: "Não concluí/não estou cursando"
    }},
    "NU_INFRAESTRUTURA": {"nome": "Nível de Infraestrutura", "mapeamento": infraestrutura_mapping}
}
    
    # Verificar se há estados selecionados
    if not estados_selecionados:
        st.warning("Selecione pelo menos um estado no filtro lateral para visualizar os dados.")
    else:
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
        
        # Preparar dados para visualização - USAR MICRODADOS_ESTADOS em vez de MICRODADOS_FULL
        if var_x in microdados_estados.columns and var_y in microdados_estados.columns:
            # Criar colunas mapeadas para nomes legíveis
            df_correlacao = microdados_estados.copy()  # MUDANÇA AQUI - usar dados filtrados por estado
            
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
# ---------------------- ABA 3: DESEMPENHO ----------------------
with abas[2]:
     # Verificação da distribuição de desempenho
    st.markdown("### Desempenho por Raça")
    fig_raca = px.bar(
        raca_desempenho, 
        x='Raça', 
        y='percentual', 
        color='CATEGORIA_DESEMPENHO',
        title='Distribuição de Desempenho por Raça', 
        labels={'percentual': 'Percentual (%)', 'Raça': 'Raça/Cor', 'CATEGORIA_DESEMPENHO': 'Desempenho'},
        category_orders={
        'CATEGORIA_DESEMPENHO': ['Desempenho Alto', 'Desempenho Médio', 'Desempenho Baixo']
        },
        color_discrete_map={'Desempenho Alto': '#99CC99', 
                            'Desempenho Médio': '#FFCC99', 
                            'Desempenho Baixo': '#FF9999'
        }
    )
    fig_raca.update_layout(
        height=400,
        bargap=0.2,
        barmode='group',
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        xaxis=dict(tickangle=-45)
    )
    st.plotly_chart(fig_raca, use_container_width=True)

    # GRAFICO 2: Análise Comparativa por Variáveis Demográficas
    st.markdown("### Análise Comparativa do Desempenho por  Variáveis Demográficas")
    
    # Seleção da variável
    variavel_selecionada = st.selectbox(
        "Selecione a variável para análise:",
        options=list(variaveis_categoricas.keys()),
        format_func=lambda x: variaveis_categoricas[x]["nome"]
    )

    # Preparação dos dados
    if variavel_selecionada in microdados_full.columns:
        # Criar uma coluna com os valores mapeados
        nome_coluna_mapeada = f"{variavel_selecionada}_NOME"
        microdados_full[nome_coluna_mapeada] = microdados_full[variavel_selecionada].map(
            variaveis_categoricas[variavel_selecionada]["mapeamento"]
        )
        
        # Calcular médias por categoria
        resultados = []
        for categoria in microdados_full[nome_coluna_mapeada].unique():
            dados_categoria = microdados_full[microdados_full[nome_coluna_mapeada] == categoria]
            for competencia in colunas_notas:
                media_comp = calcular_seguro(dados_categoria[competencia])
                resultados.append({
                    'Categoria': categoria,
                    'Competência': competencia_mapping[competencia],
                    'Média': round(media_comp, 2)
                })
        
        # Criar DataFrame para visualização
        df_resultados = pd.DataFrame(resultados)
        
        # Visualização do gráfico de barras
        fig = px.bar(
            df_resultados,
            x='Categoria',
            y='Média',
            color='Competência',
            title=f"Desempenho por {variaveis_categoricas[variavel_selecionada]['nome']}",
            labels={
                'Categoria': variaveis_categoricas[variavel_selecionada]['nome'],
                'Média': 'Nota Média',
                'Competência': 'Área de Conhecimento'
            },
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Bold,
            category_orders={
                'Categoria': variaveis_categoricas[variavel_selecionada]['ordem'],
                'Competência': list(competencia_mapping.values())
            }
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            plot_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Dados detalhados
        with st.expander("Ver dados da análise"):
            st.dataframe(
                df_resultados.pivot(index='Categoria', columns='Competência', values='Média').reset_index(),
                hide_index=True
            )
    else:
        st.warning(f"A variável {variaveis_categoricas[variavel_selecionada]['nome']} não está disponível no conjunto de dados.")

    # GRAFICO 3: Gráfico de Dispersão (Scatter Plot)
    st.markdown("### Relação entre Competências")
    col1, col2 = st.columns(2)
    
    # Controles de seleção
    with col1:
        eixo_x = st.selectbox("Eixo X:", options=colunas_notas, format_func=lambda x: competencia_mapping[x], placeholder="Selecione uma competência")
    with col2:
        eixo_y = st.selectbox("Eixo Y:", options=colunas_notas, format_func=lambda x: competencia_mapping[x], placeholder="Selecione uma competência")

    # Filtros adicionais
    with col1:
        sexo = st.selectbox("Sexo:", options=["Todos", "M", "F"])
    with col2:
        tipo_escola = st.selectbox("Tipo de Escola:", options=["Todos", "Federal", "Estadual", "Municipal", "Privada"])

    # Preparação dos dados filtrados
    dados_filtrados = microdados.copy()
    if sexo != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['TP_SEXO'] == sexo]
    if tipo_escola != "Todos":
        tipo_map = {"Federal": 1, "Estadual": 2, "Municipal": 3, "Privada": 4}
        dados_filtrados = dados_filtrados[dados_filtrados['TP_DEPENDENCIA_ADM_ESC'] == tipo_map[tipo_escola]]

    # Aplicar mapeamento para raça/cor
    dados_filtrados['RACA_COR'] = dados_filtrados['TP_COR_RACA'].map(race_mapping)

    # Visualização do gráfico de dispersão
    fig = px.scatter(
        dados_filtrados, 
        x=eixo_x, 
        y=eixo_y,
        title=f"Relação entre {competencia_mapping[eixo_x]} e {competencia_mapping[eixo_y]}",
        labels={
            eixo_x: competencia_mapping[eixo_x], 
            eixo_y: competencia_mapping[eixo_y],
            'RACA_COR': 'COR/RAÇA'
        },
        opacity=0.5,
        color="RACA_COR",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    st.plotly_chart(fig, use_container_width=True)