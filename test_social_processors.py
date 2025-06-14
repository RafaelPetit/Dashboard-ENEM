#!/usr/bin/env python3
"""
Script de teste para validar os processadores de aspectos sociais.
"""

import sys
import os
import warnings
import pandas as pd
import numpy as np

# Suprimir warnings do Streamlit
warnings.filterwarnings('ignore')

try:
    # Importar processadores de aspectos sociais
    from utils.prepara_dados.aspectos_sociais.processors import (
        SocioeconomicAnalysisProcessor, SocialCorrelationProcessor
    )
    from utils.prepara_dados.base import ProcessingConfig
    
    print("✅ Importação dos processadores sociais: OK")
    
    # Criar configuração de teste
    config = ProcessingConfig(
        cache_ttl=600,
        batch_size=100,
        memory_limit_mb=100
    )
    
    # Criar DataFrame de teste com aspectos sociais
    np.random.seed(42)
    df_test = pd.DataFrame({
        'SG_UF_PROVA': ['SP', 'RJ', 'MG', 'RS', 'BA'] * 20,
        'TP_SEXO': np.random.choice(['M', 'F'], 100),
        'TP_COR_RACA': np.random.choice([1, 2, 3, 4, 5, 6], 100),
        'Q001': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], 100),  # Escolaridade pai
        'Q002': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], 100),  # Escolaridade mãe
        'Q006': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'], 100),  # Renda
        'TP_FAIXA_ETARIA': np.random.choice([1, 2, 3, 4, 5], 100),
        'TP_DEPENDENCIA_ADM_ESC': np.random.choice([1, 2, 3, 4], 100)
    })
    
    print(f"✅ DataFrame de teste criado: {df_test.shape}")
    
    # Testar SocioeconomicAnalysisProcessor
    try:
        socio_processor = SocioeconomicAnalysisProcessor(config)
        
        # Simular variáveis categóricas
        variaveis_categoricas = {
            'Q001': {'name': 'Escolaridade do Pai'},
            'Q002': {'name': 'Escolaridade da Mãe'}
        }
        
        # Usar o método process diretamente (sem _process_internal pois é privado)
        print("⚠️  SocioeconomicAnalysisProcessor: Processador criado (implementação em progresso)")
        
    except Exception as e:
        print(f"❌ Erro em SocioeconomicAnalysisProcessor: {e}")
    
    # Testar SocialCorrelationProcessor
    try:
        corr_processor = SocialCorrelationProcessor(config)
        
        # Simular dicionário de variáveis sociais
        variaveis_sociais = {
            'Q001': {
                'mapeamento': {
                    'A': 'Nunca estudou',
                    'B': 'Ensino fundamental incompleto',
                    'C': 'Ensino fundamental completo',
                    'D': 'Ensino médio incompleto',
                    'E': 'Ensino médio completo',
                    'F': 'Ensino superior incompleto',
                    'G': 'Ensino superior completo',
                    'H': 'Pós-graduação'
                }
            },
            'Q002': {
                'mapeamento': {
                    'A': 'Nunca estudou',
                    'B': 'Ensino fundamental incompleto',
                    'C': 'Ensino fundamental completo',
                    'D': 'Ensino médio incompleto',
                    'E': 'Ensino médio completo',
                    'F': 'Ensino superior incompleto',
                    'G': 'Ensino superior completo',
                    'H': 'Pós-graduação'
                }
            }
        }
        
        result = corr_processor.process(df_test, 'Q001', 'Q002', variaveis_sociais)
        print(f"✅ SocialCorrelationProcessor: {len(result)} elementos retornados")
        if len(result) == 3:
            df_result, var_x, var_y = result
            print(f"   - DataFrame resultante: {df_result.shape if not df_result.empty else 'vazio'}")
            print(f"   - Variável X: {var_x}")
            print(f"   - Variável Y: {var_y}")
            
    except Exception as e:
        print(f"❌ Erro em SocialCorrelationProcessor: {e}")
        import traceback
        traceback.print_exc()
    
    print("🎉 TESTE DOS PROCESSADORES SOCIAIS CONCLUÍDO!")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()
