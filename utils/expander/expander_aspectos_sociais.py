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
        st.warning("⚠️ Não há dados suficientes para análise estatística.")
        return
    
    # Verificar se as variáveis existem no dicionário de mapeamentos
    if var_x not in variaveis_sociais or var_y not in variaveis_sociais:
        st.warning("⚠️ Variáveis não encontradas no dicionário de mapeamentos.")
        return
    
    # Obter nomes amigáveis das variáveis
    nome_x = variaveis_sociais[var_x].get('nome', var_x)
    nome_y = variaveis_sociais[var_y].get('nome', var_y)
    
    with st.expander(f"📊 Análise estatística da correlação: {nome_x} × {nome_y}"):
        try:
            # Realizar análise de correlação
            metricas = analisar_correlacao_categorias(df_correlacao, var_x_plot, var_y_plot)
            
            # Seção 1: Resumo Executivo
            st.write("### 🎯 Resumo Executivo")
            _mostrar_resumo_associacao(metricas, variaveis_sociais, var_x, var_y)
            
            st.divider()
            
            # Seção 2: Métricas Estatísticas
            st.write("### 📈 Métricas Estatísticas")
            _mostrar_metricas_estatisticas(metricas)
            
            st.divider()
            
            # Seção 3: Análise de Combinações
            st.write("### 🔍 Análise de Combinações")
            _mostrar_analise_categorias(df_correlacao, var_x_plot, var_y_plot, variaveis_sociais, var_x, var_y)
            
            st.divider()
            
            # Seção 4: Interpretação e Insights
            st.write("### 💡 Interpretação e Insights")
            _mostrar_interpretacao_correlacao(metricas, variaveis_sociais, var_x, var_y)
            
            st.divider()
            
            # Seção 5: Downloads e Exportação
            st.write("### 💾 Downloads e Exportação")
            _mostrar_downloads_correlacao(df_correlacao, metricas, var_x, var_y, variaveis_sociais)
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar análise estatística: {str(e)}")
            # Fallback para versão básica
            _mostrar_correlacao_basica(df_correlacao, var_x_plot, var_y_plot, variaveis_sociais, var_x, var_y)


