"""
Componentes de interface do usuário para o Dashboard.
Implementa componentes reutilizáveis seguindo padrões de design.
"""

import streamlit as st
from typing import Dict, Any, Optional, List

from .core_types import BaseUIComponent
from .config import UI_CONFIG, FOOTER_CONFIG
from .exceptions import UIComponentError

# Variável global para rastrear se st.set_page_config já foi chamado
_PAGE_CONFIG_CALLED = False


class PageConfigComponent(BaseUIComponent):
    """Componente para configuração inicial da página."""
    
    def __init__(self):
        super().__init__(UI_CONFIG)
    
    def render(self) -> None:
        """Configura a página do Streamlit."""
        global _PAGE_CONFIG_CALLED
        
        try:
            # Verificar se já foi configurado para evitar erro de múltiplas chamadas
            if _PAGE_CONFIG_CALLED:
                return
            
            # Tentar configurar apenas uma vez
            st.set_page_config(
                page_title=self.config.PAGE_TITLE,
                page_icon=self.config.PAGE_ICON,
                layout=self.config.LAYOUT,
                initial_sidebar_state=self.config.INITIAL_SIDEBAR_STATE
            )
            _PAGE_CONFIG_CALLED = True
                
        except st.errors.StreamlitAPIException as e:
            if "can only be called once" in str(e):
                # Se já foi configurado, apenas marcar como configurado
                _PAGE_CONFIG_CALLED = True
            else:
                raise UIComponentError("page_config", str(e))
        except Exception as e:
            # Para qualquer outro erro relacionado a configuração de página
            if "set_page_config" in str(e) and "once" in str(e):
                _PAGE_CONFIG_CALLED = True
            else:
                raise UIComponentError("page_config", str(e))


class HeaderComponent(BaseUIComponent):
    """Componente para o cabeçalho da aplicação."""
    
    def __init__(self):
        super().__init__(UI_CONFIG)
    
    def render(self) -> None:
        """Renderiza o cabeçalho principal."""
        try:
            st.title(self.config.MAIN_TITLE)
        except Exception as e:
            raise UIComponentError("header", str(e))


class SidebarHeaderComponent(BaseUIComponent):
    """Componente para o cabeçalho da sidebar."""
    
    def __init__(self):
        super().__init__(UI_CONFIG)
    
    def render(self) -> None:
        """Renderiza o cabeçalho da sidebar."""
        try:
            st.sidebar.header(self.config.SIDEBAR_HEADER)
        except Exception as e:
            raise UIComponentError("sidebar_header", str(e))


class TabsComponent(BaseUIComponent):
    """Componente para criação de abas."""
    
    def __init__(self):
        super().__init__(UI_CONFIG)
        self._tabs = None
    
    def render(self) -> None:
        """Cria as abas do dashboard."""
        try:
            self._tabs = st.tabs(self.config.TAB_NAMES)
            return self._tabs
        except Exception as e:
            raise UIComponentError("tabs", str(e))
    
    def get_tabs(self):
        """Retorna as abas criadas."""
        if self._tabs is None:
            raise UIComponentError("tabs", "Abas não foram renderizadas ainda")
        return self._tabs


