import streamlit as st

def titulo_com_tooltip(titulo, explicacao, chave=None):
    """
    Cria um título com ícone de informação que mostra um tooltip ao passar o mouse.
    
    Parâmetros:
    -----------
    titulo : str
        Texto do título
    explicacao : str
        Texto explicativo a ser mostrado no tooltip
    chave : str, opcional
        Chave única para o componente
    """
    # CSS para o tooltip
    st.markdown("""
    <style>
    .tooltip-container {
        position: relative;
        display: inline-flex;
        align-items: center;
    }
    .tooltip-icon {
        position: relative;
        margin-left: 8px;
        color: #9c9c9c;
        font-size: 16px;
        cursor: help;
    }
    .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        left: 30px;
        top: -10px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 14px;
        line-height: 1.5;
    }
    .tooltip-icon:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Criar HTML para o título com tooltip
    tooltip_html = f"""
    <div class="tooltip-container">
        <h3>{titulo}</h3>
        <div class="tooltip-icon">ⓘ
            <div class="tooltip-text">{explicacao}</div>
        </div>
    </div>
    """
    
    # Renderizar o HTML
    st.markdown(tooltip_html, unsafe_allow_html=True)

def custom_metric_with_tooltip(label, value, delta=None, delta_color="normal", explicacao="", key=None):
    """
    Cria uma métrica personalizada com ícone de tooltip integrado ao título.
    
    Parâmetros:
    -----------
    label : str
        Título da métrica
    value : str ou número
        Valor principal da métrica
    delta : str ou número, opcional
        Valor de delta da métrica
    delta_color : str
        Cor do delta: "normal" (verde/vermelho), "inverse", "off" (cinza)
    explicacao : str
        Texto explicativo a ser mostrado no tooltip
    key : str, opcional
        Chave única para o componente
    """
    # Formatação do delta
    delta_html = ""
    if delta is not None:
        delta_value = delta
        if isinstance(delta, (int, float)):
            delta_sign = "+" if delta > 0 else ""
            delta_value = f"{delta_sign}{delta}"
        
        # Determine a cor baseada no parâmetro delta_color
        if delta_color == "normal":
            color_class = "positive" if isinstance(delta, (int, float)) and delta > 0 else "negative"
        elif delta_color == "inverse":
            color_class = "negative" if isinstance(delta, (int, float)) and delta > 0 else "positive"
        else:  # "off"
            color_class = "neutral"
            
        delta_html = f'<div class="metric-delta {color_class}">{delta_value}</div>'

    # Determinar se está na metade direita da tela
    if key is not None:
        try:
            is_right_side = key > 3
        except (ValueError, TypeError):
            is_right_side = False

    # CSS para a métrica personalizada
    st.markdown("""
    <style>
    .custom-metric {
        font-family: "Source Sans Pro", sans-serif;
    }
    .metric-label {
        display: flex;
        align-items: center;
        color: black;
        font-size: 25px;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .tooltip-icon {
        margin-left: 5px;
        color: #9c9c9c;
        font-size: 16px;
        cursor: help;
        position: relative;
    }
    .tooltip-text {
        visibility: hidden;
        width: 250px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1000;
        top: 100%;
        left: 0;
        margin-top: 5px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
        font-weight: normal;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .tooltip-right .tooltip-text {
        left: auto;
        right: 0;
    }
    .tooltip-icon:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    .metric-value {
        color: black;
        font-size: 30px;
        font-weight: 700;
        line-height: 1;
    }
    .metric-delta {
        font-size: 14px;
        font-weight: 500;
        margin-top: 0.2rem;
    }
    .metric-delta.positive {
        color: rgb(9, 171, 59);
    }
    .metric-delta.negative {
        color: rgb(255, 43, 43);
    }
    .metric-delta.neutral {
        color: rgb(151, 151, 151);
    }
    /* Ajuste para alinhamento com outras métricas do Streamlit */
    .custom-metric {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    tooltip_position_class = "tooltip-right" if is_right_side else ""
    
    # HTML para a métrica personalizada
    metric_html = f"""
    <div class="custom-metric-container">
        <div class="custom-metric">
            <div class="metric-label">
                {label}
                <span class="tooltip-icon {tooltip_position_class}">ⓘ
                    <div class="tooltip-text">{explicacao}</div>
                </span>
            </div>
            <div class="metric-value">{value}</div>
            {delta_html}
    </div>
    """
    
    st.markdown(metric_html, unsafe_allow_html=True)