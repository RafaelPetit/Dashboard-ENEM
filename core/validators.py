"""
Sistema de validação de dados para o Dashboard.
Implementa validações robustas para entrada de dados e estado do sistema.
"""

from typing import List, Dict, Any, Optional, Union, Set
import pandas as pd
import streamlit as st

from .core_types import DataFrameType, StateList
from .config import SECURITY_CONFIG, DATA_CONFIG
from .exceptions import ValidationError


class DataValidator:
    """Validador principal para dados do Dashboard."""
    
    @staticmethod
    def validate_dataframe(df: DataFrameType, context: str = "geral") -> bool:
        """
        Valida um DataFrame para uso no Dashboard.
        
        Args:
            df: DataFrame a ser validado
            context: Contexto da validação ('geral', 'aspectos_sociais', 'desempenho')
            
        Returns:
            True se válido
            
        Raises:
            ValidationError: Se validação falhar
        """
        if not SECURITY_CONFIG.VALIDATE_INPUTS:
            return True
        
        # Verificar se é DataFrame
        if not isinstance(df, pd.DataFrame):
            raise ValidationError(f"Esperado DataFrame, recebido {type(df)}")
        
        # Verificar se não está vazio
        if df.empty:
            raise ValidationError("DataFrame está vazio")
        
        # Verificar colunas obrigatórias por contexto
        required_columns = DataValidator._get_required_columns(context)
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValidationError(f"Colunas obrigatórias ausentes: {missing_columns}")
        
        # Verificar tipos de dados
        DataValidator._validate_column_types(df, context)
        
        # Verificar valores suspeitos
        DataValidator._validate_data_quality(df, context)
        
        return True
    
    @staticmethod
    def validate_states(states: StateList) -> bool:
        """
        Valida lista de estados selecionados.
        
        Args:
            states: Lista de estados
            
        Returns:
            True se válido
            
        Raises:
            ValidationError: Se validação falhar
        """
        if not SECURITY_CONFIG.VALIDATE_INPUTS:
            return True
        
        # Verificar tipo
        if not isinstance(states, list):
            raise ValidationError(f"Estados deve ser lista, recebido {type(states)}")
        
        # Verificar se não está vazio
        if not states:
            raise ValidationError("Lista de estados não pode estar vazia")
        
        # Verificar limite máximo
        if len(states) > SECURITY_CONFIG.MAX_STATES_SELECTION:
            raise ValidationError(f"Máximo de {SECURITY_CONFIG.MAX_STATES_SELECTION} estados permitido")
        
        # Verificar códigos válidos
        valid_states = DataValidator._get_valid_state_codes()
        invalid_states = [state for state in states if state not in valid_states]
        
        if invalid_states:
            raise ValidationError(f"Códigos de estado inválidos: {invalid_states}")
        
        return True
    
    @staticmethod
    def validate_mappings(mappings: Dict[str, Any], context: str = "geral") -> bool:
        """
        Valida dicionário de mapeamentos.
        
        Args:
            mappings: Dicionário de mapeamentos
            context: Contexto da validação
            
        Returns:
            True se válido
            
        Raises:
            ValidationError: Se validação falhar
        """
        if not SECURITY_CONFIG.VALIDATE_INPUTS:
            return True
        
        # Verificar tipo
        if not isinstance(mappings, dict):
            raise ValidationError(f"Mapeamentos deve ser dict, recebido {type(mappings)}")
        
        # Verificar mapeamentos obrigatórios por contexto
        required_mappings = DataValidator._get_required_mappings(context)
        missing_mappings = [key for key in required_mappings if key not in mappings]
        
        if missing_mappings:
            raise ValidationError(f"Mapeamentos obrigatórios ausentes: {missing_mappings}")
        
        return True
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitiza texto de entrada.
        
        Args:
            text: Texto a ser sanitizado
            
        Returns:
            Texto sanitizado
        """
        if not SECURITY_CONFIG.SANITIZE_TEXT:
            return text
        
        if not isinstance(text, str):
            return str(text)
        
        # Remover caracteres potencialmente perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        sanitized = text
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Limitar tamanho
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def _get_required_columns(context: str) -> List[str]:
        """Retorna colunas obrigatórias por contexto."""
        base_columns = ['SG_UF_PROVA']
        
        context_columns = {
            'geral': base_columns + ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'],
            'aspectos_sociais': base_columns + ['TP_COR_RACA', 'TP_SEXO'],
            'desempenho': base_columns + ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        }
        
        return context_columns.get(context, base_columns)
    
    @staticmethod
    def _get_required_mappings(context: str) -> List[str]:
        """Retorna mapeamentos obrigatórios por contexto."""
        base_mappings = ['regioes_mapping']
        
        context_mappings = {
            'geral': base_mappings + ['competencia_mapping', 'colunas_notas'],
            'aspectos_sociais': base_mappings + ['variaveis_sociais'],
            'desempenho': base_mappings + ['competencia_mapping', 'race_mapping', 'variaveis_categoricas']
        }
        
        return context_mappings.get(context, base_mappings)
    
    @staticmethod
    def _get_valid_state_codes() -> Set[str]:
        """Retorna códigos de estado válidos."""
        return {
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        }
    
    @staticmethod
    def _validate_column_types(df: DataFrameType, context: str) -> None:
        """Valida tipos de dados das colunas."""
        # Validações específicas por contexto
        numeric_columns = {
            'geral': ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'],
            'aspectos_sociais': [],
            'desempenho': ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        }
        
        required_numeric = numeric_columns.get(context, [])
        
        for col in required_numeric:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                # Tentar converter
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    raise ValidationError(f"Coluna {col} deve ser numérica")
    
    @staticmethod
    def _validate_data_quality(df: DataFrameType, context: str) -> None:
        """Valida qualidade dos dados."""
        # Verificar se há pelo menos algumas linhas válidas
        min_rows = 100
        if len(df) < min_rows:
            st.warning(f"Dataset pequeno: apenas {len(df)} registros")
        
        # Verificar completude dos dados
        missing_threshold = 0.9  # 90% de dados ausentes é suspeito
        
        for col in df.columns:
            missing_ratio = df[col].isnull().sum() / len(df)
            if missing_ratio > missing_threshold:
                st.warning(f"Coluna {col} tem {missing_ratio:.1%} de dados ausentes")


class StateValidator:
    """Validador específico para estados e regiões."""
    
    REGION_MAPPING = {
        "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
        "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
        "Centro-Oeste": ["DF", "GO", "MS", "MT"],
        "Sudeste": ["ES", "MG", "RJ", "SP"],
        "Sul": ["PR", "RS", "SC"],
    }
    
    @classmethod
    def validate_region(cls, region: str) -> bool:
        """Valida se região é válida."""
        return region in cls.REGION_MAPPING
    
    @classmethod
    def get_states_from_region(cls, region: str) -> List[str]:
        """Obtém estados de uma região."""
        if not cls.validate_region(region):
            raise ValidationError(f"Região inválida: {region}")
        
        return cls.REGION_MAPPING[region]
    
    @classmethod
    def get_region_from_state(cls, state: str) -> Optional[str]:
        """Obtém região de um estado."""
        for region, states in cls.REGION_MAPPING.items():
            if state in states:
                return region
        return None


# Funções de conveniência
def safe_validate_data(df: DataFrameType, context: str = "geral") -> bool:
    """Validação segura que não levanta exceções."""
    try:
        return DataValidator.validate_dataframe(df, context)
    except ValidationError as e:
        st.error(f"Erro de validação: {e}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado na validação: {e}")
        return False


def safe_validate_states(states: StateList) -> bool:
    """Validação segura de estados que não levanta exceções."""
    try:
        return DataValidator.validate_states(states)
    except ValidationError as e:
        st.error(f"Erro de validação de estados: {e}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado na validação de estados: {e}")
        return False
