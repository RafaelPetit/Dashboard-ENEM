"""Testes para utils/prepara_dados/prepara_dados_analise_geral.py — P0.7"""
import pytest
import pandas as pd
import numpy as np
from utils.prepara_dados.prepara_dados_analise_geral import (
    preparar_dados_grafico_faltas,
    preparar_dados_evasao,
    preparar_dados_media_geral_estados,
)


# ============================================================
# P0.7 — preparar_dados_grafico_faltas
# ============================================================

class TestPrepararDadosGraficoFaltas:
    """Testes de rede de seguranca para preparar_dados_grafico_faltas."""

    @pytest.fixture
    def microdados_presenca(self):
        """Microdados com TP_PRESENCA_GERAL simulando presenca/faltas."""
        return pd.DataFrame({
            'SG_UF_PROVA': ['SP'] * 100 + ['RJ'] * 100,
            'SG_REGIAO': ['Sudeste'] * 200,
            'TP_PRESENCA_GERAL': (
                [3] * 70 + [0] * 15 + [1] * 8 + [2] * 7 +  # SP
                [3] * 80 + [0] * 10 + [1] * 5 + [2] * 5     # RJ
            ),
        })

    def test_retorna_colunas_esperadas(self, microdados_presenca):
        """Given: dados validos. When: preparar. Then: colunas corretas."""
        resultado = preparar_dados_grafico_faltas(
            microdados_presenca, ['SP', 'RJ']
        )
        assert not resultado.empty
        assert 'Estado' in resultado.columns
        assert 'Tipo de Falta' in resultado.columns
        assert 'Percentual de Faltas' in resultado.columns

    def test_tres_tipos_de_falta_por_estado(self, microdados_presenca):
        """Given: 2 estados. When: preparar. Then: 3 tipos por estado = 6 linhas."""
        resultado = preparar_dados_grafico_faltas(
            microdados_presenca, ['SP', 'RJ']
        )
        assert len(resultado) == 6  # 2 estados x 3 tipos

    def test_tipos_de_falta_corretos(self, microdados_presenca):
        """Given: dados validos. When: preparar. Then: tipos incluem 'somente'."""
        resultado = preparar_dados_grafico_faltas(
            microdados_presenca, ['SP', 'RJ']
        )
        tipos = resultado['Tipo de Falta'].unique().tolist()
        assert 'Faltou nos dois dias' in tipos
        assert 'Faltou somente no primeiro dia' in tipos
        assert 'Faltou somente no segundo dia' in tipos

    def test_percentuais_somam_menos_100(self, microdados_presenca):
        """Given: dados por estado. When: preparar.
        Then: soma de faltas < 100% (o resto sao presentes)."""
        resultado = preparar_dados_grafico_faltas(
            microdados_presenca, ['SP']
        )
        soma = resultado['Percentual de Faltas'].sum()
        # SP: 15 + 8 + 7 = 30% de faltas
        assert soma == pytest.approx(30.0, abs=0.1)

    def test_dataframe_vazio(self):
        """Given: df vazio. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_grafico_faltas(pd.DataFrame(), ['SP'])
        assert resultado.empty

    def test_dataframe_none(self):
        """Given: None. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_grafico_faltas(None, ['SP'])
        assert resultado.empty

    def test_estados_vazio(self, microdados_presenca):
        """Given: lista de estados vazia. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_grafico_faltas(microdados_presenca, [])
        assert resultado.empty

    def test_estado_inexistente(self, microdados_presenca):
        """Given: estado nao existe nos dados. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_grafico_faltas(microdados_presenca, ['XX'])
        assert resultado.empty

    def test_agrupamento_por_regiao(self, microdados_presenca):
        """Given: agrupar por regiao. When: preparar com coluna SG_REGIAO.
        Then: retorna dados agrupados."""
        resultado = preparar_dados_grafico_faltas(
            microdados_presenca, ['Sudeste'],
            coluna_agrupamento='SG_REGIAO'
        )
        assert not resultado.empty
        assert resultado.iloc[0]['Estado'] == 'Sudeste'

    def test_coluna_area_adicionada(self, microdados_presenca):
        """Given: dados validos. When: preparar. Then: coluna 'Area' presente."""
        resultado = preparar_dados_grafico_faltas(
            microdados_presenca, ['SP']
        )
        assert 'Área' in resultado.columns


# ============================================================
# P0.7 — preparar_dados_evasao
# ============================================================

