import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import geopandas as gpd

#---------------------------------- CARREGAMENTO DE DADOS ----------------------------------#
st.set_page_config(
    page_title="Dashboard ENEM",
    page_icon="📚",
    layout="wide"
)
st.title('Dados Brutos')

colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

@st.cache_data
def load_data():
    microdados = pd.DataFrame(pd.read_csv('sample.csv', sep=';', encoding='ISO-8859-1'))
    dtypes = pd.read_json("dtypes.json", typ='series')
    dados = microdados.astype(dtypes)
    # Converter todas as colunas de notas para float64
    for col in colunas_notas:
        dados[col] = dados[col].astype('float64')
    return dados

# Carregar dados uma única vez
microdados = load_data()


# Mapeamentos (usados em várias partes do código)
competencia_mapping = {
    'NU_NOTA_CN': 'Ciências da Natureza',
    'NU_NOTA_CH': 'Ciências Humanas',
    'NU_NOTA_LC': 'Linguagens e Códigos',
    'NU_NOTA_MT': 'Matemática',
    'NU_NOTA_REDACAO': 'Redação'
}

dependencia_escola_mapping = {
    1: 'Federal',
    2: 'Estadual',
    3: 'Municipal',
    4: 'Privada'
}

sexo_mapping = {
    'M': 'Masculino',
    'F': 'Feminino'
}

race_mapping = {
    0: 'Não declarado',
    1: 'Branca',
    2: 'Preta',
    3: 'Parda',
    4: 'Amarela',
    5: 'Indígena',
    6: 'Não dispõe da informação'
}

desempenho_mapping = {
    1: 'Desempenho Alto',
    2: 'Desempenho Médio',
    3: 'Desempenho Baixo',
}

infraestrutura_mapping = {
    1: 'Infraestrutura Alta',
    2: 'Infraestrutura Média',
    3: 'Infraestrutura Baixa',
}

faixa_etaria_mapping = {
    1: '< 17',
    2: '17',
    3: '18',
    4: '19',
    5: '20',
    6: '21',
    7: '22',
    8: '23',
    9: '24',
    10: '25',
    11: '26 < 30',
    12: '31 < 35',
    13: '36 < 40',
    14: '41 < 45',
    15: '46 < 50',
    16: '51 < 55',
    17: '56 < 60',
    18: '61 < 65',
    19: '66 < 70',
    20: '> 70'
}

escolaridade_pai_mae_mapping = {
    'A': 'Nunca estudou',
    'B': 'Fundamental incompleto',
    'C': 'Fundamental completo',
    'D': 'Médio incompleto',
    'E': 'Médio Completo',
    'F': 'Superior Completo',    
    'G': 'Pós-graduação Completo',
    'H': 'Não sei'
}

variaveis_categoricas = {
    "TP_COR_RACA": {
        "nome": "Raça/Cor",
        "mapeamento": race_mapping,
        "ordem": list(race_mapping.values())
    },
    "TP_SEXO": {
        "nome": "Sexo", 
        "mapeamento": sexo_mapping,
        "ordem": list(sexo_mapping.values())
    },
    "TP_DEPENDENCIA_ADM_ESC": {
        "nome": "Dependência Administrativa", 
        "mapeamento": dependencia_escola_mapping,
        "ordem": list(dependencia_escola_mapping.values())
    },
    "Q001": {
        "nome": "Escolaridade do Pai", 
        "mapeamento": escolaridade_pai_mae_mapping,
        "ordem": list(escolaridade_pai_mae_mapping.values())
    },
    "Q002": {
        "nome": "Escolaridade da Mãe", 
        "mapeamento": escolaridade_pai_mae_mapping,
        "ordem": list(escolaridade_pai_mae_mapping.values())
    },
    "TP_FAIXA_ETARIA": {
        "nome": "Faixa Etária", 
        "mapeamento": faixa_etaria_mapping,
        "ordem": list(faixa_etaria_mapping.values())
    }
}