def criar_expander_dados_distribuicao(
    contagem_aspecto: pd.DataFrame, 
    aspecto_social: str, 
    variaveis_sociais: Dict[str, Dict[str, Any]]
) -> None:
    """
    Cria um expander com análise estatística detalhada sobre a distribuição de um aspecto social.
    
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
        st.warning("⚠️ Não há dados suficientes para análise estatística.")
        return
    
    # Verificar se o aspecto social existe no dicionário
    if aspecto_social not in variaveis_sociais:
        st.warning("⚠️ Aspecto social não encontrado no dicionário de mapeamentos.")
        return
    
    # Obter nome amigável do aspecto social
    nome_aspecto = variaveis_sociais[aspecto_social].get("nome", aspecto_social)
    
    with st.expander(f"📊 Análise estatística da distribuição: {nome_aspecto}"):
        try:
            # Calcular estatísticas de distribuição
            estatisticas = calcular_estatisticas_distribuicao(contagem_aspecto)
            
            # Seção 1: Resumo Executivo
            st.write("### 🎯 Resumo Executivo")
            _mostrar_resumo_distribuicao(estatisticas, nome_aspecto, contagem_aspecto)
            
            st.divider()
            
            # Seção 2: Métricas Estatísticas
            st.write("### 📈 Métricas Estatísticas")
            _mostrar_metricas_distribuicao(estatisticas, nome_aspecto)
            
            st.divider()
            
            # Seção 3: Análise de Concentração e Equidade
            st.write("### ⚖️ Análise de Concentração e Equidade")
            _mostrar_analise_concentracao_equidade(estatisticas, nome_aspecto)
            
            st.divider()
            
            # Seção 4: Ranking e Padrões
            st.write("### 🏆 Ranking e Padrões")
            _mostrar_ranking_categorias(contagem_aspecto, nome_aspecto)
            
            st.divider()
            
            # Seção 5: Insights e Interpretação
            st.write("### 💡 Insights e Interpretação")
            _mostrar_insights_distribuicao(estatisticas, contagem_aspecto, nome_aspecto)
            
            st.divider()
            
            # Seção 6: Tabela Interativa
            st.write("### 📋 Tabela Interativa")
            _mostrar_tabela_interativa_distribuicao(contagem_aspecto, aspecto_social)
            
            st.divider()
            
            # Seção 7: Downloads e Exportação
            st.write("### 💾 Downloads e Exportação")
            _mostrar_downloads_distribuicao(contagem_aspecto, estatisticas, aspecto_social, nome_aspecto)
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar análise estatística: {str(e)}")
            # Fallback para versão básica
            _mostrar_distribuicao_basica(contagem_aspecto, aspecto_social, nome_aspecto)


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
    Cria um expander com análise completa e profissional dos dados por estado/região.
    
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
        
    with st.expander(f"📊 Análise completa dos dados por {tipo_localidade}"):
        try:
            # Verificar se temos dados suficientes
            colunas_necessarias = ['Estado', 'Categoria', 'Percentual']
            if not all(col in df_dados.columns for col in colunas_necessarias):
                st.warning(f"Dados insuficientes para análise completa. Colunas necessárias não encontradas.")
                return
            
            # Seção 1: Resumo executivo
            st.markdown("### 📈 Resumo Executivo")
            _mostrar_resumo_executivo(df_dados, tipo_localidade)
            
            st.markdown("---")
            
            # Seção 2: Análise estatística por categoria
            st.markdown("### 🔍 Análise Estatística por Categoria")
            _mostrar_analise_estatistica_categorias(df_dados, tipo_localidade)
            
            st.markdown("---")
            
            # Seção 3: Ranking e disparidades regionais
            st.markdown("### 🏆 Ranking e Disparidades Regionais")
            _mostrar_ranking_disparidades(df_dados, tipo_localidade)
            
            st.markdown("---")
            
            # Seção 4: Insights e padrões identificados
            st.markdown("### 💡 Insights e Padrões Identificados")
            _mostrar_insights_padroes(df_dados, tipo_localidade)
            
            st.markdown("---")
            
            # Seção 5: Tabela interativa com filtros
            st.markdown("### 📋 Dados Detalhados - Tabela Interativa")
            _mostrar_tabela_interativa(df_dados, tipo_localidade)
            
            st.markdown("---")
            
            # Seção 6: Downloads e exportação
            st.markdown("### 📥 Downloads e Exportação")
            _mostrar_opcoes_download(df_dados, tipo_localidade)
            
        except Exception as e:
            st.error(f"Erro ao gerar análise completa: {str(e)}")
            # Fallback para a versão básica
            st.warning("Exibindo versão simplificada dos dados:")
            _mostrar_tabela_basica(df_dados, tipo_localidade)


# Funções auxiliares para a análise completa de dados por estado/região

def _mostrar_resumo_executivo(df_dados: pd.DataFrame, tipo_localidade: str) -> None:
    """
    Mostra um resumo executivo dos dados por estado/região.
    """
    try:
        # Cálculos básicos
        total_localidades = df_dados['Estado'].nunique()
        total_categorias = df_dados['Categoria'].nunique()
        
        # Estatísticas gerais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=f"Total de {tipo_localidade}s",
                value=total_localidades
            )
        
        with col2:
            st.metric(
                label="Categorias analisadas",
                value=total_categorias
            )
        
        with col3:
            media_geral = df_dados['Percentual'].mean()
            st.metric(
                label="Percentual médio",
                value=f"{media_geral:.1f}%"
            )
        
        # Insights principais
        st.markdown("**📋 Principais observações:**")
        
        # Encontrar extremos
        max_valor = df_dados.loc[df_dados['Percentual'].idxmax()]
        min_valor = df_dados.loc[df_dados['Percentual'].idxmin()]
        
        st.write(f"• **Maior percentual:** {max_valor['Percentual']:.1f}% ({max_valor['Categoria']} - {max_valor['Estado']})")
        st.write(f"• **Menor percentual:** {min_valor['Percentual']:.1f}% ({min_valor['Categoria']} - {min_valor['Estado']})")
        
        # Variabilidade
        coef_variacao = (df_dados['Percentual'].std() / df_dados['Percentual'].mean()) * 100
        if coef_variacao < 20:
            variabilidade = "baixa"
        elif coef_variacao < 40:
            variabilidade = "moderada"
        else:
            variabilidade = "alta"
        
        st.write(f"• **Variabilidade entre {tipo_localidade}s:** {variabilidade} (CV = {coef_variacao:.1f}%)")
        
    except Exception as e:
        st.error(f"Erro ao gerar resumo executivo: {str(e)}")


def _mostrar_analise_estatistica_categorias(df_dados: pd.DataFrame, tipo_localidade: str) -> None:
    """
    Mostra análise estatística detalhada por categoria.
    """
    try:
        # Análise por categoria
        categorias = df_dados['Categoria'].unique()
        
        if len(categorias) > 1:
            categoria_selecionada = st.selectbox(
                "Selecione uma categoria para análise detalhada:",
                categorias,
                key="analise_categoria_detalhada"
            )
            
            df_categoria = df_dados[df_dados['Categoria'] == categoria_selecionada]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Estatísticas de '{categoria_selecionada}':**")
                
                # Estatísticas descritivas
                stats = df_categoria['Percentual'].describe()
                st.write(f"• **Média:** {stats['mean']:.1f}%")
                st.write(f"• **Mediana:** {stats['50%']:.1f}%")
                st.write(f"• **Desvio padrão:** {stats['std']:.1f}%")
                st.write(f"• **Amplitude:** {stats['max'] - stats['min']:.1f}%")
                
                # Percentis
                st.markdown("**Percentis:**")
                st.write(f"• P25: {stats['25%']:.1f}%")
                st.write(f"• P75: {stats['75%']:.1f}%")
                
            with col2:
                st.markdown(f"**{tipo_localidade.capitalize()}s extremos:**")
                
                # Top 3 e bottom 3
                top_3 = df_categoria.nlargest(3, 'Percentual')
                bottom_3 = df_categoria.nsmallest(3, 'Percentual')
                
                st.markdown("**🔝 Maiores percentuais:**")
                for i, row in top_3.iterrows():
                    st.write(f"• {row['Estado']}: {row['Percentual']:.1f}%")
                
                st.markdown("**🔻 Menores percentuais:**")
                for i, row in bottom_3.iterrows():
                    st.write(f"• {row['Estado']}: {row['Percentual']:.1f}%")
        
        else:
            st.info("Análise disponível apenas quando há múltiplas categorias.")
    
    except Exception as e:
        st.error(f"Erro ao gerar análise estatística: {str(e)}")


def _mostrar_ranking_disparidades(df_dados: pd.DataFrame, tipo_localidade: str) -> None:
    """
    Mostra ranking completo e análise de disparidades.
    """
    try:
        # Calcular médias por estado/região
        df_medias = df_dados.groupby('Estado')['Percentual'].agg(['mean', 'std', 'count']).reset_index()
        df_medias.columns = ['Estado', 'Media', 'Desvio', 'Categorias']
        df_medias = df_medias.sort_values('Media', ascending=False)
        
        # Ranking
        st.markdown(f"**🏆 Ranking de {tipo_localidade}s por percentual médio:**")
        
        # Dividir em grupos
        total = len(df_medias)
        tercil_size = total // 3
        
        # Primeiro tercil (melhores)
        top_tercil = df_medias.head(tercil_size)
        st.markdown("**🥇 Primeiro tercil (maiores percentuais):**")
        for i, row in top_tercil.iterrows():
            st.write(f"• {row['Estado']}: {row['Media']:.1f}% (±{row['Desvio']:.1f}%)")
        
        # Último tercil (menores)
        bottom_tercil = df_medias.tail(tercil_size)
        st.markdown("**🥉 Último tercil (menores percentuais):**")
        for i, row in bottom_tercil.iterrows():
            st.write(f"• {row['Estado']}: {row['Media']:.1f}% (±{row['Desvio']:.1f}%)")
        
        # Análise de disparidades
        st.markdown("**⚖️ Análise de disparidades:**")
        
        maior_media = df_medias['Media'].max()
        menor_media = df_medias['Media'].min()
        razao_disparidade = maior_media / menor_media if menor_media > 0 else 0
        
        st.write(f"• **Razão de disparidade:** {razao_disparidade:.2f}x")
        st.write(f"• **Diferença absoluta:** {maior_media - menor_media:.1f} pontos percentuais")
        
        # Classificação da disparidade
        if razao_disparidade < 1.5:
            nivel_disparidade = "baixa"
        elif razao_disparidade < 2.5:
            nivel_disparidade = "moderada"
        else:
            nivel_disparidade = "alta"
        
        st.write(f"• **Nível de disparidade:** {nivel_disparidade}")
        
    except Exception as e:
        st.error(f"Erro ao gerar ranking: {str(e)}")


def _mostrar_insights_padroes(df_dados: pd.DataFrame, tipo_localidade: str) -> None:
    """
    Mostra insights e padrões identificados nos dados.
    """
    try:
        st.markdown("**🔍 Análise de padrões regionais:**")
        
        # Análise por região (se for por estado)
        if tipo_localidade.lower() == "estado":
            df_com_regiao = _adicionar_regiao_aos_estados(df_dados)
            
            if 'Regiao' in df_com_regiao.columns:
                analise_regional = df_com_regiao.groupby('Regiao')['Percentual'].agg(['mean', 'std']).reset_index()
                analise_regional.columns = ['Regiao', 'Media', 'Desvio']
                analise_regional = analise_regional.sort_values('Media', ascending=False)
                
                st.markdown("**📍 Padrões por região:**")
                for i, row in analise_regional.iterrows():
                    st.write(f"• **{row['Regiao']}:** {row['Media']:.1f}% (±{row['Desvio']:.1f}%)")
                
                # Identificar região com maior variabilidade
                regiao_mais_variavel = analise_regional.loc[analise_regional['Desvio'].idxmax()]
                st.write(f"• **Região com maior variabilidade interna:** {regiao_mais_variavel['Regiao']}")
        
        # Análise de distribuição
        st.markdown("**📊 Características da distribuição:**")
        
        # Teste de normalidade simplificado
        percentuais = df_dados['Percentual'].values
        media = percentuais.mean()
        mediana = np.median(percentuais)
        
        if abs(media - mediana) < 1:
            distribuicao = "simétrica"
        elif media > mediana:
            distribuicao = "assimétrica à direita"
        else:
            distribuicao = "assimétrica à esquerda"
        
        st.write(f"• **Formato da distribuição:** {distribuicao}")
        
        # Concentração
        q1 = np.percentile(percentuais, 25)
        q3 = np.percentile(percentuais, 75)
        iqr = q3 - q1
        
        st.write(f"• **Amplitude interquartil:** {iqr:.1f}%")
        
        # Outliers
        limite_superior = q3 + 1.5 * iqr
        limite_inferior = q1 - 1.5 * iqr
        
        outliers = df_dados[(df_dados['Percentual'] > limite_superior) | 
                           (df_dados['Percentual'] < limite_inferior)]
        
        if len(outliers) > 0:
            st.write(f"• **Valores atípicos identificados:** {len(outliers)}")
            st.markdown("**🚨 Casos atípicos:**")
            for i, row in outliers.iterrows():
                st.write(f"  - {row['Estado']} ({row['Categoria']}): {row['Percentual']:.1f}%")
        else:
            st.write("• **Valores atípicos:** Nenhum identificado")
        
    except Exception as e:
        st.error(f"Erro ao gerar insights: {str(e)}")


def _mostrar_tabela_interativa(df_dados: pd.DataFrame, tipo_localidade: str) -> None:
    """
    Mostra tabela interativa com filtros e formatação.
    """
    try:
        # Filtros interativos
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por categoria
            categorias = ['Todas'] + sorted(df_dados['Categoria'].unique().tolist())
            categoria_filtro = st.selectbox(
                "Filtrar por categoria:",
                categorias,
                key="filtro_categoria_tabela"
            )
        
        with col2:
            # Filtro por faixa de percentual
            min_val = float(df_dados['Percentual'].min())
            max_val = float(df_dados['Percentual'].max())
            
            faixa_percentual = st.slider(
                "Faixa de percentual:",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                step=0.1,
                key="filtro_percentual_tabela"
            )
        
        # Aplicar filtros
        df_filtrado = df_dados.copy()
        
        if categoria_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_filtro]
        
        df_filtrado = df_filtrado[
            (df_filtrado['Percentual'] >= faixa_percentual[0]) & 
            (df_filtrado['Percentual'] <= faixa_percentual[1])
        ]
        
        # Ordenação
        ordenacao = st.radio(
            "Ordenar por:",
            ["Estado", "Categoria", "Percentual (crescente)", "Percentual (decrescente)"],
            horizontal=True,
            key="ordenacao_tabela"
        )
        
        if ordenacao == "Estado":
            df_filtrado = df_filtrado.sort_values('Estado')
        elif ordenacao == "Categoria":
            df_filtrado = df_filtrado.sort_values('Categoria')
        elif ordenacao == "Percentual (crescente)":
            df_filtrado = df_filtrado.sort_values('Percentual')
        else:
            df_filtrado = df_filtrado.sort_values('Percentual', ascending=False)
        
        # Exibir tabela
        st.dataframe(
            df_filtrado,
            column_config={
                'Estado': st.column_config.TextColumn(
                    tipo_localidade.capitalize(),
                    help=f"Nome do {tipo_localidade}"
                ),
                'Categoria': st.column_config.TextColumn(
                    "Categoria",
                    help="Categoria do aspecto social"
                ),
                'Percentual': st.column_config.NumberColumn(
                    "Percentual",
                    help="Percentual de candidatos nesta categoria",
                    format="%.1f%%"
                )
            },
            height=400,
            use_container_width=True
        )
        
        # Estatísticas da tabela filtrada
        if len(df_filtrado) > 0:
            st.caption(f"📊 Exibindo {len(df_filtrado)} registros de {len(df_dados)} totais")
        else:
            st.warning("Nenhum registro encontrado com os filtros aplicados.")
        
    except Exception as e:
        st.error(f"Erro ao gerar tabela interativa: {str(e)}")


def _mostrar_opcoes_download(df_dados: pd.DataFrame, tipo_localidade: str) -> None:
    """
    Mostra opções de download e exportação.
    """
    try:
        st.markdown("**💾 Opções de download:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download da tabela completa
            csv_completo = df_dados.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Baixar dados completos (CSV)",
                data=csv_completo,
                file_name=f"aspectos_sociais_{tipo_localidade}_completo.csv",
                mime="text/csv",
                key="download_completo"
            )
        
        with col2:
            # Download da tabela pivô
            try:
                df_pivot = _criar_tabela_pivot(df_dados, tipo_localidade)
                if df_pivot is not None and not df_pivot.empty:
                    csv_pivot = df_pivot.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📊 Baixar tabela cruzada (CSV)",
                        data=csv_pivot,
                        file_name=f"aspectos_sociais_{tipo_localidade}_pivot.csv",
                        mime="text/csv",
                        key="download_pivot"
                    )
            except Exception:
                st.info("Tabela cruzada não disponível para download")
        
        # Informações sobre os dados
        st.markdown("**ℹ️ Informações sobre os dados:**")
        st.write(f"• **Total de registros:** {len(df_dados)}")
        st.write(f"• **{tipo_localidade.capitalize()}s únicos:** {df_dados['Estado'].nunique()}")
        st.write(f"• **Categorias únicas:** {df_dados['Categoria'].nunique()}")
        st.write(f"• **Período de coleta:** ENEM 2023")
        
    except Exception as e:
        st.error(f"Erro ao gerar opções de download: {str(e)}")


def _mostrar_tabela_basica(df_dados: pd.DataFrame, tipo_localidade: str) -> None:
    """
    Mostra versão básica da tabela (fallback).
    """
    try:
        st.markdown("**📋 Tabela básica de dados:**")
        
        # Criar tabela pivô simples
        df_pivot = _criar_tabela_pivot(df_dados, tipo_localidade)
        
        if df_pivot is not None and not df_pivot.empty:
            st.dataframe(
                df_pivot,
                column_config={
                    col: st.column_config.NumberColumn(col, format="%.1f%%") 
                    for col in df_pivot.columns if col != tipo_localidade.capitalize()
                },
                height=400
            )
        else:
            # Fallback para tabela simples
            st.dataframe(df_dados, height=400)
        
    except Exception as e:
        st.error(f"Erro ao exibir tabela básica: {str(e)}")


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
        st.warning("Dados insuficientes para análise de categorias.")
        return
    
    if var_x_plot not in df_correlacao.columns or var_y_plot not in df_correlacao.columns:
        st.warning("Variáveis não encontradas nos dados.")
        return
    
    try:
        st.write("#### Análise das combinações de categorias:")
        
        # Criar tabela de contingência
        tabela_contingencia = pd.crosstab(
            df_correlacao[var_x_plot], 
            df_correlacao[var_y_plot],
            margins=True
        )
        
        st.write("**Tabela de contingência:**")
        st.dataframe(tabela_contingencia, use_container_width=True)
        
        # Mostrar percentuais
        tabela_percentuais = pd.crosstab(
            df_correlacao[var_x_plot], 
            df_correlacao[var_y_plot], 
            normalize='index'
        ) * 100
        
        st.write("**Percentuais por linha:**")
        st.dataframe(tabela_percentuais.round(1), use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao gerar análise de categorias: {str(e)}")


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
        mais_freq = estatisticas['categoria_mais_frequente']
        st.write(f"**Categoria mais frequente:** {mais_freq['Categoria']} ({mais_freq['Quantidade']:,} candidatos)")
    
    # Categoria menos frequente
    if estatisticas.get('categoria_menos_frequente') is not None:
        menos_freq = estatisticas['categoria_menos_frequente']
        st.write(f"**Categoria menos frequente:** {menos_freq['Categoria']} ({menos_freq['Quantidade']:,} candidatos)")
    
    # Número de categorias
    st.write(f"**Número de categorias:** {estatisticas.get('num_categorias', 0)}")
    
    # Média e mediana
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Média:** {estatisticas.get('media', 0):,.1f}")
    with col2:
        st.write(f"**Mediana:** {estatisticas.get('mediana', 0):,.1f}")


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
    
    # Razão entre maior e menor categoria
    if (estatisticas.get('categoria_mais_frequente') is not None and 
        estatisticas.get('categoria_menos_frequente') is not None):
        razao = estatisticas.get('razao_max_min', 0)
        st.write(f"**Razão maior/menor:** {razao:.2f}x")
    
    # Coeficiente de variação
    if 'coef_variacao' in estatisticas:
        cv = estatisticas['coef_variacao']
        st.write(f"**Coeficiente de variação:** {cv:.1f}%")


def _mostrar_analise_concentracao_percentual(contagem_aspecto: pd.DataFrame) -> None:
    """
    Mostra análise de concentração por percentual acumulado.
    """
    # Verificar se temos dados válidos
    if contagem_aspecto is None or contagem_aspecto.empty:
        st.warning("Dados insuficientes para análise de concentração percentual.")
        return
    
    if 'Percentual' not in contagem_aspecto.columns:
        st.warning("Coluna 'Percentual' não encontrada nos dados.")
        return
        
    try:
        st.write("### Análise de concentração")
        
        # Ordenar por percentual decrescente
        df_ordenado = contagem_aspecto.sort_values('Percentual', ascending=False)
        
        # Calcular percentual acumulado
        df_ordenado['Percentual_Acumulado'] = df_ordenado['Percentual'].cumsum()
        
        # Mostrar os top 3
        st.write("**Top 3 categorias (percentual acumulado):**")
        top_3 = df_ordenado.head(3)
        for i, row in top_3.iterrows():
            st.write(f"• {row['Categoria']}: {row['Percentual']:.1f}% (acumulado: {row['Percentual_Acumulado']:.1f}%)")
        
    except Exception as e:
        st.error(f"Erro ao gerar análise de concentração percentual: {str(e)}")


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
        st.selectbox(
            "Categoria em análise:",
            categorias_disponiveis,
            index=categorias_disponiveis.index(categoria_selecionada) if categoria_selecionada in categorias_disponiveis else 0,
            key="categoria_analise_regional"
        )
    else:
        st.write(f"**Categoria em análise:** {categoria_selecionada}")


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
        st.metric("Percentual médio", f"{analise['percentual_medio']:.1f}%")
    
    with col2:
        st.metric("Desvio padrão", f"{analise['desvio_padrao']:.1f}%")
    
    with col3:
        st.metric("Coef. variação", f"{analise['coef_variacao']:.1f}%")
    
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
        st.write(f"• **Diferença:** {diferenca:.1f} pontos percentuais")


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
        st.warning("Dados insuficientes para análise de variabilidade.")
        return
    
    # Exibir classificação de variabilidade
    st.write(f"**Nível de variabilidade:** {analise.get('variabilidade', 'Não disponível')}")
    
    # Interpretar disparidade
    st.write(f"**Nível de disparidade regional:** {analise.get('disparidade', 'Indefinida')}")
    
    # Informação sobre índice de Gini
    if 'indice_gini' in analise:
        st.write(f"**Índice de Gini:** {analise['indice_gini']:.4f}")


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
        st.warning("Dados insuficientes para ranking.")
        return
    
    try:
        # Filtrar pela categoria selecionada
        df_categoria = df_dados[df_dados['Categoria'] == categoria_selecionada]
        
        # Ordenar por percentual decrescente
        df_ranking = df_categoria.sort_values('Percentual', ascending=False)
        
        # Mostrar top 10
        st.write("**Top 10:**")
        top_10 = df_ranking.head(10)
        for i, row in top_10.iterrows():
            st.write(f"{i+1}. {row['Estado']}: {row['Percentual']:.1f}%")
        
    except Exception as e:
        st.error(f"Erro ao gerar ranking: {str(e)}")


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
        st.warning("Dados insuficientes para análise por região.")
        return
    
    try:
        st.write("#### Análise por região:")
        
        # Adicionar informação de região
        df_com_regiao = _adicionar_regiao_aos_estados(df_dados)
        
        if 'Região' not in df_com_regiao.columns:
            st.warning("Informação de região não disponível.")
            return
        
        # Filtrar pela categoria selecionada
        df_categoria = df_com_regiao[df_com_regiao['Categoria'] == categoria_selecionada]
        
        # Agrupar por região
        analise_regional = df_categoria.groupby('Região')['Percentual'].agg(['mean', 'std', 'count']).reset_index()
        analise_regional.columns = ['Região', 'Média', 'Desvio', 'Estados']
        analise_regional = analise_regional.sort_values('Média', ascending=False)
        
        # Mostrar resultados
        for i, row in analise_regional.iterrows():
            st.write(f"• **{row['Região']}:** {row['Média']:.1f}% (±{row['Desvio']:.1f}%, {row['Estados']} estados)")
        
    except Exception as e:
        st.error(f"Erro ao gerar análise por região: {str(e)}")


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


def _mostrar_interpretacao_correlacao(metricas: Dict, variaveis_sociais: Dict, var_x: str, var_y: str) -> None:
    """
    Mostra interpretação contextualizada da correlação entre variáveis.
    """
    try:
        nome_x = variaveis_sociais[var_x].get('nome', var_x)
        nome_y = variaveis_sociais[var_y].get('nome', var_y)
        
        coeficiente = metricas.get('coeficiente', 0)
        p_valor = metricas.get('p_valor', 1)
        
        # Interpretação do coeficiente
        if coeficiente < 0.1:
            forca = "muito fraca"
        elif coeficiente < 0.3:
            forca = "fraca"
        elif coeficiente < 0.5:
            forca = "moderada"
        elif coeficiente < 0.7:
            forca = "forte"
        else:
            forca = "muito forte"
        
        # Significância estatística
        if p_valor < 0.001:
            sig_texto = "extremamente significativa (p < 0.001)"
        elif p_valor < 0.01:
            sig_texto = "altamente significativa (p < 0.01)"
        elif p_valor < 0.05:
            sig_texto = "significativa (p < 0.05)"
        else:
            sig_texto = "não significativa (p ≥ 0.05)"
        
        # Criar interpretação
        interpretacao = f"""
        **Análise da Associação:**
        
        A associação entre **{nome_x}** e **{nome_y}** apresenta uma intensidade **{forca}** 
        (coeficiente = {coeficiente:.3f}) e é **{sig_texto}**.
        
        **Significado prático:**
        - {_gerar_insight_correlacao(coeficiente, nome_x, nome_y)}
        
        **Considerações metodológicas:**
        - Utilizou-se o coeficiente de Cramér's V para medir a associação entre variáveis categóricas
        - O teste qui-quadrado avalia se existe dependência estatística entre as variáveis
        - Valores próximos de 0 indicam independência; próximos de 1 indicam forte associação
        """
        
        st.markdown(interpretacao)
        
    except Exception as e:
        st.error(f"Erro ao gerar interpretação: {str(e)}")


def _mostrar_downloads_correlacao(df_correlacao: pd.DataFrame, metricas: Dict, var_x: str, var_y: str, variaveis_sociais: Dict) -> None:
    """
    Mostra seção de downloads para análise de correlação.
    """
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Dados da Análise:**")
            
            # Preparar dados para download
            dados_download = df_correlacao.copy()
            
            # Download dos dados
            csv = dados_download.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados da correlação (CSV)",
                data=csv,
                file_name=f"correlacao_{var_x}_{var_y}.csv",
                mime="text/csv"
            )
            
        with col2:
            st.markdown("**📈 Relatório de Análise:**")
            
            # Criar relatório
            relatorio = _criar_relatorio_correlacao(metricas, var_x, var_y, variaveis_sociais)
            
            st.download_button(
                label="📄 Baixar relatório (TXT)",
                data=relatorio,
                file_name=f"relatorio_correlacao_{var_x}_{var_y}.txt",
                mime="text/plain"
            )
        
        # Metadados
        st.markdown("**ℹ️ Metadados:**")
        st.info(f"""
        - **Observações:** {len(df_correlacao):,}
        - **Variáveis:** {var_x} × {var_y}
        - **Análise:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
        - **Método:** Coeficiente de Cramér's V
        """)
        
    except Exception as e:
        st.error(f"Erro ao gerar downloads: {str(e)}")


def _mostrar_correlacao_basica(df_correlacao: pd.DataFrame, var_x_plot: str, var_y_plot: str, variaveis_sociais: Dict, var_x: str, var_y: str) -> None:
    """
    Mostra versão básica da análise de correlação como fallback.
    """
    try:
        nome_x = variaveis_sociais[var_x].get('nome', var_x)
        nome_y = variaveis_sociais[var_y].get('nome', var_y)
        
        st.write(f"**Análise básica: {nome_x} × {nome_y}**")
        
        # Tabela de contingência simples
        tabela_contingencia = pd.crosstab(
            df_correlacao[var_x_plot], 
            df_correlacao[var_y_plot], 
            margins=True
        )
        
        st.write("**Tabela de contingência:**")
        st.dataframe(tabela_contingencia)
        
        # Estatísticas básicas
        st.write("**Estatísticas básicas:**")
        st.write(f"- Total de observações: {len(df_correlacao):,}")
        st.write(f"- Categorias em {nome_x}: {df_correlacao[var_x_plot].nunique()}")
        st.write(f"- Categorias em {nome_y}: {df_correlacao[var_y_plot].nunique()}")
        
    except Exception as e:
        st.error(f"Erro na análise básica: {str(e)}")


def _gerar_insight_correlacao(coeficiente: float, nome_x: str, nome_y: str) -> str:
    """
    Gera insight contextualizado sobre a correlação.
    """
    try:
        if coeficiente < 0.1:
            return f"As variáveis {nome_x} e {nome_y} são praticamente independentes, com pouca ou nenhuma associação entre elas."
        elif coeficiente < 0.3:
            return f"Existe uma associação fraca entre {nome_x} e {nome_y}, sugerindo alguma relação, mas não determinística."
        elif coeficiente < 0.5:
            return f"Há uma associação moderada entre {nome_x} e {nome_y}, indicando uma relação perceptível mas não dominante."
        elif coeficiente < 0.7:
            return f"Existe uma associação forte entre {nome_x} e {nome_y}, sugerindo que uma variável tem influência considerável sobre a outra."
        else:
            return f"A associação entre {nome_x} e {nome_y} é muito forte, indicando alta dependência entre as variáveis."
    except:
        return "Análise de insight não disponível."


def _criar_relatorio_correlacao(metricas: Dict, var_x: str, var_y: str, variaveis_sociais: Dict) -> str:
    """
    Cria relatório detalhado da análise de correlação.
    """
    try:
        nome_x = variaveis_sociais[var_x].get('nome', var_x)
        nome_y = variaveis_sociais[var_y].get('nome', var_y)
        
        relatorio = f"""
