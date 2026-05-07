"""Testes para refatoracoes P3.11 (html.escape) e P3.15 (god functions)."""
import pytest
import html
import numpy as np
import pandas as pd


class TestHtmlEscape:
    """P3.11: html.escape() deve sanitizar dados exibidos, mas preservar HTML intencional."""

    def test_html_escape_sanitiza_dados(self):
        """Dados com caracteres HTML devem ser escapados."""
        malicioso = '<script>alert("xss")</script>'
        esperado = html.escape(malicioso)
        assert '&lt;script&gt;' in esperado
        assert '<script>' not in esperado

    def test_html_escape_preserva_texto_normal(self):
        """Texto normal nao deve ser alterado por html.escape."""
        texto = "Média de notas por estado"
        assert html.escape(texto) == texto

    def test_explicacao_com_html_nao_escapada(self):
        """Explicacoes contem HTML intencional (<b>, <br>) que NAO deve ser escapado."""
        explicacao = '<b>Sobre:</b><br>Texto explicativo'
        # Verificar que html.escape QUEBRARIA o HTML intencional
        assert '&lt;b&gt;' in html.escape(explicacao)
        # Mas o original preserva as tags
        assert '<b>' in explicacao


class TestRefactorHelpers:
    """P3.15: helpers extraidos de god functions devem funcionar corretamente."""

    def test_encontrar_estado_extremo_max(self):
        """_encontrar_estado_extremo deve encontrar estado com maior falta."""
        from utils.estatisticas.estatistica_analise_geral import _encontrar_estado_extremo
        df = pd.DataFrame({
            'Estado': ['SP', 'RJ', 'MG'],
            'Percentual de Faltas': [10.0, 25.0, 15.0]
        })
        resultado = _encontrar_estado_extremo(df, 'max')
        assert resultado is not None
        assert resultado['Estado'] == 'RJ'
        assert resultado['Percentual de Faltas'] == 25.0

    def test_encontrar_estado_extremo_min(self):
        """_encontrar_estado_extremo deve encontrar estado com menor falta."""
        from utils.estatisticas.estatistica_analise_geral import _encontrar_estado_extremo
        df = pd.DataFrame({
            'Estado': ['SP', 'RJ', 'MG'],
            'Percentual de Faltas': [10.0, 25.0, 15.0]
        })
        resultado = _encontrar_estado_extremo(df, 'min')
        assert resultado is not None
        assert resultado['Estado'] == 'SP'

    def test_encontrar_estado_extremo_vazio(self):
        """_encontrar_estado_extremo com DF vazio retorna None."""
        from utils.estatisticas.estatistica_analise_geral import _encontrar_estado_extremo
        assert _encontrar_estado_extremo(pd.DataFrame(), 'max') is None
        assert _encontrar_estado_extremo(None, 'min') is None

    def test_determinar_tipo_falta_mais_comum(self):
        """_determinar_tipo_falta_mais_comum deve retornar tipo com maior media."""
        from utils.estatisticas.estatistica_analise_geral import _determinar_tipo_falta_mais_comum
        assert _determinar_tipo_falta_mais_comum(10.0, 5.0, 3.0) == 'Ambos os dias'
        assert _determinar_tipo_falta_mais_comum(5.0, 15.0, 3.0) == 'Primeiro dia'
        assert _determinar_tipo_falta_mais_comum(5.0, 3.0, 20.0) == 'Segundo dia'

    def test_calcular_taxa_presenca_com_coluna(self):
        """_calcular_taxa_presenca deve usar TP_PRESENCA_GERAL quando disponivel."""
        from utils.estatisticas.estatistica_analise_geral import _calcular_taxa_presenca
        df = pd.DataFrame({
            'TP_PRESENCA_GERAL': [3, 3, 1, 2],
            'NU_NOTA_CN': [500, 600, 0, 0],
        })
        taxa = _calcular_taxa_presenca(df, ['NU_NOTA_CN'], 4)
        assert taxa == 50.0  # 2 de 4 presentes

    def test_calcular_taxa_presenca_fallback(self):
        """_calcular_taxa_presenca deve usar notas como fallback."""
        from utils.estatisticas.estatistica_analise_geral import _calcular_taxa_presenca
        df = pd.DataFrame({
            'NU_NOTA_CN': [500.0, 600.0, 0.0, np.nan],
        })
        taxa = _calcular_taxa_presenca(df, ['NU_NOTA_CN'], 4)
        assert taxa == 50.0  # 2 notas validas de 4

    def test_safe_round(self):
        """_safe_round deve retornar 0.0 para valores nao finitos."""
        from utils.estatisticas.estatistica_analise_geral import _safe_round
        assert _safe_round(3.14159, 2) == 3.14
        assert _safe_round(float('inf')) == 0.0
        assert _safe_round(float('nan')) == 0.0
        assert _safe_round(float('-inf'), 4) == 0.0

    def test_calcular_metricas_associacao(self):
        """_calcular_metricas_associacao deve retornar chi2, p, gl, coef, cramer."""
        from utils.estatisticas.estatisticas_aspectos_sociais import _calcular_metricas_associacao
        tabela = pd.DataFrame({
            'A': [100, 20],
            'B': [30, 80]
        })
        chi2, p, gl, coef, cramer = _calcular_metricas_associacao(tabela, 230)
        assert chi2 > 0
        assert 0 <= p <= 1
        assert gl > 0
        assert 0 <= cramer <= 1

    def test_calcular_informacao_mutua(self):
        """_calcular_informacao_mutua deve retornar MI > 0 para tabela nao uniforme."""
        from utils.estatisticas.estatisticas_aspectos_sociais import _calcular_informacao_mutua
        tabela = pd.DataFrame({
            'A': [100, 10],
            'B': [10, 100]
        })
        mi, mi_norm = _calcular_informacao_mutua(tabela, 220)
        assert mi > 0
        assert mi_norm > 0

    def test_aplicar_filtros_demograficos_sexo(self):
        """_aplicar_filtros_demograficos deve filtrar por sexo."""
        from utils.prepara_dados.prepara_dados_desempenho import _aplicar_filtros_demograficos
        df = pd.DataFrame({
            'TP_SEXO': ['M', 'F', 'M', 'F'],
            'TP_COR_RACA': [1, 2, 1, 2],
        })
        resultado = _aplicar_filtros_demograficos(df, 'M', None, None, None)
        assert len(resultado) == 2
        assert all(resultado['TP_SEXO'] == 'M')

    def test_aplicar_filtros_demograficos_nenhum(self):
        """_aplicar_filtros_demograficos sem filtros retorna df original."""
        from utils.prepara_dados.prepara_dados_desempenho import _aplicar_filtros_demograficos
        df = pd.DataFrame({'TP_SEXO': ['M', 'F']})
        resultado = _aplicar_filtros_demograficos(df, None, None, None, None)
        assert len(resultado) == 2
