#!/usr/bin/env python3
"""
Teste rápido de importação para verificar se preparar_dados_correlacao funciona.
"""

try:
    from utils.prepara_dados import preparar_dados_correlacao
    print("✅ preparar_dados_correlacao importada com sucesso!")
    
    # Testar outras importações que podem estar causando problemas
    from utils.prepara_dados import (
        preparar_dados_histograma,
        preparar_dados_grafico_faltas,
        preparar_dados_metricas_principais
    )
    print("✅ Outras funções também importadas com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()
