#!/usr/bin/env python3
"""
Teste final de compatibilidade - verificar se todas as abas podem importar suas dependências.
"""

try:
    print("🔍 Testando imports da aba Geral...")
    from utils.prepara_dados import (
        preparar_dados_histograma,
        preparar_dados_grafico_faltas,
        preparar_dados_metricas_principais
    )
    print("✅ Aba Geral: OK")
    
    print("\n🔍 Testando imports da aba Aspectos Sociais...")
    from utils.prepara_dados import (
        preparar_dados_correlacao,
        preparar_dados_distribuicao,
        contar_candidatos_por_categoria,
        ordenar_categorias,
        preparar_dados_grafico_aspectos_por_estado,
        preparar_dados_heatmap,
        preparar_dados_barras_empilhadas,
        preparar_dados_sankey
    )
    print("✅ Aba Aspectos Sociais: OK")
    
    print("\n🔍 Testando imports da aba Desempenho...")
    from utils.prepara_dados import (
        preparar_dados_comparativo,
        preparar_dados_grafico_linha,
        preparar_dados_desempenho_geral,
        filtrar_dados_scatter
    )
    print("✅ Aba Desempenho: OK")
    
    print("\n🔍 Testando criação de processadores de desempenho...")
    from utils.prepara_dados.desempenho.processors import (
        ComparativePerformanceProcessor,
        PerformanceDistributionProcessor, 
        StatePerformanceProcessor,
        ScatterAnalysisProcessor
    )
    from utils.prepara_dados.base import ProcessingConfig
    
    config = ProcessingConfig(cache_ttl=600)
    
    comp_proc = ComparativePerformanceProcessor(config)
    dist_proc = PerformanceDistributionProcessor(config)
    state_proc = StatePerformanceProcessor(config)
    scatter_proc = ScatterAnalysisProcessor(config)
    
    print("✅ Processadores de desempenho criados com sucesso!")
    
    print("\n🎉 TODOS OS TESTES DE COMPATIBILIDADE PASSARAM!")
    print("✅ O dashboard deve funcionar sem erros de importação agora.")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
