import streamlit as st
import pandas as pd
import gc
import time
# Importar módulos do projeto
from utils.mappings import get_mappings
from tabs.geral import render_geral
from tabs.aspectos_sociais import render_aspectos_sociais
from tabs.desempenho import render_desempenho
from utils.data_loader import load_data_for_tab, filter_data_by_states, agrupar_estados_em_regioes
from utils.helpers.cache_utils import release_memory

# Configuração inicial da página
st.set_page_config(page_title="Dashboard ENEM", page_icon="📚", layout="wide")
st.title("📊 Dashboard de Análise do ENEM - 2023")

# Carregar mapeamentos (novo formato: um único dicionário)
mappings = get_mappings()
colunas_notas = mappings['colunas_notas']
competencia_mapping = mappings['competencia_mapping']
race_mapping = mappings['race_mapping']
sexo_mapping = mappings['sexo_mapping']
dependencia_escola_mapping = mappings['dependencia_escola_mapping']
variaveis_sociais = mappings['variaveis_sociais']
variaveis_categoricas = mappings['variaveis_categoricas']
desempenho_mapping = mappings['desempenho_mapping']
infraestrutura_mapping = mappings['infraestrutura_mapping']
faixa_etaria_mapping = mappings['faixa_etaria_mapping']
escolaridade_pai_mae_mapping = mappings['escolaridade_pai_mae_mapping']
regioes_mapping = mappings['regioes_mapping']
faixa_salarial = mappings['faixa_salarial']

# Carregar apenas os dados mínimos necessários para os filtros iniciais
# (só precisamos da coluna de estado para o filtro)
with st.spinner("Carregando dados iniciais..."):
    filtros_dados = load_data_for_tab("geral")

# ---------------------------- FILTROS E CONTROLES ----------------------------
st.sidebar.header("Filtros")

# Obter lista de todos os estados disponíveis
todos_estados = sorted(filtros_dados['SG_UF_PROVA'].unique())
todas_regioes = sorted(regioes_mapping.keys())

# Adicionar checkbox para selecionar todo o Brasil
selecionar_brasil = st.sidebar.checkbox("Brasil (todos os estados)", value=True)

# Variáveis para controlar o estado da seleção
estados_selecionados = []
regioes_selecionadas = []

# Função para converter seleção de regiões em lista de estados
def get_estados_por_regiao(regioes_selecionadas):
    estados = []
    for regiao in regioes_selecionadas:
        estados.extend(regioes_mapping[regiao])
    return sorted(list(set(estados)))  # Remover duplicatas e ordenar

if selecionar_brasil:
    # Se Brasil estiver selecionado, todos os estados estão selecionados
    estados_selecionados = todos_estados
    regioes_selecionadas = todas_regioes
    
    # Mostrar os selects como desativados para indicar a seleção automática
    st.sidebar.multiselect(
        "Regiões selecionadas:",
        options=todas_regioes,
        default=todas_regioes,
        disabled=True,
        help="Selecione regiões específicas quando a opção Brasil estiver desmarcada"
    )
    
    st.sidebar.multiselect(
        "Estados selecionados:",
        options=todos_estados,
        default=todos_estados,
        disabled=True,
        help="Todos os estados estão selecionados. Desmarque 'Brasil' para selecionar estados específicos."
    )
    
else:
    # Permitir seleção manual quando "Brasil" não estiver selecionado
    st.sidebar.markdown("#### Filtrar por região")
    
    # Seleção por região
    regioes_selecionadas = st.sidebar.multiselect(
        "Selecione as regiões:",
        options=todas_regioes,
        default=[],
        help="Selecionar uma região automaticamente seleciona todos os seus estados"
    )
    
    # Obter estados das regiões selecionadas
    estados_das_regioes = get_estados_por_regiao(regioes_selecionadas)
    
    st.sidebar.markdown("#### Filtrar por estado")
    st.sidebar.markdown(
        "<p style='font-size:12px; color:#666;'>Estados das regiões selecionadas já estão incluídos.</p>", 
        unsafe_allow_html=True
    )
    
    # Seleção manual de estados adicionais
    estados_adicionais = st.sidebar.multiselect(
        "Selecione estados específicos:",
        options=[e for e in todos_estados if e not in estados_das_regioes],
        default=[],
        help="Selecione estados específicos além dos já incluídos pelas regiões selecionadas"
    )
    
    # Combinar estados das regiões com estados adicionais selecionados manualmente
    estados_selecionados = sorted(list(set(estados_das_regioes + estados_adicionais)))
    
    # Verificar se pelo menos um estado ou região foi selecionado
    if not estados_selecionados:
        st.sidebar.warning("Selecione pelo menos uma região ou estado, ou marque a opção Brasil.")

# Mostrar resumo dos filtros aplicados
if estados_selecionados:
    if len(estados_selecionados) == len(todos_estados):
        st.sidebar.success("✅ Dados de todo o Brasil")
    else:
        if regioes_selecionadas:
            st.sidebar.success(f"✅ Regiões: {', '.join(regioes_selecionadas)}")
        if 'estados_adicionais' in locals() and estados_adicionais and not selecionar_brasil:
            st.sidebar.success(f"✅ Estados adicionais: {', '.join(estados_adicionais)}")
        st.sidebar.info(f"Total: {len(estados_selecionados)} estados selecionados")

