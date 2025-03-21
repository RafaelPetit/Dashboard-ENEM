def get_tooltip_correlacao_aspectos():
    """Retorna o texto do tooltip para correlação de aspectos sociais"""
    return """
    Sobre esta visualização:<br>
    Explore relações entre diferentes características sociais dos candidatos.
    
    Como usar:<br>
    - Selecione dois aspectos sociais diferentes para comparar
    - Escolha entre Heatmap, Barras Empilhadas ou Sankey
    - Passe o mouse sobre os elementos para ver detalhes
    - Consulte a "Análise estatística detalhada" para métricas avançadas
    
    Cada visualização oferece uma perspectiva única sobre como as características se correlacionam.
    """

def get_tooltip_distribuicao_aspectos():
    """Retorna o texto do tooltip para distribuição de aspectos sociais"""
    return """
    Sobre esta visualização:<br>
    Analise a distribuição de candidatos por diferentes categorias sociais.
    
    Como usar:<br>
    - Selecione o aspecto social de interesse
    - Escolha entre gráficos de Barras, Linha ou Pizza
    - Veja "Dados detalhados" no expander abaixo do gráfico
    - Analise estatísticas de concentração e equidade na distribuição
    
    Identifique rapidamente perfis predominantes e grupos minoritários.
    """

def get_tooltip_aspectos_por_estado():
    """Retorna o texto do tooltip para aspectos sociais por estado"""
    return """
    Sobre esta visualização:<br>
    Compare como as características sociais variam entre estados.
    
    Como usar:<br>
    - Selecione o aspecto social para análise geográfica
    - Ative a ordenação para ver rankings estaduais
    - Selecione uma categoria específica para análise aprofundada
    - Explore a "Análise regional detalhada" para padrões geográficos
    
    Ideal para identificar disparidades regionais em características sociais.
    """

def get_explicacao_heatmap(var_x_nome, var_y_nome):
    """Retorna explicação para o gráfico de heatmap"""
    return f"""
    **Análise da correlação entre {var_x_nome} e {var_y_nome}:**
    
    O heatmap revela padrões importantes na distribuição demográfica:
    
    - Intensidade das cores:
    Cores mais escuras indicam maior concentração percentual de candidatos nessa combinação de características
    
    - Padrões de distribuição:
    Observe como certos valores de {var_x_nome} se associam a categorias específicas de {var_y_nome}
    
    - Distribuição horizontal:
    Cada linha mostra como os candidatos de uma categoria específica de {var_x_nome} se distribuem entre as categorias de {var_y_nome}
    
    Esta visualização é particularmente útil para identificar associações entre características sociais e detectar grupos com perfis demográficos distintos.
    
    **📊 Análise estatística:** Expanda a seção "Ver análise estatística detalhada" logo abaixo para acessar métricas de associação, testes de significância e análise aprofundada das relações entre categorias.
    """

def get_explicacao_barras_empilhadas(var_x_nome, var_y_nome):
    """Retorna explicação para o gráfico de barras empilhadas"""
    return f"""
    **Análise da distribuição de {var_y_nome} por {var_x_nome}:**
    
    O gráfico de barras empilhadas evidencia:
    
    - Composição demográfica:
    Cada barra mostra a distribuição percentual de {var_y_nome} dentro de uma categoria de {var_x_nome}
    
    - Comparação entre grupos:
    Compare visualmente como a distribuição de {var_y_nome} varia entre diferentes categorias de {var_x_nome}
    
    - Proporções relativas:
    Identifique quais combinações de características são mais ou menos comuns na população estudada
    
    Esta visualização facilita a comparação proporcional entre diferentes grupos demográficos, permitindo identificar desequilíbrios na representação.
    
    **📊 Estatísticas avançadas:** Clique em "Ver análise estatística detalhada" abaixo para explorar métricas de associação, identificar padrões significativos e acessar a tabela de contingência completa entre as categorias.
    """

def get_explicacao_sankey(var_x_nome, var_y_nome):
    """Retorna explicação para o diagrama de Sankey"""
    return f"""
    **Análise de fluxo entre {var_x_nome} e {var_y_nome}:**
    
    O diagrama de Sankey ilustra como os candidatos fluem entre categorias:
    
    - Largura das conexões:
    Quanto mais larga a conexão, maior o número de candidatos que compartilham essas características
    
    - Rotas predominantes:
    Identifique as combinações mais comuns de {var_x_nome} e {var_y_nome} através das conexões mais espessas
    
    - Padrões de associação:
    Observe como categorias específicas de {var_x_nome} se distribuem entre as diferentes categorias de {var_y_nome}
    
    Esta visualização é especialmente eficaz para identificar rotas majoritárias entre características sociais e entender como diferentes grupos demográficos se interconectam.
    
    **🔍 Aprofundamento:** Para análises estatísticas detalhadas sobre essa relação, incluindo coeficientes de associação e padrões significativos, expanda a seção "Ver análise estatística detalhada" abaixo do gráfico.
    """

def get_explicacao_distribuicao(aspecto_nome, total, categoria_mais_frequente):
    """Retorna explicação para o gráfico de distribuição"""
    return f"""
    **Análise da distribuição de {aspecto_nome}:**
    
    A visualização mostra o perfil demográfico dos candidatos:
    
    - Representatividade:
    No total, {total:,} candidatos estão distribuídos nas categorias apresentadas
    
    - Categoria predominante:
    "{categoria_mais_frequente['Categoria']}" é a categoria mais comum, representando {categoria_mais_frequente['Percentual']:.1f}% do total
    
    - Implicações sociais:
    A distribuição observada reflete padrões demográficos que podem influenciar o desempenho educacional e políticas de inclusão
    
    Esta análise é fundamental para contextualizar os resultados educacionais dentro da realidade socioeconômica dos candidatos.
    
    **📈 Estatísticas detalhadas:** Expanda a seção "Ver dados detalhados" logo abaixo para acessar métricas completas sobre a distribuição, incluindo análise de concentração, estatísticas de equidade e visualização da tabela completa.
    """

def get_explicacao_aspectos_por_estado(aspecto_nome):
    """Retorna explicação para o gráfico de aspectos por estado"""
    return f"""
    **Análise geográfica de {aspecto_nome}:**
    
    A distribuição por estado revela padrões regionais importantes:
    
    - Variações geográficas:
    Observe como a composição demográfica varia entre diferentes regiões do país
    
    - Disparidades regionais:
    Identifique estados com distribuições atípicas que podem indicar contextos sociais distintos
    
    - Concentrações específicas:
    Note onde certas categorias apresentam percentuais significativamente maiores ou menores que a média nacional
    
    Esta análise espacial contribui para entender como fatores regionais podem influenciar características sociodemográficas dos candidatos, oferecendo insights para políticas educacionais contextualizadas.
    
    **🗺️ Análise regional aprofundada:** Para explorar estatísticas detalhadas por região, rankings completos e padrões de distribuição geográfica, selecione uma categoria específica e clique em "Ver análise regional detalhada" abaixo do gráfico.
    """