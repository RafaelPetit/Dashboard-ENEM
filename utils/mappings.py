def get_mappings():
    """Retorna todos os mapeamentos usados no dashboard."""
    # Definir colunas de notas
    colunas_notas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    
    # Mapeamentos
    competencia_mapping = {
        'NU_NOTA_CN': 'Ciências da Natureza',
        'NU_NOTA_CH': 'Ciências Humanas',
        'NU_NOTA_LC': 'Linguagens e Códigos',
        'NU_NOTA_MT': 'Matemática',
        'NU_NOTA_REDACAO': 'Redação'
    }
    
    dependencia_escola_mapping = {
        1: 'Federal',
        2: 'Estadual',
        3: 'Municipal',
        4: 'Privada',
        -1: 'Não Respondeu'
    }
    
    sexo_mapping = {
        'M': 'Masculino',
        'F': 'Feminino'
    }
    
    race_mapping = {
        0: 'Não declarado',
        1: 'Branca',
        2: 'Preta',
        3: 'Parda',
        4: 'Amarela',
        5: 'Indígena',
        6: 'Não dispõe da informação'
    }
    
    desempenho_mapping = {
        1: 'Desempenho Alto',
        2: 'Desempenho Médio',
        3: 'Desempenho Baixo',
    }
    
    infraestrutura_mapping = {
        1: 'Infraestrutura Alta',
        2: 'Infraestrutura Média',
        3: 'Infraestrutura Baixa',
    }
    
    faixa_etaria_mapping = {
        1: '< 17',
        2: '17',
        3: '18',
        4: '19',
        5: '20',
        6: '21',
        7: '22',
        8: '23',
        9: '24',
        10: '25',
        11: '26 < 30',
        12: '31 < 35',
        13: '36 < 40',
        14: '41 < 45',
        15: '46 < 50',
        16: '51 < 55',
        17: '56 < 60',
        18: '61 < 65',
        19: '66 < 70',
        20: '> 70'
    }
    
    escolaridade_pai_mae_mapping = {
        'A': 'Nunca estudou',
        'B': 'Fundamental incompleto',
        'C': 'Fundamental completo',
        'D': 'Médio incompleto',
        'E': 'Médio Completo',
        'F': 'Superior Completo',    
        'G': 'Pós-graduação Completo',
        'H': 'Não sei'
    }

    acesso_internet_mapping = {
        'A': 'Não',
        'B': 'Sim'
    }
    
    variaveis_categoricas = {
        "TP_COR_RACA": {
            "nome": "Raça/Cor",
            "mapeamento": race_mapping,
            "ordem": list(race_mapping.values())
        },
        "TP_SEXO": {
            "nome": "Sexo", 
            "mapeamento": sexo_mapping,
            "ordem": list(sexo_mapping.values())
        },
        "TP_DEPENDENCIA_ADM_ESC": {
            "nome": "Dependência Administrativa", 
            "mapeamento": dependencia_escola_mapping,
            "ordem": list(dependencia_escola_mapping.values())
        },
        "Q001": {
            "nome": "Escolaridade do Pai", 
            "mapeamento": escolaridade_pai_mae_mapping,
            "ordem": list(escolaridade_pai_mae_mapping.values())
        },
        "Q002": {
            "nome": "Escolaridade da Mãe", 
            "mapeamento": escolaridade_pai_mae_mapping,
            "ordem": list(escolaridade_pai_mae_mapping.values())
        },
        "TP_FAIXA_ETARIA": {
            "nome": "Faixa Etária", 
            "mapeamento": faixa_etaria_mapping,
            "ordem": list(faixa_etaria_mapping.values())
        },
        "Q025" : {
            "nome": "Acesso à Internet",
            "mapeamento": acesso_internet_mapping,
            "ordem": list(acesso_internet_mapping.values())
        }
    }
    
    # Variáveis sociais para a aba de Aspectos Sociais
    variaveis_sociais = {
        "TP_COR_RACA": {"nome": "Raça/Cor", "mapeamento": race_mapping},
        "TP_SEXO": {"nome": "Sexo", "mapeamento": sexo_mapping},
        "TP_DEPENDENCIA_ADM_ESC": {"nome": "Tipo de Escola", "mapeamento": dependencia_escola_mapping},
        "TP_FAIXA_ETARIA": {"nome": "Faixa Etária", "mapeamento": faixa_etaria_mapping},
        "Q001": {"nome": "Escolaridade do Pai", "mapeamento": escolaridade_pai_mae_mapping},
        "Q002": {"nome": "Escolaridade da Mãe", "mapeamento": escolaridade_pai_mae_mapping},
        "Q006": {"nome": "Renda Familiar", "mapeamento": {
            "A": "Nenhuma Renda",
            "B": "Até R$ 1.320,00",
            "C": "De R$ 1.320,01 até R$ 1.980,00",
            "D": "De R$ 1.980,01 até R$ 2.640,00",
            "E": "De R$ 2.640,01 até R$ 3.300,00",
            "F": "De R$ 3.300,01 até R$ 3.960,00",
            "G": "De R$ 3.960,01 até R$ 5.280,00",
            "H": "De R$ 5.280,01 até R$ 6.600,00",
            "I": "De R$ 6.600,01 até R$ 7.920,00",
            "J": "De R$ 7.920,01 até R$ 9240,00",
            "K": "De R$ 9.240,01 até R$ 10.560,00",
            "L": "De R$ 10.560,01 até R$ 11.880,00",
            "M": "De R$ 11.880,01 até R$ 13.200,00",
            "N": "De R$ 13.200,01 até R$ 15.840,00",
            "O": "De R$ 15.840,01 até R$19.800,00",
            "P": "De R$ 19.800,01 até R$ 26.400,00",
            "Q": "Acima de R$ 26.400,00"
        }},
        "Q005": {"nome": "Pessoas na Residência", "mapeamento": {
            i: str(i) for i in range(1, 22)
        }},
        "TP_ST_CONCLUSAO": {"nome": "Situação do Ensino Médio", "mapeamento": {
            1: "Já concluí o Ensino Médio",
            2: "Concluirei em 2023",
            3: "Concluirei após 2023",
            4: "Não concluí/não estou cursando"
        }},
        "NU_INFRAESTRUTURA": {"nome": "Nível de Infraestrutura", "mapeamento": infraestrutura_mapping},
        "Q025": {"nome": "Acesso à Internet", "mapeamento": acesso_internet_mapping}
    }
    
    return (
        colunas_notas, 
        competencia_mapping, 
        race_mapping, 
        sexo_mapping, 
        dependencia_escola_mapping, 
        variaveis_sociais, 
        variaveis_categoricas, 
        desempenho_mapping, 
        infraestrutura_mapping, 
        faixa_etaria_mapping, 
        escolaridade_pai_mae_mapping
    )