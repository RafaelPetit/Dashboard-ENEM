import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from utils.data_loader import calcular_seguro
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from utils.helpers.regiao_utils import obter_regiao_do_estado
from utils.mappings import get_mappings

# Obter mapeamentos e constantes
mappings = get_mappings()
CONFIG_PROCESSAMENTO = mappings.get('config_processamento', {})
LIMIARES_ESTATISTICOS = mappings.get('limiares_estatisticos', {})

@optimized_cache(ttl=1800)  # Cache válido por 30 minutos
def analisar_metricas_principais(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    colunas_notas: List[str]
) -> Dict[str, Any]:
    """
    Calcula as métricas principais para a aba Geral.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os dados dos candidatos
    estados_selecionados : list
        Lista de estados selecionados para análise
    colunas_notas : list
        Lista de colunas com notas das competências
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com métricas calculadas:
        - media_geral: Média geral de todas as competências e estados
        - maior_media: Maior média entre todas as competências
        - menor_media: Menor média entre todas as competências
        - estado_maior_media: Estado com maior média geral
        - estado_menor_media: Estado com menor média geral
        - valor_maior_media_estado: Valor da maior média por estado
        - valor_menor_media_estado: Valor da menor média por estado
        - total_candidatos: Número total de candidatos
        - medias_estados: Dicionário com médias por estado
        - medias_por_competencia: Dicionário com médias por competência
        - taxa_presenca: Percentual de candidatos presentes nos dois dias
    """
    # Verificar se temos dados válidos
    if microdados_estados is None or microdados_estados.empty:
        return _criar_metricas_principais_vazias()
    
    try:
        # Calcular médias por estado e competência (usando processamento otimizado)
        resultados = _calcular_medias_estados_competencias(microdados_estados, estados_selecionados, colunas_notas)
        
        # Extrair informações do resultado
        media_por_estado = resultados['todas_medias']
        medias_estados = resultados['medias_por_estado']
        medias_por_competencia = resultados['medias_por_competencia']
        
        # Calcular média geral
        media_geral = np.mean(media_por_estado) if media_por_estado else 0.0
        
        # Valores padrão caso não haja dados
        estado_maior_media = "N/A"
        estado_menor_media = "N/A"
        valor_maior_media_estado = 0.0
        valor_menor_media_estado = 0.0
        
        # Encontrar o estado com a maior e menor média
        if medias_estados:
            estado_maior_media, valor_maior_media_estado = max(medias_estados.items(), key=lambda x: x[1])
            estado_menor_media, valor_menor_media_estado = min(medias_estados.items(), key=lambda x: x[1])
        
        # Maior e menor média entre todas as áreas e estados
        maior_media = np.max(media_por_estado) if media_por_estado else 0.0
        menor_media = np.min([m for m in media_por_estado if m > 0]) if media_por_estado else 0.0
        
        # Total de candidatos
        total_candidatos = len(microdados_estados)
        
        # Calcular taxa de presença (candidatos que fizeram pelo menos uma prova)
        taxa_presenca = 0.0
        if 'TP_PRESENCA_GERAL' in microdados_estados.columns:
            # Código 3 = presente nos dois dias
            candidatos_presentes = microdados_estados[microdados_estados['TP_PRESENCA_GERAL'] == 3].shape[0]
            taxa_presenca = round(candidatos_presentes / total_candidatos * 100, 2) if total_candidatos > 0 else 0.0
        else:
            # Alternativa: calcular com base nas notas válidas
            candidatos_presentes = 0
            for col in colunas_notas:
                if col in microdados_estados.columns:
                    presentes_coluna = len(microdados_estados[
                        (microdados_estados[col] > 0) & 
                        (microdados_estados[col] != -1) & 
                        (microdados_estados[col].notna())
                    ])
                    candidatos_presentes = max(candidatos_presentes, presentes_coluna)
            
            taxa_presenca = round(candidatos_presentes / total_candidatos * 100, 2) if total_candidatos > 0 else 0.0
        
        # Calcular totais por região
        totais_por_regiao = _calcular_totais_por_regiao(microdados_estados)
        
        return {
            'media_geral': round(media_geral, 2),
            'maior_media': round(maior_media, 2),
            'menor_media': round(menor_media, 2),
            'estado_maior_media': estado_maior_media,
            'estado_menor_media': estado_menor_media,
            'valor_maior_media_estado': round(valor_maior_media_estado, 2),
            'valor_menor_media_estado': round(valor_menor_media_estado, 2),
            'total_candidatos': total_candidatos,
            'medias_estados': {k: round(v, 2) for k, v in medias_estados.items()},
            'medias_por_competencia': {k: round(v, 2) for k, v in medias_por_competencia.items()},
            'taxa_presenca': taxa_presenca,
            'totais_por_regiao': totais_por_regiao
        }
    except Exception as e:
        print(f"Erro ao analisar métricas principais: {e}")
        return _criar_metricas_principais_vazias()


