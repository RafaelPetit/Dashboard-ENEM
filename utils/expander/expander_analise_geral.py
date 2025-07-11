import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Tuple
from utils.helpers.regiao_utils import obter_regiao_do_estado
from utils.estatisticas.estatistica_analise_geral import (
    analisar_desempenho_por_faixa_nota,
    analisar_metricas_por_regiao
)
from utils.explicacao.explicacao_geral import (
    get_interpretacao_distribuicao
)
from utils.helpers.mappings import get_mappings

# Obter mapeamentos e constantes
mappings = get_mappings()
LIMIARES_ESTATISTICOS = mappings.get('limiares_estatisticos', {})
CONFIG_VISUALIZACAO = mappings.get('config_visualizacao', {})

def criar_expander_analise_histograma(
    df: pd.DataFrame, 
    coluna: str, 
    nome_area: str, 
    estatisticas: Dict[str, Any]
) -> None:
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
        try:
            # Título principal
            st.write(f"### Análise de distribuição de notas em {nome_area}")
            
            # Verificar se temos estatísticas válidas
            if not estatisticas or estatisticas.get('total_valido', 0) == 0:
                st.warning(f"Dados insuficientes para análise detalhada de {nome_area}.")
                return
            
            # Layout em colunas para melhor organização
            col1, col2 = st.columns(2)
            
            # Coluna 1: Estatísticas descritivas
            with col1:
                _mostrar_estatisticas_descritivas(estatisticas)
            
            # Coluna 2: Distribuição por percentis
            with col2:
                _mostrar_percentis_detalhados(estatisticas)
            
            # Análise avançada da distribuição
            st.write("#### Análise detalhada da distribuição")
            interpretacao = get_interpretacao_distribuicao(
                estatisticas.get('assimetria', 0),
                estatisticas.get('curtose', 0),
                estatisticas.get('media', 0),
                estatisticas.get('desvio_padrao', 0)
            )
            st.write(interpretacao)
            
            # Mostrar faixas de desempenho
            _mostrar_grafico_faixas_desempenho(estatisticas)
            
            # Análise comparativa de conceitos
            _mostrar_grafico_conceitos(estatisticas, nome_area)
            
        except Exception as e:
            st.error(f"Erro ao gerar análise detalhada: {str(e)}")


def criar_expander_analise_faltas(
    df_faltas: pd.DataFrame, 
    analise: Dict[str, Any]
) -> None:
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
        try:
            # Verificar se temos dados válidos para análise
            if analise is None or df_faltas is None or df_faltas.empty:
                st.warning("Dados insuficientes para análise detalhada de ausências.")
                return
                
            # Título principal
            st.write("### Análise detalhada do padrão de faltas")
            
            # Bloco de métricas principais
            _mostrar_metricas_principais_faltas(analise)
            
            # Análise por tipo de falta
            st.write("#### Comparativo entre tipos de falta")
            _criar_grafico_tipos_falta(analise.get('medias_por_tipo'))
            
            # Análise por dia de prova
            st.write("#### Comparativo entre dias de prova")
            _criar_grafico_dias_prova(analise)
            
            # Análise da variabilidade regional
            _mostrar_analise_variabilidade_faltas(analise)
            
            # Análise dos estados com maior e menor evasão
            _mostrar_estados_extremos_evasao(analise)
            
            # Mapa de calor de faltas por região
            _criar_mapa_calor_faltas(df_faltas)
            
            # Análise das causas potenciais
            _mostrar_causas_potenciais_faltas()
            
        except Exception as e:
            st.error(f"Erro ao gerar análise detalhada de faltas: {str(e)}")


def criar_expander_analise_faixas_desempenho(
    df: pd.DataFrame, 
    coluna: str, 
    nome_area: str
) -> None:
    """
    Cria um expander com análise detalhada por faixas de desempenho.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    coluna : str
        Nome da coluna (área de conhecimento) a ser analisada
    nome_area : str
        Nome formatado da área de conhecimento
    """
    with st.expander("Ver análise por faixas de desempenho"):
        try:
            # Verificar se temos dados válidos
            if df is None or df.empty or coluna not in df.columns:
                st.warning(f"Dados insuficientes para análise por faixas de desempenho em {nome_area}.")
                return
                
            # Filtrar para notas válidas
            df_valido = df[df[coluna] > 0].copy()
            
            if df_valido.empty:
                st.warning(f"Não foram encontradas notas válidas para análise em {nome_area}.")
                return
                
            # Título principal
            st.write(f"### Análise por faixas de desempenho em {nome_area}")
            
            # Analisar desempenho por faixas
            analise_faixas = analisar_desempenho_por_faixa_nota(df_valido, coluna)
            
            # Mostrar estatísticas por faixa
            _mostrar_estatisticas_por_faixa(analise_faixas)
            
            # Criar gráfico comparativo entre faixas
            _criar_grafico_comparativo_faixas(analise_faixas)
            
            # Análise da faixa predominante
            _mostrar_analise_faixa_predominante(analise_faixas)
            
            # Análise de implicações educacionais
            _mostrar_implicacoes_educacionais_faixas(analise_faixas, nome_area)
            
        except Exception as e:
            st.error(f"Erro ao gerar análise por faixas de desempenho: {str(e)}")


def criar_expander_analise_regional(
    df: pd.DataFrame, 
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str]
) -> None:
    """
    Cria um expander com análise detalhada do desempenho por região.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    colunas_notas : List[str]
        Lista de colunas com notas para análise
    competencia_mapping : Dict[str, str]
        Mapeamento entre códigos de competência e nomes legíveis
    """
    with st.expander("Ver análise por região"):
        try:
            # Verificar se temos dados válidos
            if df is None or df.empty or 'SG_UF_PROVA' not in df.columns:
                st.warning("Dados insuficientes para análise regional.")
                return
                
            # Título principal
            st.write("### Análise de desempenho por região do país")
            
            # Obter métricas por região
            metricas_regiao = analisar_metricas_por_regiao(df, colunas_notas)
            
            if not metricas_regiao:
                st.warning("Não foi possível calcular métricas por região.")
                return
                
            # Layout em abas para cada tipo de análise
            tab1, tab2, tab3 = st.tabs(["Médias por competência", "Comparativo entre regiões", "Mapa de desempenho"])
            
            # Aba 1: Médias por competência e região
            with tab1:
                _mostrar_medias_competencia_regiao(metricas_regiao, competencia_mapping)
            
            # Aba 2: Comparativo entre regiões
            with tab2:
                _criar_grafico_comparativo_regioes(metricas_regiao)
            
            # Aba 3: Mapa de desempenho (heatmap)
            with tab3:
                _criar_mapa_calor_regioes(metricas_regiao, competencia_mapping)
                
            # Análise das disparidades regionais
            st.write("#### Análise das disparidades regionais")
            _mostrar_analise_disparidades_regionais(metricas_regiao)
            
        except Exception as e:
            st.error(f"Erro ao gerar análise regional: {str(e)}")


def criar_expander_analise_comparativo_areas(
    df_areas: pd.DataFrame
) -> None:
    """
    Cria um expander com análise detalhada do comparativo entre áreas.
    
    Parâmetros:
    -----------
    df_areas : DataFrame
        DataFrame com dados comparativos entre áreas
    """
    with st.expander("Ver análise comparativa entre áreas"):
        try:
            # Verificar se temos dados válidos
            if df_areas is None or df_areas.empty:
                st.warning("Dados insuficientes para análise comparativa entre áreas.")
                return
                
            # Verificar estrutura necessária
            colunas_necessarias = ['Area', 'Media', 'DesvioPadrao']
            if not all(col in df_areas.columns for col in colunas_necessarias):
                st.warning("Estrutura de dados incorreta para análise comparativa entre áreas.")
                return
                
            # Título principal
            st.write("### Análise comparativa entre áreas de conhecimento")
            
            # Identificar áreas com melhor e pior desempenho
            melhor_area, pior_area = _identificar_areas_extremas(df_areas)
            
            # Mostrar resumo comparativo
            _mostrar_resumo_comparativo_areas(df_areas, melhor_area, pior_area)
            
            # Análise de correlação entre dificuldades das áreas
            _mostrar_analise_dificuldade_relativa(df_areas)
            
            # Mostrar tabela completa de dados
            with st.expander("Ver dados completos"):
                st.dataframe(
                    df_areas,
                    column_config={
                        "Media": st.column_config.NumberColumn("Média", format="%.2f"),
                        "DesvioPadrao": st.column_config.NumberColumn("Desvio Padrão", format="%.2f"),
                        "Mediana": st.column_config.NumberColumn("Mediana", format="%.2f"),
                        "Minimo": st.column_config.NumberColumn("Mínimo", format="%.2f") if "Minimo" in df_areas else None,
                        "Maximo": st.column_config.NumberColumn("Máximo", format="%.2f") if "Maximo" in df_areas else None
                    }
                )
                
        except Exception as e:
            st.error(f"Erro ao gerar análise comparativa entre áreas: {str(e)}")


