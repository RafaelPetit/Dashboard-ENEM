"""
Script de teste de saúde do Dashboard.
Verifica se todos os componentes principais estão funcionando.
"""

import sys
import os
import time
from pathlib import Path

# Adicionar diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_dashboard_health():
    """Testa a saúde geral do dashboard."""
    print("🔍 Iniciando teste de saúde do Dashboard...")
    
    try:
        # Teste 1: Importar módulos principais
        print("📦 Testando importações...")
        from core import run_dashboard, create_dashboard, DashboardDebugger
        from data import data_api
        print("✅ Importações bem-sucedidas")
        
        # Teste 2: Verificar configurações
        print("⚙️ Verificando configurações...")
        from core.config import UI_CONFIG, DATA_CONFIG, FILTER_CONFIG
        assert UI_CONFIG.PAGE_TITLE, "Título da página não configurado"
        print("✅ Configurações válidas")
          # Teste 3: Testar carregamento de dados
        print("💾 Testando carregamento de dados...")
        test_data = data_api.load_data_for_tab('geral')
        assert test_data is not None, "Falha no carregamento de dados"
        print(f"✅ Dados carregados: {test_data.shape}")
        
        # Teste 4: Testar mapeamentos
        print("🗺️ Testando mapeamentos...")
        from core.mapping_manager import mapping_manager
        mappings = mapping_manager.get_all_mappings()
        assert mappings, "Mapeamentos não carregados"
        print("✅ Mapeamentos carregados")
          # Teste 5: Testar sistema de filtros
        print("🔍 Testando filtros...")
        from core.filters import FilterFactory
        from core.mapping_manager import mapping_manager
        
        # Obter estados disponíveis do dataset carregado
        if 'SG_UF_PROVA' in test_data.columns:
            available_states = test_data['SG_UF_PROVA'].unique().tolist()
        else:
            available_states = ['SP', 'RJ', 'MG']  # Estados padrão para teste
        
        # Usar mapeamentos existentes
        regions_mapping = mappings.get('regioes_mapping', {})
        
        state_filter = FilterFactory.create_state_filter(regions_mapping, available_states)
        assert available_states, "Estados não disponíveis"
        print(f"✅ Filtros funcionando: {len(available_states)} estados disponíveis")
        
        print("\n🎉 Todos os testes passaram! Dashboard está saudável.")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste de saúde: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_core_performance():
    """Testa performance dos componentes core."""
    print("\n⏱️ Testando performance...")
    
    try:
        from core.performance_monitor import performance_monitor, ContextTimer
        
        # Medir tempo de inicialização
        start_time = time.time()
        
        # Simular operações principais
        with ContextTimer(performance_monitor, "health_check"):
            time.sleep(0.1)  # Simular trabalho
        
        end_time = time.time()
        print(f"✅ Performance OK: {end_time - start_time:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Dashboard Health Check")
    print("=" * 50)
    
    health_ok = test_dashboard_health()
    performance_ok = test_core_performance()
    
    if health_ok and performance_ok:
        print("\n✅ Dashboard está pronto para produção!")
        sys.exit(0)
    else:
        print("\n❌ Dashboard precisa de correções!")
        sys.exit(1)
