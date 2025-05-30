import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from typing import Dict, List, Any, Optional, Union, Tuple
from utils.estatisticas.analise_aspectos_sociais import (
    calcular_estatisticas_distribuicao,
    analisar_correlacao_categorias,
    analisar_distribuicao_regional,
    calcular_estatisticas_por_categoria
)
from utils.explicacao.explicacao_aspectos_sociais import (
    get_interpretacao_associacao,
    get_interpretacao_variabilidade_regional,
    get_analise_concentracao
)
from utils.mappings import get_mappings
from utils.helpers.regiao_utils import obter_regiao_do_estado

# Obter limiares dos mapeamentos centralizados
mappings = get_mappings()
LIMIARES_ESTATISTICOS = mappings.get('limiares_estatisticos', {})

# Constantes para classificação de variabilidade
LIMITE_VARIABILIDADE_BAIXA = LIMIARES_ESTATISTICOS.get('variabilidade_baixa', 15)
LIMITE_VARIABILIDADE_MODERADA = LIMIARES_ESTATISTICOS.get('variabilidade_moderada', 30)

# Constantes para classificação de correlação
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS.get('correlacao_fraca', 0.3)
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS.get('correlacao_moderada', 0.7)
LIMITE_CORRELACAO_FORTE = LIMIARES_ESTATISTICOS.get('correlacao_forte', 0.8)

