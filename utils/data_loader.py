import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import gc
import os
from typing import Dict, List, Any, Optional, Union, Tuple

# ------------------------------------------------------------
# FUNÇÕES DE CARREGAMENTO DE DADOS
# ------------------------------------------------------------

@st.cache_data(ttl=3600)
def load_data_for_tab(tab_name: str, apenas_filtros: bool = False):
    """
    Carrega dados otimizados para uma aba específica.
    Versão simplificada e de alto desempenho.
    
    Parâmetros:
    -----------
    tab_name : str
        Nome da aba para a qual carregar os dados ('geral', 'aspectos_sociais', 'desempenho')
    apenas_filtros : bool, default=False
        Se True, carrega apenas os dados mínimos necessários para os filtros
        
    Retorna:
    --------
    DataFrame: Dados carregados para a aba especificada
    """

    try:
        # Para filtros, carregar apenas a coluna de UF do arquivo genérico
        if apenas_filtros:
            return pd.read_parquet("sample_localizacao.parquet", 
                                  engine='pyarrow')
        
        # Carregar dados específicos da aba
        dados_especificos = pd.read_parquet(f"sample_{tab_name.lower()}.parquet", engine='pyarrow')
        
        # Aplicar otimização de tipos de dados
        dados_especificos = optimize_dtypes(dados_especificos, tab_name)
        
        return dados_especificos
        
    except Exception as e:
        st.error(f"Erro ao carregar dados para aba {tab_name}: {e}")
        return pd.DataFrame()


# ------------------------------------------------------------
# FUNÇÕES DE FILTRO E PROCESSAMENTO
# ------------------------------------------------------------

def filter_data_by_states(df: pd.DataFrame, estados: List[str]) -> pd.DataFrame:
    """
    Filtra os dados por estados selecionados de forma eficiente.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados completos
    estados : List[str]
        Lista de siglas de estados para filtrar
        
    Retorna:
    --------
    DataFrame: Dados filtrados apenas para os estados selecionados
    """
    if not estados or 'SG_UF_PROVA' not in df.columns:
        return pd.DataFrame(columns=df.columns)
    
    # Filtrar e criar uma view em vez de cópia para economizar memória
    return df[df['SG_UF_PROVA'].isin(estados)]


def agrupar_estados_em_regioes(estados: List[str], regioes_mapping: Dict[str, List[str]]) -> List[str]:
    """
    Converte lista de estados em formato mais amigável, agrupando por regiões.
    
    Parâmetros:
    -----------
    estados : List[str]
        Lista com os códigos dos estados selecionados
    regioes_mapping : Dict[str, List[str]]
        Dicionário que mapeia regiões para seus estados
        
    Retorna:
    --------
    List[str]: Lista de regiões completas e estados individuais
    """
    if not estados:
        return []
    
    estados_set = set(estados)
    estados_restantes = estados_set.copy()
    resultado = []
    
    # Verificar regiões completas
    for regiao, estados_regiao in regioes_mapping.items():
        if regiao == "Todos os estados":
            continue
        
        # Se todos os estados da região estão selecionados
        if all(estado in estados_set for estado in estados_regiao):
            resultado.append(regiao)
            # Remover estes estados da lista de restantes
            estados_restantes -= set(estados_regiao)
    
    # Adicionar estados individuais restantes
    resultado.extend(sorted(estados_restantes))
    
    return resultado


def calcular_seguro(serie_dados, operacao='media'):
    """
    Calcula estatísticas de forma segura, lidando com valores missing.
    
    Parâmetros:
    -----------
    serie_dados : Series, array ou lista
        Dados para calcular a estatística
    operacao : str, default='media'
        Tipo de operação: 'media', 'mediana', 'min', 'max', 'std'
        
    Retorna:
    --------
    float: Resultado do cálculo estatístico ou 0.0 em caso de erro
    """
    try:
        # Converter para array NumPy e remover valores inválidos
        if isinstance(serie_dados, pd.Series):
            array_dados = serie_dados.dropna().values
        else:
            array_dados = np.array(serie_dados)
            array_dados = array_dados[~np.isnan(array_dados)]
        
        if len(array_dados) == 0:
            return 0.0
            
        # Calcular estatística solicitada
        if operacao == 'media':
            return float(np.mean(array_dados))
        elif operacao == 'mediana':
            return float(np.median(array_dados))
        elif operacao == 'min':
            return float(np.min(array_dados))
        elif operacao == 'max':
            return float(np.max(array_dados))
        elif operacao == 'std':
            return float(np.std(array_dados))
        else:
            return 0.0
    except Exception as e:
        print(f"Erro ao calcular {operacao}: {e}")
        return 0.0


# ------------------------------------------------------------
# FUNÇÕES DE OTIMIZAÇÃO DE MEMÓRIA
# ------------------------------------------------------------

def optimize_dtypes(df: pd.DataFrame, dtypes) -> pd.DataFrame:
    """
    Otimiza tipos de dados para reduzir uso de memória.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame a ser otimizado
        
    Retorna:
    --------
    DataFrame: DataFrame com tipos de dados otimizados
    """
    if df.empty:
        return df
    
    # Otimizar inteiros
    arquivo_dtypes = f'dtypes_{dtypes}.json'

    dtypes = pd.read_json(arquivo_dtypes, orient='index', typ='series')

    df = df.astype(dtypes)
    
    return df


def release_memory(objects):
    """
    Libera memória de objetos Python.
    
    Parâmetros:
    -----------
    objects : Object ou List[Object]
        Objeto ou lista de objetos a serem liberados
    """
    if not isinstance(objects, list):
        objects = [objects]
    
    for obj in objects:
        del obj
    
    # Forçar coleta de lixo
    gc.collect()