def _criar_metricas_principais_vazias() -> Dict[str, Any]:
    """
    Cria um dicionário vazio com estrutura padrão para métricas principais.
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão para métricas principais
    """
    return {
        'media_geral': 0.0,
        'maior_media': 0.0,
        'menor_media': 0.0,
        'estado_maior_media': "N/A",
        'estado_menor_media': "N/A",
        'valor_maior_media_estado': 0.0,
        'valor_menor_media_estado': 0.0,
        'total_candidatos': 0,
        'medias_estados': {},
        'medias_por_competencia': {},
        'taxa_presenca': 0.0,
        'totais_por_regiao': {}
    }


@memory_intensive_function
def _calcular_medias_estados_competencias(
    df: pd.DataFrame, 
    estados: List[str], 
    colunas_notas: List[str]
) -> Dict[str, Any]:
    """
    Calcula médias por estado e competência de forma otimizada.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com os dados
    estados: List[str]
        Lista de estados para análise
    colunas_notas: List[str]
        Lista de colunas com notas
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com médias calculadas
    """
    # Inicializar estruturas de dados
    todas_medias = []
    medias_por_estado = {}
    medias_por_competencia = {}
    
    try:
        # Agrupar por estado para melhor desempenho
        grupos_estado = df.groupby('SG_UF_PROVA', observed=False)
        
        # Processar cada estado
        for estado in estados:
            try:
                dados_estado = grupos_estado.get_group(estado)
            except KeyError:
                continue  # Estado não encontrado, pular
                
            medias_estado_atual = []
            
            # Processar cada competência
            for col in colunas_notas:
                if col not in dados_estado.columns:
                    continue
                    
                # Filtrar notas válidas (maiores que 0, diferentes de -1, e não nulas)
                # -1 representa candidatos ausentes no ENEM
                notas_validas = dados_estado[
                    (dados_estado[col] > 0) & 
                    (dados_estado[col] != -1) & 
                    (dados_estado[col].notna())
                ][col]
                
                if len(notas_validas) > 0:
                    # Calcular média
                    media = calcular_seguro(notas_validas, 'media')
                    
                    # Armazenar resultados
                    todas_medias.append(media)
                    medias_estado_atual.append(media)
                    
                    # Atualizar médias por competência
                    if col not in medias_por_competencia:
                        medias_por_competencia[col] = []
                    medias_por_competencia[col].append(media)
            
            # Calcular média geral do estado
            if medias_estado_atual:
                medias_por_estado[estado] = np.mean(medias_estado_atual)
        
        # Calcular média por competência
        for comp, valores in medias_por_competencia.items():
            medias_por_competencia[comp] = np.mean(valores) if valores else 0
        
        return {
            'todas_medias': todas_medias,
            'medias_por_estado': medias_por_estado,
            'medias_por_competencia': medias_por_competencia
        }
        
    except Exception as e:
        print(f"Erro ao calcular médias por estado e competência: {e}")
        return {
            'todas_medias': [],
            'medias_por_estado': {},
            'medias_por_competencia': {}
        }