RELATÓRIO DE ANÁLISE DE CORRELAÇÃO
=====================================

Data: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

VARIÁVEIS ANALISADAS:
- X: {nome_x} ({var_x})
- Y: {nome_y} ({var_y})

MÉTRICAS ESTATÍSTICAS:
- Coeficiente de Cramér's V: {metricas.get('coeficiente', 0):.4f}
- Valor p: {metricas.get('p_valor', 1):.4f}
- Qui-quadrado: {metricas.get('qui_quadrado', 0):.4f}
- Graus de liberdade: {metricas.get('graus_liberdade', 0)}

INTERPRETAÇÃO:
{_gerar_insight_correlacao(metricas.get('coeficiente', 0), nome_x, nome_y)}

SIGNIFICÂNCIA ESTATÍSTICA:
{'Significativa' if metricas.get('p_valor', 1) < 0.05 else 'Não significativa'} (α = 0.05)

METODOLOGIA:
- Teste: Qui-quadrado de Pearson
- Medida de associação: Coeficiente de Cramér's V
- Nível de significância: 5%

OBSERVAÇÕES:
- Esta análise considera apenas a associação entre variáveis categóricas
- Correlação não implica causalidade
- Resultados baseados em dados observacionais
        """
        
        return relatorio.strip()
    
    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}"


def _mostrar_resumo_distribuicao(estatisticas: Dict, nome_aspecto: str, contagem_aspecto: pd.DataFrame) -> None:
    """
    Mostra resumo executivo da distribuição.
    """
    try:
        total_observacoes = contagem_aspecto['Quantidade'].sum()
        total_categorias = len(contagem_aspecto)
        categoria_dominante = contagem_aspecto.loc[contagem_aspecto['Percentual'].idxmax()]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🔢 Total de Observações",
                f"{total_observacoes:,}",
                help="Número total de registros analisados"
            )
            
        with col2:
            st.metric(
                "📊 Categorias",
                f"{total_categorias}",
                help="Número de categorias distintas"
            )
            
        with col3:
            st.metric(
                "🎯 Categoria Dominante",
                f"{categoria_dominante['Percentual']:.1f}%",
                help=f"Categoria: {categoria_dominante.name}"
            )
        
        # Resumo textual
        st.markdown(f"""
        **Resumo da Distribuição de {nome_aspecto}:**
        
        A análise revela que **{categoria_dominante.name}** é a categoria mais representativa, 
        concentrando **{categoria_dominante['Percentual']:.1f}%** dos casos ({categoria_dominante['Quantidade']:,} observações).
        
        A distribuição apresenta **{total_categorias}** categorias distintas, com um 
        **índice de concentração de {estatisticas.get('indice_concentracao', 0):.3f}** 
        ({'alta' if estatisticas.get('indice_concentracao', 0) > 0.5 else 'baixa'} concentração).
        """)
        
    except Exception as e:
        st.error(f"Erro ao gerar resumo: {str(e)}")


def _mostrar_metricas_distribuicao(estatisticas: Dict, nome_aspecto: str) -> None:
    """
    Mostra métricas estatísticas da distribuição.
    """
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Medidas de Tendência Central:**")
            st.write(f"• **Média:** {estatisticas.get('media', 0):.2f}%")
            st.write(f"• **Mediana:** {estatisticas.get('mediana', 0):.2f}%")
            st.write(f"• **Moda:** {estatisticas.get('moda', 0):.2f}%")
            
            st.markdown("**📊 Medidas de Dispersão:**")
            st.write(f"• **Desvio Padrão:** {estatisticas.get('desvio_padrao', 0):.2f}%")
            st.write(f"• **Coeficiente de Variação:** {estatisticas.get('coeficiente_variacao', 0):.2f}%")
            st.write(f"• **Amplitude:** {estatisticas.get('amplitude', 0):.2f}%")
            
        with col2:
            st.markdown("**⚖️ Medidas de Concentração:**")
            st.write(f"• **Índice de Concentração:** {estatisticas.get('indice_concentracao', 0):.3f}")
            st.write(f"• **Índice de Gini:** {estatisticas.get('indice_gini', 0):.3f}")
            st.write(f"• **Entropia:** {estatisticas.get('entropia', 0):.3f}")
            
            st.markdown("**📏 Percentis:**")
            st.write(f"• **P25:** {estatisticas.get('percentil_25', 0):.2f}%")
            st.write(f"• **P75:** {estatisticas.get('percentil_75', 0):.2f}%")
            st.write(f"• **P90:** {estatisticas.get('percentil_90', 0):.2f}%")
            
    except Exception as e:
        st.error(f"Erro ao gerar métricas: {str(e)}")


def _mostrar_ranking_categorias(contagem_aspecto: pd.DataFrame, nome_aspecto: str) -> None:
    """
    Mostra ranking das categorias.
    """
    try:
        # Ordenar por percentual decrescente
        df_ordenado = contagem_aspecto.sort_values('Percentual', ascending=False).reset_index(drop=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Top 5 Categorias:**")
            top_5 = df_ordenado.head(5)
            for i, row in top_5.iterrows():
                percentual = row['Percentual']
                quantidade = row['Quantidade']
                categoria = row.name if hasattr(row, 'name') else str(i+1)
                
                # Barra de progresso visual
                st.markdown(f"**{i+1}º** {categoria}")
                st.progress(percentual / 100)
                st.write(f"   {percentual:.1f}% ({quantidade:,} casos)")
                
        with col2:
            st.markdown("**🔻 5 Menores Categorias:**")
            bottom_5 = df_ordenado.tail(5)
            for i, row in bottom_5.iterrows():
                percentual = row['Percentual']
                quantidade = row['Quantidade']
                categoria = row.name if hasattr(row, 'name') else str(i+1)
                
                st.markdown(f"**{len(df_ordenado)-i}º** {categoria}")
                st.progress(percentual / 100)
                st.write(f"   {percentual:.1f}% ({quantidade:,} casos)")
                
    except Exception as e:
        st.error(f"Erro ao gerar ranking: {str(e)}")


def _mostrar_insights_distribuicao(estatisticas: Dict, contagem_aspecto: pd.DataFrame, nome_aspecto: str) -> None:
    """
    Mostra insights e interpretação da distribuição.
    """
    try:
        # Calcular insights
        total_categorias = len(contagem_aspecto)
        categoria_dominante = contagem_aspecto.loc[contagem_aspecto['Percentual'].idxmax()]
        percentual_dominante = categoria_dominante['Percentual']
        
        # Classificar concentração
        indice_concentracao = estatisticas.get('indice_concentracao', 0)
        if indice_concentracao > 0.7:
            nivel_concentracao = "muito alta"
        elif indice_concentracao > 0.5:
            nivel_concentracao = "alta"
        elif indice_concentracao > 0.3:
            nivel_concentracao = "moderada"
        else:
            nivel_concentracao = "baixa"
        
        # Analisar equidade
        coef_variacao = estatisticas.get('coeficiente_variacao', 0)
        if coef_variacao < 30:
            equidade = "alta equidade"
        elif coef_variacao < 50:
            equidade = "equidade moderada"
        else:
            equidade = "baixa equidade"
        
        # Gerar insights
        st.markdown("**🔍 Principais Insights:**")
        
        insights = f"""
        • **Concentração:** A distribuição apresenta {nivel_concentracao} concentração 
          (índice = {indice_concentracao:.3f}), com a categoria dominante representando {percentual_dominante:.1f}% do total.
        
        • **Equidade:** A distribuição demonstra {equidade} entre as categorias 
          (coeficiente de variação = {coef_variacao:.1f}%).
        
        • **Diversidade:** Com {total_categorias} categorias distintas, a distribuição 
          {'mostra alta diversidade' if total_categorias > 5 else 'apresenta baixa diversidade'}.
        
        • **Padrão:** {'Distribuição assimétrica' if percentual_dominante > 50 else 'Distribuição relativamente balanceada'} 
          com tendência {'concentrada' if indice_concentracao > 0.5 else 'dispersa'}.
        """
        
        st.markdown(insights)
        
        # Recomendações
        st.markdown("**💡 Recomendações:**")
        
        if indice_concentracao > 0.7:
            st.info("🎯 **Alta concentração detectada:** Considere investigar os fatores que levam à concentração em poucas categorias.")
        elif indice_concentracao < 0.3:
            st.info("⚖️ **Distribuição equilibrada:** A distribuição mostra boa diversidade entre as categorias.")
        
        if coef_variacao > 50:
            st.warning("⚠️ **Alta variabilidade:** Existe grande desigualdade entre as categorias.")
        
    except Exception as e:
        st.error(f"Erro ao gerar insights: {str(e)}")


def _mostrar_tabela_interativa_distribuicao(contagem_aspecto: pd.DataFrame, aspecto_social: str) -> None:
    """
    Mostra tabela interativa com filtros e ordenação.
    """
    try:
        # Opções de filtro
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro por percentual mínimo
            min_percentual = st.slider(
                "Percentual mínimo (%)",
                min_value=0.0,
                max_value=float(contagem_aspecto['Percentual'].max()),
                value=0.0,
                step=0.1,
                help="Filtrar categorias com percentual mínimo"
            )
            
        with col2:
            # Ordenação
            ordem = st.selectbox(
                "Ordenar por:",
                ["Percentual (Decrescente)", "Percentual (Crescente)", "Quantidade (Decrescente)", "Quantidade (Crescente)", "Categoria (A-Z)"],
                help="Escolha a ordenação da tabela"
            )
        
        # Aplicar filtros
        df_filtrado = contagem_aspecto[contagem_aspecto['Percentual'] >= min_percentual].copy()
        
        # Aplicar ordenação
        if ordem == "Percentual (Decrescente)":
            df_filtrado = df_filtrado.sort_values('Percentual', ascending=False)
        elif ordem == "Percentual (Crescente)":
            df_filtrado = df_filtrado.sort_values('Percentual', ascending=True)
        elif ordem == "Quantidade (Decrescente)":
            df_filtrado = df_filtrado.sort_values('Quantidade', ascending=False)
        elif ordem == "Quantidade (Crescente)":
            df_filtrado = df_filtrado.sort_values('Quantidade', ascending=True)
        elif ordem == "Categoria (A-Z)":
            df_filtrado = df_filtrado.sort_index()
        
        # Mostrar tabela
        st.dataframe(
            df_filtrado,
            column_config={
                'Quantidade': st.column_config.NumberColumn(
                    'Quantidade',
                    help="Número de observações na categoria",
                    format="%d"
                ),
                'Percentual': st.column_config.NumberColumn(
                    'Percentual (%)',
                    help="Percentual da categoria em relação ao total",
                    format="%.2f%%"
                )
            },
            use_container_width=True
        )
        
        # Informações do filtro
        st.info(f"📊 Mostrando {len(df_filtrado)} de {len(contagem_aspecto)} categorias")
        
    except Exception as e:
        st.error(f"Erro ao gerar tabela interativa: {str(e)}")


def _mostrar_downloads_distribuicao(contagem_aspecto: pd.DataFrame, estatisticas: Dict, aspecto_social: str, nome_aspecto: str) -> None:
    """
    Mostra seção de downloads para análise de distribuição.
    """
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Dados da Análise:**")
            
            # Download dos dados
            csv = contagem_aspecto.to_csv(index=True)
            st.download_button(
                label="📥 Baixar dados da distribuição (CSV)",
                data=csv,
                file_name=f"distribuicao_{aspecto_social}.csv",
                mime="text/csv"
            )
            
        with col2:
            st.markdown("**📈 Relatório de Análise:**")
            
            # Criar relatório
            relatorio = _criar_relatorio_distribuicao(estatisticas, contagem_aspecto, aspecto_social, nome_aspecto)
            
            st.download_button(
                label="📄 Baixar relatório (TXT)",
                data=relatorio,
                file_name=f"relatorio_distribuicao_{aspecto_social}.txt",
                mime="text/plain"
            )
        
        # Metadados
        st.markdown("**ℹ️ Metadados:**")
        st.info(f"""
        - **Total de observações:** {contagem_aspecto['Quantidade'].sum():,}
        - **Categorias:** {len(contagem_aspecto)}
        - **Análise:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
        - **Variável:** {nome_aspecto}
        """)
        
    except Exception as e:
        st.error(f"Erro ao gerar downloads: {str(e)}")


def _mostrar_distribuicao_basica(contagem_aspecto: pd.DataFrame, aspecto_social: str, nome_aspecto: str) -> None:
    """
    Mostra versão básica da análise de distribuição como fallback.
    """
    try:
        st.write(f"**Análise básica: {nome_aspecto}**")
        
        # Estatísticas simples
        total = contagem_aspecto['Quantidade'].sum()
        categorias = len(contagem_aspecto)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total", f"{total:,}")
            
        with col2:
            st.metric("Categorias", f"{categorias}")
        
        # Tabela básica
        st.write("**Distribuição:**")
        st.dataframe(contagem_aspecto)
        
    except Exception as e:
        st.error(f"Erro na análise básica: {str(e)}")


def _criar_relatorio_distribuicao(estatisticas: Dict, contagem_aspecto: pd.DataFrame, aspecto_social: str, nome_aspecto: str) -> str:
    """
    Cria relatório detalhado da análise de distribuição.
    """
    try:
        total_observacoes = contagem_aspecto['Quantidade'].sum()
        total_categorias = len(contagem_aspecto)
        categoria_dominante = contagem_aspecto.loc[contagem_aspecto['Percentual'].idxmax()]
        
        relatorio = f"""
