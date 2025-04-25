def get_tooltip_metricas_principais():
    """Retorna o texto do tooltip para métricas principais"""
    return """
    Esta seção apresenta as principais métricas resumidas dos dados analisados.
    
    - As métricas são calculadas considerando apenas os estados selecionados no filtro lateral
    - Os valores representam o panorama geral do desempenho dos candidatos
    - A média geral considera todas as áreas de conhecimento combinadas
    
    Passe o mouse sobre cada métrica individual para ver detalhes sobre seu cálculo.
    """

def get_tooltip_histograma():
    """Retorna o texto do tooltip para o histograma de notas"""
    return """
    Este gráfico mostra como as notas dos candidatos estão distribuídas em determinada área de conhecimento.
    
    - As barras representam o percentual de candidatos em cada faixa de nota
    - A linha vermelha vertical indica a média das notas
    - A linha verde vertical indica a mediana
    - Os valores estatísticos (min, max, média, mediana, desvio padrão, assimetria e curtose) são mostrados na caixa no canto superior esquerdo

    Um histograma com média maior que a mediana indica mais candidatos com notas acima da média. Explore a seção "Ver análise estatística detalhada" abaixo do gráfico para compreender melhor a distribuição.
    """

def get_tooltip_faltas():
    """Retorna o texto do tooltip para o gráfico de faltas"""
    return """
    Este gráfico mostra o percentual de candidatos que faltaram em cada dia do ENEM por estado.

    - A linha "Faltou nos dois dias" representa candidatos que não compareceram a nenhum dia de prova
    - A linha "Faltou apenas no primeiro dia" mostra candidatos que estiveram presentes apenas no segundo dia
    - A linha "Faltou apenas no segundo dia" mostra candidatos que estiveram presentes apenas no primeiro dia
    
    O ENEM é realizado em dois dias, com as seguintes provas:
    - 1º dia: Linguagens e Códigos + Ciências Humanas + Redação
    - 2º dia: Ciências da Natureza + Matemática
    
    Para análise detalhada dos padrões de ausência, consulte a seção expandida abaixo do gráfico.
    """

def get_tooltip_media_geral():
    """Retorna o texto do tooltip para média geral"""
    return """
    A Média Geral é calculada em duas etapas:
    
    1. Para cada estado selecionado, calcula-se a média de cada área de conhecimento 
       (Linguagens, Matemática, Ciências Humanas, Ciências da Natureza e Redação)
    
    2. A média geral é a média aritmética de todas essas médias parciais
    
    Este valor representa o desempenho médio dos candidatos considerando todas as competências e estados selecionados.
    """

def get_tooltip_total_candidatos():
    """Retorna o texto do tooltip para total de candidatos"""
    return """
    Número total de candidatos nos estados selecionados que realizaram a prova do ENEM 2023.
    
    - Foi coletada uma amostra com distribuição proporcional com 200.000 candidatos para este dashboard com foco no desempenho da plataforma
    - O total de candidatos original é de aproximadamente 3.933.955
    - Este valor considera apenas os registros válidos após aplicação dos filtros e modelagem/exclusão de dados inconsistentes
    """

def get_tooltip_maior_media():
    """Retorna o texto do tooltip para maior média"""
    return """
    A Maior Média representa o valor máximo encontrado entre todas as médias calculadas para cada combinação de estado e área de conhecimento.
    
    Este valor indica o melhor desempenho médio observado em qualquer área ou estado dentro da seleção atual.
    """

def get_tooltip_menor_media():
    """Retorna o texto de tooltip para a métrica de menor média."""
    return """
    Esta métrica mostra a menor média do ENEM entre os estados selecionados, considerando todas as provas.
    
    O valor é calculado a partir das médias de cada estado nas quatro áreas de conhecimento e na redação.
    
    Uma menor média não significa necessariamente um pior desempenho educacional, pois vários fatores 
    socioeconômicos e regionais influenciam este resultado.
    """


def get_tooltip_estado_maior_media():
    """Retorna o texto do tooltip para estado com maior média"""
    return """
    Estado que apresenta a maior média geral entre todos os estados selecionados.
    
    Para cada estado, calcula-se a média de todas as áreas de conhecimento, e então identifica-se o estado com o maior valor.
    
    Este dado é útil para identificar regiões com desempenho educacional destacado.
    """


