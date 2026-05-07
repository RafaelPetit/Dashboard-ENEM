"""Testes para data/data_loader.py:optimize_dtypes — P0.3
Os parquets ja vem pre-otimizados pelo notebook Filtragem.ipynb:
- Notas divididas por 10, -1 substituido por NaN, dtype float32
- Colunas int com range pequeno ja em int8
Estes testes validam que optimize_dtypes aplica o schema JSON corretamente."""
import pytest
import pandas as pd
import numpy as np
import json
from data.data_loader import optimize_dtypes


class TestOptimizeDtypes:
    """Testes de rede de seguranca para optimize_dtypes."""

    # --- Comportamento basico ---

    def test_dataframe_vazio_retorna_vazio(self):
        """Given: DataFrame vazio. When: optimize. Then: retorna vazio."""
        resultado = optimize_dtypes(pd.DataFrame(), 'geral')
        assert resultado.empty

    def test_aplica_dtypes_do_json(self):
        """Given: DF com colunas do 'geral'. When: optimize.
        Then: dtypes do JSON aplicados (ex: SG_UF_PROVA vira category)."""
        df = pd.DataFrame({
            'SG_UF_PROVA': ['SP'],
            'SG_REGIAO': ['Sudeste'],
            'TP_PRESENCA_CN': [3],
            'NU_NOTA_CN': [500.0],
        })
        resultado = optimize_dtypes(df, 'geral')
        assert resultado['SG_UF_PROVA'].dtype.name == 'category'

    def test_json_com_coluna_extra_nao_crasha(self):
        """FIX P1.8: Se o JSON tem colunas que nao existem no DF,
        elas sao ignoradas."""
        df = pd.DataFrame({
            'SG_UF_PROVA': ['SP'],
            'NU_NOTA_CN': [500.0],
        })
        resultado = optimize_dtypes(df, 'geral')
        assert not resultado.empty

    def test_localizacao_aplica_schema(self):
        """Given: dataset 'localizacao'. When: optimize.
        Then: aplica schema sem erro."""
        df = pd.DataFrame({
            'SG_UF_PROVA': ['SP'],
            'SG_REGIAO': ['Sudeste'],
        })
        resultado = optimize_dtypes(df, 'localizacao')
        assert 'SG_UF_PROVA' in resultado.columns

    # --- Validacao de dados pre-processados (como vem do parquet) ---

    def test_parquet_geral_ja_tem_notas_float32(self):
        """Os parquets ja vem com notas em float32 (pre-processado no notebook)."""
        df = pd.read_parquet('data/sample_geral.parquet', engine='pyarrow')
        notas = [c for c in df.columns if c.startswith('NU_NOTA_')]
        for col in notas:
            assert df[col].dtype == np.float32, f"{col} deveria ser float32, é {df[col].dtype}"

    def test_parquet_geral_notas_ja_divididas(self):
        """Notas no parquet ja estao divididas por 10 (range 0-1000)."""
        df = pd.read_parquet('data/sample_geral.parquet', engine='pyarrow')
        notas_validas = df['NU_NOTA_CN'].dropna()
        notas_validas = notas_validas[notas_validas > 0]
        assert notas_validas.max() <= 1000.0, "Notas deveriam estar divididas por 10"
        assert notas_validas.min() > 0, "Notas validas deveriam ser > 0"

    def test_parquet_geral_menos1_e_nan(self):
        """Valores -1 no parquet ja foram substituidos por NaN."""
        df = pd.read_parquet('data/sample_geral.parquet', engine='pyarrow')
        for col in [c for c in df.columns if c.startswith('NU_NOTA_')]:
            assert (df[col] == -1).sum() == 0, f"{col} ainda tem -1"
            assert (df[col] == -0.1).sum() == 0, f"{col} ainda tem -0.1"

    def test_parquet_desempenho_notas_pre_processadas(self):
        """Dataset desempenho tambem tem notas pre-processadas."""
        df = pd.read_parquet('data/sample_desempenho.parquet', engine='pyarrow')
        notas = [c for c in df.columns if c.startswith('NU_NOTA_')]
        for col in notas:
            assert df[col].dtype == np.float32, f"{col} deveria ser float32"
            assert (df[col] == -1).sum() == 0, f"{col} ainda tem -1"

    def test_optimize_preserva_dados_pre_processados(self):
        """optimize_dtypes nao deve alterar valores ja pre-processados."""
        df = pd.read_parquet('data/sample_geral.parquet', engine='pyarrow')
        nota_antes = df['NU_NOTA_CN'].iloc[0]
        resultado = optimize_dtypes(df, 'geral')
        nota_depois = resultado['NU_NOTA_CN'].iloc[0]
        # Valor deve ser identico (nenhuma transformacao aplicada)
        if pd.notna(nota_antes):
            assert nota_antes == pytest.approx(nota_depois, abs=0.01)
