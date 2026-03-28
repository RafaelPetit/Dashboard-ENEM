from typing import Any, Optional
import pandas as pd
from utils.helpers.constants import LIMIARES_ESTATISTICOS

# Constantes para classificação de correlação
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS.get('correlacao_fraca', 0.3)
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS.get('correlacao_moderada', 0.7)
LIMITE_CORRELACAO_FORTE = LIMIARES_ESTATISTICOS.get('correlacao_forte', 0.8)

def get_tooltip_correlacao_aspectos() -> str:
    """
    Retorna o texto do tooltip para a análise de correlação de aspectos sociais.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Explore relações entre diferentes características sociais dos candidatos.
    
    <b>Como usar:</b><br>
    - Selecione dois aspectos sociais diferentes para comparar
    - Escolha entre Heatmap (distribuição proporcional), Barras Empilhadas (composição) ou Sankey (fluxo)
    - Passe o mouse sobre os elementos para ver detalhes precisos
    - Consulte a "Análise estatística detalhada" para métricas avançadas
    
    Esta análise permite identificar padrões de associação entre características socioeconômicas, demográficas e educacionais, revelando estruturas subjacentes nos dados.
    
    As visualizações são otimizadas para lidar com grandes volumes de dados, mantendo alta performance mesmo com milhões de registros.
    """


def get_tooltip_distribuicao_aspectos() -> str:
    """
    Retorna o texto do tooltip para a visualização de distribuição de aspectos sociais.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Analise a distribuição de candidatos por diferentes categorias sociais.
    
    <b>Como usar:</b><br>
    - Selecione o aspecto social de interesse
    - Escolha entre gráficos de Barras (para comparações diretas), Linha (para tendências) ou Pizza (para proporções)
    - Veja "Dados detalhados" no expander abaixo do gráfico
    - Analise estatísticas de concentração e equidade na distribuição
    
    Esta visualização permite identificar rapidamente perfis predominantes e grupos minoritários, fornecendo contexto essencial para interpretação dos resultados educacionais.
    
    Os dados são processados com técnicas de otimização de memória para garantir desempenho mesmo com conjuntos de dados muito grandes.
    """


def get_tooltip_aspectos_por_estado() -> str:
    """
    Retorna o texto do tooltip para a visualização de aspectos sociais por estado/região.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Compare como as características sociais variam entre estados e regiões do Brasil.
    
    <b>Como usar:</b><br>
    - Selecione o aspecto social para análise geográfica
    - Ative a ordenação para ver rankings estaduais
    - Selecione uma categoria específica para análise aprofundada
    - Alterne entre visualização por estado ou por região
    - Explore a "Análise regional detalhada" para identificar padrões geográficos
    
    Esta visualização revela disparidades territoriais importantes nas características socioeconômicas dos candidatos, oferecendo insights sobre desigualdades regionais.
    
    Os dados são processados por lotes e com técnicas de cache para garantir performance mesmo com milhões de registros.
    """


