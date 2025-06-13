"""
Testes básicos para validar a refatoração do módulo de dados.
Execute este arquivo para verificar se tudo está funcionando corretamente.
"""

import sys
from pathlib import Path

# Adicionar o diretório pai ao path para importar o módulo
sys.path.append(str(Path(__file__).parent.parent))

def test_imports():
    """Testa se todas as importações estão funcionando."""
    print("🔍 Testando importações...")
    
    try:
        # Teste de importações principais
        from data import (
            load_data_for_tab,
            filter_data_by_states,
            agrupar_estados_em_regioes,
            calcular_seguro,
            release_memory,
            optimize_dtypes
        )
        print("✅ Importações principais: OK")
        
        # Teste de importações avançadas
        from data.loaders import tab_loader, filtered_loader
        from data.processors import state_filter, data_combiner
        from data.statistics import statistics_calculator
        from data.memory import dataframe_optimizer, memory_manager
        from data.logger import logger
        print("✅ Importações avançadas: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False


def test_configuration():
    """Testa as configurações."""
    print("\n🔍 Testando configurações...")
    
    try:
        from data.config import DATA_CONFIG, STATS_CONFIG
        
        # Testar configurações de dados
        assert DATA_CONFIG.GENERIC_FILE == "sample_gerenico.parquet"
        assert DATA_CONFIG.STATE_COLUMN == "SG_UF_PROVA"
        assert DATA_CONFIG.validate_tab_name("geral")
        assert not DATA_CONFIG.validate_tab_name("inexistente")
        
        # Testar configurações de estatísticas
        assert STATS_CONFIG.is_valid_operation("media")
        assert not STATS_CONFIG.is_valid_operation("inexistente")
        
        print("✅ Configurações: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False


def test_statistics():
    """Testa o calculador de estatísticas."""
    print("\n🔍 Testando calculador de estatísticas...")
    
    try:
        from data.statistics import statistics_calculator
        import pandas as pd
        import numpy as np
        
        # Dados de teste
        test_data = pd.Series([1, 2, 3, 4, 5, np.nan])
        
        # Testar operações
        media = statistics_calculator.calculate(test_data, 'media')
        mediana = statistics_calculator.calculate(test_data, 'mediana')
        
        assert media == 3.0
        assert mediana == 3.0
        
        # Testar dados vazios
        resultado_vazio = statistics_calculator.calculate([], 'media')
        assert resultado_vazio == 0.0
        
        print("✅ Calculador de estatísticas: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro no calculador de estatísticas: {e}")
        return False


def test_memory_optimization():
    """Testa otimização de memória."""
    print("\n🔍 Testando otimização de memória...")
    
    try:
        from data.memory import dataframe_optimizer
        import pandas as pd
        import numpy as np
        
        # Criar DataFrame de teste
        df_test = pd.DataFrame({
            'int_small': [1, 2, 3, 4, 5],
            'int_large': [1000, 2000, 3000, 4000, 5000],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'string_col': ['A', 'B', 'A', 'B', 'A']
        })
        
        # Otimizar
        df_optimized = dataframe_optimizer.optimize(df_test)
        
        # Verificar se os tipos foram otimizados
        assert df_optimized['int_small'].dtype == np.uint8
        assert df_optimized['string_col'].dtype.name == 'category'
        
        print("✅ Otimização de memória: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro na otimização de memória: {e}")
        return False


def test_exceptions():
    """Testa as exceções customizadas."""
    print("\n🔍 Testando exceções customizadas...")
    
    try:
        from data.exceptions import (
            DataLoadError,
            DataValidationError,
            DataProcessingError,
            UnsupportedOperationError
        )
        
        # Testar criação de exceções
        error1 = DataLoadError("test.parquet", "Arquivo não encontrado")
        error2 = DataValidationError("campo", "valor", "esperado")
        
        assert "test.parquet" in str(error1)
        assert "campo" in str(error2)
        
        print("✅ Exceções customizadas: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas exceções: {e}")
        return False


def test_logger():
    """Testa o sistema de logging."""
    print("\n🔍 Testando sistema de logging...")
    
    try:
        from data.logger import logger
        
        # Testar métodos de log
        logger.info("Teste de log de informação")
        logger.warning("Teste de log de aviso")
        logger.debug("Teste de log de debug")
        
        # Testar mudança de nível
        logger.set_level("DEBUG")
        logger.set_level("INFO")
        
        print("✅ Sistema de logging: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de logging: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes da refatoração do módulo de dados")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_statistics,
        test_memory_optimization,
        test_exceptions,
        test_logger
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A refatoração está funcionando corretamente.")
        print("\n📋 Próximos passos:")
        print("1. Testar com dados reais do ENEM")
        print("2. Integrar com o Dashboard.py")
        print("3. Executar testes de performance")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False
    
    return True


if __name__ == "__main__":
    main()
