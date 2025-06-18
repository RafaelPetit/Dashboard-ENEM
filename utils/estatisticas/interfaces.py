"""
Interfaces base para o módulo de estatísticas.
Define contratos que devem ser seguidos por todas as implementações.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd


class IStatisticsCalculator(ABC):
    """Interface base para calculadores de estatísticas."""
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Calcula estatísticas para os dados fornecidos.
        
        Args:
            data: DataFrame com os dados
            **kwargs: Parâmetros específicos do calculador
            
        Returns:
            Dict com as estatísticas calculadas
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: pd.DataFrame, **kwargs) -> bool:
        """
        Valida se os dados de entrada são adequados para o cálculo.
        
        Args:
            data: DataFrame com os dados
            **kwargs: Parâmetros específicos do calculador
            
        Returns:
            True se dados são válidos, False caso contrário
        """
        pass


class IDataValidator(ABC):
    """Interface para validadores de dados."""
    
    @abstractmethod
    def validate(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Valida se os dados atendem aos requisitos.
        
        Args:
            data: DataFrame a ser validado
            required_columns: Colunas obrigatórias
            
        Returns:
            True se dados são válidos, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_validation_errors(self, data: pd.DataFrame, required_columns: List[str]) -> List[str]:
        """
        Retorna lista de erros de validação.
        
        Args:
            data: DataFrame a ser validado
            required_columns: Colunas obrigatórias
            
        Returns:
            Lista com mensagens de erro
        """
        pass


class IResultBuilder(ABC):
    """Interface para construtores de resultados."""
    
    @abstractmethod
    def build_empty_result(self, reason: str = "Dados insuficientes") -> Dict[str, Any]:
        """
        Constrói um resultado vazio padrão.
        
        Args:
            reason: Motivo pelo qual o resultado está vazio
            
        Returns:
            Dict com resultado vazio estruturado
        """
        pass
    
    @abstractmethod
    def build_result(self, calculations: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constrói o resultado final combinando cálculos e metadados.
        
        Args:
            calculations: Cálculos realizados
            metadata: Metadados adicionais
            
        Returns:
            Dict com resultado estruturado
        """
        pass


class ICorrelationAnalyzer(ABC):
    """Interface para analisadores de correlação."""
    
    @abstractmethod
    def analyze_correlation(
        self, 
        data: pd.DataFrame, 
        var_x: str, 
        var_y: str
    ) -> Dict[str, Any]:
        """
        Analisa correlação entre duas variáveis.
        
        Args:
            data: DataFrame com os dados
            var_x: Nome da primeira variável
            var_y: Nome da segunda variável
            
        Returns:
            Dict com métricas de correlação
        """
        pass
    
    @abstractmethod
    def interpret_correlation(self, correlation_value: float) -> str:
        """
        Interpreta o valor da correlação.
        
        Args:
            correlation_value: Valor da correlação
            
        Returns:
            Interpretação textual da correlação
        """
        pass


class IDistributionAnalyzer(ABC):
    """Interface para analisadores de distribuição."""
    
    @abstractmethod
    def analyze_distribution(self, data: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Analisa a distribuição de uma variável.
        
        Args:
            data: DataFrame com os dados
            column: Nome da coluna a analisar
            
        Returns:
            Dict com métricas de distribuição
        """
        pass
    
    @abstractmethod
    def calculate_percentiles(
        self, 
        data: pd.Series, 
        percentiles: List[float]
    ) -> Dict[str, float]:
        """
        Calcula percentis para uma série.
        
        Args:
            data: Série com os dados
            percentiles: Lista de percentis a calcular
            
        Returns:
            Dict com percentis calculados
        """
        pass


class IRegionalAnalyzer(ABC):
    """Interface para analisadores regionais."""
    
    @abstractmethod
    def analyze_by_region(
        self, 
        data: pd.DataFrame, 
        variable: str, 
        region_column: str = 'Estado'
    ) -> Dict[str, Any]:
        """
        Analisa distribuição por região.
        
        Args:
            data: DataFrame com os dados
            variable: Variável a analisar
            region_column: Coluna com informação regional
            
        Returns:
            Dict com análise regional
        """
        pass
    
    @abstractmethod
    def classify_regional_disparity(
        self, 
        coefficient_of_variation: float, 
        amplitude_percentage: float
    ) -> str:
        """
        Classifica o nível de disparidade regional.
        
        Args:
            coefficient_of_variation: Coeficiente de variação
            amplitude_percentage: Amplitude percentual
            
        Returns:
            Classificação da disparidade
        """
        pass


class IPerformanceAnalyzer(ABC):
    """Interface para analisadores de desempenho."""
    
    @abstractmethod
    def analyze_performance_by_state(
        self, 
        data: pd.DataFrame, 
        performance_column: str
    ) -> Dict[str, Any]:
        """
        Analisa desempenho por estado.
        
        Args:
            data: DataFrame com os dados
            performance_column: Coluna com dados de desempenho
            
        Returns:
            Dict com análise de desempenho
        """
        pass
    
    @abstractmethod
    def calculate_comparative_statistics(
        self, 
        data: pd.DataFrame, 
        category_column: str, 
        value_column: str
    ) -> Dict[str, Any]:
        """
        Calcula estatísticas comparativas entre categorias.
        
        Args:
            data: DataFrame com os dados
            category_column: Coluna com categorias
            value_column: Coluna com valores
            
        Returns:
            Dict com estatísticas comparativas
        """
        pass


class DataValidator(ABC):
    """Interface para validação de dados."""
    
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> bool:
        """
        Valida se os dados estão em formato adequado para análise.
        
        Args:
            data: DataFrame a ser validado
            
        Returns:
            bool: True se dados são válidos, False caso contrário
        """
        pass


class ResultBuilder(ABC):
    """Interface para construção de resultados."""
    
    @abstractmethod
    def build_summary(self, data: pd.DataFrame, analysis_type: str) -> Dict[str, Any]:
        """
        Constrói um resumo dos dados analisados.
        
        Args:
            data: DataFrame com os dados
            analysis_type: Tipo de análise realizada
            
        Returns:
            Dict com resumo estruturado
        """
        pass


class CorrelationAnalyzer(ABC):
    """Interface para análises de correlação."""
    
    @abstractmethod
    def calculate_correlation(self, data: pd.DataFrame, variables: List[str]) -> pd.DataFrame:
        """
        Calcula correlação entre variáveis.
        
        Args:
            data: DataFrame com os dados
            variables: Lista de variáveis para análise
            
        Returns:
            DataFrame com matriz de correlação
        """
        pass


class DistributionAnalyzer(ABC):
    """Interface para análises de distribuição."""
    
    @abstractmethod
    def analyze_distribution(self, data: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Analisa distribuição de uma variável.
        
        Args:
            data: DataFrame com os dados
            column: Nome da coluna a ser analisada
            
        Returns:
            Dict com estatísticas da distribuição
        """
        pass


class RegionalAnalyzer(ABC):
    """Interface para análises regionais."""
    
    @abstractmethod
    def analyze_by_region(self, data: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """
        Analisa dados agrupados por região.
        
        Args:
            data: DataFrame com os dados
            metric: Métrica a ser analisada por região
            
        Returns:
            Dict com análise regional
        """
        pass
