"""Testes para utils/estatisticas/estatistica_analise_geral.py — P0.1, P0.2"""
import pytest
import pandas as pd
import numpy as np
from utils.estatisticas.estatistica_analise_geral import (
    analisar_distribuicao_notas,
    analisar_faltas,
)


# ============================================================
# P0.1 — analisar_distribuicao_notas
# ============================================================

class TestAnalisarDistribuicaoNotas:
    """Testes de rede de seguranca para analisar_distribuicao_notas.
    Documenta o comportamento ATUAL (incluindo bugs conhecidos)
    para detectar regressoes durante os fixes do P1."""

    # --- Estrutura de retorno ---

    def test_retorna_todas_chaves_esperadas(self):
        """Given: DataFrame valido. When: analisar. Then: dict contem todas as chaves."""
        df = pd.DataFrame({'NU_NOTA_CN': [500.0, 600.0, 700.0, 800.0, 400.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        chaves_esperadas = [
            'total_valido', 'total_candidatos', 'total_invalido',
            'media', 'mediana', 'min_valor', 'max_valor',
            'desvio_padrao', 'curtose', 'assimetria',
            'percentis', 'faixas', 'conceitos',
            'intervalo_confianca', 'coef_variacao', 'amplitude'
        ]
        for chave in chaves_esperadas:
            assert chave in resultado, f"Chave '{chave}' ausente no resultado"

    # --- Comportamento com dados validos ---

    def test_media_calculada_corretamente(self):
        """Given: notas [400, 500, 600]. When: analisar. Then: media = 500."""
        df = pd.DataFrame({'NU_NOTA_CN': [400.0, 500.0, 600.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['media'] == pytest.approx(500.0, abs=0.01)
        assert resultado['total_valido'] == 3
        assert resultado['total_invalido'] == 0

    def test_mediana_calculada_corretamente(self):
        """Given: notas [300, 500, 900]. When: analisar. Then: mediana = 500."""
        df = pd.DataFrame({'NU_NOTA_CN': [300.0, 500.0, 900.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['mediana'] == pytest.approx(500.0, abs=0.01)

    def test_min_max_corretos(self):
        """Given: notas [200, 500, 800]. When: analisar. Then: min=200, max=800."""
        df = pd.DataFrame({'NU_NOTA_CN': [200.0, 500.0, 800.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['min_valor'] == pytest.approx(200.0, abs=0.01)
        assert resultado['max_valor'] == pytest.approx(800.0, abs=0.01)

    def test_amplitude_correta(self):
        """Given: notas [200, 800]. When: analisar. Then: amplitude=600."""
        df = pd.DataFrame({'NU_NOTA_CN': [200.0, 800.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['amplitude'] == pytest.approx(600.0, abs=0.01)

    # --- BUG CONHECIDO #2: filtro < 1000 exclui nota perfeita ---

    def test_nota_1000_incluida(self):
        """FIX P1.2: filtro agora usa <= 1000, incluindo nota perfeita."""
        df = pd.DataFrame({'NU_NOTA_CN': [500.0, 750.0, 1000.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 3  # CORRIGIDO: nota 1000 incluida
        assert resultado['max_valor'] == pytest.approx(1000.0, abs=0.01)

    # --- Sentinela -0.1 (resultado do bug #1 no pipeline) ---

    def test_valor_negativo_excluido(self):
        """Given: notas com -0.1 (sentinela apos divisao por 10).
        When: analisar. Then: -0.1 excluido pelo filtro > 0."""
        df = pd.DataFrame({'NU_NOTA_CN': [500.0, -0.1, 700.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 2
        assert resultado['total_invalido'] == 1
        assert resultado['media'] == pytest.approx(600.0, abs=0.01)

    def test_valor_zero_excluido(self):
        """Given: nota 0. When: analisar. Then: 0 excluido (filtro > 0)."""
        df = pd.DataFrame({'NU_NOTA_CN': [0.0, 500.0, 700.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 2

    def test_valor_menos1_excluido(self):
        """Given: nota -1 (sentinela original antes do pipeline).
        When: analisar. Then: -1 excluido pelo filtro > 0."""
        df = pd.DataFrame({'NU_NOTA_CN': [-1.0, 500.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 1
        assert resultado['media'] == pytest.approx(500.0, abs=0.01)

    # --- Edge cases ---

    def test_dataframe_vazio(self):
        """Given: DataFrame vazio. When: analisar. Then: retorna estrutura vazia."""
        resultado = analisar_distribuicao_notas(pd.DataFrame(), 'NU_NOTA_CN')
        assert resultado['total_valido'] == 0
        assert resultado['media'] == 0.0

    def test_dataframe_none(self):
        """Given: None. When: analisar. Then: retorna estrutura vazia."""
        resultado = analisar_distribuicao_notas(None, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 0

    def test_coluna_inexistente(self):
        """Given: coluna nao existe no DF. When: analisar. Then: retorna vazio."""
        df = pd.DataFrame({'OUTRA': [500.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 0

    def test_todos_nan(self):
        """Given: todos valores NaN. When: analisar. Then: retorna vazio."""
        df = pd.DataFrame({'NU_NOTA_CN': [np.nan, np.nan, np.nan]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 0
        assert resultado['media'] == 0.0

    def test_todos_zero(self):
        """Given: todos valores 0 (ausentes). When: analisar. Then: retorna vazio."""
        df = pd.DataFrame({'NU_NOTA_CN': [0.0, 0.0, 0.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 0

    def test_um_unico_valor_valido(self):
        """Given: 1 nota valida. When: analisar. Then: media=mediana=min=max."""
        df = pd.DataFrame({'NU_NOTA_CN': [600.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 1
        assert resultado['media'] == pytest.approx(600.0, abs=0.01)
        assert resultado['mediana'] == pytest.approx(600.0, abs=0.01)
        assert resultado['desvio_padrao'] == 0.0

    # --- Faixas e conceitos ---

    def test_faixas_somam_100(self):
        """Given: notas distribuidas. When: analisar. Then: faixas somam ~100%."""
        df = pd.DataFrame({'NU_NOTA_CN': [
            100.0, 200.0, 350.0, 450.0, 550.0,
            650.0, 750.0, 850.0, 950.0, 400.0
        ]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        soma_faixas = sum(resultado['faixas'].values())
        assert soma_faixas == pytest.approx(100.0, abs=0.1)

    def test_conceitos_somam_100(self):
        """Given: notas distribuidas. When: analisar. Then: conceitos somam ~100%."""
        df = pd.DataFrame({'NU_NOTA_CN': [
            100.0, 300.0, 500.0, 700.0, 900.0,
            200.0, 400.0, 600.0, 800.0, 350.0
        ]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        soma_conceitos = sum(resultado['conceitos'].values())
        assert soma_conceitos == pytest.approx(100.0, abs=0.1)

    # --- Tipos de dados ---

    def test_float16_nao_causa_overflow(self):
        """Given: notas em float16. When: analisar. Then: funciona sem overflow."""
        df = pd.DataFrame({'NU_NOTA_CN': pd.array([500.0, 600.0, 700.0, 400.0, 800.0], dtype='float16')})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_valido'] == 5
        assert resultado['media'] > 0

    # --- Percentis ---

    def test_percentis_retornados(self):
        """Given: dados suficientes. When: analisar. Then: percentis calculados."""
        df = pd.DataFrame({'NU_NOTA_CN': list(range(100, 950, 10))})
        df['NU_NOTA_CN'] = df['NU_NOTA_CN'].astype(float)
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert 10 in resultado['percentis']
        assert 50 in resultado['percentis']
        assert 90 in resultado['percentis']
        # P50 deve ser ~mediana
        assert resultado['percentis'][50] == pytest.approx(resultado['mediana'], abs=5.0)

    # --- Intervalo de confianca ---

    def test_intervalo_confianca_contem_media(self):
        """Given: dados suficientes. When: analisar. Then: IC95% contem a media."""
        df = pd.DataFrame({'NU_NOTA_CN': [500.0 + i for i in range(100)]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        ic = resultado['intervalo_confianca']
        assert ic[0] <= resultado['media'] <= ic[1]

    # --- Total candidatos ---

    def test_total_candidatos_inclui_invalidos(self):
        """Given: 5 candidatos, 2 com nota 0. When: analisar.
        Then: total_candidatos=5, total_valido=3, total_invalido=2."""
        df = pd.DataFrame({'NU_NOTA_CN': [0.0, 0.0, 500.0, 600.0, 700.0]})
        resultado = analisar_distribuicao_notas(df, 'NU_NOTA_CN')
        assert resultado['total_candidatos'] == 5
        assert resultado['total_valido'] == 3
        assert resultado['total_invalido'] == 2


# ============================================================
# P0.2 — analisar_faltas
# ============================================================

class TestAnalisarFaltas:
    """Testes de rede de seguranca para analisar_faltas.
    Documenta bugs conhecidos de mismatch de strings."""

    @pytest.fixture
    def df_faltas_padrao(self):
        """DataFrame com a estrutura que _calcular_faltas_por_localidade produz."""
        return pd.DataFrame({
            'Estado': ['SP', 'SP', 'SP', 'RJ', 'RJ', 'RJ'],
            'Tipo de Falta': [
                'Faltou nos dois dias',
                'Faltou somente no primeiro dia',
                'Faltou somente no segundo dia',
                'Faltou nos dois dias',
                'Faltou somente no primeiro dia',
                'Faltou somente no segundo dia',
            ],
            'Percentual de Faltas': [15.0, 5.0, 7.0, 12.0, 4.0, 6.0],
            'Contagem': [150, 50, 70, 120, 40, 60],
            'Total': [1000, 1000, 1000, 1000, 1000, 1000]
        })

    # --- Estrutura de retorno ---

    def test_retorna_todas_chaves_esperadas(self, df_faltas_padrao):
        """Given: df valido. When: analisar. Then: todas as chaves presentes."""
        resultado = analisar_faltas(df_faltas_padrao)
        chaves = [
            'taxa_media_geral', 'estado_maior_falta', 'estado_menor_falta',
            'medias_por_tipo', 'tipo_mais_comum',
            'media_faltas_ambos_dias', 'media_faltas_dia1', 'media_faltas_dia2',
            'diferenca_dias', 'desvio_padrao_faltas', 'variabilidade',
            'estados_maior_evasao', 'estados_menor_evasao'
        ]
        for chave in chaves:
            assert chave in resultado, f"Chave '{chave}' ausente"

    # --- dia1 e dia2: verificacao que funciona corretamente ---

    def test_dia1_dia2_calculados_corretamente(self, df_faltas_padrao):
        """Given: dados com faltas por dia. When: analisar.
        Then: media_faltas_dia1 e dia2 tem valores corretos.
        NOTA: Auditoria previu bug de mismatch de strings, mas
        'Faltou somente no X dia' != contains 'Faltou no X dia'
        ('somente' impede o match). Confirmado como falso positivo."""
        resultado = analisar_faltas(df_faltas_padrao)
        # SP=5%, RJ=4% -> media dia1 = 4.5
        assert resultado['media_faltas_dia1'] == pytest.approx(4.5, abs=0.01)
        # SP=7%, RJ=6% -> media dia2 = 6.5
        assert resultado['media_faltas_dia2'] == pytest.approx(6.5, abs=0.01)
        # Ambos os dias tem media 13.5 > dia1 e dia2
        assert resultado['tipo_mais_comum'] == 'Ambos os dias'
        # diferenca_dias = dia2 - dia1 = 6.5 - 4.5 = 2.0
        assert resultado['diferenca_dias'] == pytest.approx(2.0, abs=0.01)

    # --- Comportamento correto de "ambos os dias" ---

    def test_media_ambos_dias_calculada(self, df_faltas_padrao):
        """Given: dados com faltas em ambos os dias.
        When: analisar. Then: media_faltas_ambos_dias calculada corretamente."""
        resultado = analisar_faltas(df_faltas_padrao)
        # SP=15%, RJ=12%, media = 13.5%
        assert resultado['media_faltas_ambos_dias'] == pytest.approx(13.5, abs=0.01)

    def test_estado_maior_falta(self, df_faltas_padrao):
        """Given: SP tem mais faltas que RJ. When: analisar.
        Then: estado_maior_falta = SP."""
        resultado = analisar_faltas(df_faltas_padrao)
        assert resultado['estado_maior_falta'] is not None
        assert resultado['estado_maior_falta']['Estado'] == 'SP'

    def test_estado_menor_falta(self, df_faltas_padrao):
        """Given: RJ tem menos faltas que SP. When: analisar.
        Then: estado_menor_falta = RJ."""
        resultado = analisar_faltas(df_faltas_padrao)
        assert resultado['estado_menor_falta'] is not None
        assert resultado['estado_menor_falta']['Estado'] == 'RJ'

    # --- Edge cases ---

    def test_dataframe_vazio(self):
        """Given: df vazio. When: analisar. Then: retorna fallback."""
        resultado = analisar_faltas(pd.DataFrame())
        assert resultado['taxa_media_geral'] == 0.0
        assert resultado['estado_maior_falta'] is None

    def test_dataframe_none(self):
        """Given: None. When: analisar. Then: retorna fallback."""
        resultado = analisar_faltas(None)
        assert resultado['taxa_media_geral'] == 0.0

    def test_colunas_ausentes(self):
        """Given: df sem colunas esperadas. When: analisar. Then: fallback."""
        df = pd.DataFrame({'A': [1], 'B': [2]})
        resultado = analisar_faltas(df)
        assert resultado['taxa_media_geral'] == 0.0

    def test_um_unico_estado(self):
        """Given: dados de 1 estado apenas. When: analisar. Then: funciona."""
        df = pd.DataFrame({
            'Estado': ['SP', 'SP', 'SP'],
            'Tipo de Falta': [
                'Faltou nos dois dias',
                'Faltou somente no primeiro dia',
                'Faltou somente no segundo dia',
            ],
            'Percentual de Faltas': [10.0, 3.0, 5.0],
            'Contagem': [100, 30, 50],
            'Total': [1000, 1000, 1000]
        })
        resultado = analisar_faltas(df)
        assert resultado['media_faltas_ambos_dias'] == pytest.approx(10.0, abs=0.01)

    # --- BUG #10: typo na estrutura vazia ---

    def test_estrutura_vazia_tem_strings_corretas(self):
        """FIX P1.5: _criar_analise_faltas_vazia agora tem strings corretas."""
        resultado = analisar_faltas(None)
        tipos = resultado['medias_por_tipo']['Tipo de Falta'].tolist()
        assert 'Faltou somente no primeiro dia' in tipos  # CORRIGIDO
        assert 'Faltou somente no segundo dia' in tipos  # CORRIGIDO

    def test_estados_evasao_lista(self, df_faltas_padrao):
        """Given: dados validos. When: analisar. Then: listas de evasao sao listas."""
        resultado = analisar_faltas(df_faltas_padrao)
        assert isinstance(resultado['estados_maior_evasao'], list)
        assert isinstance(resultado['estados_menor_evasao'], list)
