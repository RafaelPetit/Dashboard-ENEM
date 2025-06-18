"""
Análise de aspectos sociais refatorada.
Implementa análises sociais usando arquitetura modular e princípios SOLID.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function
from utils.mappings import get_mappings

# Importar analisadores especializados
from .social_analyzers import (
    SocialDistributionAnalyzer,
    SocialCorrelationAnalyzer, 
    SocialRegionalAnalyzer,
    SocialCategoryStatsCalculator
)
from .trend_analyzer import SocialTrendAnalyzer

# Imports necessários para funções auxiliares
try:
    from scipy.stats import chi2_contingency
except ImportError:
    chi2_contingency = None

# Manter compatibilidade com código existente
mappings = get_mappings()
LIMIARES_ESTATISTICOS = mappings.get('limiares_estatisticos', {})
LIMIARES_PROCESSAMENTO = mappings.get('limiares_processamento', {})

# Constantes para compatibilidade
LIMITE_VARIABILIDADE_BAIXA = LIMIARES_ESTATISTICOS.get('variabilidade_baixa', 15)
LIMITE_VARIABILIDADE_MODERADA = LIMIARES_ESTATISTICOS.get('variabilidade_moderada', 30)
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS.get('correlacao_fraca', 0.3)
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS.get('correlacao_moderada', 0.7)
LIMITE_CORRELACAO_FORTE = 0.8

@optimized_cache(ttl=1800)
def calcular_estatisticas_distribuicao(
    contagem_aspecto: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calcula estatísticas básicas sobre a distribuição de um aspecto social.
    REFATORADO: Função livre de instâncias para compatibilidade com cache Streamlit.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com a contagem de ocorrências por categoria
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com estatísticas calculadas
    """
    # Usar função auxiliar sem instância de classe
    return _calcular_distribuicao_sem_instancia(contagem_aspecto)


def _criar_estatisticas_distribuicao_vazias() -> Dict[str, Any]:
    """
    Cria um conjunto de estatísticas de distribuição vazias para casos onde não há dados suficientes.
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão
    """
    return {
        'total': 0,
        'categoria_mais_frequente': None,
        'categoria_menos_frequente': None,
        'num_categorias': 0,
        'media': 0,
        'mediana': 0,
        'indice_concentracao': 0,
        'classificacao_concentracao': "Dados insuficientes",
        'entropia': 0,
        'entropia_normalizada': 0,
        'razao_max_min': 0,
        'coef_variacao': 0,
        'desvio_padrao': 0
    }


@memory_intensive_function
@optimized_cache(ttl=1800)
def analisar_correlacao_categorias(
    df_correlacao: pd.DataFrame, 
    var_x_plot: str, 
    var_y_plot: str
) -> Dict[str, Any]:
    """
    Analisa a correlação entre duas variáveis categóricas.
    REFATORADO: Função livre de instâncias para compatibilidade com cache Streamlit.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com os dados para análise
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com métricas de correlação e análise
    """
    try:
        # Validar entrada
        if df_correlacao is None or df_correlacao.empty:
            return _criar_correlacao_vazia()
        
        if var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
            return _criar_correlacao_vazia()
        
        # Remover valores nulos
        df_clean = df_correlacao[[var_x_plot, var_y_plot]].dropna()
        
        if len(df_clean) < 10:
            return _criar_correlacao_vazia()
        
        # Criar tabela de contingência
        contingency_table = pd.crosstab(df_clean[var_x_plot], df_clean[var_y_plot])
        
        if contingency_table.empty or contingency_table.sum().sum() < 10:
            return _criar_correlacao_vazia()
        
        # Aplicar teste qui-quadrado
        if chi2_contingency is not None:
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        else:
            # Implementação básica se scipy não estiver disponível
            chi2, p_value, dof = _calculate_chi_square_basic(contingency_table)
        
        # Calcular V de Cramer
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        
        # Interpretar resultados
        interpretacao = _interpretar_v_cramer(cramers_v)
        tamanho_efeito = _classificar_tamanho_efeito(cramers_v)
        
        # Calcular informação mútua normalizada (versão básica)
        info_mutua_norm = min(cramers_v * 2, 1.0)  # Aproximação básica
        
        return {
            'qui_quadrado': float(chi2),
            'valor_p': float(p_value),
            'gl': int(dof),
            'v_cramer': float(cramers_v),
            'coeficiente': float(cramers_v),  # Alias para compatibilidade
            'n_amostras': int(n),
            'significativo': p_value < 0.05,
            'interpretacao': interpretacao,
            'tamanho_efeito': tamanho_efeito,
            'tabela_contingencia': contingency_table,
            'info_mutua_norm': float(info_mutua_norm)
        }
        
    except Exception as e:
        print(f"Erro em analisar_correlacao_categorias: {e}")
        return _criar_correlacao_vazia()


