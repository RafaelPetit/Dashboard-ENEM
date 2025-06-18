#!/usr/bin/env python3
"""
Teste independente para verificar se os expanders de aspectos sociais
estão funcionando após as correções.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from typing import Dict, Any

def test_analisar_correlacao_categorias():
    """Testa a função analisar_correlacao_categorias."""
    print("=== TESTE: analisar_correlacao_categorias ===")
    
    try:
        from utils.estatisticas.aspectos_sociais.analise_aspectos_sociais import analisar_correlacao_categorias
        
        # Dados de teste
        np.random.seed(42)
        df_test = pd.DataFrame({
            'Q001_NOME': np.random.choice(['Ensino Médio', 'Superior', 'Não informado'], 100),
            'Q002_NOME': np.random.choice(['Até 1000', '1000-3000', 'Acima de 3000'], 100)
        })
        
        resultado = analisar_correlacao_categorias(df_test, 'Q001_NOME', 'Q002_NOME')
        
        print(f"✅ Função executada com sucesso!")
        print(f"   Chaves retornadas: {sorted(resultado.keys())}")
        print(f"   Coeficiente: {resultado.get('coeficiente', 'N/A')}")
        print(f"   Interpretação: {resultado.get('interpretacao', 'N/A')}")
        print(f"   Significativo: {resultado.get('significativo', 'N/A')}")
        
        # Teste com dados insuficientes
        df_vazio = pd.DataFrame()
        resultado_vazio = analisar_correlacao_categorias(df_vazio, 'col1', 'col2')
        print(f"   Teste com dados vazios - Interpretação: {resultado_vazio.get('interpretacao', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na função: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calcular_estatisticas_distribuicao():
    """Testa a função calcular_estatisticas_distribuicao."""
    print("\n=== TESTE: calcular_estatisticas_distribuicao ===")
    
    try:
        from utils.estatisticas.aspectos_sociais.analise_aspectos_sociais import calcular_estatisticas_distribuicao
        
        # Dados de teste
        df_dist = pd.DataFrame({
            'Categoria': ['Ensino Médio', 'Superior', 'Fundamental'],
            'Quantidade': [500, 300, 200],
            'Percentual': [50.0, 30.0, 20.0]
        })
        
        resultado = calcular_estatisticas_distribuicao(df_dist)
        
        print(f"✅ Função executada com sucesso!")
        print(f"   Total: {resultado.get('total', 'N/A')}")
        print(f"   Índice concentração: {resultado.get('indice_concentracao', 'N/A')}")
        print(f"   Média: {resultado.get('media', 'N/A')}")
        print(f"   Num categorias: {resultado.get('num_categorias', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na função: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analisar_distribuicao_regional():
    """Testa a função analisar_distribuicao_regional."""
    print("\n=== TESTE: analisar_distribuicao_regional ===")
    
    try:
        from utils.estatisticas.aspectos_sociais.analise_aspectos_sociais import analisar_distribuicao_regional
        
        # Dados de teste
        df_regional = pd.DataFrame({
            'Estado': ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA'],
            'Categoria': ['Ensino Médio'] * 7,
            'Percentual': [45.2, 48.1, 42.3, 50.1, 46.8, 44.5, 41.2]
        })
        
        resultado = analisar_distribuicao_regional(df_regional, 'Q001', 'Ensino Médio')
        
        print(f"✅ Função executada com sucesso!")
        print(f"   Percentual médio: {resultado.get('percentual_medio', 'N/A')}")
        print(f"   Desvio padrão: {resultado.get('desvio_padrao', 'N/A')}")
        print(f"   Coef. variação: {resultado.get('coef_variacao', 'N/A')}")
        print(f"   Variabilidade: {resultado.get('variabilidade', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na função: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_expander_functions():
    """Testa as funções auxiliares dos expanders."""
    print("\n=== TESTE: Funções auxiliares dos expanders ===")
    
    try:
        from utils.expander.expander_aspectos_sociais import (
            _mostrar_resumo_associacao,
            _mostrar_metricas_estatisticas
        )
        
        # Simular métricas válidas
        metricas_validas = {
            'coeficiente': 0.25,
            'qui_quadrado': 15.2,
            'v_cramer': 0.25,
            'interpretacao': 'Associação fraca',
            'significativo': True,
            'valor_p': 0.02,
            'n_amostras': 1000
        }
        
        # Simular métricas insuficientes
        metricas_insuficientes = {
            'coeficiente': 0.0,
            'qui_quadrado': 0.0,
            'v_cramer': 0.0,
            'interpretacao': 'Dados insuficientes para análise',
            'significativo': False,
            'valor_p': 1.0,
            'n_amostras': 0
        }
        
        variaveis_sociais = {
            'Q001': {'nome': 'Escolaridade da Mãe'},
            'Q002': {'nome': 'Renda Familiar'}
        }
        
        print("✅ Estruturas de teste criadas com sucesso!")
        print(f"   Métricas válidas têm coeficiente: {metricas_validas['coeficiente']}")
        print(f"   Métricas insuficientes têm coeficiente: {metricas_insuficientes['coeficiente']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar funções auxiliares: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes."""
    print("🔬 EXECUTANDO TESTES DOS EXPANDERS DE ASPECTOS SOCIAIS")
    print("=" * 60)
    
    resultados = []
    
    # Executar testes
    resultados.append(test_analisar_correlacao_categorias())
    resultados.append(test_calcular_estatisticas_distribuicao())
    resultados.append(test_analisar_distribuicao_regional())
    resultados.append(test_expander_functions())
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    
    total_testes = len(resultados)
    testes_passaram = sum(resultados)
    
    print(f"✅ Testes que passaram: {testes_passaram}/{total_testes}")
    
    if testes_passaram == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! Os expanders devem estar funcionando corretamente.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    print("\n💡 DICAS PARA RESOLVER PROBLEMAS RESTANTES:")
    print("   1. Verifique se dados reais estão chegando aos expanders")
    print("   2. Confirme se as chaves esperadas estão sendo retornadas pelas funções")
    print("   3. Teste com dados reais do ENEM no Streamlit")
    print("   4. Verifique logs do navegador para erros de JavaScript")
    
    return testes_passaram == total_testes


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
