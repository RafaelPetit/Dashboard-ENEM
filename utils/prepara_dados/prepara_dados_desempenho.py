import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Set
from utils.data_loader import calcular_seguro
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from utils.prepara_dados.validacao_dados import validar_completude_dados
from utils.helpers.regiao_utils import obter_regiao_do_estado
from utils.mappings import get_mappings


# Obter mapeamentos e constantes
mappings = get_mappings()
competencia_mapping = mappings['competencia_mapping']
colunas_notas = mappings['colunas_notas']
CONFIG_PROCESSAMENTO = mappings['config_processamento']
LIMIARES_PROCESSAMENTO = mappings['limiares_processamento']

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
        print("Erro: DataFrame de entrada vazio ou None")
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    # Verificar se a variável selecionada existe nos dados
    if variavel_selecionada not in microdados_full.columns:
        print(f"Erro: Variável '{variavel_selecionada}' não encontrada nos dados")
        colunas_disponiveis = list(microdados_full.columns)
        print(f"Colunas disponíveis: {colunas_disponiveis[:20]}...")  # Mostrar apenas as primeiras 20
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    # Verificar se temos as colunas de notas
    colunas_notas_disponiveis = [col for col in colunas_notas if col in microdados_full.columns]
    if not colunas_notas_disponiveis:
        print(f"Erro: Nenhuma coluna de notas encontrada nos dados")
        print(f"Colunas de notas esperadas: {colunas_notas}")
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    # Verificar se temos dados suficientes
    colunas_necessarias = [variavel_selecionada] + colunas_notas_disponiveis
    dados_validos, taxas_completude = validar_completude_dados(
        microdados_full, 
        colunas_necessarias,
        limiar_completude=LIMIARES_PROCESSAMENTO['min_completude_dados']
    )
    
    if not dados_validos:
        # Log de colunas com baixa completude
        colunas_problema = [col for col, taxa in taxas_completude.items() 
                          if taxa < LIMIARES_PROCESSAMENTO['min_completude_dados']]
        print(f"Aviso: Baixa completude nas colunas: {colunas_problema}")
        print("Continuando processamento com dados disponíveis...")
    # Selecionar apenas colunas necessárias para economizar memória
    df_trabalho = microdados_full[colunas_necessarias].copy()
    
    # Remover registros com valores inválidos na variável categórica
    df_trabalho = df_trabalho.dropna(subset=[variavel_selecionada])
    
    # Verificar se ainda temos dados após limpeza
    if df_trabalho.empty:
        print("Erro: Nenhum dado válido após remoção de valores nulos")
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    print(f"Processando {len(df_trabalho)} registros para variável '{variavel_selecionada}'")
    
    # Determinar mapeamento de valores e nome da coluna a ser usada
    nome_coluna_mapeada = variavel_selecionada
    mapeamento = None
    
    if variavel_selecionada in variaveis_categoricas and "mapeamento" in variaveis_categoricas[variavel_selecionada]:
        mapeamento = variaveis_categoricas[variavel_selecionada]["mapeamento"]
        print(f"Usando mapeamento para '{variavel_selecionada}': {list(mapeamento.keys())[:5]}...")  # Mostrar apenas alguns valores
    
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
        print("Aviso: Nenhum resultado obtido após processamento")
        return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
    
    print(f"Processamento concluído: {len(df_resultados)} linhas de resultados")
    
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
    
    Função auxiliar para melhorar legibilidade e manutenção.
    
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
    resultados = []
    
    # Verificar se temos dados válidos
    if df.empty:
        print("Erro: DataFrame vazio em _calcular_medias_por_categoria")
        return resultados
    
    # Verificar se a coluna categoria existe
    if coluna_categoria not in df.columns:
        print(f"Erro: Coluna '{coluna_categoria}' não encontrada no DataFrame")
        return resultados
    
    # Obter categorias únicas de forma eficiente
    categorias_unicas = df[coluna_categoria].unique()
    categorias_unicas = [cat for cat in categorias_unicas if pd.notna(cat)]  # Remover NaN
    total_categorias = len(categorias_unicas)
    
    if total_categorias == 0:
        print("Erro: Nenhuma categoria válida encontrada")
        return resultados
    
    print(f"Processando {total_categorias} categorias únicas")
    
    # Verificar se há muitas categorias (pode indicar problema)
    if total_categorias > CONFIG_PROCESSAMENTO['max_categorias_alerta']:
        print(f"Alerta: {total_categorias} categorias encontradas. Isso pode afetar a performance e visualização.")
    
    # Agrupar dados para economizar memória e melhorar performance
    if total_categorias <= CONFIG_PROCESSAMENTO['limiar_agrupamento']:
        # Cálculo eficiente com agrupamento
        df_agrupado = df.groupby(coluna_categoria)
        
        for categoria in categorias_unicas:
            # Determinar o valor de exibição da categoria
            categoria_exibicao = mapeamento.get(categoria, str(categoria)) if mapeamento else str(categoria)
            
            try:
                # Obter grupo de dados para a categoria
                dados_categoria = df_agrupado.get_group(categoria)
                
                # Calcular médias para cada competência
                for competencia in colunas_notas:
                    if competencia not in dados_categoria.columns:
                        print(f"Aviso: Coluna '{competencia}' não encontrada nos dados")
                        continue
                        
                    # Filtrar apenas notas válidas (maiores que zero)
                    notas_validas = dados_categoria[dados_categoria[competencia] > 0][competencia]
                    
                    if len(notas_validas) == 0:
                        # Se não há notas válidas, usar 0 como média
                        media_comp = 0
                    else:
                        # Calcular média ou usar zero se não houver notas válidas
                        media_comp = calcular_seguro(notas_validas, 'media')
                    
                    competencia_nome = competencia_mapping.get(competencia, competencia)
                    
                    resultados.append({
                        'Categoria': categoria_exibicao,
                        'Competência': competencia_nome,
                        'Média': round(media_comp, 2)
                    })
            except KeyError:
                # Categoria pode não existir no agrupamento (caso raro)
                continue
    else:
        # Método alternativo para muitas categorias (processamento em lotes)
        for i, categoria in enumerate(categorias_unicas):
            # Filtrar dados para a categoria atual
            dados_categoria = df[df[coluna_categoria] == categoria]
            
            # Determinar o valor de exibição da categoria
            categoria_exibicao = mapeamento.get(categoria, str(categoria)) if mapeamento else str(categoria)
            
            # Calcular médias para cada competência
            for competencia in colunas_notas:
                if competencia not in dados_categoria.columns:
                    print(f"Aviso: Coluna '{competencia}' não encontrada nos dados")
                    continue
                    
                # Filtrar apenas notas válidas (maiores que zero)
                notas_validas = dados_categoria[dados_categoria[competencia] > 0][competencia]
                
                if len(notas_validas) == 0:
                    # Se não há notas válidas, usar 0 como média
                    media_comp = 0
                else:
                    # Calcular média ou usar zero se não houver notas válidas
                    media_comp = calcular_seguro(notas_validas, 'media')
                
                competencia_nome = competencia_mapping.get(competencia, competencia)
                
                resultados.append({
                    'Categoria': categoria_exibicao,
                    'Competência': competencia_nome,
                    'Média': round(media_comp, 2)
                })
            
            # Liberar memória a cada lote processado
            if (i+1) % CONFIG_PROCESSAMENTO['tamanho_lote'] == 0:
                release_memory(dados_categoria)
    
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
            print("[WARN] preparar_dados_grafico_linha: df_resultados é None")
            return pd.DataFrame(columns=['Categoria', 'Competência', 'Média'])
            
        if df_resultados.empty:
            print("[WARN] preparar_dados_grafico_linha: df_resultados está vazio")
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
        print(f"[ERRO] preparar_dados_grafico_linha: {str(e)}")
        import traceback
        traceback.print_exc()
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
        print("[WARN] preparar_dados_desempenho_geral: microdados vazios ou None")
        return pd.DataFrame()
    
    # Colunas demográficas que precisamos para análises
    colunas_demograficas = [
        'TP_COR_RACA', 'TP_SEXO', 'TP_DEPENDENCIA_ADM_ESC', 
        'TP_FAIXA_ETARIA', 'Q001', 'Q002', 'Q005', 'Q006',
        'Q025', 'TP_FAIXA_SALARIAL', 'TP_ST_CONCLUSAO'
    ]
    
    # Determinar quais colunas vamos precisar (notas + demografia)
    colunas_necessarias = list(colunas_notas)
    
    # Adicionar colunas demográficas que existem no DataFrame
    for col in colunas_demograficas:
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
    filtro_faixa_salarial: Optional[int] = None,
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
    filtro_faixa_salarial : int, opcional
        Filtro para faixa salarial específica
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
    
    # Adicionar colunas de agrupamento se presentes
    for coluna, filtro in [
        ('TP_SEXO', filtro_sexo),
        ('TP_DEPENDENCIA_ADM_ESC', filtro_tipo_escola),
        ('TP_COR_RACA', filtro_raca),
        ('TP_FAIXA_SALARIAL', filtro_faixa_salarial)
    ]:
        if filtro is not None and coluna in dados.columns:
            colunas_necessarias.append(coluna)
    
    # Selecionar colunas e criar cópia
    df = dados[colunas_necessarias].copy()
    tamanho_inicial = len(df)
    
    # Construir filtros como expressões para aplicar tudo de uma vez
    filtros = []
    
    # Notas válidas
    if excluir_notas_zero:
        filtros.append(f"{eixo_x} > 0")
        filtros.append(f"{eixo_y} > 0")
    
    # Filtros demográficos
    if filtro_sexo and 'TP_SEXO' in df.columns:
        filtros.append(f"TP_SEXO == '{filtro_sexo}'")
    
    if filtro_tipo_escola and 'TP_DEPENDENCIA_ADM_ESC' in df.columns:
        if filtro_tipo_escola == 'Pública':
            filtros.append("TP_DEPENDENCIA_ADM_ESC.isin(['1', '2', '3'])")
        elif filtro_tipo_escola == 'Privada':
            filtros.append("TP_DEPENDENCIA_ADM_ESC == '4'")
    
    if filtro_raca and 'TP_COR_RACA' in df.columns:
        filtros.append(f"TP_COR_RACA == {filtro_raca}")
    
    if filtro_faixa_salarial is not None and 'TP_FAIXA_SALARIAL' in df.columns:
        filtros.append(f"TP_FAIXA_SALARIAL == {filtro_faixa_salarial}")
    
    # Aplicar filtros
    if filtros:
        query = " & ".join(filtros)
        try:
            df = df.query(query)
        except Exception as e:
            print(f"Erro ao aplicar filtro: {e}")
            # Aplicar filtros manualmente como fallback
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
        print("Erro: Coluna 'SG_UF_PROVA' não encontrada nos dados")
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
    Processa estados em lotes para calcular médias de desempenho.
    Função auxiliar para melhorar legibilidade e manutenção.
    
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
    resultados = []
    total_estados = len(estados)
    
    # Agrupar por estado para processamento mais eficiente
    try:
        grupos_estado = microdados.groupby('SG_UF_PROVA')
    except Exception as e:
        print(f"Erro ao agrupar por estado: {e}")
        return resultados
    
    # Processar cada estado
    for i, estado in enumerate(estados):
        try:
            # Tentar obter dados do estado atual
            dados_estado = grupos_estado.get_group(estado)
        except KeyError:
            # Estado não encontrado no agrupamento, pular
            continue
        
        if len(dados_estado) == 0:
            continue  # Pular estados sem dados
        
        # Armazenar médias para calcular média geral
        medias_estado = []
        
        # Calcular média para cada área de conhecimento
        for area in colunas_notas:
            if area not in dados_estado.columns:
                continue
                
            # Filtrar notas válidas de forma mais eficiente
            notas = dados_estado[area].values
            notas_validas = notas[notas > 0]
            
            # Calcular média com função otimizada
            media_area = calcular_seguro(notas_validas, 'media')
            media_area = round(media_area, 2)
            
            # Adicionar ao resultado
            resultados.append({
                'Estado': estado,
                'Área': competencia_mapping[area],
                'Média': media_area
            })
            
            # Armazenar para média geral
            medias_estado.append(media_area)
        
        # Adicionar média geral para o estado
        if medias_estado:
            resultados.append({
                'Estado': estado,
                'Área': 'Média Geral',
                'Média': round(sum(medias_estado) / len(medias_estado), 2)
            })
        
        # Liberar memória a cada X estados processados
        if (i+1) % CONFIG_PROCESSAMENTO['tamanho_lote_estados'] == 0:
            release_memory()
    
    return resultados


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
        print(f"Erro ao converter coluna 'Área': {e}")
    
    try:
        df['Estado'] = pd.Categorical(df['Estado'], categories=estados)
    except Exception as e:
        print(f"Erro ao converter coluna 'Estado': {e}")
    
    # Otimizar coluna numérica
    try:
        df['Média'] = df['Média'].astype('float32')
    except Exception as e:
        print(f"Erro ao converter coluna 'Média': {e}")
    
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
    from utils.mappings import get_mappings
    mappings = get_mappings()
    regioes_mapping = mappings['regioes_mapping']
    
    # Verificar se temos dados para processar
    if df.empty:
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
        
        # Otimizar tipo de dados da coluna de região - SUDESTE REMOVIDO
        regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sul']
        df_agrupado['Estado'] = pd.Categorical(df_agrupado['Estado'], categories=regioes)
        
        return df_agrupado
    except Exception as e:
        print(f"Erro ao agrupar por região: {e}")
        return df  # Retornar dados originais em caso de erro