def _interpretar_correlacao_categorias(coef: float) -> str:
    """
    Interpreta o valor do coeficiente de correlação para variáveis categóricas.
    
    Parâmetros:
    -----------
    coef : float
        Valor do coeficiente de correlação normalizado
        
    Retorna:
    --------
    str: Interpretação textual da correlação
    """
    if coef < LIMITE_CORRELACAO_FRACA:
        return "associação muito fraca"
    elif coef < LIMITE_CORRELACAO_MODERADA:
        return "associação fraca"
    elif coef < LIMITE_CORRELACAO_FORTE:
        return "associação moderada"
    elif coef < 0.9:
        return "associação forte"
    else:
        return "associação muito forte"


def _interpretar_v_cramer(v_cramer: float) -> str:
    """
    Interpreta o valor do V de Cramer.
    
    Parâmetros:
    -----------
    v_cramer : float
        Valor do V de Cramer
        
    Retorna:
    --------
    str: Interpretação contextual do V de Cramer
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


def _classificar_tamanho_efeito(v_cramer: float) -> str:
    """
    Classifica o tamanho do efeito com base no V de Cramer.
    
    Parâmetros:
    -----------
    v_cramer : float
        Valor do V de Cramer
        
    Retorna:
    --------
    str: Classificação do tamanho do efeito
    """
    if v_cramer < 0.1:
        return "insignificante"
    elif v_cramer < 0.3:
        return "pequeno"
    elif v_cramer < 0.5:
        return "médio"
    else:
        return "grande"


def _criar_resultado_correlacao_vazio(motivo: str = "Dados insuficientes") -> Dict[str, Any]:
    """
    Cria um resultado de correlação vazio para casos onde não há dados suficientes.
    
    Parâmetros:
    -----------
    motivo : str, default="Dados insuficientes"
        Motivo pelo qual não foi possível calcular a correlação
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão
    """
    return {
        'qui_quadrado': 0,
        'gl': 0,
        'valor_p': 1,
        'coeficiente': 0,
        'v_cramer': 0,
        'info_mutua': 0,
        'info_mutua_norm': 0,
        'interpretacao': motivo,
        'contexto': "Não foi possível calcular associação entre estas variáveis",
        'significativo': False,
        'tamanho_efeito': "indefinido",
        'tabela_contingencia': pd.DataFrame(),
        'n_amostras': 0
    }


@optimized_cache(ttl=1800)
def analisar_distribuicao_regional(
    df_por_estado: pd.DataFrame, 
    aspecto_social: str, 
    categoria: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analisa como um aspecto social se distribui regionalmente.
    
    Parâmetros:
    -----------
    df_por_estado : DataFrame
        DataFrame com dados por estado
    aspecto_social : str
        Nome do aspecto social analisado
    categoria : str, opcional
        Categoria específica para análise
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com análise regional
    """
    # Verificar se temos dados válidos
    if df_por_estado is None or df_por_estado.empty:
        return _criar_resultado_regional_vazio()
    
    # Verificar se temos as colunas necessárias
    colunas_necessarias = ['Estado', 'Categoria', 'Percentual']
    if not all(col in df_por_estado.columns for col in colunas_necessarias):
        print(f"Colunas necessárias não encontradas. Disponíveis: {df_por_estado.columns.tolist()}")
        return _criar_resultado_regional_vazio()
    
    try:
        # Filtrar para uma categoria específica se solicitado
        if categoria:
            df_analise = df_por_estado[df_por_estado['Categoria'] == categoria].copy()
            
            # Verificar se a categoria existe nos dados
            if df_analise.empty:
                print(f"Categoria '{categoria}' não encontrada nos dados")
                return _criar_resultado_regional_vazio()
        else:
            # Se não houver categoria específica, usamos todo o dataframe
            df_analise = df_por_estado.copy()
        
        # Verificar se temos dados para análise
        if df_analise.empty or len(df_analise) < 3:  # Mínimo de 3 estados para análise significativa
            print(f"Dados insuficientes para análise regional: {len(df_analise)} estados")
            return _criar_resultado_regional_vazio()
        
        # Calcular estatísticas básicas
        percentual_medio = df_analise['Percentual'].mean()
        desvio_padrao = df_analise['Percentual'].std()
        coef_variacao = (desvio_padrao / percentual_medio * 100) if percentual_medio > 0 else 0
        
        # Calcular amplitude percentual
        valor_min = df_analise['Percentual'].min()
        valor_max = df_analise['Percentual'].max()
        amplitude = valor_max - valor_min
        amplitude_percentual = (amplitude / valor_min * 100) if valor_min > 0 else 0
        
        # Identificar estados com valores extremos (forma segura)
        try:
            idx_max = df_analise['Percentual'].idxmax()
            idx_min = df_analise['Percentual'].idxmin()
            
            maior_percentual = df_analise.loc[idx_max].copy() if idx_max in df_analise.index else None
            menor_percentual = df_analise.loc[idx_min].copy() if idx_min in df_analise.index else None
        except (KeyError, ValueError):
            # Fallback se idxmax/idxmin falhar
            maior_percentual = df_analise[df_analise['Percentual'] == valor_max].iloc[0].copy() if not df_analise.empty else None
            menor_percentual = df_analise[df_analise['Percentual'] == valor_min].iloc[0].copy() if not df_analise.empty else None
        
        # Verificar se encontramos estados válidos
        if maior_percentual is None or menor_percentual is None:
            print("Não foi possível identificar estados com valores extremos")
            return _criar_resultado_regional_vazio()
        
        # Calcular percentil 75 e 25 para identificar estados acima/abaixo da média
        percentil_75 = df_analise['Percentual'].quantile(0.75)
        percentil_25 = df_analise['Percentual'].quantile(0.25)
        
        # Identificar estados acima do percentil 75 e abaixo do 25
        estados_acima = df_analise[df_analise['Percentual'] >= percentil_75]
        estados_abaixo = df_analise[df_analise['Percentual'] <= percentil_25]
        
        # Verificar a magnitude da variabilidade
        if coef_variacao < LIMITE_VARIABILIDADE_BAIXA:
            variabilidade = "Baixa variabilidade, indicando relativa homogeneidade regional"
        elif coef_variacao < LIMITE_VARIABILIDADE_MODERADA:
            variabilidade = "Variabilidade moderada, sugerindo diferenças regionais significativas"
        else:
            variabilidade = "Alta variabilidade, mostrando importantes disparidades regionais"
        
        # Calcular o índice de Gini para desigualdade regional
        try:
            # Ordenar valores para cálculo do Gini
            valores_ordenados = sorted(df_analise['Percentual'])
            n = len(valores_ordenados)
            
            # Verificar se temos valores suficientes
            if n <= 1:
                indice_gini = 0
            else:
                # Cálculo do índice de Gini
                idx = np.arange(1, n + 1)
                s = np.sum(idx * valores_ordenados)
                indice_gini = 2 * s / (n * np.sum(valores_ordenados)) - (n + 1) / n
        except Exception as e:
            print(f"Erro ao calcular índice de Gini: {e}")
            indice_gini = 0
        
        # Retornar análise
        return {
            'percentual_medio': round(percentual_medio, 2),
            'desvio_padrao': round(desvio_padrao, 2),
            'coef_variacao': round(coef_variacao, 2),
            'amplitude': round(amplitude, 2),
            'amplitude_percentual': round(amplitude_percentual, 2),
            'maior_percentual': maior_percentual,
            'menor_percentual': menor_percentual,
            'variabilidade': variabilidade,
            'estados_acima': estados_acima,
            'estados_abaixo': estados_abaixo,
            'indice_gini': round(indice_gini, 3),
            'disparidade': _classificar_disparidade_regional(coef_variacao, amplitude_percentual)
        }
    
    except Exception as e:
        print(f"Erro ao analisar distribuição regional: {e}")
        return _criar_resultado_regional_vazio(f"Erro: {str(e)}")


