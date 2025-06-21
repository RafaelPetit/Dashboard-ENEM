"""
Componentes de UI premium para o dashboard ENEM.
Inclui header, footer e outros elementos visuais padronizados.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any


def render_premium_header(page_title: str = "Analytics ENEM", subtitle: Optional[str] = None) -> None:
    """
    Renderiza o header premium simplificado para todas as páginas.
    
    Args:
        page_title: Título da página
        subtitle: Subtítulo opcional
    """
    # Header premium simplificado
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
    '>
        <h1 style='
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
            color: white;
        '>{page_title}</h1>
        {f'<p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_premium_footer() -> None:
    """Renderiza o footer premium padrão para todas as páginas."""
    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
    
    # Footer premium com design moderno
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem 2rem 2rem;
        margin-top: 2rem;
        border-radius: 12px 12px 0 0;
        color: white;
        position: relative;
        overflow: hidden;
    '>
        <!-- Padrão de fundo sutil -->
        <div style='
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(255,255,255,0.05) 0%, transparent 50%);
            pointer-events: none;
        '></div>
        
        <div style='position: relative; z-index: 1;'>
            <!-- Header do Footer -->
            <div style='text-align: center; margin-bottom: 2.5rem;'>
                <h2 style='
                    margin: 0 0 0.5rem 0;
                    font-size: 2rem;
                    font-weight: 700;
                    background: linear-gradient(45deg, #ffffff, #e8f0ff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                '>Analytics ENEM</h2>
                <p style='
                    margin: 0;
                    font-size: 1.1rem;
                    opacity: 0.9;
                    font-weight: 300;
                '>Transformando dados educacionais em insights estratégicos</p>
            </div>
            
            <!-- Conteúdo principal do footer em grid -->
            <div style='
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 2rem;
                margin-bottom: 2rem;
            '>
                <!-- Coluna 1: Sobre -->
                <div>
                    <h3 style='
                        color: #ffffff;
                        font-size: 1.2rem;
                        margin: 0 0 1rem 0;
                        font-weight: 600;
                        border-bottom: 2px solid rgba(255,255,255,0.3);
                        padding-bottom: 0.5rem;
                    '>📊 Sobre a Plataforma</h3>
                    <p style='
                        margin: 0 0 0.8rem 0;
                        opacity: 0.9;
                        line-height: 1.5;
                        font-size: 0.95rem;
                    '>Análise avançada de 4+ milhões de registros do ENEM 2023 com visualizações interativas e insights em tempo real.</p>
                    <div style='
                        background: rgba(255,255,255,0.1);
                        padding: 0.8rem;
                        border-radius: 8px;
                        border-left: 4px solid #4CAF50;
                    '>
                        <small style='opacity: 0.9;'>✅ Dados oficiais INEP/MEC<br>
                        ✅ Processamento otimizado<br>
                        ✅ Análises estatísticas avançadas</small>
                    </div>
                </div>
                
                <!-- Coluna 2: Funcionalidades -->
                <div>
                    <h3 style='
                        color: #ffffff;
                        font-size: 1.2rem;
                        margin: 0 0 1rem 0;
                        font-weight: 600;
                        border-bottom: 2px solid rgba(255,255,255,0.3);
                        padding-bottom: 0.5rem;
                    '>🚀 Funcionalidades</h3>
                    <ul style='
                        margin: 0;
                        padding-left: 1.2rem;
                        line-height: 1.8;
                        opacity: 0.9;
                    '>
                        <li>Filtros dinâmicos por região/estado</li>
                        <li>Visualizações interativas avançadas</li>
                        <li>Análises socioeconômicas detalhadas</li>
                        <li>Métricas de desempenho em tempo real</li>
                        <li>Exportação de relatórios</li>
                        <li>Interface responsiva e moderna</li>
                    </ul>
                </div>
                
                <!-- Coluna 3: Tecnologia -->
                <div>
                    <h3 style='
                        color: #ffffff;
                        font-size: 1.2rem;
                        margin: 0 0 1rem 0;
                        font-weight: 600;
                        border-bottom: 2px solid rgba(255,255,255,0.3);
                        padding-bottom: 0.5rem;
                    '>⚡ Stack Tecnológico</h3>
                    <div style='
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 0.5rem;
                        margin-bottom: 1rem;
                    '>
                        <span style='
                            background: rgba(255,255,255,0.15);
                            padding: 0.4rem 0.8rem;
                            border-radius: 20px;
                            font-size: 0.85rem;
                            text-align: center;
                            border: 1px solid rgba(255,255,255,0.2);
                        '>🐍 Python</span>
                        <span style='
                            background: rgba(255,255,255,0.15);
                            padding: 0.4rem 0.8rem;
                            border-radius: 20px;
                            font-size: 0.85rem;
                            text-align: center;
                            border: 1px solid rgba(255,255,255,0.2);
                        '>📊 Streamlit</span>
                        <span style='
                            background: rgba(255,255,255,0.15);
                            padding: 0.4rem 0.8rem;
                            border-radius: 20px;
                            font-size: 0.85rem;
                            text-align: center;
                            border: 1px solid rgba(255,255,255,0.2);
                        '>🐼 Pandas</span>
                        <span style='
                            background: rgba(255,255,255,0.15);
                            padding: 0.4rem 0.8rem;
                            border-radius: 20px;
                            font-size: 0.85rem;
                            text-align: center;
                            border: 1px solid rgba(255,255,255,0.2);
                        '>📈 Plotly</span>
                    </div>
                    <div style='
                        background: rgba(255,255,255,0.1);
                        padding: 0.8rem;
                        border-radius: 8px;
                        text-align: center;
                    '>
                        <small style='opacity: 0.9;'>🏗️ Arquitetura SOLID & Clean Code</small>
                    </div>
                </div>
            </div>
            
            <!-- Separador -->
            <div style='
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                margin: 2rem 0 1.5rem 0;
            '></div>
            
            <!-- Footer inferior -->
            <div style='
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
            '>
                <div style='opacity: 0.8;'>
                    <strong>© 2024 Analytics ENEM</strong> | Desenvolvido para pesquisa educacional
                </div>
                <div style='display: flex; gap: 1.5rem; align-items: center;'>
                    <span style='
                        background: rgba(255,255,255,0.15);
                        padding: 0.3rem 0.8rem;
                        border-radius: 15px;
                        font-size: 0.8rem;
                        border: 1px solid rgba(255,255,255,0.2);
                    '>📄 INEP/MEC</span>
                    <span style='
                        background: rgba(76,175,80,0.2);
                        color: #4CAF50;
                        padding: 0.3rem 0.8rem;
                        border-radius: 15px;
                        font-size: 0.8rem;
                        border: 1px solid #4CAF50;
                        font-weight: 600;
                    '>✅ ATIVO</span>
                </div>
            </div>
            
            <!-- Versão e build info -->
            <div style='
                text-align: center;
                margin-top: 1.5rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(255,255,255,0.2);
                opacity: 0.7;
                font-size: 0.85rem;
            '>
                <span>v2.0.0 | Build Enterprise | Última atualização: {datetime.now().strftime("%d/%m/%Y")}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_bar() -> None:
    """Renderiza uma barra de status simplificada."""
    col1, col2, col3, col4 = st.columns(4)
    
    # Status do sistema
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 0.5rem; background: #f8f9fa; border-radius: 6px;'>
            <div style='font-size: 1rem; font-weight: bold; color: #28a745;'>🟢 Online</div>
            <div style='font-size: 0.8rem; color: #666;'>Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Dados carregados
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 0.5rem; background: #f8f9fa; border-radius: 6px;'>
            <div style='font-size: 1rem; font-weight: bold; color: #007bff;'>4M+</div>
            <div style='font-size: 0.8rem; color: #666;'>Candidatos</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cobertura
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 0.5rem; background: #f8f9fa; border-radius: 6px;'>
            <div style='font-size: 1rem; font-weight: bold; color: #fd7e14;'>27</div>
            <div style='font-size: 0.8rem; color: #666;'>Estados</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Horário atual
    with col4:
        current_time = datetime.now().strftime("%H:%M")
        st.markdown(f"""
        <div style='text-align: center; padding: 0.5rem; background: #f8f9fa; border-radius: 6px;'>
            <div style='font-size: 1rem; font-weight: bold; color: #6f42c1;'>{current_time}</div>
            <div style='font-size: 0.8rem; color: #666;'>Atualizado</div>
        </div>
        """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, delta: Optional[str] = None, 
                      delta_color: str = "normal", icon: str = "📊") -> None:
    """
    Renderiza um card de métrica premium.
    
    Args:
        title: Título da métrica
        value: Valor principal
        delta: Variação (opcional)
        delta_color: Cor da variação (normal, inverse)
        icon: Ícone para exibir
    """
    delta_html = ""
    if delta:
        delta_style = "color: #d32f2f;" if delta_color == "inverse" else "color: #2e7d32;"
        delta_html = f"<div style='font-size: 0.9rem; {delta_style} margin-top: 0.5rem;'>{delta}</div>"
    
    st.markdown(f"""
    <div style='
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s ease;
    '>
        <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
            <span style='font-size: 1.5rem; margin-right: 0.5rem;'>{icon}</span>
            <h3 style='margin: 0; color: #333; font-size: 1rem; font-weight: 600;'>{title}</h3>
        </div>
        <div style='font-size: 2rem; font-weight: bold; color: #667eea; margin: 0.5rem 0;'>{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_info_callout(message: str, type: str = "info") -> None:
    """
    Renderiza um callout informativo.
    
    Args:
        message: Mensagem a ser exibida
        type: Tipo do callout (info, success, warning, error)
    """
    colors = {
        "info": {"bg": "#e3f2fd", "border": "#2196F3", "icon": "ℹ️"},
        "success": {"bg": "#e8f5e8", "border": "#4CAF50", "icon": "✅"},
        "warning": {"bg": "#fff3e0", "border": "#ff9800", "icon": "⚠️"},
        "error": {"bg": "#ffebee", "border": "#f44336", "icon": "❌"}
    }
    
    style = colors.get(type, colors["info"])
    
    st.markdown(f"""
    <div style='
        background: {style["bg"]};
        border-left: 4px solid {style["border"]};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    '>
        <div style='display: flex; align-items: center;'>
            <span style='font-size: 1.2rem; margin-right: 0.5rem;'>{style["icon"]}</span>
            <span style='color: #333;'>{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