def criar_expander_analise_correlacao(
    df_correlacao: pd.DataFrame, 
    var_x: str, 
    var_y: str, 
    var_x_plot: str, 
    var_y_plot: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> None:
    """
    Cria um expander com análise estatística detalhada da correlação entre dois aspectos sociais.
    
    Parâmetros:
    -----------
    df_correlacao : DataFrame
        DataFrame com dados correlacionados
    var_x : str
        Código da variável original para o eixo X
    var_y : str
        Código da variável original para o eixo Y
    var_x_plot : str
        Nome da variável de plotagem para o eixo X (pode incluir sufixo _NOME)
    var_y_plot : str
        Nome da variável de plotagem para o eixo Y (pode incluir sufixo _NOME)
    variaveis_sociais : Dict
        Dicionário com informações sobre as variáveis sociais
    """
    # Validar entrada
    if df_correlacao is None or df_correlacao.empty:
        return
    
    # Verificar se as variáveis existem no dicionário de mapeamentos
    if var_x not in variaveis_sociais or var_y not in variaveis_sociais:
        return
        
    with st.expander("Ver análise estatística detalhada"):
        try:
            # Calcular métricas de correlação
            metricas = analisar_correlacao_categorias(df_correlacao, var_x_plot, var_y_plot)
            
            # Título principal
            st.write(f"### Análise de associação entre {variaveis_sociais[var_x]['nome']} e {variaveis_sociais[var_y]['nome']}")
            
            # Dividir em colunas para organizar a visualização
            col1, col2 = st.columns(2)
            
            with col1:
                # Resumo da associação
                _mostrar_resumo_associacao(metricas, variaveis_sociais, var_x, var_y)
            
            with col2:
                # Métricas estatísticas
                _mostrar_metricas_estatisticas(metricas)
                
            # Mostrar interpretação contextualizada da associação
            st.write("#### Interpretação contextualizada:")
            interpretacao = get_interpretacao_associacao(
                metricas['coeficiente'],
                variaveis_sociais[var_x]['nome'],
                variaveis_sociais[var_y]['nome']
            )
            st.write(interpretacao)
            
            # Análise por categorias
            _mostrar_analise_categorias(df_correlacao, var_x_plot, var_y_plot, variaveis_sociais, var_x, var_y)
            
            # Verificar se temos uma tabela de contingência válida
            if not metricas['tabela_contingencia'].empty:
                st.write("#### Tabela de contingência (percentuais por linha):")
                
                # Criar tabela normalizada por linha
                tabela_normalizada = metricas['tabela_contingencia'].copy()
                somas_linha = tabela_normalizada.sum(axis=1)
                tabela_normalizada = tabela_normalizada.div(somas_linha, axis=0) * 100
                
                # Formatar para exibição
                st.dataframe(tabela_normalizada.round(1).fillna(0))
        
        except Exception as e:
            st.error(f"Erro ao gerar análise de correlação: {str(e)}")


def criar_expander_dados_distribuicao(
    contagem_aspecto: pd.DataFrame, 
    aspecto_social: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> None:
    """
    Cria um expander com dados detalhados sobre a distribuição de um aspecto social.
    
    Parâmetros:
    -----------
    contagem_aspecto : DataFrame
        DataFrame com contagem de candidatos por categoria
    aspecto_social : str
        Código do aspecto social analisado
    variaveis_sociais : Dict
        Dicionário com informações sobre variáveis sociais
    """
    # Validar entrada
    if contagem_aspecto is None or contagem_aspecto.empty:
        return
    
    # Verificar se o aspecto social existe no dicionário
    if aspecto_social not in variaveis_sociais:
        return
        
    with st.expander("Ver dados detalhados"):
        try:
            # Calcular estatísticas de distribuição
            estatisticas = calcular_estatisticas_distribuicao(contagem_aspecto)
            
            # Nome amigável do aspecto social
            nome_aspecto = variaveis_sociais[aspecto_social]["nome"]
            
            # Mostrar estatísticas principais
            _mostrar_estatisticas_principais_distribuicao(estatisticas, nome_aspecto)
            
            # Mostrar análise de concentração e equidade
            _mostrar_analise_concentracao_equidade(estatisticas, nome_aspecto)
            
            # Calcular e mostrar percentuais acumulados
            _mostrar_analise_concentracao_percentual(contagem_aspecto)
            
            # Opção para exibir tabela completa
            if st.checkbox("Mostrar tabela completa", key="show_full_table_dist"):
                st.write("### Tabela completa")
                
                # Formatar colunas numéricas
                df_display = contagem_aspecto.copy()
                st.dataframe(
                    df_display,
                    column_config={
                        'Quantidade': st.column_config.NumberColumn(
                            'Quantidade',
                            format="%d"
                        ),
                        'Percentual': st.column_config.NumberColumn(
                            'Percentual (%)',
                            format="%.2f%%"
                        )
                    }
                )
                
                # Opção para download
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download dos dados (CSV)",
                    csv,
                    f"distribuicao_{aspecto_social}.csv",
                    "text/csv",
                    key='download_distribuicao_csv'
                )
                
        except Exception as e:
            st.error(f"Erro ao gerar análise de distribuição: {str(e)}")


def criar_expander_analise_regional(
    df_por_estado: pd.DataFrame, 
    aspecto_social: str, 
    categoria_selecionada: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    tipo_localidade: str = "estado"
) -> None:
    """
    Cria um expander com análise detalhada da distribuição regional de uma categoria específica.
    
    Parâmetros:
    -----------
    df_por_estado : DataFrame
        DataFrame com os dados por estado/região
    aspecto_social : str
        Código do aspecto social analisado
    categoria_selecionada : str
        Nome da categoria selecionada para análise
    variaveis_sociais : Dict
        Dicionário com mapeamentos e configurações
    tipo_localidade : str, default="estado"
        Tipo de localidade (estado ou região)
    """
    # Validar entrada
    if df_por_estado is None or df_por_estado.empty:
        return
    
    # Verificar se o aspecto social existe no dicionário
    if aspecto_social not in variaveis_sociais:
        return
        
    with st.expander(f"Ver análise regional detalhada"):
        try:
            # Analisar distribuição regional para a categoria selecionada
            analise = analisar_distribuicao_regional(df_por_estado, aspecto_social, categoria_selecionada)
            
            # Nome amigável do aspecto social
            nome_aspecto = variaveis_sociais[aspecto_social]["nome"]
            
            # Título e seletores de categoria
            _configurar_titulo_analise_regional(
                df_por_estado, aspecto_social, categoria_selecionada, nome_aspecto, tipo_localidade
            )
            
            # Mostrar estatísticas gerais
            _mostrar_estatisticas_regionais(analise, categoria_selecionada, tipo_localidade)
            
            # Mostrar variabilidade regional
            _mostrar_variabilidade_regional(analise, nome_aspecto, categoria_selecionada)
            
            # Mostrar ranking de estados/regiões
            _mostrar_ranking_localidades(df_por_estado, categoria_selecionada, analise, tipo_localidade)
            
            # Se for por estado, adicionar análise por região
            if tipo_localidade.lower() == "estado":
                _mostrar_analise_por_regiao(df_por_estado, categoria_selecionada, nome_aspecto)
            
        except Exception as e:
            st.error(f"Erro ao gerar análise regional: {str(e)}")


def criar_expander_dados_completos_estado(
    df_dados: pd.DataFrame, 
    tipo_localidade: str = "estado"
) -> None:
    """
    Cria um expander com tabela completa de dados por estado/região.
    
    Parâmetros:
    -----------
    df_dados : DataFrame
        DataFrame com os dados para a tabela
    tipo_localidade : str, default="estado"
        Tipo de localidade (estado ou região)
    """
    # Validar entrada
    if df_dados is None or df_dados.empty:
        return
        
    with st.expander(f"Ver tabela completa de dados por {tipo_localidade}"):
        try:
            # Verificar se temos dados suficientes
            colunas_necessarias = ['Estado', 'Categoria', 'Percentual']
            if not all(col in df_dados.columns for col in colunas_necessarias):
                st.warning(f"Dados insuficientes para tabela completa. Colunas necessárias não encontradas.")
                return
            
            # Criar tabela pivô
            df_pivot = _criar_tabela_pivot(df_dados, tipo_localidade)
            
            # Verificar se temos um resultado válido
            if df_pivot is None or df_pivot.empty:
                st.warning("Não foi possível criar a tabela cruzada com os dados disponíveis.")
                return
                
            # Exibir tabela com formatação adequada
            st.dataframe(
                df_pivot,
                column_config={
                    col: st.column_config.NumberColumn(col, format="%.1f%%") 
                    for col in df_pivot.columns if col != tipo_localidade.capitalize()
                },
                height=400
            )
            
            # Opção para download
            csv = df_pivot.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"Download dos dados por {tipo_localidade} (CSV)",
                csv,
                f"aspectos_sociais_por_{tipo_localidade}.csv",
                "text/csv",
                key=f'download_{tipo_localidade}_csv'
            )
            
        except Exception as e:
            st.error(f"Erro ao gerar tabela completa: {str(e)}")