def _classificar_disparidade_regional(
    coef_variacao: float, 
    amplitude_percentual: float
) -> str:
    """
    Classifica o nível de disparidade regional.
    
    Parâmetros:
    -----------
    coef_variacao : float
        Coeficiente de variação (%)
    amplitude_percentual : float
        Amplitude percentual entre maior e menor valor (%)
        
    Retorna:
    --------
    str: Classificação da disparidade regional
    """
    # Combinar dois indicadores para uma classificação mais robusta
    if coef_variacao < LIMITE_VARIABILIDADE_BAIXA and amplitude_percentual < 20:
        return "mínima"
    elif coef_variacao < LIMITE_VARIABILIDADE_MODERADA and amplitude_percentual < 50:
        return "baixa"
    elif coef_variacao < 40 and amplitude_percentual < 100:
        return "moderada"
    elif coef_variacao < 60 and amplitude_percentual < 200:
        return "significativa"
    else:
        return "extrema"


def _criar_resultado_regional_vazio(motivo: str = "Dados insuficientes") -> Dict[str, Any]:
    """
    Cria um resultado regional vazio para casos onde não há dados suficientes.
    
    Parâmetros:
    -----------
    motivo : str, default="Dados insuficientes"
        Motivo pelo qual não foi possível realizar a análise
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão
    """
    return {
        'percentual_medio': 0,
        'desvio_padrao': 0,
        'coef_variacao': 0,
        'amplitude': 0,
        'amplitude_percentual': 0,
        'maior_percentual': None,
        'menor_percentual': None,
        'variabilidade': motivo,
        'estados_acima': pd.DataFrame(),
        'estados_abaixo': pd.DataFrame(),
        'indice_gini': 0,
        'disparidade': "indefinida"
    }


