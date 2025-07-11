import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from data.data_loader import calcular_seguro
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from utils.helpers.regiao_utils import obter_regiao_do_estado
from utils.helpers.mappings import get_mappings

# Obter mapeamentos e constantes
mappings = get_mappings()
competencia_mapping = mappings['competencia_mapping']
colunas_notas = mappings['colunas_notas']
CONFIG_PROCESSAMENTO = mappings['config_processamento']
LIMIARES_PROCESSAMENTO = mappings['limiares_processamento']
CONFIG_VISUALIZACAO = mappings['config_visualizacao']

@optimized_cache(ttl=1800)  # Cache válido por 30 minutos
def preparar_dados_histograma(
    df: pd.DataFrame, 
    coluna: str, 
    competencia_mapping: Dict[str, str]
) -> Tuple[pd.DataFrame, str, str]:
    """
    Prepara os dados para o histograma de notas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    coluna : str
        Nome da coluna (área de conhecimento) a ser analisada
    competencia_mapping : dict
        Dicionário com mapeamento das colunas para nomes legíveis
        
    Retorna:
    --------
    Tuple[DataFrame, str, str]: 
        - DataFrame filtrado com valores válidos
        - Nome da coluna para processamento
        - Nome da área para exibição
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or coluna not in df.columns:
        print(f"Aviso: DataFrame vazio ou coluna {coluna} ausente")
        return pd.DataFrame(), coluna, competencia_mapping.get(coluna, coluna)
    
    try:
        # Filtrar valores inválidos (notas -1 e 0) para análises mais precisas
        df_valido = df[(df[coluna] > 0) & (df[coluna].notna())].copy()
        
        # Converter para float32 para economizar memória
        if not df_valido.empty:
            df_valido[coluna] = df_valido[coluna].astype('float32')
            
        # Otimizar tipos de dados
        
        # Obter nome amigável da área de conhecimento
        nome_area = competencia_mapping.get(coluna, coluna)
        
        return df_valido, coluna, nome_area
    except Exception as e:
        print(f"Erro ao preparar dados para histograma: {e}")
        return pd.DataFrame(), coluna, competencia_mapping.get(coluna, coluna)


@optimized_cache(ttl=1800)
def preparar_dados_grafico_faltas(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    colunas_presenca: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Prepara os dados para o gráfico de faltas por estado e dia de prova.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : List[str]
        Lista de estados selecionados para análise
    colunas_presenca : Dict[str, str], opcional
        Dicionário mapeando as colunas de presença (mantido para compatibilidade)
        
    Retorna:
    --------
    DataFrame: Dados preparados para o gráfico de faltas por dia de prova
    """
    # Verificar se temos dados válidos
    if microdados_estados is None or microdados_estados.empty:
        print("Aviso: DataFrame de microdados vazio")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
    
    # Verificar se temos estados selecionados
    if not estados_selecionados:
        print("Aviso: Nenhum estado selecionado")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
    
    # Verificar se temos a coluna de UF
    if 'SG_UF_PROVA' not in microdados_estados.columns:
        print("Erro: Coluna 'SG_UF_PROVA' não encontrada nos dados")
        print(f"Colunas disponíveis: {list(microdados_estados.columns)[:10]}...")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
        
    # Verificar se temos a coluna de presença geral
    if 'TP_PRESENCA_GERAL' not in microdados_estados.columns:
        print("Erro: Coluna 'TP_PRESENCA_GERAL' não encontrada nos dados")
        print(f"Colunas disponíveis: {list(microdados_estados.columns)[:10]}...")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
    
    # Verificar se os estados selecionados existem nos dados
    estados_nos_dados = microdados_estados['SG_UF_PROVA'].unique()
    estados_validos = [estado for estado in estados_selecionados if estado in estados_nos_dados]
    
    if not estados_validos:
        print(f"Erro: Nenhum dos estados selecionados encontrado nos dados")
        print(f"Estados selecionados: {estados_selecionados}")
        print(f"Estados nos dados: {list(estados_nos_dados)[:10]}...")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
    
    if len(estados_validos) != len(estados_selecionados):
        estados_nao_encontrados = [e for e in estados_selecionados if e not in estados_validos]
        print(f"Aviso: Estados não encontrados nos dados: {estados_nao_encontrados}")
    
    print(f"Processando dados de faltas para {len(estados_validos)} estados")
    
    try:
        return _calcular_faltas_por_estado(microdados_estados, estados_validos)
    except Exception as e:
        print(f"Erro ao preparar dados para gráfico de faltas: {e}")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])


