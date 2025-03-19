import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px

@st.cache_data
def load_data():
    """Carrega os dados do ENEM e faz pré-processamento inicial."""
    microdados = pd.DataFrame(pd.read_csv('sample.csv', sep=';', encoding='ISO-8859-1'))
    dtypes = pd.read_json("dtypes.json", typ='series')
    dados = microdados.astype(dtypes)
    
    # Converter colunas de notas para float64
    colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    for col in colunas_notas:
        dados[col] = dados[col].astype('float64')
    return dados

def filter_data_by_states(microdados, estados_selecionados):
    """Filtra os dados por estados selecionados."""
    if not estados_selecionados:
        return pd.DataFrame(columns=microdados.columns)
    return microdados[microdados['SG_UF_PROVA'].isin(estados_selecionados)].copy()

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
        elif operacao == 'std':
            resultado = np.std(array_limpa)
        elif operacao == 'curtose':
            resultado = stats.kurtosis(array_limpa)
        elif operacao == 'assimetria':
            resultado = stats.skew(array_limpa)
        else:
            return 0.0
        return float(resultado) if np.isfinite(resultado) else 0.0
    except Exception as e:
        print(f"Erro no cálculo: {e}")
        return 0.0

def prepare_data_for_histogram(df, coluna, competencia_mapping):
    """
    Prepara os dados para o histograma de notas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    coluna : str
        Nome da coluna (área de conhecimento) a ser analisada
    competencia_mapping : dict
        Dicionário com mapeamento das colunas para nomes legíveis
        
    Retorna:
    --------
    dict: Dicionário com os dados necessários para criar o histograma
    """
    # Filtrar valores inválidos (notas -1 e 0) para análises mais precisas
    df_valido = df[df[coluna] > 0]
    
    # Obter nome amigável da área de conhecimento
    nome_area = competencia_mapping[coluna]
    
    # Calcular estatísticas
    media = calcular_seguro(df_valido[coluna])
    mediana = calcular_seguro(df_valido[coluna], 'mediana')
    min_valor = calcular_seguro(df_valido[coluna], 'min')
    max_valor = calcular_seguro(df_valido[coluna], 'max')
    desvio_padrao = calcular_seguro(df_valido[coluna], 'std')
    curtose = calcular_seguro(df_valido[coluna], 'curtose')
    skillness = calcular_seguro(df_valido[coluna], 'assimetria')
    
    # Retornar dicionário com todos os dados necessários
    return {
        'df': df_valido,
        'coluna': coluna,
        'nome_area': nome_area,
        'estatisticas': {
            'media': media,
            'mediana': mediana,
            'min_valor': min_valor,
            'max_valor': max_valor,
            'desvio_padrao': desvio_padrao,
            'curtose': curtose,
            'skillness': skillness
        }
    }


