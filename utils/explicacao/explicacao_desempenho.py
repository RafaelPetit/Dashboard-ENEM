def get_tooltip_analise_comparativa():
    """Retorna o texto do tooltip para a análise comparativa"""
    return """
    Sobre esta visualização:<br>
    Compara o desempenho entre diferentes grupos demográficos nas áreas de conhecimento.
    
    Como usar:<br>
    - Selecione a variável demográfica desejada
    - Escolha entre gráfico de barras ou linhas
    - Use as opções de ordenação e filtro para personalizar a visualização
    
    Passe o mouse sobre os elementos para ver valores exatos e use a legenda para destacar áreas específicas.
    """

def get_tooltip_relacao_competencias():
    """Retorna o texto do tooltip para a relação entre competências"""
    return """
    Sobre esta visualização:<br>
    Exibe como o desempenho em duas competências se relaciona para cada candidato.
    
    Como usar:<br>
    - Selecione as competências para os eixos X e Y
    - Aplique filtros opcionais (sexo, tipo de escola, notas zero)
    - Explore os agrupamentos por cor/raça
    
    Use os controles de zoom e interaja com a legenda para explorar os dados em detalhe.
    """

def get_tooltip_desempenho_estados():
    """Retorna o texto do tooltip para o desempenho por estado"""
    return """
    Sobre esta visualização:<br>
    Apresenta as médias de desempenho por estado em cada área de conhecimento.
    
    Como usar:<br>
    - Compare todas as áreas simultaneamente
    - Ative a ordenação para visualizar rankings
    - Selecione apenas uma área para análises específicas
    
    Veja a análise automática para identificar rapidamente padrões e disparidades regionais.
    """

def get_explicacao_barras_comparativo(variavel_nome):
    """Retorna a explicação para o gráfico de barras comparativo"""
    return f"""
    **Análise do desempenho por {variavel_nome}:**
    
    Os dados revelam padrões significativos no desempenho quando agrupados por {variavel_nome.lower()}:
    
    - Disparidades entre grupos:
    As barras permitem identificar quais grupos apresentam desempenho superior/inferior
    
    - Variações por área:
    Observe em quais competências as diferenças são mais acentuadas, revelando possíveis pontos de intervenção
    
    - Padrões sistemáticos:
    Analise se as disparidades se repetem consistentemente nas diversas áreas, sugerindo fatores estruturais
    
    Estas informações são essenciais para entender como fatores socioeconômicos impactam resultados educacionais e para direcionar políticas de redução de desigualdades.
    """

def get_explicacao_linhas_comparativo(variavel_nome):
    """Retorna a explicação para o gráfico de linhas comparativo"""
    return f"""
    **Análise de tendências por {variavel_nome}:**
    
    O gráfico de linha revela padrões evolutivos importantes:
    
    - Progressões graduais:
    As linhas mostram como o desempenho varia entre categorias consecutivas, revelando relações proporcionais
    
    - Pontos de inflexão:
    Identifique momentos onde há mudanças abruptas no padrão, indicando possíveis limiares críticos
    
    - Convergências e divergências:
    Observe onde as linhas de diferentes competências se aproximam ou se distanciam, sugerindo áreas com desafios específicos
    
    Esta perspectiva dinâmica ajuda a compreender como diferentes características socioeconômicas influenciam sistematicamente o desempenho educacional.
    """

