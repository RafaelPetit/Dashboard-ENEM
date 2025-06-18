"""
API principal do módulo core do Dashboard.
Fornece interface unificada para todos os componentes do core.
"""

import streamlit as st
import gc
from typing import Dict, Any, List, Optional

from .config import UI_CONFIG, PERFORMANCE_CONFIG
from .filters import FilterFactory
from .data_manager import data_manager
from .tab_renderers import tab_executor
from .ui_components import ui_factory
from .mapping_manager import mapping_manager
from .error_handler import error_handler, handle_exceptions, safe_execute
from .exceptions import DashboardError
from .performance_monitor import performance_monitor, ContextTimer
from .admin_panel import admin_panel


class DashboardCore:
    """
    Classe principal que orquestra todos os componentes do Dashboard.
    Implementa o padrão Facade para simplificar a interface.
    """
    
    def __init__(self):
        """Inicializa o core do Dashboard."""
        self.mappings = None
        self.state_filter = None
        self.initialized = False
    
    @handle_exceptions(error_handler, "initialization")
    def initialize(self) -> bool:
        """
        Inicializa todos os componentes do Dashboard.
        
        Returns:
            True se inicialização foi bem-sucedida
        """
        try:
            # Configurar página
            page_config = ui_factory.create_page_config()
            page_config.render()
            
            # Carregar mapeamentos
            self.mappings = mapping_manager.get_all_mappings()            # Carregar dados para filtros
            filter_data = data_manager.load_filter_data()
            
            # Verificar se temos dados válidos e a coluna necessária
            if filter_data is None or filter_data.empty:
                raise ValueError("Dados de filtro não disponíveis")
            
            if 'SG_UF_PROVA' not in filter_data.columns:
                raise ValueError("Coluna SG_UF_PROVA não encontrada nos dados de filtro")
            
            # Obter estados únicos de forma segura
            # Garantir que estamos trabalhando com uma Series
            sg_uf_series = filter_data['SG_UF_PROVA']
            if hasattr(sg_uf_series, 'unique'):
                available_states = sorted(sg_uf_series.dropna().unique().tolist())
            else:
                # Fallback se por algum motivo não for uma Series
                available_states = sorted(filter_data['SG_UF_PROVA'].values.flatten())
                available_states = list(set([x for x in available_states if x is not None]))
            
            # Criar filtro de estados
            self.state_filter = FilterFactory.create_state_filter(
                self.mappings['regioes_mapping'],
                available_states
            )
            
            # Liberar dados de filtro
            data_manager.release_memory(filter_data)
            
            self.initialized = True
            return True
            
        except Exception as e:
            error_handler.handle_general_error("initialization", e)
            return False
    def render_dashboard(self) -> None:
        """Renderiza o Dashboard completo."""
        if not self.initialized:
            st.error("Dashboard não foi inicializado corretamente.")
            return
        
        try:
            # Renderizar cabeçalho
            header = ui_factory.create_header()
            header.render()
            
            # Renderizar sidebar com filtros e painel admin
            self._render_sidebar()
            
            # Renderizar conteúdo principal
            with ContextTimer(performance_monitor, "render_main_content"):
                self._render_main_content()
            
            # Renderizar rodapé
            footer = ui_factory.create_footer()
            footer.render()            
            # Otimizar performance
            if PERFORMANCE_CONFIG.FORCE_GC_AFTER_TAB:
                performance_monitor.force_gc_and_record()
                
        except Exception as e:
            error_handler.handle_general_error("dashboard_render", e)
    
    def _render_sidebar(self) -> None:
        """Renderiza a sidebar com filtros."""
        try:
            # Cabeçalho da sidebar
            sidebar_header = ui_factory.create_sidebar_header()
            sidebar_header.render()
            
            # Renderizar filtros de estado
            self.state_filter.render_filters()
            
            # Renderizar painel de administração
            admin_panel.show_admin_panel()
            
        except Exception as e:
            error_handler.handle_ui_error("sidebar", e)
    
    def _render_main_content(self) -> None:
        """Renderiza o conteúdo principal com abas."""
        try:
            # Obter estados selecionados
            selected_states = self.state_filter.get_selected_states()
            display_names = self.state_filter.get_display_names()
            
            # Mostrar status dos filtros
            status_display = ui_factory.create_status_display()
            status_display.show_filter_status(
                selected_states, 
                len(mapping_manager.get_available_states()),
                display_names
            )
            
            # Criar e renderizar abas
            tabs_component = ui_factory.create_tabs()
            tabs = tabs_component.render()
            
            # Renderizar cada aba
            self._render_tabs(tabs, selected_states, display_names)
            
        except Exception as e:
            error_handler.handle_general_error("main_content", e)
    
    def _render_tabs(self, tabs, selected_states: List[str], display_names: List[str]) -> None:
        """
        Renderiza todas as abas do Dashboard.
        
        Args:
            tabs: Objeto de abas do Streamlit
            selected_states: Estados selecionados
            display_names: Nomes para exibição
        """
        tab_names = UI_CONFIG.TAB_NAMES
        
        for i, tab_name in enumerate(tab_names):
            with tabs[i]:
                safe_execute(
                    self._render_single_tab,
                    error_handler,
                    f"tab_{tab_name}",
                    tab_name,
                    selected_states,
                    display_names
                )
    
    def _render_single_tab(self, tab_name: str, selected_states: List[str], 
                          display_names: List[str]) -> None:
        """
        Renderiza uma aba específica.
        
        Args:
            tab_name: Nome da aba
            selected_states: Estados selecionados
            display_names: Nomes para exibição
        """
        try:
            # Registrar mudança de aba para métricas
            performance_monitor.record_tab_switch(tab_name)
            
            # Obter mapeamentos necessários para a aba
            tab_mappings = mapping_manager.get_required_mappings(tab_name)
            
            # Executar aba
            with ContextTimer(performance_monitor, f"render_{tab_name.lower()}_tab"):
                tab_executor.execute_tab(
                    tab_name,
                    selected_states,
                    display_names,
                    tab_mappings
                )
            
        except Exception as e:
            performance_monitor.record_error()
            error_handler.handle_tab_error(tab_name, e)