@memory_intensive_function
def _calcular_faltas_por_estado(
    df: pd.DataFrame, 
    estados: List[str]
) -> pd.DataFrame:
    """
    Calcula percentuais de faltas por estado e tipo de falta.
    Função auxiliar para melhorar legibilidade e manutenção.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    estados : List[str]
        Lista de estados para análise
        
    Retorna:
    --------
    DataFrame: Dados de faltas por estado
    """
    dados_grafico = []
    
    # Verificar se temos dados válidos
    if df is None or df.empty:
        print("Erro: DataFrame vazio em _calcular_faltas_por_estado")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
    
    if not estados:
        print("Erro: Lista de estados vazia")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
    
    # Processamento mais eficiente usando agrupamento
    try:
        grupos_estado = df.groupby('SG_UF_PROVA', observed=True)
        print(f"Agrupamento criado com {len(grupos_estado)} grupos")
    except Exception as e:
        print(f"Erro ao agrupar por estado: {e}")
        return pd.DataFrame(columns=['Estado', 'Tipo de Falta', 'Percentual de Faltas'])
        
    # Processar cada estado selecionado
    estados_processados = 0
    for i, estado in enumerate(estados):
        try:
            # Obter dados do estado atual
            dados_estado = grupos_estado.get_group(estado)
            estados_processados += 1
        except KeyError:
            # Estado não encontrado no agrupamento, pular
            print(f"Aviso: Estado '{estado}' não encontrado nos dados agrupados")
            continue
        except Exception as e:
            print(f"Erro ao processar estado '{estado}': {e}")
            continue
            
        total_candidatos = len(dados_estado)
        
        if total_candidatos == 0:
            print(f"Aviso: Nenhum candidato encontrado para o estado '{estado}'")
            continue  # Pular estados sem candidatos
        
        # Contagem de faltas por categoria
        categorias_faltas = {
            0: {'nome': 'Faltou nos dois dias', 'contagem': 0},
            1: {'nome': 'Faltou no segundo dia', 'contagem': 0},
            2: {'nome': 'Faltou no primeiro dia', 'contagem': 0}
        }
        
        # Contagem eficiente
        try:
            valores_presenca = dados_estado['TP_PRESENCA_GERAL'].value_counts()
        except Exception as e:
            print(f"Erro ao contar presenças para estado '{estado}': {e}")
            continue
        
        for codigo, info in categorias_faltas.items():
            contagem = valores_presenca.get(codigo, 0)
            percentual = (contagem / total_candidatos * 100) if total_candidatos > 0 else 0
            
            dados_grafico.append({
                'Estado': estado,
                'Tipo de Falta': info['nome'],
                'Percentual de Faltas': round(percentual, 2),
                'Contagem': contagem,
                'Total': total_candidatos
            })
            
        # Liberar memória a cada lote de estados processados
        if (i+1) % CONFIG_PROCESSAMENTO['tamanho_lote_estados'] == 0:
            release_memory(dados_estado)
    
    print(f"Processamento concluído: {estados_processados} estados processados de {len(estados)} solicitados")
    
    # Criar DataFrame otimizado
    df_resultado = pd.DataFrame(dados_grafico)
    
    # Converter para categorias para economia de memória
    if not df_resultado.empty:
        df_resultado['Estado'] = pd.Categorical(df_resultado['Estado'], categories=estados)
        df_resultado['Tipo de Falta'] = pd.Categorical(
            df_resultado['Tipo de Falta'], 
            categories=['Faltou nos dois dias', 'Faltou no primeiro dia', 'Faltou no segundo dia']
        )
        print(f"DataFrame resultado criado com {len(df_resultado)} linhas")
    else:
        print("Aviso: Nenhum dado de falta foi processado")
        
    return df_resultado


