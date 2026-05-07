"""Testes para utils/estatisticas/estatistica_desempenho.py — P0.5"""
import pytest
import pandas as pd
import numpy as np
from utils.estatisticas.estatistica_desempenho import (
    calcular_correlacao_competencias,
    analisar_desempenho_por_estado,
)


# ============================================================
# P0.5 — calcular_correlacao_competencias
# ============================================================

class TestCalcularCorrelacaoCompetencias:
    """Testes de rede de seguranca para calcular_correlacao_competencias."""

    def test_correlacao_perfeita_positiva(self):
        """Given: X e Y perfeitamente correlacionados. When: calcular.
        Then: correlacao ~1.0, interpretacao 'Forte positiva'."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [100.0, 200.0, 300.0, 400.0, 500.0] * 10,
            'NU_NOTA_MT': [100.0, 200.0, 300.0, 400.0, 500.0] * 10,
        })
        correlacao, interpretacao = calcular_correlacao_competencias(df, 'NU_NOTA_CN', 'NU_NOTA_MT')
        assert correlacao == pytest.approx(1.0, abs=0.01)
        assert 'Forte' in interpretacao
        assert 'positiva' in interpretacao

    def test_correlacao_negativa(self):
        """Given: X e Y negativamente correlacionados. When: calcular.
        Then: correlacao < 0, interpretacao contem 'negativa'."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [100.0, 200.0, 300.0, 400.0, 500.0] * 10,
            'NU_NOTA_MT': [500.0, 400.0, 300.0, 200.0, 100.0] * 10,
        })
        correlacao, interpretacao = calcular_correlacao_competencias(df, 'NU_NOTA_CN', 'NU_NOTA_MT')
        assert correlacao < 0
        assert 'negativa' in interpretacao

    def test_sem_correlacao(self):
        """Given: X e Y independentes. When: calcular.
        Then: correlacao proxima de 0."""
        np.random.seed(42)
        df = pd.DataFrame({
            'NU_NOTA_CN': np.random.uniform(100, 900, 100),
            'NU_NOTA_MT': np.random.uniform(100, 900, 100),
        })
        correlacao, _ = calcular_correlacao_competencias(df, 'NU_NOTA_CN', 'NU_NOTA_MT')
        assert abs(correlacao) < 0.3

    def test_dataframe_vazio(self):
        """Given: DataFrame vazio. When: calcular. Then: retorna 0, msg."""
        correlacao, interpretacao = calcular_correlacao_competencias(
            pd.DataFrame(), 'NU_NOTA_CN', 'NU_NOTA_MT'
        )
        assert correlacao == 0.0
        assert 'insuficientes' in interpretacao.lower() or 'Dados' in interpretacao

    def test_coluna_inexistente(self):
        """Given: coluna nao existe. When: calcular. Then: retorna 0."""
        df = pd.DataFrame({'NU_NOTA_CN': [100.0, 200.0]})
        correlacao, _ = calcular_correlacao_competencias(df, 'NU_NOTA_CN', 'FAKE')
        assert correlacao == 0.0

    def test_exclui_zeros(self):
        """Given: dados com zeros. When: calcular. Then: zeros excluidos."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [0.0, 0.0] + [100.0, 200.0, 300.0, 400.0, 500.0] * 10,
            'NU_NOTA_MT': [0.0, 0.0] + [100.0, 200.0, 300.0, 400.0, 500.0] * 10,
        })
        correlacao, _ = calcular_correlacao_competencias(df, 'NU_NOTA_CN', 'NU_NOTA_MT')
        # Sem os zeros, correlacao deve ser perfeita
        assert correlacao == pytest.approx(1.0, abs=0.01)

    def test_amostras_insuficientes(self):
        """Given: menos de 30 amostras validas. When: calcular. Then: fallback."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [100.0, 200.0, 300.0],
            'NU_NOTA_MT': [100.0, 200.0, 300.0],
        })
        correlacao, interpretacao = calcular_correlacao_competencias(df, 'NU_NOTA_CN', 'NU_NOTA_MT')
        assert correlacao == 0.0
        assert 'insuficientes' in interpretacao.lower()

    def test_retorna_float_e_string(self):
        """Given: dados validos. When: calcular.
        Then: retorno e (float, str)."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [100.0 + i for i in range(50)],
            'NU_NOTA_MT': [100.0 + i * 0.5 for i in range(50)],
        })
        correlacao, interpretacao = calcular_correlacao_competencias(df, 'NU_NOTA_CN', 'NU_NOTA_MT')
        assert isinstance(correlacao, float)
        assert isinstance(interpretacao, str)


# ============================================================
# P0.5 (extra) — analisar_desempenho_por_estado
# ============================================================

class TestAnalisarDesempenhoPorEstado:
    """Testes para analisar_desempenho_por_estado."""

    @pytest.fixture
    def df_grafico(self):
        """DataFrame no formato produzido por preparar_dados_grafico_linha_desempenho."""
        return pd.DataFrame({
            'Estado': ['SP', 'SP', 'RJ', 'RJ', 'MG', 'MG'],
            'Área': ['Média Geral', 'Matemática', 'Média Geral', 'Matemática', 'Média Geral', 'Matemática'],
            'Média': [600.0, 550.0, 580.0, 520.0, 570.0, 510.0],
        })

    def test_identifica_melhor_e_pior_estado(self, df_grafico):
        """Given: SP > RJ > MG em Media Geral. When: analisar.
        Then: melhor=SP, pior=MG."""
        resultado = analisar_desempenho_por_estado(df_grafico, 'Média Geral')
        assert resultado['melhor_estado'] is not None
        assert resultado['melhor_estado']['Estado'] == 'SP'
        assert resultado['pior_estado'] is not None
        assert resultado['pior_estado']['Estado'] == 'MG'

    def test_calcula_desvio_padrao(self, df_grafico):
        """Given: medias [600, 580, 570]. When: analisar. Then: desvio > 0."""
        resultado = analisar_desempenho_por_estado(df_grafico, 'Média Geral')
        assert resultado['desvio_padrao'] > 0

    def test_dataframe_vazio(self):
        """Given: df vazio. When: analisar. Then: fallback."""
        resultado = analisar_desempenho_por_estado(pd.DataFrame(), 'Média Geral')
        assert resultado['melhor_estado'] is None
        assert resultado['pior_estado'] is None

    def test_area_inexistente(self, df_grafico):
        """Given: area nao existe. When: analisar. Then: fallback."""
        resultado = analisar_desempenho_por_estado(df_grafico, 'Fake Area')
        assert resultado['melhor_estado'] is None

    def test_um_unico_estado(self):
        """Given: 1 estado apenas. When: analisar. Then: melhor=pior=unico."""
        df = pd.DataFrame({
            'Estado': ['SP'],
            'Área': ['Média Geral'],
            'Média': [600.0],
        })
        resultado = analisar_desempenho_por_estado(df, 'Média Geral')
        assert resultado['melhor_estado'] is not None
        assert resultado['melhor_estado']['Estado'] == 'SP'
