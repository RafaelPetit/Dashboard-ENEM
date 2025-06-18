"""
Teste das correções dos expanders de aspectos sociais.
"""

import pandas as pd
import numpy as np
from utils.estatisticas.aspectos_sociais.analise_aspectos_sociais import (
    calcular_estatisticas_distribuicao,
    analisar_correlacao_categorias,
    analisar_distribuicao_regional,
    calcular_estatisticas_por_categoria
)

def test_funcoes_aspectos_sociais():
    """Testa as funções corrigidas de aspectos sociais."""
    
    print("🧪 Testando funções de aspectos sociais...")
    
    # Dados de teste
    df_test = pd.DataFrame({
        'Q006': ['A', 'B', 'C', 'A', 'B'] * 20,  # 100 registros
        'Q025': ['X', 'Y', 'Z', 'X', 'Y'] * 20,
        'SG_UF_PROVA': ['SP', 'RJ', 'MG', 'SP', 'RJ'] * 20
    })
    
    contagem_test = pd.DataFrame({
        'Categoria': ['A', 'B', 'C'],
        'Quantidade': [50, 30, 20],
        'Percentual': [50.0, 30.0, 20.0]
    })
    
    df_regional_test = pd.DataFrame({
        'Estado': ['SP', 'RJ', 'MG', 'RS', 'PR'],
        'Categoria': ['A'] * 5,
        'Percentual': [45.2, 38.7, 42.1, 40.5, 44.8]
    })
    
    # Teste 1: calcular_estatisticas_distribuicao
    print("\n1. Testando calcular_estatisticas_distribuicao...")
    try:
        result1 = calcular_estatisticas_distribuicao(contagem_test)
        print(f"   ✅ Resultado obtido com {result1.get('total', 0)} registros")
        print(f"   📊 Índice de concentração: {result1.get('indice_concentracao', 0)}")
        print(f"   📈 Coef. variação: {result1.get('coef_variacao', 0)}%")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 2: analisar_correlacao_categorias
    print("\n2. Testando analisar_correlacao_categorias...")
    try:
        result2 = analisar_correlacao_categorias(df_test, 'Q006', 'Q025')
        print(f"   ✅ Resultado obtido")
        print(f"   📊 Coeficiente: {result2.get('coeficiente', 0)}")
        print(f"   📈 V de Cramer: {result2.get('v_cramer', 0)}")
        print(f"   🔍 Interpretação: {result2.get('interpretacao', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 3: analisar_distribuicao_regional
    print("\n3. Testando analisar_distribuicao_regional...")
    try:
        result3 = analisar_distribuicao_regional(df_regional_test, 'Q006', 'A')
        print(f"   ✅ Resultado obtido")
        print(f"   📊 Percentual médio: {result3.get('percentual_medio', 0):.1f}%")
        print(f"   📈 Coef. variação: {result3.get('coef_variacao', 0):.1f}%")
        print(f"   🌍 Variabilidade: {result3.get('variabilidade', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 4: calcular_estatisticas_por_categoria
    print("\n4. Testando calcular_estatisticas_por_categoria...")
    try:
        result4 = calcular_estatisticas_por_categoria(df_test, 'Q006')
        print(f"   ✅ Resultado obtido")
        print(f"   📊 Total: {result4.get('total', 0)}")
        print(f"   📈 Categorias: {result4.get('num_categorias', 0)}")
        print(f"   🔍 Concentração: {result4.get('classificacao_concentracao', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n✅ Teste das funções de aspectos sociais concluído!")

if __name__ == "__main__":
    test_funcoes_aspectos_sociais()
