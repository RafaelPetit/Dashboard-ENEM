"""
Teste específico para o painel de administração.
Verifica se todos os componentes do admin funcionam corretamente.
"""

import sys
from pathlib import Path

# Adicionar diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_admin_panel():
    """Testa o painel de administração."""
    print("🔧 Testando painel de administração...")
    
    try:
        # Importar configurações
        from core.config import UI_CONFIG
        
        # Teste 1: Verificar atributos necessários
        print("📋 Verificando atributos de configuração...")
        assert hasattr(UI_CONFIG, 'VERSION'), "Atributo VERSION não encontrado"
        assert hasattr(UI_CONFIG, 'LAST_UPDATE'), "Atributo LAST_UPDATE não encontrado"
        print(f"✅ Versão: {UI_CONFIG.VERSION}")
        print(f"✅ Última atualização: {UI_CONFIG.LAST_UPDATE}")
        
        # Teste 2: Importar painel de admin
        print("🛠️ Importando painel de admin...")
        from core.admin_panel import AdminPanel
        admin = AdminPanel()
        print("✅ Painel de admin importado com sucesso")
        
        # Teste 3: Verificar métodos principais
        print("⚙️ Verificando métodos do painel...")
          # Verificar se os métodos existem
        assert hasattr(admin, 'show_admin_panel'), "Método show_admin_panel não encontrado"
        assert hasattr(admin, '_show_system_panel'), "Método _show_system_panel não encontrado"
        print("✅ Métodos encontrados")
        
        # Teste 4: Testar obtenção de informações de memória via data_manager
        print("💾 Testando informações de memória...")
        from core.data_manager import data_manager
        memory_info = data_manager.get_memory_info()
        assert isinstance(memory_info, dict), "Memory info deve ser um dicionário"
        print(f"✅ Informações de memória obtidas: {len(memory_info)} campos")
        
        print("\n🎉 Painel de admin funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro no teste do painel de admin: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_config_integrity():
    """Testa a integridade das configurações."""
    print("\n🔍 Testando integridade das configurações...")
    
    try:
        from core.config import (
            UI_CONFIG, FILTER_CONFIG, DATA_CONFIG, 
            ERROR_CONFIG, FOOTER_CONFIG, PERFORMANCE_CONFIG
        )
        
        # Verificar se todas as configurações estão acessíveis
        configs = {
            'UI_CONFIG': UI_CONFIG,
            'FILTER_CONFIG': FILTER_CONFIG,
            'DATA_CONFIG': DATA_CONFIG,
            'ERROR_CONFIG': ERROR_CONFIG,
            'FOOTER_CONFIG': FOOTER_CONFIG,
            'PERFORMANCE_CONFIG': PERFORMANCE_CONFIG
        }
        
        for config_name, config_obj in configs.items():
            assert config_obj is not None, f"{config_name} não está definida"
            print(f"✅ {config_name}: OK")
        
        # Verificar atributos específicos do UI_CONFIG
        required_attrs = ['VERSION', 'LAST_UPDATE', 'PAGE_TITLE', 'MAIN_TITLE']
        for attr in required_attrs:
            assert hasattr(UI_CONFIG, attr), f"UI_CONFIG.{attr} não encontrado"
            value = getattr(UI_CONFIG, attr)
            print(f"✅ UI_CONFIG.{attr}: {value}")
        
        print("✅ Todas as configurações estão íntegras")
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação de configurações: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Teste do Painel de Administração")
    print("=" * 50)
    
    config_ok = test_config_integrity()
    admin_ok = test_admin_panel()
    
    if config_ok and admin_ok:
        print("\n✅ Painel de admin está pronto para uso!")
        sys.exit(0)
    else:
        print("\n❌ Painel de admin precisa de correções!")
        sys.exit(1)
