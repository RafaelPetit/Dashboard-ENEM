"""Testes para utils/helpers/constants.py e mappings.py — integridade dos mapeamentos."""
import pytest
from utils.helpers.constants import (
    COLUNAS_NOTAS,
    COMPETENCIA_MAPPING,
    REGIOES_MAPPING,
    CONFIG_PROCESSAMENTO,
    CONFIG_VISUALIZACAO,
    LIMIARES,
    LIMIARES_ESTATISTICOS,
    LIMIARES_PROCESSAMENTO,
    VARIAVEIS_CATEGORICAS,
    VARIAVEIS_SOCIAIS,
)
from utils.helpers.mappings import get_mappings


class TestMappingsIntegridade:

    def test_get_mappings_retorna_dict(self):
        m = get_mappings()
        assert isinstance(m, dict)

    def test_colunas_notas(self):
        assert len(COLUNAS_NOTAS) == 5
        for col in COLUNAS_NOTAS:
            assert col.startswith('NU_NOTA_')

    def test_competencia_mapping_completo(self):
        assert len(COMPETENCIA_MAPPING) == 5
        for col in COLUNAS_NOTAS:
            assert col in COMPETENCIA_MAPPING

    def test_regioes_mapping_cinco_regioes(self):
        assert len(REGIOES_MAPPING) == 5
        for regiao in ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']:
            assert regiao in REGIOES_MAPPING

    def test_todos_estados_mapeados(self):
        todos_estados = set()
        for estados in REGIOES_MAPPING.values():
            todos_estados.update(estados)
        assert len(todos_estados) == 27  # 26 estados + DF

    def test_config_processamento(self):
        assert 'max_amostras_scatter' in CONFIG_PROCESSAMENTO
        assert CONFIG_PROCESSAMENTO['max_amostras_scatter'] > 0

    def test_config_visualizacao(self):
        assert 'altura_padrao_grafico' in CONFIG_VISUALIZACAO
        assert CONFIG_VISUALIZACAO['altura_padrao_grafico'] > 0

    def test_limiares_estatisticos(self):
        assert 'correlacao_fraca' in LIMIARES_ESTATISTICOS
        assert 'correlacao_moderada' in LIMIARES_ESTATISTICOS
        assert LIMIARES_ESTATISTICOS['correlacao_fraca'] < LIMIARES_ESTATISTICOS['correlacao_moderada']

    def test_variaveis_categoricas_tem_mapeamento(self):
        for var, config in VARIAVEIS_CATEGORICAS.items():
            assert 'nome' in config, f"{var} sem 'nome'"
            assert 'mapeamento' in config, f"{var} sem 'mapeamento'"

    def test_variaveis_sociais_tem_mapeamento(self):
        for var, config in VARIAVEIS_SOCIAIS.items():
            assert 'nome' in config, f"{var} sem 'nome'"
            assert 'mapeamento' in config, f"{var} sem 'mapeamento'"
