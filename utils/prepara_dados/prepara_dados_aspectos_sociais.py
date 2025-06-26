import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Set
from utils.helpers.cache_utils import optimized_cache, memory_intensive_function, release_memory
from utils.prepara_dados.validacao_dados import validar_completude_dados
from utils.helpers.regiao_utils import obter_regiao_do_estado
from utils.mappings import get_mappings

# Obter mapeamentos e constantes
mappings = get_mappings()
CONFIG_PROCESSAMENTO = mappings['config_processamento']
LIMIARES_PROCESSAMENTO = mappings['limiares_processamento']

@optimized_cache(ttl=1800)  # Cache válido por 30 minutos
def preparar_dados_correlacao(
    microdados: pd.DataFrame, 
    var_x: str, 
    var_y: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> Tuple[pd.DataFrame, str, str]:
    """
    Prepara os dados para análise de correlação entre duas variáveis sociais.
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com os dados a serem analisados
    var_x : str
        Nome da primeira variável a ser correlacionada
    var_y : str
        Nome da segunda variável a ser correlacionada
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações das variáveis
        
    Retorna:
    --------
    Tuple[DataFrame, str, str]
        (DataFrame com dados preparados, nome da coluna X para plotar, nome da coluna Y para plotar)
    """
    # Verificar se temos dados suficientes
    if microdados.empty:
        return pd.DataFrame(), var_x, var_y
    
    # Verificar se as variáveis estão presentes no DataFrame
    colunas_necessarias = [var_x, var_y]
    dados_validos, taxas_completude = validar_completude_dados(
        microdados, 
        colunas_necessarias,
        limiar_completude=LIMIARES_PROCESSAMENTO['min_completude_dados']
    )
    
    if not dados_validos:
        # Log de colunas com baixa completude
        colunas_problema = [col for col, taxa in taxas_completude.items() 
                           if taxa < LIMIARES_PROCESSAMENTO['min_completude_dados']]
        print(f"Aviso: Baixa completude nas colunas: {colunas_problema}")
    
    # Selecionar apenas colunas necessárias para economizar memória
    df_correlacao = microdados[colunas_necessarias].copy()
    
    # Remover registros com valores inválidos
    df_correlacao = df_correlacao.dropna(subset=colunas_necessarias)
    
    # Aplicar mapeamentos para variável X
    var_x_plot = aplicar_mapeamento(df_correlacao, var_x, variaveis_sociais)
    
    # Aplicar mapeamentos para variável Y
    var_y_plot = aplicar_mapeamento(df_correlacao, var_y, variaveis_sociais)
    
    # Otimizar tipos de dados
    
    return df_correlacao, var_x_plot, var_y_plot


def aplicar_mapeamento(
    df: pd.DataFrame, 
    variavel: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> str:
    """
    Aplica mapeamento a uma variável se necessário e retorna o nome da coluna para uso em gráficos.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    variavel : str
        Nome da variável a ser mapeada
    variaveis_sociais : Dict
        Dicionário com mapeamentos
        
    Retorna:
    --------
    str
        Nome da coluna a ser usada para plotagem
    """
    # Verificar se a variável existe no DataFrame e no dicionário de mapeamentos
    if variavel not in df.columns:
        print(f"Aviso: Variável '{variavel}' não encontrada no DataFrame")
        return variavel
    
    if variavel not in variaveis_sociais:
        print(f"Aviso: Variável '{variavel}' não encontrada no dicionário de mapeamentos")
        return variavel
    
    # Verificar se precisamos aplicar mapeamento (se não for já do tipo object/string)
    if "mapeamento" in variaveis_sociais[variavel] and df[variavel].dtype != 'object':
        coluna_nome = f'{variavel}_NOME'
        
        try:
            mapeamento = variaveis_sociais[variavel]["mapeamento"]
            df[coluna_nome] = df[variavel].map(mapeamento)
            
            # Converter para categoria para economizar memória
            categorias = list(mapeamento.values())
            df[coluna_nome] = pd.Categorical(
                df[coluna_nome], 
                categories=categorias
            )
            
            return coluna_nome
        except Exception as e:
            print(f"Erro ao aplicar mapeamento para '{variavel}': {e}")
            return variavel
    
    return variavel


@optimized_cache(ttl=1800)
def preparar_dados_distribuicao(
    microdados: pd.DataFrame, 
    aspecto_social: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> Tuple[pd.DataFrame, str]:
    """
    Prepara os dados para análise de distribuição de um aspecto social.
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com os microdados
    aspecto_social : str
        Nome do aspecto social a ser analisado
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
        
    Retorna:
    --------
    Tuple[DataFrame, str]
        (DataFrame preparado, nome da coluna para plotar)
    """
    # Verificar se temos dados suficientes
    if microdados.empty or aspecto_social not in microdados.columns:
        print(f"Aviso: Aspecto social '{aspecto_social}' não encontrado nos dados")
        return pd.DataFrame(), aspecto_social
    
    # Selecionar apenas a coluna necessária para economizar memória
    df_dist = microdados[[aspecto_social]].copy()
    
    # Remover valores nulos
    df_dist = df_dist.dropna(subset=[aspecto_social])
    
    # Aplicar mapeamento
    coluna_plot = aplicar_mapeamento(df_dist, aspecto_social, variaveis_sociais)
    
    # Otimizar tipos de dados
    
    return df_dist, coluna_plot


@memory_intensive_function
def contar_candidatos_por_categoria(
    df: pd.DataFrame, 
    coluna_plot: str
) -> pd.DataFrame:
    """
    Conta o número de candidatos em cada categoria de um aspecto social.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados
    coluna_plot : str
        Nome da coluna a ser contabilizada
        
    Retorna:
    --------
    DataFrame
        DataFrame com contagem de candidatos por categoria
    """
    if df.empty or coluna_plot not in df.columns:
        return pd.DataFrame(columns=['Categoria', 'Quantidade'])
    
    try:
        # Usar método eficiente de contagem
        contagem = df[coluna_plot].value_counts().reset_index()
        contagem.columns = ['Categoria', 'Quantidade']
        
        # Calcular percentuais para análise
        total = contagem['Quantidade'].sum()
        contagem['Percentual'] = (contagem['Quantidade'] / total * 100).round(2)
        
        return contagem
    except Exception as e:
        print(f"Erro ao contar candidatos por categoria: {e}")
        return pd.DataFrame(columns=['Categoria', 'Quantidade', 'Percentual'])


def ordenar_categorias(
    contagem_aspecto: pd.DataFrame, 
    aspecto_social: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """
    Ordena as categorias de acordo com a configuração do aspecto social.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com contagem de candidatos por categoria
    aspecto_social : str
        Nome do aspecto social
    variaveis_sociais : Dict
        Dicionário com configurações
        
    Retorna:
    --------
    DataFrame
        DataFrame ordenado
    """
    if contagem_aspecto.empty or 'Categoria' not in contagem_aspecto.columns:
        return contagem_aspecto
    
    try:
        if aspecto_social in variaveis_sociais:
            if "ordem" in variaveis_sociais[aspecto_social]:
                # Usar ordem explicitamente definida
                ordem_categorias = variaveis_sociais[aspecto_social]["ordem"]
                
                # Filtrar para incluir apenas categorias presentes nos dados
                categorias_presentes = set(contagem_aspecto['Categoria'])
                ordem_filtrada = [cat for cat in ordem_categorias if cat in categorias_presentes]
                
                # Verificar se temos categorias não mapeadas e adicionar ao final
                categorias_nao_mapeadas = [cat for cat in categorias_presentes if cat not in ordem_filtrada]
                ordem_final = ordem_filtrada + sorted(categorias_nao_mapeadas)
                
                # Aplicar ordem categórica
                contagem_aspecto['Categoria'] = pd.Categorical(
                    contagem_aspecto['Categoria'], 
                    categories=ordem_final, 
                    ordered=True
                )
                return contagem_aspecto.sort_values('Categoria')
            
            elif "mapeamento" in variaveis_sociais[aspecto_social]:
                # Usar a ordem do mapeamento original
                mapeamento = variaveis_sociais[aspecto_social]["mapeamento"]
                
                # Obter valores do mapeamento na ordem original das chaves
                valores_ordenados = list(mapeamento.values())
                
                # Filtrar para incluir apenas categorias presentes nos dados
                categorias_presentes = set(contagem_aspecto['Categoria'])
                categorias_ordenadas = [cat for cat in valores_ordenados if cat in categorias_presentes]
                
                # Adicionar categorias não mapeadas ao final
                categorias_nao_mapeadas = [cat for cat in categorias_presentes if cat not in categorias_ordenadas]
                ordem_final = categorias_ordenadas + sorted(categorias_nao_mapeadas)
                
                # Aplicar ordenação categórica
                contagem_aspecto['Categoria'] = pd.Categorical(
                    contagem_aspecto['Categoria'],
                    categories=ordem_final,
                    ordered=True
                )
                return contagem_aspecto.sort_values('Categoria')
        
        # Se não houver ordem nem mapeamento, ordenar por quantidade
        return contagem_aspecto.sort_values('Quantidade', ascending=False)
    
    except Exception as e:
        print(f"Erro ao ordenar categorias: {e}")
        return contagem_aspecto  # Retornar dados sem ordenação em caso de erro


@memory_intensive_function
def preparar_dados_heatmap(
    df_correlacao: pd.DataFrame, 
    var_x_plot: str, 
    var_y_plot: str
) -> pd.DataFrame:
    """
    Prepara dados para visualização em heatmap.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com dados correlacionados
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    DataFrame
        DataFrame normalizado para heatmap
    """
    # Verificar se temos dados válidos
    if df_correlacao.empty or var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        print(f"Aviso: Dados insuficientes para criar heatmap")
        return pd.DataFrame()
    
    try:
        # Contar ocorrências para cada combinação (método otimizado)
        contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
        
        # Verificar se temos contagens para trabalhar
        if contagem.empty:
            return pd.DataFrame()
        
        # Calcular percentuais (normalização)
        contagem_pivot = contagem.pivot(index=var_x_plot, columns=var_y_plot, values='Contagem')
        
        # Substituir NaN por 0
        contagem_pivot = contagem_pivot.fillna(0)
        
        # Normalizar por linha (para mostrar distribuição percentual)
        row_sums = contagem_pivot.sum(axis=1)
        
        # Evitar divisão por zero
        row_sums = row_sums.replace(0, np.nan)
        normalized_pivot = contagem_pivot.div(row_sums, axis=0) * 100
        
        # Substituir NaN por 0 novamente
        normalized_pivot = normalized_pivot.fillna(0)
        
        return normalized_pivot
    
    except Exception as e:
        print(f"Erro ao preparar dados para heatmap: {e}")
        return pd.DataFrame()


@memory_intensive_function
def preparar_dados_barras_empilhadas(
    df_correlacao: pd.DataFrame, 
    var_x_plot: str, 
    var_y_plot: str
) -> pd.DataFrame:
    """
    Prepara dados para visualização em barras empilhadas.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com dados correlacionados
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    DataFrame
        DataFrame formatado para barras empilhadas
    """
    # Verificar se temos dados válidos
    if df_correlacao.empty or var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        print(f"Aviso: Dados insuficientes para criar barras empilhadas")
        return pd.DataFrame()
    
    try:
        # Contar ocorrências para cada combinação (método otimizado)
        contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
        
        # Verificar se temos contagens para trabalhar
        if contagem.empty:
            return pd.DataFrame()
        
        # Preparar dados para barras empilhadas
        df_barras = contagem.copy()
        
        # Calcular totais por categoria X (mais eficiente)
        totais = df_barras.groupby(var_x_plot)['Contagem'].sum()
        
        # Converter para dicionário para acesso mais rápido
        totais_dict = totais.to_dict()
        
        # Adicionar coluna de Total para facilitar cálculos
        df_barras['Total'] = df_barras[var_x_plot].map(totais_dict)
        
        # Calcular percentual para cada combinação
        df_barras['Percentual'] = df_barras.apply(
            lambda row: (row['Contagem'] / row['Total'] * 100) if row['Total'] > 0 else 0, 
            axis=1
        ).round(2)
        
        return df_barras
    
    except Exception as e:
        print(f"Erro ao preparar dados para barras empilhadas: {e}")
        return pd.DataFrame()


@memory_intensive_function
def preparar_dados_sankey(
    df_correlacao: pd.DataFrame, 
    var_x_plot: str, 
    var_y_plot: str
) -> Tuple[List[str], List[int], List[int], List[int]]:
    """
    Prepara dados para visualização em diagrama de Sankey.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com dados correlacionados
    var_x_plot : str
        Nome da variável para o eixo X
    var_y_plot : str
        Nome da variável para o eixo Y
        
    Retorna:
    --------
    Tuple[List[str], List[int], List[int], List[int]]
        (labels, source, target, value) - dados para o diagrama Sankey
    """
    # Verificar se temos dados válidos
    if df_correlacao.empty or var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        print(f"Aviso: Dados insuficientes para criar diagrama Sankey")
        return [], [], [], []
    
    try:
        # Contar ocorrências para cada combinação (método otimizado)
        contagem = df_correlacao.groupby([var_x_plot, var_y_plot]).size().reset_index(name='Contagem')
        
        # Verificar se temos contagens para trabalhar
        if contagem.empty:
            return [], [], [], []
        
        # Criar listas para o diagrama Sankey
        categorias_x = contagem[var_x_plot].unique().tolist()
        categorias_y = contagem[var_y_plot].unique().tolist()
        labels = categorias_x + categorias_y
        
        # Mapear valores para índices (uso de dicionário é mais eficiente)
        source_indices = {val: i for i, val in enumerate(categorias_x)}
        target_offset = len(source_indices)
        target_indices = {val: i + target_offset for i, val in enumerate(categorias_y)}
        
        # Criar listas de source, target e value
        source = [source_indices[s] for s in contagem[var_x_plot]]
        target = [target_indices[t] for t in contagem[var_y_plot]]
        value = contagem['Contagem'].tolist()
        
        return labels, source, target, value
    
    except Exception as e:
        print(f"Erro ao preparar dados para diagrama Sankey: {e}")
        return [], [], [], []


@optimized_cache(ttl=1800)
def preparar_dados_grafico_aspectos_por_estado(
    microdados_estados: pd.DataFrame, 
    aspecto_social: str, 
    estados_selecionados: List[str], 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    agrupar_por_regiao: bool = False
) -> pd.DataFrame:
    """
    Prepara os dados para o gráfico de distribuição de aspectos sociais por estado ou região.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame filtrado com dados dos estados selecionados
    aspecto_social : str
        Nome do aspecto social a ser analisado
    estados_selecionados : List[str]
        Lista de estados selecionados para análise
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações das variáveis sociais
    agrupar_por_regiao : bool, default=False
        Se True, agrupa os dados por região em vez de mostrar por estado
    
    Retorna:
    --------
    DataFrame
        DataFrame formatado para o gráfico de linha por estado/região
    """
    # Verificar se temos dados válidos
    if microdados_estados.empty or not estados_selecionados:
        return pd.DataFrame()
    
    # Verificar se as colunas necessárias existem
    if aspecto_social not in microdados_estados.columns or 'SG_UF_PROVA' not in microdados_estados.columns:
        print(f"Aviso: Colunas necessárias não encontradas nos dados")
        return pd.DataFrame()
    
    # Verificar se o aspecto social está no dicionário de variáveis
    if aspecto_social not in variaveis_sociais:
        print(f"Aviso: Aspecto social '{aspecto_social}' não encontrado no dicionário de variáveis")
        return pd.DataFrame()
    
    try:
        # Processar dados em lotes para economizar memória
        resultados = _processar_aspectos_por_estado(
            microdados_estados, 
            aspecto_social, 
            estados_selecionados, 
            variaveis_sociais
        )
        
        # Criar DataFrame a partir dos resultados
        df_resultado = pd.DataFrame(resultados)
        
        # Se não houver resultados, retornar DataFrame vazio
        if df_resultado.empty:
            return df_resultado
        
        # Agrupar por região se solicitado
        if agrupar_por_regiao:
            df_resultado = _agrupar_por_regiao(df_resultado, aspecto_social)
        
        # Otimizar tipos de dados
        
        # Ordenar resultado para garantir consistência na visualização
        df_resultado = df_resultado.sort_values(['Estado', 'Categoria'])
        
        return df_resultado
    
    except Exception as e:
        print(f"Erro ao preparar dados para gráfico de aspectos por estado: {e}")
        return pd.DataFrame()


@memory_intensive_function
def _processar_aspectos_por_estado(
    microdados: pd.DataFrame, 
    aspecto_social: str, 
    estados: List[str], 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Processa dados de aspectos sociais por estado em lotes.
    Função auxiliar para melhorar legibilidade e manutenção.
    
    Parâmetros:
    -----------
    microdados : DataFrame
        DataFrame com os dados
    aspecto_social : str
        Nome do aspecto social a analisar
    estados : List[str]
        Lista de estados a processar
    variaveis_sociais : Dict
        Dicionário com mapeamentos das variáveis
        
    Retorna:
    --------
    List[Dict[str, Any]]: Lista de resultados calculados
    """
    resultados = []
    
    # Criar cópia para não modificar o DataFrame original
    df = microdados.copy()
    
    # Aplicar mapeamento para o aspecto social
    coluna_plot = aplicar_mapeamento(df, aspecto_social, variaveis_sociais)
    
    # Agrupar por estado para processamento mais eficiente
    try:
        grupos_estado = df.groupby('SG_UF_PROVA')
    except Exception as e:
        print(f"Erro ao agrupar por estado: {e}")
        return resultados
    
    # Obter categorias do aspecto social
    if "mapeamento" in variaveis_sociais[aspecto_social]:
        categorias = list(variaveis_sociais[aspecto_social]["mapeamento"].values())
    else:
        categorias = df[coluna_plot].unique().tolist()
    
    # Processar cada estado em lotes
    for i, estado in enumerate(estados):
        try:
            # Tentar obter dados do estado atual
            dados_estado = grupos_estado.get_group(estado)
        except KeyError:
            # Estado não encontrado no agrupamento, pular
            continue
        
        if dados_estado.empty:
            continue  # Pular estados sem dados
        
        # Calcular total de candidatos para o estado
        total_estado = len(dados_estado)
        
        # Contar cada categoria para o estado atual
        contagem_categorias = dados_estado[coluna_plot].value_counts()
        
        # Converter contagem para dicionário para acesso mais rápido
        contagem_dict = contagem_categorias.to_dict()
        
        # Gerar resultados para cada categoria
        for categoria in categorias:
            quantidade = contagem_dict.get(categoria, 0)
            percentual = (quantidade / total_estado * 100) if total_estado > 0 else 0
            
            resultados.append({
                'Estado': estado,
                'Categoria': categoria,
                'Quantidade': quantidade,
                'Percentual': round(percentual, 2)
            })
        
        # Liberar memória a cada X estados processados
        if (i+1) % CONFIG_PROCESSAMENTO['tamanho_lote_estados'] == 0:
            release_memory()
    
    return resultados


def _agrupar_por_regiao(
    df: pd.DataFrame, 
    aspecto_social: str
) -> pd.DataFrame:
    """
    Agrupa os dados por região em vez de por estado.
    Função auxiliar para melhorar legibilidade e manutenção.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com dados por estado
    aspecto_social : str
        Nome do aspecto social analisado
        
    Retorna:
    --------
    DataFrame: DataFrame com dados agrupados por região
    """
    # Importar localmente para evitar importação circular
    from utils.mappings import get_mappings
    from utils.helpers.regiao_utils import obter_regiao_do_estado
    
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
        
        # Agrupar por região e categoria
        df_agrupado = df_com_regiao.groupby(['Região', 'Categoria'])['Percentual'].mean().reset_index()
        
        # Calcular quantidades somando para cada região/categoria
        quantidades = df_com_regiao.groupby(['Região', 'Categoria'])['Quantidade'].sum().reset_index()
        
        # Juntar quantidades com percentuais
        df_agrupado = df_agrupado.merge(quantidades, on=['Região', 'Categoria'])
        
        # Renomear coluna de região para manter compatibilidade
        df_agrupado = df_agrupado.rename(columns={'Região': 'Estado'})
        
        # Otimizar tipo de dados da coluna de região - SUDESTE REMOVIDO
        regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sul']
        df_agrupado['Estado'] = pd.Categorical(df_agrupado['Estado'], categories=regioes)
        df_agrupado['Percentual'] = df_agrupado['Percentual'].round(2)
        
        return df_agrupado
    
    except Exception as e:
        print(f"Erro ao agrupar por região: {e}")
        return df  # Retornar dados originais em caso de erro