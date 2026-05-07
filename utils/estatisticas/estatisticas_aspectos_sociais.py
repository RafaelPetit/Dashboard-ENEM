import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from scipy.stats import chi2_contingency
from utils.helpers.cache_utils import optimized_cache
from utils.helpers.constants import LIMIARES_ESTATISTICOS, LIMIARES_PROCESSAMENTO

# Constantes para classificação de variabilidade
LIMITE_VARIABILIDADE_BAIXA = LIMIARES_ESTATISTICOS.get('variabilidade_baixa', 15)
LIMITE_VARIABILIDADE_MODERADA = LIMIARES_ESTATISTICOS.get('variabilidade_moderada', 30)

# Constantes para classificação de correlação
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS.get('correlacao_fraca', 0.3)
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS.get('correlacao_moderada', 0.7)
LIMITE_CORRELACAO_FORTE = 0.8  # Valor padrão para correlação forte


def _calcular_gini(valores) -> float:
    """Calcula o coeficiente de Gini para uma série de valores (formula unificada P3.6)."""
    try:
        arr = np.sort(np.asarray(valores, dtype=float))
        n = len(arr)
        if n <= 1 or np.sum(arr) == 0:
            return 0.0
        index = np.arange(1, n + 1)
        return float((np.sum((2 * index - n - 1) * arr)) / (n * np.sum(arr)))
    except Exception:
        return 0.0