def criar_histograma(dados_histograma):
    """
    Cria um histograma formatado com informações estatísticas.
    
    Parâmetros:
    -----------
    dados_histograma : dict
        Dicionário com os dados para criar o histograma
        
    Retorna:
    --------
    Figure: Objeto de figura Plotly com o histograma formatado
    """
    # Extrair dados do dicionário
    df = dados_histograma['df']
    coluna = dados_histograma['coluna']
    nome_area = dados_histograma['nome_area']
    stats = dados_histograma['estatisticas']
    
    media = stats['media']
    mediana = stats['mediana']
    min_valor = stats['min_valor']
    max_valor = stats['max_valor']
    desvio_padrao = stats['desvio_padrao']
    curtose = stats['curtose']
    skillness = stats['skillness']

    # Criar histograma
    fig = px.histogram(
        df,
        x=coluna,
        nbins=30,
        histnorm='percent',
        title=f"Histograma das notas - {nome_area}",
        labels={coluna: f"Nota ({nome_area})"},
        opacity=0.7,
        color_discrete_sequence=['#3366CC']
    )
    
    # Adicionar linhas de média e mediana
    fig.add_vline(x=media, line_dash="dash", line_color="red")
    fig.add_vline(x=mediana, line_dash="dash", line_color="green")
    
    # Formatação do layout
    fig.update_layout(
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
    
    # Adicionar caixa de estatísticas
    stats_text = f"""
    <b>Estatísticas:</b><br>
    Média: {media:.2f}<br>
    Mediana: {mediana:.2f}<br>
    Mínimo: {min_valor:.2f}<br>
    Máximo: {max_valor:.2f}<br>
    desvio Padrão: {desvio_padrao:.2f}<br>
    Curtose: {curtose:.2f}<br>
    Assimetria: {skillness:.2f}
    """

    fig.add_annotation(
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
    
    return fig

def prepare_data_for_line_chart(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """
    Prepara dados para o gráfico de linhas na aba Geral.
    Inclui uma linha adicional com a média geral de todas as competências.
    """
    dados_grafico = []
    dados_medias_gerais = []  # Lista separada para médias gerais
    
    # Primeiro, calculamos a média para cada área e estado
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        medias_estado_atual = []  # Lista para armazenar médias deste estado
        
        for area in colunas_notas:
            dados_filtrados = dados_estado[dados_estado[area] > 0][area]
            media_area = round(calcular_seguro(dados_filtrados), 2)
            
            # Adicionar ao DataFrame de resultados
            dados_grafico.append({
                'Estado': estado,
                'Área': competencia_mapping[area],
                'Média': media_area
            })
            
            # Armazenar para cálculo da média geral
            medias_estado_atual.append(media_area)
        
        # Calcular e armazenar a média geral para este estado
        if medias_estado_atual:
            media_geral_estado = round(np.mean(medias_estado_atual), 2)
            
            # Armazenar em lista separada
            dados_medias_gerais.append({
                'Estado': estado,
                'Área': 'Média Geral',
                'Média': media_geral_estado,
            })
    
    # Combinar os DataFrames com médias gerais primeiro
    df_medias_gerais = pd.DataFrame(dados_medias_gerais)
    df_outras_areas = pd.DataFrame(dados_grafico)
    df_final = pd.concat([df_medias_gerais, df_outras_areas], ignore_index=True)
    
    return df_final



def prepare_data_for_absence_chart(microdados_estados, estados_selecionados, colunas_presenca):
    """
    Prepara os dados para o gráfico de faltas por estado e área de conhecimento.
    Inclui faltas na Redação mesmo sem a coluna TP_PRESENCA_REDACAO.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os dados dos candidatos
    estados_selecionados : lista
        Lista de estados selecionados para análise
    colunas_presenca : dict
        Dicionário mapeando as colunas de presença com seus nomes para exibição
        
    Retorna:
    --------
    DataFrame: Dados preparados para o gráfico de linha de faltas
    """
    dados_grafico = []
    dados_gerais = []  # Lista separada para os dados gerais
    
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        total_candidatos = len(dados_estado)
        
        if total_candidatos == 0:
            continue  # Pular estados sem candidatos
        
        # Contar faltas gerais (quem faltou em pelo menos uma prova)
        faltas_gerais = len(dados_estado[dados_estado['TP_PRESENCA_GERAL'] == 0])
        percentual_faltas_gerais = (faltas_gerais / total_candidatos * 100) if total_candidatos > 0 else 0
        
        # Armazenar dados gerais em lista separada
        dados_gerais.append({
            'Estado': estado,
            'Área': 'Geral (qualquer prova)',
            'Percentual de Faltas': percentual_faltas_gerais
        })
        
        # Contar faltas por área específica
        for coluna, nome_area in colunas_presenca.items():
            # Para a redação, precisamos tratar de forma especial
            if coluna == 'TP_PRESENCA_REDACAO':
                # Verificar se temos a coluna de nota de redação
                if 'NU_NOTA_REDACAO' in dados_estado.columns:
                    # Considerar como falta se a nota é 0, nula, ou menor ou igual a zero
                    faltas_redacao = len(dados_estado[(dados_estado['NU_NOTA_REDACAO'].isna()) | 
                                                      (dados_estado['NU_NOTA_REDACAO'] <= 0)])
                    percentual_faltas_area = (faltas_redacao / total_candidatos * 100) if total_candidatos > 0 else 0
                    
                    dados_grafico.append({
                        'Estado': estado,
                        'Área': 'Redação',
                        'Percentual de Faltas': percentual_faltas_area
                    })
            elif coluna in dados_estado.columns:
                faltas_area = len(dados_estado[dados_estado[coluna] == 0])
                percentual_faltas_area = (faltas_area / total_candidatos * 100) if total_candidatos > 0 else 0
                
                dados_grafico.append({
                    'Estado': estado,
                    'Área': nome_area,
                    'Percentual de Faltas': percentual_faltas_area
                })
    
    # Combinar os DataFrames com dados gerais primeiro
    df_geral = pd.DataFrame(dados_gerais)
    df_areas = pd.DataFrame(dados_grafico)
    df_final = pd.concat([df_geral, df_areas], ignore_index=True)
    
    return df_final