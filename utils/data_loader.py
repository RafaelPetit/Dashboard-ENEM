import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

@st.cache_data
def load_data():
    """Carrega os dados do ENEM e faz pré-processamento inicial."""
    microdados = pd.DataFrame(pd.read_csv('sample.csv', sep=';', encoding='ISO-8859-1'))
    dtypes = pd.read_json("dtypes - Copia.json", typ='series')
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
    
def agrupar_estados_em_regioes(estados_selecionados, regioes_mapping):
    """
    Converte uma lista de estados em um formato mais amigável,
    agrupando por regiões quando todos os estados de uma região estiverem presentes.
    
    Parâmetros:
    -----------
    estados_selecionados : list
        Lista com os códigos dos estados selecionados
    regioes_mapping : dict
        Dicionário que mapeia regiões para seus estados
        
    Retorna:
    --------
    str
        String formatada com regiões e/ou estados para exibição
    """
    # Converter para conjunto para operações mais eficientes
    estados_set = set(estados_selecionados)
    estados_restantes = estados_set.copy()
    resultado = []
    
    # Verificar regiões completas
    for regiao, estados_regiao in regioes_mapping.items():
        # Se todos os estados da região estão selecionados
        if all(estado in estados_set for estado in estados_regiao):
            resultado.append(regiao)
            # Remover estes estados da lista de restantes
            for estado in estados_regiao:
                if estado in estados_restantes:
                    estados_restantes.remove(estado)
    
    # Adicionar estados individuais restantes
    if estados_restantes:
        resultado.extend(sorted(estados_restantes))
    
    return resultado

