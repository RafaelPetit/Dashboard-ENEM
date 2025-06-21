"""
Utilitários para gerenciamento de páginas navegáveis.

Este módulo fornece funcionalidades para:
- Limpeza automática de cache ao trocar páginas
- Gerenciamento de estado entre páginas
- Otimização de memória
- Monitoramento de navegação
"""

import streamlit as st
import gc
from typing import Optional, Dict, Any, List
from utils.helpers.cache_utils import clear_all_cache, release_memory, deep_cleanup, check_memory_and_cleanup, clear_page_specific_cache

class PageManager:
    """Gerenciador de páginas para otimização de memória e cache."""
    
    def __init__(self):
        self.current_page: Optional[str] = None
        self.previous_page: Optional[str] = None
        self.page_cache: Dict[str, Any] = {}
        
    def register_page_change(self, page_name: str) -> None:
        """
        Registra mudança de página e executa limpeza se necessário.
        
        Args:
            page_name: Nome da página atual
        """
        if 'current_page' not in st.session_state:
            st.session_state.current_page = page_name
            st.session_state.previous_page = None
        else:
            st.session_state.previous_page = st.session_state.current_page
            st.session_state.current_page = page_name
          # Executar limpeza se mudou de página
        if (st.session_state.previous_page and 
            st.session_state.previous_page != page_name):
            self.cleanup_previous_page()
    
    def cleanup_previous_page(self) -> None:
        """Executa limpeza de memória e cache da página anterior."""
        try:
            previous_page = st.session_state.previous_page
            
            if previous_page:
                # 1. Limpeza específica da página anterior
                clear_page_specific_cache(previous_page)
                
                # 2. Verificar uso de memória e executar limpeza se necessário
                cleanup_executed = check_memory_and_cleanup()
                
                # 3. Se não houve limpeza automática, fazer limpeza padrão
                if not cleanup_executed:
                    clear_all_cache()
                    release_memory()
                    gc.collect()
                
                print(f"[PAGE_MANAGER] Limpeza executada ao sair de: {previous_page}")
            else:
                # Limpeza básica se não há página anterior
                release_memory()
                gc.collect()
                
        except Exception as e:
            print(f"[PAGE_MANAGER] Erro na limpeza: {str(e)}")
            # Em caso de erro, tentar limpeza básica
            try:
                release_memory()
                gc.collect()
            except:
                pass
                gc.collect()
            except:
                pass
    
    def get_current_page(self) -> Optional[str]:
        """Retorna o nome da página atual."""
        return getattr(st.session_state, 'current_page', None)
    
    def get_previous_page(self) -> Optional[str]:
        """Retorna o nome da página anterior."""
        return getattr(st.session_state, 'previous_page', None)
    
    def is_page_change(self, page_name: str) -> bool:
        """
        Verifica se houve mudança de página.
        
        Args:
            page_name: Nome da página atual
            
        Returns:
            True se houve mudança de página
        """
        current = self.get_current_page()
        return current is not None and current != page_name


# Instância global do gerenciador
page_manager = PageManager()


def setup_page_config(
    page_title: str,
    page_icon: str = "📊",
    layout: str = "wide",
    initial_sidebar_state: str = "expanded"
) -> None:
    """
    Configura a página com parâmetros padrão otimizados.
    
    Args:
        page_title: Título da página
        page_icon: Ícone da página
        layout: Layout da página
        initial_sidebar_state: Estado inicial da barra lateral
    """
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Dashboard de Análise do ENEM 2023"
        }
    )


def register_page_navigation(page_name: str) -> None:
    """
    Registra navegação de página e executa limpezas necessárias.
    
    Args:
        page_name: Nome da página atual
    """
    page_manager.register_page_change(page_name)


def cleanup_on_page_change(page_name: str) -> None:
    """
    Executa limpeza automática ao detectar mudança de página.
    
    Args:
        page_name: Nome da página atual
    """
    if page_manager.is_page_change(page_name):
        page_manager.cleanup_previous_page()


