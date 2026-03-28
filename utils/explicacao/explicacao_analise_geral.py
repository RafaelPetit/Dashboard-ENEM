from typing import Optional, Tuple
from utils.helpers.constants import LIMIARES_ESTATISTICOS, CONFIG_VISUALIZACAO

def get_tooltip_metricas_principais() -> str:
    """
    Retorna o texto do tooltip para o painel de métricas principais.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre estas métricas:</b><br>
    Esta seção apresenta as principais métricas resumidas dos dados analisados.
    
    <b>Como interpretar:</b><br>
    - As métricas são calculadas considerando apenas os estados selecionados no filtro lateral
    - Os valores representam o panorama geral do desempenho dos candidatos
    - A média geral considera todas as áreas de conhecimento combinadas
    
    Passe o mouse sobre cada métrica individual para ver detalhes sobre seu cálculo.
    """


def get_tooltip_histograma() -> str:
    """
    Retorna o texto do tooltip para o histograma de notas.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Este gráfico mostra como as notas dos candidatos estão distribuídas em determinada área de conhecimento.
    
    <b>Como interpretar:</b><br>
    - As barras representam o percentual de candidatos em cada faixa de nota
    - A linha vermelha vertical indica a média das notas
    - A linha verde vertical indica a mediana
    - A caixa no canto superior esquerdo mostra estatísticas detalhadas
    
    <b>O que observar:</b><br>
    - Quando a média é maior que a mediana: distribuição com cauda à direita (mais candidatos com notas baixas)
    - Quando a média é menor que a mediana: distribuição com cauda à esquerda (mais candidatos com notas altas)
    - Largura da distribuição: indica a variabilidade das notas

    Veja a análise expandida abaixo do gráfico para interpretações detalhadas da distribuição.
    """


def get_tooltip_faltas() -> str:
    """
    Retorna o texto do tooltip para o gráfico de faltas.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Este gráfico mostra o percentual de candidatos que faltaram em cada dia do ENEM por estado.

    <b>Como interpretar:</b><br>
    - <span style="color:#1f77b4">Faltou nos dois dias:</span> candidatos que não compareceram a nenhum dia de prova
    - <span style="color:#ff7f0e">Faltou somente no primeiro dia:</span> candidatos presentes apenas no segundo dia
    - <span style="color:#2ca02c">Faltou somente no segundo dia:</span> candidatos presentes apenas no primeiro dia
    
    <b>Contexto importante:</b><br>
    O ENEM é realizado em dois dias, com as seguintes provas:
    - 1º dia: Linguagens e Códigos + Ciências Humanas + Redação
    - 2º dia: Ciências da Natureza + Matemática
    
    Para análise detalhada dos padrões de ausência, consulte a seção expandida abaixo do gráfico.
    """


def get_tooltip_media_geral() -> str:
    """
    Retorna o texto do tooltip para a métrica de média geral.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Como é calculada:</b><br>
    A Média Geral é calculada em duas etapas:
    
    1. Para cada estado selecionado, calcula-se a média de cada área de conhecimento 
       (Linguagens, Matemática, Ciências Humanas, Ciências da Natureza e Redação)
    
    2. A média geral é a média aritmética de todas essas médias parciais
    
    <b>O que representa:</b><br>
    Este valor indica o desempenho médio dos candidatos considerando todas as competências e estados selecionados.
    """


def get_tooltip_total_candidatos() -> str:
    """
    Retorna o texto do tooltip para a métrica de total de candidatos.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>O que representa:</b><br>
    Número total de candidatos nos estados selecionados que realizaram a prova do ENEM no ano analisado.
    
    <b>Observações importantes:</b><br>
    - Foi coletada uma amostra com distribuição proporcional por estado para este dashboard
    - O valor considera apenas registros válidos após filtragem e modelagem de dados
    - Candidatos que não compareceram a nenhum dia de prova (código 0 de presença) são contabilizados neste total
    """