RELATÓRIO DE ANÁLISE DE DISTRIBUIÇÃO
====================================

Data: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

VARIÁVEL ANALISADA:
- Nome: {nome_aspecto}
- Código: {aspecto_social}

RESUMO GERAL:
- Total de observações: {total_observacoes:,}
- Número de categorias: {total_categorias}
- Categoria dominante: {categoria_dominante.name} ({categoria_dominante['Percentual']:.1f}%)

MÉTRICAS ESTATÍSTICAS:
- Média: {estatisticas.get('media', 0):.2f}%
- Mediana: {estatisticas.get('mediana', 0):.2f}%
- Desvio padrão: {estatisticas.get('desvio_padrao', 0):.2f}%
- Coeficiente de variação: {estatisticas.get('coeficiente_variacao', 0):.2f}%
- Índice de concentração: {estatisticas.get('indice_concentracao', 0):.3f}
- Índice de Gini: {estatisticas.get('indice_gini', 0):.3f}

DISTRIBUIÇÃO POR CATEGORIA:
{'-' * 50}
"""
        
        # Adicionar dados por categoria
        for categoria, row in contagem_aspecto.sort_values('Percentual', ascending=False).iterrows():
            relatorio += f"{categoria}: {row['Quantidade']:,} ({row['Percentual']:.2f}%)\n"
        
        relatorio += f"""
{'-' * 50}

INTERPRETAÇÃO:
- Concentração: {'Alta' if estatisticas.get('indice_concentracao', 0) > 0.5 else 'Baixa'}
- Equidade: {'Baixa' if estatisticas.get('coeficiente_variacao', 0) > 50 else 'Alta'}
- Diversidade: {'Alta' if total_categorias > 5 else 'Baixa'}

METODOLOGIA:
- Análise descritiva de distribuição de frequências
- Cálculo de medidas de tendência central e dispersão
- Índices de concentração e equidade
- Análise de padrões e outliers

OBSERVAÇÕES:
- Dados baseados em informações observacionais
- Análise realizada sobre a distribuição completa
- Interpretação contextualizada aos aspectos sociais
        """
        
        return relatorio.strip()
    
    except Exception as e:
        return f"Erro ao gerar relatório: {str(e)}"