def get_explicacao_dispersao(eixo_x_nome, eixo_y_nome, correlacao):
    """Retorna a explicação para o gráfico de dispersão com base na correlação calculada"""
    # Determinar tipo de correlação para explicação contextualizada
    if correlacao > 0.7:
        descricao_correlacao = f"forte correlação positiva (r={correlacao:.2f})"
        padrao_texto = "mostra um padrão claro de associação positiva, com pontos formando uma tendência diagonal ascendente"
        implicacao = "sugere que estas competências compartilham bases cognitivas ou pedagógicas semelhantes"
    elif correlacao > 0.4:
        descricao_correlacao = f"correlação moderada positiva (r={correlacao:.2f})"
        padrao_texto = "apresenta uma tendência diagonal visível, embora com dispersão considerável"
        implicacao = "indica algum grau de interdependência entre estas competências"
    elif correlacao > 0.2:
        descricao_correlacao = f"correlação fraca positiva (r={correlacao:.2f})"
        padrao_texto = "mostra uma leve tendência de associação, mas com alta dispersão"
        implicacao = "sugere que há outros fatores importantes que determinam o desempenho em cada área"
    elif correlacao > -0.2:
        descricao_correlacao = f"correlação insignificante (r={correlacao:.2f})"
        padrao_texto = "apresenta distribuição difusa sem padrão claro"
        implicacao = "indica que estas competências funcionam de forma independente"
    elif correlacao > -0.4:
        descricao_correlacao = f"correlação fraca negativa (r={correlacao:.2f})"
        padrao_texto = "mostra uma leve tendência inversa, mas com alta dispersão"
        implicacao = "sugere um pequeno trade-off entre estas competências"
    elif correlacao > -0.7:
        descricao_correlacao = f"correlação moderada negativa (r={correlacao:.2f})"
        padrao_texto = "apresenta tendência diagonal descendente visível"
        implicacao = "indica que pode haver certo antagonismo entre as habilidades necessárias"
    else:
        descricao_correlacao = f"forte correlação negativa (r={correlacao:.2f})"
        padrao_texto = "mostra padrão claro de associação inversa"
        implicacao = "sugere um forte trade-off entre as habilidades envolvidas"
    
    return f"""
    **Análise da relação entre {eixo_x_nome} e {eixo_y_nome}:**
    
    Os dados revelam uma {descricao_correlacao} entre estas duas competências:
    
    - Padrão de distribuição:
    A nuvem de pontos {padrao_texto}, o que {implicacao}
    
    - Agrupamentos demográficos:
    Observe como diferentes grupos raciais se distribuem no espaço de desempenho, revelando possíveis padrões de inequidade
    
    - Concentrações:<br>
    As regiões com maior densidade de pontos indicam os padrões de desempenho mais comuns entre os candidatos
    
    Esta visualização é fundamental para entender como diferentes habilidades cognitivas se relacionam no processo educacional e como intervenções em uma área podem impactar outras.
    """

def get_explicacao_desempenho_estados(area_texto, melhor_estado, pior_estado, variabilidade):
    """Retorna a explicação para o gráfico de desempenho por estado"""
    # Personalizar texto com base na variabilidade
    if variabilidade == "alta":
        var_texto = "significativa variabilidade"
        implica_texto = "indicando grandes desigualdades regionais no sistema educacional"
    elif variabilidade == "moderada":
        var_texto = "moderada variabilidade"
        implica_texto = "sugerindo diferenças regionais importantes, mas não extremas"
    elif variabilidade == "baixa":
        var_texto = "baixa variabilidade"
        implica_texto = "indicando relativa homogeneidade entre os sistemas educacionais regionais"
    else:
        var_texto = "variabilidade heterogênea"
        implica_texto = "com diferentes padrões por área de conhecimento"
    
    return f"""
    **Análise do desempenho por estado{area_texto}:**
    
    A visualização revela padrões geográficos significativos no desempenho educacional:
    
    - Disparidades regionais:
    Observa-se {var_texto} entre os estados, {implica_texto}. {melhor_estado} apresenta o melhor desempenho geral, enquanto {pior_estado} mostra os menores resultados.
    
    - Padrões por competência:
    As áreas de conhecimento apresentam perfis distintos de distribuição territorial, refletindo possivelmente tradições educacionais regionais e foco curricular.
    
    - Potencial para políticas públicas:
    Estados com desempenho superior podem oferecer modelos e práticas educacionais que, adaptados a contextos locais, poderiam beneficiar outras regiões.
    
    Esta análise espacial é essencial para compreender como fatores regionais - incluindo desenvolvimento econômico, infraestrutura e políticas educacionais - impactam o desempenho dos estudantes.
    """