import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any, Optional, List
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function
from utils.estatisticas.metricas_desempenho import calcular_indicadores_desigualdade
from utils.mappings import get_mappings

# Obter limiares para análise estatística dos mapeamentos centralizados
mappings = get_mappings()
LIMIARES_ESTATISTICOS = mappings['limiares_estatisticos']
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS['correlacao_fraca']
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS['correlacao_moderada']

@optimized_cache(ttl=1800)
def calcular_correlacao_competencias(
    df: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str
) -> Tuple[float, str]:
    """
    Calcula a correlação entre duas competências e fornece interpretação.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame contendo os dados
    eixo_x: str
        Nome da coluna para o primeiro eixo
    eixo_y: str
        Nome da coluna para o segundo eixo
        
    Retorna:
    --------
    Tuple[float, str]: Coeficiente de correlação e interpretação textual
    """
    # Verificar se temos dados suficientes
    if df.empty or eixo_x not in df.columns or eixo_y not in df.columns:
        return 0.0, "Dados insuficientes"
    
    # Remover linhas com valores ausentes ou zero em qualquer um dos eixos
    df_valido = df[(df[eixo_x] > 0) & (df[eixo_y] > 0)].dropna(subset=[eixo_x, eixo_y])
    
    # Verificar se temos amostras suficientes para cálculo válido
    min_amostras = mappings['limiares_processamento']['min_amostras_correlacao']
    if len(df_valido) < min_amostras:
        return 0.0, f"Amostras insuficientes (n={len(df_valido)})"
    
    try:
        # Calcular correlação
        correlacao = df_valido[eixo_x].corr(df_valido[eixo_y])
        
        # Verificar se o resultado é um número válido
        if pd.isna(correlacao):
            return 0.0, "Correlação indefinida"
        
        # Interpretar valor de correlação
        interpretacao = _interpretar_correlacao(correlacao)
        
        return correlacao, interpretacao
        
    except Exception as e:
        print(f"Erro ao calcular correlação: {e}")
        return 0.0, "Erro no cálculo"


def _interpretar_correlacao(correlacao: float) -> str:
    """
    Interpreta o valor do coeficiente de correlação.
    
    Parâmetros:
    -----------
    correlacao: float
        Valor do coeficiente de correlação
        
    Retorna:
    --------
    str: Interpretação textual da correlação
    """
    # Determinar força da correlação
    if abs(correlacao) < LIMITE_CORRELACAO_FRACA:
        intensidade = "Fraca"
    elif abs(correlacao) < LIMITE_CORRELACAO_MODERADA:
        intensidade = "Moderada"
    else:
        intensidade = "Forte"
    
    # Determinar direção da correlação
    if correlacao > 0:
        direcao = " positiva"
    elif correlacao < 0:
        direcao = " negativa"
    else:
        return "Ausente"  # Caso especial para correlação = 0
    
    return intensidade + direcao


@optimized_cache(ttl=1800)
def gerar_estatisticas_descritivas(
    df: pd.DataFrame, 
    coluna: str, 
    precisao: int = 2,
    excluir_zeros: bool = True
) -> pd.Series:
    """
    Gera estatísticas descritivas para uma coluna.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame contendo os dados
    coluna: str
        Nome da coluna para análise
    precisao: int, default=2
        Número de casas decimais para arredondamento
    excluir_zeros: bool, default=True
        Se True, exclui valores zero da análise
        
    Retorna:
    --------
    Series: Estatísticas descritivas (count, mean, std, min, 25%, 50%, 75%, max)
    """
    # Verificar se temos dados válidos
    if df.empty or coluna not in df.columns:
        return pd.Series({
            'count': 0, 'mean': 0, 'std': 0, 'min': 0, 
            '25%': 0, '50%': 0, '75%': 0, 'max': 0
        })
    
    # Filtrar valores válidos
    dados = df[coluna]
    if excluir_zeros:
        dados = dados[dados > 0]
    
    # Verificar se ainda temos dados após filtragem
    if dados.empty:
        return pd.Series({
            'count': 0, 'mean': 0, 'std': 0, 'min': 0, 
            '25%': 0, '50%': 0, '75%': 0, 'max': 0
        })
    
    # Calcular estatísticas
    try:
        return dados.describe().round(precisao)
    except Exception as e:
        print(f"Erro ao calcular estatísticas descritivas: {e}")
        return pd.Series({
            'count': 0, 'mean': 0, 'std': 0, 'min': 0, 
            '25%': 0, '50%': 0, '75%': 0, 'max': 0
        })


