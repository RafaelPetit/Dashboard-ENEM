"""
Dashboard de Análise do ENEM 2023 - Versão Refatorada

Este arquivo mantém compatibilidade com a estrutura original enquanto
utiliza a nova arquitetura modular implementada no módulo core.

A nova implementação oferece:
- Melhor separação de responsabilidades
- Tratamento robusto de erros
- Gerenciamento otimizado de memória
- Código mais testável e manutenível
- Configurações centralizadas

Para desenvolvimento futuro, use a nova API:
    from core import create_dashboard, DashboardDebugger
    
    dashboard = create_dashboard()
    dashboard.run()
    DashboardDebugger.show_debug_info(dashboard)
"""

from core import run_dashboard

# Executar Dashboard usando a nova arquitetura modular
# O run_dashboard() deve ser chamado apenas uma vez para evitar erro do st.set_page_config()
run_dashboard()