"""
Gerenciador de mapeamentos para o Dashboard.
Centraliza acesso aos mapeamentos de dados e configurações.
"""

from typing import Dict, Any, Optional
from functools import lru_cache

from .core_types import MappingProvider, MappingDict
from .exceptions import MappingError, ConfigurationError


class DashboardMappingManager(MappingProvider):
    """Gerenciador centralizado para mapeamentos do Dashboard."""
    
    def __init__(self):
        """Inicializa o gerenciador de mapeamentos."""
        self._mappings_cache: Optional[MappingDict] = None
        self._mapping_keys = {
            'colunas_notas', 'competencia_mapping', 'race_mapping', 
            'sexo_mapping', 'dependencia_escola_mapping', 'variaveis_sociais',
            'variaveis_categoricas', 'desempenho_mapping', 'infraestrutura_mapping',
            'faixa_etaria_mapping', 'escolaridade_pai_mae_mapping', 'regioes_mapping',
            'faixa_salarial'
        }
    
    @lru_cache(maxsize=1)
    def get_all_mappings(self) -> MappingDict:
        """
        Retorna todos os mapeamentos disponíveis.
        
        Returns:
            Dicionário com todos os mapeamentos
            
        Raises:
            MappingError: Se houver erro ao carregar mapeamentos
        """
        try:
            if self._mappings_cache is None:
                # Tentar diferentes estratégias de importação
                mappings_data = None
                
                # Estratégia 1: Importar diretamente
                try:
                    from utils.mappings import get_mappings
                    mappings_data = get_mappings()
                except ImportError:
                    # Estratégia 2: Importar usando caminho absoluto
                    try:
                        import sys
                        import os
                        utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')
                        sys.path.insert(0, utils_path)
                        from utils.mappings import get_mappings
                        mappings_data = get_mappings()
                        sys.path.remove(utils_path)
                    except ImportError:
                        # Estratégia 3: Usar mapeamentos padrão
                        mappings_data = self._get_default_mappings()
                
                if mappings_data is None:
                    raise MappingError("load", "Não foi possível carregar mapeamentos")
                
                self._mappings_cache = mappings_data
                
                # Validar mapeamentos carregados
                self._validate_mappings(self._mappings_cache)
            
            return self._mappings_cache
            
        except MappingError:
            raise
        except Exception as e:
            raise MappingError("load", f"Erro ao carregar mapeamentos: {str(e)}")
    
    def get_mapping(self, key: str) -> Optional[Any]:
        """
        Retorna um mapeamento específico.
        
        Args:
            key: Chave do mapeamento desejado
            
        Returns:
            Valor do mapeamento ou None se não encontrado
            
        Raises:
            MappingError: Se a chave for inválida
        """
        try:
            mappings = self.get_all_mappings()
            
            if key not in mappings:
                available_keys = list(mappings.keys())
                raise MappingError(
                    key, 
                    f"Chave '{key}' não encontrada. Chaves disponíveis: {available_keys}"
                )
            
            return mappings[key]
            
        except MappingError:
            raise
        except Exception as e:
            raise MappingError(key, f"Erro ao acessar mapeamento: {str(e)}")
    
    def get_required_mappings(self, tab_name: str) -> MappingDict:
        """
        Retorna mapeamentos necessários para uma aba específica.
        
        Args:
            tab_name: Nome da aba
            
        Returns:
            Dicionário com mapeamentos necessários
        """
        all_mappings = self.get_all_mappings()
        
        # Mapeamentos base necessários para todas as abas
        base_mappings = {
            'regioes_mapping': all_mappings['regioes_mapping']
        }
        
        # Mapeamentos específicos por aba
        if tab_name == "Geral":
            base_mappings.update({
                'colunas_notas': all_mappings['colunas_notas'],
                'competencia_mapping': all_mappings['competencia_mapping']
            })
        
        elif tab_name == "Aspectos Sociais":
            base_mappings.update({
                'variaveis_sociais': all_mappings['variaveis_sociais']
            })
        
        elif tab_name == "Desempenho":
            base_mappings.update({
                'colunas_notas': all_mappings['colunas_notas'],
                'competencia_mapping': all_mappings['competencia_mapping'],
                'race_mapping': all_mappings['race_mapping'],
                'variaveis_categoricas': all_mappings['variaveis_categoricas'],
                'desempenho_mapping': all_mappings['desempenho_mapping']
            })
        
        return base_mappings
    
    def _validate_mappings(self, mappings: MappingDict) -> None:
        """
        Valida se todos os mapeamentos essenciais estão presentes.
        
        Args:
            mappings: Dicionário de mapeamentos para validar
            
        Raises:
            ConfigurationError: Se algum mapeamento essencial estiver ausente
        """
        missing_keys = []
        
        for key in self._mapping_keys:
            if key not in mappings:
                missing_keys.append(key)
        
        if missing_keys:
            raise ConfigurationError(
                "mappings", 
                f"Mapeamentos ausentes: {missing_keys}"
            )
        
        # Validações específicas
        self._validate_regions_mapping(mappings.get('regioes_mapping', {}))
        self._validate_competencia_mapping(mappings.get('competencia_mapping', {}))
    
    def _validate_regions_mapping(self, regions_mapping: Dict[str, Any]) -> None:
        """Valida o mapeamento de regiões."""
        if not regions_mapping:
            raise ConfigurationError("regioes_mapping", "Mapeamento de regiões não pode estar vazio")
        
        expected_regions = {'Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'}
        actual_regions = set(regions_mapping.keys())
        
        missing_regions = expected_regions - actual_regions
        if missing_regions:
            raise ConfigurationError(
                "regioes_mapping", 
                f"Regiões ausentes: {missing_regions}"
            )
    
    def _validate_competencia_mapping(self, competencia_mapping: Dict[str, Any]) -> None:
        """Valida o mapeamento de competências."""
        if not competencia_mapping:
            raise ConfigurationError("competencia_mapping", "Mapeamento de competências não pode estar vazio")
        
        expected_competencias = {'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'}
        actual_competencias = set(competencia_mapping.keys())
        
        missing_competencias = expected_competencias - actual_competencias
        if missing_competencias:
            raise ConfigurationError(
                "competencia_mapping", 
                f"Competências ausentes: {missing_competencias}"
            )
    
    def refresh_mappings(self) -> None:
        """
        Força recarregamento dos mapeamentos.
        Útil se os mapeamentos forem atualizados em runtime.
        """
        self._mappings_cache = None
        self.get_all_mappings.cache_clear()
    
    def get_available_states(self) -> list:
        """
        Retorna lista de todos os estados disponíveis baseada no mapeamento de regiões.
        
        Returns:
            Lista ordenada de códigos de estados
        """
        regions_mapping = self.get_mapping('regioes_mapping')
        all_states = []
        
        for states in regions_mapping.values():
            all_states.extend(states)
        
        return sorted(list(set(all_states)))
    
    def get_states_by_region(self, region: str) -> list:
        """
        Retorna estados de uma região específica.
        
        Args:
            region: Nome da região
            
        Returns:
            Lista de estados da região
        """
        regions_mapping = self.get_mapping('regioes_mapping')
        return regions_mapping.get(region, [])
    
    def get_region_by_state(self, state: str) -> Optional[str]:
        """
        Retorna a região de um estado específico.
        
        Args:
            state: Código do estado
            
        Returns:
            Nome da região ou None se não encontrado
        """
        regions_mapping = self.get_mapping('regioes_mapping')
        
        for region, states in regions_mapping.items():
            if state in states:
                return region
        
        return None
    
    def _get_default_mappings(self) -> Dict[str, Any]:
        """
        Retorna mapeamentos padrão caso não seja possível importar do utils.
        
        Returns:
            Dicionário com mapeamentos básicos
        """
        return {
            'colunas_notas': ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'],
            'competencia_mapping': {
                'NU_NOTA_CN': 'Ciências da Natureza',
                'NU_NOTA_CH': 'Ciências Humanas',
                'NU_NOTA_LC': 'Linguagens e Códigos',
                'NU_NOTA_MT': 'Matemática',
                'NU_NOTA_REDACAO': 'Redação'
            },
            'race_mapping': {
                0: 'Não declarado',
                1: 'Branca',
                2: 'Preta',
                3: 'Parda',
                4: 'Amarela',
                5: 'Indígena',
                6: 'Não dispõe da informação'
            },
            'sexo_mapping': {
                'M': 'Masculino',
                'F': 'Feminino'
            },
            'dependencia_escola_mapping': {
                1: 'Federal',
                2: 'Estadual',
                3: 'Municipal',
                4: 'Privada',
                -1: 'Não Respondeu'
            },
            'regioes_mapping': {
                "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
                "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
                "Centro-Oeste": ["DF", "GO", "MS", "MT"],
                "Sudeste": ["ES", "MG", "RJ", "SP"],
                "Sul": ["PR", "RS", "SC"],
            },
            'variaveis_sociais': {
                "TP_COR_RACA": {"nome": "Raça/Cor", "mapeamento": {
                    0: 'Não declarado', 1: 'Branca', 2: 'Preta', 3: 'Parda', 4: 'Amarela', 5: 'Indígena', 6: 'Não dispõe da informação'
                }},
                "TP_SEXO": {"nome": "Sexo", "mapeamento": {'M': 'Masculino', 'F': 'Feminino'}},
                "TP_DEPENDENCIA_ADM_ESC": {"nome": "Tipo de Escola", "mapeamento": {
                    1: 'Federal', 2: 'Estadual', 3: 'Municipal', 4: 'Privada', -1: 'Não Respondeu'
                }}
            },
            'variaveis_categoricas': {
                "TP_COR_RACA": {
                    "nome": "Raça/Cor",
                    "mapeamento": {0: 'Não declarado', 1: 'Branca', 2: 'Preta', 3: 'Parda', 4: 'Amarela', 5: 'Indígena', 6: 'Não dispõe da informação'},
                    "ordem": ['Não declarado', 'Branca', 'Preta', 'Parda', 'Amarela', 'Indígena', 'Não dispõe da informação']
                },
                "TP_SEXO": {
                    "nome": "Sexo",
                    "mapeamento": {'M': 'Masculino', 'F': 'Feminino'},
                    "ordem": ['Masculino', 'Feminino']
                }
            },
            'desempenho_mapping': {
                1: 'Desempenho Alto',
                2: 'Desempenho Médio',
                3: 'Desempenho Baixo',
            }
        }


