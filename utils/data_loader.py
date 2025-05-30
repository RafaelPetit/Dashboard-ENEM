import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import pyarrow as pa
import pyarrow.parquet as pq
import os
from joblib import Memory
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable

# Constantes de configuração
CACHE_DIR = ".streamlit/cache"
SAMPLE_FRACTIONS = {
    'ultra_fast': 0.01,  # 1% da amostra para navegação/filtragem muito rápida
    'fast': 0.05,        # 5% para análise exploratória rápida
    'normal': 0.25,      # 25% para análise detalhada (padrão)
    'detailed': 0.5,     # 50% para análise mais profunda
    'full': 1.0          # 100% para análise completa (lenta)
}

# Configuração de cache persistente para computações intensivas
memory = Memory(CACHE_DIR, verbose=0)


# ------------------------------------------------------------
# FUNÇÕES DE CARREGAMENTO DE DADOS
# ------------------------------------------------------------

@st.cache_data(ttl=3600)  # Cache válido por 1 hora
def generate_aggregated_data_cache(
    df: pd.DataFrame, 
    estados: List[str], 
    groupby_col: str
) -> pd.DataFrame:
    """
    Gera cache de dados pré-agregados por estado/região.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados brutos
    estados : List[str]
        Lista de estados a incluir na agregação
    groupby_col : str
        Coluna adicional para agrupar além do estado
        
    Retorna:
    --------
    DataFrame: Dados agregados com estatísticas por estado
    """
    # Filtrar por estados selecionados
    if estados and 'SG_UF_PROVA' in df.columns:
        df_filtrado = df[df['SG_UF_PROVA'].isin(estados)]
    else:
        df_filtrado = df
    
    # Verificar se temos dados para agregar
    if df_filtrado.empty:
        return pd.DataFrame()
    
    # Agregar dados com estatísticas
    return df_filtrado.groupby([groupby_col, 'SG_UF_PROVA']).agg({
        'NU_NOTA_CN': ['mean', 'median', 'std'],
        'NU_NOTA_CH': ['mean', 'median', 'std'],
        'NU_NOTA_LC': ['mean', 'median', 'std'],
        'NU_NOTA_MT': ['mean', 'median', 'std']
    }).reset_index()


@st.cache_data
def load_data_for_tab(tab_name: str, optimize_memory: bool = True) -> pd.DataFrame:
    """
    Carrega dados otimizados para uma aba específica.
    
    Parâmetros:
    -----------
    tab_name : str
        Nome da aba para a qual carregar os dados
    optimize_memory : bool, default=True
        Se True, aplica otimizações de memória aos dados carregados
        
    Retorna:
    --------
    DataFrame: Dados carregados para a aba especificada
    """
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
            
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar dados para aba {tab_name}: {e}")
        return pd.DataFrame()


@st.cache_data
def load_data_columns(
    tab_name: str, 
    columns: List[str], 
    sample_frac: Optional[float] = None
) -> pd.DataFrame:
    """
    Carrega apenas colunas específicas de um arquivo parquet.
    
    Parâmetros:
    -----------
    tab_name : str
        Nome da aba para a qual carregar os dados
    columns : List[str]
        Lista de nomes de colunas para carregar
    sample_frac : float, opcional
        Fração dos dados a amostrar (entre 0 e 1)
        
    Retorna:
    --------
    DataFrame: Dados carregados com apenas as colunas especificadas
    """
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
def load_data_for_tab_with_sampling(
    tab_name: str, 
    sample_level: str = 'normal'
) -> pd.DataFrame:
    """
    Carrega dados com amostragem adaptativa baseada no nível de detalhe.
    
    Parâmetros:
    -----------
    tab_name : str
        Nome da aba para a qual carregar os dados
    sample_level : str, default='normal'
        Nível de amostragem a ser aplicado ('ultra_fast', 'fast', 'normal', 'detailed', 'full')
        
    Retorna:
    --------
    DataFrame: Dados amostrados de acordo com o nível especificado
    """
    file_path = f"sample_{tab_name.lower()}.parquet"
    
    try:
        # Definir fração da amostra com base no nível solicitado
        sample_fraction = SAMPLE_FRACTIONS.get(sample_level, 0.25)
        
        # Carregar apenas uma amostra dos dados para economizar memória e tempo
        dados = pd.read_parquet(file_path, engine='pyarrow')
        
        # Aplicar amostragem estratificada por estado para manter representatividade
        if sample_fraction < 1.0 and 'SG_UF_PROVA' in dados.columns:
            # Amostragem estratificada por estado
            dados_amostrados = dados.groupby('SG_UF_PROVA', group_keys=False).apply(
                lambda x: x.sample(frac=sample_fraction, random_state=42)
            )
            return dados_amostrados
        
        return dados
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


# ------------------------------------------------------------
# FUNÇÕES DE FILTRO E PROCESSAMENTO
# ------------------------------------------------------------

def filter_data_by_states(
    microdados: pd.DataFrame, 
    estados_selecionados: List[str]
) -> pd.DataFrame:
    """
    Filtra os dados por estados selecionados.
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com dados completos
    estados_selecionados : List[str]
        Lista de siglas de estados para filtrar
        
    Retorna:
    --------
    DataFrame: Dados filtrados apenas para os estados selecionados
    """
    # Verificar se há estados selecionados e se a coluna de estado existe
    if not estados_selecionados or 'SG_UF_PROVA' not in microdados.columns:
        return pd.DataFrame(columns=microdados.columns)
    
    # Filtrar e retornar uma cópia para evitar modificar o original
    return microdados[microdados['SG_UF_PROVA'].isin(estados_selecionados)].copy()