def get_tooltip_maior_media() -> str:
    """
    Retorna o texto do tooltip para a métrica de maior média.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Como é calculada:</b><br>
    A Maior Média representa o valor máximo encontrado entre todas as médias calculadas para cada combinação de estado e área de conhecimento.
    
    <b>O que representa:</b><br>
    Este valor indica o melhor desempenho médio observado em qualquer área ou estado dentro da seleção atual.
    
    <b>Interpretação:</b><br>
    Uma maior média em determinada área pode indicar:
    - Maior facilidade dos candidatos naquela competência
    - Questões com nível de dificuldade menor
    - Melhor preparação dos estudantes para aquele conteúdo
    """


def get_tooltip_menor_media() -> str:
    """
    Retorna o texto do tooltip para a métrica de menor média.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Como é calculada:</b><br>
    A Menor Média representa o valor mínimo encontrado entre todas as médias calculadas para cada combinação de estado e área de conhecimento.
    
    <b>O que representa:</b><br>
    Este valor indica o desempenho médio mais baixo observado em qualquer área ou estado dentro da seleção atual.
    
    <b>Interpretação:</b><br>
    Uma menor média em determinada área pode indicar:
    - Maior dificuldade dos candidatos naquela competência
    - Questões com nível de dificuldade maior
    - Necessidade de reforço no ensino daquele conteúdo
    """


def get_tooltip_estado_maior_media() -> str:
    """
    Retorna o texto do tooltip para a métrica de estado com maior média.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Como é identificado:</b><br>
    Para cada estado, calcula-se a média de todas as áreas de conhecimento, e então identifica-se o estado com o maior valor médio.
    
    <b>O que representa:</b><br>
    Estado que apresenta a maior média geral entre todos os estados selecionados no filtro atual.
    
    <b>Interpretação contextual:</b><br>
    Diferenças entre estados podem refletir diversos fatores:
    - Qualidade da educação básica regional
    - Fatores socioeconômicos
    - Acesso a recursos educacionais
    - Políticas educacionais locais
    """


def get_tooltip_media_por_regiao() -> str:
    """
    Retorna o texto do tooltip para o gráfico de médias por região.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Este gráfico mostra as médias de desempenho por região do Brasil, permitindo comparação regional.
    
    <b>Como interpretar:</b><br>
    - Cada barra representa a média geral de uma região
    - Cores destacadas indicam as regiões com maior (verde) e menor (laranja) média
    - A altura da barra é proporcional ao valor da média
    
    <b>O que observar:</b><br>
    - Disparidades regionais no desempenho educacional
    - Padrões geográficos que podem indicar necessidade de políticas específicas
    - Regiões que podem servir como referência de boas práticas educacionais
    
    Para uma análise estadual mais detalhada, desative a opção "Agrupar por região" nos controles.
    """


def get_tooltip_comparativo_areas() -> str:
    """
    Retorna o texto do tooltip para o gráfico comparativo entre áreas.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Este gráfico compara o desempenho médio dos candidatos entre as diferentes áreas de conhecimento.
    
    <b>Como interpretar:</b><br>
    - Cada barra/ponto representa uma área de conhecimento do ENEM
    - A altura indica a nota média dos candidatos naquela área
    - As barras de erro (quando visíveis) mostram o desvio padrão, indicando a variabilidade das notas
    
    <b>Tipos de visualização:</b><br>
    - Barras: Comparação direta entre áreas
    - Radar: Análise multidimensional do desempenho
    - Linha: Tendência entre áreas (útil quando há ordenação lógica)
    
    <b>O que observar:</b><br>
    - Áreas com melhor e pior desempenho médio
    - Diferenças na variabilidade das notas (dispersão)
    - Padrões que podem indicar pontos fortes e fracos no sistema educacional
    """


