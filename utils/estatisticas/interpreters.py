"""
Interpretadores para resultados estatísticos.
Fornece interpretações contextuais seguindo o princípio Single Responsibility.
"""
from typing import Dict, Any, Optional
from utils.mappings import get_mappings


class CorrelationInterpreter:
    """Interpretador para correlações."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.thresholds = self.mappings['limiares_estatisticos']
    
    def interpret_correlation_strength(self, correlation_value: float) -> str:
        """
        Interpreta a força da correlação.
        
        Args:
            correlation_value: Valor da correlação
            
        Returns:
            Interpretação textual da força
        """
        abs_corr = abs(correlation_value)
        
        if abs_corr < self.thresholds['correlacao_fraca']:
            strength = "muito fraca"
        elif abs_corr < self.thresholds['correlacao_moderada']:
            strength = "fraca"
        elif abs_corr < self.thresholds['correlacao_forte']:
            strength = "moderada"
        elif abs_corr < 0.9:
            strength = "forte"
        else:
            strength = "muito forte"
        
        return f"associação {strength}"
    
    def interpret_cramers_v(self, v_cramer: float) -> str:
        """
        Interpreta o valor do V de Cramer.
        
        Args:
            v_cramer: Valor do V de Cramer
            
        Returns:
            Interpretação contextual
        """
        if v_cramer < 0.1:
            return "Associação negligenciável, indicando que estas características são praticamente independentes"
        elif v_cramer < 0.2:
            return "Associação fraca, sugerindo que estas características compartilham uma pequena sobreposição"
        elif v_cramer < 0.3:
            return "Associação moderada, indicando algum grau de relação entre estas características"
        elif v_cramer < 0.4:
            return "Associação relativamente forte, sugerindo uma conexão importante entre estas características sociais"
        else:
            return "Associação muito forte, evidenciando uma substancial inter-relação entre estas características"
    
    def classify_effect_size(self, v_cramer: float) -> str:
        """
        Classifica o tamanho do efeito.
        
        Args:
            v_cramer: Valor do V de Cramer
            
        Returns:
            Classificação do tamanho do efeito
        """
        if v_cramer < 0.1:
            return "insignificante"
        elif v_cramer < 0.3:
            return "pequeno"
        elif v_cramer < 0.5:
            return "médio"
        else:
            return "grande"


class VariabilityInterpreter:
    """Interpretador para medidas de variabilidade."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.thresholds = self.mappings['limiares_estatisticos']
    
    def interpret_coefficient_of_variation(self, cv: float) -> str:
        """
        Interpreta o coeficiente de variação.
        
        Args:
            cv: Coeficiente de variação em percentual
            
        Returns:
            Interpretação da variabilidade
        """
        if cv < self.thresholds['variabilidade_baixa']:
            return "Baixa variabilidade"
        elif cv < self.thresholds['variabilidade_moderada']:
            return "Variabilidade moderada"
        else:
            return "Alta variabilidade"
    
    def interpret_regional_variability(self, cv: float) -> str:
        """
        Interpreta a variabilidade regional específica.
        
        Args:
            cv: Coeficiente de variação
            
        Returns:
            Interpretação específica para análise regional
        """
        if cv < self.thresholds['variabilidade_baixa']:
            return "Baixa variabilidade, indicando relativa homogeneidade regional"
        elif cv < self.thresholds['variabilidade_moderada']:
            return "Variabilidade moderada, sugerindo diferenças regionais significativas"
        else:
            return "Alta variabilidade, mostrando importantes disparidades regionais"
    
    def classify_regional_disparity(self, cv: float, amplitude_percentual: float) -> str:
        """
        Classifica disparidade regional baseada em múltiplos indicadores.
        
        Args:
            cv: Coeficiente de variação
            amplitude_percentual: Amplitude percentual
            
        Returns:
            Classificação da disparidade
        """
        if cv < self.thresholds['variabilidade_baixa'] and amplitude_percentual < 20:
            return "mínima"
        elif cv < self.thresholds['variabilidade_moderada'] and amplitude_percentual < 50:
            return "baixa"
        elif cv < 40 and amplitude_percentual < 100:
            return "moderada"
        elif cv < 60 and amplitude_percentual < 200:
            return "significativa"
        else:
            return "extrema"


class ConcentrationInterpreter:
    """Interpretador para medidas de concentração."""
    
    def classify_concentration(self, concentration_index: float) -> str:
        """
        Classifica o nível de concentração.
        
        Args:
            concentration_index: Índice de concentração
            
        Returns:
            Classificação da concentração
        """
        if concentration_index < 0.2:
            return "Distribuição muito homogênea"
        elif concentration_index < 0.4:
            return "Distribuição relativamente homogênea"
        elif concentration_index < 0.6:
            return "Distribuição moderadamente concentrada"
        elif concentration_index < 0.8:
            return "Distribuição concentrada"
        else:
            return "Distribuição muito concentrada"
    
    def interpret_gini_coefficient(self, gini: float) -> str:
        """
        Interpreta o coeficiente de Gini.
        
        Args:
            gini: Coeficiente de Gini
            
        Returns:
            Interpretação da desigualdade
        """
        if gini < 0.2:
            return "Desigualdade muito baixa"
        elif gini < 0.3:
            return "Desigualdade baixa"
        elif gini < 0.4:
            return "Desigualdade moderada"
        elif gini < 0.5:
            return "Desigualdade alta"
        else:
            return "Desigualdade muito alta"