# Funções auxiliares para análise de correlação

def _mostrar_resumo_associacao(
    metricas: Dict[str, Any], 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    var_x: str, 
    var_y: str
) -> None:
    """
    Mostra resumo da associação entre variáveis.
    """
    st.write("#### Resumo da associação:")
    
    # Verificar se temos métricas válidas
    if 'interpretacao' not in metricas or 'coeficiente' not in metricas:
        st.warning("Dados insuficientes para análise de associação.")
        return
    
    # Mostrar força da associação
    st.write(f"• **Força da associação:** {metricas['interpretacao']}")
    st.write(f"• **Coeficiente de contingência:** {metricas['coeficiente']:.4f}")
    
    # Mostrar significância estatística
    if metricas.get('significativo', False):
        st.write("• **Significância estatística:** Há evidência de associação significativa")
        st.write(f"• **Valor p:** {metricas.get('valor_p', 0):.5f} (significativo)")
    else:
        st.write("• **Significância estatística:** Sem evidência de associação significativa")
        st.write(f"• **Valor p:** {metricas.get('valor_p', 1):.5f} (não significativo)")
    
    # Mostrar tamanho do efeito
    if 'tamanho_efeito' in metricas and metricas['tamanho_efeito'] != 'indefinido':
        st.write(f"• **Tamanho do efeito:** {metricas['tamanho_efeito']}")