class MappingValidator:
    """Validador para mapeamentos de dados."""
    
    @staticmethod
    def validate_mapping_structure(mapping: Dict[str, Any], expected_keys: set) -> bool:
        """
        Valida estrutura de um mapeamento.
        
        Args:
            mapping: Mapeamento a ser validado
            expected_keys: Chaves esperadas
            
        Returns:
            True se válido
            
        Raises:
            ConfigurationError: Se estrutura for inválida
        """
        if not isinstance(mapping, dict):
            raise ConfigurationError("mapping_structure", "Mapeamento deve ser um dicionário")
        
        actual_keys = set(mapping.keys())
        missing_keys = expected_keys - actual_keys
        
        if missing_keys:
            raise ConfigurationError(
                "mapping_structure", 
                f"Chaves ausentes: {missing_keys}"
            )
        
        return True
    
    @staticmethod
    def validate_non_empty_values(mapping: Dict[str, Any]) -> bool:
        """
        Valida se os valores do mapeamento não estão vazios.
        
        Args:
            mapping: Mapeamento a ser validado
            
        Returns:
            True se válido
            
        Raises:
            ConfigurationError: Se algum valor estiver vazio
        """
        empty_keys = []
        
        for key, value in mapping.items():
            if not value or (isinstance(value, (list, dict, str)) and len(value) == 0):
                empty_keys.append(key)
        
        if empty_keys:
            raise ConfigurationError(
                "empty_values", 
                f"Valores vazios encontrados para: {empty_keys}"
            )
        
        return True


# Instância global do gerenciador
mapping_manager = DashboardMappingManager()