# Funções auxiliares para análise de histograma

def _mostrar_estatisticas_descritivas(estatisticas: Dict[str, Any]) -> None:
    """
    Mostra as estatísticas descritivas básicas no expander.
    
    Parâmetros:
    -----------
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
    """
    st.write("#### Estatísticas descritivas")
    
    # Estatísticas básicas sobre candidatos
    st.write(f"- **Candidatos com notas válidas:** {estatisticas.get('total_valido', 0):,}")
    st.write(f"- **Candidatos sem nota:** {estatisticas.get('total_invalido', 0):,}")
    
    # Estatísticas de tendência central
    st.write(f"- **Média:** {estatisticas.get('media', 0):.2f}")
    st.write(f"- **Mediana:** {estatisticas.get('mediana', 0):.2f}")
    st.write(f"- **Desvio padrão:** {estatisticas.get('desvio_padrao', 0):.2f}")
    
    # Estatísticas de forma
    st.write(f"- **Assimetria:** {estatisticas.get('assimetria', 0):.2f}")
    st.write(f"- **Curtose:** {estatisticas.get('curtose', 0):.2f}")
    
    # Estatísticas de amplitude
    st.write(f"- **Mínimo:** {estatisticas.get('min_valor', 0):.2f}")
    st.write(f"- **Máximo:** {estatisticas.get('max_valor', 0):.2f}")
    st.write(f"- **Amplitude:** {estatisticas.get('amplitude', 0):.2f}")
    
    # Coeficiente de variação
    st.write(f"- **Coeficiente de variação:** {estatisticas.get('coef_variacao', 0):.2f}%")
    
    # Intervalo de confiança
    ic = estatisticas.get('intervalo_confianca', [0, 0])
    st.write(f"- **Intervalo de confiança (95%):** [{ic[0]:.2f}, {ic[1]:.2f}]")


def _mostrar_percentis_detalhados(estatisticas: Dict[str, Any]) -> None:
    """
    Mostra os percentis detalhados no expander.
    
    Parâmetros:
    -----------
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
    """
    st.write("#### Distribuição por percentis")
    
    # Obter percentis do dicionário
    percentis = estatisticas.get('percentis', {})
    
    if not percentis:
        st.info("Dados de percentis não disponíveis.")
        return
    
    # Mostrar percentis organizados
    percentis_ordenados = sorted(percentis.items())
    for p, valor in percentis_ordenados:
        st.write(f"- **Percentil {p}:** {valor:.2f}")
    
    # Criar tabela com quartis e interpretação
    quartis_df = pd.DataFrame({
        'Quartil': ['Q1 (25%)', 'Q2 (50%)', 'Q3 (75%)'],
        'Valor': [
            percentis.get(25, 0),
            percentis.get(50, 0),
            percentis.get(75, 0)
        ],
        'Interpretação': [
            '25% dos candidatos obtiveram nota abaixo deste valor',
            '50% dos candidatos obtiveram nota abaixo deste valor (mediana)',
            '75% dos candidatos obtiveram nota abaixo deste valor'
        ]
    })
    
    st.table(quartis_df)


