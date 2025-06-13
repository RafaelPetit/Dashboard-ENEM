"""
Gerenciador de filtros de estado e região.
Implementa lógica de seleção de estados e regiões com interface limpa.
"""

import streamlit as st
from typing import List, Dict, Tuple, Optional

from .core_types import StateFilter, StateList
from .config import FILTER_CONFIG
from .exceptions import FilterError, StateSelectionError


class StateFilterManager(StateFilter):
    """Gerenciador especializado para filtros de estado e região."""
    
    def __init__(self, regions_mapping: Dict[str, List[str]], available_states: List[str]):
        """
        Inicializa o gerenciador de filtros.
        
        Args:
            regions_mapping: Mapeamento de regiões para estados
            available_states: Lista de estados disponíveis nos dados
        """
        self.regions_mapping = regions_mapping
        self.available_states = sorted(available_states)
        self.all_regions = sorted(regions_mapping.keys())
        
        # Estado interno
        self._selected_states: List[str] = []
        self._selected_regions: List[str] = []
        self._brasil_selected: bool = True
    
    def render_filters(self) -> None:
        """Renderiza os componentes de filtro na sidebar."""
        try:
            self._render_brasil_checkbox()
            
            if self._brasil_selected:
                self._render_disabled_selectors()
                self._select_all_states()
            else:
                self._render_region_selector()
                self._render_state_selector()
                self._validate_selection()
            
            self._render_selection_summary()
            
        except Exception as e:
            raise FilterError("state_filter_render", str(e))
    
    def get_selected_states(self) -> StateList:
        """Retorna lista de estados selecionados."""
        return self._selected_states.copy()
    
    def get_display_names(self) -> List[str]:
        """Retorna nomes formatados para exibição."""
        try:
            from data import agrupar_estados_em_regioes
            return agrupar_estados_em_regioes(self._selected_states, self.regions_mapping)
        except Exception:
            # Fallback se a função não estiver disponível
            return self._selected_states.copy()
    
    def is_brasil_selected(self) -> bool:
        """Verifica se todo o Brasil está selecionado."""
        return self._brasil_selected
    
    def _render_brasil_checkbox(self) -> None:
        """Renderiza checkbox para seleção do Brasil inteiro."""
        self._brasil_selected = st.sidebar.checkbox(
            FILTER_CONFIG.BRASIL_CHECKBOX_LABEL, 
            value=True,
            key="brasil_checkbox"
        )
    
    def _render_disabled_selectors(self) -> None:
        """Renderiza seletores desabilitados quando Brasil está selecionado."""
        st.sidebar.multiselect(
            "Regiões selecionadas:",
            options=self.all_regions,
            default=self.all_regions,
            disabled=True,
            help="Selecione regiões específicas quando a opção Brasil estiver desmarcada",
            key="regions_disabled"
        )
        
        st.sidebar.multiselect(
            "Estados selecionados:",
            options=self.available_states,
            default=self.available_states,
            disabled=True,
            help=FILTER_CONFIG.DISABLED_HELP,
            key="states_disabled"
        )
    
    def _render_region_selector(self) -> None:
        """Renderiza seletor de regiões."""
        st.sidebar.markdown("#### Filtrar por região")
        
        self._selected_regions = st.sidebar.multiselect(
            FILTER_CONFIG.REGION_SELECT_LABEL,
            options=self.all_regions,
            default=[],
            help=FILTER_CONFIG.REGION_HELP,
            key="regions_selector"
        )
    
    def _render_state_selector(self) -> None:
        """Renderiza seletor de estados."""
        # Obter estados das regiões selecionadas
        states_from_regions = self._get_states_from_regions(self._selected_regions)
        
        st.sidebar.markdown("#### Filtrar por estado")
        st.sidebar.markdown(
            "<p style='font-size:12px; color:#666;'>Estados das regiões selecionadas já estão incluídos.</p>",
            unsafe_allow_html=True
        )
        
        # Estados disponíveis para seleção manual (excluindo os já selecionados por região)
        available_for_manual = [
            state for state in self.available_states 
            if state not in states_from_regions
        ]
        
        additional_states = st.sidebar.multiselect(
            FILTER_CONFIG.STATE_SELECT_LABEL,
            options=available_for_manual,
            default=[],
            help=FILTER_CONFIG.STATE_HELP,
            key="additional_states"
        )
        
        # Combinar estados das regiões com estados adicionais
        self._selected_states = sorted(list(set(states_from_regions + additional_states)))
    
    def _select_all_states(self) -> None:
        """Seleciona todos os estados quando Brasil está marcado."""
        self._selected_states = self.available_states.copy()
        self._selected_regions = self.all_regions.copy()
    
    def _get_states_from_regions(self, selected_regions: List[str]) -> List[str]:
        """Converte regiões selecionadas em lista de estados."""
        states = []
        for region in selected_regions:
            if region in self.regions_mapping:
                states.extend(self.regions_mapping[region])
        return sorted(list(set(states)))
    
    def _validate_selection(self) -> None:
        """Valida se pelo menos um estado foi selecionado."""
        if not self._selected_states:
            st.sidebar.warning(FILTER_CONFIG.WARNING_NO_SELECTION)
    
    def _render_selection_summary(self) -> None:
        """Renderiza resumo da seleção atual."""
        if not self._selected_states:
            return
        
        if len(self._selected_states) == len(self.available_states):
            st.sidebar.success(FILTER_CONFIG.SUCCESS_BRASIL)
        else:
            if self._selected_regions:
                st.sidebar.success(
                    FILTER_CONFIG.SUCCESS_REGIONS.format(', '.join(self._selected_regions))
                )
            
            # Verificar se há estados adicionais selecionados manualmente
            states_from_regions = self._get_states_from_regions(self._selected_regions)
            additional_states = [
                state for state in self._selected_states 
                if state not in states_from_regions
            ]
            
            if additional_states:
                st.sidebar.success(
                    FILTER_CONFIG.SUCCESS_ADDITIONAL.format(', '.join(additional_states))
                )
            
            st.sidebar.info(
                FILTER_CONFIG.INFO_TOTAL.format(len(self._selected_states))
            )


