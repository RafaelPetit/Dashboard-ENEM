import streamlit as st
import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Any, Tuple
from utils.estatisticas.estatistica_desempenho import analisar_desempenho_por_estado, calcular_estatisticas_comparativas
from utils.helpers.mappings import get_mappings
from utils.helpers.regiao_utils import obter_regiao_do_estado

# Suprimir warnings específicos de cálculos matemáticos
warnings.filterwarnings('ignore', message='invalid value encountered in scalar subtract')
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')

# Obter limiares dos mapeamentos centralizados
mappings = get_mappings()
LIMIARES_ESTATISTICOS = mappings['limiares_estatisticos']

# Constantes para classificação de variabilidade
LIMITE_VARIABILIDADE_BAIXA = LIMIARES_ESTATISTICOS['variabilidade_baixa']
LIMITE_VARIABILIDADE_MODERADA = LIMIARES_ESTATISTICOS['variabilidade_moderada']

# Constantes para classificação de correlação
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS['correlacao_fraca']
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS['correlacao_moderada']
LIMITE_CORRELACAO_FORTE = LIMIARES_ESTATISTICOS['correlacao_forte']

def criar_expander_analise_comparativa(
    df_resultados: pd.DataFrame, 
    variavel_selecionada: str, 
    variaveis_categoricas: Dict[str, Dict[str, Any]], 
    competencia_mapping: Dict[str, str], 
    config_filtros: Dict[str, Any]
) -> None:
    """
    Cria um expander com análise detalhada dos dados comparativos por variável demográfica.
    
    Parâmetros:
    -----------
    df_resultados : DataFrame
        DataFrame com os dados de médias por categoria e competência
    variavel_selecionada : str
        Nome da variável demográfica selecionada
    variaveis_categoricas : dict
        Dicionário com informações sobre as variáveis categóricas
    competencia_mapping : dict
        Dicionário mapeando códigos de competência para nomes legíveis
    config_filtros : dict
        Configurações de filtros selecionadas pelo usuário
    """
    # Validar entrada
    if df_resultados is None or df_resultados.empty:
        return
        
    with st.expander("Ver análise detalhada por categoria"):
        try:
            # Variável nome para exibição
            variavel_nome = variaveis_categoricas[variavel_selecionada]['nome']
            
            # Calcular diferenças e estatísticas importantes
            analise_geral = calcular_estatisticas_comparativas(df_resultados, variavel_selecionada)
            
            # Definir qual competência analisar em detalhe
            competencias_analise, titulo_comp = _determinar_competencias_analise(
                df_resultados, config_filtros
            )
            
            # Título principal da análise
            st.write(f"### Análise do desempenho por {variavel_nome} {titulo_comp}")
            
            # Mostrar disparidades entre categorias
            _mostrar_disparidades_entre_categorias(df_resultados, competencias_analise)
            
            # Análise global das disparidades
            _mostrar_analise_global_disparidades(analise_geral)
            
            # Análise de variabilidade
            _mostrar_variabilidade_entre_categorias(df_resultados, competencias_analise)
        except Exception as e:
            st.error(f"Erro ao gerar análise detalhada: {str(e)}")


def criar_expander_relacao_competencias(
    dados_filtrados: pd.DataFrame, 
    config_filtros: Dict[str, Any], 
    competencia_mapping: Dict[str, str], 
    correlacao: float, 
    interpretacao: str
) -> None:
    """
    Cria um expander com análise detalhada da relação entre duas competências.
    
    Parâmetros:
    -----------
    dados_filtrados : DataFrame
        DataFrame com os dados filtrados para análise
    config_filtros : dict
        Configurações de filtros selecionadas pelo usuário
    competencia_mapping : dict
        Dicionário mapeando códigos de competência para nomes legíveis
    correlacao : float
        Coeficiente de correlação calculado
    interpretacao : str
        Interpretação do coeficiente de correlação
    """
    # Validar entrada
    if dados_filtrados is None or dados_filtrados.empty:
        return
        
    with st.expander("Ver análise detalhada da correlação"):
        try:
            eixo_x = config_filtros['eixo_x']
            eixo_y = config_filtros['eixo_y']
            eixo_x_nome = competencia_mapping[eixo_x]
            eixo_y_nome = competencia_mapping[eixo_y]
            
            # Título da análise
            st.write(f"### Análise da relação entre {eixo_x_nome} e {eixo_y_nome}")
            
            # Estatísticas de correlação
            _mostrar_estatisticas_correlacao(correlacao, interpretacao)
            
            # Interpretação contextualizada
            _mostrar_interpretacao_educacional(correlacao, eixo_x_nome, eixo_y_nome)
            
            # Estatísticas comparativas por competência
            _mostrar_estatisticas_comparativas_competencias(
                dados_filtrados, eixo_x, eixo_y, 
                eixo_x_nome, eixo_y_nome
            )
            
            # Informação sobre os filtros aplicados
            _mostrar_filtros_aplicados(config_filtros)
        except Exception as e:
            st.error(f"Erro ao gerar análise detalhada de correlação: {str(e)}")


