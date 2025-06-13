"""
Renderizadores especializados para as abas do Dashboard.
Implementa padrão Strategy para renderização de diferentes tipos de aba.
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Callable

from .core_types import TabRenderer, DataFrameType, StateList, BaseTabRenderer
from .config import ERROR_CONFIG, DATA_CONFIG
from .exceptions import TabRenderError
from .data_manager import data_manager


class GeralTabRenderer(BaseTabRenderer):
    """Renderizador especializado para a aba Geral."""
    
    def __init__(self):
        super().__init__("Geral", DATA_CONFIG)
    
    def render(self, data: DataFrameType, states: StateList, 
               display_names: List[str], **kwargs) -> None:
        """
        Renderiza a aba Geral.
        
        Args:
            data: DataFrame com dados filtrados
            states: Lista de estados selecionados
            display_names: Nomes formatados para exibição
            **kwargs: Argumentos adicionais (colunas_notas, competencia_mapping)
        """
        try:
            if not self.validate_data(data):
                st.warning(ERROR_CONFIG.WARNING_NO_DATA)
                return
            
            # Importar e executar renderizador específico
            from tabs.geral import render_geral
            
            render_geral(
                data,
                states,
                display_names,
                kwargs.get('colunas_notas', []),
                kwargs.get('competencia_mapping', {})
            )
            
        except Exception as e:
            raise TabRenderError(self.name, str(e))
    
    def validate_data(self, data: DataFrameType) -> bool:
        """Validação específica para dados da aba Geral."""
        if not super().validate_data(data):
            return False
        
        # Verificar colunas essenciais para aba Geral
        required_columns = ['SG_UF_PROVA']  # Adicionar outras conforme necessário
        missing_cols = [col for col in required_columns if col not in data.columns]
        
        if missing_cols:
            st.error(f"Colunas obrigatórias ausentes para aba Geral: {missing_cols}")
            return False
        
        return True


class AspectosTabRenderer(BaseTabRenderer):
    """Renderizador especializado para a aba Aspectos Sociais."""
    
    def __init__(self):
        super().__init__("Aspectos Sociais", DATA_CONFIG)
    
    def render(self, data: DataFrameType, states: StateList, 
               display_names: List[str], **kwargs) -> None:
        """
        Renderiza a aba Aspectos Sociais.
        
        Args:
            data: DataFrame com dados filtrados
            states: Lista de estados selecionados
            display_names: Nomes formatados para exibição
            **kwargs: Argumentos adicionais (variaveis_sociais)
        """
        try:
            if not self.validate_data(data):
                st.warning(ERROR_CONFIG.WARNING_NO_DATA)
                return
            
            # Importar e executar renderizador específico
            from tabs.aspectos_sociais import render_aspectos_sociais
            
            render_aspectos_sociais(
                data,
                states,
                display_names,
                kwargs.get('variaveis_sociais', {})
            )
            
        except Exception as e:
            raise TabRenderError(self.name, str(e))
    
    def validate_data(self, data: DataFrameType) -> bool:
        """Validação específica para dados da aba Aspectos Sociais."""
        if not super().validate_data(data):
            return False
        
        # Verificações específicas se necessário
        return True


class DesempenhoTabRenderer(BaseTabRenderer):
    """Renderizador especializado para a aba Desempenho."""
    
    def __init__(self):
        super().__init__("Desempenho", DATA_CONFIG)
    
    def render(self, data: DataFrameType, states: StateList, 
               display_names: List[str], **kwargs) -> None:
        """
        Renderiza a aba Desempenho.
        
        Args:
            data: DataFrame com dados filtrados
            states: Lista de estados selecionados
            display_names: Nomes formatados para exibição
            **kwargs: Argumentos adicionais diversos
        """
        try:
            if not self.validate_data(data):
                st.warning(ERROR_CONFIG.WARNING_NO_DATA)
                return
            
            # Importar e executar renderizador específico
            from tabs.desempenho import render_desempenho
            
            # Para aba de desempenho, pode precisar de dados completos também
            microdados_completo = kwargs.get('microdados_completo')
            if microdados_completo is None:
                # Carregar se não fornecido
                microdados_completo = data_manager.load_tab_data("desempenho")
            
            render_desempenho(
                microdados_completo,  # Dataset completo
                data,  # Dataset filtrado
                states,
                display_names,
                kwargs.get('colunas_notas', []),
                kwargs.get('competencia_mapping', {}),
                kwargs.get('race_mapping', {}),
                kwargs.get('variaveis_categoricas', {}),
                kwargs.get('desempenho_mapping', {})
            )
            
        except Exception as e:
            raise TabRenderError(self.name, str(e))
    
    def validate_data(self, data: DataFrameType) -> bool:
        """Validação específica para dados da aba Desempenho."""
        if not super().validate_data(data):
            return False
        
        # Verificações específicas se necessário
        return True


class TabRenderManager:
    """Gerenciador principal para renderização de abas."""
    
    def __init__(self):
        """Inicializa o gerenciador com renderizadores disponíveis."""
        self._renderers: Dict[str, TabRenderer] = {
            "Geral": GeralTabRenderer(),
            "Aspectos Sociais": AspectosTabRenderer(),
            "Desempenho": DesempenhoTabRenderer()
        }
    
    def render_tab(self, tab_name: str, data: DataFrameType, states: StateList,
                   display_names: List[str], **kwargs) -> None:
        """
        Renderiza uma aba específica.
        
        Args:
            tab_name: Nome da aba a ser renderizada
            data: DataFrame com dados filtrados
            states: Lista de estados selecionados
            display_names: Nomes formatados para exibição
            **kwargs: Argumentos adicionais específicos da aba
        """
        try:
            if tab_name not in self._renderers:
                raise TabRenderError(tab_name, f"Renderizador não encontrado para aba '{tab_name}'")
            
            renderer = self._renderers[tab_name]
            renderer.render(data, states, display_names, **kwargs)
            
        except TabRenderError:
            raise
        except Exception as e:
            raise TabRenderError(tab_name, f"Erro inesperado: {str(e)}")
    
    def get_available_tabs(self) -> List[str]:
        """Retorna lista de abas disponíveis."""
        return list(self._renderers.keys())
    
    def add_renderer(self, tab_name: str, renderer: TabRenderer) -> None:
        """
        Adiciona um novo renderizador.
        
        Args:
            tab_name: Nome da aba
            renderer: Instância do renderizador
        """
        self._renderers[tab_name] = renderer
    
    def remove_renderer(self, tab_name: str) -> None:
        """
        Remove um renderizador.
        
        Args:
            tab_name: Nome da aba a ser removida
        """
        if tab_name in self._renderers:
            del self._renderers[tab_name]


class TabExecutor:
    """Executor que gerencia o carregamento de dados e renderização de abas."""
    
    def __init__(self, render_manager: TabRenderManager):
        """
        Inicializa o executor.
        
        Args:
            render_manager: Gerenciador de renderização
        """
        self.render_manager = render_manager
        self.data_processor = data_manager
    
    def execute_tab(self, tab_name: str, states: StateList, 
                   display_names: List[str], mappings: Dict[str, Any]) -> None:
        """
        Executa uma aba completa: carrega dados, filtra e renderiza.
        
        Args:
            tab_name: Nome da aba
            states: Estados selecionados
            display_names: Nomes para exibição
            mappings: Dicionário com mapeamentos necessários
        """
        try:
            # Verificar se há estados selecionados
            if not states:
                st.warning(ERROR_CONFIG.WARNING_SELECT_STATE)
                return
            
            # Obter tipo da aba para carregamento
            tab_type = DATA_CONFIG.TAB_TYPES.get(tab_name)
            if not tab_type:
                raise TabRenderError(tab_name, f"Tipo de aba desconhecido: {tab_name}")
            
            # Carregar e filtrar dados
            with st.spinner(f"Carregando dados para {tab_name}..."):
                raw_data = self.data_processor.load_tab_data(tab_type)
                filtered_data = self.data_processor.filter_by_states(raw_data, states)
                
                # Liberar dados originais se diferentes
                if id(raw_data) != id(filtered_data):
                    self.data_processor.release_memory(raw_data)
            
            # Preparar argumentos específicos da aba
            render_kwargs = self._prepare_render_kwargs(tab_name, mappings, raw_data)
            
            # Renderizar aba
            self.render_manager.render_tab(
                tab_name, filtered_data, states, display_names, **render_kwargs
            )
            
            # Liberar memória após uso
            self.data_processor.release_memory(filtered_data)
            
        except TabRenderError:
            st.error(f"Erro ao executar aba {tab_name}")
            raise
        except Exception as e:
            st.error(f"Erro inesperado na aba {tab_name}: {str(e)}")
            raise TabRenderError(tab_name, str(e))
    
    def _prepare_render_kwargs(self, tab_name: str, mappings: Dict[str, Any], 
                              raw_data: Optional[DataFrameType] = None) -> Dict[str, Any]:
        """
        Prepara argumentos específicos para renderização de cada aba.
        
        Args:
            tab_name: Nome da aba
            mappings: Dicionário com mapeamentos
            raw_data: Dados brutos (para aba Desempenho)
            
        Returns:
            Dicionário com argumentos para renderização
        """
        kwargs = {}
        
        if tab_name == "Geral":
            kwargs.update({
                'colunas_notas': mappings.get('colunas_notas', []),
                'competencia_mapping': mappings.get('competencia_mapping', {})
            })
        
        elif tab_name == "Aspectos Sociais":
            kwargs.update({
                'variaveis_sociais': mappings.get('variaveis_sociais', {})
            })
        
        elif tab_name == "Desempenho":
            kwargs.update({
                'microdados_completo': raw_data,
                'colunas_notas': mappings.get('colunas_notas', []),
                'competencia_mapping': mappings.get('competencia_mapping', {}),
                'race_mapping': mappings.get('race_mapping', {}),
                'variaveis_categoricas': mappings.get('variaveis_categoricas', {}),
                'desempenho_mapping': mappings.get('desempenho_mapping', {})
            })
        
        return kwargs


# Instância global do gerenciador
tab_render_manager = TabRenderManager()
tab_executor = TabExecutor(tab_render_manager)
