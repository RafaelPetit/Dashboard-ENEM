import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff

def criar_expander_analise_histograma(df, coluna, nome_area, estatisticas):
    """
    Cria um expander com análise detalhada da distribuição de notas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    coluna : str
        Nome da coluna (área de conhecimento) a ser analisada
    nome_area : str
        Nome formatado da área de conhecimento
    estatisticas : dict
        Dicionário com estatísticas calculadas
    """
    with st.expander("Ver análise estatística detalhada"):
        # Título principal
        st.write(f"### Análise de distribuição de notas em {nome_area}")
        
        # Bloco de estatísticas principais
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Estatísticas descritivas")
            st.write(f"- **Candidatos com notas válidas:** {estatisticas['total_valido']:,}")
            st.write(f"- **Candidatos sem nota:** {estatisticas['total_invalido']:,}")
            st.write(f"- **Média:** {estatisticas['media']:.2f}")
            st.write(f"- **Mediana:** {estatisticas['mediana']:.2f}")
            st.write(f"- **Desvio padrão:** {estatisticas['desvio_padrao']:.2f}")
            st.write(f"- **Assimetria:** {estatisticas['assimetria']:.2f}")
            st.write(f"- **Curtose:** {estatisticas['curtose']:.2f}")
            st.write(f"- **Mínimo:** {estatisticas['min_valor']:.2f}")
            st.write(f"- **Máximo:** {estatisticas['max_valor']:.2f}")
        
        with col2:
            st.write("#### Distribuição por percentis")
            for p, valor in estatisticas['percentis'].items():
                st.write(f"- **Percentil {p}:** {valor:.2f}")
        
        # Análise contextual
        st.write("#### Interpretação educacional")
        
        # Parágrafos de análise com base nas estatísticas
        if estatisticas['assimetria'] > 0.5:
            st.write("""
            **Distribuição com assimetria positiva:** A cauda direita mais longa indica que a maioria dos candidatos 
            obteve notas abaixo da média, enquanto poucos conseguiram alcançar pontuações muito altas. 
            Este padrão pode refletir:
            
            - Conteúdo particularmente desafiador para a maioria dos estudantes
            - Possível lacuna no ensino destes temas no ensino médio regular
            - Necessidade de revisão das metodologias de ensino nesta área
            """)
        elif estatisticas['assimetria'] < -0.5:
            st.write("""
            **Distribuição com assimetria negativa:** A cauda esquerda mais longa sugere que a maioria dos candidatos 
            conseguiu notas acima da média, com poucos ficando com pontuações muito baixas. 
            Este padrão pode indicar:
            
            - Conteúdo bem trabalhado no ensino médio
            - Metodologias de ensino eficazes nesta área
            - Possível facilidade relativa desta prova específica
            """)
        else:
            st.write("""
            **Distribuição aproximadamente simétrica:** A distribuição de notas é relativamente equilibrada em torno da média. 
            Este padrão sugere:
            
            - Equilíbrio entre facilidade e dificuldade na prova
            - Eficácia moderada do ensino nesta área
            - Diversidade balanceada de habilidades entre os candidatos
            """)
            
        if estatisticas['curtose'] > 0.5:
            st.write("""
            **Alta concentração em torno da média (leptocúrtica):** O pico pronunciado indica muitos candidatos com notas 
            próximas à média e poucas notas extremas. Isto pode refletir:
            
            - Homogeneidade na formação educacional para esta área
            - Consistência no nível de preparação dos candidatos
            - Avaliação eficaz em diferenciar candidatos em um range médio
            """)
        elif estatisticas['curtose'] < -0.5:
            st.write("""
            **Distribuição mais plana (platicúrtica):** A distribuição achatada indica maior variabilidade, 
            com menos concentração em torno da média. Isto pode sugerir:
            
            - Grande heterogeneidade na formação educacional
            - Desigualdade significativa no acesso a ensino de qualidade nesta área
            - Avaliação que cobre amplo espectro de dificuldades
            """)


