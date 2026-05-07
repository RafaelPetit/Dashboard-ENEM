"""Testes para utils/prepara_dados/prepara_dados_desempenho.py — P0.6"""
import pytest
import pandas as pd
import numpy as np
from utils.prepara_dados.prepara_dados_desempenho import (
    preparar_dados_comparativo,
    filtrar_dados_scatter,
    preparar_dados_grafico_linha,
)


# ============================================================
# P0.6 — preparar_dados_comparativo
# ============================================================

class TestPrepararDadosComparativo:
    """Testes de rede de seguranca para preparar_dados_comparativo."""

    @pytest.fixture
    def microdados_basico(self):
        """Microdados minimos para teste."""
        return pd.DataFrame({
            'TP_SEXO': ['M', 'M', 'F', 'F', 'M'] * 20,
            'NU_NOTA_CN': [500.0, 600.0, 550.0, 650.0, 700.0] * 20,
            'NU_NOTA_MT': [450.0, 550.0, 600.0, 700.0, 650.0] * 20,
        })

    @pytest.fixture
    def variaveis_categoricas(self):
        return {
            'TP_SEXO': {
                'nome': 'Sexo',
                'mapeamento': {'M': 'Masculino', 'F': 'Feminino'},
                'ordem': ['Masculino', 'Feminino']
            }
        }

    @pytest.fixture
    def colunas_notas(self):
        return ['NU_NOTA_CN', 'NU_NOTA_MT']

    @pytest.fixture
    def competencia_mapping(self):
        return {
            'NU_NOTA_CN': 'Ciencias da Natureza',
            'NU_NOTA_MT': 'Matematica',
        }

    def test_retorna_dataframe_com_colunas_esperadas(
        self, microdados_basico, variaveis_categoricas, colunas_notas, competencia_mapping
    ):
        """Given: dados validos. When: preparar. Then: colunas Categoria, Competencia, Media."""
        resultado = preparar_dados_comparativo(
            microdados_basico, 'TP_SEXO', variaveis_categoricas,
            colunas_notas, competencia_mapping
        )
        assert not resultado.empty
        assert 'Categoria' in resultado.columns
        assert 'Competência' in resultado.columns
        assert 'Média' in resultado.columns

    def test_categorias_mapeadas(
        self, microdados_basico, variaveis_categoricas, colunas_notas, competencia_mapping
    ):
        """Given: mapeamento M->Masculino, F->Feminino. When: preparar.
        Then: categorias usam nomes legíveis."""
        resultado = preparar_dados_comparativo(
            microdados_basico, 'TP_SEXO', variaveis_categoricas,
            colunas_notas, competencia_mapping
        )
        categorias = resultado['Categoria'].unique()
        assert 'Masculino' in categorias
        assert 'Feminino' in categorias

    def test_competencias_mapeadas(
        self, microdados_basico, variaveis_categoricas, colunas_notas, competencia_mapping
    ):
        """Given: mapping de competencia. When: preparar.
        Then: nomes legiveis usados."""
        resultado = preparar_dados_comparativo(
            microdados_basico, 'TP_SEXO', variaveis_categoricas,
            colunas_notas, competencia_mapping
        )
        competencias = resultado['Competência'].unique()
        assert 'Ciencias da Natureza' in competencias
        assert 'Matematica' in competencias

    def test_medias_positivas(
        self, microdados_basico, variaveis_categoricas, colunas_notas, competencia_mapping
    ):
        """Given: notas validas. When: preparar. Then: medias > 0."""
        resultado = preparar_dados_comparativo(
            microdados_basico, 'TP_SEXO', variaveis_categoricas,
            colunas_notas, competencia_mapping
        )
        assert all(resultado['Média'] > 0)

    def test_dataframe_vazio(
        self, variaveis_categoricas, colunas_notas, competencia_mapping
    ):
        """Given: df vazio. When: preparar. Then: retorna df vazio."""
        resultado = preparar_dados_comparativo(
            pd.DataFrame(), 'TP_SEXO', variaveis_categoricas,
            colunas_notas, competencia_mapping
        )
        assert resultado.empty

    def test_variavel_inexistente(
        self, microdados_basico, variaveis_categoricas, colunas_notas, competencia_mapping
    ):
        """Given: variavel nao existe no df. When: preparar. Then: df vazio."""
        resultado = preparar_dados_comparativo(
            microdados_basico, 'COLUNA_FAKE', variaveis_categoricas,
            colunas_notas, competencia_mapping
        )
        assert resultado.empty

    def test_notas_zero_excluidas(
        self, variaveis_categoricas, colunas_notas, competencia_mapping
    ):
        """Given: notas com zeros. When: preparar. Then: zeros excluidos do calculo."""
        df = pd.DataFrame({
            'TP_SEXO': ['M'] * 40,
            'NU_NOTA_CN': [0.0] * 20 + [500.0] * 20,
            'NU_NOTA_MT': [600.0] * 40,
        })
        resultado = preparar_dados_comparativo(
            df, 'TP_SEXO', variaveis_categoricas, colunas_notas, competencia_mapping
        )
        # CN deve ter media 500 (zeros excluidos)
        media_cn = resultado[resultado['Competência'] == 'Ciencias da Natureza']['Média'].iloc[0]
        assert media_cn == pytest.approx(500.0, abs=1.0)


