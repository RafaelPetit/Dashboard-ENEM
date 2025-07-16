import streamlit as st
import gc

from utils.helpers.mappings import get_mappings

# Configuração inicial da página
st.set_page_config(
    page_title="Dashboard ENEM Norte - Análise Acadêmica", 
    page_icon="🏠", 
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
    .warning-card {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
    }
    .success-card {
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
    }
    .info-card {
        background-color: #DBEAFE;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
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
    .region-badge {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .tech-badge {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .link-button {
        background-color: #3B82F6;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
        transition: background-color 0.3s;
    }
    .link-button:hover {
        background-color: #2563EB;
        color: white;
        text-decoration: none;
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
        st.session_state.last_data_update = "11/07/2025"

# Função para limpar cache e memória entre navegações
def clear_page_memory():
    """Limpa cache específico de páginas"""
    # Limpar apenas cache relacionado a dados específicos de páginas
    if hasattr(st.cache_data, 'clear'):
        st.cache_data.clear()
    gc.collect()

# Inicializar session state
init_session_state()


# ...existing code...

# Título principal com indicação regional
st.title("🌎 Dashboard ENEM 2023 - Região Norte/Nordeste")
st.markdown("#### Plataforma de Análise Acadêmica para Pesquisa Educacional - Versão Norte/Nordeste")

# Aviso importante sobre a divisão regional
st.markdown("""
<div class="warning-card">
    <h4>📍 Cobertura Regional desta Plataforma</h4>
    <p>
        Esta versão da plataforma contém dados das regiões <strong>Norte e Nordeste</strong>. Para análise das regiões <strong>Sudeste, Sul e Centro-Oeste</strong>, acesse a <strong> Versão abaixo</strong> da plataforma.
    </p>
    <p style="margin-top: 1rem;">
        <a href="https://enem-insights-sul.streamlit.app/" target="_blank" class="link-button">
            🌐 Acessar Versão Sul (SP, RJ, MG, ES, PR, RS, SC, DF, GO, MT, MS)
        </a>
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------- CONTEÚDO PRINCIPAL ----------------------------
# Container principal com duas colunas
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.markdown("""
    <div class="highlight">
        <h3>🎓 Sobre a Pesquisa Científica</h3>
        <p>
            Este dashboard representa o produto final de uma investigação científica desenvolvida na Universidade Paulista (UNIP) 
            como parte de um projeto de Iniciação Científica em Ciência da Computação. A plataforma foi arquitetada 
            para oferecer análises estatísticas rigorosas e visualizações interativas que aprofundam a compreensão 
            sobre os fatores multidimensionais que influenciam o desempenho educacional no Brasil, utilizando 
            os microdados oficiais do ENEM 2023 fornecidos pelo INEP.
        </p>
        <p>
            A metodologia empregada fundamenta-se em técnicas avançadas de ciência de dados, processamento de 
            grandes volumes de informação e análise estatística multivariada, garantindo rigor científico 
            adequado para publicação acadêmica.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Módulos Analíticos Disponíveis")
    
    # Módulo Análise Geral
    st.markdown("""
    <div class="feature-card">
        <h3>🏠 Análise Geral</h3>
        <p><span class="badge">Estatísticas Descritivas</span><span class="badge">Distribuições</span><span class="badge">Comparativos Regionais</span></p>
        <p>
            Oferece uma visão abrangente e panorâmica do cenário educacional das regiões Norte e Nordeste no ENEM 2023. 
            Este módulo implementa análises estatísticas descritivas robustas, incluindo métricas de tendência central, 
            dispersão e forma das distribuições, proporcionando insights fundamentais sobre os padrões de desempenho educacional.
        </p>
        <ul>
            <li><strong>Histogramas interativos:</strong> Distribuição de notas por competência com análises de assimetria e curtose</li>
            <li><strong>Análise regional comparativa:</strong> Métricas estatísticas por estado com identificação de outliers</li>
            <li><strong>Desempenho por área de conhecimento:</strong> Correlações entre Ciências da Natureza, Humanas, Linguagens, Matemática e Redação</li>
            <li><strong>Estudo de participação:</strong> Análise de taxas de ausência, evasão e padrões de comparecimento</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Módulo Aspectos Socioeconômicos
    st.markdown("""
    <div class="feature-card">
        <h3>👥 Aspectos Socioeconômicos</h3>
        <p><span class="badge">Análise Multivariada</span><span class="badge">Correlações</span><span class="badge">Equidade Educacional</span></p>
        <p>
            Módulo dedicado à investigação científica das relações complexas entre fatores socioeconômicos e 
            desempenho educacional. Utiliza técnicas estatísticas avançadas para identificar padrões, desigualdades 
            e correlações significativas, contribuindo para o entendimento das dimensões sociais da educação brasileira.
        </p>
        <ul>
            <li><strong>Análise de renda familiar:</strong> Correlação entre faixas salariais e desempenho acadêmico com testes de significância</li>
            <li><strong>Tipo de escola:</strong> Comparativo estatístico entre instituições públicas e privadas</li>
            <li><strong>Variáveis demográficas:</strong> Impacto de gênero, idade e localização no rendimento escolar</li>
            <li><strong>Índice de infraestrutura:</strong> Análise de componentes principais para avaliação socioeconômica</li>
            <li><strong>Mapas de calor:</strong> Visualização de correlações entre múltiplas variáveis sociais</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Módulo Análise de Desempenho
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Análise de Desempenho</h3>
        <p><span class="badge">Competências ENEM</span><span class="badge">Análise de Redação</span><span class="badge">Padrões Estatísticos</span></p>
        <p>
            Módulo especializado em análises aprofundadas das métricas de desempenho acadêmico, implementando 
            algoritmos estatísticos para identificação de padrões, tendências e relações entre diferentes 
            competências avaliadas no ENEM, com foco especial na análise da prova de Redação.
        </p>
        <ul>
            <li><strong>Análise por competência:</strong> Desempenho detalhado nas cinco competências da Redação com distribuições estatísticas</li>
            <li><strong>Correlações inter-áreas:</strong> Matriz de correlação entre Matemática, Ciências da Natureza, Humanas e Linguagens</li>
            <li><strong>Classificação de desempenho:</strong> Algoritmos de categorização em níveis Alto, Médio e Baixo</li>
            <li><strong>Análise de outliers:</strong> Identificação de padrões atípicos de desempenho para investigação qualitativa</li>
            <li><strong>Gráficos de dispersão:</strong> Visualização de relações não-lineares entre variáveis de desempenho</li>
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
    
    st.info("🌎 **Escopo**: Todas as regiões do Norte e Nordeste disponíveis")
    
    # Status do sistema
    st.markdown("""
    <div class="success-card">
        <h3>🔍 Informações do Dataset Regional</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas sobre o dataset
    col1, col2 = st.columns(2)


    with col1:
        st.metric("Registros Regionais", "1.877.453", help="Candidatos das regiões Norte e Nordeste")
        st.metric("Cobertura Regional", "47,72%", help="Percentual do território nacional coberto nesta versão")
    
    with col2:
        st.metric("Variáveis Analíticas", "31", help="Total de variáveis processadas e otimizadas")
        st.metric("Processamento", st.session_state.last_data_update, help="Data da última otimização dos dados")
    
    # Estados incluídos nesta versão
    st.markdown("""
    <div class="feature-card">
        <h3>🗺️ Regiões Incluídas</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **Norte:** AC, AP, AM, PA, RO, RR, TO
                
    **Nordeste:** AL, BA, CE, MA, PB, PE, PI, RN, SE  
    
    Para análise de Sudeste, Sul e Centro-Oeste utilize as versões abaixo:.
    """)
    
    # Card específico para redirecionamento à versão Sudeste/Sul/Centro-Oeste
    st.markdown("""
    <div class="info-card">
        <h3>🌐 Precisa Analisar Outras Regiões?</h3>
        <p>
            Se você precisa analisar dados das regiões <strong>Sudeste, Sul e Centro-Oeste</strong>, acesse nossa versão complementar:
        </p>
        <p style="text-align: center; margin-top: 1rem;">
            <a href="https://enem-insights-sul.streamlit.app/" target="_blank" class="link-button">
                📊 Dashboard ENEM Sul
            </a>
        </p>
        <p style="font-size: 12px; margin-top: 0.5rem; text-align: center;">
            <em>Mesma metodologia, dados complementares</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Guia rápido
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 Guia de Navegação</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    1. **Configure os filtros** na barra lateral para delimitar sua análise
    2. **Navegue sequencialmente** pelos módulos analíticos no menu
    3. **Interaja com as visualizações** para explorar dados específicos
    4. **Expanda as seções** para acessar análises estatísticas detalhadas
    5. **Interprete os resultados** com auxílio das explicações contextuais
    6. **Aplique os insights** em suas pesquisas
                """)
    
# Arquitetura técnica e metodológica
st.markdown("---")
st.markdown("### 🏗️ Arquitetura Técnica e Metodologia Científica")

method_col1, method_col2, method_col3 = st.columns(3)

with method_col1:
    st.markdown("""
    <div class="feature-card">
        <h4>🔬 Metodologia Científica</h4>
        <p>
            A pesquisa emprega métodos quantitativos rigorosos com análise estatística descritiva e inferencial. 
            O processamento de grandes volumes (Big Data) utiliza algoritmos otimizados para garantir precisão 
            matemática e reprodutibilidade científica. Implementa-se validação sistemática de dados e tratamento 
            de valores ausentes conforme boas práticas de pesquisa empírica.
        </p>
        <p><span class="badge">Análise Multivariada</span><span class="badge">Testes Estatísticos</span><span class="badge">Validação de Dados</span></p>
    </div>
    """, unsafe_allow_html=True)

with method_col2:
    st.markdown("""
    <div class="feature-card">
        <h4>💻 Stack Tecnológico</h4>
        <p>
            <strong>Interface:</strong> Streamlit com arquitetura modular<br>
            <strong>Processamento:</strong> Pandas otimizado + NumPy<br>
            <strong>Visualização:</strong> Plotly para gráficos interativos<br>
            <strong>Análise:</strong> SciPy para estatísticas avançadas<br>
            <strong>Armazenamento:</strong> Formato Parquet otimizado<br>
            <strong>Performance:</strong> Sistema de cache multicamadas
        </p>
        <p><span class="tech-badge">Python</span><span class="tech-badge">Streamlit</span><span class="tech-badge">Plotly</span></p>
    </div>
    """, unsafe_allow_html=True)

with method_col3:
    st.markdown("""
    <div class="feature-card">
        <h4>📋 Limitações e Considerações Éticas</h4>
        <p>
            Esta pesquisa apresenta resultados observacionais que não estabelecem relações causais. 
            Trabalha exclusivamente com dados oficiais do INEP, respeitando integralmente as políticas 
            de privacidade, anonimização e uso ético das informações. A divisão regional visa otimização 
            técnica sem prejuízo à qualidade analítica.
        </p>
        <p><span class="badge">Ética em Pesquisa</span><span class="badge">LGPD Compliance</span></p>
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
        <p style='font-size: 12px; margin-top: 10px; font-style: italic;'>Linha de Pesquisa: Ciência de Dados Educacionais</p>
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #475569;'>
        <p style='font-size: 16px;'><b>Plataforma de Análise Científica do ENEM 2023</b></p>
        <p style='font-size: 14px; margin-top: 1rem;'>Projeto de pesquisa desenvolvido como contribuição científica 
        para a compreensão dos fatores que influenciam o desempenho educacional.</p>
        <hr style='margin: 15px 0; border-color: #E2E8F0;'>
        <p style='font-size: 11px; margin-top: 5px;'>v2.1.0 </p>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    st.markdown("""
    <div style='text-align: right; color: #475569;'>
        <p style='font-size: 16px;'><b>Equipe de Pesquisa</b></p>
        <p style='font-size: 14px; margin-bottom: 5px; margin-top: 10px;'><b>Pesquisador Responsável:</b></p>
        <p style='font-size: 14px; margin-top: 0;'>Rafael Petit</p>
        <p style='font-size: 12px; margin-top: -2px;'>rpetit.dev@gmail.com</p>
        <p style='font-size: 14px; margin-bottom: 5px; margin-top: 15px;'><b>Orientador Científico:</b></p>
        <p style='font-size: 14px; margin-top: 0;'>Prof. Dr. César C. Xavier</p>
        <p style='font-size: 12px; margin-top: -5px;'>cesarcx@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Limpeza de memória ao final
gc.collect()