class DashboardAPI:
    """API simplificada para uso do Dashboard."""
    
    def __init__(self):
        """Inicializa a API."""
        self.core = DashboardCore()
    
    def run(self) -> None:
        """
        Executa o Dashboard completo.
        Método principal para iniciar a aplicação.
        """
        try:
            # Inicializar core
            if not self.core.initialize():
                st.error("❌ Falha na inicialização do Dashboard")
                st.stop()
            
            # Renderizar dashboard
            self.core.render_dashboard()
            
        except Exception as e:
            st.error(f"❌ Erro crítico no Dashboard: {str(e)}")
            st.error("Por favor, recarregue a página.")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo de erros ocorridos.
        
        Returns:
            Dicionário com estatísticas de erro
        """
        return error_handler.get_error_summary()
    
    def reset_errors(self) -> None:
        """Reseta o tracking de erros."""
        error_handler.reset_error_tracking()


class DashboardDebugger:
    """Utilitários para debug do Dashboard."""
    
    @staticmethod
    def show_debug_info(dashboard_api: DashboardAPI) -> None:
        """
        Exibe informações de debug na sidebar.
        
        Args:
            dashboard_api: Instância da API do Dashboard
        """
        if st.sidebar.checkbox("Modo Debug", value=False):
            st.sidebar.subheader("Informações de Debug")
            
            # Estatísticas de erro
            error_summary = dashboard_api.get_error_summary()
            st.sidebar.json(error_summary)
            
            # Informações de memória
            try:
                memory_info = data_manager.get_memory_info()
                st.sidebar.json(memory_info)
            except Exception as e:
                st.sidebar.error(f"Erro ao obter info de memória: {e}")
            
            # Botão para limpar cache
            if st.sidebar.button("Limpar Cache"):
                data_manager.clear_cache()
                st.sidebar.success("Cache limpo!")
            
            # Botão para resetar erros
            if st.sidebar.button("Resetar Erros"):
                dashboard_api.reset_errors()
                st.sidebar.success("Erros resetados!")


# Funções de conveniência para compatibilidade

def run_dashboard() -> None:
    """
    Função de conveniência para executar o Dashboard.
    Compatível com o código legado.
    """
    api = DashboardAPI()
    api.run()


def create_dashboard() -> DashboardAPI:
    """
    Cria uma instância da API do Dashboard.
    
    Returns:
        Instância configurada da API
    """
    return DashboardAPI()


# Instâncias globais
dashboard_api = DashboardAPI()
dashboard_debugger = DashboardDebugger()
