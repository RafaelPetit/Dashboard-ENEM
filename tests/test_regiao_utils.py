"""Testes para utils/helpers/regiao_utils.py — mapeamento estado/região."""
import pytest
import pandas as pd
from utils.helpers.regiao_utils import (
    obter_regiao_do_estado,
    obter_estados_da_regiao,
    obter_todas_regioes,
    adicionar_regiao_aos_estados,
    agrupar_dados_por_regiao,
)


class TestObterRegiao:

    def test_estado_sudeste(self):
        assert obter_regiao_do_estado('SP') == 'Sudeste'
        assert obter_regiao_do_estado('RJ') == 'Sudeste'
        assert obter_regiao_do_estado('MG') == 'Sudeste'
        assert obter_regiao_do_estado('ES') == 'Sudeste'

    def test_estado_sul(self):
        assert obter_regiao_do_estado('PR') == 'Sul'
        assert obter_regiao_do_estado('SC') == 'Sul'
        assert obter_regiao_do_estado('RS') == 'Sul'

    def test_estado_norte(self):
        assert obter_regiao_do_estado('AM') == 'Norte'

    def test_estado_nordeste(self):
        assert obter_regiao_do_estado('BA') == 'Nordeste'

    def test_estado_centro_oeste(self):
        assert obter_regiao_do_estado('DF') == 'Centro-Oeste'
        assert obter_regiao_do_estado('GO') == 'Centro-Oeste'

    def test_estado_invalido(self):
        assert obter_regiao_do_estado('XX') == ''
        assert obter_regiao_do_estado('') == ''


class TestObterEstadosDaRegiao:

    def test_sul(self):
        estados = obter_estados_da_regiao('Sul')
        assert set(estados) == {'RS', 'SC', 'PR'}

    def test_sudeste(self):
        estados = obter_estados_da_regiao('Sudeste')
        assert set(estados) == {'SP', 'RJ', 'MG', 'ES'}

    def test_regiao_invalida(self):
        assert obter_estados_da_regiao('Inexistente') == []


class TestObterTodasRegioes:

    def test_cinco_regioes(self):
        regioes = obter_todas_regioes()
        assert len(regioes) == 5
        for r in ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']:
            assert r in regioes


class TestAdicionarRegiaoAosEstados:

    def test_adiciona_coluna(self):
        df = pd.DataFrame({'Estado': ['SP', 'RS', 'BA']})
        resultado = adicionar_regiao_aos_estados(df)
        assert 'Região' in resultado.columns
        assert resultado.loc[resultado['Estado'] == 'SP', 'Região'].iloc[0] == 'Sudeste'
        assert resultado.loc[resultado['Estado'] == 'RS', 'Região'].iloc[0] == 'Sul'

    def test_dataframe_vazio(self):
        df = pd.DataFrame({'Estado': []})
        resultado = adicionar_regiao_aos_estados(df)
        assert resultado.empty

    def test_none(self):
        assert adicionar_regiao_aos_estados(None) is None


class TestAgruparDadosPorRegiao:

    def test_agrupamento_basico(self):
        df = pd.DataFrame({
            'Estado': ['SP', 'RJ', 'PR', 'SC'],
            'Média': [500.0, 480.0, 490.0, 510.0]
        })
        resultado = agrupar_dados_por_regiao(df, coluna_estado='Estado', coluna_valor='Média')
        assert 'Estado' in resultado.columns  # Renomeado de Região
        assert len(resultado) == 2  # Sudeste e Sul

    def test_dataframe_vazio(self):
        df = pd.DataFrame({'Estado': [], 'Média': []})
        resultado = agrupar_dados_por_regiao(df)
        assert resultado.empty