class PerformanceInterpreter:
    """Interpretador para análises de desempenho."""
    
    def __init__(self):
        self.mappings = get_mappings()
        self.performance_mapping = self.mappings['mapeamento_desempenho']
    
    def classify_performance_level(self, score: float) -> str:
        """
        Classifica o nível de desempenho baseado na nota.
        
        Args:
            score: Nota de desempenho
            
        Returns:
            Classificação do desempenho
        """
        faixas = self.performance_mapping['faixas_notas']
        
        for level, (min_score, max_score) in faixas.items():
            if min_score <= score < max_score:
                return level
        
        return "indefinido"
    
    def interpret_performance_gap(self, percentage_gap: float) -> str:
        """
        Interpreta a diferença de desempenho.
        
        Args:
            percentage_gap: Diferença percentual de desempenho
            
        Returns:
            Interpretação da diferença
        """
        if percentage_gap < 5:
            return "Diferença pequena"
        elif percentage_gap < 15:
            return "Diferença moderada"
        elif percentage_gap < 30:
            return "Diferença significativa"
        else:
            return "Diferença muito grande"
    
    def interpret_score_distribution(
        self, 
        mean: float, 
        std: float, 
        cv: float
    ) -> Dict[str, str]:
        """
        Interpreta a distribuição de notas.
        
        Args:
            mean: Média das notas
            std: Desvio padrão
            cv: Coeficiente de variação
            
        Returns:
            Dict com interpretações da distribuição
        """
        interpretations = {}
        
        # Interpretar média
        if mean < 450:
            interpretations['mean_level'] = "Desempenho médio abaixo do esperado"
        elif mean < 600:
            interpretations['mean_level'] = "Desempenho médio regular"
        elif mean < 750:
            interpretations['mean_level'] = "Desempenho médio bom"
        else:
            interpretations['mean_level'] = "Desempenho médio excelente"
        
        # Interpretar variabilidade
        if cv < 15:
            interpretations['variability'] = "Baixa dispersão nas notas"
        elif cv < 25:
            interpretations['variability'] = "Dispersão moderada nas notas"
        else:
            interpretations['variability'] = "Alta dispersão nas notas"
        
        return interpretations


class TrendInterpreter:
    """Interpretador para análises de tendências temporais."""
    
    def interpret_trend_direction(self, slope: float, r_squared: float) -> str:
        """
        Interpreta a direção e força da tendência.
        
        Args:
            slope: Inclinação da linha de tendência
            r_squared: R-quadrado da regressão
            
        Returns:
            Interpretação da tendência
        """
        # Determinar direção
        if abs(slope) < 0.01:
            direction = "estável"
        elif slope > 0:
            direction = "crescente"
        else:
            direction = "decrescente"
        
        # Determinar intensidade
        if r_squared < 0.3:
            intensity = "fraca"
        elif r_squared < 0.7:
            intensity = "moderada"
        else:
            intensity = "forte"
        
        return f"{direction} {intensity}"
    
    def interpret_percentage_change(self, percentage_change: float) -> str:
        """
        Interpreta a mudança percentual.
        
        Args:
            percentage_change: Mudança percentual
            
        Returns:
            Interpretação da mudança
        """
        abs_change = abs(percentage_change)
        
        if abs_change < 5:
            magnitude = "manteve-se relativamente estável"
        elif percentage_change > 0:
            if abs_change < 15:
                magnitude = f"aumentou moderadamente ({abs_change:.1f}%)"
            else:
                magnitude = f"aumentou significativamente ({abs_change:.1f}%)"
        else:
            if abs_change < 15:
                magnitude = f"diminuiu moderadamente ({abs_change:.1f}%)"
            else:
                magnitude = f"diminuiu significativamente ({abs_change:.1f}%)"
        
        return f"{magnitude} ao longo do período analisado"


class StatisticalSignificanceInterpreter:
    """Interpretador para significância estatística."""
    
    @staticmethod
    def interpret_p_value(p_value: float, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Interpreta o valor p.
        
        Args:
            p_value: Valor p do teste
            alpha: Nível de significância
            
        Returns:
            Dict com interpretação da significância
        """
        is_significant = p_value < alpha
        
        if p_value < 0.001:
            strength = "muito forte"
        elif p_value < 0.01:
            strength = "forte"
        elif p_value < 0.05:
            strength = "moderada"
        else:
            strength = "fraca ou ausente"
        
        return {
            'is_significant': is_significant,
            'strength': strength,
            'interpretation': f"Evidência {strength} de associação estatística"
        }
    
    @staticmethod
    def interpret_confidence_interval(lower: float, upper: float, point_estimate: float) -> str:
        """
        Interpreta intervalo de confiança.
        
        Args:
            lower: Limite inferior
            upper: Limite superior
            point_estimate: Estimativa pontual
            
        Returns:
            Interpretação do intervalo
        """
        range_size = upper - lower
        relative_range = (range_size / point_estimate * 100) if point_estimate > 0 else 0
        
        if relative_range < 10:
            precision = "alta precisão"
        elif relative_range < 20:
            precision = "precisão moderada"
        else:
            precision = "baixa precisão"
        
        return f"Estimativa com {precision} (variação de ±{relative_range:.1f}%)"
