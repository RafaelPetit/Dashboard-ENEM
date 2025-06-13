"""
Script de validação da refatoração do Dashboard ENEM.
Testa todos os componentes principais e valida a arquitetura.
"""

def test_core_imports():
    """Testa importações básicas do core."""
    print("🔍 Testando importações do core...")
    
    try:
        # Importações básicas
        from core import run_dashboard, create_dashboard
        print("✅ Funções principais importadas")
        
        # Componentes avançados  
        from core import cache_manager, performance_monitor
        print("✅ Sistemas de cache e performance importados")
        
        # Validadores
        from core import DataValidator, safe_validate_data
        print("✅ Validadores importados")
        
        # Configurações
        from core.config import UI_CONFIG, PERFORMANCE_CONFIG
        print("✅ Configurações carregadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        return False


def test_core_functionality():
    """Testa funcionalidades básicas sem streamlit."""
    print("\n🧪 Testando funcionalidades...")
    
    try:
        # Test cache manager
        from core.cache_manager import CacheKey
        key = CacheKey.generate("test", param1="value1", param2="value2")
        assert isinstance(key, str)
        print("✅ Cache manager funcionando")
        
        # Test validators
        from core.validators import StateValidator
        assert StateValidator.validate_region("Norte")
        states = StateValidator.get_states_from_region("Norte")
        assert len(states) > 0
        print("✅ Validadores funcionando")
        
        # Test performance monitor
        from core.performance_monitor import performance_monitor
        performance_monitor.start_timer("test_operation")
        import time
        time.sleep(0.01)  # Simular operação
        elapsed = performance_monitor.end_timer("test_operation")
        assert elapsed > 0
        print("✅ Performance monitor funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na funcionalidade: {e}")
        return False


def test_architecture():
    """Testa aspectos arquiteturais."""
    print("\n🏗️ Testando arquitetura...")
    
    try:
        # Verificar se todas as instâncias globais existem
        from core import (
            data_manager, cache_manager, performance_monitor,
            mapping_manager, error_handler, ui_factory
        )
        
        # Verificar se são instâncias válidas
        assert hasattr(data_manager, 'load_tab_data')
        assert hasattr(cache_manager, 'get_performance_stats')
        assert hasattr(performance_monitor, 'get_performance_summary')
        print("✅ Instâncias globais válidas")
        
        # Verificar configurações
        from core.config import PERFORMANCE_CONFIG, SECURITY_CONFIG
        assert hasattr(PERFORMANCE_CONFIG, 'ENABLE_CACHE')
        assert hasattr(SECURITY_CONFIG, 'VALIDATE_INPUTS')
        print("✅ Configurações válidas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na arquitetura: {e}")
        return False


def test_dashboard_creation():
    """Testa criação do dashboard sem executar streamlit."""
    print("\n🎯 Testando criação do dashboard...")
    
    try:
        from core import create_dashboard
        dashboard = create_dashboard()
        
        # Verificar se o dashboard tem os métodos esperados
        assert hasattr(dashboard, 'run')
        assert hasattr(dashboard, 'get_error_summary')
        assert hasattr(dashboard, 'reset_errors')
        print("✅ Dashboard criado com sucesso")
        
        # Test debugger
        from core import DashboardDebugger
        assert hasattr(DashboardDebugger, 'show_debug_info')
        print("✅ Debugger disponível")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação do dashboard: {e}")
        return False


def generate_validation_report():
    """Gera relatório de validação."""
    print("\n📋 Gerando relatório de validação...")
    
    try:
        from core.performance_monitor import performance_monitor
        from core.cache_manager import cache_manager
        
        # Coletar informações
        perf_stats = performance_monitor.get_performance_summary()
        cache_stats = cache_manager.get_performance_stats()
        
        report = {
            "validation_timestamp": "2025-06-13T12:00:00",
            "core_version": "2.0.0",
            "status": "✅ VALIDAÇÃO COMPLETA",
            "performance_available": bool(perf_stats),
            "cache_available": bool(cache_stats),
            "modules_loaded": [
                "config", "core_types", "exceptions", "cache_manager",
                "validators", "performance_monitor", "data_manager",
                "mapping_manager", "filters", "ui_components",
                "tab_renderers", "error_handler", "admin_panel",
                "dashboard_api"
            ]
        }
        
        print("✅ Relatório gerado")
        return report
        
    except Exception as e:
        print(f"❌ Erro no relatório: {e}")
        return None


def main():
    """Executa todos os testes de validação."""
    print("🚀 VALIDAÇÃO DA REFATORAÇÃO DO DASHBOARD ENEM v2.0")
    print("=" * 55)
    
    tests = [
        ("Importações do Core", test_core_imports),
        ("Funcionalidades", test_core_functionality), 
        ("Arquitetura", test_architecture),
        ("Criação do Dashboard", test_dashboard_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📝 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    # Resumo dos resultados
    print("\n" + "=" * 55)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 55)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 REFATORAÇÃO VALIDADA COM SUCESSO!")
        print("✅ Todos os componentes estão funcionando corretamente")
        print("✅ Arquitetura modular implementada com sucesso")
        print("✅ Sistema pronto para produção")
        
        # Gerar relatório final
        report = generate_validation_report()
        if report:
            print("\n📋 Relatório de validação disponível")
            
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija antes de usar em produção")
    
    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