def _mostrar_metricas_estatisticas(metricas: Dict[str, Any]) -> None:
    """
    Mostra métricas estatísticas detalhadas.
    """
    st.write("#### Métricas estatísticas:")
    
    # Verificar se temos métricas válidas
    if 'qui_quadrado' not in metricas or 'v_cramer' not in metricas:
        st.warning("Dados insuficientes para métricas estatísticas detalhadas.")
        return
    
    # Qui-quadrado e graus de liberdade
    st.write(f"• **Estatística qui-quadrado:** {metricas['qui_quadrado']:.2f}")
    st.write(f"• **Graus de liberdade:** {metricas.get('gl', 0)}")
    
    # V de Cramer
    st.write(f"• **V de Cramer:** {metricas['v_cramer']:.4f}")
    
    # Informação mútua
    if 'info_mutua_norm' in metricas:
        st.write(f"• **Informação mútua normalizada:** {metricas['info_mutua_norm']:.4f}")
    
    # Tamanho da amostra
    if 'n_amostras' in metricas:
        st.write(f"• **Tamanho da amostra:** {metricas['n_amostras']:,}")


def _mostrar_analise_categorias(
    df_correlacao: pd.DataFrame, 
    var_x_plot: str, 
    var_y_plot: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]], 
    var_x: str, 
    var_y: str
) -> None:
    """
    Mostra análise detalhada das combinações de categorias.
    """
    # Verificar se temos dados válidos
    if df_correlacao is None or df_correlacao.empty:
        return
    
    if var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        return
    
    try:
        st.write("#### Destaques por categoria:")
        
        # Calcular tabela cruzada com contagem
        tabela_cruzada = pd.crosstab(
            df_correlacao[var_x_plot], 
            df_correlacao[var_y_plot], 
            normalize='index'
        ) * 100
        
        # Verificar se temos uma tabela válida
        if tabela_cruzada.empty:
            st.warning("Dados insuficientes para análise por categoria.")
            return
        
        # Destacar combinações mais notáveis
        max_valores = {}
        for cat_x in tabela_cruzada.index:
            # Encontrar a categoria_y com maior associação
            if cat_x in tabela_cruzada.index:
                max_cat_y = tabela_cruzada.loc[cat_x].idxmax()
                max_valor = tabela_cruzada.loc[cat_x, max_cat_y]
                max_valores[cat_x] = (max_cat_y, max_valor)
        
        # Mostrar as associações mais fortes (até 3)
        sorted_cats = sorted(max_valores.items(), key=lambda x: x[1][1], reverse=True)[:3]
        
        for cat_x, (cat_y, valor) in sorted_cats:
            st.write(f"• **{cat_x}**: {valor:.1f}% estão na categoria **{cat_y}** de {variaveis_sociais[var_y]['nome']}")
        
        # Opção para ver todas as combinações
        if len(max_valores) > 3:
            if st.checkbox("Ver todas as combinações", key="ver_todas_combinacoes"):
                st.write("#### Todas as combinações mais fortes:")
                for cat_x, (cat_y, valor) in sorted_cats[3:]:
                    st.write(f"• **{cat_x}**: {valor:.1f}% estão na categoria **{cat_y}** de {variaveis_sociais[var_y]['nome']}")
    
    except Exception as e:
        st.warning(f"Não foi possível realizar análise por categorias: {str(e)}")


# Funções auxiliares para análise de distribuição

def _mostrar_estatisticas_principais_distribuicao(
    estatisticas: Dict[str, Any], 
    nome_aspecto: str
) -> None:
    """
    Mostra estatísticas principais da distribuição.
    """
    st.write(f"### Estatísticas de {nome_aspecto}")
    
    # Verificar se temos estatísticas válidas
    if estatisticas is None or 'total' not in estatisticas:
        st.warning("Dados insuficientes para estatísticas de distribuição.")
        return
    
    # Total de candidatos
    st.write(f"**Total de candidatos:** {estatisticas['total']:,}")
    
    # Categoria mais frequente
    if estatisticas.get('categoria_mais_frequente') is not None:
        cat_mais = estatisticas['categoria_mais_frequente']
        if isinstance(cat_mais, pd.Series) and 'Categoria' in cat_mais.index and 'Quantidade' in cat_mais.index:
            st.write(
                f"**Categoria mais frequente:** {cat_mais['Categoria']} " + 
                f"({cat_mais['Quantidade']:,} candidatos - " + 
                f"{cat_mais.get('Percentual', 0):.1f}%)"
            )
    
    # Categoria menos frequente
    if estatisticas.get('categoria_menos_frequente') is not None:
        cat_menos = estatisticas['categoria_menos_frequente']
        if isinstance(cat_menos, pd.Series) and 'Categoria' in cat_menos.index and 'Quantidade' in cat_menos.index:
            st.write(
                f"**Categoria menos frequente:** {cat_menos['Categoria']} " + 
                f"({cat_menos['Quantidade']:,} candidatos - " + 
                f"{cat_menos.get('Percentual', 0):.1f}%)"
            )
    
    # Número de categorias
    st.write(f"**Número de categorias:** {estatisticas.get('num_categorias', 0)}")
    
    # Média e mediana
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Média por categoria", f"{estatisticas.get('media', 0):,.1f}")
    with col2:
        st.metric("Mediana", f"{estatisticas.get('mediana', 0):,.1f}")