def get_tooltip_evasao() -> str:
    """
    Retorna o texto do tooltip para o gráfico de evasão.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    <b>Sobre esta visualização:</b><br>
    Este gráfico analisa os padrões de presença e ausência dos candidatos por estado.
    
    <b>Como interpretar:</b><br>
    - "Presentes": candidatos que compareceram aos dois dias de prova
    - "Faltantes Dia 1": candidatos que faltaram apenas no primeiro dia
    - "Faltantes Dia 2": candidatos que faltaram apenas no segundo dia
    - "Faltantes Ambos": candidatos que não compareceram a nenhum dia
    
    <b>Tipos de visualização:</b><br>
    - Barras: Comparação direta entre estados
    - Mapa de Calor: Visualização da intensidade de evasão por região
    - Pizza: Distribuição geral por tipo de presença/ausência
    
    <b>O que observar:</b><br>
    - Estados com maior taxa de evasão total
    - Padrões diferentes entre ausência no primeiro e segundo dia
    - Relações entre localização geográfica e taxas de evasão
    """


def get_explicacao_histograma(
    nome_area: str, 
    media: float, 
    mediana: float, 
    assimetria: float, 
    curtose: float
) -> str:
    """
    Retorna a explicação contextualizada para o histograma de notas.
    
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
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação e tratamento de parâmetros
    nome_area = nome_area if nome_area else "área selecionada"
    
    try:
        media = float(media)
        mediana = float(mediana)
        assimetria = float(assimetria)
        curtose = float(curtose)
    except (ValueError, TypeError):
        media = 0.0
        mediana = 0.0
        assimetria = 0.0
        curtose = 0.0
    
    # Análise do formato da distribuição
    formato, interpretacao = _analisar_formato_distribuicao(media, mediana, assimetria)
    
    # Análise da curtose
    pico, significado_pico = _analisar_curtose(curtose)
    
    # Obter implicação educacional
    implicacao = _get_implicacao_educacional(media, mediana, assimetria)
    
    return f"""
    **Análise da distribuição de notas em {nome_area}:**
    
    A visualização mostra uma {formato}, {interpretacao}:
    
    - **Medidas de tendência central:**
      Média de {media:.2f} e mediana de {mediana:.2f}
    
    - **Forma da distribuição:**
      Apresenta {pico}, {significado_pico}
    
    - **Implicações educacionais:**
      O padrão de distribuição sugere {implicacao}
    
    Esta análise é essencial para entender como o desempenho dos candidatos se distribui e identificar padrões que possam orientar políticas educacionais.
    
    **📊 Análise aprofundada:** Expanda a seção "Ver análise estatística detalhada" abaixo para acessar métricas completas sobre a distribuição, análise percentílica e correlações com outros indicadores.
    """


def get_explicacao_faltas(
    taxa_geral: float, 
    tipo_mais_comum: str, 
    estado_maior_falta: Optional[str] = None, 
    estado_menor_falta: Optional[str] = None
) -> str:
    """
    Retorna a explicação contextualizada para o gráfico de faltas.
    
    Parâmetros:
    -----------
    taxa_geral : float
        Taxa média de faltas geral (%)
    tipo_mais_comum : str
        Tipo de falta mais comum
    estado_maior_falta : str, opcional
        Estado com maior taxa de faltas
    estado_menor_falta : str, opcional
        Estado com menor taxa de faltas
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação e tratamento de parâmetros
    try:
        taxa_geral = float(taxa_geral)
    except (ValueError, TypeError):
        taxa_geral = 0.0
        
    tipo_mais_comum = tipo_mais_comum if tipo_mais_comum else "Não identificado"
    estado_maior_falta = estado_maior_falta if estado_maior_falta else "Não identificado"
    estado_menor_falta = estado_menor_falta if estado_menor_falta else "Não identificado"
    
    # Construir análise de estados apenas se tivermos dados válidos
    analise_estados = ""
    if estado_maior_falta != "Não identificado" and estado_menor_falta != "Não identificado":
        analise_estados = f"""
    - **{estado_maior_falta}** apresenta a maior taxa de candidatos que faltaram nos dois dias
    - **{estado_menor_falta}** registra a menor taxa de candidatos que faltaram nos dois dias"""
    
    return f"""
    **Análise do padrão de ausências no ENEM:**
    
    Em média, **{taxa_geral:.1f}%** dos candidatos faltaram em pelo menos um dos dias de prova:
    
    - O padrão mais comum de ausência foi: **{tipo_mais_comum}**{analise_estados}
    
    A análise por dia de falta permite insights importantes sobre o comportamento dos candidatos:
    
    - **Faltas no segundo dia:** Podem indicar desistência após a experiência do primeiro dia, questões relacionadas à dificuldade percebida, ou priorização estratégica de provas específicas
    
    - **Faltas no primeiro dia:** Geralmente associadas a questões logísticas, imprevistos, ou estratégia de foco em determinadas áreas do conhecimento
    
    - **Faltas em ambos os dias:** Representam desistência completa, que pode estar relacionada a fatores socioeconômicos, distância geográfica ou outras barreiras de acesso
    
    **🔍 Análise detalhada:** Para explorar estatísticas completas sobre as ausências, expanda a seção "Ver análise detalhada de ausências" abaixo do gráfico.
    """