def get_explicacao_heatmap(var_x_nome: str, var_y_nome: str) -> str:
    """
    Retorna explicação contextualizada para o gráfico de heatmap.
    
    Parâmetros:
    -----------
    var_x_nome : str
        Nome da variável no eixo X
    var_y_nome : str
        Nome da variável no eixo Y
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação de parâmetros
    if not var_x_nome or not var_y_nome:
        var_x_nome = "primeira característica" if not var_x_nome else var_x_nome
        var_y_nome = "segunda característica" if not var_y_nome else var_y_nome
    
    return f"""
    **Análise da correlação entre {var_x_nome} e {var_y_nome}:**
    
    O heatmap revela padrões importantes na distribuição demográfica:
    
    - **Intensidade das cores:**
      Cores mais escuras indicam maior concentração percentual de candidatos nessa combinação de características
    
    - **Padrões de distribuição:**
      Observe como certos valores de {var_x_nome} se associam a categorias específicas de {var_y_nome}
    
    - **Distribuição horizontal:**
      Cada linha mostra como os candidatos de uma categoria específica de {var_x_nome} se distribuem entre as categorias de {var_y_nome}
    
    - **Gradientes e contrastes:**
      Áreas com mudanças abruptas de cor indicam fronteiras entre grupos sociais com perfis distintos
    
    Esta visualização é particularmente útil para identificar associações entre características sociais e detectar grupos com perfis demográficos distintos.
    
    **📊 Análise estatística:** Expanda a seção "Ver análise estatística detalhada" logo abaixo para acessar métricas de associação como V de Cramer, testes de significância e análise aprofundada das relações entre categorias.
    """


def get_explicacao_barras_empilhadas(var_x_nome: str, var_y_nome: str) -> str:
    """
    Retorna explicação contextualizada para o gráfico de barras empilhadas.
    
    Parâmetros:
    -----------
    var_x_nome : str
        Nome da variável no eixo X
    var_y_nome : str
        Nome da variável no eixo Y
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação de parâmetros
    if not var_x_nome or not var_y_nome:
        var_x_nome = "primeira característica" if not var_x_nome else var_x_nome
        var_y_nome = "segunda característica" if not var_y_nome else var_y_nome
    
    return f"""
    **Análise da distribuição de {var_y_nome} por {var_x_nome}:**
    
    O gráfico de barras empilhadas evidencia:
    
    - **Composição demográfica:**
      Cada barra mostra a distribuição percentual de {var_y_nome} dentro de uma categoria de {var_x_nome}
    
    - **Comparação entre grupos:**
      Compare visualmente como a distribuição de {var_y_nome} varia entre diferentes categorias de {var_x_nome}
    
    - **Proporções relativas:**
      Identifique quais combinações de características são mais ou menos comuns na população estudada
    
    - **Variações percentuais:**
      As diferenças na altura de cada segmento revelam disparidades importantes entre os perfis demográficos
    
    Esta visualização facilita a comparação proporcional entre diferentes grupos demográficos, permitindo identificar desequilíbrios na representação e tendências estruturais.
    
    **📊 Estatísticas avançadas:** Clique em "Ver análise estatística detalhada" abaixo para explorar métricas de associação, identificar padrões significativos e acessar a tabela de contingência completa entre as categorias.
    """