def _mostrar_analise_concentracao_equidade(
    estatisticas: Dict[str, Any], 
    nome_aspecto: str
) -> None:
    """
    Mostra análise de concentração e equidade.
    """
    st.write("### Análise de distribuição")
    
    # Verificar se temos estatísticas válidas
    if estatisticas is None or 'indice_concentracao' not in estatisticas:
        st.warning("Dados insuficientes para análise de concentração.")
        return
    
    # Índice de concentração
    indice = estatisticas['indice_concentracao']
    st.write(f"**Índice de concentração:** {indice:.4f}")
    st.write(f"**Classificação:** {estatisticas.get('classificacao_concentracao', 'Não disponível')}")
    
    # Análise de concentração contextualizada
    analise_concentracao = get_analise_concentracao(indice, nome_aspecto)
    st.write(analise_concentracao)
    
    # Razão entre maior e menor categoria
    if (estatisticas.get('categoria_mais_frequente') is not None and 
        estatisticas.get('categoria_menos_frequente') is not None):
        
        cat_mais = estatisticas['categoria_mais_frequente']
        cat_menos = estatisticas['categoria_menos_frequente']
        
        if (isinstance(cat_mais, pd.Series) and isinstance(cat_menos, pd.Series) and 
            'Quantidade' in cat_mais.index and 'Quantidade' in cat_menos.index and 
            cat_menos['Quantidade'] > 0):
            
            razao = cat_mais['Quantidade'] / cat_menos['Quantidade']
            st.write(f"**Razão entre maior e menor categoria:** {razao:.1f}x")
    
    # Coeficiente de variação
    if 'coef_variacao' in estatisticas:
        cv = estatisticas['coef_variacao']
        st.write(f"**Coeficiente de variação:** {cv:.2f}%")
        
        # Interpretar variabilidade
        if cv < LIMITE_VARIABILIDADE_BAIXA:
            st.write("**Interpretação:** Baixa variabilidade entre categorias")
        elif cv < LIMITE_VARIABILIDADE_MODERADA:
            st.write("**Interpretação:** Variabilidade moderada entre categorias")
        else:
            st.write("**Interpretação:** Alta variabilidade entre categorias")


def _mostrar_analise_concentracao_percentual(contagem_aspecto: pd.DataFrame) -> None:
    """
    Mostra análise de concentração por percentual acumulado.
    """
    # Verificar se temos dados válidos
    if contagem_aspecto is None or contagem_aspecto.empty:
        return
    
    if 'Percentual' not in contagem_aspecto.columns:
        return
        
    try:
        # Verificar se temos mais de uma categoria para análise
        if len(contagem_aspecto) > 1:
            # Ordenar por quantidade e calcular percentual acumulado
            contagem_sorted = contagem_aspecto.sort_values('Quantidade', ascending=False).copy()
            contagem_sorted['Percentual Acumulado'] = contagem_sorted['Percentual'].cumsum()
            
            # Encontrar concentração em 50% e 80%
            percentual_50 = next((i+1 for i, val in enumerate(contagem_sorted['Percentual Acumulado']) 
                                if val >= 50), len(contagem_sorted))
            percentual_80 = next((i+1 for i, val in enumerate(contagem_sorted['Percentual Acumulado']) 
                                if val >= 80), len(contagem_sorted))
            
            # Análise de concentração
            st.write(f"**Concentração de candidatos:**")
            st.write(f"• {percentual_50} de {len(contagem_sorted)} categorias representam 50% dos candidatos")
            st.write(f"• {percentual_80} de {len(contagem_sorted)} categorias representam 80% dos candidatos")
            
            # Opção para visualizar percentuais acumulados
            if st.checkbox("Ver percentuais acumulados", key="ver_percentuais_acumulados"):
                st.dataframe(
                    contagem_sorted[['Categoria', 'Quantidade', 'Percentual', 'Percentual Acumulado']],
                    column_config={
                        'Quantidade': st.column_config.NumberColumn('Quantidade', format="%d"),
                        'Percentual': st.column_config.NumberColumn('Percentual (%)', format="%.2f%%"),
                        'Percentual Acumulado': st.column_config.NumberColumn('Acumulado (%)', format="%.2f%%")
                    }
                )
    
    except Exception as e:
        st.warning(f"Não foi possível calcular concentração percentual: {str(e)}")