def get_explicacao_media_estados(
    media_geral: float,
    maior_estado: str,
    maior_valor: float,
    menor_estado: str,
    menor_valor: float,
    diferenca_percentual: float,
    por_regiao: bool = False
) -> str:
    """
    Retorna a explicação contextualizada para o gráfico de médias por estado/região.
    
    Parâmetros:
    -----------
    media_geral : float
        Média geral de todos os estados/regiões
    maior_estado : str
        Estado/região com maior média
    maior_valor : float
        Valor da maior média
    menor_estado : str
        Estado/região com menor média
    menor_valor : float
        Valor da menor média
    diferenca_percentual : float
        Diferença percentual entre maior e menor média
    por_regiao : bool, default=False
        Indica se o gráfico está agrupado por região
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação e tratamento de parâmetros
    try:
        media_geral = float(media_geral)
        maior_valor = float(maior_valor)
        menor_valor = float(menor_valor)
        diferenca_percentual = float(diferenca_percentual)
    except (ValueError, TypeError):
        media_geral = 0.0
        maior_valor = 0.0
        menor_valor = 0.0
        diferenca_percentual = 0.0
        
    maior_estado = maior_estado if maior_estado else "Não identificado"
    menor_estado = menor_estado if menor_estado else "Não identificado"
    
    # Determinar tipo de localidade
    tipo_localidade = "região" if por_regiao else "estado"
    
    # Classificar a magnitude da diferença
    classificacao = _classificar_diferenca_percentual(diferenca_percentual)
    
    return f"""
    **Análise da distribuição de desempenho por {tipo_localidade}:**
    
    A visualização revela uma **{classificacao} variação** no desempenho médio entre {tipo_localidade}s do Brasil:
    
    - **Média geral nacional:** {media_geral:.1f} pontos
    
    - **{maior_estado}:** Apresenta o melhor desempenho com média de {maior_valor:.1f} pontos
    
    - **{menor_estado}:** Registra a menor média com {menor_valor:.1f} pontos
    
    - **Diferença percentual:** {diferenca_percentual:.1f}% entre o melhor e o pior desempenho
    
    Estas disparidades geográficas são multifatoriais e podem refletir:
    
    - **Fatores socioeconômicos:** Níveis de renda, acesso a recursos educacionais e infraestrutura
    - **Qualidade do ensino:** Formação docente, metodologias e recursos pedagógicos
    - **Políticas educacionais:** Investimentos públicos, programas de apoio e capacitação
    - **Aspectos culturais:** Valorização da educação e perspectivas de futuro
    
    **🔎 Interpretação contextualizada:** Para uma análise mais detalhada, incluindo comparações entre áreas de conhecimento específicas por {tipo_localidade}, expanda a seção "Ver análise detalhada por {tipo_localidade}" abaixo.
    """


def get_explicacao_comparativo_areas(
    melhor_area: str,
    melhor_media: float,
    pior_area: str,
    pior_media: float,
    maior_variabilidade: str,
    menor_variabilidade: str
) -> str:
    """
    Retorna a explicação contextualizada para o gráfico comparativo entre áreas.
    
    Parâmetros:
    -----------
    melhor_area : str
        Área com maior média
    melhor_media : float
        Valor da maior média
    pior_area : str
        Área com menor média
    pior_media : float
        Valor da menor média
    maior_variabilidade : str
        Área com maior variabilidade (desvio padrão)
    menor_variabilidade : str
        Área com menor variabilidade (desvio padrão)
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação e tratamento de parâmetros
    try:
        melhor_media = float(melhor_media)
        pior_media = float(pior_media)
    except (ValueError, TypeError):
        melhor_media = 0.0
        pior_media = 0.0
        
    melhor_area = melhor_area if melhor_area else "Não identificada"
    pior_area = pior_area if pior_area else "Não identificada"
    maior_variabilidade = maior_variabilidade if maior_variabilidade else "Não identificada"
    menor_variabilidade = menor_variabilidade if menor_variabilidade else "Não identificada"
    
    # Calcular diferença percentual
    if pior_media > 0:
        diferenca_percentual = ((melhor_media - pior_media) / pior_media) * 100
    else:
        diferenca_percentual = 0.0
    
    return f"""
    **Análise comparativa entre áreas de conhecimento:**
    
    O comparativo revela diferenças significativas no desempenho dos candidatos entre as diferentes competências avaliadas:
    
    - **{melhor_area}:** Apresenta o melhor desempenho médio com {melhor_media:.1f} pontos
    
    - **{pior_area}:** Registra o menor desempenho médio com {pior_media:.1f} pontos
    
    - **Diferença percentual:** {diferenca_percentual:.1f}% entre a melhor e a pior área
    
    - **Variabilidade:** {maior_variabilidade} mostra a maior dispersão de notas, enquanto {menor_variabilidade} apresenta notas mais homogêneas
    
    Estas diferenças podem refletir:
    
    - **Qualidade do ensino:** Áreas com menor média podem indicar deficiências no ensino básico
    - **Dificuldade das provas:** Diferentes níveis de complexidade entre as áreas
    - **Preparação dos candidatos:** Foco de estudo em determinadas disciplinas
    - **Natureza do conteúdo:** Algumas áreas podem exigir habilidades mais complexas ou abstratas
    
    **📈 Análise de tendências:** Para uma interpretação mais aprofundada, incluindo correlações entre áreas de conhecimento e fatores socioeconômicos, expanda a seção "Ver análise comparativa detalhada" abaixo.
    """