def criar_expander_desempenho_estados(
    df_grafico: pd.DataFrame, 
    area_analise: str, 
    analise: Dict[str, Any], 
    tipo_localidade: str = "estado"
) -> None:
    """
    Cria um expander com análise detalhada do desempenho por estado/região.
    
    Parâmetros:
    -----------
    df_grafico : DataFrame
        DataFrame com os dados utilizados para o gráfico
    area_analise : str
        Nome da área selecionada para análise
    analise : dict
        Dicionário com resultados da análise estatística
    tipo_localidade : str, default="estado"
        Tipo de localidade (estado ou região)
    """
    # Validar entrada
    if df_grafico is None or df_grafico.empty:
        return
        
    with st.expander(f"Ver análise detalhada por {tipo_localidade}"):
        try:
            # Título e seleção de área específica
            area_analise, analise, titulo_analise = _configurar_analise_area(
                df_grafico, area_analise, analise
            )
            
            st.write(f"### {titulo_analise}")
            
            # Desempenho comparativo entre estados/regiões
            _mostrar_comparativo_localidades(analise, tipo_localidade)
            
            # Estatísticas descritivas
            _mostrar_estatisticas_gerais_localidades(analise)
            
            # Se os dados estão agrupados por estado, mostrar análise regional
            if tipo_localidade == "estado":
                _mostrar_desempenho_por_regiao(df_grafico, area_analise)
            
            # Opção para ver lista completa ordenada
            _mostrar_ranking_completo(df_grafico, area_analise, tipo_localidade)
        except Exception as e:
            st.error(f"Erro ao gerar análise detalhada por {tipo_localidade}: {str(e)}")


# Funções auxiliares para exibição de análise comparativa

def _determinar_competencias_analise(
    df_resultados: pd.DataFrame, 
    config_filtros: Dict[str, Any]
) -> Tuple[List[str], str]:
    """
    Determina quais competências analisar com base nos filtros.
    """
    if config_filtros.get('mostrar_apenas_competencia') and config_filtros.get('competencia_filtro'):
        competencias_analise = [config_filtros['competencia_filtro']]
        titulo_comp = f"em {config_filtros['competencia_filtro']}"
    else:
        competencias_analise = sorted(df_resultados['Competência'].unique().tolist())
        titulo_comp = "nas diversas competências"
    
    return competencias_analise, titulo_comp


def _mostrar_disparidades_entre_categorias(
    df_resultados: pd.DataFrame, 
    competencias_analise: List[str]
) -> None:
    """
    Exibe análise de disparidades entre categorias para cada competência.
    """
    st.write("#### Disparidades entre categorias:")
    
    for competencia in competencias_analise:
        try:
            df_comp = df_resultados[df_resultados['Competência'] == competencia].copy()
            
            if df_comp.empty:
                continue
                
            # Calcular estatísticas para esta competência
            media_geral = df_comp['Média'].mean()
            
            # Usar método seguro para encontrar valores extremos
            max_idx = df_comp['Média'].idxmax() if not df_comp['Média'].isna().all() else None
            min_idx = df_comp['Média'].idxmin() if not df_comp['Média'].isna().all() else None
            
            if max_idx is not None and min_idx is not None:
                categoria_max = df_comp.loc[max_idx]
                categoria_min = df_comp.loc[min_idx]
                diferenca_max_min = categoria_max['Média'] - categoria_min['Média']
                
                # Exibir estatísticas da competência
                if len(competencias_analise) > 1:
                    st.write(f"**{competencia}:**")
                
                # Usar função auxiliar para exibir estatísticas no formato padrão
                _exibir_estatistica("Maior média", f"{categoria_max['Categoria']} ({categoria_max['Média']:.1f} pontos)")
                _exibir_estatistica("Menor média", f"{categoria_min['Categoria']} ({categoria_min['Média']:.1f} pontos)")
                
                diferenca_percentual = (diferenca_max_min/categoria_min['Média']*100) if categoria_min['Média'] > 0 else 0
                _exibir_estatistica("Diferença", f"{diferenca_max_min:.1f} pontos ({diferenca_percentual:.1f}% superior)")
                
                if len(competencias_analise) > 1:
                    st.write("---")
        except Exception as e:
            st.warning(f"Não foi possível analisar disparidades para {competencia}: {str(e)}")