def _mostrar_grafico_faixas_desempenho(estatisticas: Dict[str, Any]) -> None:
    """
    Mostra gráfico de barras com faixas de desempenho.
    
    Parâmetros:
    -----------
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
    """
    # Verificar se temos dados de faixas
    faixas = estatisticas.get('faixas', {})
    if not faixas:
        return
        
    st.write("#### Distribuição por faixas de desempenho")
    
    # Organizar faixas em ordem específica
    ordem_faixas = [
        'Abaixo de 300', 
        '300 a 500', 
        '500 a 700', 
        '700 a 900', 
        '900 ou mais'
    ]
    
    # Criar DataFrame para plotagem
    df_faixas = pd.DataFrame({
        'Faixa': [faixa for faixa in ordem_faixas if faixa in faixas],
        'Percentual': [faixas.get(faixa, 0) for faixa in ordem_faixas if faixa in faixas]
    })
    
    if df_faixas.empty:
        st.info("Dados de faixas de desempenho não disponíveis.")
        return
    
    # Criar gráfico de barras
    fig = px.bar(
        df_faixas,
        x='Faixa',
        y='Percentual',
        text_auto='.1f',
        title="Distribuição de candidatos por faixas de nota",
        labels={'Percentual': '% de Candidatos', 'Faixa': 'Faixa de Nota'},
        color='Faixa',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        xaxis_title="Faixa de nota",
        yaxis_title="Percentual de candidatos (%)",
        yaxis=dict(ticksuffix='%'),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _mostrar_grafico_conceitos(estatisticas: Dict[str, Any], nome_area: str) -> None:
    """
    Mostra gráfico de barras com conceitos de desempenho.
    
    Parâmetros:
    -----------
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
    nome_area : str
        Nome da área de conhecimento
    """
    # Verificar se temos dados de conceitos
    conceitos = estatisticas.get('conceitos', {})
    if not conceitos:
        return
        
    st.write(f"#### Distribuição por conceitos em {nome_area}")
    
    # Organizar conceitos em ordem específica
    ordem_conceitos = [
        'Insuficiente (abaixo de 450)',
        'Regular (450 a 600)',
        'Bom (600 a 750)',
        'Muito bom (750 a 850)',
        'Excelente (850 ou mais)'
    ]
    
    # Criar DataFrame para plotagem
    df_conceitos = pd.DataFrame({
        'Conceito': [conceito for conceito in ordem_conceitos if conceito in conceitos],
        'Percentual': [conceitos.get(conceito, 0) for conceito in ordem_conceitos if conceito in conceitos]
    })
    
    if df_conceitos.empty:
        st.info("Dados de conceitos não disponíveis.")
        return
    
    # Criar gráfico de barras
    fig = px.bar(
        df_conceitos,
        x='Conceito',
        y='Percentual',
        text_auto='.1f',
        title=f"Distribuição de candidatos por conceito em {nome_area}",
        labels={'Percentual': '% de Candidatos', 'Conceito': 'Conceito'},
        color='Conceito',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    fig.update_layout(
        xaxis_title="Conceito",
        yaxis_title="Percentual de candidatos (%)",
        yaxis=dict(ticksuffix='%'),
        plot_bgcolor='white',
        xaxis=dict(tickangle=-25)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Descrição dos conceitos:**
    - **Insuficiente (abaixo de 450)**: Desenvolvimento insuficiente das competências avaliadas
    - **Regular (450 a 600)**: Desenvolvimento parcial das competências avaliadas
    - **Bom (600 a 750)**: Bom desenvolvimento das competências avaliadas
    - **Muito bom (750 a 850)**: Desenvolvimento muito bom das competências avaliadas
    - **Excelente (850 ou mais)**: Desenvolvimento excelente das competências avaliadas
    """)


# Funções auxiliares para análise de faltas

def _mostrar_metricas_principais_faltas(analise: Dict[str, Any]) -> None:
    """
    Mostra as métricas principais de faltas.
    
    Parâmetros:
    -----------
    analise : Dict[str, Any]
        Dicionário com análises de faltas
    """
    # Métricas gerais
    st.write(f"- **Taxa média geral de faltas:** {analise.get('taxa_media_geral', 0):.2f}%")
    
    # Estado com maior taxa de faltas
    estado_maior_falta = analise.get('estado_maior_falta')
    if estado_maior_falta:
        st.write(f"- **Estado com maior taxa de faltas nos dois dias:** {estado_maior_falta.get('Estado')} ({estado_maior_falta.get('Percentual de Faltas', 0):.2f}%)")
    
    # Estado com menor taxa de faltas
    estado_menor_falta = analise.get('estado_menor_falta')
    if estado_menor_falta:
        st.write(f"- **Estado com menor taxa de faltas nos dois dias:** {estado_menor_falta.get('Estado')} ({estado_menor_falta.get('Percentual de Faltas', 0):.2f}%)")


def _criar_grafico_tipos_falta(medias_por_tipo: pd.DataFrame) -> None:
    """
    Cria gráfico de barras para tipos de faltas.
    
    Parâmetros:
    -----------
    medias_por_tipo : DataFrame
        DataFrame com médias por tipo de falta
    """
    if medias_por_tipo is None or medias_por_tipo.empty:
        st.info("Dados insuficientes para análise por tipo de falta.")
        return
        
    # Criar gráfico de barras
    fig = px.bar(
        medias_por_tipo,
        x='Tipo de Falta',
        y='Percentual de Faltas',
        text_auto='.1f',
        title="Taxa média de faltas por tipo",
        labels={'Percentual de Faltas': '% de Faltas', 'Tipo de Falta': 'Padrão de Ausência'},
        color='Tipo de Falta',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        yaxis=dict(ticksuffix='%'),
        xaxis_title="Padrão de Ausência",
        yaxis_title="Taxa média de faltas (%)",
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _criar_grafico_dias_prova(analise: Dict[str, Any]) -> None:
    """
    Cria gráfico de barras para comparação entre dias de prova.
    
    Parâmetros:
    -----------
    analise : Dict[str, Any]
        Dicionário com análises de faltas
    """
    # Criar dataframe para comparação entre dias
    dias_df = pd.DataFrame({
        'Dia de Prova': ['Primeiro dia apenas', 'Segundo dia apenas', 'Ambos os dias'],
        'Taxa média de faltas (%)': [
            analise.get('media_faltas_dia1', 0), 
            analise.get('media_faltas_dia2', 0), 
            analise.get('media_faltas_ambos_dias', 0)
        ]
    })
    
    # Criar gráfico de barras
    fig = px.bar(
        dias_df,
        x='Dia de Prova',
        y='Taxa média de faltas (%)',
        text_auto='.1f',
        title="Comparativo de faltas entre dias de prova",
        color='Dia de Prova',
        color_discrete_sequence=['#7D3C98', '#2471A3', '#CB4335']
    )
    
    fig.update_layout(
        yaxis=dict(ticksuffix='%'),
        xaxis_title="Padrão de Ausência",
        yaxis_title="Taxa média de faltas (%)",
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar diferença entre os dias
    diferenca_dias = analise.get('diferenca_dias', 0)
    if abs(diferenca_dias) < 0.5:
        st.info("📊 **Padrão equilibrado:** Taxa de faltas semelhante entre primeiro e segundo dia de prova.")
    elif diferenca_dias > 0:
        st.info(f"📊 **Maior evasão no segundo dia:** Taxa de faltas {abs(diferenca_dias):.2f} pontos percentuais maior no segundo dia, sugerindo possível desistência após experiência no primeiro dia.")
    else:
        st.info(f"📊 **Maior evasão no primeiro dia:** Taxa de faltas {abs(diferenca_dias):.2f} pontos percentuais maior no primeiro dia, sugerindo possível estratégia de participação seletiva.")


def _mostrar_analise_variabilidade_faltas(analise: Dict[str, Any]) -> None:
    """
    Mostra análise da variabilidade de faltas entre estados.
    
    Parâmetros:
    -----------
    analise : Dict[str, Any]
        Dicionário com análises de faltas
    """
    st.write("#### Análise da variabilidade regional")
    st.write(f"- **Desvio padrão entre estados:** {analise.get('desvio_padrao_faltas', 0):.2f} pontos percentuais")
    st.write(f"- **Avaliação da variabilidade:** {analise.get('variabilidade', 'N/A')}")


def _mostrar_estados_extremos_evasao(analise: Dict[str, Any]) -> None:
    """
    Mostra análise dos estados com maior e menor evasão.
    
    Parâmetros:
    -----------
    analise : Dict[str, Any]
        Dicionário com análises de faltas
    """
    st.write("#### Estados com extremos de evasão")
    
    # Estados com maior evasão
    estados_maior_evasao = analise.get('estados_maior_evasao', [])
    if estados_maior_evasao:
        st.write("**Estados com maior taxa de ausência:**")
        for estado in estados_maior_evasao:
            st.write(f"- **{estado.get('Estado')}:** {estado.get('Percentual', 0):.2f}% ({estado.get('Contagem', 0):,} de {estado.get('Total', 0):,} candidatos)")
    
    # Estados com menor evasão
    estados_menor_evasao = analise.get('estados_menor_evasao', [])
    if estados_menor_evasao:
        st.write("**Estados com menor taxa de ausência:**")
        for estado in estados_menor_evasao:
            st.write(f"- **{estado.get('Estado')}:** {estado.get('Percentual', 0):.2f}% ({estado.get('Contagem', 0):,} de {estado.get('Total', 0):,} candidatos)")


def _criar_mapa_calor_faltas(df_faltas: pd.DataFrame) -> None:
    """
    Cria mapa de calor de faltas por estado e região.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame com dados de faltas
    """
    if df_faltas is None or df_faltas.empty:
        return
        
    try:
        # Verificar estrutura necessária
        if 'Estado' not in df_faltas.columns or 'Tipo de Falta' not in df_faltas.columns:
            return
            
        # Criar cópia do DataFrame
        df_mapa = df_faltas.copy()
        
        # Adicionar informação de região
        df_mapa['Região'] = df_mapa['Estado'].apply(obter_regiao_do_estado)
        
        # Filtrar apenas dados de "Faltou nos dois dias"
        df_mapa = df_mapa[df_mapa['Tipo de Falta'] == 'Faltou nos dois dias']
        
        # Agrupar por região
        df_regiao = df_mapa.groupby('Região')['Percentual de Faltas'].mean().reset_index()
        
        if not df_regiao.empty:
            st.write("#### Mapa de calor de faltas por região")
            
            # Criar mapa de calor
            fig = px.imshow(
                pd.pivot_table(
                    df_regiao, 
                    values='Percentual de Faltas',
                    index=['Região']
                ),
                text_auto='.2f',
                color_continuous_scale='Reds',
                title="Taxa média de faltas por região"
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Erro ao criar mapa de calor: {str(e)}")


def _mostrar_causas_potenciais_faltas() -> None:
    """Mostra análise das causas potenciais para faltas."""
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


# Funções auxiliares para análise por faixas de desempenho

def _mostrar_estatisticas_por_faixa(analise_faixas: Dict[str, Any]) -> None:
    """
    Mostra estatísticas detalhadas por faixa de desempenho.
    
    Parâmetros:
    -----------
    analise_faixas : Dict[str, Any]
        Análise por faixas de desempenho
    """
    # Verificar se temos estatísticas por faixa
    estatisticas_faixas = analise_faixas.get('estatisticas_faixas', {})
    if not estatisticas_faixas:
        st.info("Dados de estatísticas por faixa não disponíveis.")
        return
        
    st.write("#### Estatísticas por faixa de desempenho")
    
    # Criar DataFrame para exibição
    dados = []
    for faixa, stats in estatisticas_faixas.items():
        dados.append({
            'Faixa': faixa,
            'Candidatos': stats.get('contagem', 0),
            'Percentual': stats.get('percentual', 0),
            'Média': stats.get('media', 0),
            'Desvio Padrão': stats.get('desvio_padrao', 0)
        })
    
    df_stats = pd.DataFrame(dados)
    
    # Ordenar por faixas na ordem correta
    ordem_faixas = [
        'Insuficiente (abaixo de 450)',
        'Regular (450 a 600)',
        'Bom (600 a 750)',
        'Muito bom (750 a 850)',
        'Excelente (850 ou mais)'
    ]
    
    # Filtrar apenas faixas que existem nos dados
    df_stats['Faixa'] = pd.Categorical(
        df_stats['Faixa'], 
        categories=[f for f in ordem_faixas if f in df_stats['Faixa'].values],
        ordered=True
    )
    
    df_stats = df_stats.sort_values('Faixa')
    
    # Mostrar tabela formatada
    st.dataframe(
        df_stats,
        column_config={
            "Candidatos": st.column_config.NumberColumn(format="%d"),
            "Percentual": st.column_config.NumberColumn(format="%.2f%%"),
            "Média": st.column_config.NumberColumn(format="%.2f"),
            "Desvio Padrão": st.column_config.NumberColumn(format="%.2f")
        },
        hide_index=True
    )


def _criar_grafico_comparativo_faixas(analise_faixas: Dict[str, Any]) -> None:
    """
    Cria gráfico comparativo entre faixas de desempenho.
    
    Parâmetros:
    -----------
    analise_faixas : Dict[str, Any]
        Análise por faixas de desempenho
    """
    # Verificar se temos dados de percentual por faixa
    percentuais = analise_faixas.get('percentual', {})
    if not percentuais:
        return
        
    st.write("#### Distribuição de candidatos por faixa")
    
    # Criar DataFrame para plotagem
    dados = []
    for faixa, percentual in percentuais.items():
        dados.append({
            'Faixa': faixa,
            'Percentual': percentual
        })
    
    df_plot = pd.DataFrame(dados)
    
    # Criar gráfico de pizza para distribuição
    fig = px.pie(
        df_plot, 
        values='Percentual', 
        names='Faixa',
        title="Distribuição de candidatos por faixas de desempenho",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}: %{value:.2f}%'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _mostrar_analise_faixa_predominante(analise_faixas: Dict[str, Any]) -> None:
    """
    Mostra análise da faixa de desempenho predominante.
    
    Parâmetros:
    -----------
    analise_faixas : Dict[str, Any]
        Análise por faixas de desempenho
    """
    # Obter faixa predominante
    faixa_predominante = analise_faixas.get('faixa_predominante', '')
    if not faixa_predominante:
        return
        
    # Obter percentual da faixa predominante
    percentuais = analise_faixas.get('percentual', {})
    percentual = percentuais.get(faixa_predominante, 0)
    
    st.write("#### Análise da faixa predominante")
    st.write(f"A faixa predominante é **{faixa_predominante}**, representando **{percentual:.2f}%** dos candidatos.")
    
    # Interpretação específica por faixa
    interpretacoes = {
        'Insuficiente (abaixo de 450)': """
        A predominância de candidatos com desempenho insuficiente sugere sérios desafios educacionais, 
        indicando possíveis lacunas no ensino básico desta área ou dificuldades significativas dos estudantes 
        em compreender e aplicar os conceitos avaliados.
        """,
        
        'Regular (450 a 600)': """
        A predominância de desempenho regular indica que a maioria dos candidatos possui domínio parcial dos 
        conteúdos, sugerindo oportunidades de melhoria no ensino para elevar o nível geral de compreensão 
        e aplicação dos conceitos.
        """,
        
        'Bom (600 a 750)': """
        A predominância de bom desempenho sugere que o ensino desta área tem sido relativamente eficaz, 
        com a maioria dos candidatos demonstrando domínio satisfatório dos conteúdos e competências avaliados.
        """,
        
        'Muito bom (750 a 850)': """
        A predominância de desempenho muito bom indica excelência educacional nesta área, 
        com a maioria dos candidatos demonstrando domínio avançado dos conteúdos e capacidade 
        de aplicação dos conceitos em diferentes contextos.
        """,
        
        'Excelente (850 ou mais)': """
        A predominância de desempenho excelente sugere um cenário educacional excepcional nesta área, 
        com a maioria dos candidatos alcançando níveis superiores de compreensão e aplicação dos conhecimentos, 
        significativamente acima das expectativas básicas.
        """
    }
    
    if faixa_predominante in interpretacoes:
        st.write(interpretacoes[faixa_predominante])


def _mostrar_implicacoes_educacionais_faixas(analise_faixas: Dict[str, Any], nome_area: str) -> None:
    """
    Mostra implicações educacionais da distribuição por faixas.
    
    Parâmetros:
    -----------
    analise_faixas : Dict[str, Any]
        Análise por faixas de desempenho
    nome_area : str
        Nome da área de conhecimento
    """
    # Verificar se temos dados percentuais
    percentuais = analise_faixas.get('percentual', {})
    if not percentuais:
        return
        
    st.write("#### Implicações educacionais")
    
    # Calcular percentual abaixo e acima de 600 (limiar para desempenho adequado)
    faixas_abaixo = ['Insuficiente (abaixo de 450)', 'Regular (450 a 600)']
    faixas_acima = ['Bom (600 a 750)', 'Muito bom (750 a 850)', 'Excelente (850 ou mais)']
    
    percentual_abaixo = sum(percentuais.get(faixa, 0) for faixa in faixas_abaixo)
    percentual_acima = sum(percentuais.get(faixa, 0) for faixa in faixas_acima)
    
    # Determinar interpretação com base na distribuição
    if percentual_abaixo > 70:
        st.write(f"""
        Em {nome_area}, a grande maioria dos candidatos (**{percentual_abaixo:.1f}%**) está abaixo do nível 
        considerado adequado (600 pontos), o que sugere desafios significativos no ensino desta área. 
        
        **Recomendações:**
        - Revisão curricular para identificar lacunas de aprendizagem
        - Fortalecimento da formação docente em metodologias específicas para esta área
        - Desenvolvimento de programas de reforço focados nos conceitos fundamentais
        - Aprimoramento de materiais didáticos e recursos de aprendizagem
        """)
    elif percentual_abaixo > 50:
        st.write(f"""
        Em {nome_area}, mais da metade dos candidatos (**{percentual_abaixo:.1f}%**) está abaixo do nível 
        considerado adequado (600 pontos), indicando oportunidades de melhoria no ensino.
        
        **Recomendações:**
        - Diagnóstico detalhado dos pontos fracos mais comuns
        - Diversificação de estratégias pedagógicas
        - Implementação de programas de monitoria e reforço
        - Maior conexão entre teoria e aplicação prática dos conteúdos
        """)
    elif percentual_acima > 70:
        st.write(f"""
        Em {nome_area}, a maioria dos candidatos (**{percentual_acima:.1f}%**) demonstra domínio satisfatório 
        ou avançado dos conteúdos (acima de 600 pontos), indicando boas práticas educacionais nesta área.
        
        **Potenciais fatores de sucesso:**
        - Metodologias de ensino eficazes que poderiam ser replicadas em outras áreas
        - Materiais didáticos de alta qualidade
        - Formação docente adequada às demandas da disciplina
        - Possível valorização cultural desta área de conhecimento
        """)
    else:
        st.write(f"""
        Em {nome_area}, observa-se uma distribuição relativamente equilibrada entre candidatos abaixo (**{percentual_abaixo:.1f}%**) 
        e acima (**{percentual_acima:.1f}%**) do nível considerado adequado (600 pontos).
        
        **Abordagem recomendada:**
        - Estratégias diferenciadas para atender os diferentes níveis de proficiência
        - Identificação de fatores que contribuem para o sucesso de alguns grupos
        - Atenção especial à transição entre os níveis regular e bom
        - Desenvolvimento de avaliações formativas para monitoramento contínuo do progresso
        """)


# Funções auxiliares para análise regional

def _mostrar_medias_competencia_regiao(metricas_regiao: Dict[str, Dict[str, float]], competencia_mapping: Dict[str, str]) -> None:
    """
    Mostra médias por competência e região.
    
    Parâmetros:
    -----------
    metricas_regiao : Dict[str, Dict[str, float]]
        Métricas por região
    competencia_mapping : Dict[str, str]
        Mapeamento entre códigos de competência e nomes legíveis
    """
    if not metricas_regiao:
        st.info("Dados insuficientes para análise por região.")
        return
        
    # Criar DataFrame para visualização
    dados = []
    for regiao, metricas in metricas_regiao.items():
        linha = {'Região': regiao}
        
        # Adicionar métricas por competência
        for cod_comp, nome_comp in competencia_mapping.items():
            # Obter valor da métrica para esta competência nesta região
            valor = metricas.get(cod_comp, 0)
            
            # Verificar se o valor é válido (não NaN ou None)
            if pd.isna(valor) or valor is None:
                valor = 0
                
            # Adicionar à linha com nome legível da competência
            linha[nome_comp] = valor
        
        # Adicionar média geral
        media_geral = metricas.get('media_geral', 0)
        if pd.isna(media_geral) or media_geral is None:
            media_geral = 0
            
        linha['Média Geral'] = media_geral
        
        # Adicionar total de candidatos
        total_candidatos = metricas.get('total_candidatos', 0)
        if pd.isna(total_candidatos) or total_candidatos is None:
            total_candidatos = 0
            
        linha['Total de Candidatos'] = total_candidatos
        
        dados.append(linha)
    
    # Criar DataFrame
    df_metricas = pd.DataFrame(dados)
    
    # Ordenar por média geral (decrescente)
    if 'Média Geral' in df_metricas.columns:
        df_metricas = df_metricas.sort_values('Média Geral', ascending=False)
    
    # Substituir NaN por zeros
    df_metricas = df_metricas.fillna(0)
    
    # Formatar números para evitar exibição de NaN
    for col in df_metricas.columns:
        if col != 'Região':
            df_metricas[col] = df_metricas[col].apply(lambda x: round(float(x), 2) if pd.notnull(x) else 0)
    
    # Mostrar tabela formatada
    st.dataframe(
        df_metricas,
        column_config={
            col: st.column_config.NumberColumn(format="%.2f") 
            for col in df_metricas.columns 
            if col not in ['Região', 'Total de Candidatos']
        },
        hide_index=True
    )


def _criar_grafico_comparativo_regioes(metricas_regiao: Dict[str, Dict[str, float]]) -> None:
    """
    Cria gráfico comparativo entre regiões.
    
    Parâmetros:
    -----------
    metricas_regiao : Dict[str, Dict[str, float]]
        Métricas por região
    """
    if not metricas_regiao:
        return
        
    # Criar DataFrame para visualização
    dados = []
    for regiao, metricas in metricas_regiao.items():
        dados.append({
            'Região': regiao,
            'Média Geral': metricas.get('media_geral', 0)
        })
    
    df_plot = pd.DataFrame(dados)
    
    # Ordenar por média geral (decrescente)
    df_plot = df_plot.sort_values('Média Geral', ascending=False)
    
    # Criar gráfico de barras
    fig = px.bar(
        df_plot,
        x='Região',
        y='Média Geral',
        text_auto='.1f',
        title="Comparativo de médias por região",
        color='Região',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        xaxis_title="Região",
        yaxis_title="Média Geral",
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _criar_mapa_calor_regioes(metricas_regiao: Dict[str, Dict[str, float]], competencia_mapping: Dict[str, str]) -> None:
    """
    Cria mapa de calor para análise regional por competência.
    
    Parâmetros:
    -----------
    metricas_regiao : Dict[str, Dict[str, float]]
        Métricas por região
    competencia_mapping : Dict[str, str]
        Mapeamento entre códigos de competência e nomes legíveis
    """
    if not metricas_regiao:
        return
        
    # Criar DataFrame para visualização
    dados = []
    
    # Percorrer cada região
    for regiao, metricas in metricas_regiao.items():
        # Percorrer cada competência
        for cod_comp, nome_comp in competencia_mapping.items():
            # Pular a média geral, total de candidatos e outras métricas que não são competências
            if cod_comp not in metricas:
                continue
                
            # Obter valor da métrica
            valor = metricas.get(cod_comp, 0)
            
            # Verificar se o valor é válido
            if valor > 0 and not pd.isna(valor):
                dados.append({
                    'Região': regiao,
                    'Competência': nome_comp,
                    'Média': valor
                })
    
    # Verificar se temos dados suficientes
    if not dados:
        st.info("Dados insuficientes para criar mapa de calor.")
        return
        
    # Criar DataFrame
    df_plot = pd.DataFrame(dados)
    
    # Criar mapa de calor apenas se tivermos dados
    if not df_plot.empty:
        # Pivotar o DataFrame para formato de matriz
        pivot_df = pd.pivot_table(
            df_plot, 
            values='Média',
            index=['Região'],
            columns=['Competência'],
            aggfunc='mean'
        )
        
        # Criar mapa de calor
        fig = px.imshow(
            pivot_df,
            text_auto='.1f',
            aspect="auto",
            color_continuous_scale='Viridis',
            title="Mapa de calor do desempenho regional por competência"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Área de Conhecimento",
            yaxis_title="Região"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados insuficientes para criar mapa de calor das regiões.")


def _mostrar_analise_disparidades_regionais(metricas_regiao: Dict[str, Dict[str, float]]) -> None:
    """
    Mostra análise das disparidades regionais.
    
    Parâmetros:
    -----------
    metricas_regiao : Dict[str, Dict[str, float]]
        Métricas por região
    """
    if not metricas_regiao:
        return
        
    # Calcular média nacional ponderada pelo número de candidatos
    total_candidatos = 0
    soma_ponderada = 0
    
    for regiao, metricas in metricas_regiao.items():
        candidatos = metricas.get('total_candidatos', 0)
        media = metricas.get('media_geral', 0)
        
        total_candidatos += candidatos
        soma_ponderada += candidatos * media
    
    media_nacional = soma_ponderada / total_candidatos if total_candidatos > 0 else 0
    
    # Identificar regiões com maior e menor média
    maior_media = 0
    menor_media = float('inf')
    regiao_maior_media = ""
    regiao_menor_media = ""
    
    for regiao, metricas in metricas_regiao.items():
        media = metricas.get('media_geral', 0)
        
        if media > maior_media:
            maior_media = media
            regiao_maior_media = regiao
            
        if media < menor_media and media > 0:
            menor_media = media
            regiao_menor_media = regiao
    
    # Calcular disparidade percentual
    disparidade_percentual = ((maior_media - menor_media) / menor_media * 100) if menor_media > 0 else 0
    
    # Mostrar análise
    st.write(f"**Média nacional:** {media_nacional:.2f} pontos")
    st.write(f"**Região com maior média:** {regiao_maior_media} ({maior_media:.2f} pontos)")
    st.write(f"**Região com menor média:** {regiao_menor_media} ({menor_media:.2f} pontos)")
    st.write(f"**Disparidade percentual:** {disparidade_percentual:.2f}%")
    
    # Interpretar disparidade
    if disparidade_percentual < 5:
        st.write("""
        A baixa disparidade regional sugere relativa homogeneidade no ensino entre as diferentes regiões do país, 
        possivelmente refletindo políticas educacionais de alcance nacional eficazes.
        """)
    elif disparidade_percentual < 15:
        st.write("""
        A disparidade moderada entre regiões indica algumas diferenças na qualidade e acesso educacional, 
        mas sem extremos acentuados, sugerindo que políticas específicas para as regiões de menor desempenho 
        poderiam aproximar os resultados.
        """)
    else:
        st.write("""
        A alta disparidade regional revela um cenário de desigualdade educacional significativa no país, 
        demandando políticas públicas específicas para reduzir essas diferenças e proporcionar oportunidades 
        mais equitativas aos estudantes de todas as regiões.
        """)


# Funções auxiliares para análise comparativa entre áreas

def _identificar_areas_extremas(df_areas: pd.DataFrame) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Identifica áreas com melhor e pior desempenho.
    
    Parâmetros:
    -----------
    df_areas : DataFrame
        DataFrame com dados por área
        
    Retorna:
    --------
    Tuple[Dict[str, Any], Dict[str, Any]]: Tupla com dicionários da melhor e pior área
    """
    if df_areas is None or df_areas.empty:
        return {}, {}
        
    # Ordenar por média
    df_ordenado = df_areas.sort_values('Media', ascending=False)
    
    # Melhor área
    melhor_area = {}
    if not df_ordenado.empty:
        row = df_ordenado.iloc[0]
        melhor_area = {
            'nome': row['Area'],
            'media': row['Media'],
            'desvio': row.get('DesvioPadrao', 0),
            'mediana': row.get('Mediana', 0)
        }
    
    # Pior área
    pior_area = {}
    if len(df_ordenado) > 1:
        row = df_ordenado.iloc[-1]
        pior_area = {
            'nome': row['Area'],
            'media': row['Media'],
            'desvio': row.get('DesvioPadrao', 0),
            'mediana': row.get('Mediana', 0)
        }
    
    return melhor_area, pior_area


def _mostrar_resumo_comparativo_areas(df_areas: pd.DataFrame, melhor_area: Dict[str, Any], pior_area: Dict[str, Any]) -> None:
    """
    Mostra resumo comparativo entre áreas.
    
    Parâmetros:
    -----------
    df_areas : DataFrame
        DataFrame com dados por área
    melhor_area : Dict[str, Any]
        Dicionário com dados da melhor área
    pior_area : Dict[str, Any]
        Dicionário com dados da pior área
    """
    st.write("#### Resumo comparativo")
    
    # Verificar se temos dados válidos
    if not melhor_area or not pior_area:
        st.info("Dados insuficientes para análise comparativa.")
        return
    
    # Calcular diferença percentual
    diferenca_percentual = ((melhor_area['media'] - pior_area['media']) / pior_area['media'] * 100) if pior_area['media'] > 0 else 0
    
    # Identificar áreas com maior e menor variabilidade
    df_variabilidade = df_areas.copy()
    if 'DesvioPadrao' in df_variabilidade.columns and 'Media' in df_variabilidade.columns:
        df_variabilidade['CV'] = (df_variabilidade['DesvioPadrao'] / df_variabilidade['Media'] * 100)
        
        # Obter área com maior variabilidade
        idx_max = df_variabilidade['CV'].idxmax() if not df_variabilidade['CV'].isna().all() else None
        maior_variabilidade = df_variabilidade.loc[idx_max, 'Area'] if idx_max is not None else "N/A"
        
        # Obter área com menor variabilidade
        idx_min = df_variabilidade['CV'].idxmin() if not df_variabilidade['CV'].isna().all() else None
        menor_variabilidade = df_variabilidade.loc[idx_min, 'Area'] if idx_min is not None else "N/A"
    else:
        maior_variabilidade = "N/A"
        menor_variabilidade = "N/A"
    
    # Mostrar informações
    st.write(f"**Área com melhor desempenho:** {melhor_area['nome']} (média: {melhor_area['media']:.2f})")
    st.write(f"**Área com pior desempenho:** {pior_area['nome']} (média: {pior_area['media']:.2f})")
    st.write(f"**Diferença percentual:** {diferenca_percentual:.2f}%")
    
    st.write(f"**Área com maior variabilidade nas notas:** {maior_variabilidade}")
    st.write(f"**Área com menor variabilidade nas notas:** {menor_variabilidade}")
    
    # Interpretar a diferença
    if diferenca_percentual < 5:
        st.write("""
        A pequena diferença entre as áreas sugere um equilíbrio no domínio das diferentes competências pelos candidatos, 
        possivelmente refletindo um ensino igualmente eficaz em todas as áreas do conhecimento.
        """)
    elif diferenca_percentual < 15:
        st.write("""
        A diferença moderada entre as áreas indica algumas disparidades no ensino ou na dificuldade intrínseca 
        das competências avaliadas, mas sem extremos preocupantes.
        """)
    else:
        st.write("""
        A diferença significativa entre as áreas sugere um desequilíbrio importante no ensino das diferentes competências, 
        possivelmente refletindo maior ênfase ou eficácia pedagógica em determinadas áreas em detrimento de outras.
        """)

def _mostrar_analise_dificuldade_relativa(df_areas: pd.DataFrame) -> None:
    """
    Mostra uma análise robusta e profissional sobre a dificuldade relativa entre áreas de conhecimento,
    incluindo explicações sobre o gráfico, insights estatísticos e interpretações educacionais.

    Parâmetros:
    -----------
    df_areas : DataFrame
        DataFrame com dados comparativos entre áreas (deve conter colunas 'Area', 'Media', 'DesvioPadrao', 'Mediana', 'Minimo', 'Maximo')
    """
    import streamlit as st
    import plotly.express as px
    import pandas as pd

    st.write("### Dificuldade Relativa entre Áreas de Conhecimento")

    if df_areas is None or df_areas.empty:
        st.warning("Dados insuficientes para análise de dificuldade relativa entre áreas.")
        return

    # Gráfico: Ranking de médias das áreas
    st.write("#### Ranking de Desempenho Médio")
    fig = px.bar(
        df_areas.sort_values("Media", ascending=True),
        x="Media",
        y="Area",
        orientation="h",
        text="Media",
        color="Media",
        color_continuous_scale="Blues",
        labels={"Media": "Nota Média", "Area": "Área de Conhecimento"},
        title="Ranking das Áreas por Nota Média"
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(plot_bgcolor='white', height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico: Dispersão das notas (Desvio Padrão)
    if "DesvioPadrao" in df_areas.columns:
        st.write("#### Dispersão das Notas por Área")
        fig_disp = px.bar(
            df_areas.sort_values("DesvioPadrao", ascending=False),
            x="DesvioPadrao",
            y="Area",
            orientation="h",
            text="DesvioPadrao",
            color="DesvioPadrao",
            color_continuous_scale="Oranges",
            labels={"DesvioPadrao": "Desvio Padrão", "Area": "Área de Conhecimento"},
            title="Dispersão das Notas (Desvio Padrão) por Área"
        )
        fig_disp.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_disp.update_layout(plot_bgcolor='white', height=400)
        st.plotly_chart(fig_disp, use_container_width=True)

    # Tabela resumo com principais estatísticas
    st.write("#### Estatísticas Resumidas por Área")
    colunas_exibir = ["Area", "Media", "Mediana", "DesvioPadrao", "Minimo", "Maximo"]
    colunas_presentes = [col for col in colunas_exibir if col in df_areas.columns]
    st.dataframe(
        df_areas[colunas_presentes].sort_values("Media", ascending=False),
        column_config={
            "Media": st.column_config.NumberColumn("Média", format="%.2f"),
            "Mediana": st.column_config.NumberColumn("Mediana", format="%.2f"),
            "DesvioPadrao": st.column_config.NumberColumn("Desvio Padrão", format="%.2f"),
            "Minimo": st.column_config.NumberColumn("Mínimo", format="%.2f"),
            "Maximo": st.column_config.NumberColumn("Máximo", format="%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )

    # Insights e explicações
    st.write("#### Interpretação e Insights")
    melhor = df_areas.loc[df_areas["Media"].idxmax()]
    pior = df_areas.loc[df_areas["Media"].idxmin()]
    maior_disp = df_areas.loc[df_areas["DesvioPadrao"].idxmax()] if "DesvioPadrao" in df_areas.columns else None
    menor_disp = df_areas.loc[df_areas["DesvioPadrao"].idxmin()] if "DesvioPadrao" in df_areas.columns else None

    st.markdown(f"""
- **Área com maior média:** <b>{melhor['Area']}</b> ({melhor['Media']:.2f})
- **Área com menor média:** <b>{pior['Area']}</b> ({pior['Media']:.2f})
- **Diferença absoluta:** <b>{abs(melhor['Media'] - pior['Media']):.2f} pontos</b>
- **Diferença percentual:** <b>{(abs(melhor['Media'] - pior['Media']) / pior['Media'] * 100):.2f}%</b>
""", unsafe_allow_html=True)

    if maior_disp is not None and menor_disp is not None:
        st.markdown(f"""
- **Maior dispersão (desvio padrão):** <b>{maior_disp['Area']}</b> ({maior_disp['DesvioPadrao']:.2f})
- **Menor dispersão (desvio padrão):** <b>{menor_disp['Area']}</b> ({menor_disp['DesvioPadrao']:.2f})
""", unsafe_allow_html=True)

    # Interpretação educacional
    st.info("""
    **Como interpretar a dificuldade relativa entre áreas?**

    - Áreas com **menor média** podem indicar maior dificuldade dos candidatos, seja por maior complexidade dos conteúdos, deficiências no ensino ou menor afinidade dos estudantes.
    - Áreas com **maior desvio padrão** sugerem maior heterogeneidade no desempenho, indicando que alguns grupos conseguem bons resultados enquanto outros têm dificuldades.
    - Diferenças percentuais elevadas entre as médias das áreas podem sinalizar a necessidade de políticas educacionais específicas para equilibrar o ensino e o aprendizado.

    **Sugestões de análise:**
    - Investigar fatores curriculares, metodológicos ou socioeconômicos que possam explicar as diferenças.
    - Observar se áreas tradicionalmente consideradas "difíceis" (como Matemática) realmente apresentam médias mais baixas e maior dispersão.
    - Utilizar esses dados para orientar intervenções pedagógicas e políticas públicas voltadas à redução das desigualdades entre áreas
    """)

def criar_expander_analise_histograma(
    df: pd.DataFrame, 
    coluna: str, 
    nome_area: str, 
    estatisticas: Dict[str, Any]
) -> None:
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
        # Verificar se temos dados suficientes
        if df is None or df.empty or estatisticas is None:
            st.warning("Dados insuficientes para análise detalhada.")
            return
        
        # Criar abas para diferentes análises
        tab_stats, tab_perc, tab_faixas, tab_interpretation = st.tabs([
            "Estatísticas Básicas", 
            "Análise Percentílica", 
            "Faixas de Desempenho",
            "Interpretação Estatística"
        ])
        
        with tab_stats:
            _mostrar_estatisticas_descritivas(estatisticas)
        
        with tab_perc:
            _mostrar_percentis_detalhados(estatisticas)
        
        with tab_faixas:
            _mostrar_grafico_faixas_desempenho(estatisticas)
            _mostrar_grafico_conceitos(estatisticas, nome_area)
        
        with tab_interpretation:
            # Usar função do módulo de explicação para interpretação avançada
            interpretation = get_interpretacao_distribuicao(
                estatisticas.get('assimetria', 0),
                estatisticas.get('curtose', 0),
                estatisticas.get('media', 0),
                estatisticas.get('desvio_padrao', 0)
            )
            st.markdown(interpretation)


def criar_expander_analise_faltas(
    df_faltas: pd.DataFrame, 
    analise: Dict[str, Any]
) -> None:
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
        # Verificar se temos dados suficientes
        if df_faltas is None or df_faltas.empty or analise is None:
            st.warning("Dados insuficientes para análise detalhada de ausências.")
            return
        
        # Criar abas para diferentes análises
        tab_overview, tab_detalhes, tab_regional, tab_causas = st.tabs([
            "Visão Geral", 
            "Análise por Dia", 
            "Análise Regional",
            "Possíveis Causas"
        ])
        
        with tab_overview:
            st.write("#### Visão geral das ausências no ENEM")
            _mostrar_metricas_principais_faltas(analise)
            _criar_grafico_tipos_falta(analise.get('medias_por_tipo', pd.DataFrame()))
        
        with tab_detalhes:
            st.write("#### Análise comparativa entre dias de prova")
            _criar_grafico_dias_prova(analise)
        
        with tab_regional:
            st.write("#### Análise regional de ausências")
            _mostrar_analise_variabilidade_faltas(analise)
            _mostrar_estados_extremos_evasao(analise)
            _criar_mapa_calor_faltas(df_faltas)
        
        with tab_causas:
            _mostrar_causas_potenciais_faltas()


def criar_expander_analise_faixas_desempenho(
    df: pd.DataFrame, 
    coluna: str, 
    nome_area: str
) -> None:
    """
    Cria um expander com análise detalhada por faixas de desempenho.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    coluna : str
        Nome da coluna (área de conhecimento) a ser analisada
    nome_area : str
        Nome formatado da área de conhecimento
    """
    with st.expander("Ver análise por faixas de desempenho"):
        # Verificar se temos dados suficientes
        if df is None or df.empty or coluna not in df.columns:
            st.warning("Dados insuficientes para análise por faixas de desempenho.")
            return
        
        # Calcular análise por faixas de desempenho
        with st.spinner("Calculando estatísticas por faixas..."):
            analise_faixas = analisar_desempenho_por_faixa_nota(df, coluna)
        
        if not analise_faixas or not analise_faixas.get('percentual'):
            st.warning("Não foi possível calcular estatísticas por faixas de desempenho.")
            return
        
        # Criar abas para diferentes análises
        tab_visao, tab_stats, tab_implicacoes = st.tabs([
            "Distribuição por Faixa", 
            "Estatísticas Detalhadas", 
            "Implicações Educacionais"
        ])
        
        with tab_visao:
            _criar_grafico_comparativo_faixas(analise_faixas)
            _mostrar_analise_faixa_predominante(analise_faixas)
        
        with tab_stats:
            _mostrar_estatisticas_por_faixa(analise_faixas)
        
        with tab_implicacoes:
            _mostrar_implicacoes_educacionais_faixas(analise_faixas, nome_area)


def criar_expander_analise_regional(
    df: pd.DataFrame, 
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str]
) -> None:
    """
    Cria um expander com análise detalhada do desempenho por região.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    colunas_notas : List[str]
        Lista de colunas com notas para análise
    competencia_mapping : Dict[str, str]
        Mapeamento entre códigos de competência e nomes legíveis
    """
    with st.expander("Ver análise por região"):
        # Verificar se temos dados suficientes
        if df is None or df.empty or 'SG_UF_PROVA' not in df.columns:
            st.warning("Dados insuficientes para análise regional.")
            return
        
        # Calcular métricas por região
        with st.spinner("Calculando métricas por região..."):
            metricas_regiao = analisar_metricas_por_regiao(df, colunas_notas)
        
        if not metricas_regiao:
            st.warning("Não foi possível calcular métricas por região.")
            return
        
        # Criar abas para diferentes análises
        tab_resumo, tab_detalhes, tab_visual, tab_disparidades = st.tabs([
            "Resumo Regional", 
            "Métricas por Competência", 
            "Visualização Comparativa",
            "Análise de Disparidades"
        ])
        
        with tab_resumo:
            st.write("#### Resumo do desempenho por região")
            _criar_grafico_comparativo_regioes(metricas_regiao)
        
        with tab_detalhes:
            st.write("#### Detalhamento por região e competência")
            _mostrar_medias_competencia_regiao(metricas_regiao, competencia_mapping)
        
        with tab_visual:
            st.write("#### Mapa de calor do desempenho regional")
            _criar_mapa_calor_regioes(metricas_regiao, competencia_mapping)
        
        with tab_disparidades:
            st.write("#### Análise de disparidades regionais")
            _mostrar_analise_disparidades_regionais(metricas_regiao)


def criar_expander_analise_comparativo_areas(
    df_areas: pd.DataFrame
) -> None:
    """
    Cria um expander com análise detalhada do comparativo entre áreas.
    
    Parâmetros:
    -----------
    df_areas : DataFrame
        DataFrame com dados comparativos entre áreas
    """
    with st.expander("Ver análise comparativa entre áreas"):
        # Verificar se temos dados suficientes
        if df_areas is None or df_areas.empty:
            st.warning("Dados insuficientes para análise comparativa entre áreas.")
            return
        
        # Identificar áreas com melhor e pior desempenho
        melhor_area, pior_area = _identificar_areas_extremas(df_areas)
        
        # Criar abas para diferentes análises
        tab_resumo, tab_dificuldade, tab_analise = st.tabs([
            "Resumo Comparativo", 
            "Dificuldade Relativa", 
            "Análise de Diferenças"
        ])
        
        with tab_resumo:
            _mostrar_resumo_comparativo_areas(df_areas, melhor_area, pior_area)
        
        with tab_dificuldade:
            _mostrar_analise_dificuldade_relativa(df_areas)
        
        with tab_analise:
            st.write("#### Análise de diferenças entre áreas")
            
            # Criar um seletor para comparar duas áreas específicas
            areas_disponiveis = df_areas['Area'].tolist()
            if len(areas_disponiveis) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    area1 = st.selectbox("Primeira área", areas_disponiveis, index=0)
                with col2:
                    # Definir índice padrão para área 2 (segundo item ou primeiro se houver apenas um)
                    idx2 = min(1, len(areas_disponiveis)-1)
                    area2 = st.selectbox("Segunda área", areas_disponiveis, index=idx2)
                
                # Extrair dados das áreas selecionadas
                dados_area1 = df_areas[df_areas['Area'] == area1].iloc[0] if not df_areas[df_areas['Area'] == area1].empty else None
                dados_area2 = df_areas[df_areas['Area'] == area2].iloc[0] if not df_areas[df_areas['Area'] == area2].empty else None
                
                if dados_area1 is not None and dados_area2 is not None:
                    # Calcular diferença percentual
                    diff_percent = ((dados_area1['Media'] - dados_area2['Media']) / dados_area2['Media'] * 100) if dados_area2['Media'] > 0 else 0
                    
                    st.write(f"**Diferença entre {area1} e {area2}:**")
                    st.write(f"- Média {area1}: {dados_area1['Media']:.2f}")
                    st.write(f"- Média {area2}: {dados_area2['Media']:.2f}")
                    st.write(f"- Diferença absoluta: {abs(dados_area1['Media'] - dados_area2['Media']):.2f} pontos")
                    st.write(f"- Diferença percentual: {abs(diff_percent):.2f}% {'maior' if diff_percent > 0 else 'menor'}")
                    
                    if 'DesvioPadrao' in df_areas.columns:
                        st.write(f"- Desvio padrão {area1}: {dados_area1['DesvioPadrao']:.2f}")
                        st.write(f"- Desvio padrão {area2}: {dados_area2['DesvioPadrao']:.2f}")
                        
                        # Comparar variabilidade
                        cv1 = (dados_area1['DesvioPadrao'] / dados_area1['Media'] * 100) if dados_area1['Media'] > 0 else 0
                        cv2 = (dados_area2['DesvioPadrao'] / dados_area2['Media'] * 100) if dados_area2['Media'] > 0 else 0
                        
                        st.write(f"- Coeficiente de variação {area1}: {cv1:.2f}%")
                        st.write(f"- Coeficiente de variação {area2}: {cv2:.2f}%")
                        
                        # Interpretar diferença na variabilidade
                        if abs(cv1 - cv2) < 5:
                            st.write("Ambas as áreas apresentam variabilidade semelhante nas notas.")
                        else:
                            area_mais_variavel = area1 if cv1 > cv2 else area2
                            st.write(f"A área de **{area_mais_variavel}** apresenta **maior variabilidade** nas notas, indicando desempenho mais heterogêneo entre os candidatos.")
            else:
                st.warning("Dados insuficientes para comparação entre áreas específicas.")


# Completando funções auxiliares pendentes

def _mostrar_grafico_faixas_desempenho(estatisticas: Dict[str, Any]) -> None:
    """
    Mostra gráfico de barras com faixas de desempenho.
    
    Parâmetros:
    -----------
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
    """
    # Verificar se temos dados de faixas
    faixas = estatisticas.get('faixas', {})
    if not faixas:
        st.info("Dados de faixas de desempenho não disponíveis.")
        return
        
    st.write("#### Distribuição por faixas de desempenho")
    
    # Organizar faixas em ordem específica
    ordem_faixas = [
        'Abaixo de 300', 
        '300 a 500', 
        '500 a 700', 
        '700 a 900', 
        '900 ou mais'
    ]
    
    # Criar DataFrame para plotagem
    df_faixas = pd.DataFrame({
        'Faixa': [faixa for faixa in ordem_faixas if faixa in faixas],
        'Percentual': [faixas.get(faixa, 0) for faixa in ordem_faixas if faixa in faixas]
    })
    
    if df_faixas.empty:
        st.info("Nenhuma faixa com dados disponíveis.")
        return
    
    # Criar gráfico de barras
    fig = px.bar(
        df_faixas,
        x='Faixa',
        y='Percentual',
        text_auto='.1f',
        title="Distribuição de candidatos por faixas de nota",
        labels={'Percentual': '% de Candidatos', 'Faixa': 'Faixa de Nota'},
        color='Faixa',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        xaxis_title="Faixa de nota",
        yaxis_title="Percentual de candidatos (%)",
        yaxis=dict(ticksuffix='%'),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _mostrar_percentis_detalhados(estatisticas: Dict[str, Any]) -> None:
    """
    Mostra os percentis detalhados no expander.
    
    Parâmetros:
    -----------
    estatisticas : Dict[str, Any]
        Dicionário com estatísticas calculadas
    """
    st.write("#### Distribuição por percentis")
    
    # Obter percentis do dicionário
    percentis = estatisticas.get('percentis', {})
    
    if not percentis:
        st.info("Dados de percentis não disponíveis.")
        return
    
    # Mostrar percentis organizados
    percentis_ordenados = sorted(percentis.items())
    for p, valor in percentis_ordenados:
        st.write(f"- **Percentil {p}:** {valor:.2f}")
    
    # Criar tabela com quartis e interpretação
    quartis_df = pd.DataFrame({
        'Quartil': ['Q1 (25%)', 'Q2 (50%)', 'Q3 (75%)'],
        'Valor': [
            percentis.get(25, 0),
            percentis.get(50, 0),
            percentis.get(75, 0)
        ],
        'Interpretação': [
            '25% dos candidatos obtiveram nota abaixo deste valor',
            '50% dos candidatos obtiveram nota abaixo deste valor (mediana)',
            '75% dos candidatos obtiveram nota abaixo deste valor'
        ]
    })
    
    st.table(quartis_df)


def _identificar_areas_extremas(df_areas: pd.DataFrame) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Identifica áreas com melhor e pior desempenho.
    
    Parâmetros:
    -----------
    df_areas : DataFrame
        DataFrame com dados por área
        
    Retorna:
    --------
    Tuple[Dict[str, Any], Dict[str, Any]]: Tupla com dicionários da melhor e pior área
    """
    if df_areas is None or df_areas.empty:
        return {}, {}
        
    # Ordenar por média
    df_ordenado = df_areas.sort_values('Media', ascending=False)
    
    # Melhor área
    melhor_area = {}
    if not df_ordenado.empty:
        row = df_ordenado.iloc[0]
        melhor_area = {
            'nome': row['Area'],
            'media': row['Media'],
            'desvio': row.get('DesvioPadrao', 0),
            'mediana': row.get('Mediana', 0)
        }
    
    # Pior área
    pior_area = {}
    if len(df_ordenado) > 1:
        row = df_ordenado.iloc[-1]
        pior_area = {
            'nome': row['Area'],
            'media': row['Media'],
            'desvio': row.get('DesvioPadrao', 0),
            'mediana': row.get('Mediana', 0)
        }
    
    return melhor_area, pior_area


def _criar_mapa_calor_faltas(df_faltas: pd.DataFrame) -> None:
    """
    Cria mapa de calor de faltas por estado e região.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame com dados de faltas
    """
    if df_faltas is None or df_faltas.empty:
        return
        
    try:
        # Verificar estrutura necessária
        if 'Estado' not in df_faltas.columns or 'Tipo de Falta' not in df_faltas.columns:
            st.warning("Estrutura de dados insuficiente para criar mapa de calor.")
            return
            
        # Criar cópia do DataFrame
        df_mapa = df_faltas.copy()
        
        # Adicionar informação de região
        df_mapa['Região'] = df_mapa['Estado'].apply(obter_regiao_do_estado)
        
        # Filtrar apenas dados de "Faltou nos dois dias"
        df_mapa = df_mapa[df_mapa['Tipo de Falta'] == 'Faltou nos dois dias']
        
        # Agrupar por região
        df_regiao = df_mapa.groupby('Região')['Percentual de Faltas'].mean().reset_index()
        
        if not df_regiao.empty:
            st.write("#### Média de faltas por região")
            
            # Criar gráfico de barras para médias por região
            fig = px.bar(
                df_regiao.sort_values('Percentual de Faltas', ascending=False),
                x='Região',
                y='Percentual de Faltas',
                text_auto='.1f',
                title="Taxa média de faltas por região",
                labels={'Percentual de Faltas': '% de Faltas', 'Região': 'Região do Brasil'},
                color='Região',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            
            fig.update_layout(
                yaxis=dict(ticksuffix='%'),
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Erro ao criar mapa de calor: {str(e)}")


def _mostrar_estatisticas_por_faixa(analise_faixas: Dict[str, Any]) -> None:
    """
    Mostra estatísticas detalhadas por faixa de desempenho.
    
    Parâmetros:
    -----------
    analise_faixas : Dict[str, Any]
        Análise por faixas de desempenho
    """
    # Verificar se temos estatísticas por faixa
    estatisticas_faixas = analise_faixas.get('estatisticas_faixas', {})
    if not estatisticas_faixas:
        st.info("Dados de estatísticas por faixa não disponíveis.")
        return
        
    st.write("#### Estatísticas por faixa de desempenho")
    
    # Criar DataFrame para exibição
    dados = []
    for faixa, stats in estatisticas_faixas.items():
        dados.append({
            'Faixa': faixa,
            'Candidatos': stats.get('contagem', 0),
            'Percentual': stats.get('percentual', 0),
            'Média': stats.get('media', 0),
            'Desvio Padrão': stats.get('desvio_padrao', 0)
        })
    
    df_stats = pd.DataFrame(dados)
    
    # Ordenar por faixas na ordem correta
    ordem_faixas = [
        'Insuficiente (abaixo de 450)',
        'Regular (450 a 600)',
        'Bom (600 a 750)',
        'Muito bom (750 a 850)',
        'Excelente (850 ou mais)'
    ]
    
    # Filtrar apenas faixas que existem nos dados
    df_stats['Faixa'] = pd.Categorical(
        df_stats['Faixa'], 
        categories=[f for f in ordem_faixas if f in df_stats['Faixa'].values],
        ordered=True
    )
    
    df_stats = df_stats.sort_values('Faixa')
    
    # Mostrar tabela formatada
    st.dataframe(
        df_stats,
        column_config={
            "Candidatos": st.column_config.NumberColumn(format="%d"),
            "Percentual": st.column_config.NumberColumn(format="%.2f%%"),
            "Média": st.column_config.NumberColumn(format="%.2f"),
            "Desvio Padrão": st.column_config.NumberColumn(format="%.2f")
        },
        hide_index=True
    )