def calcular_seguro(
    serie_dados: Union[pd.Series, np.ndarray, List[float]], 
    operacao: str = 'media'
) -> float:
    """
    Calcula estatísticas de forma segura, lidando com valores missing ou inválidos.
    
    Parâmetros:
    -----------
    serie_dados : Series, array ou lista
        Dados para calcular a estatística
    operacao : str, default='media'
        Tipo de operação: 'media', 'mediana', 'min', 'max', 'std', 'curtose', 'assimetria'
        
    Retorna:
    --------
    float: Resultado do cálculo estatístico ou 0.0 em caso de erro
    """
    try:
        if isinstance(serie_dados, pd.Series):
            # Para pandas Series, remover valores NaN primeiro
            serie_limpa = serie_dados.dropna()
            if len(serie_limpa) == 0:
                return 0.0
            array_dados = np.array(serie_limpa, dtype=np.float32)
        else:
            # Para arrays ou listas, converter para array NumPy
            if len(serie_dados) == 0:
                return 0.0
            array_dados = np.array(serie_dados, dtype=np.float32)
        
        # Remover valores não finitos (NaN, inf)
        array_limpa = array_dados[np.isfinite(array_dados)]
        if len(array_limpa) == 0:
            return 0.0
        
        # Calcular a estatística solicitada
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
        
        # Garantir que o resultado seja um número finito
        return float(resultado) if np.isfinite(resultado) else 0.0
    
    except Exception as e:
        print(f"Erro no cálculo de '{operacao}': {e}")
        return 0.0


def agrupar_estados_em_regioes(
    estados_selecionados: List[str], 
    regioes_mapping: Dict[str, List[str]]
) -> List[str]:
    """
    Converte uma lista de estados em um formato mais amigável,
    agrupando por regiões quando todos os estados de uma região estiverem presentes.
    
    Parâmetros:
    -----------
    estados_selecionados : List[str]
        Lista com os códigos dos estados selecionados
    regioes_mapping : Dict[str, List[str]]
        Dicionário que mapeia regiões para seus estados
        
    Retorna:
    --------
    List[str]: Lista de regiões completas e estados individuais
    """
    # Verificar se há estados selecionados
    if not estados_selecionados:
        return []
    
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


# ------------------------------------------------------------
# FUNÇÕES DE OTIMIZAÇÃO DE MEMÓRIA
# ------------------------------------------------------------

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
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
    # Verificar se o DataFrame está vazio
    if df.empty:
        return df
    
    # Fazer uma cópia para não modificar o original
    df_otimizado = df.copy()
    
    # Converter inteiros para tipos menores quando possível
    for col in df_otimizado.select_dtypes(include=['int64']).columns:
        # Analisar alcance dos valores
        col_min, col_max = df_otimizado[col].min(), df_otimizado[col].max()
        
        # Escolher tipo mais eficiente
        if col_min >= 0:  # Valores não negativos
            if col_max < 256:
                df_otimizado[col] = df_otimizado[col].astype(np.uint8)
            elif col_max < 65536:
                df_otimizado[col] = df_otimizado[col].astype(np.uint16)
            elif col_max < 4294967296:
                df_otimizado[col] = df_otimizado[col].astype(np.uint32)
        else:  # Valores que podem ser negativos
            if col_min > -128 and col_max < 128:
                df_otimizado[col] = df_otimizado[col].astype(np.int8)
            elif col_min > -32768 and col_max < 32768:
                df_otimizado[col] = df_otimizado[col].astype(np.int16)
            elif col_min > -2147483648 and col_max < 2147483648:
                df_otimizado[col] = df_otimizado[col].astype(np.int32)
    
    # Converter floats para tipos menores quando possível
    for col in df_otimizado.select_dtypes(include=['float64']).columns:
        # Para notas (sabemos que são entre 0-1000, precisão de 0.1 é suficiente)
        if any(col.startswith(prefix) for prefix in ['NU_NOTA_']):
            df_otimizado[col] = df_otimizado[col].astype(np.float32)
            
    # Otimizar strings
    for col in df_otimizado.select_dtypes(include=['object']).columns:
        # Se os valores únicos são limitados, converter para categoria
        if df_otimizado[col].nunique() / len(df_otimizado) < 0.5:  # Limiar arbitrário de 50%
            df_otimizado[col] = df_otimizado[col].astype('category')
            
    return df_otimizado


# ------------------------------------------------------------
# FUNÇÕES DE CACHE DE COMPUTAÇÃO INTENSIVA
# ------------------------------------------------------------

@memory.cache
def compute_intensive_task(
    df_hash: str, 
    task_type: str, 
    **kwargs: Any
) -> Optional[pd.DataFrame]:
    """
    Executa e armazena em cache tarefas computacionalmente intensivas.
    O parâmetro df_hash permite identificar unicamente cada DataFrame.
    
    Parâmetros:
    -----------
    df_hash : str
        Hash único para identificar o DataFrame
    task_type : str
        Tipo de tarefa a executar ('correlation_matrix', 'aggregation', etc.)
    **kwargs : Any
        Parâmetros específicos para cada tipo de tarefa
        
    Retorna:
    --------
    DataFrame: Resultado da computação ou None em caso de erro
    """
    # Recuperar dados do DataFrame do kwargs
    df = kwargs.pop('df', None)
    if df is None or df.empty:
        return None
    
    try:
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
    
    except Exception as e:
        print(f"Erro ao executar tarefa '{task_type}': {e}")
        return None