def _mostrar_analise_global_disparidades(analise_geral: Dict[str, Any]) -> None:
    """
    Exibe análise global das disparidades entre categorias.
    """
    st.write("#### Análise global:")
    
    maior_disp = analise_geral.get('maior_disparidade', {})
    menor_disp = analise_geral.get('menor_disparidade', {})
    
    if maior_disp.get('competencia'):
        _exibir_estatistica(
            "Maior disparidade", 
            f"{maior_disp['competencia']} ({maior_disp.get('diferenca', 0):.1f} pontos)"
        )
    else:
        _exibir_estatistica("Maior disparidade", "Dados insuficientes")
    
    if menor_disp.get('competencia'):
        _exibir_estatistica(
            "Menor disparidade", 
            f"{menor_disp['competencia']} ({menor_disp.get('diferenca', 0):.1f} pontos)"
        )
    else:
        _exibir_estatistica("Menor disparidade", "Dados insuficientes")


def _mostrar_variabilidade_entre_categorias(
    df_resultados: pd.DataFrame, 
    competencias_analise: List[str]
) -> None:
    """
    Exibe análise de variabilidade entre categorias para cada competência.
    """
    st.write("#### Variabilidade entre categorias:")
    
    for competencia in competencias_analise:
        try:
            df_comp = df_resultados[df_resultados['Competência'] == competencia].copy()
            
            if df_comp.empty or df_comp['Média'].isna().all():
                continue
                
            desvio = df_comp['Média'].std()
            media = df_comp['Média'].mean()
            coef_var = (desvio / media * 100) if media > 0 else 0
            
            if len(competencias_analise) > 1:
                st.write(f"**{competencia}:**")
            
            _exibir_estatistica("Desvio padrão", f"{desvio:.2f} pontos")
            _exibir_estatistica("Coeficiente de variação", f"{coef_var:.2f}%")
            
            # Interpretação da variabilidade
            interpretacao = _interpretar_variabilidade(coef_var)
            _exibir_estatistica("Interpretação", interpretacao)
            
            if len(competencias_analise) > 1:
                st.write("---")
        except Exception as e:
            st.warning(f"Não foi possível analisar variabilidade para {competencia}: {str(e)}")


def _interpretar_variabilidade(coef_var: float) -> str:
    """
    Interpreta o coeficiente de variação.
    """
    if coef_var > LIMITE_VARIABILIDADE_MODERADA:
        return "Alta variabilidade, indicando forte influência da variável demográfica"
    elif coef_var > LIMITE_VARIABILIDADE_BAIXA:
        return "Variabilidade moderada, sugerindo influência significativa da variável demográfica"
    else:
        return "Baixa variabilidade, indicando influência limitada da variável demográfica"


# Funções auxiliares para exibição de análise de correlação

def _mostrar_estatisticas_correlacao(
    correlacao: float, 
    interpretacao: str
) -> None:
    """
    Exibe estatísticas de correlação.
    """
    st.write("#### Correlação:")
    _exibir_estatistica("Coeficiente de Pearson", f"{correlacao:.4f}")
    _exibir_estatistica("Interpretação", interpretacao)
    
    # Calcular coeficiente de determinação (r²)
    r_squared = correlacao**2
    _exibir_estatistica(
        "Coeficiente determinação (r²)", 
        f"{r_squared:.4f} ({(r_squared*100):.1f}% da variação pode ser explicada)"
    )


def _mostrar_interpretacao_educacional(
    correlacao: float, 
    eixo_x_nome: str, 
    eixo_y_nome: str
) -> None:
    """
    Exibe interpretação educacional da correlação.
    """
    st.write("#### Significado educacional:")
    
    contexto = _gerar_interpretacao_correlacao(correlacao, eixo_x_nome, eixo_y_nome)
    st.write(contexto)