@optimized_cache(ttl=1800)
def calcular_estatisticas_por_categoria(
    df_por_estado: pd.DataFrame
) -> Dict[str, Dict[str, Any]]:
    """
    Calcula estatísticas agregadas para cada categoria em todos os estados.
    
    Parâmetros:
    -----------
    df_por_estado : DataFrame
        DataFrame com dados por estado e categoria
        
    Retorna:
    --------
    Dict[str, Dict[str, Any]]
        Dicionário com estatísticas por categoria
    """
    # Verificar se temos dados válidos
    if df_por_estado is None or df_por_estado.empty:
        return {}
    
    # Verificar se temos as colunas necessárias
    colunas_necessarias = ['Estado', 'Categoria', 'Percentual']
    if not all(col in df_por_estado.columns for col in colunas_necessarias):
        print(f"Colunas necessárias não encontradas. Disponíveis: {df_por_estado.columns.tolist()}")
        return {}
    
    try:
        # Obter lista única de categorias
        categorias = df_por_estado['Categoria'].unique()
        
        # Dicionário para armazenar resultados
        resultados = {}
        
        # Calcular estatísticas para cada categoria
        for categoria in categorias:
            df_categoria = df_por_estado[df_por_estado['Categoria'] == categoria]
            
            # Verificar se temos dados suficientes
            if len(df_categoria) < 3:  # Mínimo de 3 estados
                continue
                
            # Calcular estatísticas
            percentual_medio = df_categoria['Percentual'].mean()
            desvio_padrao = df_categoria['Percentual'].std()
            coef_variacao = (desvio_padrao / percentual_medio * 100) if percentual_medio > 0 else 0
            
            # Armazenar resultados
            resultados[categoria] = {
                'percentual_medio': round(percentual_medio, 2),
                'desvio_padrao': round(desvio_padrao, 2),
                'coef_variacao': round(coef_variacao, 2),
                'n_estados': len(df_categoria),
                'min': round(df_categoria['Percentual'].min(), 2),
                'max': round(df_categoria['Percentual'].max(), 2),
                'amplitude': round(df_categoria['Percentual'].max() - df_categoria['Percentual'].min(), 2)
            }
        
        return resultados
    
    except Exception as e:
        print(f"Erro ao calcular estatísticas por categoria: {e}")
        return {}


