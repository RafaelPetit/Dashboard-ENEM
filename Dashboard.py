import streamlit as st
# Importar módulos do projeto
from utils.data_loader import load_data, filter_data_by_states
from utils.mappings import get_mappings
from tabs.geral import render_geral
from tabs.aspectos_sociais import render_aspectos_sociais
from tabs.desempenho import render_desempenho


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