@optimized_cache(ttl=1800)
def analisar_desempenho_por_estado(
    df_grafico: pd.DataFrame, 
    area_selecionada: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analisa o desempenho por estado, identificando estados com melhor e pior desempenho.
    
    Parâmetros:
    -----------
    df_grafico: DataFrame
        DataFrame com dados do gráfico de linha
    area_selecionada: str, opcional
        Área específica para análise, se fornecida
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com resultados da análise contendo:
        - melhor_estado: Series com dados do estado com melhor desempenho
        - pior_estado: Series com dados do estado com pior desempenho
        - media_geral: float com a média geral de todos os estados
        - desvio_padrao: float com o desvio padrão entre os estados
        - coef_variacao: float com o coeficiente de variação (%)
        - diferenca_percentual: float com a diferença percentual entre melhor e pior
    """
    # Verificar se temos dados para análise
    if df_grafico is None or df_grafico.empty:
        return _criar_resultado_analise_vazio()
    
    # Determinar qual área analisar (específica ou média geral)
    area_para_analise = area_selecionada if area_selecionada else 'Média Geral'
    
    # Verificar se a coluna 'Área' existe
    if 'Área' not in df_grafico.columns:
        return _criar_resultado_analise_vazio()
    
    df_analise = df_grafico[df_grafico['Área'] == area_para_analise]
    
    # Verificar se temos dados para análise após filtragem
    if df_analise.empty:
        return _criar_resultado_analise_vazio()
    
    # Encontrar estados com melhor e pior desempenho
    try:
        # Usar o método idxmax/idxmin de forma segura
        if len(df_analise) > 0 and 'Média' in df_analise.columns:
            indice_melhor = df_analise['Média'].idxmax()
            indice_pior = df_analise['Média'].idxmin()
            
            # Verificar se os índices são válidos
            if indice_melhor in df_analise.index and indice_pior in df_analise.index:
                melhor_estado = df_analise.loc[indice_melhor]
                pior_estado = df_analise.loc[indice_pior]
                
                # Calcular estatísticas gerais
                media_geral = df_analise['Média'].mean()
                desvio_padrao = df_analise['Média'].std()
                
                # Calcular variabilidade (coeficiente de variação)
                coef_variacao = (desvio_padrao / media_geral * 100) if media_geral > 0 else 0
                
                # Calcular diferença percentual entre melhor e pior
                diferenca_percentual = ((melhor_estado['Média'] - pior_estado['Média']) / pior_estado['Média'] * 100) if pior_estado['Média'] > 0 else 0
                
                # Verificar se todos os valores são finitos
                if not all(np.isfinite([media_geral, desvio_padrao, coef_variacao, diferenca_percentual])):
                    print("Aviso: Valores não finitos encontrados nas estatísticas")
                
                return {
                    'melhor_estado': melhor_estado,
                    'pior_estado': pior_estado,
                    'media_geral': round(media_geral, 2),
                    'desvio_padrao': round(desvio_padrao, 2),
                    'coef_variacao': round(coef_variacao, 2),
                    'diferenca_percentual': round(diferenca_percentual, 2)
                }
        
        # Se chegarmos aqui, algo deu errado
        return _criar_resultado_analise_vazio()
    
    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro ao analisar desempenho por estado: {e}")
        return _criar_resultado_analise_vazio()


def _criar_resultado_analise_vazio() -> Dict[str, Any]:
    """
    Cria um resultado de análise vazio para casos onde não há dados suficientes.
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão
    """
    return {
        'melhor_estado': None,
        'pior_estado': None,
        'media_geral': 0,
        'desvio_padrao': 0,
        'coef_variacao': 0,
        'diferenca_percentual': 0
    }


@memory_intensive_function
@optimized_cache(ttl=1800)
def calcular_estatisticas_comparativas(
    df_resultados: pd.DataFrame, 
    variavel_selecionada: str
) -> Dict[str, Any]:
    """
    Calcula estatísticas para análise comparativa entre categorias.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com os resultados por categoria e competência
    variavel_selecionada: str
        Nome da variável categórica analisada
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com estatísticas calculadas
    """
    # Verificar se temos dados válidos
    if df_resultados is None or df_resultados.empty:
        return _criar_resultado_comparativo_vazio()
    
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Competência', 'Categoria', 'Média']
    if not all(col in df_resultados.columns for col in colunas_necessarias):
        return _criar_resultado_comparativo_vazio()
    
    # Inicializar dicionário de resultados
    resultados = {
        'maior_disparidade': {'competencia': None, 'diferenca': 0, 'categoria_max': None, 'categoria_min': None},
        'menor_disparidade': {'competencia': None, 'diferenca': float('inf'), 'categoria_max': None, 'categoria_min': None},
        'disparidades_por_competencia': {},
        'indicadores_globais': {}
    }
    
    try:
        # Obter lista de competências únicas
        competencias = df_resultados['Competência'].unique()
        
        # Verificar se temos competências para analisar
        if len(competencias) == 0:
            return _criar_resultado_comparativo_vazio()
            
        # Calcular indicadores globais (usando todas as competências)
        try:
            # Calcular indicadores de desigualdade para todas as competências
            indicadores_globais = calcular_indicadores_desigualdade(
                df_resultados, 
                coluna_categoria='Categoria',
                coluna_valor='Média'
            )
            resultados['indicadores_globais'] = indicadores_globais
        except Exception as e:
            print(f"Erro ao calcular indicadores globais: {e}")
        
        # Calcular para cada competência
        for competencia in competencias:
            # Filtrar dados apenas desta competência
            df_comp = df_resultados[df_resultados['Competência'] == competencia]
            
            # Verificar se temos pelo menos duas categorias para comparar
            if len(df_comp) <= 1:
                continue
                
            # Obter valor máximo e mínimo
            max_valor = df_comp['Média'].max()
            min_valor = df_comp['Média'].min()
            
            try:
                categoria_max = df_comp.loc[df_comp['Média'].idxmax()]['Categoria']
                categoria_min = df_comp.loc[df_comp['Média'].idxmin()]['Categoria']
            except (KeyError, ValueError):
                # Método alternativo se idxmax/idxmin falhar
                df_max = df_comp[df_comp['Média'] == max_valor].iloc[0] if len(df_comp[df_comp['Média'] == max_valor]) > 0 else None
                df_min = df_comp[df_comp['Média'] == min_valor].iloc[0] if len(df_comp[df_comp['Média'] == min_valor]) > 0 else None
                
                if df_max is None or df_min is None:
                    continue
                    
                categoria_max = df_max['Categoria']
                categoria_min = df_min['Categoria']
            
            # Calcular diferença entre máximo e mínimo
            diferenca = max_valor - min_valor
            diferenca_percentual = (diferenca / min_valor * 100) if min_valor > 0 else 0
            
            # Calcular indicadores de desigualdade para esta competência
            try:
                indicadores = calcular_indicadores_desigualdade(
                    df_comp, 
                    coluna_categoria='Categoria',
                    coluna_valor='Média'
                )
            except Exception as e:
                print(f"Erro ao calcular indicadores para competência {competencia}: {e}")
                indicadores = {
                    'razao_max_min': 0,
                    'coef_variacao': 0,
                    'range_percentual': 0
                }
            
            # Armazenar dados desta competência
            resultados['disparidades_por_competencia'][competencia] = {
                'diferenca': diferenca,
                'diferenca_percentual': diferenca_percentual,
                'categoria_max': categoria_max,
                'categoria_min': categoria_min,
                'valor_max': max_valor,
                'valor_min': min_valor,
                'razao_max_min': indicadores['razao_max_min'],
                'coef_variacao': indicadores['coef_variacao'],
                'range_percentual': indicadores['range_percentual']
            }
            
            # Atualizar maior e menor disparidade global
            if diferenca > resultados['maior_disparidade']['diferenca']:
                resultados['maior_disparidade'] = {
                    'competencia': competencia,
                    'diferenca': diferenca,
                    'diferenca_percentual': diferenca_percentual,
                    'categoria_max': categoria_max,
                    'categoria_min': categoria_min,
                    'valor_max': max_valor,
                    'valor_min': min_valor,
                    'razao_max_min': indicadores['razao_max_min'],
                    'coef_variacao': indicadores['coef_variacao']
                }
            
            if diferenca < resultados['menor_disparidade']['diferenca'] and diferenca > 0:
                resultados['menor_disparidade'] = {
                    'competencia': competencia,
                    'diferenca': diferenca,
                    'diferenca_percentual': diferenca_percentual,
                    'categoria_max': categoria_max,
                    'categoria_min': categoria_min,
                    'valor_max': max_valor,
                    'valor_min': min_valor,
                    'razao_max_min': indicadores['razao_max_min'],
                    'coef_variacao': indicadores['coef_variacao']
                }
        
        # Verificar se encontramos alguma disparidade
        if resultados['menor_disparidade']['diferenca'] == float('inf'):
            resultados['menor_disparidade'] = {
                'competencia': None,
                'diferenca': 0,
                'diferenca_percentual': 0,
                'categoria_max': None,
                'categoria_min': None,
                'valor_max': 0,
                'valor_min': 0,
                'razao_max_min': 0,
                'coef_variacao': 0
            }
            
        return resultados
        
    except Exception as e:
        print(f"Erro ao calcular estatísticas comparativas: {e}")
        return _criar_resultado_comparativo_vazio()


def _criar_resultado_comparativo_vazio() -> Dict[str, Any]:
    """
    Cria um resultado comparativo vazio para casos onde não há dados suficientes.
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão para análise comparativa
    """
    return {
        'maior_disparidade': {
            'competencia': None, 'diferenca': 0, 'diferenca_percentual': 0,
            'categoria_max': None, 'categoria_min': None, 'valor_max': 0, 'valor_min': 0,
            'razao_max_min': 0, 'coef_variacao': 0
        },
        'menor_disparidade': {
            'competencia': None, 'diferenca': 0, 'diferenca_percentual': 0,
            'categoria_max': None, 'categoria_min': None, 'valor_max': 0, 'valor_min': 0,
            'razao_max_min': 0, 'coef_variacao': 0
        },
        'disparidades_por_competencia': {},
        'indicadores_globais': {
            'razao_max_min': 0,
            'coef_variacao': 0,
            'range_percentual': 0
        }
    }


@optimized_cache(ttl=1800)
def calcular_percentis_desempenho(
    df: pd.DataFrame, 
    coluna: str, 
    percentis: List[float] = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
) -> Dict[str, float]:
    """
    Calcula percentis de desempenho para uma coluna específica.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame contendo os dados
    coluna: str
        Nome da coluna para análise
    percentis: List[float], default=[0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
        Lista de percentis a serem calculados
        
    Retorna:
    --------
    Dict[str, float]: Dicionário com percentis calculados
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or coluna not in df.columns:
        return {f"P{int(p*100)}": 0 for p in percentis}
    
    # Filtrar valores válidos
    valores = df[coluna].dropna()
    valores = valores[valores > 0]
    
    # Verificar se ainda temos dados após filtragem
    if len(valores) == 0:
        return {f"P{int(p*100)}": 0 for p in percentis}
    
    try:
        # Calcular percentis
        resultado = {}
        for p in percentis:
            valor_percentil = valores.quantile(p)
            resultado[f"P{int(p*100)}"] = round(valor_percentil, 2)
        
        return resultado
    
    except Exception as e:
        print(f"Erro ao calcular percentis: {e}")
        return {f"P{int(p*100)}": 0 for p in percentis}


@optimized_cache(ttl=1800)
def analisar_variabilidade_entre_categorias(
    df_resultados: pd.DataFrame, 
    competencia: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analisa a variabilidade de desempenho entre diferentes categorias.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com os resultados por categoria e competência
    competencia: str, opcional
        Competência específica para análise. Se None, analisa todas.
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com medidas de variabilidade
    """
    # Verificar se temos dados válidos
    if df_resultados is None or df_resultados.empty:
        return {
            'coef_variacao': 0,
            'amplitude': 0,
            'desvio_padrao': 0,
            'variancia': 0
        }
    
    # Filtrar por competência específica, se fornecida
    if competencia is not None:
        df_analise = df_resultados[df_resultados['Competência'] == competencia]
    else:
        df_analise = df_resultados
    
    # Verificar se temos dados após filtragem
    if df_analise.empty:
        return {
            'coef_variacao': 0,
            'amplitude': 0,
            'desvio_padrao': 0,
            'variancia': 0
        }
    
    try:
        # Calcular medidas de variabilidade
        medias_por_categoria = df_analise.groupby('Categoria')['Média'].mean()
        media_geral = medias_por_categoria.mean()
        desvio_padrao = medias_por_categoria.std()
        variancia = medias_por_categoria.var()
        valor_min = medias_por_categoria.min()
        valor_max = medias_por_categoria.max()
        amplitude = valor_max - valor_min
        
        # Calcular coeficiente de variação (em porcentagem)
        coef_variacao = (desvio_padrao / media_geral * 100) if media_geral > 0 else 0
        
        # Criar classificação da variabilidade
        if coef_variacao < LIMIARES_ESTATISTICOS['variabilidade_baixa']:
            classificacao = "Baixa variabilidade"
        elif coef_variacao < LIMIARES_ESTATISTICOS['variabilidade_moderada']:
            classificacao = "Variabilidade moderada"
        else:
            classificacao = "Alta variabilidade"
        
        return {
            'coef_variacao': round(coef_variacao, 2),
            'amplitude': round(amplitude, 2),
            'desvio_padrao': round(desvio_padrao, 2),
            'variancia': round(variancia, 2),
            'media_geral': round(media_geral, 2),
            'valor_min': round(valor_min, 2),
            'valor_max': round(valor_max, 2),
            'classificacao': classificacao
        }
    
    except Exception as e:
        print(f"Erro ao analisar variabilidade: {e}")
        return {
            'coef_variacao': 0,
            'amplitude': 0,
            'desvio_padrao': 0,
            'variancia': 0
        }