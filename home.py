import streamlit as st
import gc
import pandas as pd

from utils.mappings import get_mappings
from utils.data_loader import load_data_for_tab
from utils.helpers.sidebar_filter import render_sidebar_filters

# Configuração inicial da página
st.set_page_config(
    page_title="Dashboard ENEM - Análise Acadêmica", 
    page_icon="📚", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1 {
        color: #1E3A8A;
        margin-bottom: 1.5rem;
    }
    h2 {
        color: #2563EB;
        margin-top: 2rem;
    }
    h3 {
        color: #3B82F6;
        margin-top: 1.5rem;
    }
    .highlight {
        background-color: #EFF6FF;
        border-left: 3px solid #2563EB;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E2E8F0;
        color: #64748B;
    }
    .badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Função para inicializar session_state
def init_session_state():
    """Inicializa variáveis do session_state se não existirem"""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = get_mappings()
    
    # Modo de desenvolvimento (para depuração)
    if 'dev_mode' not in st.session_state:
        st.session_state.dev_mode = False
    
    # Data da última atualização
    if 'last_data_update' not in st.session_state:
        st.session_state.last_data_update = "01/07/2025"

# Função para limpar cache e memória entre navegações
def clear_page_memory():
    """Limpa cache específico de páginas"""
    # Limpar apenas cache relacionado a dados específicos de páginas
    if hasattr(st.cache_data, 'clear'):
        st.cache_data.clear()
    gc.collect()

# Inicializar session state
init_session_state()

# Renderizar filtros laterais centralizados (remove duplicidade)
estados_selecionados, locais_selecionados = render_sidebar_filters()

# Título principal
st.title("📊 Dashboard de Análise do ENEM 2023")
st.markdown("#### _Plataforma de Análise Acadêmica para Pesquisa Educacional_")

# ---------------------------- CONTEÚDO PRINCIPAL ----------------------------
# Container principal com duas colunas
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.markdown("""
    <div class="highlight">
        <h3>🎓 Sobre o Projeto</h3>
        <p>
            Este dashboard é produto de uma pesquisa acadêmica desenvolvida na Universidade Paulista (UNIP) 
            como parte de um projeto de Iniciação Científica. A plataforma visa oferecer insights 
            estatísticos e visualizações interativas para aprofundar a compreensão sobre os fatores 
            que influenciam o desempenho educacional no Brasil, utilizando os microdados do ENEM 2023.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Módulos de Análise")
    
    # Módulo Geral
    st.markdown("""
    <div class="feature-card">
        <h3>🏠 Análise Geral</h3>
        <p><span class="badge">Estatísticas</span><span class="badge">Distribuições</span><span class="badge">Comparativos</span></p>
        <p>
            Oferece uma visão abrangente do cenário nacional do ENEM 2023, com métricas-chave, 
            distribuição estatística de notas, análise por estado/região e comparativos entre 
            áreas de conhecimento. Ideal para uma primeira compreensão das tendências gerais.
        </p>
        <ul>
            <li>Histogramas de distribuição de notas por competência</li>
            <li>Comparativo regional com destaques estatísticos</li>
            <li>Análise de desempenho entre áreas de conhecimento</li>
            <li>Estudo de taxas de ausência e evasão</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Módulo Aspectos Sociais
    st.markdown("""
    <div class="feature-card">
        <h3>👥 Aspectos Socioeconômicos</h3>
        <p><span class="badge">Correlações</span><span class="badge">Variáveis Sociais</span><span class="badge">Equidade</span></p>
        <p>
            Explora a relação entre fatores socioeconômicos e o desempenho dos candidatos,
            permitindo a identificação de padrões, desigualdades e correlações significativas 
            entre contexto social e resultados acadêmicos.
        </p>
        <ul>
            <li>Correlação entre renda familiar e desempenho</li>
            <li>Análise por tipo de escola (pública/privada)</li>
            <li>Impacto de variáveis demográficas nas notas</li>
            <li>Investigação sobre fatores de inclusão e acessibilidade</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Módulo Desempenho
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Análise de Desempenho</h3>
        <p><span class="badge">Competências</span><span class="badge">Redação</span><span class="badge">Tendências</span></p>
        <p>
            Aprofunda-se nas métricas específicas de desempenho acadêmico, com foco nas 
            competências avaliadas, padrões de pontuação na redação e análises comparativas 
            temporais e entre subgrupos populacionais.
        </p>
        <ul>
            <li>Desempenho detalhado por competência avaliada</li>
            <li>Análise das notas de redação e seus critérios</li>
            <li>Estudo de fatores específicos que impactam o desempenho</li>
            <li>Identificação de tendências e padrões de evolução</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with main_col2:
    # Card com informações sobre a seleção atual
    st.markdown("""
    <div class="feature-card">
        <h3>📍 Filtros Aplicados</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar dados dos filtros para obter todos os estados
    filtros_dados = load_data_for_tab("localizacao", apenas_filtros=True)
    


    if isinstance(filtros_dados, pd.DataFrame):
        # Coletamos apenas a coluna específica para economizar memória
        todos_estados = filtros_dados["SG_UF_PROVA"].drop_duplicates().sort_values().tolist()
    else:
        raise ValueError("filtros_dados não é um DataFrame válido.")
    
    if estados_selecionados:
        if len(estados_selecionados) == len(todos_estados):
            st.info("🇧🇷 **Escopo**: Todo o Brasil")
        else:
            st.info(f"📊 **Estados selecionados**: {len(estados_selecionados)}")
            
            # Mostrar detalhes da seleção
            if len(locais_selecionados) <= 5:
                for local in locais_selecionados:
                    st.write(f"• {local}")
            else:
                st.write(f"• {locais_selecionados[0]}")
                st.write(f"• {locais_selecionados[1]}")
                st.write("• ...")
                st.write(f"• {locais_selecionados[-1]}")
                st.caption(f"_Total: {len(locais_selecionados)} locais_")
    else:
        st.warning("⚠️ Nenhum estado selecionado")
    
    # Status do sistema
    st.markdown("""
    <div class="feature-card">
        <h3>🔍 Informações do Dataset</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas sobre o dataset
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Registros", "3.933.955", help="Número total de candidatos no dataset")
        st.metric("Cobertura", "100%", help="Percentual de estados brasileiros incluídos")
    
    with col2:
        st.metric("Variáveis", "82", help="Total de variáveis disponíveis nos microdados")
        st.metric("Atualizado em", st.session_state.last_data_update, help="Data da última atualização dos dados")
    
    # Adicionar uma visualização sim    ples para destacar um insight
    st.markdown("""
    <div class="feature-card">
        <h3>💡 Insight em Destaque</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    > **Sabia que...**  
    > A taxa média de ausência no segundo dia de provas é 15,7% maior que no primeiro dia em todo o país?
    
    Este é apenas um dos muitos insights que você pode explorar em nossa plataforma.
    """)
    
    # Guia rápido
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 Guia Rápido</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    1. **Selecione os filtros** desejados na barra lateral
    2. **Navegue entre as análises** usando o menu de páginas
    3. **Interaja com os gráficos** passando o mouse sobre eles
    4. **Explore os expanders** para análises mais detalhadas
    5. **Leia as explicações** contextuais sobre cada visualização
    """)

# Informações acadêmicas e metodológicas
st.markdown("---")
st.markdown("### 📝 Metodologia e Tecnologias")

method_col1, method_col2, method_col3 = st.columns(3)

with method_col1:
    st.markdown("""
    <div class="feature-card">
        <h4>🔬 Metodologia</h4>
        <p>
            A pesquisa utiliza métodos quantitativos de análise estatística descritiva e inferencial,
            com processamento de grandes volumes de dados (Big Data) e visualização interativa para
            identificação de padrões e correlações significativas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with method_col2:
    st.markdown("""
    <div class="feature-card">
        <h4>💻 Tecnologias</h4>
        <p>
            • <strong>Streamlit:</strong> Interface interativa<br>
            • <strong>Polars:</strong> Processamento de dados de alta performance<br>
            • <strong>Plotly:</strong> Visualizações dinâmicas<br>
            • <strong>Python:</strong> Análise estatística avançada<br>
            • <strong>Cloud:</strong> Hospedagem e disponibilização
        </p>
    </div>
    """, unsafe_allow_html=True)

with method_col3:
    st.markdown("""
    <div class="feature-card">
        <h4>📋 Limitações e Considerações</h4>
        <p>
            Os resultados apresentados são observacionais e não determinam causalidade. 
            A pesquisa trabalha com os dados oficiais disponibilizados pelo INEP,
            respeitando todas as políticas de privacidade e uso ético das informações.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Rodapé com informações institucionais
st.markdown("<div class='footer'>", unsafe_allow_html=True)

footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])

with footer_col1:
    try:
        logo = "Logo.jpg"
        st.image(logo, width=120)
    except:
        st.markdown("<h3>UNIP</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='color: #475569;'>
        <p><b>Universidade Paulista</b></p>
        <p style='font-size: 14px;'>Campus Sorocaba</p>
        <p style='font-size: 13px;'>Programa de Iniciação Científica</p>
        <p style='font-size: 13px;'>Curso de Ciência da Computação</p>
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #475569;'>
        <p style='font-size: 16px;'><b>Dashboard de Análise do ENEM 2023</b></p>
        <p style='font-size: 14px; margin-top: 1rem;'>Projeto desenvolvido como parte das atividades de iniciação científica,
        buscando contribuir para a compreensão dos fatores que influenciam o desempenho educacional no Brasil.</p>
        <hr style='margin: 15px 0; border-color: #E2E8F0;'>
        <p style='font-size: 12px;'>© 2025 - Todos os direitos reservados</p>
        <p style='font-size: 11px; margin-top: 5px;'>v2.1.0 - Analytics Engine</p>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    st.markdown("""
    <div style='text-align: right; color: #475569;'>
        <p style='font-size: 16px;'><b>Equipe do Projeto</b></p>
        <p style='font-size: 14px; margin-bottom: 5px; margin-top: 10px;'><b>Pesquisador:</b></p>
        <p style='font-size: 14px; margin-top: 0;'>Rafael Petit</p>
        <p style='font-size: 12px; margin-top: -5px;'>rpetit.dev@gmail.com</p>
        <p style='font-size: 14px; margin-bottom: 5px; margin-top: 15px;'><b>Orientador:</b></p>
        <p style='font-size: 14px; margin-top: 0;'>Prof. Dr. César C. Xavier</p>
        <p style='font-size: 12px; margin-top: -5px;'>cesarcx@gmail.com</p>
        <p style='font-size: 14px; margin-top: 15px;'><a href="https://github.com/usuario/repo" target="_blank">Repositório GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Limpeza de memória ao final
gc.collect()