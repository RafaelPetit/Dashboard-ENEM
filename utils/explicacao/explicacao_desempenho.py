from utils.helpers.mappings import get_mappings

# Obter limiares dos mapeamentos centralizados
mappings = get_mappings()
LIMIARES_ESTATISTICOS = mappings['limiares_estatisticos']

# Constantes para classificação de correlação
LIMITE_CORRELACAO_FRACA = LIMIARES_ESTATISTICOS['correlacao_fraca']
LIMITE_CORRELACAO_MODERADA = LIMIARES_ESTATISTICOS['correlacao_moderada']
LIMITE_CORRELACAO_FORTE = LIMIARES_ESTATISTICOS['correlacao_forte']

def get_tooltip_analise_comparativa() -> str:
    """
    Retorna o texto do tooltip para a análise comparativa por variável demográfica.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    Sobre esta visualização:<br>
    Compara o desempenho entre diferentes grupos demográficos nas áreas de conhecimento.
    
    Como usar:<br>
    - Selecione a variável demográfica desejada
    - Escolha entre gráfico de barras (para comparações diretas) ou linhas (para visualizar tendências)
    - Use as opções de ordenação para destacar disparidades
    - Aplique filtros por competência para análises específicas
    - Explore a análise detalhada disponível na seção expansível abaixo do gráfico
    
    Os dados são processados em tempo real com otimização de memória para garantir alta performance mesmo com grandes volumes de dados.
    
    Passe o mouse sobre os elementos para ver valores exatos e use a legenda para destacar áreas específicas.
    """


def get_tooltip_relacao_competencias() -> str:
    """
    Retorna o texto do tooltip para a visualização da relação entre competências.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    Sobre esta visualização:<br>
    Exibe como o desempenho em duas competências se relaciona para cada candidato, com análise estatística de correlação.
    
    Como usar:<br>
    - Selecione as competências para os eixos X e Y
    - Aplique filtros opcionais (sexo, tipo de escola)
    - Ative a opção de excluir notas zero para análises mais precisas
    - Explore os agrupamentos por cor/raça ou faixa salarial
    - Observe a linha de tendência que mostra a correlação estatística
    - Consulte a análise detalhada disponível na seção expansível abaixo
    
    O sistema calcula automaticamente coeficientes de correlação, determinação (r²) e fornece interpretações educacionais contextualizadas.
    
    Use os controles de zoom e interaja com a legenda para explorar os dados em detalhe.
    """


def get_tooltip_desempenho_estados() -> str:
    """
    Retorna o texto do tooltip para a visualização de desempenho por estado/região.
    
    Retorna:
    --------
    str: Texto formatado em HTML para exibição em tooltip
    """
    return """
    Sobre esta visualização:<br>
    Apresenta as médias de desempenho por estado ou região em cada área de conhecimento.
    
    Como usar:<br>
    - Compare todas as áreas simultaneamente ou filtre por área específica
    - Ative a ordenação para visualizar rankings por desempenho
    - Alterne entre visualização por estado ou por região
    - Passe o mouse sobre os pontos para ver valores exatos
    - Clique em itens da legenda para destacar ou ocultar áreas específicas
    - Explore a "Análise detalhada" abaixo para insights aprofundados
    
    O processamento dos dados é otimizado para lidar com grandes volumes de informação, calculando automaticamente estatísticas relevantes como variabilidade, diferenças percentuais e comparações regionais.
    
    Veja a análise automática para identificar rapidamente padrões e disparidades regionais.
    """


def get_explicacao_barras_comparativo(variavel_nome: str) -> str:
    """
    Retorna a explicação para o gráfico de barras comparativo.
    
    Parâmetros:
    -----------
    variavel_nome : str
        Nome da variável demográfica selecionada
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação do parâmetro
    if not variavel_nome:
        variavel_nome = "variável selecionada"
        
    return f"""
    **Análise do desempenho por {variavel_nome}:**
    
    Os dados revelam padrões significativos no desempenho quando agrupados por {variavel_nome.lower()}:
    
    - **Disparidades entre grupos:**
      As barras permitem identificar quais grupos apresentam desempenho superior/inferior, destacando inequidades potenciais
    
    - **Variações por área de conhecimento:**
      Observe em quais competências as diferenças são mais acentuadas, revelando possíveis pontos para intervenções educacionais direcionadas
    
    - **Padrões sistemáticos:**
      Analise se as disparidades se repetem consistentemente nas diversas áreas, sugerindo fatores estruturais que transcendem disciplinas específicas
    
    - **Magnitudes comparativas:**
      A escala uniforme permite comparar o tamanho das disparidades entre diferentes competências
    
    Estas informações são essenciais para entender como fatores socioeconômicos e demográficos impactam resultados educacionais e para direcionar políticas de redução de desigualdades.
    
    **💡 Recomendação:** Expanda a seção "Ver análise detalhada por categoria" logo abaixo para acessar métricas adicionais, estatísticas de variabilidade entre grupos e uma análise completa das disparidades por competência.
    """


def get_explicacao_linhas_comparativo(variavel_nome: str) -> str:
    """
    Retorna a explicação para o gráfico de linhas comparativo.
    
    Parâmetros:
    -----------
    variavel_nome : str
        Nome da variável demográfica selecionada
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação do parâmetro
    if not variavel_nome:
        variavel_nome = "variável selecionada"
        
    return f"""
    **Análise de tendências por {variavel_nome}:**
    
    O gráfico de linha revela padrões evolutivos importantes no desempenho:
    
    - **Progressões graduais:**
      As linhas mostram como o desempenho varia entre categorias consecutivas, revelando relações proporcionais e tendências
    
    - **Pontos de inflexão:**
      Identifique momentos onde há mudanças abruptas no padrão, indicando possíveis limiares críticos ou transições importantes
    
    - **Convergências e divergências:**
      Observe onde as linhas de diferentes competências se aproximam ou se distanciam, sugerindo áreas com desafios específicos
    
    - **Efeitos de ordenação:**
      Ao usar a ordenação por valor decrescente, é possível visualizar facilmente a hierarquia de desempenho entre categorias
    
    Esta perspectiva dinâmica ajuda a compreender como diferentes características socioeconômicas influenciam sistematicamente o desempenho educacional ao longo de um espectro de categorias.
    
    **💡 Dica:** Para uma análise mais profunda, incluindo estatísticas de disparidade, variabilidade entre categorias e identificação de padrões específicos por competência, clique na seção "Ver análise detalhada por categoria" abaixo.
    """