def _gerar_interpretacao_correlacao(
    correlacao: float, 
    eixo_x_nome: str, 
    eixo_y_nome: str
) -> str:
    """
    Gera texto interpretativo para correlação no contexto educacional.
    """
    correlacao_abs = abs(correlacao)
    
    if correlacao_abs > LIMITE_CORRELACAO_FORTE:
        return f"Existe uma forte associação entre as competências, sugerindo que habilidades e conhecimentos semelhantes são necessários para ambas as áreas. Estudantes com bom desempenho em {eixo_x_nome} muito provavelmente também terão bom desempenho em {eixo_y_nome}."
    elif correlacao_abs > LIMITE_CORRELACAO_MODERADA:
        return f"Há uma associação moderada entre as competências, indicando que algumas habilidades se sobrepõem, mas cada área também exige conhecimentos específicos. Muitos estudantes com bom desempenho em {eixo_x_nome} também terão bom desempenho em {eixo_y_nome}, mas há exceções significativas."
    elif correlacao_abs > LIMITE_CORRELACAO_FRACA:
        return f"A associação fraca sugere que as competências compartilham algumas habilidades básicas, mas são amplamente distintas em seus requisitos. O desempenho em {eixo_x_nome} é apenas um preditor limitado do desempenho em {eixo_y_nome}."
    else:
        return f"Há pouca ou nenhuma associação linear entre as competências, indicando que são áreas de conhecimento e habilidades distintas. O desempenho em {eixo_x_nome} não permite prever o desempenho em {eixo_y_nome}."


def _mostrar_estatisticas_comparativas_competencias(
    dados_filtrados: pd.DataFrame, 
    eixo_x: str, 
    eixo_y: str, 
    eixo_x_nome: str, 
    eixo_y_nome: str
) -> None:
    """
    Exibe estatísticas comparativas entre duas competências.
    """
    if eixo_x not in dados_filtrados.columns or eixo_y not in dados_filtrados.columns:
        st.warning("Dados insuficientes para análise comparativa.")
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        # Estatísticas para eixo X
        df_stats_x = calcular_estatisticas_competencia(dados_filtrados, eixo_x)
        _mostrar_estatisticas_competencia(df_stats_x, eixo_x_nome)
        
    with col2:
        # Estatísticas para eixo Y
        df_stats_y = calcular_estatisticas_competencia(dados_filtrados, eixo_y)
        _mostrar_estatisticas_competencia(df_stats_y, eixo_y_nome)
    
    # Análise comparativa entre competências
    _mostrar_comparacao_competencias(df_stats_x, df_stats_y, eixo_x_nome, eixo_y_nome)


def _mostrar_estatisticas_competencia(
    estatisticas: Dict[str, float], 
    competencia_nome: str
) -> None:
    """
    Exibe estatísticas descritivas de uma competência.
    """
    st.write(f"#### Estatísticas: {competencia_nome}")
    _exibir_estatistica("Média", f"{estatisticas.get('média', 0):.2f} pontos")
    _exibir_estatistica("Mediana", f"{estatisticas.get('mediana', 0):.2f} pontos")
    _exibir_estatistica("Desvio padrão", f"{estatisticas.get('desvio_padrão', 0):.2f}")
    _exibir_estatistica("Coef. variação", f"{estatisticas.get('coef_variação', 0):.2f}%")
    _exibir_estatistica("Mínimo", f"{estatisticas.get('mínimo', 0):.2f} pontos")
    _exibir_estatistica("Máximo", f"{estatisticas.get('máximo', 0):.2f} pontos")


def _mostrar_comparacao_competencias(
    stats_x: Dict[str, float], 
    stats_y: Dict[str, float], 
    nome_x: str, 
    nome_y: str
) -> None:
    """
    Exibe comparação entre as estatísticas de duas competências.
    """
    st.write("#### Comparação entre as competências:")
    
    # Comparação de médias
    media_x = stats_x.get('média', 0)
    media_y = stats_y.get('média', 0)
    comparacao_medias = _gerar_comparacao_medias(media_x, media_y, nome_x, nome_y)
    _exibir_estatistica("", comparacao_medias, prefixo="")
    
    # Comparação de variabilidade
    var_x = stats_x.get('coef_variação', 0)
    var_y = stats_y.get('coef_variação', 0)
    comparacao_var = _gerar_comparacao_variabilidade(var_x, var_y, nome_x, nome_y)
    _exibir_estatistica("", comparacao_var, prefixo="")


