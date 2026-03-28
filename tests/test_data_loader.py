"""Testes para data/data_loader.py — funções de carregamento e cálculo estatístico."""
import pytest
import pandas as pd
import numpy as np
from data.data_loader import calcular_seguro, filter_data_by_states, agrupar_estados_em_regioes


# ============================================================
# calcular_seguro
# ============================================================

class TestCalcularSeguro:

    def test_media_valores_validos(self):
        serie = pd.Series([10.0, 20.0, 30.0])
        assert calcular_seguro(serie, 'media') == pytest.approx(20.0)

    def test_mediana_valores_validos(self):
        serie = pd.Series([10.0, 20.0, 30.0])
        assert calcular_seguro(serie, 'mediana') == pytest.approx(20.0)

    def test_min_max(self):
        serie = pd.Series([5.0, 15.0, 25.0])
        assert calcular_seguro(serie, 'min') == pytest.approx(5.0)
        assert calcular_seguro(serie, 'max') == pytest.approx(25.0)

    def test_desvio_padrao(self):
        serie = pd.Series([10.0, 20.0, 30.0])
        resultado = calcular_seguro(serie, 'std')
        assert resultado > 0
        assert resultado == calcular_seguro(serie, 'desvio')

    def test_media_serie_vazia(self):
        serie = pd.Series([], dtype=float)
        assert calcular_seguro(serie, 'media') == 0.0

    def test_media_com_nan(self):
        serie = pd.Series([10.0, np.nan, 30.0])
        assert calcular_seguro(serie, 'media') == pytest.approx(20.0)

    def test_media_com_inf(self):
        serie = pd.Series([10.0, np.inf, 20.0])
        assert calcular_seguro(serie, 'media') == pytest.approx(15.0)

    def test_curtose_poucos_pontos(self):
        serie = pd.Series([1.0, 2.0, 3.0])
        assert calcular_seguro(serie, 'curtose') == 0.0

    def test_curtose_suficiente(self):
        serie = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        resultado = calcular_seguro(serie, 'curtose')
        assert isinstance(resultado, float)

    def test_assimetria(self):
        serie = pd.Series([1.0, 2.0, 3.0, 4.0, 100.0])
        resultado = calcular_seguro(serie, 'assimetria')
        assert resultado > 0  # Assimétrica à direita

    def test_operacao_invalida(self):
        serie = pd.Series([1.0, 2.0])
        assert calcular_seguro(serie, 'inexistente') == 0.0

    def test_desvio_padrao_um_elemento(self):
        serie = pd.Series([42.0])
        assert calcular_seguro(serie, 'std') == 0.0

    def test_float16_nao_causa_overflow(self):
        serie = pd.Series([100.0, 200.0, 300.0], dtype='float16')
        resultado = calcular_seguro(serie, 'media')
        assert resultado > 0
        assert not np.isnan(resultado)

    def test_lista_como_entrada(self):
        assert calcular_seguro([10, 20, 30], 'media') == pytest.approx(20.0)


# ============================================================
# filter_data_by_states
# ============================================================

class TestFilterDataByStates:

    def test_filtro_basico(self):
        df = pd.DataFrame({
            'SG_UF_PROVA': ['SP', 'RJ', 'MG', 'SP'],
            'valor': [1, 2, 3, 4]
        })
        resultado = filter_data_by_states(df, ['SP'])
        assert len(resultado) == 2
        assert all(resultado['SG_UF_PROVA'] == 'SP')

    def test_filtro_multiplos_estados(self):
        df = pd.DataFrame({
            'SG_UF_PROVA': ['SP', 'RJ', 'MG', 'PR'],
            'valor': [1, 2, 3, 4]
        })
        resultado = filter_data_by_states(df, ['SP', 'MG'])
        assert len(resultado) == 2

    def test_filtro_estados_vazio(self):
        df = pd.DataFrame({'SG_UF_PROVA': ['SP'], 'valor': [1]})
        resultado = filter_data_by_states(df, [])
        assert resultado.empty
        assert list(resultado.columns) == list(df.columns)

    def test_filtro_estado_inexistente(self):
        df = pd.DataFrame({'SG_UF_PROVA': ['SP', 'RJ'], 'valor': [1, 2]})
        resultado = filter_data_by_states(df, ['XX'])
        assert resultado.empty

    def test_coluna_ausente(self):
        df = pd.DataFrame({'OUTRA_COLUNA': ['SP'], 'valor': [1]})
        resultado = filter_data_by_states(df, ['SP'])
        assert resultado.empty


# ============================================================
# agrupar_estados_em_regioes
# ============================================================

class TestAgruparEstadosEmRegioes:

    @pytest.fixture
    def regioes_mapping(self):
        return {
            "Todos os estados": [],
            "Sul": ["RS", "SC", "PR"],
            "Sudeste": ["SP", "RJ", "ES", "MG"],
        }

    def test_regiao_completa(self, regioes_mapping):
        estados = ["RS", "SC", "PR"]
        resultado = agrupar_estados_em_regioes(estados, regioes_mapping)
        assert "Sul" in resultado

    def test_estados_individuais(self, regioes_mapping):
        estados = ["SP", "RS"]
        resultado = agrupar_estados_em_regioes(estados, regioes_mapping)
        # SP sozinho não completa Sudeste, RS sozinho não completa Sul
        assert "SP" in resultado or "RS" in resultado

    def test_lista_vazia(self, regioes_mapping):
        assert agrupar_estados_em_regioes([], regioes_mapping) == []