@optimized_cache(ttl=3600)  # Cache válido por 1 hora
def preparar_dados_metricas_principais(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    colunas_notas: List[str]
) -> Dict[str, Any]:
    """
    Prepara dados para as métricas principais exibidas no início da aba.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados filtrados por estado
    estados_selecionados : List[str]
        Lista de estados selecionados para análise
    colunas_notas : List[str]
        Lista de colunas com notas a serem analisadas
        
    Retorna:
    --------
    Dict[str, Any]: Dicionário com métricas calculadas
    """
    # Verificar se temos dados válidos
    if microdados_estados is None or microdados_estados.empty:
        print("Aviso: DataFrame de microdados vazio")
        return _gerar_metricas_vazias(colunas_notas)
    
    try:
        # Calculando métricas básicas
        total_candidatos = len(microdados_estados)
        
        # Calcular percentual de faltas (candidatos que faltaram nos dois dias)
        if 'TP_PRESENCA_GERAL' in microdados_estados.columns:
            faltas_totais = len(microdados_estados[microdados_estados['TP_PRESENCA_GERAL'] == 0])
            percentual_faltas = (faltas_totais / total_candidatos * 100) if total_candidatos > 0 else 0
        else:
            faltas_totais = 0
            percentual_faltas = 0
        
        # Calcular médias por área de conhecimento
        medias = {}
        for coluna in colunas_notas:
            if coluna in microdados_estados.columns:
                notas_validas = microdados_estados[microdados_estados[coluna] > 0][coluna]
                media = calcular_seguro(notas_validas, 'media')
                medias[coluna] = round(media, 2)
            else:
                medias[coluna] = None
        
        # Calcular média geral
        medias_validas = [v for v in medias.values() if v is not None]
        media_geral = round(sum(medias_validas) / len(medias_validas), 2) if medias_validas else 0
        
        # Calcular desempenho por regiões
        desempenho_regioes = _calcular_desempenho_regioes(
            microdados_estados, 
            estados_selecionados, 
            colunas_notas
        )
        
        # Montar resultado final
        return {
            'total_candidatos': total_candidatos,
            'faltas_totais': faltas_totais,
            'percentual_faltas': percentual_faltas,
            'medias_por_area': medias,
            'media_geral': media_geral,
            'desempenho_regioes': desempenho_regioes
        }
    except Exception as e:
        print(f"Erro ao preparar métricas principais: {e}")
        return _gerar_metricas_vazias(colunas_notas)


def _gerar_metricas_vazias(colunas_notas: List[str]) -> Dict[str, Any]:
    """
    Gera estrutura de métricas vazia quando não há dados disponíveis.
    
    Parâmetros:
    -----------
    colunas_notas : List[str]
        Lista de colunas de notas para inicializar estrutura vazia
        
    Retorna:
    --------
    Dict[str, Any]: Estrutura de métricas vazia
    """
    return {
        'total_candidatos': 0,
        'faltas_totais': 0,
        'percentual_faltas': 0,
        'medias_por_area': {coluna: 0 for coluna in colunas_notas},
        'media_geral': 0,
        'desempenho_regioes': {}
    }


