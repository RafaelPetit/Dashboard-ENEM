#!/usr/bin/env python3
"""
Teste de importação de todas as funções usadas pelas abas.
"""

try:
    # Testar imports da aba aspectos sociais
    from utils.prepara_dados import (
        preparar_dados_correlacao,
        preparar_dados_distribuicao,
        contar_candidatos_por_categoria,
        ordenar_categorias,
        preparar_dados_grafico_aspectos_por_estado
    )
    print("✅ Funções de aspectos sociais importadas com sucesso!")
    
    # Testar imports da aba geral
    from utils.prepara_dados import (
        preparar_dados_histograma,
        preparar_dados_grafico_faltas,
        preparar_dados_metricas_principais
    )
    print("✅ Funções gerais importadas com sucesso!")
    
    # Testar imports da aba desempenho
    from utils.prepara_dados import (
        preparar_dados_comparativo,
        preparar_dados_grafico_linha,
        preparar_dados_desempenho_geral
    )
    print("✅ Funções de desempenho importadas com sucesso!")
    
    print("🎉 TODAS AS IMPORTAÇÕES FUNCIONARAM!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()
