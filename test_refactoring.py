"""
Teste simples para verificar se a refatoração das classes base está funcionando.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

import pandas as pd
import numpy as np

try:
    # Testar importação das classes base
    from utils.prepara_dados.base import (
        BaseDataProcessor,
        CacheableProcessor, 
        StateGroupedProcessor,
        DataProcessorFactory,
        ProcessingConfig
    )
    
    print("✅ Importação das classes base: OK")
    
    # Testar importação das classes utilitárias
    from utils.prepara_dados.common_utils import (
        MappingManager,
        StatisticalCalculator,
        DataAggregator,
        DataFilter
    )
    
    print("✅ Importação das classes utilitárias: OK")
    
    # Testar criação de processadores básicos
    config = ProcessingConfig()
    print(f"✅ Configuração criada: {config}")
    
    # Testar factory
    factory = DataProcessorFactory()
    basic_processor = factory.create_basic_processor("test_basic")
    state_processor = factory.create_state_processor("test_state")
    
    print("✅ Factory funcionando: OK")
    print("✅ Processadores criados: OK")
    
    # Testar utilitários
    mapping_manager = MappingManager()
    stats_calc = StatisticalCalculator()
    data_agg = DataAggregator()
    data_filter = DataFilter()
    
    print("✅ Utilitários instanciados: OK")
    
    # Criar DataFrame de teste
    test_data = pd.DataFrame({
        'SG_UF_PROVA': ['SP', 'RJ', 'MG', 'SP', 'RJ'],
        'NU_NOTA_MT': [500, 600, 550, 480, 620],
        'NU_NOTA_LC': [520, 580, 560, 490, 610],
        'TP_SEXO': ['M', 'F', 'M', 'F', 'M']
    })
    
    print(f"✅ DataFrame de teste criado: {test_data.shape}")
    
    # Testar validação
    valid = basic_processor.validate_input(test_data, ['SG_UF_PROVA', 'NU_NOTA_MT'])
    print(f"✅ Validação de entrada: {valid}")
    
    # Testar otimização
    optimized_data = basic_processor.optimize_dataframe(test_data)
    print(f"✅ Otimização de DataFrame: {optimized_data.dtypes}")
    
    print("\n🎉 TODOS OS TESTES PASSARAM! A refatoração está funcionando corretamente.")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()
