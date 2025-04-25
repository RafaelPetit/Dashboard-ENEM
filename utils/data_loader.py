import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import pyarrow as pa
import pyarrow.parquet as pq
import os
from joblib import Memory

# Configuração de cache persistente para computações intensivas
CACHE_DIR = ".streamlit/cache"
memory = Memory(CACHE_DIR, verbose=0)

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
def load_data_for_tab(tab_name, optimize_memory=True):
    """Carrega dados otimizados para uma aba específica."""
    file_path = f"sample_{tab_name.lower()}.parquet"
    
    try:
        # Carregar os dados usando PyArrow para melhor desempenho e controle de memória
        dados = pd.read_parquet(file_path, engine='pyarrow')
        
        # Carregar tipos de dados otimizados
        try:
            dtypes = pd.read_json(f"dtypes_{tab_name.lower()}.json", typ='series')
            dados = dados.astype(dtypes)
        except Exception as e:
            print(f"Aviso: Não foi possível aplicar dtypes otimizados: {e}")
        
        # Otimizar tipos de dados para economizar memória
        if optimize_memory:
            dados = optimize_dtypes(dados)
            
        # Converter colunas de notas para float32 (mais leve que float64) apenas se existirem no dataframe
        colunas_notas = [col for col in ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'] 
                         if col in dados.columns]
        for col in colunas_notas:
            dados[col] = dados[col].astype('float32')
            
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar dados para aba {tab_name}: {e}")
        return pd.DataFrame()

@st.cache_data
def load_data_columns(tab_name, columns, sample_frac=None):
    """Carrega apenas colunas específicas de um arquivo parquet."""
    file_path = f"sample_{tab_name.lower()}.parquet"
    
    try:
        dados = pd.read_parquet(file_path, columns=columns, engine='pyarrow')
        
        # Aplicar amostragem se especificado
        if sample_frac is not None and sample_frac < 1.0:
            dados = dados.sample(frac=sample_frac, random_state=42)
            
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar colunas específicas: {e}")
        return pd.DataFrame()

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
        array_dados = np.array(serie_dados, dtype=np.float32)  # float32 em vez de float64
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
    list
        Lista de regiões completas e estados individuais
    """
    # Converter para conjunto para operações mais eficientes
    estados_set = set(estados_selecionados)
    estados_restantes = estados_set.copy()
    resultado = []
    
    # Verificar regiões completas
    for regiao, estados_regiao in regioes_mapping.items():
        # Ignorar a entrada "Todos os estados"
        if regiao == "Todos os estados":
            continue
            
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

def optimize_dtypes(df):
    """Otimiza tipos de dados para reduzir uso de memória."""
    # Converter inteiros para tipos menores quando possível
    for col in df.select_dtypes(include=['int64']).columns:
        # Analisar alcance dos valores
        col_min, col_max = df[col].min(), df[col].max()
        
        # Escolher tipo mais eficiente
        if col_min >= 0:  # Valores não negativos
            if col_max < 256:
                df[col] = df[col].astype(np.uint8)
            elif col_max < 65536:
                df[col] = df[col].astype(np.uint16)
            elif col_max < 4294967296:
                df[col] = df[col].astype(np.uint32)
        else:  # Valores que podem ser negativos
            if col_min > -128 and col_max < 128:
                df[col] = df[col].astype(np.int8)
            elif col_min > -32768 and col_max < 32768:
                df[col] = df[col].astype(np.int16)
            elif col_min > -2147483648 and col_max < 2147483648:
                df[col] = df[col].astype(np.int32)
    
    # Converter floats para tipos menores quando possível
    for col in df.select_dtypes(include=['float64']).columns:
        # Para notas (sabemos que são entre 0-1000, precisão de 0.1 é suficiente)
        if col.startswith('NU_NOTA_'):
            df[col] = df[col].astype(np.float32)
            
    # Otimizar strings
    for col in df.select_dtypes(include=['object']).columns:
        # Se os valores únicos são limitados, converter para categoria
        if df[col].nunique() / len(df) < 0.5:  # Limiar arbitrário de 50%
            df[col] = df[col].astype('category')
            
    return df

@memory.cache
def compute_intensive_task(df_hash, task_type, **kwargs):
    """
    Executa e armazena em cache tarefas computacionalmente intensivas.
    O parâmetro df_hash permite identificar unicamente cada DataFrame.
    """
    # Recuperar dados do DataFrame do kwargs
    df = kwargs.pop('df')
    
    # Diferentes tipos de tarefas computacionais intensivas
    if task_type == "correlation_matrix":
        cols = kwargs.get('columns', df.select_dtypes(include=['number']).columns)
        return df[cols].corr()
    
    elif task_type == "aggregation":
        group_cols = kwargs.get('group_by', ['SG_UF_PROVA'])
        agg_cols = kwargs.get('agg_columns', ['NU_NOTA_CN', 'NU_NOTA_CH'])
        agg_funcs = kwargs.get('agg_funcs', ['mean', 'median', 'std'])
        
        agg_dict = {col: agg_funcs for col in agg_cols}
        return df.groupby(group_cols).agg(agg_dict).reset_index()
        
    # Adicione mais tipos de tarefas conforme necessário
    
    return None