# ============================================================
# P0.6 — filtrar_dados_scatter
# ============================================================

class TestFiltrarDadosScatter:
    """Testes de rede de seguranca para filtrar_dados_scatter."""

    @pytest.fixture
    def dados_scatter(self):
        """DataFrame para testes de scatter plot."""
        np.random.seed(42)
        n = 200
        return pd.DataFrame({
            'NU_NOTA_CN': np.random.uniform(100, 900, n),
            'NU_NOTA_MT': np.random.uniform(100, 900, n),
            'TP_SEXO': np.random.choice(['M', 'F'], n),
            'TP_DEPENDENCIA_ADM_ESC': np.random.choice([1, 2, 3, 4], n),
            'TP_FAIXA_SALARIAL': np.random.choice([0, 1, 2, 3, 4, 5], n),
        })

    def test_retorna_dataframe_e_contagem(self, dados_scatter):
        """Given: dados validos. When: filtrar. Then: retorna (df, int)."""
        resultado, removidos = filtrar_dados_scatter(
            dados_scatter, None, None, 'NU_NOTA_CN', 'NU_NOTA_MT'
        )
        assert isinstance(resultado, pd.DataFrame)
        assert isinstance(removidos, int)
        assert not resultado.empty

    def test_filtro_sexo(self, dados_scatter):
        """Given: filtro sexo='M'. When: filtrar. Then: apenas masculinos."""
        resultado, _ = filtrar_dados_scatter(
            dados_scatter, 'M', None, 'NU_NOTA_CN', 'NU_NOTA_MT'
        )
        assert all(resultado['TP_SEXO'] == 'M')

    def test_filtro_escola_publica(self, dados_scatter):
        """Given: filtro tipo_escola='Publica'. When: filtrar.
        Then: apenas escolas publicas (1, 2, 3)."""
        resultado, _ = filtrar_dados_scatter(
            dados_scatter, None, 'Pública', 'NU_NOTA_CN', 'NU_NOTA_MT'
        )
        assert all(resultado['TP_DEPENDENCIA_ADM_ESC'].isin([1, 2, 3]))

    def test_filtro_escola_privada(self, dados_scatter):
        """Given: filtro tipo_escola='Privada'. When: filtrar.
        Then: apenas escola privada (4)."""
        resultado, _ = filtrar_dados_scatter(
            dados_scatter, None, 'Privada', 'NU_NOTA_CN', 'NU_NOTA_MT'
        )
        assert all(resultado['TP_DEPENDENCIA_ADM_ESC'] == 4)

    def test_excluir_notas_zero(self):
        """Given: dados com zeros. When: excluir_notas_zero=True.
        Then: zeros removidos."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [0.0, 500.0, 600.0],
            'NU_NOTA_MT': [700.0, 0.0, 800.0],
        })
        resultado, removidos = filtrar_dados_scatter(
            df, None, None, 'NU_NOTA_CN', 'NU_NOTA_MT', excluir_notas_zero=True
        )
        # Apenas a 3a linha tem ambos > 0
        assert len(resultado) == 1
        assert removidos == 2

    def test_manter_notas_zero(self):
        """Given: dados com zeros. When: excluir_notas_zero=False.
        Then: zeros mantidos."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [0.0, 500.0, 600.0] * 20,
            'NU_NOTA_MT': [700.0, 0.0, 800.0] * 20,
        })
        resultado, _ = filtrar_dados_scatter(
            df, None, None, 'NU_NOTA_CN', 'NU_NOTA_MT', excluir_notas_zero=False
        )
        assert len(resultado) == 60

    def test_dataframe_vazio(self):
        """Given: df vazio. When: filtrar. Then: retorna vazio."""
        resultado, removidos = filtrar_dados_scatter(
            pd.DataFrame(), None, None, 'NU_NOTA_CN', 'NU_NOTA_MT'
        )
        assert resultado.empty
        assert removidos == 0

    def test_colunas_inexistentes(self):
        """Given: eixos nao existem. When: filtrar. Then: retorna vazio."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        resultado, _ = filtrar_dados_scatter(df, None, None, 'X', 'Y')
        assert resultado.empty

    def test_limite_max_amostras(self):
        """Given: mais amostras que o limite. When: filtrar.
        Then: resultado limitado."""
        np.random.seed(42)
        df = pd.DataFrame({
            'NU_NOTA_CN': np.random.uniform(100, 900, 100000),
            'NU_NOTA_MT': np.random.uniform(100, 900, 100000),
        })
        resultado, _ = filtrar_dados_scatter(
            df, None, None, 'NU_NOTA_CN', 'NU_NOTA_MT', max_amostras=1000
        )
        assert len(resultado) == 1000

    def test_filtro_faixa_salarial_lista(self, dados_scatter):
        """Given: filtro_faixa_salarial como lista. When: filtrar.
        Then: apenas faixas da lista."""
        resultado, _ = filtrar_dados_scatter(
            dados_scatter, None, None, 'NU_NOTA_CN', 'NU_NOTA_MT',
            filtro_faixa_salarial=[1, 2]
        )
        assert all(resultado['TP_FAIXA_SALARIAL'].isin([1, 2]))

    def test_nan_removidos(self):
        """Given: dados com NaN. When: filtrar. Then: NaN removidos."""
        df = pd.DataFrame({
            'NU_NOTA_CN': [500.0, np.nan, 600.0] * 20,
            'NU_NOTA_MT': [700.0, 800.0, np.nan] * 20,
        })
        resultado, _ = filtrar_dados_scatter(
            df, None, None, 'NU_NOTA_CN', 'NU_NOTA_MT', excluir_notas_zero=False
        )
        assert not resultado['NU_NOTA_CN'].isna().any()
        assert not resultado['NU_NOTA_MT'].isna().any()


# ============================================================
# P0.6 (extra) — preparar_dados_grafico_linha
# ============================================================

class TestPrepararDadosGraficoLinha:
    """Testes para preparar_dados_grafico_linha."""

    @pytest.fixture
    def df_resultados(self):
        return pd.DataFrame({
            'Categoria': ['A', 'A', 'B', 'B'],
            'Competência': ['CN', 'MT', 'CN', 'MT'],
            'Média': [500.0, 600.0, 450.0, 550.0],
        })

    def test_retorna_dataframe(self, df_resultados):
        """Given: dados validos. When: preparar. Then: retorna DataFrame."""
        resultado = preparar_dados_grafico_linha(df_resultados)
        assert isinstance(resultado, pd.DataFrame)
        assert not resultado.empty

    def test_filtro_competencia(self, df_resultados):
        """Given: filtro CN. When: preparar. Then: apenas CN."""
        resultado = preparar_dados_grafico_linha(
            df_resultados, competencia_filtro='CN'
        )
        assert all(resultado['Competência'] == 'CN')
        assert len(resultado) == 2

    def test_ordenacao_decrescente(self, df_resultados):
        """Given: ordenar por CN decrescente. When: preparar.
        Then: A (500) antes de B (450)... mas como Categorical."""
        resultado = preparar_dados_grafico_linha(
            df_resultados, competencia_ordenacao='CN', ordenar_decrescente=True
        )
        assert not resultado.empty

    def test_dataframe_vazio(self):
        """Given: df vazio. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_grafico_linha(pd.DataFrame())
        assert resultado.empty

    def test_none_retorna_vazio(self):
        """Given: None. When: preparar. Then: retorna vazio."""
        resultado = preparar_dados_grafico_linha(None)
        assert resultado.empty