@memory_intensive_function
def analisar_tendencias_temporais(
    df_historico: pd.DataFrame, 
    aspecto_social: str, 
    categoria: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analisa tendências temporais de um aspecto social.
    
    Parâmetros:
    -----------
    df_historico : DataFrame
        DataFrame com dados históricos
    aspecto_social : str
        Nome do aspecto social analisado
    categoria : str, opcional
        Categoria específica para análise
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com análise de tendências
    """
    # Verificar se temos dados válidos
    if df_historico is None or df_historico.empty:
        return {'tendencia': 'indefinida', 'mensagem': 'Dados históricos insuficientes'}
    
    # Verificar se temos as colunas necessárias
    colunas_necessarias = ['Ano', 'Categoria', 'Percentual']
    if not all(col in df_historico.columns for col in colunas_necessarias):
        return {'tendencia': 'indefinida', 'mensagem': 'Colunas necessárias não encontradas'}
    
    try:
        # Filtrar para uma categoria específica se solicitado
        if categoria:
            df_analise = df_historico[df_historico['Categoria'] == categoria].copy()
        else:
            # Se não houver categoria específica, usamos todo o dataframe
            df_analise = df_historico.copy()
        
        # Verificar se temos pontos suficientes para análise de tendência
        if len(df_analise) < 3:  # Mínimo de 3 pontos temporais
            return {'tendencia': 'indefinida', 'mensagem': 'Pontos temporais insuficientes'}
        
        # Ordenar por ano
        df_analise = df_analise.sort_values('Ano')
        
        # Calcular tendência linear
        x = df_analise['Ano'].astype(float)
        y = df_analise['Percentual']
        
        # Ajustar linha de tendência
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Determinar direção da tendência
        if abs(slope) < 0.01:  # Limiar para considerar estabilidade
            direcao = "estável"
        elif slope > 0:
            direcao = "crescente"
        else:
            direcao = "decrescente"
        
        # Determinar intensidade da tendência
        r_squared = r_value**2
        if r_squared < 0.3:
            intensidade = "fraca"
        elif r_squared < 0.7:
            intensidade = "moderada"
        else:
            intensidade = "forte"
        
        # Calcular variação percentual entre primeiro e último período
        primeiro = df_analise.iloc[0]['Percentual']
        ultimo = df_analise.iloc[-1]['Percentual']
        variacao_percentual = ((ultimo - primeiro) / primeiro * 100) if primeiro > 0 else 0
        
        # Construir mensagem descritiva
        if abs(variacao_percentual) < 5:
            descricao = f"Manteve-se relativamente estável ao longo do período analisado"
        elif variacao_percentual > 0:
            descricao = f"Aumentou {abs(variacao_percentual):.1f}% ao longo do período analisado"
        else:
            descricao = f"Diminuiu {abs(variacao_percentual):.1f}% ao longo do período analisado"
        
        # Retornar análise de tendência
        return {
            'tendencia': f"{direcao} {intensidade}",
            'slope': round(slope, 4),
            'r_squared': round(r_squared, 3),
            'p_value': round(p_value, 4),
            'significativa': p_value < 0.05,
            'variacao_percentual': round(variacao_percentual, 2),
            'primeiro_valor': round(primeiro, 2),
            'ultimo_valor': round(ultimo, 2),
            'descricao': descricao,
            'mensagem': f"Tendência {direcao} {intensidade} (R² = {r_squared:.2f})"
        }
    
    except Exception as e:
        print(f"Erro ao analisar tendências temporais: {e}")
        return {'tendencia': 'erro', 'mensagem': f'Erro na análise: {str(e)}'}


def _calcular_distribuicao_sem_instancia(contagem_aspecto: pd.DataFrame) -> Dict[str, Any]:
    """
    Implementa cálculo de distribuição sem usar instâncias de classe.
    Compatível com cache do Streamlit.
    """
    try:
        if contagem_aspecto.empty or 'Quantidade' not in contagem_aspecto.columns:
            return _criar_estatisticas_distribuicao_vazias()
        
        quantities = contagem_aspecto['Quantidade']
        total = quantities.sum()
        
        if total <= 0:
            return _criar_estatisticas_distribuicao_vazias()
        
        # Estatísticas básicas
        max_idx = quantities.idxmax()
        min_idx = quantities.idxmin()
        
        most_frequent = contagem_aspecto.loc[max_idx] if max_idx in contagem_aspecto.index else None
        least_frequent = contagem_aspecto.loc[min_idx] if min_idx in contagem_aspecto.index else None
        
        # Estatísticas de concentração
        proportions = quantities / total
        gini_coefficient = _calculate_gini_coefficient(proportions)
        
        # Estatísticas de variabilidade
        mean_val = quantities.mean()
        median_val = quantities.median()
        std_val = quantities.std()
        cv = (std_val / mean_val * 100) if mean_val > 0 else 0
        
        # Classificação de concentração baseada no coeficiente de Gini
        if gini_coefficient < 0.2:
            concentracao_class = "Distribuição equilibrada"
        elif gini_coefficient < 0.4:
            concentracao_class = "Concentração moderada"
        elif gini_coefficient < 0.6:
            concentracao_class = "Concentração alta"
        else:
            concentracao_class = "Concentração muito alta"
        
        return {
            'total': int(total),
            'categoria_mais_frequente': most_frequent,
            'categoria_menos_frequente': least_frequent,
            'num_categorias': len(contagem_aspecto),
            'media': round(mean_val, 2),
            'mediana': round(median_val, 2),
            'desvio_padrao': round(std_val, 2),
            'coef_variacao': round(cv, 2),
            'indice_concentracao': round(gini_coefficient, 4),
            'classificacao_concentracao': concentracao_class,
            'entropia': 0,  # Pode ser implementado depois se necessário
            'entropia_normalizada': 0,  # Pode ser implementado depois se necessário
            'razao_max_min': round(quantities.max() / quantities.min() if quantities.min() > 0 else 0, 2)
        }
        
    except Exception as e:
        print(f"Erro em _calcular_distribuicao_sem_instancia: {e}")
        return _criar_estatisticas_distribuicao_vazias()


def _analisar_correlacao_sem_instancia(df_correlacao: pd.DataFrame, var_x: str, var_y: str) -> Dict[str, Any]:
    """
    Implementa análise de correlação sem usar instâncias de classe.
    Compatível com cache do Streamlit.
    """
    try:
        if df_correlacao.empty or var_x not in df_correlacao.columns or var_y not in df_correlacao.columns:
            return _criar_correlacao_vazia()
        
        # Limpar dados
        clean_data = df_correlacao.dropna(subset=[var_x, var_y])
        
        if len(clean_data) < 10:  # Mínimo para análise estatística confiável
            return _criar_correlacao_vazia()
        
        # Criar tabela de contingência
        contingency_table = pd.crosstab(clean_data[var_x], clean_data[var_y])
        
        if contingency_table.empty or contingency_table.sum().sum() < 10:
            return _criar_correlacao_vazia()
        
        # Calcular qui-quadrado
        if chi2_contingency is not None:
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        else:
            # Fallback simples se scipy não estiver disponível
            chi2, p_value, dof = _calculate_chi_square_basic(contingency_table)
            
        # Calcular V de Cramér
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if chi2 > 0 and min_dim > 0 else 0
        
        # Interpretação
        if p_value < 0.001:
            significance = "Muito Significante (p < 0.001)"
        elif p_value < 0.01:
            significance = "Significante (p < 0.01)"
        elif p_value < 0.05:
            significance = "Moderadamente Significante (p < 0.05)"
        else:
            significance = "Não Significante (p ≥ 0.05)"
        
        interpretation = _interpretar_v_cramer(cramers_v)
        tamanho_efeito = _classificar_tamanho_efeito(cramers_v)
        
        # Calcular informação mútua normalizada (versão básica)
        info_mutua_norm = min(cramers_v * 2, 1.0)  # Aproximação básica
        
        return {
            'qui_quadrado': round(chi2, 4),
            'valor_p': round(p_value, 6),
            'gl': int(dof),
            'v_cramer': round(cramers_v, 4),
            'coeficiente': round(cramers_v, 4),  # Alias para compatibilidade
            'n_amostras': int(n),
            'significativo': p_value < 0.05,
            'interpretacao': interpretation,
            'tamanho_efeito': tamanho_efeito,
            'tabela_contingencia': contingency_table,
            'info_mutua_norm': round(info_mutua_norm, 4)
        }
        
    except Exception as e:
        print(f"Erro em _analisar_correlacao_sem_instancia: {e}")
        return _criar_correlacao_vazia()


def _calculate_gini_coefficient(data: pd.Series) -> float:
    """Calcula coeficiente de Gini para uma série de dados."""
    try:
        sorted_data = np.sort(data)
        n = len(sorted_data)
        cumsum = np.cumsum(sorted_data)
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] > 0 else 0
    except:
        return 0.0


def _criar_correlacao_vazia() -> Dict[str, Any]:
    """Cria resultado de correlação vazio."""
    return {
        'qui_quadrado': 0.0,
        'valor_p': 1.0,
        'gl': 0,
        'v_cramer': 0.0,
        'coeficiente': 0.0,  # Alias para compatibilidade
        'n_amostras': 0,
        'significativo': False,
        'interpretacao': "Dados insuficientes para análise",
        'tamanho_efeito': 'indeterminado',
        'tabela_contingencia': pd.DataFrame(),
        'info_mutua_norm': 0.0
    }

# ============================================================================
# FUNÇÕES PARA COMPATIBILIDADE COM EXPANDERS
# ============================================================================

@optimized_cache(ttl=1800)
def analisar_distribuicao_regional(
    df_por_estado: pd.DataFrame, 
    aspecto_social: str, 
    categoria_selecionada: str
) -> Dict[str, Any]:
    """
    Analisa a distribuição regional de uma categoria específica de aspecto social.
    REFATORADO: Função livre de instâncias para compatibilidade com cache Streamlit.
    
    Parâmetros:
    -----------
    df_por_estado : DataFrame
        DataFrame com dados por estado
    aspecto_social : str
        Código do aspecto social
    categoria_selecionada : str
        Categoria selecionada para análise
        
    Retorna:
    --------
    Dict[str, Any]: Análise da distribuição regional
    """
    try:
        # Validar entrada
        if df_por_estado is None or df_por_estado.empty:
            return _criar_resultado_regional_vazio("DataFrame vazio")
        
        # Filtrar dados para a categoria selecionada
        df_categoria = df_por_estado[df_por_estado['Categoria'] == categoria_selecionada]
        
        if df_categoria.empty:
            return _criar_resultado_regional_vazio("Categoria não encontrada")
        
        # Calcular estatísticas
        percentuais = df_categoria['Percentual'].dropna()
        
        if len(percentuais) == 0:
            return _criar_resultado_regional_vazio("Sem dados de percentual")
        
        media = percentuais.mean()
        desvio = percentuais.std()
        coef_var = (desvio / media * 100) if media > 0 else 0
        
        # Encontrar extremos
        idx_max = percentuais.idxmax()
        idx_min = percentuais.idxmin()
        
        maior_percentual = df_categoria.loc[idx_max] if idx_max in df_categoria.index else None
        menor_percentual = df_categoria.loc[idx_min] if idx_min in df_categoria.index else None
        
        # Classificar variabilidade
        if coef_var < LIMITE_VARIABILIDADE_BAIXA:
            variabilidade = "baixa"
            disparidade = "baixa"
        elif coef_var < LIMITE_VARIABILIDADE_MODERADA:
            variabilidade = "moderada"
            disparidade = "moderada"
        else:
            variabilidade = "alta"
            disparidade = "alta"
        
        # Calcular amplitude
        amplitude = percentuais.max() - percentuais.min()
        
        # Calcular índice de Gini aproximado
        indice_gini = _calculate_gini_coefficient(percentuais)
        
        return {
            'percentual_medio': float(media),
            'desvio_padrao': float(desvio),
            'coef_variacao': float(coef_var),
            'amplitude': float(amplitude),
            'variabilidade': variabilidade,
            'disparidade': disparidade,
            'maior_percentual': maior_percentual,
            'menor_percentual': menor_percentual,
            'indice_gini': float(indice_gini),
            'n_localidades': len(percentuais)
        }
        
    except Exception as e:
        print(f"Erro em analisar_distribuicao_regional: {e}")
        return _criar_resultado_regional_vazio(f"Erro: {str(e)}")


@optimized_cache(ttl=1800)
def calcular_estatisticas_por_categoria(
    df: pd.DataFrame, 
    aspecto_social: str
) -> Dict[str, Any]:
    """
    Calcula estatísticas por categoria de um aspecto social.
    REFATORADO: Função livre de instâncias para compatibilidade com cache Streamlit.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    aspecto_social : str
        Código do aspecto social
        
    Retorna:
    --------
    Dict[str, Any]: Estatísticas por categoria
    """
    try:
        # Validar entrada
        if df is None or df.empty:
            return _criar_resultado_categoria_vazio("DataFrame vazio")
        
        if aspecto_social not in df.columns:
            return _criar_resultado_categoria_vazio("Aspecto social não encontrado")
        
        # Contar categorias
        contagem = df[aspecto_social].value_counts().reset_index()
        contagem.columns = ['Categoria', 'Quantidade']
        
        # Calcular percentuais
        total = contagem['Quantidade'].sum()
        contagem['Percentual'] = (contagem['Quantidade'] / total * 100)
        
        # Calcular estatísticas
        return calcular_estatisticas_distribuicao(contagem)
        
    except Exception as e:
        print(f"Erro em calcular_estatisticas_por_categoria: {e}")
        return _criar_resultado_categoria_vazio(f"Erro: {str(e)}")


def _calculate_chi_square_basic(contingency_table: pd.DataFrame) -> Tuple[float, float, int]:
    """
    Implementação básica do teste qui-quadrado quando scipy não está disponível.
    
    Parâmetros:
    -----------
    contingency_table : DataFrame
        Tabela de contingência
        
    Retorna:
    --------
    Tuple[float, float, int]: Chi-quadrado, p-valor aproximado, graus de liberdade
    """
    try:
        # Calcular totais marginais
        row_totals = contingency_table.sum(axis=1)
        col_totals = contingency_table.sum(axis=0)
        grand_total = contingency_table.sum().sum()
        
        # Calcular frequências esperadas
        chi2 = 0.0
        for i in contingency_table.index:
            for j in contingency_table.columns:
                observed = contingency_table.loc[i, j]
                expected = (row_totals[i] * col_totals[j]) / grand_total
                if expected > 0:
                    chi2 += ((observed - expected) ** 2) / expected
        
        # Graus de liberdade
        dof = (len(contingency_table.index) - 1) * (len(contingency_table.columns) - 1)
        
        # P-valor aproximado (muito básico)
        p_value = 0.05 if chi2 > 3.841 else 0.1  # Aproximação grosseira
        
        return chi2, p_value, dof
        
    except Exception:
        return 0.0, 1.0, 0


def _criar_resultado_regional_vazio(motivo: str = "Dados insuficientes") -> Dict[str, Any]:
    """
    Cria um resultado de análise regional vazio.
    
    Parâmetros:
    -----------
    motivo : str
        Motivo pelo qual não foi possível calcular
        
    Retorna:
    --------
    Dict[str, Any]: Resultado vazio
    """
    return {
        'percentual_medio': 0.0,
        'desvio_padrao': 0.0,
        'coef_variacao': 0.0,
        'amplitude': 0.0,
        'variabilidade': 'indeterminada',
        'disparidade': 'indeterminada',
        'maior_percentual': None,
        'menor_percentual': None,
        'indice_gini': 0.0,
        'n_localidades': 0,
        'motivo': motivo
    }


def _criar_resultado_categoria_vazio(motivo: str = "Dados insuficientes") -> Dict[str, Any]:
    """
    Cria um resultado de estatísticas por categoria vazio.
    
    Parâmetros:
    -----------
    motivo : str
        Motivo pelo qual não foi possível calcular
        
    Retorna:
    --------
    Dict[str, Any]: Resultado vazio
    """
    return {
        'total': 0,
        'num_categorias': 0,
        'categoria_mais_frequente': None,
        'categoria_menos_frequente': None,
        'media': 0.0,
        'mediana': 0.0,
        'desvio_padrao': 0.0,
        'coef_variacao': 0.0,
        'indice_concentracao': 0.0,
        'classificacao_concentracao': 'indeterminada',
        'motivo': motivo
    }