# Funções auxiliares para análise regional

def _configurar_titulo_analise_regional(
    df_dados: pd.DataFrame, 
    aspecto_social: str, 
    categoria_selecionada: str, 
    nome_aspecto: str, 
    tipo_localidade: str
) -> None:
    """
    Configura título e seletores para análise regional.
    """
    # Obter lista de categorias disponíveis
    categorias_disponiveis = sorted(df_dados['Categoria'].unique())
    
    st.write(f"### Análise de {nome_aspecto} por {tipo_localidade}")
    
    # Opção para selecionar categoria diferente
    if len(categorias_disponiveis) > 1:
        categoria_atual = st.selectbox(
            f"Selecione uma categoria de {nome_aspecto} para análise detalhada:",
            categorias_disponiveis,
            index=categorias_disponiveis.index(categoria_selecionada) if categoria_selecionada in categorias_disponiveis else 0,
            key=f"categoria_regional_{aspecto_social}"
        )
        
        if categoria_atual != categoria_selecionada:
            st.info(f"Você selecionou a categoria '{categoria_atual}'. Clique novamente em 'Ver análise regional detalhada' abaixo do gráfico para atualizar a análise.")
    else:
        st.write(f"**Categoria selecionada:** {categoria_selecionada}")


def _mostrar_estatisticas_regionais(
    analise: Dict[str, Any], 
    categoria_selecionada: str, 
    tipo_localidade: str
) -> None:
    """
    Mostra estatísticas gerais da análise regional.
    """
    st.write(f"#### Estatísticas da categoria '{categoria_selecionada}'")
    
    # Verificar se temos análise válida
    if analise is None or 'percentual_medio' not in analise:
        st.warning("Dados insuficientes para análise regional.")
        return
    
    # Estatísticas principais em colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Média nacional", f"{analise['percentual_medio']:.1f}%")
        st.metric("Desvio padrão", f"{analise['desvio_padrao']:.1f}%")
    
    with col2:
        st.metric("Valor máximo", f"{analise.get('amplitude', 0) + analise['percentual_medio']:.1f}%")
        st.metric("Valor mínimo", f"{analise['percentual_medio'] - analise.get('amplitude', 0)/2:.1f}%")
    
    with col3:
        st.metric("Amplitude", f"{analise.get('amplitude', 0):.1f}%")
        st.metric("Coef. variação", f"{analise.get('coef_variacao', 0):.1f}%")
    
    # Verificar estados com valores extremos
    _mostrar_localidades_extremas(analise, tipo_localidade)


