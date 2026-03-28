"""Testes para utils/prepara_dados/ — funções de preparação de dados."""
import pytest
import pandas as pd
import numpy as np
from utils.prepara_dados.prepara_dados_analise_geral import (
    preparar_dados_histograma,
    preparar_dados_comparativo_areas,
)
from utils.prepara_dados.prepara_dados_aspectos_sociais import (
    contar_candidatos_por_categoria,
    ordenar_categorias,
    aplicar_mapeamento,
)


# ============================================================
# preparar_dados_histograma
# ============================================================

class TestPrepararDadosHistograma:

    def test_dados_validos(self):
        df = pd.DataFrame({'NU_NOTA_CN': [0.0, -1.0, 50.0, 70.0, 30.0]})
        mapping = {'NU_NOTA_CN': 'Ciências da Natureza'}
        df_result, col, nome = preparar_dados_histograma(df, 'NU_NOTA_CN', mapping)
        assert len(df_result) == 3  # Exclui 0 e -1
        assert col == 'NU_NOTA_CN'
        assert nome == 'Ciências da Natureza'

    def test_coluna_inexistente(self):
        df = pd.DataFrame({'NU_NOTA_CN': [50.0]})
        df_result, col, nome = preparar_dados_histograma(df, 'FAKE', {})
        assert df_result.empty

    def test_dataframe_vazio(self):
        df = pd.DataFrame()
        df_result, _, _ = preparar_dados_histograma(df, 'X', {})
        assert df_result.empty

    def test_todas_notas_zero(self):
        df = pd.DataFrame({'NU_NOTA_CN': [0.0, 0.0, 0.0]})
        df_result, _, _ = preparar_dados_histograma(df, 'NU_NOTA_CN', {'NU_NOTA_CN': 'CN'})
        assert df_result.empty


# ============================================================
# preparar_dados_comparativo_areas
# ============================================================

class TestPrepararDadosComparativoAreas:

    def test_basico(self):
        df = pd.DataFrame({
            'SG_UF_PROVA': ['SP'] * 10,
            'NU_NOTA_CN': [50.0] * 10,
            'NU_NOTA_MT': [60.0] * 10,
        })
        mapping = {'NU_NOTA_CN': 'Ciências da Natureza', 'NU_NOTA_MT': 'Matemática'}
        resultado = preparar_dados_comparativo_areas(df, ['SP'], ['NU_NOTA_CN', 'NU_NOTA_MT'], mapping)
        assert not resultado.empty
        assert 'Area' in resultado.columns
        assert 'Media' in resultado.columns
        assert len(resultado) == 2

    def test_dataframe_vazio(self):
        resultado = preparar_dados_comparativo_areas(pd.DataFrame(), [], [], {})
        assert resultado.empty


# ============================================================
# contar_candidatos_por_categoria
# ============================================================

class TestContarCandidatos:

    def test_contagem_basica(self):
        df = pd.DataFrame({'cat': ['A', 'A', 'B', 'C']})
        resultado = contar_candidatos_por_categoria(df, 'cat')
        assert len(resultado) == 3
        assert 'Categoria' in resultado.columns
        assert 'Quantidade' in resultado.columns
        assert 'Percentual' in resultado.columns
        assert resultado['Quantidade'].sum() == 4

    def test_coluna_inexistente(self):
        df = pd.DataFrame({'cat': ['A']})
        resultado = contar_candidatos_por_categoria(df, 'inexistente')
        assert resultado.empty

    def test_dataframe_vazio(self):
        resultado = contar_candidatos_por_categoria(pd.DataFrame(), 'cat')
        assert resultado.empty


# ============================================================
# ordenar_categorias
# ============================================================

class TestOrdenarCategorias:

    def test_ordem_predefinida(self):
        contagem = pd.DataFrame({
            'Categoria': ['C', 'A', 'B'],
            'Quantidade': [10, 30, 20]
        })
        variaveis = {
            'var1': {'nome': 'Teste', 'mapeamento': {}, 'ordem': ['A', 'B', 'C']}
        }
        resultado = ordenar_categorias(contagem, 'var1', variaveis)
        assert list(resultado['Categoria']) == ['A', 'B', 'C']

    def test_sem_ordem_predefinida(self):
        contagem = pd.DataFrame({
            'Categoria': ['C', 'A', 'B'],
            'Quantidade': [10, 30, 20]
        })
        resultado = ordenar_categorias(contagem, 'inexistente', {})
        assert not resultado.empty

    def test_dataframe_vazio(self):
        resultado = ordenar_categorias(pd.DataFrame(), 'var', {})
        assert resultado.empty


# ============================================================
# aplicar_mapeamento
# ============================================================

class TestAplicarMapeamento:

    def test_mapeamento_numerico(self):
        df = pd.DataFrame({'var': [1, 2, 3]})
        variaveis_sociais = {
            'var': {'nome': 'Teste', 'mapeamento': {1: 'Um', 2: 'Dois', 3: 'Três'}}
        }
        coluna_plot = aplicar_mapeamento(df, 'var', variaveis_sociais)
        assert coluna_plot == 'var_NOME'
        assert 'var_NOME' in df.columns

    def test_sem_mapeamento(self):
        df = pd.DataFrame({'var': ['a', 'b']})
        variaveis_sociais = {'var': {'nome': 'Teste'}}
        coluna_plot = aplicar_mapeamento(df, 'var', variaveis_sociais)
        assert coluna_plot == 'var'  # Sem mapeamento, retorna coluna original
