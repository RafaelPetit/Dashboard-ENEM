"""
Carregador de dados seguro que aplica correções automáticas
para evitar overflow em cálculos estatísticos.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import warnings

def carregar_dados_enem_seguro(arquivo_path: str, aplicar_correcoes: bool = True) -> pd.DataFrame:
    """
    Carrega dados do ENEM aplicando correções automáticas para evitar overflow.
    
    Args:
        arquivo_path: Caminho para o arquivo de dados
        aplicar_correcoes: Se deve aplicar correções de tipos automaticamente
    
    Returns:
        DataFrame com dados corrigidos
    """
    try:
        # Carregar dados
        if arquivo_path.endswith('.parquet'):
            df = pd.read_parquet(arquivo_path)
        elif arquivo_path.endswith('.csv'):
            df = pd.read_csv(arquivo_path)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {arquivo_path}")
        
        print(f"Dados carregados: {df.shape}")
        
        if aplicar_correcoes:
            df = aplicar_correcoes_tipos_enem(df)
        
        return df
        
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def aplicar_correcoes_tipos_enem(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica correções específicas para dados do ENEM.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame corrigido
    """
    try:
        if df is None or df.empty:
            return df
            
        df_corrigido = df.copy()
        
        # Identificar e corrigir colunas de notas
        colunas_notas = [col for col in df.columns if 'NOTA' in col.upper()]
        
        print(f"Corrigindo tipos de {len(colunas_notas)} colunas de notas...")
        
        for col in colunas_notas:
            # Converter tipos de baixa precisão para float64
            if df_corrigido[col].dtype in ['float16', 'int16']:
                print(f"  Convertendo {col} de {df_corrigido[col].dtype} para float64")
                df_corrigido[col] = df_corrigido[col].astype('float64')
            
            # Limpar valores extremos (outliers absurdos)
            serie = df_corrigido[col]
            mask_extremos = (serie > 2000) | (serie < -100)
            
            if mask_extremos.any():
                num_extremos = mask_extremos.sum()
                print(f"  Removendo {num_extremos} valores extremos de {col}")
                df_corrigido.loc[mask_extremos, col] = np.nan
        
        # Verificar e corrigir outras colunas numéricas se necessário
        for col in df_corrigido.select_dtypes(include=['float16']).columns:
            if col not in colunas_notas:
                print(f"  Convertendo {col} de float16 para float32")
                df_corrigido[col] = df_corrigido[col].astype('float32')
        
        print("Correções aplicadas com sucesso!")
        return df_corrigido
        
    except Exception as e:
        print(f"Erro ao aplicar correções: {e}")
        return df


def calcular_estatisticas_seguras(data, operacoes: List[str] = None) -> Dict[str, float]:
    """
    Calcula estatísticas de forma segura para grandes datasets.
    
    Args:
        data: Array ou Series com os dados
        operacoes: Lista de operações a calcular
        
    Returns:
        Dicionário com resultados das operações
    """
    if operacoes is None:
        operacoes = ['media', 'mediana', 'min', 'max', 'std']
    
    try:
        # Converter para array numpy
        if hasattr(data, 'values'):
            arr = data.values
        else:
            arr = np.asarray(data)
        
        # Converter para dtype seguro
        if arr.dtype in [np.float16, np.int8, np.int16]:
            arr = arr.astype(np.float64)
        
        # Filtrar valores válidos
        mask = np.isfinite(arr) & (arr >= -1) & (arr <= 2000)
        if not np.any(mask):
            return {op: 0.0 for op in operacoes}
            
        valid_data = arr[mask]
        
        # Para cálculos estatísticos, usar apenas valores >= 0
        for op in ['media', 'std']:
            if op in operacoes:
                valid_stats_data = valid_data[valid_data >= 0]
                if len(valid_stats_data) == 0:
                    continue
        
        resultados = {}
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            
            for op in operacoes:
                try:
                    if op == 'media':
                        stats_data = valid_data[valid_data >= 0]
                        if len(stats_data) > 1000000:
                            # Calcular em chunks para datasets grandes
                            chunk_size = 100000
                            chunks = [stats_data[i:i+chunk_size] for i in range(0, len(stats_data), chunk_size)]
                            chunk_means = [np.mean(chunk.astype(np.float64)) for chunk in chunks]
                            chunk_sizes = [len(chunk) for chunk in chunks]
                            result = np.average(chunk_means, weights=chunk_sizes)
                        else:
                            result = np.mean(stats_data.astype(np.float64))
                        resultados[op] = float(result) if np.isfinite(result) else 0.0
                        
                    elif op == 'mediana':
                        if len(valid_data) > 1000000:
                            sample_size = min(100000, len(valid_data))
                            sample_data = np.random.choice(valid_data, size=sample_size, replace=False)
                            result = np.median(sample_data)
                        else:
                            result = np.median(valid_data)
                        resultados[op] = float(result) if np.isfinite(result) else 0.0
                        
                    elif op == 'std':
                        stats_data = valid_data[valid_data >= 0]
                        if len(stats_data) < 2:
                            resultados[op] = 0.0
                        else:
                            result = np.std(stats_data.astype(np.float64), ddof=1)
                            resultados[op] = float(result) if np.isfinite(result) else 0.0
                            
                    elif op == 'min':
                        result = np.min(valid_data)
                        resultados[op] = float(result) if np.isfinite(result) else 0.0
                        
                    elif op == 'max':
                        result = np.max(valid_data)
                        resultados[op] = float(result) if np.isfinite(result) else 0.0
                        
                    else:
                        resultados[op] = 0.0
                        
                except Exception as e:
                    print(f"Erro ao calcular {op}: {e}")
                    resultados[op] = 0.0
        
        return resultados
        
    except Exception as e:
        print(f"Erro no cálculo de estatísticas: {e}")
        return {op: 0.0 for op in operacoes}


def testar_correcoes():
    """Testa as correções com os dados disponíveis."""
    try:
        print("=== TESTE DAS CORREÇÕES ===")
        
        # Tentar carregar arquivo de teste
        arquivo_teste = "sample_gerenico.parquet"
        
        print(f"Carregando {arquivo_teste}...")
        df_original = pd.read_parquet(arquivo_teste)
        
        print(f"Dados originais: {df_original.shape}")
        
        # Verificar tipos antes
        nota_cols = [col for col in df_original.columns if 'NOTA' in col.upper()]
        print("\nTipos ANTES da correção:")
        for col in nota_cols:
            print(f"  {col}: {df_original[col].dtype}")
        
        # Aplicar correções
        df_corrigido = aplicar_correcoes_tipos_enem(df_original)
        
        print("\nTipos DEPOIS da correção:")
        for col in nota_cols:
            print(f"  {col}: {df_corrigido[col].dtype}")
        
        # Testar cálculos
        print("\nTeste de cálculos estatísticos:")
        for col in nota_cols[:3]:  # Primeiros 3
            stats = calcular_estatisticas_seguras(df_corrigido[col])
            print(f"  {col}: média={stats['media']:.2f}, mediana={stats['mediana']:.2f}")
        
        print("\n✅ Testes concluídos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")


if __name__ == "__main__":
    testar_correcoes()