nome_colunas = {
                "TP_FAIXA_ETARIA": "Faixa Etária",
                "TP_SEXO": "Sexo",
                "TP_ESTADO_CIVIL": "Estado Civil",
                "TP_COR_RACA": "Raça/Cor",
                "TP_NACIONALIDADE": "Nacionalidade",
                "TP_ST_CONCLUSAO": "Situação Conclusão",
                "TP_ANO_CONCLUIU": "Ano Conclusão",
                "TP_ENSINO": "Tipo de Ensino",
                "NO_MUNICIPIO_ESC": "Município Escola",
                "SG_UF_ESC": "Estado Escola",
                "TP_DEPENDENCIA_ADM_ESC": "Dependência Administrativa",
                "TP_LOCALIZACAO_ESC": "Localização Escola",
                "NO_MUNICIPIO_PROVA": "Município Prova",
                "SG_UF_PROVA": "Estado",
                "TP_PRESENCA_CN": "Presença Ciências da Natureza",
                "TP_PRESENCA_CH": "Presença Ciências Humanas",
                "TP_PRESENCA_LC": "Presença Linguagens e Códigos",
                "TP_PRESENCA_MT": "Presença Matemática",
                "NU_NOTA_CN": "Ciências da Natureza",
                "NU_NOTA_CH": "Ciências Humanas",
                "NU_NOTA_LC": "Linguagens e Códigos",
                "NU_NOTA_MT": "Matemática",
                "TX_RESPOSTAS_CN": "Respostas Ciências da Natureza",
                "TX_RESPOSTAS_CH": "Respostas Ciências Humanas",
                "TX_RESPOSTAS_LC": "Respostas Linguagens e Códigos",
                "TX_RESPOSTAS_MT": "Respostas Matemática",
                "SG_UF_RESIDENCIA": "Estado Residência",
                "TP_LINGUA": "Língua Estrangeira",
                "TX_GABARITO_CN": "Gabarito Ciências da Natureza",
                "TX_GABARITO_CH": "Gabarito Ciências Humanas",
                "TX_GABARITO_LC": "Gabarito Linguagens e Códigos",
                "TX_GABARITO_MT": "Gabarito Matemática",
                "TP_STATUS_REDACAO": "Status Redação",
                "NU_NOTA_COMP1": "Nota Competência 1",
                "NU_NOTA_COMP2": "Nota Competência 2",
                "NU_NOTA_COMP3": "Nota Competência 3",
                "NU_NOTA_COMP4": "Nota Competência 4",
                "NU_NOTA_COMP5": "Nota Competência 5",
                "NU_NOTA_REDACAO": "Redação",
                "NU_NOTA_REDACAO": "Redação",
                "Q001": "Escolaridade do Pai",
                "Q002": "Escolaridade da Mãe",
                "Q003": "Ocupação do Pai",
                "Q004": "Ocupação da Mãe",
                "Q005": "Pessoa na Residência",
                "Q006": "Renda Familiar",
                "Q007": "Empregados na Residência",
                "Q008": "Banheiro",
                "Q009": "Quartos",
                "Q010": "Carro",
                "Q011": "Moto",
                "Q012": "Geladeira",
                "Q013": "Freezer",
                "Q014": "Máquina de Lavar",
                "Q015": "Secadora",
                "Q016": "Microondas",
                "Q017": "Lava Louça",
                "Q018": "Aspirador de Pó",
                "Q019": "Televisão",
                "Q020": "DVD",
                "Q021": "TV Assinatura",
                "Q022": "Celular",
                "Q023": "Telefone Fixo",
                "Q024": "Computador",
                "Q025": "Internet",
                "TP_PRESENCA_GERAL": "Presença Geral",
                "NU_DESEMPENHO": "Desempenho",
                "NU_INFRAESTRUTURA": "Infraestrutura",
                "NU_MEDIA_GERAL": "Média Geral",
            }

# Renomear as colunas do DataFrame usando o dicionário nome_colunas
microdados = microdados.rename(columns=nome_colunas)
#---------------------------------- VISUALIZAÇÃO DE DADOS ----------------------------------#

# Dados detalhados
with st.expander("Colunas"):  
        colunas = st.multiselect('Selecione as colunas', list(microdados.columns), list(microdados.columns))

st.sidebar.title('Fitros')
with st.sidebar.expander('Estados'):
    estados = st.multiselect('Selecione os estados', list(microdados['Estado'].unique()), list(microdados['Estado'].unique()))

with st.sidebar.expander('Média das Notas'):
    media = st.slider('Selecione a Média das notas', 0, 1000, (0, 1000))
# with st.sidebar.expander('Nota de Ciências da Natureza'):
#     cn = st.slider('Selecione a Nota de Redação', 0, 1000, (0, 1000))
# with st.sidebar.expander('Nota de Ciências Humanas'):
#     ch = st.slider('Selecione a Nota de Ciências Humanas', 0, 1000, (0, 1000))
# with st.sidebar.expander('Nota de Linguagens e Códigos'):
#     lc = st.slider('Selecione a Nota de Linguagens e Códigos', 0, 1000, (0, 1000))
# with st.sidebar.expander('Nota de Matemática'):
#     mt = st.slider('Selecione a Nota de Matemática', 0, 1000, (0, 1000))
# with st.sidebar.expander('Nota de Redação'):
#     redacao = st.slider('Selecione a Nota de Redação', 0, 1000, (0, 1000))

with st.sidebar.expander('Faixa Etária'):
    faixa_etaria = st.multiselect('Selecione a Faixa Etária', list(faixa_etaria_mapping.values()), list(faixa_etaria_mapping.values()))
with st.sidebar.expander('Sexo'):
    sexo = st.multiselect('Selecione o Sexo', list(sexo_mapping.values()), list(sexo_mapping.values()))
with st.sidebar.expander('Raça/Cor'):
    raca = st.multiselect('Selecione a Raça/Cor', list(race_mapping.values())),
with st.sidebar.expander('Dependência Administrativa'):
    dependencia = st.multiselect('Selecione a Dependência Administrativa', list(dependencia_escola_mapping.values()), list(dependencia_escola_mapping.values()))

query = '`Média Geral` >= @media[0] and `Média Geral` <= @media[1]'

dados_filtrados = microdados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas.')
                          