@optimized_cache(ttl=1800)
def calcular_estatisticas_distribuicao(
    contagem_aspecto: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calcula estatísticas básicas sobre a distribuição de um aspecto social.
    """
    if contagem_aspecto is None or contagem_aspecto.empty or 'Quantidade' not in contagem_aspecto.columns:
        return _criar_estatisticas_distribuicao_vazias()

    try:
        total = contagem_aspecto['Quantidade'].sum()
        if total <= 0:
            return _criar_estatisticas_distribuicao_vazias()

        proporcoes = contagem_aspecto['Quantidade'] / total

        # Métricas de tendência central e dispersão
        metricas_basicas = _calcular_metricas_basicas_distribuicao(contagem_aspecto, proporcoes, total)

        # Métricas de concentração e desigualdade
        metricas_concentracao = _calcular_metricas_concentracao(proporcoes, contagem_aspecto)

        # Categorias extremas
        idx_max = contagem_aspecto['Quantidade'].idxmax()
        idx_min = contagem_aspecto['Quantidade'].idxmin()

        return {
            'total': int(total),
            'categoria_mais_frequente': contagem_aspecto.loc[idx_max] if idx_max in contagem_aspecto.index else None,
            'categoria_menos_frequente': contagem_aspecto.loc[idx_min] if idx_min in contagem_aspecto.index else None,
            'num_categorias': len(contagem_aspecto),
            **metricas_basicas,
            **metricas_concentracao,
        }

    except Exception as e:
        logging.warning(f"Erro em calcular_estatisticas_distribuicao: {e}")
        return _criar_estatisticas_distribuicao_vazias()


def _calcular_metricas_basicas_distribuicao(
    contagem: pd.DataFrame, proporcoes: pd.Series, total: int
) -> Dict[str, float]:
    """Calcula média, mediana, moda, dispersão e percentis."""
    media = proporcoes.mean() * 100
    mediana = proporcoes.median() * 100
    desvio_padrao = proporcoes.std() * 100
    amplitude = (proporcoes.max() - proporcoes.min()) * 100
    coef_variacao = (desvio_padrao / media * 100) if media > 0 else 0

    try:
        idx_moda = contagem['Quantidade'].idxmax()
        moda = (contagem.loc[idx_moda, 'Quantidade'] / total) * 100
    except Exception:
        moda = 0.0

    max_q = contagem['Quantidade'].max()
    min_q = contagem['Quantidade'].min()

    return {
        'media': round(media, 2),
        'mediana': round(mediana, 2),
        'moda': round(moda, 2),
        'desvio_padrao': round(desvio_padrao, 2),
        'amplitude': round(amplitude, 2),
        'coef_variacao': round(coef_variacao, 2),
        'razao_max_min': round((max_q / min_q) if min_q > 0 else 0, 2),
        'percentil_25': round(proporcoes.quantile(0.25) * 100, 2),
        'percentil_75': round(proporcoes.quantile(0.75) * 100, 2),
        'percentil_90': round(proporcoes.quantile(0.90) * 100, 2),
    }


def _calcular_metricas_concentracao(proporcoes: pd.Series, contagem: pd.DataFrame) -> Dict[str, Any]:
    """Calcula índice de concentração (HHI), entropia e Gini."""
    # HHI invertido
    if proporcoes.empty or proporcoes.isna().any():
        indice_concentracao = 0.0
    else:
        indice_concentracao = 1 - (proporcoes ** 2).sum()

    # Entropia
    proporcoes_validas = proporcoes[proporcoes > 0]
    entropia = -np.sum(proporcoes_validas * np.log2(proporcoes_validas)) if len(proporcoes_validas) > 0 else 0
    entropia_normalizada = entropia / np.log2(len(proporcoes_validas)) if len(proporcoes_validas) > 1 else 0

    # Gini (funcao unificada P3.6)
    indice_gini = _calcular_gini(proporcoes.values)

    # Classificação
    if indice_concentracao < 0.2:
        classificacao = "Distribuição muito homogênea"
    elif indice_concentracao < 0.4:
        classificacao = "Distribuição relativamente homogênea"
    elif indice_concentracao < 0.6:
        classificacao = "Distribuição moderadamente concentrada"
    elif indice_concentracao < 0.8:
        classificacao = "Distribuição concentrada"
    else:
        classificacao = "Distribuição muito concentrada"

    return {
        'indice_concentracao': round(float(indice_concentracao), 3),
        'classificacao_concentracao': classificacao,
        'entropia': round(float(entropia), 3),
        'entropia_normalizada': round(float(entropia_normalizada), 3),
        'indice_gini': round(float(indice_gini), 3),
    }


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


@optimized_cache(ttl=1800)
def analisar_correlacao_categorias(
    df_correlacao: pd.DataFrame, 
    var_x_plot: str, 
    var_y_plot: str
) -> Dict[str, Any]:
    """
    Analisa a correlação entre duas variáveis categóricas.
    
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
    # Verificar se temos dados válidos
    if df_correlacao is None or df_correlacao.empty:
        return _criar_resultado_correlacao_vazio()
    
    # Verificar se as variáveis existem no DataFrame
    if var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        return _criar_resultado_correlacao_vazio()
    
    # Verificar se temos amostras suficientes
    min_amostras = LIMIARES_PROCESSAMENTO.get('min_amostras_correlacao', 100)
    if len(df_correlacao) < min_amostras:
        return _criar_resultado_correlacao_vazio('Amostras insuficientes')
    
    try:
        # Remover valores ausentes
        df_valido = df_correlacao.dropna(subset=[var_x_plot, var_y_plot])
        
        # Verificar se ainda temos dados suficientes após a limpeza
        if len(df_valido) < min_amostras:
            return _criar_resultado_correlacao_vazio('Amostras insuficientes após limpeza')
        
        # Criar tabela de contingência
        tabela_contingencia = pd.crosstab(df_valido[var_x_plot], df_valido[var_y_plot])
        
        # Verificar se a tabela tem dimensões suficientes
        if tabela_contingencia.shape[0] <= 1 or tabela_contingencia.shape[1] <= 1:
            return _criar_resultado_correlacao_vazio('Categorias insuficientes')
        
        # Calcular metricas de associacao (extraido em P3.15)
        n = tabela_contingencia.sum().sum()
        chi2, p_valor, gl, coef_normalizado, v_cramer = _calcular_metricas_associacao(tabela_contingencia, n)

        # Interpretar resultados
        interpretacao = _interpretar_correlacao_categorias(coef_normalizado)
        contexto = _interpretar_v_cramer(v_cramer)
        significativo = p_valor < 0.05
        tamanho_efeito = _classificar_tamanho_efeito(v_cramer)

        # Calcular informação mútua (extraido em P3.15)
        mi, mi_normalizado = _calcular_informacao_mutua(tabela_contingencia, n)

        # Retornar métricas com nomes padronizados
        return {
            'qui_quadrado': round(chi2, 2),
            'gl': gl,
            'valor_p': round(p_valor, 4),
            'coeficiente': round(coef_normalizado, 3),
            'v_cramer': round(v_cramer, 3),
            'info_mutua': round(mi, 3),
            'info_mutua_norm': round(mi_normalizado, 3),
            'interpretacao': interpretacao,
            'contexto': contexto,
            'significativo': significativo,
            'tamanho_efeito': tamanho_efeito,
            'tabela_contingencia': tabela_contingencia,
            'n_amostras': int(n)
        }
    
    except Exception as e:
        logging.warning(f"Erro em analisar_correlacao_categorias: {e}")
        return _criar_resultado_correlacao_vazio(f"Erro: {str(e)}")


def _calcular_metricas_associacao(tabela_contingencia: pd.DataFrame, n: int) -> tuple:
    """Calcula chi-quadrado, coeficiente de contingencia normalizado e V de Cramer (fix P3.15)."""
    chi2, p_valor, gl, _ = chi2_contingency(tabela_contingencia)
    coef_contingencia = np.sqrt(chi2 / (chi2 + n))
    k = min(len(tabela_contingencia), len(tabela_contingencia.columns))
    c_max = np.sqrt((k - 1) / k)
    coef_normalizado = coef_contingencia / c_max if c_max > 0 else 0
    v_cramer = np.sqrt(chi2 / (n * min(tabela_contingencia.shape[0] - 1, tabela_contingencia.shape[1] - 1)))
    # Validar resultados finitos
    if not all(np.isfinite([chi2, p_valor, coef_normalizado, v_cramer])):
        chi2 = chi2 if np.isfinite(chi2) else 0
        p_valor = p_valor if np.isfinite(p_valor) else 1
        coef_normalizado = coef_normalizado if np.isfinite(coef_normalizado) else 0
        v_cramer = v_cramer if np.isfinite(v_cramer) else 0
    return chi2, p_valor, gl, coef_normalizado, v_cramer


def _calcular_informacao_mutua(tabela_contingencia: pd.DataFrame, n: int) -> tuple:
    """Calcula informacao mutua e sua versao normalizada a partir da tabela de contingencia (fix P3.15)."""
    p_x = tabela_contingencia.sum(axis=1) / n
    p_y = tabela_contingencia.sum(axis=0) / n
    H_x = -np.sum(p_x * np.log2(p_x + 1e-10))
    H_y = -np.sum(p_y * np.log2(p_y + 1e-10))
    H_max = min(H_x, H_y)

    # Usar mascara conjunta para manter arrays alinhados (fix P1.4)
    p_xy = tabela_contingencia.values.flatten() / n
    p_x_rep = np.repeat(p_x.values, len(p_y))
    p_y_rep = np.tile(p_y.values, len(p_x))
    mask_pos = p_xy > 0
    mi = np.sum(p_xy[mask_pos] * np.log2(p_xy[mask_pos] / (p_x_rep[mask_pos] * p_y_rep[mask_pos])))
    mi_normalizado = mi / H_max if H_max > 0 else 0
    return float(mi), float(mi_normalizado)


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
        return _criar_resultado_regional_vazio()
    
    try:
        # Filtrar para uma categoria específica se solicitado
        if categoria:
            df_analise = df_por_estado[df_por_estado['Categoria'] == categoria]
            
            # Verificar se a categoria existe nos dados
            if df_analise.empty:
                return _criar_resultado_regional_vazio()
        else:
            # Se não houver categoria específica, usamos todo o dataframe
            df_analise = df_por_estado
        
        # Verificar se temos dados para análise
        if df_analise.empty or len(df_analise) < 3:  # Mínimo de 3 estados para análise significativa
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
            
            maior_percentual = df_analise.loc[idx_max] if idx_max in df_analise.index else None
            menor_percentual = df_analise.loc[idx_min] if idx_min in df_analise.index else None
        except (KeyError, ValueError):
            # Fallback se idxmax/idxmin falhar
            maior_percentual = df_analise[df_analise['Percentual'] == valor_max].iloc[0] if not df_analise.empty else None
            menor_percentual = df_analise[df_analise['Percentual'] == valor_min].iloc[0] if not df_analise.empty else None
        
        # Verificar se encontramos estados válidos
        if maior_percentual is None or menor_percentual is None:
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
        
        # Calcular o índice de Gini para desigualdade regional (funcao unificada P3.6)
        indice_gini = _calcular_gini(df_analise['Percentual'].values)
        
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
        logging.warning(f"Erro em analisar_distribuicao_regional: {e}")
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