def get_explicacao_histograma(nome_area, media, mediana, assimetria, curtose):
    """
    Retorna a explicação para o histograma de notas.
    
    Parâmetros:
    -----------
    nome_area : str
        Nome da área de conhecimento
    media : float
        Média das notas
    mediana : float
        Mediana das notas
    assimetria : float
        Coeficiente de assimetria
    curtose : float
        Coeficiente de curtose
    """
    # Análise do formato da distribuição
    if media > mediana:
        formato = "assimetria positiva (cauda direita mais longa)"
        interpretacao = "existem mais candidatos com notas baixas, enquanto um número menor de candidatos alcança notas mais altas"
    elif media < mediana:
        formato = "assimetria negativa (cauda esquerda mais longa)"
        interpretacao = "a maioria dos candidatos consegue notas razoavelmente altas, enquanto poucos têm desempenho muito baixo"
    else:
        formato = "distribuição aproximadamente simétrica"
        interpretacao = "as notas estão distribuídas de forma relativamente uniforme em torno da média"
    
    # Análise da curtose
    if curtose < -0.5:
        pico = "distribuição platicúrtica (achatada)"
        significado_pico = "com menor concentração de notas ao redor da média e caudas mais espessas"
    elif curtose > 0.5:
        pico = "distribuição leptocúrtica (pontiaguda)"
        significado_pico = "com maior concentração de notas próximas à média"
    else:
        pico = "distribuição mesocúrtica (próxima da normal)"
        significado_pico = "com distribuição de notas semelhante à curva normal"
    
    return f"""
    **Análise da distribuição de notas em {nome_area}:**
    
    A visualização mostra uma {formato}, {interpretacao}:
    
    - Medidas de tendência central:
    Média de {media:.2f} e mediana de {mediana:.2f}
    
    - Forma da distribuição:
    Apresenta {pico}, {significado_pico}
    
    - Implicações educacionais:
    O padrão de distribuição sugere {get_implicacao_educacional(media, mediana, assimetria)}
    
    Esta análise é essencial para entender como o desempenho dos candidatos se distribui e identificar padrões que possam orientar políticas educacionais.
    
    **📊 Análise aprofundada:** Expanda a seção "Ver análise estatística detalhada" abaixo para acessar métricas completas sobre a distribuição, análise percentílica e correlações com outros indicadores.
    """

def get_implicacao_educacional(media, mediana, assimetria):
    """
    Retorna uma interpretação educacional com base nas estatísticas.
    """
    if assimetria > 0.5:
        return "que a maioria dos candidatos encontra desafios significativos nesta área, com poucos conseguindo alcançar excelência, indicando possível necessidade de reforço no ensino básico deste conteúdo"
    elif assimetria < -0.5:
        return "que o ensino desta área tem sido efetivo para a maioria dos candidatos, com poucos apresentando grande dificuldade, possivelmente refletindo boas práticas pedagógicas que poderiam ser replicadas em outras áreas"
    else:
        return "relativa homogeneidade no aprendizado, com a maioria dos candidatos demonstrando nível semelhante de domínio do conteúdo"

def get_explicacao_faltas(taxa_geral, tipo_mais_comum, estado_maior_falta, estado_menor_falta):
    """
    Retorna a explicação para o gráfico de faltas.
    
    Parâmetros:
    -----------
    taxa_geral : float
        Taxa média de faltas geral
    tipo_mais_comum : str
        Tipo de falta mais comum
    estado_maior_falta : str
        Estado com maior taxa de faltas
    estado_menor_falta : str
        Estado com menor taxa de faltas
    """
    return f"""
    **Análise do padrão de ausências no ENEM:**
    
    Em média, {taxa_geral:.1f}% dos candidatos faltaram em pelo menos um dos dias de prova:
    
    - O padrão mais comum de ausência foi: {tipo_mais_comum}
    - {estado_maior_falta} apresenta a maior taxa de candidatos que faltaram nos dois dias
    - {estado_menor_falta} registra a menor taxa de candidatos que faltaram nos dois dias
    
    A análise por dia de falta permite insights importantes sobre o comportamento dos candidatos. Faltas no segundo dia podem indicar desistência após a experiência do primeiro dia, enquanto faltas apenas no primeiro dia podem estar relacionadas a questões logísticas ou estratégia de foco em determinadas provas.
    
    **🔍 Análise detalhada:** Para explorar estatísticas completas sobre as ausências, expanda a seção "Ver análise detalhada de ausências" abaixo do gráfico.
    """