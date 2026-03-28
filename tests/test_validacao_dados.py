"""Testes para utils/prepara_dados/validacao_dados.py — validação de completude e outliers."""
import pytest
import pandas as pd
import numpy as np
from utils.prepara_dados.validacao_dados import validar_completude_dados, verificar_outliers


class TestValidarCompletude:

    def test_completude_total(self):
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        valido, taxas = validar_completude_dados(df, ['A', 'B'])
        assert valido is True
        assert taxas['A'] == pytest.approx(1.0)
        assert taxas['B'] == pytest.approx(1.0)

    def test_completude_insuficiente(self):
        df = pd.DataFrame({'A': [1, None, None, None, None]})
        valido, taxas = validar_completude_dados(df, ['A'], limiar_completude=0.7)
        assert valido is False
        assert taxas['A'] == pytest.approx(0.2)

    def test_completude_parcial(self):
        df = pd.DataFrame({'A': [1, 2, None], 'B': [4, 5, 6]})
        valido, taxas = validar_completude_dados(df, ['A', 'B'], limiar_completude=0.5)
        assert taxas['A'] == pytest.approx(2/3, rel=0.01)
        assert taxas['B'] == pytest.approx(1.0)

    def test_coluna_ausente(self):
        df = pd.DataFrame({'A': [1, 2]})
        valido, taxas = validar_completude_dados(df, ['A', 'INEXISTENTE'])
        assert valido is False
        assert taxas['INEXISTENTE'] == 0.0

    def test_dataframe_vazio(self):
        valido, taxas = validar_completude_dados(pd.DataFrame(), ['A'])
        assert valido is False

    def test_dataframe_none(self):
        valido, taxas = validar_completude_dados(None, ['A'])
        assert valido is False


class TestVerificarOutliers:

    def test_sem_outliers(self):
        df = pd.DataFrame({'A': [10, 11, 12, 13, 14, 15]})
        resultado = verificar_outliers(df, ['A'])
        assert resultado['A']['quantidade'] == 0

    def test_com_outliers_iqr(self):
        df = pd.DataFrame({'A': [10, 11, 12, 13, 14, 15, 100]})
        resultado = verificar_outliers(df, ['A'], metodo='iqr')
        assert resultado['A']['quantidade'] >= 1

    def test_coluna_ausente(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        resultado = verificar_outliers(df, ['B'])
        assert resultado['B']['quantidade'] == 0

    def test_dataframe_vazio(self):
        resultado = verificar_outliers(pd.DataFrame(), ['A'])
        assert resultado['A']['quantidade'] == 0