def _gerar_comparacao_medias(
    media_x: float, 
    media_y: float, 
    nome_x: str, 
    nome_y: str
) -> str:
    """
    Gera texto comparativo para médias de duas competências.
    """
    # Verificar valores válidos para evitar erros matemáticos
    if not (np.isfinite(media_x) and np.isfinite(media_y)) or media_y == 0:
        return "Não foi possível calcular comparação entre as médias devido a dados insuficientes."
    
    # Calcular diferença com proteção contra overflow
    try:
        diff_percent = ((media_x - media_y) / media_y * 100)
        if not np.isfinite(diff_percent):
            return "Diferença entre médias não pode ser calculada (valores extremos)."
    except (OverflowError, ZeroDivisionError):
        return "Erro no cálculo da diferença percentual entre as médias."
    
    if abs(diff_percent) < 1:
        return f"As médias de desempenho são praticamente iguais (diferença de apenas {abs(diff_percent):.2f}%)."
    else:
        comp_maior = nome_x if media_x > media_y else nome_y
        comp_menor = nome_y if media_x > media_y else nome_x
        diff_abs = abs(media_x - media_y)
        diff_perc = abs(diff_percent)
        
        # Verificar se os valores são finitos antes de formatar
        if np.isfinite(diff_abs) and np.isfinite(diff_perc):
            return f"A média em {comp_maior} é {diff_perc:.2f}% maior que em {comp_menor} (diferença de {diff_abs:.2f} pontos)."
        else:
            return "Diferença significativa detectada, mas valores extremos impedem cálculo preciso."


def _gerar_comparacao_variabilidade(
    var_x: float, 
    var_y: float, 
    nome_x: str, 
    nome_y: str
) -> str:
    """
    Gera texto comparativo para variabilidade de duas competências.
    """
    # Verificar valores válidos para evitar erros matemáticos
    if not (np.isfinite(var_x) and np.isfinite(var_y)):
        return "Não foi possível calcular comparação de variabilidade devido a dados insuficientes."
    
    # Calcular diferença com proteção contra valores inválidos
    try:
        diff_var = abs(var_x - var_y)
        if not np.isfinite(diff_var):
            return "Diferença de variabilidade não pode ser calculada (valores extremos)."
    except (OverflowError, RuntimeError):
        return "Erro no cálculo da diferença de variabilidade."
    
    if diff_var < 5:
        return "Ambas as competências apresentam níveis similares de variabilidade nos resultados."
    else:
        comp_mais_var = nome_x if var_x > var_y else nome_y
        comp_menos_var = nome_y if var_x > var_y else nome_x
        return f"{comp_mais_var} apresenta maior variabilidade nos resultados que {comp_menos_var}, indicando maior heterogeneidade no desempenho dos estudantes."


def _mostrar_filtros_aplicados(config_filtros: Dict[str, Any]) -> None:
    """
    Exibe informações sobre os filtros aplicados na análise.
    """
    st.write("#### Filtros aplicados na análise:")
    
    filtros_texto = []
    if config_filtros.get('sexo') and config_filtros.get('sexo') != "Todos":
        filtros_texto.append(f"Sexo: {config_filtros['sexo']}")
    if config_filtros.get('tipo_escola') and config_filtros.get('tipo_escola') != "Todos":
        filtros_texto.append(f"Tipo de escola: {config_filtros['tipo_escola']}")
    if config_filtros.get('excluir_notas_zero'):
        filtros_texto.append("Excluindo notas zero")
    if config_filtros.get('faixa_salarial') and len(config_filtros['faixa_salarial']) < 8:
        filtros_texto.append(f"Faixas salariais selecionadas: {', '.join([str(f) for f in config_filtros['faixa_salarial']])}")
    
    if filtros_texto:
        for filtro in filtros_texto:
            _exibir_estatistica("", filtro, prefixo="")
    else:
        _exibir_estatistica("", "Sem filtros ativos (todos os dados)", prefixo="")


# Funções auxiliares para exibição de análise por estados/regiões