def get_explicacao_sankey(var_x_nome: str, var_y_nome: str) -> str:
    """
    Retorna explicação contextualizada para o diagrama de Sankey.
    
    Parâmetros:
    -----------
    var_x_nome : str
        Nome da variável no eixo X
    var_y_nome : str
        Nome da variável no eixo Y
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação de parâmetros
    if not var_x_nome or not var_y_nome:
        var_x_nome = "primeira característica" if not var_x_nome else var_x_nome
        var_y_nome = "segunda característica" if not var_y_nome else var_y_nome
    
    return f"""
    **Análise de fluxo entre {var_x_nome} e {var_y_nome}:**
    
    O diagrama de Sankey ilustra como os candidatos fluem entre categorias:
    
    - **Largura das conexões:**
      Quanto mais larga a conexão, maior o número de candidatos que compartilham essas características
    
    - **Rotas predominantes:**
      Identifique as combinações mais comuns de {var_x_nome} e {var_y_nome} através das conexões mais espessas
    
    - **Padrões de associação:**
      Observe como categorias específicas de {var_x_nome} se distribuem entre as diferentes categorias de {var_y_nome}
    
    - **Concentrações e dispersões:**
      Nós com muitas conexões indicam categorias que se conectam com diversas outras, enquanto conexões isoladas revelam associações exclusivas
    
    Esta visualização é especialmente eficaz para identificar rotas majoritárias entre características sociais e entender como diferentes grupos demográficos se interconectam.
    
    **🔍 Aprofundamento:** Para análises estatísticas detalhadas sobre essa relação, incluindo coeficientes de associação e padrões significativos, expanda a seção "Ver análise estatística detalhada" abaixo do gráfico.
    """


def get_explicacao_distribuicao(
    aspecto_nome: str, 
    total: Optional[int] = None, 
    categoria_mais_frequente: Optional[Any] = None
) -> str:
    """
    Retorna explicação contextualizada para o gráfico de distribuição.
    
    Parâmetros:
    -----------
    aspecto_nome : str
        Nome do aspecto social
    total : int, opcional
        Número total de candidatos
    categoria_mais_frequente : Dict ou Series, opcional
        Informações sobre a categoria mais frequente
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação de parâmetros
    if not aspecto_nome:
        aspecto_nome = "característica selecionada"
    
    # Valores padrão
    total_formatado = f"{total:,}" if total else "N/A"
    categoria_predominante = "N/A"
    percentual_predominante = "N/A"
    
    # Verificar se temos informações sobre a categoria mais frequente
    if categoria_mais_frequente is not None:
        if isinstance(categoria_mais_frequente, pd.Series):
            # Tratar como Series do pandas
            if 'Categoria' in categoria_mais_frequente.index:
                categoria_predominante = categoria_mais_frequente['Categoria']
            if 'Percentual' in categoria_mais_frequente.index:
                try:
                    percentual_predominante = f"{categoria_mais_frequente['Percentual']:.1f}%"
                except (TypeError, ValueError):
                    percentual_predominante = "N/A"
        elif isinstance(categoria_mais_frequente, dict):
            # Tratar como dicionário
            if 'Categoria' in categoria_mais_frequente:
                categoria_predominante = categoria_mais_frequente['Categoria']
            if 'Percentual' in categoria_mais_frequente:
                try:
                    percentual_predominante = f"{categoria_mais_frequente['Percentual']:.1f}%"
                except (TypeError, ValueError):
                    percentual_predominante = "N/A"
    
    return f"""
    **Análise da distribuição de {aspecto_nome}:**
    
    A visualização mostra o perfil demográfico dos candidatos:
    
    - **Representatividade:**
      No total, {total_formatado} candidatos estão distribuídos nas categorias apresentadas
    
    - **Categoria predominante:**
      "{categoria_predominante}" é a categoria mais comum, representando {percentual_predominante} do total
    
    - **Implicações sociais:**
      A distribuição observada reflete padrões demográficos que podem influenciar o desempenho educacional e políticas de inclusão
    
    - **Diversidade e concentração:**
      O grau de dispersão entre as categorias indica quão diversificado ou concentrado é o perfil socioeconômico dos participantes
    
    Esta análise é fundamental para contextualizar os resultados educacionais dentro da realidade socioeconômica dos candidatos e identificar potenciais barreiras à equidade.
    
    **📈 Estatísticas detalhadas:** Expanda a seção "Ver dados detalhados" logo abaixo para acessar métricas completas sobre a distribuição, incluindo análise de concentração, estatísticas de equidade e visualização da tabela completa.
    """

