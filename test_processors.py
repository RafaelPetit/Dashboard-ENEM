#!/usr/bin/env python3
"""
Script de teste para validar os processadores específicos.
"""

import sys
import os
import warnings
import pandas as pd
import numpy as np

# Suprimir warnings do Streamlit
warnings.filterwarnings('ignore')

try:    # Importar processadores específicos
    from utils.prepara_dados.geral.processors import (
        HistogramDataProcessor, AttendanceAnalysisProcessor, 
        MainMetricsProcessor, CorrelationAnalysisProcessor
    )
    from utils.prepara_dados.aspectos_sociais.processors import SocioeconomicAnalysisProcessor
    from utils.prepara_dados.desempenho.processors import PerformanceDistributionProcessor
    from utils.prepara_dados.base import ProcessingConfig
    
    print("✅ Importação dos processadores: OK")
    
    # Criar configuração de teste
    config = ProcessingConfig(
        cache_ttl=600,
        batch_size=100,
        memory_limit_mb=100
    )
      # Criar DataFrame de teste
    np.random.seed(42)
    df_test = pd.DataFrame({
        'SG_UF_PROVA': ['SP', 'RJ', 'MG', 'RS', 'BA'] * 10,
        'NU_NOTA_MT': np.random.randint(200, 900, 50),
        'NU_NOTA_LC': np.random.randint(200, 900, 50),
        'NU_NOTA_CN': np.random.randint(200, 900, 50),
        'NU_NOTA_CH': np.random.randint(200, 900, 50),
        'TP_SEXO': np.random.choice(['M', 'F'], 50),
        'TP_PRESENCA_GERAL': np.random.choice([0, 1, 2, 3], 50)
    })
    
    colunas_notas = ['NU_NOTA_MT', 'NU_NOTA_LC', 'NU_NOTA_CN', 'NU_NOTA_CH']
    
    print(f"✅ DataFrame de teste criado: {df_test.shape}")
    
    # Testar HistogramDataProcessor
    try:
        hist_processor = HistogramDataProcessor(config)
        result = hist_processor.process(df_test, 'NU_NOTA_MT')
        print(f"✅ HistogramDataProcessor: {len(result)} elementos retornados")
        print(f"   - DataFrame resultante: {result[0].shape if not result[0].empty else 'vazio'}")
        print(f"   - Coluna: {result[1]}")
        print(f"   - Nome da área: {result[2]}")
    except Exception as e:
        print(f"❌ Erro em HistogramDataProcessor: {e}")
      # Testar AttendanceAnalysisProcessor
    try:
        attendance_processor = AttendanceAnalysisProcessor(config)
        result = attendance_processor.process(df_test, ['SP', 'RJ', 'MG'])
        print(f"✅ AttendanceAnalysisProcessor: {result.shape}")
        if not result.empty:
            print(f"   - Colunas: {list(result.columns)}")
    except Exception as e:
        print(f"❌ Erro em AttendanceAnalysisProcessor: {e}")
    
    # Testar MainMetricsProcessor
    try:
        metrics_processor = MainMetricsProcessor(config)
        result = metrics_processor.process(df_test, ['SP', 'RJ', 'MG'], colunas_notas)
        print(f"✅ MainMetricsProcessor: {len(result)} métricas calculadas")
        print(f"   - Total candidatos: {result.get('total_candidatos', 'N/A')}")
        print(f"   - Média geral: {result.get('media_geral', 'N/A')}")
    except Exception as e:
        print(f"❌ Erro em MainMetricsProcessor: {e}")
    
    # Testar CorrelationAnalysisProcessor
    try:
        corr_processor = CorrelationAnalysisProcessor(config)
        result = corr_processor.process(df_test, colunas_notas)
        print(f"✅ CorrelationAnalysisProcessor: {result.shape}")
        if not result.empty:
            print(f"   - Correlação MT-LC: {result.iloc[0, 1] if result.shape[0] > 0 else 'N/A'}")
    except Exception as e:
        print(f"❌ Erro em CorrelationAnalysisProcessor: {e}")
    
    # Testar outros processadores de forma básica (instanciação)
    try:
        socio_processor = SocioeconomicAnalysisProcessor()
        print("✅ SocioeconomicAnalysisProcessor: Instanciado")
    except Exception as e:
        print(f"❌ Erro em SocioeconomicAnalysisProcessor: {e}")
    
    try:
        perf_processor = PerformanceDistributionProcessor()
        print("✅ PerformanceDistributionProcessor: Instanciado")
    except Exception as e:
        print(f"❌ Erro em PerformanceDistributionProcessor: {e}")
    
    print("🎉 TESTE DOS PROCESSADORES CONCLUÍDO!")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()