def _configurar_analise_area(
    df_grafico: pd.DataFrame, 
    area_analise: str, 
    analise: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], str]:
    """
    Configura a análise para área específica ou geral.
    """
    titulo_analise = f"Análise de desempenho em {area_analise}" if area_analise != "Média Geral" else "Análise de desempenho geral"
    
    # Verificar se é análise específica ou geral
    if area_analise == "Média Geral":
        competencias = df_grafico['Área'].unique().tolist()
        if 'Média Geral' in competencias:
            competencias.remove('Média Geral')
        
        # Seletor de área específica
        area_selecionada = st.selectbox(
            "Selecione uma área específica para análise detalhada:",
            ["Média Geral"] + sorted(competencias),
            key="area_analise_detalhada"
        )
        
        if area_selecionada != "Média Geral":
            area_analise = area_selecionada
            titulo_analise = f"Análise de desempenho em {area_analise}"
            # Recalcular análise para a área específica
            analise = analisar_desempenho_por_estado(df_grafico, area_analise)
        else:
            st.info("Selecione uma área específica no filtro de ordenação para ver análise detalhada por área.")
    
    return area_analise, analise, titulo_analise


def _mostrar_comparativo_localidades(
    analise: Dict[str, Any], 
    tipo_localidade: str
) -> None:
    """
    Exibe comparativo de desempenho entre localidades.
    """
    st.write(f"#### Comparativo entre {tipo_localidade}s:")
    
    if analise.get('melhor_estado') is not None and analise.get('pior_estado') is not None:
        melhor = analise['melhor_estado']
        pior = analise['pior_estado']
        
        if isinstance(melhor, pd.Series) and 'Estado' in melhor.index and 'Média' in melhor.index:
            _exibir_estatistica(
                "Melhor desempenho", 
                f"{melhor['Estado']} ({melhor['Média']:.1f} pontos)"
            )
        else:
            _exibir_estatistica("Melhor desempenho", "Dados indisponíveis")
            
        if isinstance(pior, pd.Series) and 'Estado' in pior.index and 'Média' in pior.index:
            _exibir_estatistica(
                "Pior desempenho", 
                f"{pior['Estado']} ({pior['Média']:.1f} pontos)"
            )
        else:
            _exibir_estatistica("Pior desempenho", "Dados indisponíveis")
        
        # Calcular diferença apenas se ambos os valores estão disponíveis
        if (isinstance(melhor, pd.Series) and isinstance(pior, pd.Series) and 
            'Média' in melhor.index and 'Média' in pior.index):
            diferenca = melhor['Média'] - pior['Média']
            _exibir_estatistica("Diferença entre extremos", f"{diferenca:.1f} pontos")
    else:
        st.info(f"Dados insuficientes para análise comparativa entre {tipo_localidade}s.")


def _mostrar_estatisticas_gerais_localidades(analise: Dict[str, Any]) -> None:
    """
    Exibe estatísticas gerais sobre localidades.
    """
    st.write(f"#### Estatísticas gerais:")
    
    _exibir_estatistica("Média nacional", f"{analise.get('media_geral', 0):.1f} pontos")
    _exibir_estatistica("Desvio padrão", f"{analise.get('desvio_padrao', 0):.1f} pontos")
    
    # Interpretar variabilidade
    coef_var = analise.get('coef_variacao', 0)
    interpretacao_variabilidade = _interpretar_variabilidade_numerica(coef_var)
    _exibir_estatistica("Variabilidade", f"{interpretacao_variabilidade.capitalize()} (CV = {coef_var:.2f}%)")


def _interpretar_variabilidade_numerica(coef_var: float) -> str:
    """
    Interpreta o valor do coeficiente de variação numericamente.
    """
    if coef_var > LIMITE_VARIABILIDADE_MODERADA:
        return "alta"
    elif coef_var > LIMITE_VARIABILIDADE_BAIXA:
        return "moderada"
    else:
        return "baixa"


def _mostrar_desempenho_por_regiao(
    df_grafico: pd.DataFrame, 
    area_analise: str
) -> None:
    """
    Exibe análise de desempenho por região.
    """
    st.write("#### Desempenho por região:")
    
    try:
        # Adicionar coluna de região aos dados
        df_regioes = adicionar_regiao_aos_estados(df_grafico)
        
        # Filtrar para a área específica
        df_regioes = df_regioes[df_regioes['Área'] == area_analise]
        
        # Agrupar por região
        if not df_regioes.empty and 'Região' in df_regioes.columns:
            medias_por_regiao = df_regioes.groupby('Região')['Média'].mean().reset_index()
            medias_por_regiao = medias_por_regiao.sort_values('Média', ascending=False)
            
            for _, row in medias_por_regiao.iterrows():
                _exibir_estatistica(row['Região'], f"{row['Média']:.1f} pontos")
        else:
            st.info("Dados insuficientes para análise por região.")
    except Exception as e:
        st.warning(f"Não foi possível analisar o desempenho por região: {str(e)}")


