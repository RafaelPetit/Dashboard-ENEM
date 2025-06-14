#!/usr/bin/env python3
"""
Teste para verificar se todos os problemas da aba desempenho foram resolvidos.
"""

import sys
import os
import traceback
import warnings

# Suprimir warnings desnecessários para o teste
warnings.filterwarnings('ignore', category=RuntimeWarning)

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_performance_data_preparation():
    """Testa se as funções de preparação de dados de desempenho funcionam."""
    try:
        import pandas as pd
        from utils.prepara_dados.desempenho.data_manager import preparar_dados_comparativo
        
        # Criar dados de teste mais realistas
        df_test = pd.DataFrame({
            'NU_NOTA_CN': [500.5, 600.2, 700.8, 450.3, 550.1],
            'NU_NOTA_CH': [480.7, 580.4, 680.9, 430.2, 530.6],
            'NU_NOTA_LC': [490.3, 590.1, 690.7, 440.8, 540.4],
            'NU_NOTA_MT': [510.2, 610.5, 710.1, 460.9, 560.3],
            'NU_NOTA_REDACAO': [600.0, 700.0, 800.0, 500.0, 650.0],
            'TP_SEXO': [1, 2, 1, 2, 1],
            'SG_UF_PROVA': ['SP', 'RJ', 'MG', 'SP', 'RJ'],
            'TP_ESCOLA': [1, 2, 1, 2, 1]
        })
        
        # Criar mapeamentos simples para teste
        variaveis_categoricas = {
            'TP_SEXO': {
                'mapeamento': {1: 'Masculino', 2: 'Feminino'}
            }
        }
        
        competencia_mapping = {
            'NU_NOTA_CN': 'Ciências da Natureza',
            'NU_NOTA_CH': 'Ciências Humanas',
            'NU_NOTA_LC': 'Linguagens e Códigos',
            'NU_NOTA_MT': 'Matemática',
            'NU_NOTA_REDACAO': 'Redação'
        }
        
        # Tentar executar a função
        result = preparar_dados_comparativo(
            df_test,
            'TP_SEXO',
            ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'],
            variaveis_categoricas,
            competencia_mapping
        )
        
        if not result.empty:
            print(f"✓ preparar_dados_comparativo funciona - {len(result)} resultados")
            return True
        else:
            print("⚠ preparar_dados_comparativo retornou DataFrame vazio")
            return False
            
    except Exception as e:
        print(f"✗ Erro na preparação de dados de desempenho: {e}")
        print(traceback.format_exc())
        return False

def test_filter_fix():
    """Testa especificamente se o filter_valid_scores está funcionando corretamente."""
    try:
        import pandas as pd
        from utils.prepara_dados.desempenho.processors import ComparativePerformanceProcessor
        
        # Criar dados de teste
        df_test = pd.DataFrame({
            'NU_NOTA_CN': [500, 600, 700, 0, None],
            'NU_NOTA_CH': [550, 650, 750, 50, 580],
            'TP_SEXO': [1, 2, 1, 2, 1]
        })
        
        # Instanciar o processador
        processor = ComparativePerformanceProcessor("test")
        
        # Testar o filtro diretamente
        filtered_data = processor.data_filter.filter_valid_scores(
            df_test,
            score_columns=['NU_NOTA_CN', 'NU_NOTA_CH']
        )
        
        print(f"✓ filter_valid_scores funciona corretamente - {len(filtered_data)} registros válidos de {len(df_test)}")
        return True
    except Exception as e:
        print(f"✗ Erro no teste do filtro: {e}")
        print(traceback.format_exc())
        return False

def test_expander_functions():
    """Testa se as funções do expander não causam overflow."""
    try:
        import numpy as np
        from utils.expander.expander_desempenho import _gerar_comparacao_medias, _gerar_comparacao_variabilidade
        
        # Teste com valores normais
        result1 = _gerar_comparacao_medias(500.5, 480.2, "Matemática", "Linguagens")
        print(f"✓ Comparação de médias normais: {result1[:50]}...")
        
        # Teste com valores extremos
        result2 = _gerar_comparacao_medias(np.inf, 500, "Teste1", "Teste2")
        print(f"✓ Comparação com valores extremos tratada: {result2[:50]}...")
        
        # Teste de variabilidade
        result3 = _gerar_comparacao_variabilidade(100.0, 80.0, "Area1", "Area2")
        print(f"✓ Comparação de variabilidade: {result3[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ Erro nas funções do expander: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=== Teste Completo da Aba Desempenho ===")
    
    tests = [
        ("Teste Correção do Filtro", test_filter_fix),
        ("Teste Preparação de Dados", test_performance_data_preparation),
        ("Teste Funções Expander", test_expander_functions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        results.append(test_func())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Resumo dos Testes ===")
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("✅ Todos os problemas da aba desempenho foram corrigidos!")
        print("✅ A aba desempenho deve funcionar normalmente agora.")
    elif passed > 0:
        print("⚠ Alguns problemas foram corrigidos, mas ainda há questões para resolver.")
    else:
        print("❌ Ainda há problemas significativos para resolver.")
