"""Testes para utils/estatisticas/estatisticas_aspectos_sociais.py — P0.4, P0.8"""
import pytest
import pandas as pd
import numpy as np
from utils.estatisticas.estatisticas_aspectos_sociais import (
    analisar_correlacao_categorias,
    calcular_estatisticas_distribuicao,
)


# ============================================================
# P0.4 — analisar_correlacao_categorias
# ============================================================

class TestAnalisarCorrelacaoCategorias:
    """Testes de rede de seguranca para analisar_correlacao_categorias."""

    @pytest.fixture
    def df_correlacao_forte(self):
        """DataFrame com correlacao forte entre X e Y."""
        data = {'X': [], 'Y': []}
        for _ in range(100): data['X'].append('A'); data['Y'].append('1')
        for _ in range(100): data['X'].append('B'); data['Y'].append('2')
        for _ in range(10): data['X'].append('A'); data['Y'].append('2')
        for _ in range(10): data['X'].append('B'); data['Y'].append('1')
        return pd.DataFrame(data)

    @pytest.fixture
    def df_independente(self):
        """DataFrame com variaveis independentes (sem correlacao)."""
        np.random.seed(42)
        n = 300
        return pd.DataFrame({
            'X': np.random.choice(['A', 'B'], n),
            'Y': np.random.choice(['1', '2'], n),
        })

    @pytest.fixture
    def df_com_zeros(self):
        """DataFrame que gera zeros na tabela de contingencia."""
        data = {'X': [], 'Y': []}
        for _ in range(100): data['X'].append('A'); data['Y'].append('1')
        for _ in range(80): data['X'].append('B'); data['Y'].append('2')
        for _ in range(5): data['X'].append('A'); data['Y'].append('2')
        # B+1 tem ZERO, C+2 tem ZERO
        for _ in range(50): data['X'].append('C'); data['Y'].append('1')
        return pd.DataFrame(data)

    # --- Estrutura de retorno ---

    def test_retorna_todas_chaves(self, df_correlacao_forte):
        """Given: dados validos. When: analisar. Then: todas as chaves presentes."""
        resultado = analisar_correlacao_categorias(df_correlacao_forte, 'X', 'Y')
        chaves = [
            'qui_quadrado', 'gl', 'valor_p', 'coeficiente',
            'v_cramer', 'info_mutua', 'info_mutua_norm',
            'interpretacao', 'contexto', 'significativo',
            'tamanho_efeito', 'tabela_contingencia', 'n_amostras'
        ]
        for chave in chaves:
            assert chave in resultado, f"Chave '{chave}' ausente"

    # --- Correlacao forte ---

    def test_correlacao_forte_detectada(self, df_correlacao_forte):
        """Given: dados com forte associacao. When: analisar.
        Then: V de Cramer alto, p-valor significativo."""
        resultado = analisar_correlacao_categorias(df_correlacao_forte, 'X', 'Y')
        assert resultado['v_cramer'] > 0.5
        assert resultado['significativo'] == True
        assert resultado['qui_quadrado'] > 0

    def test_mi_com_correlacao_forte(self, df_correlacao_forte):
        """Given: dados com forte associacao. When: analisar.
        Then: MI > 0 (nao crashou silenciosamente)."""
        resultado = analisar_correlacao_categorias(df_correlacao_forte, 'X', 'Y')
        assert resultado['info_mutua'] > 0
        assert resultado['info_mutua_norm'] > 0

    # --- Independencia ---

    def test_independencia_v_cramer_baixo(self, df_independente):
        """Given: dados independentes. When: analisar.
        Then: V de Cramer baixo."""
        resultado = analisar_correlacao_categorias(df_independente, 'X', 'Y')
        assert resultado['v_cramer'] < 0.1

    # --- BUG #5: MI com zeros na tabela de contingencia ---

    def test_mi_com_zeros_calcula_corretamente(self, df_com_zeros):
        """FIX P1.4: MI agora usa mascara conjunta em vez de filtrar p_xy.
        Funciona mesmo com celulas zero na tabela de contingencia."""
        resultado = analisar_correlacao_categorias(df_com_zeros, 'X', 'Y')
        assert resultado['info_mutua'] > 0  # CORRIGIDO: MI calculada
        assert resultado['n_amostras'] == 235  # CORRIGIDO: total correto
        assert resultado['v_cramer'] > 0  # CORRIGIDO: Cramer calculado

    # --- Edge cases ---

    def test_dataframe_vazio(self):
        """Given: DataFrame vazio. When: analisar. Then: retorna fallback."""
        resultado = analisar_correlacao_categorias(pd.DataFrame(), 'X', 'Y')
        assert resultado['n_amostras'] == 0
        assert resultado['significativo'] == False

    def test_dataframe_none(self):
        """Given: None. When: analisar. Then: retorna fallback."""
        resultado = analisar_correlacao_categorias(None, 'X', 'Y')
        assert resultado['n_amostras'] == 0

    def test_colunas_inexistentes(self):
        """Given: colunas nao existem. When: analisar. Then: fallback."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        resultado = analisar_correlacao_categorias(df, 'X', 'Y')
        assert resultado['n_amostras'] == 0

    def test_amostras_insuficientes(self):
        """Given: menos de 30 amostras. When: analisar. Then: fallback."""
        df = pd.DataFrame({'X': ['A', 'B'], 'Y': ['1', '2']})
        resultado = analisar_correlacao_categorias(df, 'X', 'Y')
        assert resultado['n_amostras'] == 0
        assert 'insuficientes' in resultado['interpretacao'].lower()

    def test_uma_unica_categoria(self):
        """Given: apenas 1 categoria em X. When: analisar. Then: fallback."""
        df = pd.DataFrame({'X': ['A'] * 100, 'Y': ['1', '2'] * 50})
        resultado = analisar_correlacao_categorias(df, 'X', 'Y')
        assert resultado['n_amostras'] == 0

    # --- N amostras ---

    def test_n_amostras_correto(self, df_correlacao_forte):
        """Given: 220 registros. When: analisar. Then: n_amostras = 220."""
        resultado = analisar_correlacao_categorias(df_correlacao_forte, 'X', 'Y')
        assert resultado['n_amostras'] == 220

    # --- Interpretacoes ---

    def test_interpretacao_retorna_string(self, df_correlacao_forte):
        """Given: dados validos. When: analisar. Then: interpretacao e string."""
        resultado = analisar_correlacao_categorias(df_correlacao_forte, 'X', 'Y')
        assert isinstance(resultado['interpretacao'], str)
        assert len(resultado['interpretacao']) > 0

    def test_contexto_retorna_string(self, df_correlacao_forte):
        """Given: dados validos. When: analisar. Then: contexto e string."""
        resultado = analisar_correlacao_categorias(df_correlacao_forte, 'X', 'Y')
        assert isinstance(resultado['contexto'], str)


# ============================================================
# P0.8 — calcular_estatisticas_distribuicao
# ============================================================

class TestCalcularEstatisticasDistribuicao:
    """Testes de rede de seguranca para calcular_estatisticas_distribuicao."""

    @pytest.fixture
    def contagem_padrao(self):
        """Contagem tipica de distribuicao."""
        return pd.DataFrame({
            'Categoria': ['A', 'B', 'C', 'D'],
            'Quantidade': [100, 200, 150, 50]
        })

    # --- Estrutura de retorno ---

    def test_retorna_chaves_essenciais(self, contagem_padrao):
        """Given: contagem valida. When: calcular. Then: chaves essenciais presentes."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        chaves = ['total', 'categoria_mais_frequente', 'categoria_menos_frequente',
                   'num_categorias', 'media', 'mediana', 'indice_concentracao']
        for chave in chaves:
            assert chave in resultado, f"Chave '{chave}' ausente"

    # --- Valores corretos ---

    def test_total_correto(self, contagem_padrao):
        """Given: quantidades 100+200+150+50. When: calcular. Then: total=500."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        assert resultado['total'] == 500

    def test_categoria_mais_frequente(self, contagem_padrao):
        """Given: B tem 200 (maior). When: calcular.
        Then: categoria_mais_frequente identifica B."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        assert resultado['categoria_mais_frequente'] is not None
        assert resultado['categoria_mais_frequente']['Quantidade'] == 200

    def test_categoria_menos_frequente(self, contagem_padrao):
        """Given: D tem 50 (menor). When: calcular.
        Then: categoria_menos_frequente identifica D."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        assert resultado['categoria_menos_frequente'] is not None
        assert resultado['categoria_menos_frequente']['Quantidade'] == 50

    def test_num_categorias(self, contagem_padrao):
        """Given: 4 categorias. When: calcular. Then: num_categorias=4."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        assert resultado['num_categorias'] == 4

    # --- Concentracao ---

    def test_distribuicao_uniforme_tem_alta_concentracao(self):
        """Given: distribuicao perfeitamente uniforme. When: calcular.
        Then: indice_concentracao proximo de (1 - 1/n) = maximo."""
        contagem = pd.DataFrame({
            'Categoria': ['A', 'B', 'C', 'D'],
            'Quantidade': [100, 100, 100, 100]
        })
        resultado = calcular_estatisticas_distribuicao(contagem)
        # HHI invertido para uniforme: 1 - sum(0.25^2 * 4) = 1 - 0.25 = 0.75
        assert resultado['indice_concentracao'] == pytest.approx(0.75, abs=0.01)

    def test_distribuicao_concentrada_tem_baixo_indice(self):
        """Given: distribuicao muito concentrada (1 domina). When: calcular.
        Then: indice_concentracao baixo."""
        contagem = pd.DataFrame({
            'Categoria': ['A', 'B', 'C'],
            'Quantidade': [990, 5, 5]
        })
        resultado = calcular_estatisticas_distribuicao(contagem)
        assert resultado['indice_concentracao'] < 0.1

    # --- Edge cases ---

    def test_dataframe_vazio(self):
        """Given: contagem vazia. When: calcular. Then: fallback."""
        resultado = calcular_estatisticas_distribuicao(pd.DataFrame())
        assert resultado['total'] == 0

    def test_dataframe_none(self):
        """Given: None. When: calcular. Then: fallback."""
        resultado = calcular_estatisticas_distribuicao(None)
        assert resultado['total'] == 0

    def test_sem_coluna_quantidade(self):
        """Given: df sem coluna 'Quantidade'. When: calcular. Then: fallback."""
        df = pd.DataFrame({'Categoria': ['A'], 'Contagem': [10]})
        resultado = calcular_estatisticas_distribuicao(df)
        assert resultado['total'] == 0

    def test_uma_unica_categoria(self):
        """Given: 1 categoria apenas. When: calcular. Then: funciona."""
        contagem = pd.DataFrame({'Categoria': ['A'], 'Quantidade': [100]})
        resultado = calcular_estatisticas_distribuicao(contagem)
        assert resultado['total'] == 100
        assert resultado['num_categorias'] == 1

    def test_todas_quantidades_zero(self):
        """Given: quantidades todas zero. When: calcular. Then: fallback."""
        contagem = pd.DataFrame({'Categoria': ['A', 'B'], 'Quantidade': [0, 0]})
        resultado = calcular_estatisticas_distribuicao(contagem)
        assert resultado['total'] == 0

    # --- Metricas avancadas ---

    def test_gini_retornado(self, contagem_padrao):
        """Given: dados validos. When: calcular. Then: indice_gini presente."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        assert 'indice_gini' in resultado
        assert 0 <= resultado['indice_gini'] <= 1

    def test_entropia_retornada(self, contagem_padrao):
        """Given: dados validos. When: calcular. Then: entropia presente e >= 0."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        assert 'entropia' in resultado
        assert resultado['entropia'] >= 0

    def test_razao_max_min(self, contagem_padrao):
        """Given: max=200, min=50. When: calcular. Then: razao = 4.0."""
        resultado = calcular_estatisticas_distribuicao(contagem_padrao)
        assert resultado['razao_max_min'] == pytest.approx(4.0, abs=0.01)