# Agrupar estados em regiões para exibição amigável
locais_selecionados = agrupar_estados_em_regioes(estados_selecionados, regioes_mapping)

# Liberar memória dos dados usados apenas para filtros
del filtros_dados
gc.collect()

# Criar abas
abas = st.tabs(["Geral", "Aspectos Sociais", "Desempenho"])

# Renderizar cada aba com seus dados específicos
with abas[0]:
    try:
        # Carregar dados específicos para aba Geral
        with st.spinner("Carregando dados para análise geral..."):
            microdados_geral = load_data_for_tab("geral")
            # Filtrar dados com base nos estados selecionados
            microdados_estados_geral = filter_data_by_states(microdados_geral, estados_selecionados)
        
        # Renderizar aba
        render_geral(microdados_estados_geral, estados_selecionados, locais_selecionados, 
                    colunas_notas, competencia_mapping)
        # Liberar memória
        release_memory([microdados_geral, microdados_estados_geral])
    except Exception as e:
        st.error(f"Erro ao carregar a aba Geral: {str(e)}")
    
with abas[1]:
    try:
        # Carregar dados específicos para aba Aspectos Sociais
        with st.spinner("Carregando dados para análise de aspectos sociais..."):
            microdados_aspectos = load_data_for_tab("aspectos_sociais")
            # Filtrar dados com base nos estados selecionados 
            microdados_estados_aspectos = filter_data_by_states(microdados_aspectos, estados_selecionados)
        
        # Verificar se temos dados suficientes para análise
        if microdados_estados_aspectos.empty:
            st.warning("Não há dados suficientes para análise de aspectos sociais com os filtros atuais.")
        else:
            # Renderizar aba
            render_aspectos_sociais(microdados_estados_aspectos, estados_selecionados, 
                                  locais_selecionados, variaveis_sociais)
        
        # Liberar memória
        release_memory([microdados_aspectos, microdados_estados_aspectos])
    except Exception as e:
        st.error(f"Erro ao carregar a aba Aspectos Sociais: {str(e)}")
    
with abas[2]:
    try:
        # Carregar dados específicos para aba Desempenho
        with st.spinner("Carregando dados para análise de desempenho..."):
            microdados_desempenho = load_data_for_tab("desempenho")
            # Filtrar dados com base nos estados selecionados
            microdados_estados_desempenho = filter_data_by_states(microdados_desempenho, estados_selecionados)
        
        # Renderizar aba
        render_desempenho(microdados_desempenho, microdados_estados_desempenho, estados_selecionados, 
                        locais_selecionados, colunas_notas, competencia_mapping, 
                        race_mapping, variaveis_categoricas, desempenho_mapping)
        # Liberar memória
        release_memory([microdados_desempenho, microdados_estados_desempenho])
    except Exception as e:
        st.error(f"Erro ao carregar a aba Desempenho: {str(e)}")
    
# Forçar coleta de lixo para garantir liberação de memória
gc.collect()

# Exibir informações sobre o projeto
st.markdown("---")  # Linha divisória

# Criando o layout do rodapé melhorado
footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])

with footer_col1:
    # Coluna da instituição
    try:
        logo = "Logo.jpg"  # Caminho para o logo
        st.image(logo, width=100)
    except:
        st.write("**UNIP - Universidade Paulista**")
    
    st.markdown("""
    <div style='color: #636363; margin-top: 10px;'>
        <p><b>Universidade Paulista</b></p>
        <p style='font-size: 13px;'>Campus Sorocaba</p>
        <p style='font-size: 12px;'>Curso de Ciência da Computação</p>
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    # Informações sobre o projeto (centralizado)
    st.markdown("""
    <div style='text-align: center; color: #636363;'>
        <p style='font-size: 16px;'><b>Dashboard de Análise do ENEM 2023</b></p>
                <br>
        <p style='font-size: 14px;'>Projeto de Iniciação Científica</p>
        <hr style='margin: 10px 0; border-color: #e0e0e0;'>
        <p style='font-size: 12px;'>© 2025 - Todos os direitos reservados</p>
        <p style='font-size: 11px; margin-top: 10px;'>v1.5.0 - Atualizado em 28/05/2025</p>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    # Coluna da equipe (desenvolvedor e orientador)
    st.markdown("""
    <div style='text-align: right; color: #636363;'>
        <p style='font-size: 15px;'><b>Equipe</b></p>
        <p style='font-size: 14px; margin-bottom: 2px;'><b>Desenvolvedor:</b></p>
        <p style='font-size: 13px; margin-top: 0;'>Rafael Petit <br> rpetit.dev@gmail.com</p>
        <p style='font-size: 14px; margin-bottom: 2px; margin-top: 15px;'><b>Orientador:</b></p>
        <p style='font-size: 13px; margin-top: 0;'>Prof. Dr. César C. Xavier <br> cesarcx@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)