def criar_expander_analise_faltas(df_faltas, analise):
    """
    Cria um expander com análise detalhada das faltas.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame com os dados de faltas
    analise : dict
        Dicionário com métricas de análise
    """
    with st.expander("Ver análise detalhada de ausências"):
        # Título principal
        st.write("### Análise detalhada do padrão de faltas")
        
        # Bloco de métricas principais
        st.write(f"- **Taxa média geral de faltas:** {analise['taxa_media_geral']:.2f}%")
        
        if analise['estado_maior_falta'] is not None:
            st.write(f"- **Estado com maior taxa de faltas nos dois dias:** {analise['estado_maior_falta']['Estado']} ({analise['estado_maior_falta']['Percentual de Faltas']:.2f}%)")
        
        if analise['estado_menor_falta'] is not None:
            st.write(f"- **Estado com menor taxa de faltas nos dois dias:** {analise['estado_menor_falta']['Estado']} ({analise['estado_menor_falta']['Percentual de Faltas']:.2f}%)")
        
        # Análise por tipo de falta
        st.write("#### Comparativo entre tipos de falta")
        
        # Criar dataframe para o gráfico
        medias_por_tipo = analise['medias_por_tipo']
        
        fig_tipos = px.bar(
            medias_por_tipo,
            x='Tipo de Falta',
            y='Percentual de Faltas',
            text_auto='.1f',
            title="Taxa média de faltas por tipo",
            labels={'Percentual de Faltas': '% de Faltas', 'Tipo de Falta': 'Padrão de Ausência'},
            color_discrete_sequence=['#3366CC']
        )
        
        fig_tipos.update_layout(
            yaxis=dict(ticksuffix='%'),
            xaxis_title="Padrão de Ausência",
            yaxis_title="Taxa média de faltas (%)",
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_tipos, use_container_width=True)
        
        # Análise por dia de prova
        st.write("#### Comparativo entre dias de prova")
        
        # Criar dataframe para comparação entre dias
        dias_df = pd.DataFrame({
            'Dia de Prova': ['Primeiro dia apenas', 'Segundo dia apenas', 'Ambos os dias'],
            'Taxa média de faltas (%)': [analise['media_faltas_dia1'], analise['media_faltas_dia2'], analise['media_faltas_ambos_dias']]
        })
        
        fig_dias = px.bar(
            dias_df,
            x='Dia de Prova',
            y='Taxa média de faltas (%)',
            text_auto='.1f',
            title="Comparativo de faltas entre dias de prova",
            color_discrete_sequence=['#7D3C98', '#2471A3', '#CB4335']
        )
        
        fig_dias.update_layout(
            yaxis=dict(ticksuffix='%'),
            xaxis_title="Padrão de Ausência",
            yaxis_title="Taxa média de faltas (%)",
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_dias, use_container_width=True)
        
        # Análise da variabilidade regional
        st.write("#### Análise da variabilidade regional")
        st.write(f"- **Desvio padrão entre estados:** {analise['desvio_padrao_faltas']:.2f} pontos percentuais")
        st.write(f"- **Avaliação da variabilidade:** {analise['variabilidade']}")
        
        # Diferença entre dias
        if abs(analise['diferenca_dias']) < 0.5:
            st.write("- **Padrão de dias:** Taxa de faltas semelhante entre primeiro e segundo dia de prova")
        elif analise['diferenca_dias'] > 0:
            st.write(f"- **Padrão de dias:** Taxa de faltas maior no segundo dia (diferença de {analise['diferenca_dias']:.2f} pontos percentuais)")
        else:
            st.write(f"- **Padrão de dias:** Taxa de faltas maior no primeiro dia (diferença de {abs(analise['diferenca_dias']):.2f} pontos percentuais)")
        
        # Análise das causas potenciais
        st.write("#### Fatores potenciais para ausências")
        st.write("""
        As ausências em exames nacionais como o ENEM podem ser atribuídas a diversos fatores:
        
        1. **Fatores associados a faltar nos dois dias:**
           - Inscrição apenas para obter certificado de conclusão do Ensino Médio (necessita apenas da inscrição)
           - Impossibilidade de comparecer em ambos os dias (trabalho, saúde, etc.)
           - Inscrição para reservar a possibilidade de fazer a prova, mas desistência posterior
        
        2. **Fatores associados a faltar apenas no primeiro dia:**
           - Interesse específico apenas nas provas de Ciências da Natureza e Matemática
           - Problemas logísticos específicos do primeiro fim de semana
           - Estratégia focada em cursos que priorizam as provas do segundo dia
        
        3. **Fatores associados a faltar apenas no segundo dia:**
           - Percepção de dificuldade após o primeiro dia, levando à desistência
           - Interesse específico apenas nas provas de Ciências Humanas, Linguagens e Redação
           - Problemas logísticos específicos do segundo fim de semana
        """)