class TestPrepararDadosEvasao:
    """Testes de rede de seguranca para preparar_dados_evasao."""

    @pytest.fixture
    def microdados_evasao(self):
        """Microdados para analise de evasao."""
        return pd.DataFrame({
            'SG_UF_PROVA': ['SP'] * 100 + ['RJ'] * 100,
            'TP_PRESENCA_GERAL': (
                [3] * 70 + [0] * 15 + [1] * 8 + [2] * 7 +
                [3] * 80 + [0] * 10 + [1] * 5 + [2] * 5
            ),
        })

    def test_retorna_colunas_esperadas(self, microdados_evasao):
        """Given: dados validos. When: preparar. Then: colunas corretas."""
        resultado = preparar_dados_evasao(microdados_evasao, ['SP', 'RJ'])
        assert not resultado.empty
        assert 'Estado' in resultado.columns
        assert 'Métrica' in resultado.columns
        assert 'Valor' in resultado.columns

    def test_quatro_metricas_por_estado(self, microdados_evasao):
        """Given: 2 estados. When: preparar.
        Then: 4 metricas por estado = 8 linhas."""
        resultado = preparar_dados_evasao(microdados_evasao, ['SP', 'RJ'])
        assert len(resultado) == 8  # 2 estados x 4 metricas

    def test_metricas_presentes(self, microdados_evasao):
        """Given: dados validos. When: preparar. Then: 4 metricas corretas."""
        resultado = preparar_dados_evasao(microdados_evasao, ['SP'])
        metricas = resultado['Métrica'].unique().tolist()
        assert 'Presentes' in metricas
        assert 'Faltantes Dia 1' in metricas
        assert 'Faltantes Dia 2' in metricas
        assert 'Faltantes Ambos' in metricas

    def test_percentuais_somam_100(self, microdados_evasao):
        """Given: dados de 1 estado. When: preparar.
        Then: soma dos percentuais = 100%."""
        resultado = preparar_dados_evasao(microdados_evasao, ['SP'])
        soma = resultado['Valor'].sum()
        assert soma == pytest.approx(100.0, abs=0.1)

    def test_presentes_sp_70_porcento(self, microdados_evasao):
        """Given: SP com 70 presentes de 100. When: preparar.
        Then: Presentes = 70%."""
        resultado = preparar_dados_evasao(microdados_evasao, ['SP'])
        presentes = resultado[
            (resultado['Estado'] == 'SP') & (resultado['Métrica'] == 'Presentes')
        ]['Valor'].iloc[0]
        assert presentes == pytest.approx(70.0, abs=0.1)

    def test_dataframe_vazio(self):
        """Given: df vazio. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_evasao(pd.DataFrame(), ['SP'])
        assert resultado.empty

    def test_dataframe_none(self):
        """Given: None. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_evasao(None, ['SP'])
        assert resultado.empty

    def test_sem_coluna_presenca(self):
        """Given: df sem TP_PRESENCA_GERAL. When: preparar. Then: vazio."""
        df = pd.DataFrame({'SG_UF_PROVA': ['SP'], 'OUTRA': [1]})
        resultado = preparar_dados_evasao(df, ['SP'])
        assert resultado.empty


# ============================================================
# P0.7 (extra) — preparar_dados_media_geral_estados
# ============================================================

class TestPrepararDadosMediaGeralEstados:
    """Testes para preparar_dados_media_geral_estados."""

    @pytest.fixture
    def microdados_media(self):
        return pd.DataFrame({
            'SG_UF_PROVA': ['SP'] * 50 + ['RJ'] * 50,
            'NU_NOTA_CN': [500.0] * 50 + [450.0] * 50,
            'NU_NOTA_MT': [600.0] * 50 + [550.0] * 50,
        })

    def test_retorna_media_por_estado(self, microdados_media):
        """Given: SP e RJ com notas diferentes. When: preparar.
        Then: medias corretas por estado."""
        resultado = preparar_dados_media_geral_estados(
            microdados_media, ['SP', 'RJ'],
            ['NU_NOTA_CN', 'NU_NOTA_MT']
        )
        assert not resultado.empty
        assert 'Local' in resultado.columns
        assert 'Média Geral' in resultado.columns
        assert len(resultado) == 2

    def test_media_sp_correta(self, microdados_media):
        """Given: SP com CN=500, MT=600. When: preparar.
        Then: media geral SP = 550."""
        resultado = preparar_dados_media_geral_estados(
            microdados_media, ['SP'], ['NU_NOTA_CN', 'NU_NOTA_MT']
        )
        media_sp = resultado[resultado['Local'] == 'SP']['Média Geral'].iloc[0]
        assert media_sp == pytest.approx(550.0, abs=0.1)

    def test_dataframe_vazio(self):
        """Given: df vazio. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_media_geral_estados(
            pd.DataFrame(), [], []
        )
        assert resultado.empty