def _calcular_totais_por_regiao(df: pd.DataFrame) -> Dict[str, int]:
    """
    Calcula o total de candidatos por região.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com os dados
        
    Retorna:
    --------
    Dict[str, int]: Dicionário com total de candidatos por região
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or 'SG_UF_PROVA' not in df.columns:
        return {}
    
    try:
        # Criar coluna temporária com a região de cada estado
        df_temp = df.copy()
        df_temp['REGIAO'] = df_temp['SG_UF_PROVA'].apply(obter_regiao_do_estado)
        
        # Contar candidatos por região
        contagem = df_temp['REGIAO'].value_counts().to_dict()
        
        # Remover região vazia se existir
        if '' in contagem:
            del contagem['']
            
        return contagem
        
    except Exception as e:
        print(f"Erro ao calcular totais por região: {e}")
        return {}


@optimized_cache(ttl=1800)
def analisar_distribuicao_notas(
    df_dados: pd.DataFrame, 
    coluna: str
) -> Dict[str, Any]:
    """
    Analisa a distribuição de notas para uma área específica.
    
    Parâmetros:
    -----------
    df_dados : DataFrame
        DataFrame com os dados filtrados
    coluna : str
        Nome da coluna a ser analisada
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com análises estatísticas:
        - total_valido: Número de candidatos com notas válidas
        - total_invalido: Número de candidatos com notas inválidas (zero ou ausentes)
        - media: Média das notas válidas
        - mediana: Mediana das notas válidas
        - min_valor: Valor mínimo entre notas válidas
        - max_valor: Valor máximo entre notas válidas
        - desvio_padrao: Desvio padrão das notas válidas
        - curtose: Curtose da distribuição
        - assimetria: Assimetria da distribuição
        - percentis: Dicionário com percentis (10, 25, 50, 75, 90, 95, 99)
        - faixas: Dicionário com percentuais em cada faixa de nota
        - conceitos: Dicionário com percentuais em cada conceito
    """
    # Verificar se temos dados válidos
    if df_dados is None or df_dados.empty or coluna not in df_dados.columns:
        return _criar_analise_distribuicao_vazia()
    
    try:
        # Converter para float64 para evitar overflow com float16
        if df_dados[coluna].dtype in ['float16', 'int16']:
            coluna_convertida = df_dados[coluna].astype('float64')
        else:
            coluna_convertida = df_dados[coluna]
        
        # Dados apenas para notas válidas (maiores que 0 e diferentes de -1)
        # -1 representa candidatos ausentes no ENEM
        df_valido = df_dados[
            (coluna_convertida > 0) & 
            (coluna_convertida != -1) & 
            (coluna_convertida.notna()) &
            (coluna_convertida < 1000)  # Adicionar limite superior para evitar outliers extremos
        ]
        
        # Verificar se temos dados suficientes após filtragem
        if df_valido.empty:
            return _criar_analise_distribuicao_vazia()
        
        # Usar a coluna convertida para os cálculos
        coluna_valida = coluna_convertida[df_valido.index]
        
        # Calcular estatísticas básicas
        media = calcular_seguro(coluna_valida, 'media')
        mediana = calcular_seguro(coluna_valida, 'mediana')
        min_valor = calcular_seguro(coluna_valida, 'min')
        max_valor = calcular_seguro(coluna_valida, 'max')
        desvio_padrao = calcular_seguro(coluna_valida, 'std')
        curtose = calcular_seguro(coluna_valida, 'curtose')
        assimetria = calcular_seguro(coluna_valida, 'assimetria')
        
        # Calcular percentis de forma segura
        percentis = _calcular_percentis_seguros(coluna_valida, [10, 25, 50, 75, 90, 95, 99])
        
        # Calcular faixas de desempenho
        total_valido = len(df_valido)
        total_candidatos = len(df_dados)  # Total real de candidatos (incluindo ausentes)
        faixas = _calcular_faixas_desempenho(df_valido, coluna, total_valido)
        
        # Análise de conceito (baseado em faixas típicas de nota do ENEM)
        conceitos = _calcular_conceitos(df_valido, coluna, total_valido)
        
        # Calcular intervalo de confiança para a média (95%)
        intervalo_confianca = _calcular_intervalo_confianca(coluna_valida)
        
        # Calcular coeficiente de variação (%) com validação
        if media > 0 and desvio_padrao > 0 and not np.isnan(desvio_padrao) and not np.isinf(desvio_padrao):
            coef_variacao = (desvio_padrao / media * 100)
        else:
            coef_variacao = 0.0
        
        # Validar se coef_variacao é finito
        if not np.isfinite(coef_variacao):
            coef_variacao = 0.0
        
        # Retornar análise completa com validações
        return {
            'total_valido': total_valido,
            'total_candidatos': total_candidatos,  # Total real incluindo ausentes
            'total_invalido': len(df_dados) - total_valido,
            'media': round(media, 2) if np.isfinite(media) else 0.0,
            'mediana': round(mediana, 2) if np.isfinite(mediana) else 0.0,
            'min_valor': round(min_valor, 2) if np.isfinite(min_valor) else 0.0,
            'max_valor': round(max_valor, 2) if np.isfinite(max_valor) else 0.0,
            'desvio_padrao': round(desvio_padrao, 2) if np.isfinite(desvio_padrao) else 0.0,
            'curtose': round(curtose, 4) if np.isfinite(curtose) else 0.0,
            'assimetria': round(assimetria, 4) if np.isfinite(assimetria) else 0.0,
            'percentis': {k: round(v, 2) if np.isfinite(v) else 0.0 for k, v in percentis.items()},
            'faixas': {k: round(v, 2) if np.isfinite(v) else 0.0 for k, v in faixas.items()},
            'conceitos': {k: round(v, 2) if np.isfinite(v) else 0.0 for k, v in conceitos.items()},
            'intervalo_confianca': [
                round(intervalo_confianca[0], 2) if np.isfinite(intervalo_confianca[0]) else 0.0,
                round(intervalo_confianca[1], 2) if np.isfinite(intervalo_confianca[1]) else 0.0
            ],
            'coef_variacao': round(coef_variacao, 2) if np.isfinite(coef_variacao) else 0.0,
            'amplitude': round(max_valor - min_valor, 2) if np.isfinite(max_valor - min_valor) else 0.0
        }
    except Exception as e:
        print(f"Erro ao analisar distribuição de notas: {e}")
        return _criar_analise_distribuicao_vazia()


def _criar_analise_distribuicao_vazia() -> Dict[str, Any]:
    """
    Cria um dicionário vazio com estrutura padrão para análise de distribuição.
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão para análise de distribuição
    """
    return {
        'total_valido': 0,
        'total_candidatos': 0,  # Total real incluindo ausentes
        'total_invalido': 0,
        'media': 0.0,
        'mediana': 0.0,
        'min_valor': 0.0,
        'max_valor': 0.0,
        'desvio_padrao': 0.0,
        'curtose': 0.0,
        'assimetria': 0.0,
        'percentis': {p: 0.0 for p in [10, 25, 50, 75, 90, 95, 99]},
        'faixas': {
            'Abaixo de 300': 0.0,
            '300 a 500': 0.0,
            '500 a 700': 0.0,
            '700 a 900': 0.0,
            '900 ou mais': 0.0
        },
        'conceitos': {
            'Insuficiente (abaixo de 450)': 0.0,
            'Regular (450 a 600)': 0.0,
            'Bom (600 a 750)': 0.0,
            'Muito bom (750 a 850)': 0.0,
            'Excelente (850 ou mais)': 0.0
        },
        'intervalo_confianca': [0.0, 0.0],
        'coef_variacao': 0.0,
        'amplitude': 0.0
    }


def _calcular_percentis_seguros(serie: pd.Series, pontos_percentis: List[int]) -> Dict[int, float]:
    """
    Calcula percentis de forma segura para uma série.
    
    Parâmetros:
    -----------
    serie: Series
        Série com valores numéricos
    pontos_percentis: List[int]
        Lista de percentis a calcular
        
    Retorna:
    --------
    Dict[int, float]: Dicionário com percentis calculados
    """
    try:
        # Converter para float64 para evitar overflow
        if serie.dtype in ['float16', 'int16']:
            serie = serie.astype('float64')
        
        # Remover valores inválidos
        serie_limpa = serie.dropna()
        serie_limpa = serie_limpa[np.isfinite(serie_limpa)]
        
        if len(serie_limpa) == 0:
            return {p: 0.0 for p in pontos_percentis}
        
        return {p: np.percentile(serie_limpa, p) for p in pontos_percentis}
    except Exception as e:
        print(f"Erro ao calcular percentis: {e}")
        return {p: 0.0 for p in pontos_percentis}


def _calcular_faixas_desempenho(df: pd.DataFrame, coluna: str, total: int) -> Dict[str, float]:
    """
    Calcula percentuais para diferentes faixas de desempenho.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com dados válidos
    coluna: str
        Nome da coluna com notas
    total: int
        Total de registros válidos
        
    Retorna:
    --------
    Dict[str, float]: Dicionário com percentuais por faixa
    """
    if total == 0:
        return {
            'Abaixo de 300': 0.0,
            '300 a 500': 0.0,
            '500 a 700': 0.0,
            '700 a 900': 0.0,
            '900 ou mais': 0.0
        }
    
    try:
        return {
            'Abaixo de 300': len(df[df[coluna] < 300]) / total * 100,
            '300 a 500': len(df[(df[coluna] >= 300) & (df[coluna] < 500)]) / total * 100,
            '500 a 700': len(df[(df[coluna] >= 500) & (df[coluna] < 700)]) / total * 100,
            '700 a 900': len(df[(df[coluna] >= 700) & (df[coluna] < 900)]) / total * 100,
            '900 ou mais': len(df[df[coluna] >= 900]) / total * 100
        }
    except Exception as e:
        print(f"Erro ao calcular faixas de desempenho: {e}")
        return {
            'Abaixo de 300': 0.0,
            '300 a 500': 0.0,
            '500 a 700': 0.0,
            '700 a 900': 0.0,
            '900 ou mais': 0.0
        }


def _calcular_conceitos(df: pd.DataFrame, coluna: str, total: int) -> Dict[str, float]:
    """
    Calcula percentuais para diferentes conceitos.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com dados válidos
    coluna: str
        Nome da coluna com notas
    total: int
        Total de registros válidos
        
    Retorna:
    --------
    Dict[str, float]: Dicionário com percentuais por conceito
    """
    if total == 0:
        return {
            'Insuficiente (abaixo de 450)': 0.0,
            'Regular (450 a 600)': 0.0,
            'Bom (600 a 750)': 0.0,
            'Muito bom (750 a 850)': 0.0,
            'Excelente (850 ou mais)': 0.0
        }
    
    try:
        return {
            'Insuficiente (abaixo de 450)': len(df[df[coluna] < 450]) / total * 100,
            'Regular (450 a 600)': len(df[(df[coluna] >= 450) & (df[coluna] < 600)]) / total * 100,
            'Bom (600 a 750)': len(df[(df[coluna] >= 600) & (df[coluna] < 750)]) / total * 100,
            'Muito bom (750 a 850)': len(df[(df[coluna] >= 750) & (df[coluna] < 850)]) / total * 100,
            'Excelente (850 ou mais)': len(df[df[coluna] >= 850]) / total * 100
        }
    except Exception as e:
        print(f"Erro ao calcular conceitos: {e}")
        return {
            'Insuficiente (abaixo de 450)': 0.0,
            'Regular (450 a 600)': 0.0,
            'Bom (600 a 750)': 0.0,
            'Muito bom (750 a 850)': 0.0,
            'Excelente (850 ou mais)': 0.0
        }


def _calcular_intervalo_confianca(serie: pd.Series, nivel: float = 0.95) -> Tuple[float, float]:
    """
    Calcula intervalo de confiança para a média de uma série.
    
    Parâmetros:
    -----------
    serie: Series
        Série com valores numéricos
    nivel: float, default=0.95
        Nível de confiança (0.95 = 95%)
        
    Retorna:
    --------
    Tuple[float, float]: Limite inferior e superior do intervalo
    """
    try:
        from scipy import stats
        
        # Verificar se temos dados suficientes
        if len(serie) < 2:
            return (0.0, 0.0)
        
        # Converter para float64 para evitar overflow
        if serie.dtype in ['float16', 'int16']:
            serie = serie.astype('float64')
        
        # Remover valores nulos ou inválidos
        serie_limpa = serie.dropna()
        if len(serie_limpa) < 2:
            return (0.0, 0.0)
        
        # Remover valores infinitos
        serie_limpa = serie_limpa[np.isfinite(serie_limpa)]
        if len(serie_limpa) < 2:
            return (0.0, 0.0)
        
        media = serie_limpa.mean()
        
        # Verificar se a média é válida
        if not np.isfinite(media):
            return (0.0, 0.0)
        
        # Calcular erro padrão
        try:
            erro_padrao = stats.sem(serie_limpa)
        except:
            # Fallback manual
            erro_padrao = serie_limpa.std(ddof=1) / np.sqrt(len(serie_limpa))
        
        # Verificar se o erro padrão é válido
        if not np.isfinite(erro_padrao) or erro_padrao <= 0:
            return (media, media)
        
        # Calcular intervalo de confiança
        try:
            intervalo = stats.t.interval(nivel, len(serie_limpa)-1, loc=media, scale=erro_padrao)
        except:
            # Fallback simples
            margem_erro = 1.96 * erro_padrao  # Aproximação para grandes amostras
            intervalo = (media - margem_erro, media + margem_erro)
        
        # Verificar se o intervalo é válido
        if not (np.isfinite(intervalo[0]) and np.isfinite(intervalo[1])):
            return (media, media)
            
        return intervalo
        
    except Exception as e:
        print(f"Erro ao calcular intervalo de confiança: {e}")
        return (0.0, 0.0)


@optimized_cache(ttl=1800)
def analisar_faltas(
    df_faltas: pd.DataFrame
) -> Dict[str, Any]:
    """
    Analisa padrões de faltas no ENEM com base nos dias de ausência.
    
    Parâmetros:
    -----------
    df_faltas : DataFrame
        DataFrame preparado com dados de faltas
        
    Retorna:
    --------
    Dict[str, Any]
        Dicionário com análises sobre faltas:
        - taxa_media_geral: Taxa média geral de faltas
        - estado_maior_falta: Estado com maior taxa de faltas
        - estado_menor_falta: Estado com menor taxa de faltas
        - medias_por_tipo: DataFrame com médias por tipo de falta
        - tipo_mais_comum: Tipo de falta mais comum
        - media_faltas_ambos_dias: Média de faltas em ambos os dias
        - media_faltas_dia1: Média de faltas no primeiro dia
        - media_faltas_dia2: Média de faltas no segundo dia
        - diferenca_dias: Diferença entre faltas no segundo e primeiro dia
        - desvio_padrao_faltas: Desvio padrão das faltas por estado
        - variabilidade: Classificação da variabilidade de faltas
        - estados_maior_evasao: Lista de estados com maior evasão
        - estados_menor_evasao: Lista de estados com menor evasão
    """
    # Verificar se temos dados válidos
    if df_faltas is None or df_faltas.empty:
        return _criar_analise_faltas_vazia()
    
    try:
        # Verificar estrutura mínima necessária
        colunas_necessarias = ['Estado', 'Tipo de Falta', 'Percentual de Faltas']
        if not all(col in df_faltas.columns for col in colunas_necessarias):
            return _criar_analise_faltas_vazia()
        
        # Normalizar tipos de faltas para padronização
        df_normalizado = _normalizar_tipos_faltas(df_faltas)
        
        # Filtrar para tipos específicos de falta
        df_ambos_dias = df_normalizado[df_normalizado['Tipo de Falta'] == 'Faltou nos dois dias'].copy()
        df_dia1 = df_normalizado[df_normalizado['Tipo de Falta'] == 'Faltou no primeiro dia'].copy()
        df_dia2 = df_normalizado[df_normalizado['Tipo de Falta'] == 'Faltou no segundo dia'].copy()
        
        # Calcular médias por tipo de falta
        media_faltas_ambos_dias = df_ambos_dias['Percentual de Faltas'].mean() if not df_ambos_dias.empty else 0
        media_faltas_dia1 = df_dia1['Percentual de Faltas'].mean() if not df_dia1.empty else 0
        media_faltas_dia2 = df_dia2['Percentual de Faltas'].mean() if not df_dia2.empty else 0
        
        # Calcular taxa média geral (soma das três médias)
        taxa_media_geral = media_faltas_ambos_dias + media_faltas_dia1 + media_faltas_dia2
        
        # Estado com maior taxa de faltas em ambos os dias
        estado_maior_falta = None
        estado_menor_falta = None
        
        if not df_ambos_dias.empty:
            try:
                idx_max = df_ambos_dias['Percentual de Faltas'].idxmax()
                estado_maior_falta = df_ambos_dias.loc[idx_max].to_dict()
            except (KeyError, ValueError):
                # Alternativa se idxmax falhar
                df_max = df_ambos_dias.loc[df_ambos_dias['Percentual de Faltas'] == df_ambos_dias['Percentual de Faltas'].max()]
                if not df_max.empty:
                    estado_maior_falta = df_max.iloc[0].to_dict()
        
        # Estado com menor taxa de faltas em ambos os dias
        if not df_ambos_dias.empty:
            try:
                idx_min = df_ambos_dias['Percentual de Faltas'].idxmin()
                estado_menor_falta = df_ambos_dias.loc[idx_min].to_dict()
            except (KeyError, ValueError):
                # Alternativa se idxmin falhar
                df_min = df_ambos_dias.loc[df_ambos_dias['Percentual de Faltas'] == df_ambos_dias['Percentual de Faltas'].min()]
                if not df_min.empty:
                    estado_menor_falta = df_min.iloc[0].to_dict()
        
        # Tipo de falta mais comum (média mais alta)
        tipo_mais_comum = 'Ambos os dias'
        maior_media = media_faltas_ambos_dias
        
        if media_faltas_dia1 > maior_media:
            tipo_mais_comum = 'Primeiro dia'
            maior_media = media_faltas_dia1
        
        if media_faltas_dia2 > maior_media:
            tipo_mais_comum = 'Segundo dia'
            maior_media = media_faltas_dia2
        
        # Criar DataFrame com médias por tipo
        medias_por_tipo = pd.DataFrame({
            'Tipo de Falta': ['Faltou nos dois dias', 'Faltou no primeiro dia', 'Faltou no segundo dia'],
            'Percentual de Faltas': [media_faltas_ambos_dias, media_faltas_dia1, media_faltas_dia2]
        })
        
        # Desvio padrão das faltas por estado (para os dois dias)
        desvio_padrao_faltas = df_ambos_dias['Percentual de Faltas'].std() if not df_ambos_dias.empty else 0
        
        # Análise da variabilidade de faltas por estado
        if desvio_padrao_faltas < 2:
            variabilidade = "Baixa variabilidade entre estados"
        elif desvio_padrao_faltas < 5:
            variabilidade = "Variabilidade moderada entre estados"
        else:
            variabilidade = "Alta variabilidade entre estados"
        
        # Diferença entre faltas no primeiro e segundo dia
        diferenca_dias = media_faltas_dia2 - media_faltas_dia1
        
        # Identificar estados com maior e menor evasão (top 3)
        estados_maior_evasao = _identificar_estados_maior_evasao(df_ambos_dias, 3)
        estados_menor_evasao = _identificar_estados_menor_evasao(df_ambos_dias, 3)
        
        # Retornar análise completa
        return {
            'taxa_media_geral': round(taxa_media_geral, 2),
            'estado_maior_falta': estado_maior_falta,
            'estado_menor_falta': estado_menor_falta,
            'medias_por_tipo': medias_por_tipo,
            'tipo_mais_comum': tipo_mais_comum,
            'media_faltas_ambos_dias': round(media_faltas_ambos_dias, 2),
            'media_faltas_dia1': round(media_faltas_dia1, 2),
            'media_faltas_dia2': round(media_faltas_dia2, 2),
            'diferenca_dias': round(diferenca_dias, 2),
            'desvio_padrao_faltas': round(desvio_padrao_faltas, 2),
            'variabilidade': variabilidade,
            'estados_maior_evasao': estados_maior_evasao,
            'estados_menor_evasao': estados_menor_evasao
        }
    except Exception as e:
        print(f"Erro ao analisar faltas: {e}")
        return _criar_analise_faltas_vazia()


def _criar_analise_faltas_vazia() -> Dict[str, Any]:
    """
    Cria um dicionário vazio com estrutura padrão para análise de faltas.
    
    Retorna:
    --------
    Dict[str, Any]: Dicionário com valores padrão para análise de faltas
    """
    return {
        'taxa_media_geral': 0.0,
        'estado_maior_falta': None,
        'estado_menor_falta': None,
        'medias_por_tipo': pd.DataFrame({
            'Tipo de Falta': ['Faltou nos dois dias', 'Faltou no primeiro dia', 'Faltou no segundo dia'],
            'Percentual de Faltas': [0.0, 0.0, 0.0]
        }),
        'tipo_mais_comum': 'N/A',
        'media_faltas_ambos_dias': 0.0,
        'media_faltas_dia1': 0.0,
        'media_faltas_dia2': 0.0,
        'diferenca_dias': 0.0,
        'desvio_padrao_faltas': 0.0,
        'variabilidade': 'N/A',
        'estados_maior_evasao': [],
        'estados_menor_evasao': []
    }


def _normalizar_tipos_faltas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza os tipos de faltas para nomenclatura padrão.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com dados de faltas
        
    Retorna:
    --------
    DataFrame: DataFrame com tipos de faltas normalizados
    """
    # Criar cópia para não modificar o original
    df_normalizado = df.copy()
    
    # Mapeamento para normalização
    mapeamento = {
        'Faltou nos dois dias': 'Faltou nos dois dias',
        'Faltou no segundo dia': 'Faltou no segundo dia',
        'Faltou no primeiro dia': 'Faltou no primeiro dia',
        'Faltou apenas no segundo dia': 'Faltou no segundo dia',
        'Faltou apenas no primeiro dia': 'Faltou no primeiro dia'
    }
    
    # Aplicar normalização
    for padrao, normalizacao in mapeamento.items():
        df_normalizado.loc[df_normalizado['Tipo de Falta'].str.contains(padrao, case=False), 'Tipo de Falta'] = normalizacao
    
    return df_normalizado


