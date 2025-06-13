"""
Tratador de erros para o Dashboard.
Implementa tratamento centralizado e logging de erros.
"""

import streamlit as st
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps

from .core_types import ErrorHandler
from .config import ERROR_CONFIG
from .exceptions import DashboardError, TabRenderError, DataLoadError, UIComponentError


class DashboardErrorHandler(ErrorHandler):
    """Tratador de erros centralizado para o Dashboard."""
    
    def __init__(self):
        """Inicializa o tratador de erros."""
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, str] = {}
    
    def handle_tab_error(self, tab_name: str, error: Exception) -> None:
        """
        Trata erro específico de uma aba.
        
        Args:
            tab_name: Nome da aba onde ocorreu o erro
            error: Exceção que ocorreu
        """
        error_key = f"tab_{tab_name}"
        self._increment_error_count(error_key)
        
        # Determinar tipo de erro e mensagem apropriada
        if isinstance(error, TabRenderError):
            message = f"Erro na renderização da aba {tab_name}: {error}"
        elif isinstance(error, DataLoadError):
            message = f"Erro ao carregar dados para aba {tab_name}: {error}"
        else:
            message = f"Erro inesperado na aba {tab_name}: {str(error)}"
        
        # Exibir erro para o usuário
        st.error(message)
        
        # Log detalhado se em modo debug
        self._log_error(error_key, error, message)
        
        # Armazenar último erro
        self.last_errors[error_key] = message
    
    def handle_data_error(self, operation: str, error: Exception) -> None:
        """
        Trata erro relacionado aos dados.
        
        Args:
            operation: Operação que causou o erro
            error: Exceção que ocorreu
        """
        error_key = f"data_{operation}"
        self._increment_error_count(error_key)
        
        # Determinar mensagem baseada no tipo de erro
        if isinstance(error, DataLoadError):
            message = f"Erro no carregamento de dados ({operation}): {error}"
        else:
            message = f"Erro na operação de dados '{operation}': {str(error)}"
        
        # Exibir erro para o usuário
        st.error(message)
        
        # Log detalhado
        self._log_error(error_key, error, message)
        
        # Armazenar último erro
        self.last_errors[error_key] = message
    
    def handle_ui_error(self, component: str, error: Exception) -> None:
        """
        Trata erro de componente de UI.
        
        Args:
            component: Nome do componente
            error: Exceção que ocorreu
        """
        error_key = f"ui_{component}"
        self._increment_error_count(error_key)
        
        if isinstance(error, UIComponentError):
            message = f"Erro no componente de interface '{component}': {error}"
        else:
            message = f"Erro inesperado no componente '{component}': {str(error)}"
        
        # Para erros de UI, usar warning ao invés de error
        st.warning(message)
        
        # Log detalhado
        self._log_error(error_key, error, message)
        
        # Armazenar último erro
        self.last_errors[error_key] = message
    
    def handle_general_error(self, context: str, error: Exception) -> None:
        """
        Trata erro geral do sistema.
        
        Args:
            context: Contexto onde ocorreu o erro
            error: Exceção que ocorreu
        """
        error_key = f"general_{context}"
        self._increment_error_count(error_key)
        
        message = f"Erro no sistema ({context}): {str(error)}"
        
        # Exibir erro crítico
        st.error(f"🚨 {message}")
        st.error("Por favor, recarregue a página ou entre em contato com o suporte.")
        
        # Log detalhado
        self._log_error(error_key, error, message)
        
        # Armazenar último erro
        self.last_errors[error_key] = message
    
    def _increment_error_count(self, error_key: str) -> None:
        """Incrementa contador de erros para uma chave específica."""
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def _log_error(self, error_key: str, error: Exception, message: str) -> None:
        """
        Faz log detalhado do erro.
        
        Args:
            error_key: Chave do erro
            error: Exceção original
            message: Mensagem formatada
        """
        try:
            # Tentar usar o logger do módulo de dados se disponível
            from data.logger import logger
            logger.error(f"[{error_key}] {message}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        except ImportError:
            # Fallback para print se logger não estiver disponível
            print(f"ERROR [{error_key}]: {message}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo dos erros ocorridos.
        
        Returns:
            Dicionário com estatísticas de erro
        """
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': len(self.error_counts),
            'error_counts': self.error_counts.copy(),
            'last_errors': self.last_errors.copy()
        }
    
    def reset_error_tracking(self) -> None:
        """Reseta o tracking de erros."""
        self.error_counts.clear()
        self.last_errors.clear()


def handle_exceptions(error_handler: DashboardErrorHandler, 
                     context: str = "general"):
    """
    Decorator para tratamento automático de exceções.
    
    Args:
        error_handler: Instância do tratador de erros
        context: Contexto da operação
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TabRenderError as e:
                error_handler.handle_tab_error(e.tab_name, e)
                return None
            except DataLoadError as e:
                error_handler.handle_data_error(e.tab_type, e)
                return None
            except UIComponentError as e:
                error_handler.handle_ui_error(e.component, e)
                return None
            except DashboardError as e:
                error_handler.handle_general_error(context, e)
                return None
            except Exception as e:
                error_handler.handle_general_error(context, e)
                return None
        
        return wrapper
    return decorator


def safe_execute(func: Callable, error_handler: DashboardErrorHandler, 
                context: str = "operation", *args, **kwargs) -> Any:
    """
    Executa uma função de forma segura com tratamento de erro.
    
    Args:
        func: Função a ser executada
        error_handler: Tratador de erros
        context: Contexto da operação
        *args, **kwargs: Argumentos para a função
    
    Returns:
        Resultado da função ou None se erro
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_general_error(context, e)
        return None


class ErrorRecoveryManager:
    """Gerenciador para recuperação de erros."""
    
    def __init__(self, error_handler: DashboardErrorHandler):
        """
        Inicializa o gerenciador de recuperação.
        
        Args:
            error_handler: Tratador de erros
        """
        self.error_handler = error_handler
    
    def attempt_data_recovery(self, tab_type: str) -> Optional[Any]:
        """
        Tenta recuperar dados em caso de erro de carregamento.
        
        Args:
            tab_type: Tipo da aba para recuperação
            
        Returns:
            Dados recuperados ou None
        """
        try:
            # Tentar carregar dados básicos
            from data import load_data_for_tab
            
            st.warning(f"Tentando recarregar dados para {tab_type}...")
            data = load_data_for_tab(tab_type)
            
            if not data.empty:
                st.success("Dados recarregados com sucesso!")
                return data
            else:
                st.error("Não foi possível recuperar os dados.")
                return None
                
        except Exception as e:
            self.error_handler.handle_data_error("recovery", e)
            return None
    
    def suggest_user_actions(self, error_type: str) -> None:
        """
        Sugere ações para o usuário baseadas no tipo de erro.
        
        Args:
            error_type: Tipo do erro ocorrido
        """
        suggestions = {
            "data_load": [
                "Verifique sua conexão com a internet",
                "Tente recarregar a página",
                "Verifique se os arquivos de dados estão disponíveis"
            ],
            "tab_render": [
                "Tente selecionar uma aba diferente",
                "Verifique os filtros aplicados",
                "Recarregue a página se o problema persistir"
            ],
            "ui_component": [
                "Recarregue a página",
                "Verifique se seu navegador está atualizado",
                "Tente limpar o cache do navegador"
            ],
            "memory": [
                "Feche outras abas do navegador",
                "Selecione menos estados para análise",
                "Recarregue a aplicação"
            ]
        }
        
        if error_type in suggestions:
            st.info("💡 Sugestões para resolver o problema:")
            for suggestion in suggestions[error_type]:
                st.write(f"• {suggestion}")


# Instância global do tratador de erros
error_handler = DashboardErrorHandler()
recovery_manager = ErrorRecoveryManager(error_handler)
