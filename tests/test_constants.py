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

    # ===== Testes P3.2: variaveis_sociais derivada de variaveis_categoricas =====

    def test_variaveis_sociais_sem_campo_ordem(self):
        """P3.2: variaveis_sociais nao deve ter campo 'ordem'."""
        for var, config in VARIAVEIS_SOCIAIS.items():
            assert 'ordem' not in config, f"{var} tem 'ordem' — deveria ter sido removido"

    def test_variaveis_sociais_overrides_nomes(self):
        """P3.2: nomes divergentes devem estar corretos em cada dicionario."""
        assert VARIAVEIS_CATEGORICAS['TP_DEPENDENCIA_ADM_ESC']['nome'] == 'Dependência Administrativa'
        assert VARIAVEIS_SOCIAIS['TP_DEPENDENCIA_ADM_ESC']['nome'] == 'Tipo de Escola'
        assert VARIAVEIS_CATEGORICAS['TP_FAIXA_SALARIAL']['nome'] == 'Faixa Salarial'
        assert VARIAVEIS_SOCIAIS['TP_FAIXA_SALARIAL']['nome'] == 'Renda Familiar'

    def test_variaveis_sociais_mapeamentos_identicos_para_chaves_compartilhadas(self):
        """P3.2: mapeamentos devem ser identicos para chaves em comum."""
        for var in VARIAVEIS_SOCIAIS:
            if var in VARIAVEIS_CATEGORICAS:
                assert VARIAVEIS_SOCIAIS[var]['mapeamento'] == VARIAVEIS_CATEGORICAS[var]['mapeamento'], \
                    f"Mapeamento de {var} diverge entre sociais e categoricas"

    def test_variaveis_sociais_exclui_tp_escola(self):
        """P3.2: TP_ESCOLA nao deve estar em variaveis_sociais."""
        assert 'TP_ESCOLA' not in VARIAVEIS_SOCIAIS
        assert 'TP_ESCOLA' in VARIAVEIS_CATEGORICAS

    def test_variaveis_sociais_inclui_q005(self):
        """P3.2: Q005 (Pessoas na Residencia) deve estar apenas em sociais."""
        assert 'Q005' in VARIAVEIS_SOCIAIS
        assert 'Q005' not in VARIAVEIS_CATEGORICAS
        assert VARIAVEIS_SOCIAIS['Q005']['nome'] == 'Pessoas na Residência'