def _identificar_estados_maior_evasao(df: pd.DataFrame, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Identifica os estados com maior taxa de evasão.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com dados de faltas
    top_n: int, default=3
        Número de estados a retornar
        
    Retorna:
    --------
    List[Dict[str, Any]]: Lista com informações dos estados
    """
    if df is None or df.empty:
        return []
    
    try:
        # Ordenar por percentual de faltas (decrescente)
        df_ordenado = df.sort_values('Percentual de Faltas', ascending=False)
        
        # Obter top N estados
        resultado = []
        for i, row in df_ordenado.head(top_n).iterrows():
            resultado.append({
                'Estado': row['Estado'],
                'Percentual': round(row['Percentual de Faltas'], 2),
                'Contagem': int(row['Contagem']) if 'Contagem' in row else 0,
                'Total': int(row['Total']) if 'Total' in row else 0
            })
        
        return resultado
        
    except Exception as e:
        print(f"Erro ao identificar estados com maior evasão: {e}")
        return []


def _identificar_estados_menor_evasao(df: pd.DataFrame, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Identifica os estados com menor taxa de evasão.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com dados de faltas
    top_n: int, default=3
        Número de estados a retornar
        
    Retorna:
    --------
    List[Dict[str, Any]]: Lista com informações dos estados
    """
    if df is None or df.empty:
        return []
    
    try:
        # Ordenar por percentual de faltas (crescente)
        df_ordenado = df.sort_values('Percentual de Faltas', ascending=True)
        
        # Obter top N estados
        resultado = []
        for i, row in df_ordenado.head(top_n).iterrows():
            resultado.append({
                'Estado': row['Estado'],
                'Percentual': round(row['Percentual de Faltas'], 2),
                'Contagem': int(row['Contagem']) if 'Contagem' in row else 0,
                'Total': int(row['Total']) if 'Total' in row else 0
            })
        
        return resultado
        
    except Exception as e:
        print(f"Erro ao identificar estados com menor evasão: {e}")
        return []


@optimized_cache(ttl=1800)
def analisar_desempenho_por_faixa_nota(
    df: pd.DataFrame, 
    coluna: str,
    faixas: Optional[Dict[str, Tuple[float, float]]] = None
) -> Dict[str, Any]:
    """
    Analisa a distribuição dos candidatos por faixas de notas.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com os dados
    coluna: str
        Nome da coluna com notas
    faixas: Dict[str, Tuple[float, float]], opcional
        Dicionário com definição personalizada de faixas
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com análise por faixas
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or coluna not in df.columns:
        return {
            'contagem': {},
            'percentual': {},
            'faixa_predominante': '',
            'total_valido': 0
        }
    
    try:
        # Filtrar notas válidas
        df_valido = df[df[coluna] > 0]
        
        # Verificar se temos dados após filtragem
        if df_valido.empty:
            return {
                'contagem': {},
                'percentual': {},
                'faixa_predominante': '',
                'total_valido': 0
            }
        
        # Definir faixas padrão se não fornecidas
        if faixas is None:
            faixas = {
                'Insuficiente': (0, 450),
                'Regular': (450, 600),
                'Bom': (600, 750),
                'Muito bom': (750, 850),
                'Excelente': (850, 1000)
            }
        
        # Calcular contagem por faixa
        contagem = {}
        for nome, (min_val, max_val) in faixas.items():
            contagem[nome] = len(df_valido[(df_valido[coluna] >= min_val) & (df_valido[coluna] < max_val)])
        
        # Calcular percentuais
        total = len(df_valido)
        percentual = {nome: (count / total * 100) for nome, count in contagem.items()}
        
        # Identificar faixa predominante
        faixa_predominante = max(contagem.items(), key=lambda x: x[1])[0] if contagem else ''
        
        # Criar estatísticas por faixa
        estatisticas_faixas = {}
        for nome, (min_val, max_val) in faixas.items():
            notas_faixa = df_valido[(df_valido[coluna] >= min_val) & (df_valido[coluna] < max_val)][coluna]
            if len(notas_faixa) > 0:
                estatisticas_faixas[nome] = {
                    'media': round(notas_faixa.mean(), 2),
                    'mediana': round(notas_faixa.median(), 2),
                    'desvio_padrao': round(notas_faixa.std(), 2) if len(notas_faixa) > 1 else 0,
                    'contagem': len(notas_faixa),
                    'percentual': round(len(notas_faixa) / total * 100, 2)
                }
            else:
                estatisticas_faixas[nome] = {
                    'media': 0,
                    'mediana': 0,
                    'desvio_padrao': 0,
                    'contagem': 0,
                    'percentual': 0
                }
        
        return {
            'contagem': contagem,
            'percentual': {k: round(v, 2) for k, v in percentual.items()},
            'faixa_predominante': faixa_predominante,
            'total_valido': total,
            'estatisticas_faixas': estatisticas_faixas
        }
        
    except Exception as e:
        print(f"Erro ao analisar desempenho por faixa: {e}")
        return {
            'contagem': {},
            'percentual': {},
            'faixa_predominante': '',
            'total_valido': 0,
            'estatisticas_faixas': {}
        }


@optimized_cache(ttl=1800)
def analisar_metricas_por_regiao(
    df: pd.DataFrame, 
    colunas_notas: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Calcula métricas de desempenho por região.
    
    Parâmetros:
    -----------
    df: DataFrame
        DataFrame com os dados
    colunas_notas: List[str]
        Lista de colunas com notas
        
    Retorna:
    --------
    Dict[str, Dict[str, float]]: Dicionário com métricas por região
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or 'SG_UF_PROVA' not in df.columns:
        return {}
    
    try:
        # Criar coluna temporária com a região
        df_temp = df.copy()
        df_temp['REGIAO'] = df_temp['SG_UF_PROVA'].apply(obter_regiao_do_estado)
        
        # Remover valores vazios ou nulos na coluna de região
        df_temp = df_temp[df_temp['REGIAO'] != '']
        
        # Verificar se temos dados após filtragem
        if df_temp.empty:
            return {}
        
        # Calcular métricas por região
        resultados = {}
        for regiao in df_temp['REGIAO'].unique():
            dados_regiao = df_temp[df_temp['REGIAO'] == regiao]
            
            # Inicializar métricas para esta região
            metricas_regiao = {}
            
            # Calcular média para cada coluna de notas
            for coluna in colunas_notas:
                if coluna in dados_regiao.columns:
                    notas_validas = dados_regiao[dados_regiao[coluna] > 0][coluna]
                    if len(notas_validas) > 0:
                        metricas_regiao[coluna] = round(notas_validas.mean(), 2)
                    else:
                        metricas_regiao[coluna] = 0.0
            
            # Calcular média geral da região
            valores_validos = [v for v in metricas_regiao.values() if v > 0]
            if valores_validos:
                metricas_regiao['media_geral'] = round(sum(valores_validos) / len(valores_validos), 2)
            else:
                metricas_regiao['media_geral'] = 0.0
                
            # Adicionar total de candidatos
            metricas_regiao['total_candidatos'] = len(dados_regiao)
            
            # Adicionar ao resultado
            resultados[regiao] = metricas_regiao
        
        return resultados
        
    except Exception as e:
        print(f"Erro ao analisar métricas por região: {e}")
        return {}