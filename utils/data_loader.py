import streamlit as st
import pandas as pd
import numpy as np

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
        else:
            return 0.0
        return float(resultado) if np.isfinite(resultado) else 0.0
    except Exception as e:
        print(f"Erro no cálculo: {e}")
        return 0.0

def prepare_data_for_line_chart(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping):
    """Prepara dados para o gráfico de linhas na aba Geral."""
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
    return pd.DataFrame(dados_grafico)

def prepare_infrastructure_data(microdados, race_mapping, infraestrutura_mapping):
    """Prepara dados para análise de infraestrutura por raça."""
    infra_desempenho = microdados.groupby(['TP_COR_RACA', 'NU_INFRAESTRUTURA']).size().reset_index(name='count')
    raca_total = microdados.groupby('TP_COR_RACA').size().reset_index(name='total')
    infra_desempenho = infra_desempenho.merge(raca_total, on='TP_COR_RACA')
    infra_desempenho['percentual'] = (infra_desempenho['count'] / infra_desempenho['total']) * 100
    infra_desempenho['Raça'] = infra_desempenho['TP_COR_RACA'].map(race_mapping)
    infra_desempenho['infraestrutura'] = infra_desempenho['NU_INFRAESTRUTURA'].map(infraestrutura_mapping)
    return infra_desempenho