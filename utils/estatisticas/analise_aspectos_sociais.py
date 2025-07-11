import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from scipy.stats import chi2_contingency
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function
from utils.mappings import get_mappings

# Obter limiares para análise estatística dos mapeamentos centralizados
mappings = get_mappings()
LIMIARES_ESTATISTICOS = mappings.get('limiares_estatisticos', {})
LIMIARES_PROCESSAMENTO = mappings.get('limiares_processamento', {})

# Constantes para classificação de variabilidade
LIMITE_VARIABILIDADE_BAIXA = LIMIARES_ESTATISTICOS.get('variabilidade_baixa', 15)
LIMITE_VARIABILIDADE_MODERADA = LIMIARES_ESTATISTICOS.get('variabilidade_moderada', 30)

# Constantes para classificação de correlação
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS.get('correlacao_fraca', 0.3)
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS.get('correlacao_moderada', 0.7)
LIMITE_CORRELACAO_FORTE = 0.8  # Valor padrão para correlação forte

@optimized_cache(ttl=1800)
def calcular_estatisticas_distribuicao(
    contagem_aspecto: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calcula estatísticas básicas sobre a distribuição de um aspecto social.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com a contagem de ocorrências por categoria
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com estatísticas calculadas
    """
    # Verificar se temos dados válidos
    if contagem_aspecto is None or contagem_aspecto.empty or 'Quantidade' not in contagem_aspecto.columns:
        return _criar_estatisticas_distribuicao_vazias()
        
    try:
        # Calcular total
        total = contagem_aspecto['Quantidade'].sum()
        
        # Verificar se temos um total válido
        if total <= 0:
            return _criar_estatisticas_distribuicao_vazias()
        
        # Encontrar categorias com maior e menor quantidade (forma segura)
        try:
            idx_max = contagem_aspecto['Quantidade'].idxmax()
            idx_min = contagem_aspecto['Quantidade'].idxmin()
            
            categoria_mais_frequente = contagem_aspecto.loc[idx_max].copy() if idx_max in contagem_aspecto.index else None
            categoria_menos_frequente = contagem_aspecto.loc[idx_min].copy() if idx_min in contagem_aspecto.index else None
        except (KeyError, ValueError):
            # Fallback se idxmax/idxmin falhar
            max_valor = contagem_aspecto['Quantidade'].max()
            min_valor = contagem_aspecto['Quantidade'].min()
            
            categoria_mais_frequente = contagem_aspecto[contagem_aspecto['Quantidade'] == max_valor].iloc[0].copy() if max_valor > 0 else None
            categoria_menos_frequente = contagem_aspecto[contagem_aspecto['Quantidade'] == min_valor].iloc[0].copy() if min_valor > 0 else None
        
        # Verificar se encontramos categorias válidas
        if categoria_mais_frequente is None or categoria_menos_frequente is None:
            return _criar_estatisticas_distribuicao_vazias()
        
        # Calcular média e mediana
        media = contagem_aspecto['Quantidade'].mean()
        mediana = contagem_aspecto['Quantidade'].median()
        
        # Calcular o índice de concentração (Gini simplificado)
        proporcoes = contagem_aspecto['Quantidade'] / total
        
        # Verificar se temos proporcões válidas
        if proporcoes.empty or proporcoes.isna().any():
            indice_concentracao = 0
        else:
            # Quanto mais próximo de 1, mais desigual a distribuição
            indice_concentracao = 1 - (1 / len(contagem_aspecto)) * (proporcoes**2).sum() * len(contagem_aspecto)
            
            # Verificar se o índice é um número válido
            if not np.isfinite(indice_concentracao):
                indice_concentracao = 0
        
        # Calcular a entropia (medida de dispersão)
        try:
            # Proporcões devem ser não-negativas e somar 1
            proporcoes_validas = proporcoes[proporcoes > 0]
            entropia = -np.sum(proporcoes_validas * np.log2(proporcoes_validas))
            entropia_normalizada = entropia / np.log2(len(proporcoes_validas)) if len(proporcoes_validas) > 0 else 0
        except Exception as e:
            print(f"Erro ao calcular entropia: {e}")
            entropia = 0
            entropia_normalizada = 0
        
        # Calcular razão entre maior e menor valor
        razao_max_min = categoria_mais_frequente['Quantidade'] / categoria_menos_frequente['Quantidade'] if categoria_menos_frequente['Quantidade'] > 0 else 0
        
        # Calcular o coeficiente de variação
        cv = (contagem_aspecto['Quantidade'].std() / media * 100) if media > 0 else 0
        
        # Classificar a distribuição
        if indice_concentracao < 0.2:
            classificacao_concentracao = "Distribuição muito homogênea"
        elif indice_concentracao < 0.4:
            classificacao_concentracao = "Distribuição relativamente homogênea"
        elif indice_concentracao < 0.6:
            classificacao_concentracao = "Distribuição moderadamente concentrada"
        elif indice_concentracao < 0.8:
            classificacao_concentracao = "Distribuição concentrada"
        else:
            classificacao_concentracao = "Distribuição muito concentrada"
        
        # Retornar estatísticas em um dicionário
        return {
            'total': int(total),
            'categoria_mais_frequente': categoria_mais_frequente,
            'categoria_menos_frequente': categoria_menos_frequente,
            'num_categorias': len(contagem_aspecto),
            'media': round(media, 2),
            'mediana': round(mediana, 2),
            'indice_concentracao': round(indice_concentracao, 3),
            'classificacao_concentracao': classificacao_concentracao,
            'entropia': round(entropia, 3),
            'entropia_normalizada': round(entropia_normalizada, 3),
            'razao_max_min': round(razao_max_min, 2),
            'coef_variacao': round(cv, 2),
            'desvio_padrao': round(contagem_aspecto['Quantidade'].std(), 2)
        }
    
    except Exception as e:
        print(f"Erro ao calcular estatísticas de distribuição: {e}")
        return _criar_estatisticas_distribuicao_vazias()


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
        print(f"Variáveis não encontradas no DataFrame: {var_x_plot}, {var_y_plot}")
        return _criar_resultado_correlacao_vazio()
    
    # Verificar se temos amostras suficientes
    min_amostras = LIMIARES_PROCESSAMENTO.get('min_amostras_correlacao', 100)
    if len(df_correlacao) < min_amostras:
        print(f"Amostras insuficientes para análise de correlação: {len(df_correlacao)} < {min_amostras}")
        return _criar_resultado_correlacao_vazio('Amostras insuficientes')
    
    try:
        # Remover valores ausentes
        df_valido = df_correlacao.dropna(subset=[var_x_plot, var_y_plot])
        
        # Verificar se ainda temos dados suficientes após a limpeza
        if len(df_valido) < min_amostras:
            print(f"Amostras insuficientes após remoção de valores ausentes: {len(df_valido)} < {min_amostras}")
            return _criar_resultado_correlacao_vazio('Amostras insuficientes após limpeza')
        
        # Criar tabela de contingência
        tabela_contingencia = pd.crosstab(df_valido[var_x_plot], df_valido[var_y_plot])
        
        # Verificar se a tabela tem dimensões suficientes
        if tabela_contingencia.shape[0] <= 1 or tabela_contingencia.shape[1] <= 1:
            print(f"Tabela de contingência inadequada: {tabela_contingencia.shape}")
            return _criar_resultado_correlacao_vazio('Categorias insuficientes')
        
        # Calcular qui-quadrado e coeficiente de contingência
        chi2, p_valor, gl, _ = chi2_contingency(tabela_contingencia)
        
        # Tamanho da amostra
        n = tabela_contingencia.sum().sum()
        
        # Calcular coeficiente de contingência
        coef_contingencia = np.sqrt(chi2 / (chi2 + n))
        
        # Valor máximo do coeficiente (para normalização)
        k = min(len(tabela_contingencia), len(tabela_contingencia.columns))
        c_max = np.sqrt((k - 1) / k)
        
        # Coeficiente normalizado
        coef_normalizado = coef_contingencia / c_max if c_max > 0 else 0
        
        # Calcular V de Cramer
        v_cramer = np.sqrt(chi2 / (n * min(tabela_contingencia.shape[0] - 1, tabela_contingencia.shape[1] - 1)))
        
        # Verificar se os resultados são números válidos
        if not all(np.isfinite([chi2, p_valor, coef_normalizado, v_cramer])):
            print("Resultados de correlação contêm valores não finitos")
            # Tentar corrigir valores inválidos
            chi2 = chi2 if np.isfinite(chi2) else 0
            p_valor = p_valor if np.isfinite(p_valor) else 1
            coef_normalizado = coef_normalizado if np.isfinite(coef_normalizado) else 0
            v_cramer = v_cramer if np.isfinite(v_cramer) else 0
        
        # Interpretar a força da associação
        interpretacao = _interpretar_correlacao_categorias(coef_normalizado)
        
        # Interpretar V de Cramer
        contexto = _interpretar_v_cramer(v_cramer)
        
        # Classificar significância estatística
        significativo = p_valor < 0.05
        
        # Calcular tamanho do efeito
        tamanho_efeito = _classificar_tamanho_efeito(v_cramer)
        
        # Calcular a incerteza máxima (para normalização)
        p_x = tabela_contingencia.sum(axis=1) / n
        p_y = tabela_contingencia.sum(axis=0) / n
        H_x = -np.sum(p_x * np.log2(p_x + 1e-10))
        H_y = -np.sum(p_y * np.log2(p_y + 1e-10))
        H_max = min(H_x, H_y)
        
        # Calcular informação mútua normalizada
        p_xy = tabela_contingencia.values.flatten() / n
        p_xy = p_xy[p_xy > 0]  # Remover zeros
        p_x_rep = np.repeat(p_x.values, len(p_y))
        p_y_rep = np.tile(p_y.values, len(p_x))
        indices_validos = p_xy > 0
        mi = np.sum(p_xy[indices_validos] * np.log2(p_xy[indices_validos] / (p_x_rep[indices_validos] * p_y_rep[indices_validos])))
        mi_normalizado = mi / H_max if H_max > 0 else 0
        
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
        print(f"Erro ao analisar correlação entre categorias: {e}")
        return _criar_resultado_correlacao_vazio(f"Erro: {str(e)}")


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