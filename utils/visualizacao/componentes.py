import streamlit as st
import pandas as pd
from typing import Dict, List, Any

def criar_filtros_comparativo(
    df_resultados: pd.DataFrame, 
    variaveis_categoricas: Dict[str, Dict[str, Any]], 
    variavel_selecionada: str
) -> Dict[str, Any]:
    """
    Cria filtros interativos para o gráfico comparativo de desempenho.
    
    Parâmetros:
    -----------
    df_resultados: DataFrame
        DataFrame com os resultados processados
    variaveis_categoricas: Dict
        Dicionário com metadados das variáveis categóricas
    variavel_selecionada: str
        Nome da variável categórica selecionada
        
    Retorna:
    --------
    Dict[str, Any]: Configurações dos filtros selecionados
    """
    # Obter competências únicas para filtro
    competencias = sorted(df_resultados['Competência'].unique().tolist())
    
    # Criar layout com colunas para filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tipo_grafico = st.radio(
            "Tipo de gráfico:",
            ["Gráfico de Linhas", "Gráfico de Barras"],
            key=f"tipo_grafico_{variavel_selecionada}"
        )
    
    with col2:
        mostrar_apenas_competencia = st.checkbox(
            "Mostrar apenas uma competência", 
            value=False,
            key=f"mostrar_competencia_{variavel_selecionada}"
        )
    
    with col3:
        ordenar_decrescente = st.checkbox(
            "Ordenar por valor decrescente", 
            value=False,
            key=f"ordenar_{variavel_selecionada}"
        )
    
    # Exibir seletor de competência apenas se checkbox estiver marcado
    competencia_filtro = None
    if mostrar_apenas_competencia and competencias:
        competencia_filtro = st.selectbox(
            "Selecione a competência:",
            options=competencias,
            key=f"competencia_filtro_{variavel_selecionada}"
        )
    
    # Retornar configurações dos filtros
    return {
        'tipo_grafico': tipo_grafico,
        'mostrar_apenas_competencia': mostrar_apenas_competencia,
        'ordenar_decrescente': ordenar_decrescente,
        'competencia_filtro': competencia_filtro
    }


def criar_filtros_dispersao(
    colunas_notas: List[str], 
    competencia_mapping: Dict[str, str]
) -> Dict[str, Any]:
    """
    Cria filtros interativos para o gráfico de dispersão entre competências.
    
    Parâmetros:
    -----------
    colunas_notas: List[str]
        Lista de colunas com notas a analisar
    competencia_mapping: Dict[str, str]
        Mapeamento de códigos para nomes de competências
        
    Retorna:
    --------
    Dict[str, Any]: Configurações dos filtros selecionados
    """
    st.write("### Configurações do gráfico")
    
    # Criar layout com colunas para eixos
    col1, col2 = st.columns(2)
    
    with col1:
        # Eixo X (competência no eixo horizontal)
        eixo_x = st.selectbox(
            "Competência (Eixo X):",
            options=colunas_notas,
            format_func=lambda x: competencia_mapping[x],
            index=0,
            key="eixo_x_dispersao"
        )
        
        # Filtro de sexo
        sexo = st.radio(
            "Filtrar por sexo:",
            options=["Todos", "M", "F"],
            index=0,
            key="sexo_dispersao",
            horizontal=True
        )
        
        # Remoção do checkbox "Excluir notas zero"
        # excluir_notas_zero sempre será True por padrão
        excluir_notas_zero = True
        
    with col2:
        # Eixo Y (competência no eixo vertical)
        opcoes_eixo_y = [col for col in colunas_notas if col != eixo_x]
        
        # Verificar se há opções disponíveis para o eixo Y
        if not opcoes_eixo_y:
            # Se não há opções, usar todas as colunas e mostrar aviso
            opcoes_eixo_y = colunas_notas
            st.warning("Aviso: Mesma competência selecionada para ambos os eixos")
        
        # Garantir que temos pelo menos uma opção
        indice_y = 0
        if len(opcoes_eixo_y) > 1:
            indice_y = 1 if opcoes_eixo_y[0] == eixo_x else 0
        
        eixo_y = st.selectbox(
            "Competência (Eixo Y):",
            options=opcoes_eixo_y,
            format_func=lambda x: competencia_mapping[x],
            index=indice_y,
            key="eixo_y_dispersao"
        )
        
        # Filtro de tipo de escola
        tipo_escola = st.radio(
            "Filtrar por tipo de escola:",
            options=["Todos", "Pública", "Privada"],
            index=0,
            key="escola_dispersao",
            horizontal=True
        )
        
        # Colorir por faixa salarial
        colorir_por_faixa = st.checkbox(
            "Colorir por faixa salarial", 
            value=False,
            key="colorir_faixa_dispersao"
        )
    
    # Filtro de faixa salarial com controle de visibilidade
    if colorir_por_faixa:
        faixa_salarial = st.multiselect(
            "Selecione as faixas salariais:",
            options=list(range(8)),  # 0 a 7
            default=list(range(8)),
            format_func=lambda x: f"Faixa {x}",
            key="faixa_salarial_dispersao"
        )
    else:
        faixa_salarial = list(range(8))  # Todas as faixas
    
    # Retornar configurações dos filtros
    return {
        'eixo_x': eixo_x,
        'eixo_y': eixo_y,
        'sexo': sexo,
        'tipo_escola': tipo_escola,
        'excluir_notas_zero': excluir_notas_zero,
        'faixa_salarial': faixa_salarial,
        'colorir_por_faixa': colorir_por_faixa
    }


def criar_filtros_estados(df_grafico: pd.DataFrame) -> Dict[str, Any]:
    """
    Cria filtros interativos para o gráfico de linha de desempenho por estado.
    
    Parâmetros:
    -----------
    df_grafico: DataFrame
        DataFrame com os dados para o gráfico
        
    Retorna:
    --------
    Dict[str, Any]: Configurações dos filtros selecionados
    """
    # Verificar se temos dados
    if df_grafico is None or df_grafico.empty:
        return {
            'area_selecionada': None,
            'ordenar_por_nota': False,
            'mostrar_apenas_area': False
        }
    
    # Obter áreas únicas para filtro
    areas = sorted(df_grafico['Área'].unique().tolist())
    
    # Criar layout com colunas para filtros
    col1, col2, col3 = st.columns(3)
    
    # Opção para mostrar apenas uma área
    with col1:
        mostrar_apenas_area = st.checkbox(
            "Mostrar apenas uma área", 
            value=False,
            key="mostrar_area_estados"
        )
    
    # Opção para ordenar por nota
    with col2:
        ordenar_por_nota = st.checkbox(
            "Ordenar por nota", 
            value=False,
            key="ordenar_estados"
        )
    
    # Seletor de área (visível apenas se uma das opções acima estiver marcada)
    area_selecionada = None
    if (mostrar_apenas_area or ordenar_por_nota) and areas:
        with col3:
            area_selecionada = st.selectbox(
                "Selecione a área:",
                options=areas,
                key="area_filtro_estados"
            )
    
    # Retornar configurações dos filtros
    return {
        'area_selecionada': area_selecionada,
        'ordenar_por_nota': ordenar_por_nota,
        'mostrar_apenas_area': mostrar_apenas_area
    }