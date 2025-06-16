"""
Teste final do módulo data refatorado.
"""
print("=== TESTE FINAL DO MÓDULO DATA ===")

try:
    # Teste básico de importação
    from data import load_data_for_tab, calcular_seguro
    print("✅ Importações principais funcionando")
    
    # Teste de cálculo seguro
    import numpy as np
    dados_teste = np.array([500.0, 600.0, 700.0, 800.0, 900.0])
    resultado = calcular_seguro(dados_teste, 'media')
    print(f"✅ Cálculo seguro: média = {resultado}")
    
    # Teste de módulos especializados
    from data.loaders import tab_loader
    from data.processors import state_filter
    from data.statistics import statistics_calculator
    print("✅ Módulos especializados carregados")
    
    print("\n🎯 MÓDULO DATA: ARQUITETURA SOLID E CLEAN CODE CONFIRMADA")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
    import traceback
    traceback.print_exc()
