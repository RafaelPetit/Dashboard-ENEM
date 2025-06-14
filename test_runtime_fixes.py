#!/usr/bin/env python3
"""
Teste final para verificar se todos os problemas de runtime foram corrigidos.
"""

import sys
import os
import traceback

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mapping_manager():
    """Testa se o MappingManager tem o método get_mappings."""
    try:
        from utils.prepara_dados.common_utils import MappingManager
        
        manager = MappingManager()
        mappings = manager.get_mappings()
        
        # Verificar se tem as chaves esperadas
        expected_keys = ['config_processamento']
        for key in expected_keys:
            if key in mappings:
                print(f"✓ MappingManager tem a chave '{key}'")
            else:
                print(f"✗ MappingManager não tem a chave '{key}'")
                return False
        
        print("✓ MappingManager.get_mappings() funciona corretamente")
        return True
    except Exception as e:
        print(f"✗ Erro no MappingManager: {e}")
        print(traceback.format_exc())
        return False

def test_data_filter():
    """Testa se o DataFilter tem o método filter_valid_scores."""
    try:
        import pandas as pd
        from utils.prepara_dados.common_utils import DataFilter
        
        # Criar dados de teste
        df_test = pd.DataFrame({
            'NU_NOTA_CN': [100, 200, 300, 0, None],
            'NU_NOTA_CH': [150, 250, 350, 50, 180]
        })
        
        # Testar o método
        result = DataFilter.filter_valid_scores(df_test, ['NU_NOTA_CN', 'NU_NOTA_CH'])
        
        print(f"✓ DataFilter.filter_valid_scores() funciona - {len(result)} registros válidos")
        return True
    except Exception as e:
        print(f"✗ Erro no DataFilter: {e}")
        print(traceback.format_exc())
        return False

def test_processors_instantiation():
    """Testa se os processadores podem ser instanciados."""
    try:
        from utils.prepara_dados.geral.processors import HistogramDataProcessor
        from utils.prepara_dados.desempenho.processors import ComparativePerformanceProcessor
        from utils.prepara_dados.aspectos_sociais.processors import SocioeconomicAnalysisProcessor
        
        # Testar instanciação
        hist_proc = HistogramDataProcessor("test")
        comp_proc = ComparativePerformanceProcessor("test")
        corr_proc = SocioeconomicAnalysisProcessor("test")
        
        print("✓ Todos os processadores podem ser instanciados")
        return True
    except Exception as e:
        print(f"✗ Erro na instanciação dos processadores: {e}")
        print(traceback.format_exc())
        return False

def test_data_managers():
    """Testa se os data managers podem ser instanciados."""
    try:
        from utils.prepara_dados.geral.data_manager import GeralDataManager
        from utils.prepara_dados.desempenho.data_manager import PerformanceDataManager
        from utils.prepara_dados.aspectos_sociais.data_manager import SocialDataManager
        
        # Testar instanciação
        geral_manager = GeralDataManager()
        perf_manager = PerformanceDataManager()
        social_manager = SocialDataManager()
        
        print("✓ Todos os data managers podem ser instanciados")
        return True
    except Exception as e:
        print(f"✗ Erro na instanciação dos data managers: {e}")
        print(traceback.format_exc())
        return False

def test_main_api_imports():
    """Testa se a API principal pode ser importada."""
    try:
        from utils.prepara_dados import (
            preparar_dados_histograma,
            preparar_dados_correlacao,
            filtrar_dados_scatter
        )
        
        print("✓ Funções principais da API podem ser importadas")
        return True
    except Exception as e:
        print(f"✗ Erro na importação da API principal: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=== Teste Final de Correções de Runtime ===")
    
    tests = [
        ("Teste MappingManager", test_mapping_manager),
        ("Teste DataFilter", test_data_filter),
        ("Teste Instanciação Processadores", test_processors_instantiation),
        ("Teste Instanciação Data Managers", test_data_managers),
        ("Teste Importações API Principal", test_main_api_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        results.append(test_func())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Resumo Final ===")
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("✓ Todos os problemas de runtime foram corrigidos!")
        print("✓ O dashboard deve funcionar agora sem erros de método não encontrado.")
    else:
        print("✗ Ainda há problemas para resolver.")
        print("Verifique os erros acima e corrija antes de testar o dashboard.")