class FilterValidator:
    """Validador para filtros de estado."""
    
    @staticmethod
    def validate_regions_mapping(regions_mapping: Dict[str, List[str]]) -> bool:
        """
        Valida o mapeamento de regiões.
        
        Args:
            regions_mapping: Dicionário de regiões para validar
            
        Returns:
            True se válido
            
        Raises:
            StateSelectionError: Se o mapeamento for inválido
        """
        if not regions_mapping:
            raise StateSelectionError("Mapeamento de regiões não pode estar vazio")
        
        for region, states in regions_mapping.items():
            if not isinstance(states, list) or not states:
                raise StateSelectionError(f"Região '{region}' deve ter lista não vazia de estados")
        
        return True
    
    @staticmethod
    def validate_states_list(states: List[str]) -> bool:
        """
        Valida lista de estados.
        
        Args:
            states: Lista de estados para validar
            
        Returns:
            True se válida
            
        Raises:
            StateSelectionError: Se a lista for inválida
        """
        if not states:
            raise StateSelectionError("Lista de estados não pode estar vazia")
        
        if not all(isinstance(state, str) and len(state) == 2 for state in states):
            raise StateSelectionError("Estados devem ser strings de 2 caracteres")
        
        return True


# Factory para criação de filtros
class FilterFactory:
    """Factory para criação de gerenciadores de filtro."""
    
    @staticmethod
    def create_state_filter(regions_mapping: Dict[str, List[str]], 
                           available_states: List[str]) -> StateFilterManager:
        """
        Cria um gerenciador de filtros de estado.
        
        Args:
            regions_mapping: Mapeamento de regiões
            available_states: Estados disponíveis
            
        Returns:
            Instância do gerenciador de filtros
        """
        # Validar entradas
        FilterValidator.validate_regions_mapping(regions_mapping)
        FilterValidator.validate_states_list(available_states)
        
        return StateFilterManager(regions_mapping, available_states)