def get_navigation_info() -> Dict[str, Optional[str]]:
    """
    Retorna informações sobre navegação atual.
    
    Returns:
        Dicionário com informações de navegação
    """
    return {
        'current_page': page_manager.get_current_page(),
        'previous_page': page_manager.get_previous_page()
    }


def render_page_debug_info() -> None:
    """Renderiza informações de debug sobre navegação (apenas para desenvolvimento)."""
    if st.secrets.get("DEBUG_MODE", False):
        info = get_navigation_info()
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔧 Debug Info")
        st.sidebar.json(info)


class PageDecorator:
    """Decorator para automatizar gerenciamento de páginas."""
    
    def __init__(self, page_name: str):
        self.page_name = page_name
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Registrar navegação
            register_page_navigation(self.page_name)
            
            try:
                # Executar função da página
                return func(*args, **kwargs)
            finally:
                # Cleanup adicional se necessário
                pass
                
        return wrapper


def page_wrapper(page_name: str):
    """
    Wrapper funcional para páginas.
    
    Args:
        page_name: Nome da página
        
    Usage:
        @page_wrapper("Análise Geral")
        def main():
            # código da página
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            register_page_navigation(page_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def safe_page_execution(page_name: str, page_function, *args, **kwargs):
    """
    Executa função de página com tratamento seguro de erros e limpeza automática.
    
    Esta função garante que:
    1. A navegação de página seja registrada
    2. A limpeza de memória seja executada ao trocar de página
    3. Erros sejam tratados graciosamente
    4. Recursos sejam liberados mesmo em caso de erro
    
    Args:
        page_name: Nome da página
        page_function: Função da página a ser executada
        *args, **kwargs: Argumentos para a função
        
    Returns:
        Resultado da função da página
    """
    try:
        # Registrar navegação e executar limpeza se necessário
        register_page_navigation(page_name)
        
        # Executar função da página
        return page_function(*args, **kwargs)
        
    except Exception as e:
        st.error(f"Erro na página {page_name}: {str(e)}")
        st.warning("Tente recarregar a página ou verificar os filtros aplicados.")
        
        # Log do erro para debug
        print(f"[SAFE_PAGE_EXECUTION] Erro em {page_name}: {str(e)}")
        
    finally:
        # Cleanup básico em caso de erro ou execução normal
        try:
            release_memory()
        except Exception as cleanup_error:
            print(f"[SAFE_PAGE_EXECUTION] Erro na limpeza: {str(cleanup_error)}")
    
    Args:
        page_name: Nome da página
        page_function: Função da página a ser executada
        *args, **kwargs: Argumentos para a função
    """
    try:
        register_page_navigation(page_name)
        return page_function(*args, **kwargs)
    except Exception as e:
        st.error(f"Erro na página {page_name}: {str(e)}")
        st.warning("Tente recarregar a página ou verificar os filtros aplicados.")
    finally:
        # Cleanup básico em caso de erro
        release_memory()


# Configurações específicas para diferentes tipos de página
PAGE_CONFIGS = {
    "dashboard": {
        "cache_ttl": 3600,  # 1 hora
        "max_cache_entries": 10,
        "cleanup_on_exit": True
    },
    "analysis": {
        "cache_ttl": 1800,  # 30 minutos
        "max_cache_entries": 5,
        "cleanup_on_exit": True
    },
    "visualization": {
        "cache_ttl": 900,   # 15 minutos
        "max_cache_entries": 3,
        "cleanup_on_exit": True
    }
}


def get_page_config(page_type: str = "dashboard") -> Dict[str, Any]:
    """
    Retorna configuração específica para tipo de página.
    
    Args:
        page_type: Tipo da página (dashboard, analysis, visualization)
        
    Returns:
        Configuração da página
    """
    return PAGE_CONFIGS.get(page_type, PAGE_CONFIGS["dashboard"])
