import streamlit as st
# Importar módulos do projeto
from utils.mappings import get_mappings
from tabs.geral import render_geral
from tabs.aspectos_sociais import render_aspectos_sociais
from tabs.desempenho import render_desempenho
from utils.data_loader import load_data, filter_data_by_states


# Configuração inicial da página
st.set_page_config(page_title="Dashboard ENEM", page_icon="📚", layout="wide")
st.title("📊 Dashboard de Análise do ENEM - 2023")

# Carregar dados e mapeamentos
microdados = load_data()
colunas_notas, competencia_mapping, race_mapping, sexo_mapping, \
    dependencia_escola_mapping, variaveis_sociais, variaveis_categoricas, \
    desempenho_mapping, infraestrutura_mapping, faixa_etaria_mapping, \
    escolaridade_pai_mae_mapping = get_mappings()

# ---------------------------- FILTROS E CONTROLES ----------------------------
st.sidebar.header("Filtros")

# Obter lista de todos os estados disponíveis
todos_estados = sorted(microdados['SG_UF_PROVA'].unique())

# Adicionar checkbox para selecionar todo o Brasil
selecionar_brasil = st.sidebar.checkbox("Brasil (todos os estados)", value=True)

# Condicionar o multiselect ao estado do checkbox
if selecionar_brasil:
    estados_selecionados = todos_estados
    # Mostrar o multiselect como desativado para indicar a seleção automática
    st.sidebar.multiselect(
        "Estados selecionados:",
        options=todos_estados,
        default=todos_estados,
        disabled=True
    )
else:
    # Permitir seleção manual quando "Brasil" não estiver selecionado
    estados_selecionados = st.sidebar.multiselect(
        "Selecione os Estados:",
        options=todos_estados,
        default=[]
    )
    # Verificar se pelo menos um estado foi selecionado
    if not estados_selecionados:
        st.sidebar.warning("Selecione pelo menos um estado ou marque a opção Brasil.")

# Filtrar dados com base nos estados selecionados
microdados_estados = filter_data_by_states(microdados, estados_selecionados)

# Criar abas
abas = st.tabs(["Geral", "Aspectos Sociais", "Desempenho"])

# Renderizar cada aba
with abas[0]:
    render_geral(microdados_estados, estados_selecionados, colunas_notas, competencia_mapping)
    
with abas[1]:
    render_aspectos_sociais(microdados_estados, estados_selecionados, variaveis_sociais)
    
with abas[2]:
    render_desempenho(microdados, microdados_estados, estados_selecionados, 
                      colunas_notas, competencia_mapping, race_mapping, 
                      variaveis_categoricas, desempenho_mapping)
    
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
        <p style='font-size: 14px;'>Projeto de Iniciação Científica</p>
        <hr style='margin: 10px 0; border-color: #e0e0e0;'>
        <p style='font-size: 12px;'>© 2025 - Todos os direitos reservados</p>
        <p style='font-size: 11px; margin-top: 10px;'>v1.3.0 - Atualizado em 21/03/2025</p>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    # Coluna da equipe (desenvolvedor e orientador)
    st.markdown("""
    <div style='text-align: right; color: #636363;'>
        <p style='font-size: 15px;'><b>Equipe</b></p>
        <p style='font-size: 14px; margin-bottom: 2px;'><b>Desenvolvedor:</b></p>
        <p style='font-size: 13px; margin-top: 0;'>Rafael Petit</p>
        <p style='font-size: 12px; margin-top: 0;'>rpetit.dev@gmail.com</p>
        <p style='font-size: 14px; margin-bottom: 2px; margin-top: 15px;'><b>Orientador:</b></p>
        <p style='font-size: 13px; margin-top: 0;'>Prof. Dr. César C. Xavier</p>
        <p style='font-size: 12px; margin-top: 0;'>cesarcx@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)