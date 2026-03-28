import pandas as pd
import warnings
from typing import Dict, List, Tuple, Optional, Any, Union
from data.data_loader import calcular_seguro
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from utils.prepara_dados.validacao_dados import validar_completude_dados
from utils.helpers.constants import (
    COMPETENCIA_MAPPING as competencia_mapping,
    COLUNAS_NOTAS as colunas_notas,
    CONFIG_PROCESSAMENTO,
    LIMIARES_PROCESSAMENTO,
)

# Suprimir warnings específicos do pandas
warnings.filterwarnings('ignore', message='The default of observed=False is deprecated')
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')

@optimized_cache(ttl=1800)  # Cache válido por 30 minutos
def preparar_dados_comparativo(
    microdados_full: pd.DataFrame, 
    variavel_selecionada: str, 
    variaveis_categoricas: Dict[str, Dict[str, Any]], 
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Prepara os dados para análise comparativa de desempenho por variável categórica.
    
    Parâmetros:
    -----------
    microdados_full : DataFrame
        DataFrame com os dados completos
    variavel_selecionada : str
        Nome da variável categórica selecionada para análise
    variaveis_categoricas : Dict
        Dicionário com metadados das variáveis categóricas
    colunas_notas : List[str]
        Lista das colunas que contêm as notas a serem analisadas
    competencia_mapping : Dict
        Mapeamento de códigos de competência para nomes legíveis
        
    Retorna:
    --------
    DataFrame: DataFrame pronto para visualização com médias por categoria e competência
    """
    # Verificar se temos dados de entrada válidos
    if microdados_full is None or microdados_full.empty:
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    # Verificar se a variável selecionada existe nos dados
    if variavel_selecionada not in microdados_full.columns:
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    # Verificar se temos as colunas de notas
    colunas_notas_disponiveis = [col for col in colunas_notas if col in microdados_full.columns]
    if not colunas_notas_disponiveis:
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    # Verificar se temos dados suficientes
    colunas_necessarias = [variavel_selecionada] + colunas_notas_disponiveis
    dados_validos, taxas_completude = validar_completude_dados(
        microdados_full, 
        colunas_necessarias,
        limiar_completude=LIMIARES_PROCESSAMENTO['min_completude_dados']
    )
    
    if not dados_validos:
        # Continuar processamento com dados disponíveis
        pass
    # Selecionar apenas colunas necessárias para economizar memória
    df_trabalho = microdados_full[colunas_necessarias].copy()
    
    # Remover registros com valores inválidos na variável categórica
    df_trabalho = df_trabalho.dropna(subset=[variavel_selecionada])
    
    # Verificar se ainda temos dados após limpeza
    if df_trabalho.empty:
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    # Determinar mapeamento de valores e nome da coluna a ser usada
    nome_coluna_mapeada = variavel_selecionada
    mapeamento = None
    
    if variavel_selecionada in variaveis_categoricas and "mapeamento" in variaveis_categoricas[variavel_selecionada]:
        mapeamento = variaveis_categoricas[variavel_selecionada]["mapeamento"]
    
    # Calcular médias para cada combinação categoria-competência
    resultados = _calcular_medias_por_categoria(
        df_trabalho, 
        nome_coluna_mapeada, 
        colunas_notas_disponiveis,  # Usar apenas colunas disponíveis
        competencia_mapping,
        mapeamento
    )
    
    df_resultados = pd.DataFrame(resultados)
    
    # Verificar se obtivemos resultados
    if df_resultados.empty:
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    
    # Aplicar ordem categórica se disponível no mapeamento
    if (variavel_selecionada in variaveis_categoricas and 
        "ordem" in variaveis_categoricas[variavel_selecionada]):
        ordem = variaveis_categoricas[variavel_selecionada]["ordem"]
        
        # Filtrar a ordem para incluir apenas categorias presentes nos dados
        categorias_presentes = df_resultados['Categoria'].unique()
        ordem_filtrada = [cat for cat in ordem if cat in categorias_presentes]
        
        # Verificar se temos categorias não mapeadas e adicionar ao final
        categorias_nao_mapeadas = [cat for cat in categorias_presentes if cat not in ordem_filtrada]
        ordem_final = ordem_filtrada + sorted(categorias_nao_mapeadas)
        
        # Definir a ordem categórica
        df_resultados['Categoria'] = pd.Categorical(
            df_resultados['Categoria'],
            categories=ordem_final,
            ordered=True
        )
        
        # Ordenar o DataFrame pela ordem categórica
        df_resultados = df_resultados.sort_values('Categoria')
    
    # Liberar memória da cópia de trabalho
    release_memory(df_trabalho)
    
    # Retornar dataframe otimizado
    return df_resultados


@memory_intensive_function
def _calcular_medias_por_categoria(
    df: pd.DataFrame,
    coluna_categoria: str,
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str],
    mapeamento: Optional[Dict[Any, str]] = None
) -> List[Dict[str, Any]]:
    """
    Calcula médias de desempenho para cada combinação de categoria e competência.
    Versão vetorizada — usa groupby + mean em vez de loops com calcular_seguro.

    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados filtrados
    coluna_categoria : str
        Nome da coluna que contém as categorias
    colunas_notas : List[str]
        Lista das colunas que contêm as notas
    competencia_mapping : Dict
        Mapeamento de códigos de competência para nomes legíveis
    mapeamento : Dict, opcional
        Mapeamento de valores numéricos de categoria para textos legíveis

    Retorna:
    --------
    List[Dict[str, Any]]: Lista de dicionários com os resultados calculados
    """
    if df.empty or coluna_categoria not in df.columns:
        return []

    # Filtrar apenas colunas disponíveis
    colunas_disponiveis = [c for c in colunas_notas if c in df.columns]
    if not colunas_disponiveis:
        return []

    # Remover NaN na coluna de categoria
    df_trabalho = df[[coluna_categoria] + colunas_disponiveis].dropna(subset=[coluna_categoria])
    if df_trabalho.empty:
        return []

    # Substituir notas <= 0 por NaN para que groupby.mean() as ignore
    df_trabalho[colunas_disponiveis] = df_trabalho[colunas_disponiveis].where(
        df_trabalho[colunas_disponiveis] > 0
    )

    # UMA operação vetorizada: groupby + mean para todas as combinações
    medias_df = df_trabalho.groupby(coluna_categoria, observed=True)[colunas_disponiveis].mean()

    # Construir resultados a partir do DataFrame de médias
    resultados = []
    for categoria in medias_df.index:
        categoria_exibicao = mapeamento.get(categoria, str(categoria)) if mapeamento else str(categoria)

        for competencia in colunas_disponiveis:
            media_val = medias_df.loc[categoria, competencia]
            media_comp = round(float(media_val), 2) if pd.notna(media_val) else 0

            competencia_nome = competencia_mapping.get(competencia, competencia)
            resultados.append({
                'Categoria': categoria_exibicao,
                'Competência': competencia_nome,
                'Média': media_comp
            })

    return resultados


@optimized_cache(ttl=1800)
def preparar_dados_grafico_linha(
    df_resultados: pd.DataFrame, 
    competencia_ordenacao: Optional[str] = None, 
    competencia_filtro: Optional[str] = None, 
    ordenar_decrescente: bool = False
) -> pd.DataFrame:
    """
    Prepara os dados para o gráfico de linha de desempenho por categoria.
    
    Parâmetros:
    -----------
    df_resultados : DataFrame
        DataFrame com os resultados das médias por categoria e competência
    competencia_ordenacao : str, opcional
        Competência usada para ordenar as categorias (se ordenar_decrescente=True)
    competencia_filtro : str, opcional
        Filtrar para mostrar apenas esta competência
    ordenar_decrescente : bool, default=False
        Se True, ordena as categorias por valor decrescente da competência de ordenação
        
    Retorna:
    --------
    DataFrame: DataFrame preparado para visualização em gráfico de linha
    """
    try:
        # Verificar se temos dados para processar
        if df_resultados is None:
            return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
            
        if df_resultados.empty:
            return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
        
        # Trabalhar com uma cópia dos dados
        df_linha = df_resultados.copy()
        
        # Filtrar por competência específica, se solicitado
        if competencia_filtro is not None:
            df_linha = df_linha[df_linha['Competência'] == competencia_filtro]
        
        # Aplicar ordenação por valor se solicitado
        if ordenar_decrescente:
            # Se não for especificada uma competência de ordenação, use a que está filtrada
            # ou a primeira competência disponível
            if competencia_ordenacao is None:
                if competencia_filtro is not None:
                    competencia_ordenacao = competencia_filtro
                else:
                    competencias_disponiveis = df_resultados['Competência'].unique()
                    if len(competencias_disponiveis) > 0:
                        competencia_ordenacao = competencias_disponiveis[0]
            
            # Verificar se temos uma competência válida para ordenação
            if competencia_ordenacao is not None:
                # Obter ordem das categorias com base na competência de ordenação
                df_ordem = df_resultados[df_resultados['Competência'] == competencia_ordenacao]
                
                if not df_ordem.empty:
                    # Ordenar por média decrescente
                    ordem_categorias = df_ordem.sort_values('Média', ascending=False)['Categoria'].unique().tolist()
                    
                    # Aplicar essa ordem como tipo categórico ordenado
                    df_linha['Categoria'] = pd.Categorical(
                        df_linha['Categoria'], 
                        categories=ordem_categorias, 
                        ordered=True
                    )
                    
                    # Forçar a ordenação do DataFrame
                    df_linha = df_linha.sort_values('Categoria')
                    
                    # Importante: Marcar o DataFrame como tendo ordem aplicada
                    df_linha.attrs['ordenado'] = True
        
        return df_linha
        
    except Exception as e:
        # Sempre retornar um DataFrame válido, mesmo em caso de erro
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])


def obter_ordem_categorias(
    df_resultados: pd.DataFrame, 
    variavel_selecionada: str, 
    variaveis_categoricas: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Determina a ordem das categorias para exibição no gráfico.
    
    Parâmetros:
    -----------
    df_resultados : DataFrame
        DataFrame com os dados de resultados
    variavel_selecionada : str
        Nome da variável categórica selecionada
    variaveis_categoricas : Dict
        Dicionário com metadados das variáveis categóricas
        
    Retorna:
    --------
    List[str]: Lista com a ordem das categorias para exibição
    """
    # Verificar se temos dados para processar
    if df_resultados.empty:
        return []
        
    categorias_unicas = df_resultados['Categoria'].unique()
    
    # Verificar se existe uma ordem predefinida para esta variável
    if variavel_selecionada in variaveis_categoricas and 'ordem' in variaveis_categoricas[variavel_selecionada]:
        # Obter ordem predefinida e filtrar para incluir apenas categorias presentes nos dados
        ordem_definida = variaveis_categoricas[variavel_selecionada]['ordem']
        ordem_filtrada = [cat for cat in ordem_definida if cat in categorias_unicas]
        
        # Adicionar categorias que estão nos dados mas não na ordem predefinida
        categorias_faltantes = [cat for cat in categorias_unicas if cat not in ordem_filtrada]
        return ordem_filtrada + sorted(categorias_faltantes)
    
    # Usar ordem alfabética como padrão
    return sorted(categorias_unicas)


@optimized_cache(ttl=3600)
def preparar_dados_desempenho_geral(
    microdados: pd.DataFrame, 
    colunas_notas: List[str], 
    desempenho_mapping: Dict[int, str]
) -> pd.DataFrame:
    """
    Prepara dados gerais de desempenho, incluindo categorias de desempenho.
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com os microdados originais
    colunas_notas : List[str]
        Lista de colunas de notas a serem consideradas
    desempenho_mapping : Dict
        Mapeamento de códigos numéricos para categorias de desempenho
        
    Retorna:
    --------
    DataFrame: DataFrame com dados preparados e categoria de desempenho adicionada
    """
    # Verificar se temos dados para processar
    if microdados is None or microdados.empty:
        return pd.DataFrame()
    
      
    # Determinar quais colunas vamos precisar (notas + demografia)
    colunas_necessarias = list(colunas_notas)
    
    # Adicionar colunas demográficas que existem no DataFrame
    from utils.helpers.constants import VARIAVEIS_CATEGORICAS
    for col in VARIAVEIS_CATEGORICAS:
        if col in microdados.columns:
            colunas_necessarias.append(col)
    
    # Adicionar coluna de desempenho se existir
    if 'NU_DESEMPENHO' in microdados.columns:
        colunas_necessarias.append('NU_DESEMPENHO')
    
    # Criar cópia otimizada do DataFrame com apenas as colunas necessárias
    microdados_full = microdados[colunas_necessarias].copy()
    
    # Adicionar categoria de desempenho se existir a coluna
    if 'NU_DESEMPENHO' in microdados_full.columns:
        microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['NU_DESEMPENHO'].map(desempenho_mapping)
        
        # Converter para categoria para economizar memória
        if not microdados_full['CATEGORIA_DESEMPENHO'].isna().all():
            microdados_full['CATEGORIA_DESEMPENHO'] = microdados_full['CATEGORIA_DESEMPENHO'].astype('category')
    
    return microdados_full


@optimized_cache(ttl=1800)
def filtrar_dados_scatter(
    dados: pd.DataFrame, 
    filtro_sexo: Optional[str], 
    filtro_tipo_escola: Optional[str], 
    eixo_x: str, 
    eixo_y: str, 
    excluir_notas_zero: bool = True, 
    filtro_raca: Optional[str] = None,
    filtro_faixa_salarial: Optional[Union[int, List[int]]] = None,
    max_amostras: int = CONFIG_PROCESSAMENTO['max_amostras_scatter']
) -> Tuple[pd.DataFrame, int]:
    """
    Filtra dados para visualização de gráfico de dispersão.
    
    Parâmetros:
    -----------
    dados : DataFrame
        DataFrame com os dados completos
    filtro_sexo : str, opcional
        Filtro para sexo específico ('M' ou 'F')
    filtro_tipo_escola : str, opcional
        Filtro para tipo de escola ('Pública' ou 'Privada')
    eixo_x : str
        Coluna a ser usada no eixo X
    eixo_y : str
        Coluna a ser usada no eixo Y
    excluir_notas_zero : bool, default=True
        Se True, exclui registros com notas zero
    filtro_raca : str, opcional
        Filtro para raça/cor específica
    filtro_faixa_salarial : Union[int, List[int]], opcional
        Filtro para faixa salarial específica (valor único) ou lista de faixas salariais
    max_amostras : int, default=50000
        Número máximo de amostras para o gráfico de dispersão
        
    Retorna:
    --------
    Tuple[DataFrame, int]: DataFrame filtrado e quantidade de registros removidos
    """
    # Verificar se temos dados válidos
    if dados.empty or eixo_x not in dados.columns or eixo_y not in dados.columns:
        return pd.DataFrame(), 0
    
    # Determinar colunas necessárias para a análise
    colunas_necessarias = [eixo_x, eixo_y]
    
    # Adicionar colunas de filtro se necessárias
    for coluna, filtro in [
        ('TP_SEXO', filtro_sexo),
        ('TP_DEPENDENCIA_ADM_ESC', filtro_tipo_escola),
        ('TP_COR_RACA', filtro_raca),
        ('TP_FAIXA_SALARIAL', filtro_faixa_salarial)
    ]:
        if filtro is not None and coluna in dados.columns:
            colunas_necessarias.append(coluna)
    
    # Adicionar TP_FAIXA_SALARIAL se colorir por faixa estiver ativo
    if 'TP_FAIXA_SALARIAL' in dados.columns and 'TP_FAIXA_SALARIAL' not in colunas_necessarias:
        colunas_necessarias.append('TP_FAIXA_SALARIAL')
    
    # Selecionar colunas e criar cópia
    df = dados[colunas_necessarias].copy()
    tamanho_inicial = len(df)
    
    # Aplicar filtros de forma mais robusta - usar sempre método manual
    try:
        # Aplicar filtro de notas zero primeiro
        if excluir_notas_zero:
            df = df[(df[eixo_x] > 0) & (df[eixo_y] > 0)]
        
        # Aplicar filtros demográficos manualmente
        if filtro_sexo and filtro_sexo != 'Todos' and 'TP_SEXO' in df.columns:
            df = df[df['TP_SEXO'].isin([filtro_sexo, str(filtro_sexo)])]
            
        if filtro_tipo_escola and filtro_tipo_escola != 'Todos' and 'TP_DEPENDENCIA_ADM_ESC' in df.columns:
            if filtro_tipo_escola == 'Pública':
                df = df[df['TP_DEPENDENCIA_ADM_ESC'].isin([1, 2, 3, '1', '2', '3', 1.0, 2.0, 3.0])]
            elif filtro_tipo_escola == 'Privada':
                df = df[df['TP_DEPENDENCIA_ADM_ESC'].isin([4, '4', 4.0])]
                
        if filtro_raca and 'TP_COR_RACA' in df.columns:
            df = df[df['TP_COR_RACA'] == filtro_raca]
            
        if filtro_faixa_salarial is not None and 'TP_FAIXA_SALARIAL' in df.columns:
            if isinstance(filtro_faixa_salarial, list):
                valores_aceitos = []
                for f in filtro_faixa_salarial:
                    valores_aceitos.extend([f, str(f), float(f)])
                df = df[df['TP_FAIXA_SALARIAL'].isin(valores_aceitos)]
            else:
                df = df[df['TP_FAIXA_SALARIAL'].isin([filtro_faixa_salarial, str(filtro_faixa_salarial), float(filtro_faixa_salarial)])]
                
    except Exception as e:
        # Em caso de erro, aplicar apenas filtro básico
        if excluir_notas_zero:
            df = df[(df[eixo_x] > 0) & (df[eixo_y] > 0)]
    
    # Remover valores NaN nos eixos
    df = df.dropna(subset=[eixo_x, eixo_y])
    
    # Limitar número de amostras para performance
    if len(df) > max_amostras:
        df = df.sample(n=max_amostras, random_state=42)
    
    # Calcular registros removidos
    registros_removidos = tamanho_inicial - len(df)
    
    return df, registros_removidos


@optimized_cache(ttl=3600)
def preparar_dados_grafico_linha_desempenho(
    microdados_estados: pd.DataFrame, 
    estados_selecionados: List[str], 
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str], 
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Prepara dados para o gráfico de linha que mostra o desempenho médio por estado ou região.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os dados dos candidatos filtrados por estado
    estados_selecionados : List[str]
        Lista de estados selecionados para análise
    colunas_notas : List[str]
        Lista de colunas com notas a serem analisadas
    competencia_mapping : Dict
        Dicionário de mapeamento de códigos de competência para nomes legíveis
    agrupar_por_regiao : bool, default=False
        Se True, agrupa os dados por região em vez de mostrar por estado
        
    Retorna:
    --------
    DataFrame: DataFrame com os dados preparados para visualização
    """
    # Verificar se temos dados válidos
    if microdados_estados.empty or not estados_selecionados:
        return pd.DataFrame()
    
    # Verificar se temos a coluna de UF
    if 'SG_UF_PROVA' not in microdados_estados.columns:
        return pd.DataFrame()
    
    # Usar processamento em lotes para reduzir uso de memória
    resultados = _processar_estados_em_lotes(
        microdados_estados, 
        estados_selecionados, 
        colunas_notas, 
        competencia_mapping
    )
    
    # Criar DataFrame otimizado
    df_final = pd.DataFrame(resultados)
    
    # Se não houver dados, retornar DataFrame vazio
    if df_final.empty:
        return df_final
    
    # Otimizar tipos de dados usando categorias
    df_final = _otimizar_tipos_dados(df_final, estados_selecionados, competencia_mapping)
    
    # Agrupar por região se solicitado
    if agrupar_por_regiao:
        df_final = _agrupar_por_regiao(df_final)
    
    return df_final


@memory_intensive_function
def _processar_estados_em_lotes(
    microdados: pd.DataFrame,
    estados: List[str],
    colunas_notas: List[str],
    competencia_mapping: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Calcula médias de desempenho por estado e competência.
    Versão vetorizada — usa groupby + mean em vez de loops com calcular_seguro.

    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com os dados
    estados : List[str]
        Lista de estados a processar
    colunas_notas : List[str]
        Colunas com notas a processar
    competencia_mapping : Dict
        Mapeamento de códigos para nomes de competências

    Retorna:
    --------
    List[Dict[str, Any]]: Lista de resultados calculados
    """
    if microdados.empty or 'SG_UF_PROVA' not in microdados.columns:
        return []

    colunas_disponiveis = [c for c in colunas_notas if c in microdados.columns]
    if not colunas_disponiveis:
        return []

    try:
        # Filtrar estados solicitados e colunas necessárias
        df = microdados[microdados['SG_UF_PROVA'].isin(estados)][['SG_UF_PROVA'] + colunas_disponiveis].copy()

        # Substituir notas <= 0 por NaN para que mean() as ignore
        df[colunas_disponiveis] = df[colunas_disponiveis].where(df[colunas_disponiveis] > 0)

        # UMA operação vetorizada: groupby + mean
        medias_df = df.groupby('SG_UF_PROVA', observed=True)[colunas_disponiveis].mean()

        # Construir resultados
        resultados = []
        for estado in estados:
            if estado not in medias_df.index:
                continue

            medias_estado = []
            for area in colunas_disponiveis:
                media_val = medias_df.loc[estado, area]
                media_area = round(float(media_val), 2) if pd.notna(media_val) else 0.0

                resultados.append({
                    'Estado': estado,
                    'Área': competencia_mapping.get(area, area),
                    'Média': media_area
                })
                if media_area > 0:
                    medias_estado.append(media_area)

            # Média geral do estado
            if medias_estado:
                resultados.append({
                    'Estado': estado,
                    'Área': 'Média Geral',
                    'Média': round(sum(medias_estado) / len(medias_estado), 2)
                })

        return resultados

    except Exception as e:
        import logging; logging.warning(f"Erro em _processar_estados_em_lotes: {e}")
        return []


def _otimizar_tipos_dados(
    df: pd.DataFrame, 
    estados: List[str], 
    competencia_mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Otimiza tipos de dados do DataFrame para economizar memória.
    Função auxiliar para melhorar legibilidade e manutenção.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame a otimizar
    estados : List[str]
        Lista de estados para usar como categorias
    competencia_mapping : Dict
        Mapeamento de competências para usar como categorias
        
    Retorna:
    --------
    DataFrame: DataFrame com tipos otimizados
    """
    # Converter colunas para tipos categóricos
    areas_unicas = list(competencia_mapping.values()) + ['Média Geral']
    
    # Usar try/except para cada conversão para evitar erros
    try:
        df['Área'] = pd.Categorical(df['Área'], categories=areas_unicas)
    except Exception as e:
        pass
    
    try:
        df['Estado'] = pd.Categorical(df['Estado'], categories=estados)
    except Exception as e:
        pass
    
    # Otimizar coluna numérica
    try:
        df['Média'] = df['Média'].astype('float32')
    except Exception as e:
        pass
    return df


def _agrupar_por_regiao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os dados por região em vez de por estado.
    Função auxiliar para melhorar legibilidade e manutenção.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados por estado
        
    Retorna:
    --------
    DataFrame: DataFrame com dados agrupados por região
    """
    # Importar localmente para evitar importação circular
    from utils.helpers.mappings import get_mappings
    mappings = get_mappings()
    regioes_mapping = mappings['regioes_mapping']
    
    # Verificar se temos dados para processar
    if df is None or df.empty:
        return df
    
    try:
        # Criar um mapeamento de estado para região
        estado_para_regiao = {estado: regiao 
                             for regiao, estados in regioes_mapping.items() 
                             for estado in estados}
        
        # Adicionar coluna de região
        df_com_regiao = df.copy()
        df_com_regiao['Região'] = df_com_regiao['Estado'].map(estado_para_regiao)
        
        # Agrupar por região e área
        df_agrupado = df_com_regiao.groupby(['Região', 'Área'])['Média'].mean().reset_index()
        
        # Renomear coluna de região para manter compatibilidade
        df_agrupado = df_agrupado.rename(columns={'Região': 'Estado'})
        
        # Otimizar tipo de dados da coluna de região
        regioes = list(regioes_mapping.keys())
        df_agrupado['Estado'] = pd.Categorical(df_agrupado['Estado'], categories=regioes)
        
        return df_agrupado
    except Exception as e:
        return df  # Retornar dados originais em caso de erro