def get_explicacao_dispersao(eixo_x_nome: str, eixo_y_nome: str, correlacao: float) -> str:
    """
    Retorna a explicação para o gráfico de dispersão com base na correlação calculada.
    
    Parâmetros:
    -----------
    eixo_x_nome : str
        Nome da competência no eixo X
    eixo_y_nome : str
        Nome da competência no eixo Y
    correlacao : float
        Coeficiente de correlação entre as competências
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação de parâmetros
    if not eixo_x_nome or not eixo_y_nome:
        eixo_x_nome = "Competência 1" if not eixo_x_nome else eixo_x_nome
        eixo_y_nome = "Competência 2" if not eixo_y_nome else eixo_y_nome
        
    try:
        correlacao_float = float(correlacao)
    except (ValueError, TypeError):
        correlacao_float = 0.0
        
    # Determinar tipo de correlação para explicação contextualizada
    descricao_correlacao, padrao_texto, implicacao = _obter_descricao_correlacao(correlacao_float, eixo_x_nome, eixo_y_nome)
    
    # Determinar o coeficiente de determinação (r²)
    r_squared = correlacao_float**2
    r_squared_percent = r_squared * 100
    
    return f"""
    **Análise da relação entre {eixo_x_nome} e {eixo_y_nome}:**
    
    Os dados revelam uma {descricao_correlacao} entre estas duas competências:
    
    - **Padrão de distribuição:**
      A nuvem de pontos {padrao_texto}, o que {implicacao}
    
    - **Coeficiente de determinação:**
      O r² de {r_squared:.2f} indica que {r_squared_percent:.1f}% da variação em uma competência pode ser explicada pela outra
    
    - **Agrupamentos demográficos:**
      Observe como diferentes grupos se distribuem no espaço de desempenho, revelando possíveis padrões de inequidade educacional
    
    - **Linha de tendência:**
      A linha vermelha tracejada representa a relação estatística linear entre as duas competências
    
    Esta visualização é fundamental para entender como diferentes habilidades cognitivas se relacionam no processo educacional e como intervenções em uma área podem impactar outras.
    
    **📊 Análise avançada:** Não deixe de clicar em "Ver análise detalhada da correlação" logo abaixo para acessar estatísticas completas de ambas as competências, interpretação educacional contextualizada e análises adicionais de variabilidade.
    """


def get_explicacao_desempenho_estados(
    area_texto: str, 
    melhor_estado: str, 
    pior_estado: str, 
    variabilidade: str, 
    tipo_localidade: str = "estado"
) -> str:
    """
    Retorna a explicação para o gráfico de desempenho por estado/região.
    
    Parâmetros:
    -----------
    area_texto : str
        Texto descritivo da área selecionada
    melhor_estado : str
        Nome do estado/região com melhor desempenho
    pior_estado : str
        Nome do estado/região com pior desempenho
    variabilidade : str
        Descrição da variabilidade entre estados/regiões
    tipo_localidade : str, default="estado"
        Tipo de localidade (estado ou região)
        
    Retorna:
    --------
    str: Texto explicativo formatado em Markdown
    """
    # Validação de parâmetros
    area_texto = area_texto if area_texto else ""
    melhor_estado = melhor_estado if melhor_estado else "Dado indisponível"
    pior_estado = pior_estado if pior_estado else "Dado indisponível"
    variabilidade = variabilidade.lower() if variabilidade else "variável"
    
    # Ajustar se temos estados indisponíveis
    melhor_info = f"**{melhor_estado}** apresenta o melhor desempenho médio" if melhor_estado != "Dado indisponível" else ""
    pior_info = f"**{pior_estado}** apresenta o menor desempenho médio" if pior_estado != "Dado indisponível" else ""
    
    # Criar lista de bullet points baseada nos dados disponíveis
    pontos_chave = []
    if melhor_info:
        pontos_chave.append(melhor_info)
    if pior_info:
        pontos_chave.append(pior_info)
    pontos_chave.append(f"A análise indica uma **{variabilidade} variação** no desempenho entre {tipo_localidade}s")
    
    # Formatar bullets como string
    bullets = "\n".join([f"- {ponto}" for ponto in pontos_chave])
    
    return f"""
    **Análise do desempenho por {tipo_localidade}{area_texto}:**
    
    O gráfico mostra diferenças significativas no desempenho médio entre diferentes {tipo_localidade}s do Brasil:
    
    {bullets}
    
    Estas diferenças regionais podem refletir:
    - Disparidades nos sistemas educacionais locais
    - Variações no nível socioeconômico médio de cada região
    - Diferenças no acesso a recursos educacionais
    - Fatores contextuais específicos de cada localidade
    
    A visualização permite identificar padrões regionais que podem orientar políticas educacionais focalizadas e redistribuição de recursos.
    
    **💡 Dica:** Para explorar estatísticas detalhadas, comparações regionais e análise percentual das diferenças, clique em "Ver análise detalhada por {tipo_localidade}" abaixo. A opção de visualização por região também está disponível para análises mais abrangentes.
    """


def get_interpretacao_correlacao(correlacao: float, eixo_x_nome: str, eixo_y_nome: str) -> str:
    """
    Gera uma interpretação educacional da correlação entre competências.
    
    Parâmetros:
    -----------
    correlacao : float
        Coeficiente de correlação entre as competências
    eixo_x_nome : str
        Nome da competência no eixo X
    eixo_y_nome : str
        Nome da competência no eixo Y
        
    Retorna:
    --------
    str: Texto interpretativo da correlação
    """
    # Validação de parâmetros
    if not eixo_x_nome or not eixo_y_nome:
        eixo_x_nome = "Competência 1" if not eixo_x_nome else eixo_x_nome
        eixo_y_nome = "Competência 2" if not eixo_y_nome else eixo_y_nome
        
    try:
        correlacao_abs = abs(float(correlacao))
    except (ValueError, TypeError):
        correlacao_abs = 0.0
    
    if correlacao_abs > LIMITE_CORRELACAO_FORTE:
        return f"""
        Existe uma forte associação entre as competências, sugerindo que habilidades e conhecimentos semelhantes são necessários para ambas as áreas. 
        
        Estudantes com bom desempenho em {eixo_x_nome} muito provavelmente também terão bom desempenho em {eixo_y_nome}.
        
        Implicações educacionais:
        - Estratégias pedagógicas que desenvolvem uma área provavelmente beneficiarão a outra
        - Intervenções podem ser coordenadas para maximizar benefícios em ambas as áreas
        - Dificuldades em uma competência podem sinalizar desafios na outra
        """
    elif correlacao_abs > LIMITE_CORRELACAO_MODERADA:
        return f"""
        Há uma associação moderada entre as competências, indicando que algumas habilidades se sobrepõem, mas cada área também exige conhecimentos específicos.
        
        Muitos estudantes com bom desempenho em {eixo_x_nome} também terão bom desempenho em {eixo_y_nome}, mas há exceções significativas.
        
        Implicações educacionais:
        - Existe complementaridade parcial entre as áreas
        - Algumas estratégias de ensino podem beneficiar ambas as competências
        - É importante atenção específica para cada área, pois há aspectos independentes
        """
    elif correlacao_abs > LIMITE_CORRELACAO_FRACA:
        return f"""
        A associação fraca sugere que as competências compartilham algumas habilidades básicas, mas são amplamente distintas em seus requisitos.
        
        O desempenho em {eixo_x_nome} é apenas um preditor limitado do desempenho em {eixo_y_nome}.
        
        Implicações educacionais:
        - As áreas requerem abordagens pedagógicas diferenciadas
        - O desenvolvimento em uma área tem impacto reduzido na outra
        - As avaliações devem considerar cada competência de forma independente
        """
    else:
        return f"""
        Há pouca ou nenhuma associação linear entre as competências, indicando que são áreas de conhecimento e habilidades distintas.
        
        O desempenho em {eixo_x_nome} não permite prever o desempenho em {eixo_y_nome}.
        
        Implicações educacionais:
        - As competências requerem estratégias de ensino completamente diferentes
        - O desenvolvimento em uma área não implica em benefícios para a outra
        - As áreas devem ser trabalhadas como domínios independentes no currículo
        """


# Funções auxiliares

def _obter_descricao_correlacao(correlacao: float, eixo_x_nome: str, eixo_y_nome: str) -> tuple:
    """
    Obtém descrições textuais para explicar uma correlação específica.
    
    Parâmetros:
    -----------
    correlacao : float
        Coeficiente de correlação a ser descrito
    eixo_x_nome : str
        Nome da competência no eixo X
    eixo_y_nome : str
        Nome da competência no eixo Y
        
    Retorna:
    --------
    tuple: (descrição_correlação, padrão_texto, implicação)
    """
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
        
    return descricao_correlacao, padrao_texto, implicacao