def get_explicacao_evasao(
    taxa_media_presenca: float,
    taxa_media_ausencia_total: float,
    estado_maior_presenca: str,
    estado_menor_presenca: str,
    diferenca_dia1_dia2: float
) -> str:
    """
    Retorna a explicação contextualizada para o gráfico de evasão.
    
    Parâmetros:
    -----------
    taxa_media_presenca : float
        Taxa média de presença em ambos os dias (%)
    taxa_media_ausencia_total : float
        Taxa média de ausência em ambos os dias (%)
    estado_maior_presenca : str
        Estado com maior taxa de presença
    estado_menor_presenca : str
        Estado com menor taxa de presença
    diferenca_dia1_dia2 : float
        Diferença percentual entre faltas no 1º e 2º dia
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação e tratamento de parâmetros
    try:
        taxa_media_presenca = float(taxa_media_presenca)
        taxa_media_ausencia_total = float(taxa_media_ausencia_total)
        diferenca_dia1_dia2 = float(diferenca_dia1_dia2)
    except (ValueError, TypeError):
        taxa_media_presenca = 0.0
        taxa_media_ausencia_total = 0.0
        diferenca_dia1_dia2 = 0.0
        
    estado_maior_presenca = estado_maior_presenca if estado_maior_presenca else "Não identificado"
    estado_menor_presenca = estado_menor_presenca if estado_menor_presenca else "Não identificado"
    
    # Determinar se há mais faltas no primeiro ou segundo dia
    dia_mais_faltas = "primeiro" if diferenca_dia1_dia2 < 0 else "segundo"
    abs_diferenca = abs(diferenca_dia1_dia2)
    
    return f"""
    **Análise dos padrões de presença e ausência no ENEM:**
    
    Os dados mostram que, em média:
    
    - **{taxa_media_presenca:.1f}%** dos candidatos comparecem a ambos os dias de prova
    - **{taxa_media_ausencia_total:.1f}%** dos candidatos faltam a ambos os dias (inscritos que não realizam nenhuma prova)
    - **{estado_maior_presenca}** apresenta a maior taxa de presença nos dois dias
    - **{estado_menor_presenca}** registra a menor taxa de presença nos dois dias
    
    **Padrão diferencial entre dias:**
    
    Há **{abs_diferenca:.1f}%** mais faltas no {dia_mais_faltas} dia de prova em relação ao outro, o que pode indicar:
    
    - **Faltas no segundo dia:** Frequentemente associadas à percepção de dificuldade após o primeiro dia, cansaço, ou foco estratégico em determinadas áreas
    
    - **Faltas no primeiro dia:** Podem refletir questões logísticas, conflitos de agenda, ou estratégia de priorização de áreas específicas
    
    **Implicações educacionais:**
    
    Estes dados são valiosos para:
    - Planejamento logístico das próximas edições do exame
    - Desenvolvimento de políticas para reduzir a evasão
    - Compreensão de barreiras regionais ao acesso educacional
    - Criação de estratégias de engajamento dos candidatos
    
    **🔄 Análise regional:** Para explorar a relação entre localização geográfica e padrões de evasão, consulte a seção expandida abaixo.
    """


# Funções auxiliares

def _get_implicacao_educacional(media: float, mediana: float, assimetria: float) -> str:
    """
    Retorna uma interpretação educacional com base nas estatísticas.
    
    Parâmetros:
    -----------
    media : float
        Média das notas
    mediana : float
        Mediana das notas
    assimetria : float
        Coeficiente de assimetria
        
    Retorna:
    --------
    str: Texto com a interpretação educacional
    """
    if assimetria > 0.5:
        return "que a maioria dos candidatos encontra desafios significativos nesta área, com poucos conseguindo alcançar excelência, indicando possível necessidade de reforço no ensino básico deste conteúdo"
    elif assimetria < -0.5:
        return "que o ensino desta área tem sido efetivo para a maioria dos candidatos, com poucos apresentando grande dificuldade, possivelmente refletindo boas práticas pedagógicas que poderiam ser replicadas em outras áreas"
    else:
        return "relativa homogeneidade no aprendizado, com a maioria dos candidatos demonstrando nível semelhante de domínio do conteúdo"


def _analisar_formato_distribuicao(
    media: float, 
    mediana: float, 
    assimetria: float
) -> Tuple[str, str]:
    """
    Analisa o formato da distribuição com base na média, mediana e assimetria.
    
    Parâmetros:
    -----------
    media : float
        Média das notas
    mediana : float
        Mediana das notas
    assimetria : float
        Coeficiente de assimetria
        
    Retorna:
    --------
    Tuple[str, str]: Tupla contendo (formato da distribuição, interpretação)
    """
    if assimetria > 0.5 or (media > mediana and abs(media - mediana) > 5):
        formato = "assimetria positiva (cauda direita mais longa)"
        interpretacao = "existem mais candidatos com notas baixas, enquanto um número menor de candidatos alcança notas mais altas"
    elif assimetria < -0.5 or (media < mediana and abs(media - mediana) > 5):
        formato = "assimetria negativa (cauda esquerda mais longa)"
        interpretacao = "a maioria dos candidatos consegue notas razoavelmente altas, enquanto poucos têm desempenho muito baixo"
    else:
        formato = "distribuição aproximadamente simétrica"
        interpretacao = "as notas estão distribuídas de forma relativamente uniforme em torno da média"
        
    return formato, interpretacao


def _analisar_curtose(curtose: float) -> Tuple[str, str]:
    """
    Analisa a curtose da distribuição.
    
    Parâmetros:
    -----------
    curtose : float
        Coeficiente de curtose
        
    Retorna:
    --------
    Tuple[str, str]: Tupla contendo (tipo de distribuição, significado)
    """
    if curtose < -0.5:
        pico = "distribuição platicúrtica (achatada)"
        significado_pico = "com menor concentração de notas ao redor da média e caudas mais espessas"
    elif curtose > 0.5:
        pico = "distribuição leptocúrtica (pontiaguda)"
        significado_pico = "com maior concentração de notas próximas à média"
    else:
        pico = "distribuição mesocúrtica (próxima da normal)"
        significado_pico = "com distribuição de notas semelhante à curva normal"
        
    return pico, significado_pico


def _classificar_diferenca_percentual(diferenca: float) -> str:
    """
    Classifica a magnitude de uma diferença percentual.
    
    Parâmetros:
    -----------
    diferenca : float
        Valor da diferença percentual
        
    Retorna:
    --------
    str: Classificação da diferença
    """
    if diferenca < 5:
        return "pequena"
    elif diferenca < 15:
        return "moderada"
    elif diferenca < 30:
        return "significativa"
    else:
        return "extremamente acentuada"


def get_interpretacao_distribuicao(
    assimetria: float, 
    curtose: float, 
    media: float, 
    desvio_padrao: float
) -> str:
    """
    Retorna uma interpretação estatística detalhada sobre a distribuição.
    
    Parâmetros:
    -----------
    assimetria : float
        Coeficiente de assimetria
    curtose : float
        Coeficiente de curtose
    media : float
        Média das notas
    desvio_padrao : float
        Desvio padrão das notas
        
    Retorna:
    --------
    str: Texto interpretativo formatado em Markdown
    """
    # Validação e tratamento de parâmetros
    try:
        assimetria = float(assimetria)
        curtose = float(curtose)
        media = float(media)
        desvio_padrao = float(desvio_padrao)
    except (ValueError, TypeError):
        assimetria = 0.0
        curtose = 0.0
        media = 0.0
        desvio_padrao = 0.0
    
    # Interpretação da assimetria
    if assimetria > 1.0:
        desc_assimetria = "**forte assimetria positiva**, com uma longa cauda à direita"
        implic_assimetria = "a maioria dos candidatos obtém notas baixas a médias, com poucos alcançando pontuações muito altas"
    elif assimetria > 0.5:
        desc_assimetria = "**assimetria positiva moderada**, com uma cauda estendida à direita"
        implic_assimetria = "há uma concentração de candidatos em notas abaixo da média, com uma proporção menor atingindo notas altas"
    elif assimetria > -0.5:
        desc_assimetria = "**distribuição aproximadamente simétrica**"
        implic_assimetria = "as notas dos candidatos se distribuem de maneira relativamente equilibrada em torno da média"
    elif assimetria > -1.0:
        desc_assimetria = "**assimetria negativa moderada**, com uma cauda estendida à esquerda"
        implic_assimetria = "há uma concentração de candidatos em notas acima da média, com uma proporção menor obtendo notas baixas"
    else:
        desc_assimetria = "**forte assimetria negativa**, com uma longa cauda à esquerda"
        implic_assimetria = "a maioria dos candidatos alcança notas médias a altas, com poucos obtendo pontuações muito baixas"
    
    # Interpretação da curtose
    if curtose > 3.0:
        desc_curtose = "**distribuição extremamente leptocúrtica** (muito pontiaguda)"
        implic_curtose = "há uma concentração muito alta de candidatos com notas próximas da média, com caudas finas (poucos valores extremos)"
    elif curtose > 1.0:
        desc_curtose = "**distribuição leptocúrtica** (pontiaguda)"
        implic_curtose = "há uma concentração considerável de candidatos com notas próximas da média"
    elif curtose > -1.0:
        desc_curtose = "**distribuição mesocúrtica** (similar à normal)"
        implic_curtose = "as notas seguem um padrão de dispersão próximo ao da distribuição normal"
    else:
        desc_curtose = "**distribuição platicúrtica** (achatada)"
        implic_curtose = "há uma dispersão mais uniforme das notas, com menos concentração em torno da média e caudas mais espessas"
    
    # Interpretação do coeficiente de variação
    cv = (desvio_padrao / media * 100) if media > 0 else 0
    if cv < 10:
        desc_variacao = "**muito baixa variabilidade** (CV = {:.1f}%)".format(cv)
        implic_variacao = "há grande homogeneidade nas notas, indicando consistência no desempenho dos candidatos"
    elif cv < 20:
        desc_variacao = "**baixa variabilidade** (CV = {:.1f}%)".format(cv)
        implic_variacao = "as notas apresentam razoável consistência, com dispersão moderada"
    elif cv < 30:
        desc_variacao = "**variabilidade moderada** (CV = {:.1f}%)".format(cv)
        implic_variacao = "existe heterogeneidade considerável nas notas, refletindo diferenças significativas no desempenho"
    else:
        desc_variacao = "**alta variabilidade** (CV = {:.1f}%)".format(cv)
        implic_variacao = "há grande heterogeneidade nas notas, sugerindo disparidades acentuadas no desempenho dos candidatos"
    
    return f"""
    **Análise estatística aprofundada da distribuição:**
    
    A distribuição apresenta {desc_assimetria}, o que significa que {implic_assimetria}.
    
    Quanto à concentração das notas, observa-se uma {desc_curtose}, indicando que {implic_curtose}.
    
    Em termos de dispersão relativa, as notas mostram {desc_variacao}, o que sugere que {implic_variacao}.
    
    **Implicações educacionais:**
    
    Esta configuração estatística pode indicar:
    
    - **Nível de dificuldade da prova:** {_interpretar_dificuldade(assimetria)}
    - **Efetividade do ensino:** {_interpretar_efetividade(assimetria, cv)}
    - **Equidade educacional:** {_interpretar_equidade(cv, curtose)}
    
    Estas informações são valiosas para ajustar metodologias de ensino, identificar áreas que necessitam de intervenção pedagógica e desenvolver políticas educacionais mais direcionadas.
    """


def _interpretar_dificuldade(assimetria: float) -> str:
    """
    Interpreta o nível de dificuldade com base na assimetria.
    
    Parâmetros:
    -----------
    assimetria : float
        Coeficiente de assimetria
        
    Retorna:
    --------
    str: Interpretação do nível de dificuldade
    """
    if assimetria > 0.7:
        return "Prova potencialmente desafiadora para a maioria dos candidatos"
    elif assimetria > 0.3:
        return "Dificuldade moderada, com desafios para uma parcela significativa dos candidatos"
    elif assimetria > -0.3:
        return "Nível de dificuldade bem calibrado para o público-alvo"
    elif assimetria > -0.7:
        return "Prova possivelmente acessível para a maioria dos candidatos"
    else:
        return "Conteúdo aparentemente dominado pela maioria dos candidatos"


def _interpretar_efetividade(assimetria: float, cv: float) -> str:
    """
    Interpreta a efetividade do ensino com base na assimetria e CV.
    
    Parâmetros:
    -----------
    assimetria : float
        Coeficiente de assimetria
    cv : float
        Coeficiente de variação
        
    Retorna:
    --------
    str: Interpretação da efetividade do ensino
    """
    if assimetria > 0.5 and cv > 25:
        return "Possíveis lacunas no ensino desta competência, com grande disparidade de resultados"
    elif assimetria > 0.3 and cv > 20:
        return "Oportunidades de melhoria no ensino, com heterogeneidade significativa no aprendizado"
    elif assimetria < -0.3 and cv < 20:
        return "Sinais de efetividade no ensino, com boa absorção do conteúdo pela maioria"
    else:
        return "Padrão de ensino típico, com áreas de possível aprimoramento"


def _interpretar_equidade(cv: float, curtose: float) -> str:
    """
    Interpreta a equidade educacional com base no CV e curtose.
    
    Parâmetros:
    -----------
    cv : float
        Coeficiente de variação
    curtose : float
        Coeficiente de curtose
        
    Retorna:
    --------
    str: Interpretação da equidade educacional
    """
    if cv > 30 and curtose < -0.5:
        return "Indícios de potencial inequidade educacional, com grande dispersão e distribuição achatada"
    elif cv > 25 and curtose > 1.0:
        return "Polarização de desempenho, com grupos distintos de alto e baixo rendimento"
    elif cv < 15:
        return "Sinais de equidade nos resultados, com consistência no desempenho entre os candidatos"
    else:
        return "Disparidades moderadas no acesso à educação de qualidade"