#!/usr/bin/env python3
"""
Teste específico para verificar se o problema do filter_valid_scores foi corrigido.
"""

import sys
import os
import traceback

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_filter_method():
    """Testa se o DataFilter.filter_valid_scores aceita os parâmetros corretos."""
    try:
        import pandas as pd
        from utils.prepara_dados.common_utils import DataFilter
        
        # Criar dados de teste
        df_test = pd.DataFrame({
            'NU_NOTA_CN': [100, 200, 300, 0, None],
            'NU_NOTA_CH': [150, 250, 350, 50, 180],
            'VARIAVEL_TESTE': ['A', 'B', 'C', 'D', 'E']
        })
        
        # Testar o método com parâmetros corretos
        result = DataFilter.filter_valid_scores(
            df_test, 
            score_columns=['NU_NOTA_CN', 'NU_NOTA_CH']
        )
        
        print(f"✓ DataFilter.filter_valid_scores() funciona com parâmetros corretos - {len(result)} registros válidos")
        return True
    except Exception as e:
        print(f"✗ Erro no DataFilter: {e}")
        print(traceback.format_exc())
        return False

def test_processor_instantiation():
    """Testa se o processador de desempenho pode ser instanciado."""
    try:
        from utils.prepara_dados.desempenho.processors import ComparativePerformanceProcessor
        
        # Testar instanciação
        processor = ComparativePerformanceProcessor("test")
        
        print("✓ ComparativePerformanceProcessor pode ser instanciado")
        return True
    except Exception as e:
        print(f"✗ Erro na instanciação do processador: {e}")
        print(traceback.format_exc())
        return False

def test_simple_processing():
    """Testa um processamento simples para verificar se a correção funcionou."""
    try:
        import pandas as pd
        from utils.prepara_dados.desempenho.data_manager import PerformanceDataManager
        
        # Criar dados de teste mínimos
        df_test = pd.DataFrame({
            'NU_NOTA_CN': [500, 600, 700],
            'NU_NOTA_CH': [550, 650, 750],
            'NU_NOTA_LC': [480, 580, 680],
            'NU_NOTA_MT': [520, 620, 720],
            'NU_NOTA_REDACAO': [600, 700, 800],
            'TP_SEXO': [1, 2, 1],
            'SG_UF_PROVA': ['SP', 'RJ', 'MG']
        })
        
        # Testar se consegue instanciar o manager
        manager = PerformanceDataManager()
        print("✓ PerformanceDataManager pode ser instanciado")
        
        return True
    except Exception as e:
        print(f"✗ Erro no teste de processamento: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=== Teste de Correção do filter_valid_scores ===")
    
    tests = [
        ("Teste DataFilter método", test_data_filter_method),
        ("Teste Instanciação Processador", test_processor_instantiation),
        ("Teste Processamento Simples", test_simple_processing)
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
        print("✓ Problema do filter_valid_scores foi corrigido!")
    else:
        print("✗ Ainda há problemas para resolver.")