def get_explicacao_aspectos_por_estado(
    aspecto_nome: str, 
    categoria_selecionada: Optional[str] = None,
    tipo_localidade: str = "estado"
) -> str:
    """
    Retorna o texto explicativo para o gráfico de aspectos sociais por estado/região.
    
    Parâmetros:
    -----------
    aspecto_nome : str
        Nome do aspecto social selecionado
    categoria_selecionada : str, opcional
        Nome da categoria específica selecionada para análise
    tipo_localidade : str, default="estado"
        Tipo de localidade (estado ou região)
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação de parâmetros
    if not aspecto_nome:
        aspecto_nome = "característica selecionada"
    
    tipo_localidade = tipo_localidade.lower()
    if tipo_localidade not in ["estado", "região"]:
        tipo_localidade = "estado"
    
    # Texto específico para categoria selecionada
    categoria_texto = ""
    if categoria_selecionada:
        categoria_texto = f"\n\nA análise está focada especificamente na categoria **{categoria_selecionada}**, mostrando como esta se distribui geograficamente."
    
    return f"""
    **Análise da distribuição de {aspecto_nome} por {tipo_localidade}:**

    O gráfico mostra como a distribuição de {aspecto_nome} varia entre os diferentes {tipo_localidade}s do Brasil.{categoria_texto}
    
    Esta visualização permite:
    
    - **Identificar padrões regionais:**
      Observe como certas características sociais se concentram em áreas específicas do país
    
    - **Comparar percentuais entre localidades:**
      Compare diretamente como cada categoria se distribui nas diferentes regiões geográficas
    
    - **Detectar disparidades territoriais:**
      Identifique {tipo_localidade}s com perfis significativamente diferentes da média nacional
    
    - **Analisar padrões geográficos:**
      Observe como fatores históricos, econômicos e sociais podem explicar as diferenças regionais
    
    As diferenças observadas podem refletir aspectos socioeconômicos, culturais, históricos ou políticos característicos de cada {tipo_localidade}, oferecendo insights sobre as desigualdades e particularidades regionais do Brasil.
    
    **💡 Análise detalhada:** Para métricas de variabilidade regional, coeficientes de dispersão e identificação de localidades com valores extremos, expanda a seção "Ver análise regional detalhada" abaixo.
    """


def get_interpretacao_associacao(
    coeficiente: float, 
    var_x_nome: str, 
    var_y_nome: str
) -> str:
    """
    Gera uma interpretação contextualizada da associação entre variáveis categóricas.
    
    Parâmetros:
    -----------
    coeficiente : float
        Coeficiente de associação (V de Cramer ou similar)
    var_x_nome : str
        Nome da primeira variável
    var_y_nome : str
        Nome da segunda variável
        
    Retorna:
    --------
    str: Texto interpretativo da associação
    """
    # Validação de parâmetros
    if not var_x_nome or not var_y_nome:
        var_x_nome = "primeira característica" if not var_x_nome else var_x_nome
        var_y_nome = "segunda característica" if not var_y_nome else var_y_nome
    
    try:
        coef_valor = float(coeficiente)
    except (ValueError, TypeError):
        coef_valor = 0.0
    
    if coef_valor > LIMITE_CORRELACAO_FORTE:
        return f"""
        Existe uma **forte associação** entre {var_x_nome} e {var_y_nome}, indicando que estas características sociais estão intimamente relacionadas.
        
        Esta forte associação sugere que:
        - Existe uma sobreposição significativa entre estas dimensões sociais
        - Conhecer uma característica permite prever a outra com considerável precisão
        - Há provável influência de fatores estruturais comuns afetando ambas as características
        - Políticas que visam uma dessas dimensões provavelmente impactarão a outra
        
        Em termos sociais, esta forte interdependência revela um aspecto importante da estrutura socioeconômica e demográfica da população estudada.
        """
    elif coef_valor > LIMITE_CORRELACAO_MODERADA:
        return f"""
        Há uma **associação moderada** entre {var_x_nome} e {var_y_nome}, demonstrando uma conexão significativa, porém não determinística.
        
        Esta associação moderada indica que:
        - Existe uma relação consistente, mas com exceções importantes
        - Há tendências claras de certos grupos se associarem mais frequentemente
        - As características compartilham alguns fatores causais, mas mantêm aspectos independentes
        - Intervenções em uma área podem ter efeitos parciais na outra
        
        Este nível de associação sugere interseções importantes entre estas dimensões sociais, revelando padrões relevantes para análises demográficas e educacionais.
        """
    elif coef_valor > LIMITE_CORRELACAO_FRACA:
        return f"""
        Existe uma **associação fraca** entre {var_x_nome} e {var_y_nome}, mostrando alguma relação, porém com substancial independência.
        
        Esta associação fraca sugere que:
        - As características têm alguma sobreposição, mas são majoritariamente independentes
        - Há tendências sutis, mas com muitas exceções e variações
        - Fatores externos diferentes influenciam cada característica
        - Intervenções específicas provavelmente serão necessárias para cada dimensão
        
        Este nível de associação indica que, embora exista alguma conexão, estas características sociais operam de forma relativamente autônoma no contexto estudado.
        """
    else:
        return f"""
        Há uma **associação mínima ou inexistente** entre {var_x_nome} e {var_y_nome}, indicando que estas características são essencialmente independentes.
        
        Esta ausência de associação significativa indica que:
        - As características não se influenciam mutuamente de forma relevante
        - Conhecer uma característica não ajuda a prever a outra
        - Diferentes fatores sociais e contextuais determinam cada dimensão
        - Políticas e intervenções precisam abordar cada área separadamente
        
        A independência entre estas dimensões sociais sugere uma diversidade de perfis na população estudada, sem padrões significativos de agrupamento.
        """


def get_interpretacao_variabilidade_regional(
    coef_variacao: float, 
    aspecto_nome: str, 
    categoria: Optional[str] = None
) -> str:
    """
    Gera uma interpretação da variabilidade regional de um aspecto social.
    
    Parâmetros:
    -----------
    coef_variacao : float
        Coeficiente de variação (%) da distribuição entre estados/regiões
    aspecto_nome : str
        Nome do aspecto social
    categoria : str, opcional
        Categoria específica, se aplicável
        
    Retorna:
    --------
    str: Texto interpretativo da variabilidade regional
    """
    # Validação de parâmetros
    if not aspecto_nome:
        aspecto_nome = "característica analisada"
    
    # Texto específico para categoria
    categoria_texto = f" na categoria {categoria}" if categoria else ""
    
    try:
        cv = float(coef_variacao)
    except (ValueError, TypeError):
        cv = 0.0
    
    # Limiares de variabilidade obtidos dos mapeamentos
    limite_baixo = LIMIARES_ESTATISTICOS.get('variabilidade_baixa', 15)
    limite_moderado = LIMIARES_ESTATISTICOS.get('variabilidade_moderada', 30)
    
    if cv < limite_baixo:
        return f"""
        A distribuição de {aspecto_nome}{categoria_texto} apresenta **baixa variabilidade regional** (CV={cv:.1f}%), indicando uma distribuição relativamente homogênea pelo território nacional.
        
        Esta homogeneidade sugere que:
        - O aspecto analisado se distribui de forma similar nas diferentes regiões
        - Fatores geográficos têm pouca influência nesta característica social
        - Há consistência nas condições socioeconômicas relacionadas a este aspecto
        - Políticas nacionais podem ser mais efetivas que abordagens regionais específicas
        
        A baixa variabilidade indica que este aspecto transcende barreiras geográficas, mantendo padrões consistentes em diferentes contextos regionais.
        """
    elif cv < limite_moderado:
        return f"""
        A distribuição de {aspecto_nome}{categoria_texto} apresenta **variabilidade regional moderada** (CV={cv:.1f}%), indicando diferenças significativas entre localidades.
        
        Esta variabilidade moderada sugere que:
        - Existem padrões regionais relevantes, mas não extremos
        - Fatores geográficos e contextuais influenciam esta característica
        - Há diferenças regionais que merecem atenção específica
        - Políticas adaptadas a contextos regionais podem ser mais efetivas
        
        Este nível de variação indica a necessidade de considerar fatores regionais na análise deste aspecto social, reconhecendo diferenças contextuais importantes.
        """
    else:
        return f"""
        A distribuição de {aspecto_nome}{categoria_texto} apresenta **alta variabilidade regional** (CV={cv:.1f}%), revelando disparidades territoriais substanciais.
        
        Esta alta heterogeneidade indica que:
        - Existem contrastes marcantes entre diferentes regiões do país
        - Fatores geográficos, históricos e socioeconômicos têm forte influência
        - Há contextos regionais específicos que criam realidades muito distintas
        - Políticas nacionais uniformes podem ser inadequadas, exigindo abordagens regionalizadas
        
        A acentuada variabilidade sugere a necessidade de análises regionais específicas e intervenções adaptadas às diferentes realidades territoriais do país.
        """


def get_analise_concentracao(indice_concentracao: float, aspecto_nome: str) -> str:
    """
    Gera uma análise do índice de concentração de um aspecto social.
    
    Parâmetros:
    -----------
    indice_concentracao : float
        Índice de concentração (Gini ou similar, entre 0 e 1)
    aspecto_nome : str
        Nome do aspecto social
        
    Retorna:
    --------
    str: Texto analítico sobre a concentração
    """
    # Validação de parâmetros
    if not aspecto_nome:
        aspecto_nome = "característica analisada"
    
    try:
        indice = float(indice_concentracao)
        # Garantir que o índice esteja entre 0 e 1
        indice = max(0, min(indice, 1))
    except (ValueError, TypeError):
        indice = 0.0
    
    if indice < 0.2:
        return f"""
        O {aspecto_nome} apresenta uma **distribuição muito equilibrada** (índice de concentração: {indice:.3f}), com candidatos distribuídos de forma bastante homogênea entre as categorias.
        
        Esta baixa concentração indica:
        - Diversidade significativa no perfil dos participantes
        - Ausência de categorias dominantes que concentrem a maioria dos candidatos
        - Representatividade relativamente equilibrada das diferentes características
        
        Um perfil demográfico tão equilibrado é relevante para análises de equidade e representatividade.
        """
    elif indice < 0.4:
        return f"""
        O {aspecto_nome} apresenta uma **distribuição relativamente equilibrada** (índice de concentração: {indice:.3f}), com moderada variação na representação das categorias.
        
        Este nível de concentração sugere:
        - Algumas categorias têm representação maior, mas sem dominância extrema
        - Há diversidade significativa, com boa representação de múltiplos grupos
        - O perfil geral é moderadamente heterogêneo
        
        Esta distribuição moderadamente equilibrada oferece um contexto diversificado para análises educacionais.
        """
    elif indice < 0.6:
        return f"""
        O {aspecto_nome} apresenta uma **concentração moderada** (índice: {indice:.3f}), com algumas categorias representando porções significativamente maiores que outras.
        
        Esta concentração moderada indica:
        - Existem categorias predominantes, mas não de forma extrema
        - Há desequilíbrios notáveis na representação de diferentes grupos
        - O perfil geral mostra heterogeneidade, mas com tendências de concentração
        
        Este padrão de distribuição merece atenção em análises de representatividade e equidade.
        """
    elif indice < 0.8:
        return f"""
        O {aspecto_nome} apresenta uma **alta concentração** (índice: {indice:.3f}), com distribuição significativamente desigual entre as categorias.
        
        Esta alta concentração revela:
        - Poucas categorias concentram grande parte dos candidatos
        - Existem grupos significativamente sub-representados
        - O perfil geral é bastante homogêneo em termos desta característica
        
        Esta distribuição desigual é um fator importante a considerar em análises de equidade educacional.
        """
    else:
        return f"""
        O {aspecto_nome} apresenta uma **concentração extremamente alta** (índice: {indice:.3f}), com distribuição muito desigual entre as categorias.
        
        Esta concentração extrema indica:
        - Uma ou poucas categorias dominam fortemente a distribuição
        - A maioria das categorias tem representação mínima
        - O perfil é altamente homogêneo para esta característica
        
        Esta distribuição altamente desequilibrada constitui um aspecto crítico para análises de diversidade e equidade.
        """