import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

@st.cache_data(ttl=3600)  # Cache válido por 1 hora
def generate_aggregated_data_cache(df, estados, groupby_col):
    """Cache de dados pré-agregados por estado/região."""
    return df.groupby([groupby_col, 'SG_UF_PROVA']).agg({
        'NU_NOTA_CN': ['mean', 'median', 'std'],
        'NU_NOTA_CH': ['mean', 'median', 'std'],
        'NU_NOTA_LC': ['mean', 'median', 'std'],
        'NU_NOTA_MT': ['mean', 'median', 'std']
    }).reset_index()

@st.cache_data
def load_data_for_tab(tab_name):
    """Carrega dados otimizados para uma aba específica."""
    file_path = f"sample_{tab_name.lower()}.parquet"
    
    try:
        dados = pd.read_parquet(file_path)
        dtypes = pd.read_json(f"dtypes_{tab_name.lower()}.json", typ='series')
        dados = dados.astype(dtypes)
        
        # Converter colunas de notas para float64 apenas se existirem no dataframe
        colunas_notas = [col for col in ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'] 
                         if col in dados.columns]
        for col in colunas_notas:
            dados[col] = dados[col].astype('float64')
            
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar dados para aba {tab_name}: {e}")
        return pd.DataFrame()
    
    # Criar amostras progressivas em diferentes tamanhos
@st.cache_data
def load_data_for_tab_with_sampling(tab_name, sample_level='normal'):
    """Carrega dados com amostragem adaptativa baseada no nível de detalhe."""
    file_path = f"sample_{tab_name.lower()}.parquet"
    
    try:
        # Definir fração da amostra com base no nível solicitado
        sample_fraction = {
            'ultra_fast': 0.01,  # 1% da amostra para navegação/filtragem muito rápida
            'fast': 0.05,        # 5% para análise exploratória rápida
            'normal': 0.25,      # 25% para análise detalhada (padrão)
            'detailed': 0.5,     # 50% para análise mais profunda
            'full': 1.0          # 100% para análise completa (lenta)
        }.get(sample_level, 0.25)
        
        # Carregar apenas uma amostra dos dados para economizar memória e tempo
        dados = pd.read_parquet(file_path, engine='pyarrow')
        
        # Aplicar amostragem estratificada por estado para manter representatividade
        if sample_fraction < 1.0:
            # Amostragem estratificada por estado
            dados_amostrados = dados.groupby('SG_UF_PROVA', group_keys=False).apply(
                lambda x: x.sample(frac=sample_fraction, random_state=42)
            )
            return dados_amostrados
        
        return dados
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

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