def _mostrar_ranking_completo(
    df_grafico: pd.DataFrame, 
    area_analise: str, 
    tipo_localidade: str
) -> None:
    """
    Exibe ranking completo de localidades.
    """
    if st.checkbox(f"Ver ranking completo de {tipo_localidade}s", key="ver_ranking_completo"):
        try:
            # Filtrar e ordenar dados para a área específica
            ranking = df_grafico[df_grafico['Área'] == area_analise].sort_values('Média', ascending=False)
            
            if not ranking.empty:
                # Selecionar e formatar colunas para exibição
                ranking = ranking[['Estado', 'Média']].reset_index(drop=True)
                ranking.index = ranking.index + 1  # Iniciar índice em 1
                
                # Configurar formatação da coluna Média
                st.dataframe(
                    ranking, 
                    column_config={"Média": st.column_config.NumberColumn("Média", format="%.1f")}
                )
            else:
                st.info(f"Dados insuficientes para gerar ranking de {tipo_localidade}s.")
        except Exception as e:
            st.warning(f"Não foi possível gerar o ranking: {str(e)}")


# Funções auxiliares genéricas

def _exibir_estatistica(
    titulo: str, 
    valor: Any, 
    prefixo: str = "• "
) -> None:
    """
    Exibe um item de estatística no formato padrão.
    """
    if titulo:
        st.write(f"{prefixo}**{titulo}:** {valor}")
    else:
        st.write(f"{prefixo}{valor}")


def calcular_estatisticas_competencia(
    dados: pd.DataFrame, 
    coluna: str
) -> Dict[str, float]:
    """
    Calcula estatísticas descritivas para uma competência.
    
    Parâmetros:
    -----------
    dados : DataFrame
        DataFrame com os dados
    coluna : str
        Nome da coluna com as notas
        
    Retorna:
    --------
    dict
        Dicionário com estatísticas calculadas
    """
    # Verificar se temos dados válidos
    if dados is None or dados.empty or coluna not in dados.columns:
        return {
            'média': 0,
            'mediana': 0,
            'desvio_padrão': 0,
            'coef_variação': 0,
            'mínimo': 0,
            'máximo': 0,
            'q25': 0,
            'q75': 0
        }
    
    try:
        # Filtrar valores válidos
        valores_validos = dados[coluna].dropna()
        valores_validos = valores_validos[valores_validos > 0] if len(valores_validos) > 0 else valores_validos
        
        if len(valores_validos) == 0:
            return {
                'média': 0,
                'mediana': 0,
                'desvio_padrão': 0,
                'coef_variação': 0,
                'mínimo': 0,
                'máximo': 0,
                'q25': 0,
                'q75': 0
            }
        
        # Calcular estatísticas
        media = valores_validos.mean()
        desvio = valores_validos.std()
        
        return {
            'média': media,
            'mediana': valores_validos.median(),
            'desvio_padrão': desvio,
            'coef_variação': (desvio / media * 100) if media > 0 else 0,
            'mínimo': valores_validos.min(),
            'máximo': valores_validos.max(),
            'q25': valores_validos.quantile(0.25),
            'q75': valores_validos.quantile(0.75)
        }
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        return {
            'média': 0,
            'mediana': 0,
            'desvio_padrão': 0,
            'coef_variação': 0,
            'mínimo': 0,
            'máximo': 0,
            'q25': 0,
            'q75': 0
        }


def adicionar_regiao_aos_estados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona a informação de região para cada estado.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com coluna 'Estado'
        
    Retorna:
    --------
    DataFrame
        DataFrame com coluna 'Região' adicionada
    """
    # Verificar se temos dados válidos
    if df is None or df.empty or 'Estado' not in df.columns:
        return df
    
    try:
        # Criar cópia para não modificar o original
        df_com_regiao = df.copy()
        
        # Adicionar coluna de região usando a função auxiliar
        df_com_regiao['Região'] = df_com_regiao['Estado'].apply(obter_regiao_do_estado)
        
        return df_com_regiao
    except Exception as e:
        print(f"Erro ao adicionar região aos estados: {e}")
        return df