def _mostrar_localidades_extremas(
    analise: Dict[str, Any], 
    tipo_localidade: str
) -> None:
    """
    Mostra localidades com valores extremos.
    """
    # Verificar se temos dados de valores extremos
    if analise.get('maior_percentual') is None or analise.get('menor_percentual') is None:
        return
    
    # Formatar nome da localidade
    nome_loc = tipo_localidade.capitalize()
    
    st.write(f"#### {nome_loc}s com valores extremos:")
    
    # Maior percentual
    maior = analise['maior_percentual']
    if isinstance(maior, pd.Series) and 'Estado' in maior.index and 'Percentual' in maior.index:
        st.write(f"• **Maior percentual:** {maior['Estado']} ({maior['Percentual']:.1f}%)")
    
    # Menor percentual
    menor = analise['menor_percentual']
    if isinstance(menor, pd.Series) and 'Estado' in menor.index and 'Percentual' in menor.index:
        st.write(f"• **Menor percentual:** {menor['Estado']} ({menor['Percentual']:.1f}%)")
    
    # Calcular diferença entre maior e menor (se ambos disponíveis)
    if (isinstance(maior, pd.Series) and isinstance(menor, pd.Series) and 
        'Percentual' in maior.index and 'Percentual' in menor.index):
        diferenca = maior['Percentual'] - menor['Percentual']
        diferenca_percentual = (diferenca / menor['Percentual'] * 100) if menor['Percentual'] > 0 else 0
        
        st.write(f"• **Diferença:** {diferenca:.1f} pontos percentuais ({diferenca_percentual:.1f}% superior)")


def _mostrar_variabilidade_regional(
    analise: Dict[str, Any], 
    nome_aspecto: str, 
    categoria_selecionada: str
) -> None:
    """
    Mostra análise de variabilidade regional.
    """
    st.write("#### Análise de variabilidade regional:")
    
    # Verificar se temos dados para análise
    if analise is None or 'coef_variacao' not in analise:
        st.warning("Dados insuficientes para análise de variabilidade regional.")
        return
    
    # Exibir classificação de variabilidade
    st.write(f"**Nível de variabilidade:** {analise.get('variabilidade', 'Não disponível')}")
    
    # Interpretar disparidade
    st.write(f"**Nível de disparidade regional:** {analise.get('disparidade', 'Indefinida')}")
    
    # Usar a função de interpretação contextualizada
    interpretacao = get_interpretacao_variabilidade_regional(
        analise['coef_variacao'], 
        nome_aspecto, 
        categoria_selecionada
    )
    st.write(interpretacao)
    
    # Informação sobre índice de Gini
    if 'indice_gini' in analise:
        st.write(f"**Índice de Gini regional:** {analise['indice_gini']:.4f}")
        st.write("*Valores mais próximos de 1 indicam maior desigualdade na distribuição regional*")


def _mostrar_ranking_localidades(
    df_dados: pd.DataFrame, 
    categoria_selecionada: str, 
    analise: Dict[str, Any], 
    tipo_localidade: str
) -> None:
    """
    Mostra ranking completo de localidades.
    """
    st.write(f"#### Ranking de {tipo_localidade}s:")
    
    # Verificar se temos dados válidos
    if df_dados is None or df_dados.empty:
        st.warning(f"Dados insuficientes para ranking de {tipo_localidade}s.")
        return
    
    try:
        # Filtrar dados para a categoria selecionada
        df_categoria = df_dados[df_dados['Categoria'] == categoria_selecionada].copy()
        
        if df_categoria.empty:
            st.warning(f"Sem dados para a categoria '{categoria_selecionada}'.")
            return
        
        # Ordenar por percentual
        df_ranking = df_categoria.sort_values('Percentual', ascending=False)[['Estado', 'Percentual']]
        
        # Adicionar classificação relativa à média
        media = analise.get('percentual_medio', df_ranking['Percentual'].mean())
        
        df_ranking['Comparação à média'] = df_ranking['Percentual'].apply(
            lambda x: "Acima da média" if x > media + 1 else 
                     ("Na média" if abs(x - media) <= 1 else "Abaixo da média")
        )
        
        # Renomear colunas para melhor legibilidade
        df_ranking = df_ranking.rename(columns={
            'Estado': tipo_localidade.capitalize(),
            'Percentual': 'Percentual (%)'
        })
        
        # Adicionar índice a partir de 1
        df_ranking = df_ranking.reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        
        # Exibir o ranking
        st.dataframe(
            df_ranking,
            column_config={
                'Percentual (%)': st.column_config.NumberColumn(
                    'Percentual (%)',
                    format="%.1f%%"
                ),
                'Comparação à média': st.column_config.TextColumn(
                    'Comparação à média',
                    width="medium"
                )
            },
            hide_index=False
        )
    
    except Exception as e:
        st.warning(f"Erro ao gerar ranking: {str(e)}")