@memory_intensive_function
def _calcular_desempenho_regioes(
    df: pd.DataFrame, 
    estados: List[str], 
    colunas_notas: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Calcula desempenho médio por região para todas as áreas de conhecimento.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    estados : List[str]
        Lista de estados selecionados
    colunas_notas : List[str]
        Lista de colunas com notas
        
    Retorna:
    --------
    Dict[str, Dict[str, float]]: Médias por região e área de conhecimento
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or 'SG_UF_PROVA' not in df.columns:
        return {}
        
    # Adicionar coluna de região
    df_temp = df.copy()
    df_temp['REGIAO'] = df_temp['SG_UF_PROVA'].apply(obter_regiao_do_estado)
    
    # Calcular médias por região e área
    resultado = {}
    regioes = df_temp['REGIAO'].unique()
    
    for regiao in regioes:
        if not regiao:  # Ignorar valores vazios
            continue
            
        dados_regiao = df_temp[df_temp['REGIAO'] == regiao]
        
        medias_regiao = {}
        for coluna in colunas_notas:
            if coluna in dados_regiao.columns:
                notas_validas = dados_regiao[dados_regiao[coluna] > 0][coluna]
                media = calcular_seguro(notas_validas, 'media')
                medias_regiao[coluna] = round(media, 2)
            else:
                medias_regiao[coluna] = None
                
        resultado[regiao] = medias_regiao
    
    # Liberar memória
    release_memory(df_temp)
    
    return resultado


@optimized_cache(ttl=3600)
def preparar_dados_media_geral_estados(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    colunas_notas: List[str], 
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Prepara dados para visualização da média geral por estado ou região.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados filtrados por estado
    estados_selecionados : List[str]
        Lista de estados selecionados para análise
    colunas_notas : List[str]
        Lista de colunas com notas a serem analisadas
    agrupar_por_regiao : bool, default=False
        Se True, agrupa os dados por região em vez de mostrar por estado
        
    Retorna:
    --------
    DataFrame: Dados de média geral por estado ou região
    """
    # Verificar se temos dados válidos
    if microdados_estados is None or microdados_estados.empty:
        print("Aviso: DataFrame de microdados vazio")
        return pd.DataFrame(columns=['Local', 'Média Geral'])
    
    try:
        # Agrupar os dados por estado
        if 'SG_UF_PROVA' not in microdados_estados.columns:
            print("Erro: Coluna 'SG_UF_PROVA' não encontrada nos dados")
            return pd.DataFrame(columns=['Local', 'Média Geral'])
            
        resultado = []
        
        # Processo eficiente usando agrupamento
        grupos_estado = microdados_estados.groupby('SG_UF_PROVA')
        
        for estado in estados_selecionados:
            try:
                dados_estado = grupos_estado.get_group(estado)
            except KeyError:
                continue  # Estado não encontrado, pular
                
            # Calcular médias por área de conhecimento
            medias_estado = []
            for coluna in colunas_notas:
                if coluna in dados_estado.columns:
                    notas_validas = dados_estado[dados_estado[coluna] > 0][coluna]
                    if len(notas_validas) > 0:
                        media = calcular_seguro(notas_validas, 'media')
                        medias_estado.append(media)
            
            # Calcular média geral do estado
            if medias_estado:
                media_geral = sum(medias_estado) / len(medias_estado)
                resultado.append({
                    'Local': estado,
                    'Média Geral': round(media_geral, 2)
                })
        
        # Criar DataFrame
        df_resultado = pd.DataFrame(resultado)
        
        # Agrupar por região se solicitado
        if agrupar_por_regiao and not df_resultado.empty:
            df_resultado = _agrupar_estados_por_regiao(df_resultado)
            
        return df_resultado
    except Exception as e:
        print(f"Erro ao preparar dados de média geral por estado: {e}")
        return pd.DataFrame(columns=['Local', 'Média Geral'])


def _agrupar_estados_por_regiao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa estados por região, calculando a média dos valores numéricos.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados por estado, com coluna 'Local' contendo os estados
        
    Retorna:
    --------
    DataFrame: DataFrame com dados agrupados por região
    """
    # Verificar se temos dados para processar
    if df is None or df.empty or 'Local' not in df.columns:
        return df
    
    try:
        # Criar coluna de região
        df_temp = df.copy()
        df_temp['Região'] = df_temp['Local'].apply(obter_regiao_do_estado)
        
        # Remover estados sem região associada
        df_temp = df_temp[df_temp['Região'] != ""]
        
        # Agrupar por região
        colunas_numericas = df_temp.select_dtypes(include='number').columns.tolist()
        df_agrupado = df_temp.groupby('Região')[colunas_numericas].mean().reset_index()
        
        # Renomear coluna para manter compatibilidade
        df_agrupado = df_agrupado.rename(columns={'Região': 'Local'})
        
        # Arredondar valores numéricos
        for col in colunas_numericas:
            df_agrupado[col] = df_agrupado[col].round(2)
            
        return df_agrupado
    except Exception as e:
        print(f"Erro ao agrupar estados por região: {e}")
        return df


@optimized_cache(ttl=3600)
def preparar_dados_evasao(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str]
) -> pd.DataFrame:
    """
    Prepara dados de evasão (faltas) dos candidatos por estado.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados filtrados por estado
    estados_selecionados : List[str]
        Lista de estados selecionados para análise
        
    Retorna:
    --------
    DataFrame: Dados de evasão por estado
    """
    # Verificar se temos dados válidos
    if microdados_estados is None or microdados_estados.empty:
        print("Aviso: DataFrame de microdados vazio")
        return pd.DataFrame(columns=['Estado', 'Métrica', 'Valor'])
        
    # Verificar se temos as colunas necessárias
    colunas_necessarias = ['SG_UF_PROVA', 'TP_PRESENCA_GERAL']
    if not all(col in microdados_estados.columns for col in colunas_necessarias):
        print("Erro: Colunas necessárias ausentes")
        return pd.DataFrame(columns=['Estado', 'Métrica', 'Valor'])
    
    try:
        resultado = []
        
        # Processamento eficiente usando agrupamento
        grupos_estado = microdados_estados.groupby('SG_UF_PROVA')
        
        for estado in estados_selecionados:
            try:
                dados_estado = grupos_estado.get_group(estado)
            except KeyError:
                continue  # Estado não encontrado, pular
                
            total_candidatos = len(dados_estado)
            
            # Contar presença/ausência
            presenca_counts = dados_estado['TP_PRESENCA_GERAL'].value_counts()
            
            # Faltou nos dois dias (código 0)
            faltas_ambos = presenca_counts.get(0, 0)
            
            # Faltou no segundo dia (código 1 - presente apenas no primeiro)
            faltas_dia2 = presenca_counts.get(1, 0)
            
            # Faltou no primeiro dia (código 2 - presente apenas no segundo)
            faltas_dia1 = presenca_counts.get(2, 0)
            
            # Presente nos dois dias (código 3)
            presentes = presenca_counts.get(3, 0)
            
            # Calcular percentuais
            if total_candidatos > 0:
                percentual_faltas_ambos = (faltas_ambos / total_candidatos) * 100
                percentual_faltas_dia1 = (faltas_dia1 / total_candidatos) * 100
                percentual_faltas_dia2 = (faltas_dia2 / total_candidatos) * 100
                percentual_presentes = (presentes / total_candidatos) * 100
            else:
                percentual_faltas_ambos = 0
                percentual_faltas_dia1 = 0
                percentual_faltas_dia2 = 0
                percentual_presentes = 0
                
            # Adicionar dados ao resultado
            resultado.extend([
                {'Estado': estado, 'Métrica': 'Presentes', 'Valor': round(percentual_presentes, 2), 'Contagem': presentes},
                {'Estado': estado, 'Métrica': 'Faltantes Dia 1', 'Valor': round(percentual_faltas_dia1, 2), 'Contagem': faltas_dia1},
                {'Estado': estado, 'Métrica': 'Faltantes Dia 2', 'Valor': round(percentual_faltas_dia2, 2), 'Contagem': faltas_dia2},
                {'Estado': estado, 'Métrica': 'Faltantes Ambos', 'Valor': round(percentual_faltas_ambos, 2), 'Contagem': faltas_ambos}
            ])
        
        # Criar DataFrame otimizado
        df_resultado = pd.DataFrame(resultado)
        
        # Converter para categorias para economia de memória
        if not df_resultado.empty:
            df_resultado['Estado'] = pd.Categorical(df_resultado['Estado'], categories=estados_selecionados)
            df_resultado['Métrica'] = pd.Categorical(
                df_resultado['Métrica'], 
                categories=['Presentes', 'Faltantes Dia 1', 'Faltantes Dia 2', 'Faltantes Ambos']
            )
            
    except Exception as e:
        print(f"Erro ao preparar dados de evasão: {e}")
        return pd.DataFrame(columns=['Estado', 'Métrica', 'Valor'])


@optimized_cache(ttl=3600)
def preparar_dados_comparativo_areas(
    microdados_estados: pd.DataFrame,
    estados_selecionados: List[str],
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Prepara dados para comparativo de desempenho entre diferentes áreas de conhecimento.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados filtrados por estado
    estados_selecionados : List[str]
        Lista de estados selecionados para análise
    colunas_notas : List[str]
        Lista de colunas com notas a serem analisadas
    competencia_mapping : Dict[str, str]
        Mapeamento entre códigos de competência e nomes legíveis
        
    Retorna:
    --------
    DataFrame: Dados de desempenho médio por área de conhecimento
    """
    # Verificar se temos dados válidos
    if microdados_estados is None or microdados_estados.empty:
        print("Aviso: DataFrame de microdados vazio")
        return pd.DataFrame(columns=['Area', 'Media', 'DesvioPadrao', 'Mediana'])
    
    # Verificar se temos as colunas de notas
    colunas_ausentes = [col for col in colunas_notas if col not in microdados_estados.columns]
    if colunas_ausentes:
        print(f"Aviso: Colunas ausentes: {colunas_ausentes}")
    
    try:
        resultado = []
        
        for coluna in colunas_notas:
            if coluna not in microdados_estados.columns:
                continue
                
            # Filtrar notas válidas
            notas_validas = microdados_estados[microdados_estados[coluna] > 0][coluna]
            
            if len(notas_validas) > 0:
                # Calcular estatísticas
                media = calcular_seguro(notas_validas, 'media')
                mediana = calcular_seguro(notas_validas, 'mediana')
                desvio = calcular_seguro(notas_validas, 'desvio')
                
                # Obter nome legível da área
                nome_area = competencia_mapping.get(coluna, coluna)
                
                resultado.append({
                    'Area': nome_area,
                    'Media': round(media, 2),
                    'DesvioPadrao': round(desvio, 2),
                    'Mediana': round(mediana, 2),
                    'Minimo': round(float(notas_validas.min()), 2),
                    'Maximo': round(float(notas_validas.max()), 2)
                })
        
        # Criar DataFrame
        df_resultado = pd.DataFrame(resultado)
        
        # Ordenar por média decrescente
        if not df_resultado.empty:
            df_resultado = df_resultado.sort_values('Media', ascending=False)
            
        return df_resultado
    except Exception as e:
        print(f"Erro ao preparar dados comparativos entre áreas: {e}")
        return pd.DataFrame(columns=['Area', 'Media', 'DesvioPadrao', 'Mediana'])