class FooterComponent(BaseUIComponent):
    """Componente para o rodapé da aplicação."""
    
    def __init__(self):
        super().__init__(FOOTER_CONFIG)
    
    def render(self) -> None:
        """Renderiza o rodapé completo."""
        try:
            st.markdown("---")
            
            # Layout do rodapé em 3 colunas
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                self._render_institution_column()
            
            with col2:
                self._render_project_column()
            
            with col3:
                self._render_team_column()
                
        except Exception as e:
            raise UIComponentError("footer", str(e))
    
    def _render_institution_column(self) -> None:
        """Renderiza coluna da instituição."""
        try:
            # Tentar carregar logo
            st.image(self.config.LOGO_PATH, width=100)
        except:
            st.write(f"**{self.config.UNIVERSITY_NAME}**")
        
        st.markdown(f"""
        <div style='color: #636363; margin-top: 10px;'>
            <p><b>{self.config.UNIVERSITY_NAME}</b></p>
            <p style='font-size: 13px;'>{self.config.CAMPUS_NAME}</p>
            <p style='font-size: 12px;'>{self.config.COURSE_NAME}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_project_column(self) -> None:
        """Renderiza coluna do projeto."""
        st.markdown(f"""
        <div style='text-align: center; color: #636363;'>
            <p style='font-size: 16px;'><b>{self.config.PROJECT_TITLE}</b></p>
                    <br>
            <p style='font-size: 14px;'>{self.config.PROJECT_TYPE}</p>
            <hr style='margin: 10px 0; border-color: #e0e0e0;'>
            <p style='font-size: 12px;'>{self.config.COPYRIGHT}</p>
            <p style='font-size: 11px; margin-top: 10px;'>{self.config.VERSION} - {self.config.LAST_UPDATE}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_team_column(self) -> None:
        """Renderiza coluna da equipe."""
        st.markdown(f"""
        <div style='text-align: right; color: #636363;'>
            <p style='font-size: 15px;'><b>Equipe</b></p>
            <p style='font-size: 14px; margin-bottom: 2px;'><b>Desenvolvedor:</b></p>
            <p style='font-size: 13px; margin-top: 0;'>{self.config.DEVELOPER_NAME} <br> {self.config.DEVELOPER_EMAIL}</p>
            <p style='font-size: 14px; margin-bottom: 2px; margin-top: 15px;'><b>Orientador:</b></p>
            <p style='font-size: 13px; margin-top: 0;'>{self.config.ADVISOR_NAME} <br> {self.config.ADVISOR_EMAIL}</p>
        </div>
        """, unsafe_allow_html=True)


class LoadingComponent(BaseUIComponent):
    """Componente para exibição de loading states."""
    
    def __init__(self, message: str = "Carregando..."):
        super().__init__(None)
        self.message = message
    
    def render(self) -> None:
        """Renderiza indicador de carregamento."""
        return st.spinner(self.message)
    
    def update_message(self, message: str) -> None:
        """Atualiza mensagem de carregamento."""
        self.message = message


class MessageComponent(BaseUIComponent):
    """Componente para exibição de mensagens ao usuário."""
    
    def __init__(self):
        super().__init__(None)
    
    def render(self) -> None:
        """Método render não aplicável para este componente."""
        pass
    
    def show_info(self, message: str) -> None:
        """Exibe mensagem informativa."""
        st.info(message)
    
    def show_success(self, message: str) -> None:
        """Exibe mensagem de sucesso."""
        st.success(message)
    
    def show_warning(self, message: str) -> None:
        """Exibe mensagem de aviso."""
        st.warning(message)
    
    def show_error(self, message: str) -> None:
        """Exibe mensagem de erro."""
        st.error(message)


class StatusDisplayComponent(BaseUIComponent):
    """Componente para exibição de status dos filtros."""
    
    def __init__(self):
        super().__init__(None)
        self.message_component = MessageComponent()
    
    def render(self) -> None:
        """Método render não aplicável para este componente."""
        pass
    
    def show_filter_status(self, selected_states: List[str], 
                          total_states: int, display_names: List[str]) -> None:
        """
        Exibe status atual dos filtros aplicados.
        
        Args:
            selected_states: Estados selecionados
            total_states: Total de estados disponíveis
            display_names: Nomes formatados para exibição
        """
        if not selected_states:
            return
        
        if len(selected_states) == total_states:
            message = "Analisando dados para todo o Brasil"
        else:
            message = f"Dados filtrados para: {', '.join(display_names)}"
        
        self.message_component.show_info(message)


class UIComponentFactory:
    """Factory para criação de componentes de UI."""
    
    @staticmethod
    def create_page_config() -> PageConfigComponent:
        """Cria componente de configuração de página."""
        return PageConfigComponent()
    
    @staticmethod
    def create_header() -> HeaderComponent:
        """Cria componente de cabeçalho."""
        return HeaderComponent()
    
    @staticmethod
    def create_sidebar_header() -> SidebarHeaderComponent:
        """Cria componente de cabeçalho da sidebar."""
        return SidebarHeaderComponent()
    
    @staticmethod
    def create_tabs() -> TabsComponent:
        """Cria componente de abas."""
        return TabsComponent()
    
    @staticmethod
    def create_footer() -> FooterComponent:
        """Cria componente de rodapé."""
        return FooterComponent()
    
    @staticmethod
    def create_loading(message: str = "Carregando...") -> LoadingComponent:
        """Cria componente de carregamento."""
        return LoadingComponent(message)
    
    @staticmethod
    def create_message() -> MessageComponent:
        """Cria componente de mensagens."""
        return MessageComponent()
    
    @staticmethod
    def create_status_display() -> StatusDisplayComponent:
        """Cria componente de exibição de status."""
        return StatusDisplayComponent()


# Instâncias globais dos componentes principais
ui_factory = UIComponentFactory()