def _mostrar_analise_por_regiao(
    df_dados: pd.DataFrame, 
    categoria_selecionada: str, 
    nome_aspecto: str
) -> None:
    """
    Mostra análise agrupada por região.
    """
    # Verificar se temos dados válidos
    if df_dados is None or df_dados.empty:
        return
    
    try:
        # Filtrar para a categoria selecionada
        df_categoria = df_dados[df_dados['Categoria'] == categoria_selecionada].copy()
        
        if len(df_categoria) < 5:  # Precisamos de pelo menos alguns estados
            return
        
        st.write("#### Análise por região:")
        
        # Adicionar informação de região
        df_regioes = _adicionar_regiao_aos_estados(df_categoria)
        
        # Verificar se conseguimos adicionar regiões
        if 'Região' not in df_regioes.columns:
            st.warning("Não foi possível realizar análise por região.")
            return
        
        # Agrupar por região
        df_por_regiao = df_regioes.groupby('Região')['Percentual'].mean().reset_index()
        df_por_regiao = df_por_regiao.sort_values('Percentual', ascending=False)
        
        # Gráfico de barras por região
        fig = px.bar(
            df_por_regiao,
            x='Região',
            y='Percentual',
            text_auto='.1f',
            title=f"Média de '{categoria_selecionada}' por região",
            labels={'Percentual': 'Percentual (%)', 'Região': 'Região'},
            color_discrete_sequence=['#3366CC']
        )
        
        fig.update_layout(
            yaxis=dict(ticksuffix='%'),
            plot_bgcolor='white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise textual da distribuição regional
        if len(df_por_regiao) > 1:
            maior_regiao = df_por_regiao.iloc[0]['Região']
            menor_regiao = df_por_regiao.iloc[-1]['Região']
            
            st.write(f"**Maior concentração:** {maior_regiao} ({df_por_regiao.iloc[0]['Percentual']:.1f}%)")
            st.write(f"**Menor concentração:** {menor_regiao} ({df_por_regiao.iloc[-1]['Percentual']:.1f}%)")
    
    except Exception as e:
        st.warning(f"Não foi possível realizar análise por região: {str(e)}")


def _criar_tabela_pivot(
    df_dados: pd.DataFrame, 
    tipo_localidade: str
) -> pd.DataFrame:
    """
    Cria tabela pivô para visualização completa dos dados.
    
    Parâmetros:
    -----------
    df_dados : DataFrame
        DataFrame com os dados brutos
    tipo_localidade : str
        Tipo de localidade (estado ou região)
        
    Retorna:
    --------
    DataFrame
        Tabela pivô formatada
    """
    try:
        # Verificar se temos dados válidos
        if df_dados is None or df_dados.empty:
            return pd.DataFrame()
        
        # Usar pivot_table em vez de pivot para lidar com valores duplicados
        df_pivot = df_dados.pivot_table(
            index='Estado', 
            columns='Categoria', 
            values='Percentual',
            aggfunc='mean'  # Calcula a média quando há valores duplicados
        ).reset_index()
        
        # Renomear o índice para o tipo de localidade
        df_pivot = df_pivot.rename(columns={'Estado': tipo_localidade.capitalize()})
        
        # Expandir colunas para formato adequado
        df_pivot = df_pivot.round(1)
        
        return df_pivot
    
    except Exception as e:
        print(f"Erro ao criar tabela pivô: {e}")
        return pd.DataFrame()


def _adicionar_regiao_aos_estados(df: pd.DataFrame) -> pd.DataFrame:
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
        
        # Obter mapeamento de regiões
        regioes_mapping = mappings.get('regioes_mapping', {})
        
        # Criar mapeamento invertido (de estado para região)
        estado_para_regiao = {}
        for regiao, estados in regioes_mapping.items():
            for estado in estados:
                estado_para_regiao[estado] = regiao
        
        # Adicionar coluna de região
        df_com_regiao['Região'] = df_com_regiao['Estado'].map(estado_para_regiao)
        
        return df_com_regiao
    
    except Exception as e:
        print(f"Erro ao adicionar região aos estados: {e}")
        return df