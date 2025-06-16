"""
Camada de compatibilidade para manter a API existente funcionando
com a nova arquitetura SOLID refatorada.

Este módulo fornece wrappers que traduzem chamadas da API antiga
para a nova arquitetura baseada em factories e processadores.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import pandas as pd

from .factories import DataProcessingOrchestrator, ComponentFactory
from .config import get_config, get_legacy_config
from utils.helpers.cache_utils import optimized_cache


class CompatibilityLayer:
    """Camada de compatibilidade para manter a API existente."""
    
    def __init__(self):
        self.orchestrator = DataProcessingOrchestrator()
        self.config = get_config()
    
    @optimized_cache(ttl=1800)
    def preparar_dados_comparativo_novo(
        self,
        microdados_full: pd.DataFrame,
        variavel_selecionada: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]],
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Nova implementação usando a arquitetura SOLID para preparar dados comparativos.
        
        Args:
            microdados_full: DataFrame com microdados
            variavel_selecionada: Variável para comparação
            variaveis_categoricas: Mapeamentos de variáveis categóricas
            colunas_notas: Lista de colunas de notas
            competencia_mapping: Mapeamento de competências
            
        Returns:
            DataFrame preparado para visualização
        """
        try:
            # Usar o factory para criar processador
            from .factories import StateProcessorFactory
            processor = StateProcessorFactory.create_performance_processor()
              # Aplicar filtros usando estratégias
            from .factories import FilterStrategyFactory
            filter_factory = FilterStrategyFactory()
            score_filter = filter_factory.get_score_filter()
            
            # Filtrar dados válidos
            filtered_data = score_filter.apply_filter(
                microdados_full,
                exclude_zero_scores=True,
                score_columns=colunas_notas
            )
            
            if filtered_data.empty:
                return pd.DataFrame()
            
            # Processar por categorias da variável selecionada
            if variavel_selecionada not in filtered_data.columns:
                print(f"Variável {variavel_selecionada} não encontrada")
                return pd.DataFrame()
              # Usar mapeamento se disponível
            from .common_utils import MappingManager
            mapping_manager = MappingManager()
            
            # Aplicar mapeamento básico
            plot_column = variavel_selecionada
            if variavel_selecionada in variaveis_categoricas:
                if "mapeamento" in variaveis_categoricas[variavel_selecionada]:
                    mapping = variaveis_categoricas[variavel_selecionada]["mapeamento"]
                    mapped_data = filtered_data.copy()
                    mapped_data[f"{variavel_selecionada}_mapped"] = mapped_data[variavel_selecionada].map(mapping).fillna(mapped_data[variavel_selecionada])
                    plot_column = f"{variavel_selecionada}_mapped"
                else:
                    mapped_data = filtered_data
            else:
                mapped_data = filtered_data
            
            # Agrupar por categoria e calcular médias
            results = []
            categories = mapped_data[plot_column].unique()
            
            stats_calculator = ComponentFactory.get_stats_calculator()
            
            for category in categories:
                category_data = mapped_data[mapped_data[plot_column] == category]
                
                for score_col in colunas_notas:
                    if score_col in category_data.columns:
                        valid_scores = category_data[category_data[score_col] > 0][score_col]
                        
                        if len(valid_scores) > 0:
                            mean_score = stats_calculator.calculate_mean(valid_scores.tolist())
                            competence_name = competencia_mapping.get(score_col, score_col)
                            
                            results.append({
                                'Categoria': category,
                                'Competencia': competence_name,
                                'Media': round(mean_score, 2),
                                'Quantidade': len(valid_scores)
                            })
            
            # Formatar para visualização
            formatter = ComponentFactory.get_data_formatter()
            return formatter.format_for_bar_chart(results, 'Categoria', 'Media')
            
        except Exception as e:
            print(f"Erro na nova implementação de dados comparativos: {e}")
            return pd.DataFrame()
    
    @optimized_cache(ttl=1800)
    def preparar_dados_aspecto_social_novo(
        self,
        microdados_full: pd.DataFrame,
        aspecto_social: str,
        variaveis_categoricas: Dict[str, Dict[str, Any]],
        agrupar_por_regiao: bool = False
    ) -> pd.DataFrame:
        """
        Nova implementação para aspectos sociais usando arquitetura SOLID.
        
        Args:
            microdados_full: DataFrame com microdados
            aspecto_social: Aspecto social a analisar
            variaveis_categoricas: Mapeamentos de variáveis
            agrupar_por_regiao: Se deve agrupar por região
            
        Returns:
            DataFrame preparado para visualização
        """
        try:
            # Validar entrada
            validator = ComponentFactory.get_validator()
            if not validator.validate(microdados_full, [aspecto_social]):
                return pd.DataFrame()
            
            # Criar processador social
            from .factories import StateProcessorFactory
            processor = StateProcessorFactory.create_social_processor()
            
            # Obter estados únicos nos dados
            if 'SG_UF_PROVA' not in microdados_full.columns:
                print("Coluna SG_UF_PROVA não encontrada")
                return pd.DataFrame()
            
            states = microdados_full['SG_UF_PROVA'].unique().tolist()
            
            # Processar usando novo orquestrador
            results = self.orchestrator.process_social_aspects_data(
                microdados_full,
                states,
                aspecto_social,
                variaveis_categoricas,
                agrupar_por_regiao
            )
            
            return results
            
        except Exception as e:
            print(f"Erro na nova implementação de aspectos sociais: {e}")
            return pd.DataFrame()
    
    @optimized_cache(ttl=3600)
    def preparar_dados_desempenho_estados_novo(
        self,
        microdados_estados: pd.DataFrame,
        estados_selecionados: List[str],
        colunas_notas: List[str],
        competencia_mapping: Dict[str, str],
        agrupar_por_regiao: bool = False
    ) -> pd.DataFrame:
        """
        Nova implementação para desempenho por estados usando arquitetura SOLID.
        
        Args:
            microdados_estados: DataFrame com dados por estado
            estados_selecionados: Lista de estados
            colunas_notas: Colunas de notas
            competencia_mapping: Mapeamento de competências
            agrupar_por_regiao: Se deve agrupar por região
            
        Returns:
            DataFrame preparado para visualização
        """
        try:
            # Usar orquestrador principal
            results = self.orchestrator.process_performance_data(
                microdados_estados,
                estados_selecionados,
                colunas_notas,
                competencia_mapping,
                agrupar_por_regiao
            )
            
            return results
            
        except Exception as e:
            print(f"Erro na nova implementação de desempenho por estados: {e}")
            return pd.DataFrame()
    
    def aplicar_filtros_combinados(
        self,
        data: pd.DataFrame,
        filtros: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Aplica múltiplos filtros de forma otimizada usando estratégias.
        
        Args:
            data: DataFrame a filtrar
            filtros: Dicionário com critérios de filtro
            
        Returns:
            DataFrame filtrado
        """
        try:
            # Criar estratégias de filtro
            from .factories import FilterStrategyFactory
            
            strategies = []
            
            # Adicionar filtros de notas se necessário
            if any(key in filtros for key in ['exclude_zero_scores', 'min_score', 'max_score']):
                strategies.append(FilterStrategyFactory.get_score_filter())
            
            # Adicionar filtros demográficos se necessário
            if any(key in filtros for key in ['gender', 'school_type', 'race', 'income_bracket']):
                strategies.append(FilterStrategyFactory.get_demographic_filter())
            
            # Aplicar filtros combinados
            if strategies:
                combined_filter = FilterStrategyFactory.create_combined_filter(strategies)
                return combined_filter.apply_filter(data, **filtros)
            
            return data
            
        except Exception as e:
            print(f"Erro ao aplicar filtros combinados: {e}")
            return data


# Instância global da camada de compatibilidade
_compatibility_layer = CompatibilityLayer()


# Funções de conveniência que mantêm a API original
def preparar_dados_comparativo_otimizado(
    microdados_full: pd.DataFrame,
    variavel_selecionada: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]],
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Função otimizada para preparar dados comparativos.
    Usa a nova arquitetura SOLID por baixo dos panos.
    """
    return _compatibility_layer.preparar_dados_comparativo_novo(
        microdados_full, variavel_selecionada, variaveis_categoricas,
        colunas_notas, competencia_mapping
    )


def preparar_dados_aspecto_social_otimizado(
    microdados_full: pd.DataFrame,
    aspecto_social: str,
    variaveis_categoricas: Dict[str, Dict[str, Any]],
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Função otimizada para preparar dados de aspectos sociais.
    Usa a nova arquitetura SOLID por baixo dos panos.
    """
    return _compatibility_layer.preparar_dados_aspecto_social_novo(
        microdados_full, aspecto_social, variaveis_categoricas, agrupar_por_regiao
    )


def preparar_dados_desempenho_estados_otimizado(
    microdados_estados: pd.DataFrame,
    estados_selecionados: List[str],
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str],
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Função otimizada para preparar dados de desempenho por estados.
    Usa a nova arquitetura SOLID por baixo dos panos.
    """
    return _compatibility_layer.preparar_dados_desempenho_estados_novo(
        microdados_estados, estados_selecionados, colunas_notas,
        competencia_mapping, agrupar_por_regiao
    )


def aplicar_filtros_inteligentes(
    data: pd.DataFrame,
    **filtros
) -> pd.DataFrame:
    """
    Aplica filtros de forma inteligente usando estratégias otimizadas.
    
    Exemplos de uso:
    - aplicar_filtros_inteligentes(data, exclude_zero_scores=True, gender='F')
    - aplicar_filtros_inteligentes(data, school_type='Pública', min_score=400)
    """
    return _compatibility_layer.aplicar_filtros_combinados(data, filtros)


# Função para demonstrar uso da nova arquitetura
def exemplo_uso_nova_arquitetura():
    """
    Exemplo de como usar a nova arquitetura diretamente.
    """
    print("=== Exemplo de Uso da Nova Arquitetura SOLID ===")
    
    # 1. Criar componentes usando factories
    from .factories import ComponentFactory, StateProcessorFactory
    
    validator = ComponentFactory.get_validator()
    memory_manager = ComponentFactory.get_memory_manager()
    stats_calculator = ComponentFactory.get_stats_calculator()
    
    print("✓ Componentes criados usando factories")
    
    # 2. Criar processador específico
    performance_processor = StateProcessorFactory.create_performance_processor()
    
    print("✓ Processador de desempenho criado")
    
    # 3. Usar orquestrador para operações complexas
    orchestrator = DataProcessingOrchestrator()
    
    print("✓ Orquestrador inicializado")
    
    # 4. Aplicar configurações
    from .config import get_config, update_config
    
    config = get_config()
    print(f"✓ Configuração carregada: batch_size = {config.memory.batch_size_states}")
    
    # 5. Atualizar configuração se necessário
    update_config(debug=True)
    print("✓ Configuração atualizada")
    
    print("\n=== Arquitetura SOLID implementada com sucesso! ===")
    print("Princípios aplicados:")
    print("- Single Responsibility Principle (SRP)")
    print("- Open/Closed Principle (OCP)")
    print("- Liskov Substitution Principle (LSP)")
    print("- Interface Segregation Principle (ISP)")
    print("- Dependency Inversion Principle (DIP)")
    print("- Factory Pattern")
    print("- Strategy Pattern")
    print("- Singleton Pattern")


if __name__ == "__main__":
    exemplo_uso_nova_arquitetura()
