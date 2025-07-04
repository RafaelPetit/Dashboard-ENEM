from typing import Dict, Any, List

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
    
    tipo_escola_mapping = {
        1: 'Não informado',
        2: 'Pública',
        3: 'Privada'
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

    faixa_salarial = {
        0: 'Nenhuma Renda',
        1: 'Até 1 salário mínimo',
        2: '1 a 2 salários mínimos',
        3: '2 a 3 salários mínimos',
        4: '3 a 5 salários mínimos',
        5: '5 a 10 salários mínimos',
        6: '10 a 20 salários mínimos',
        7: ' > 20 salários mínimos'
    }

    conclusao_ensino_medio_mapping = {
        1: "Ensino Médio Completo",
        2: "concluir em 2023",
        3: "concluir após 2023",
        4: "Não concluído e não cursado"
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
        },

        "TP_FAIXA_SALARIAL": {
            "nome": "Faixa Salarial",
            "mapeamento": faixa_salarial,
            "ordem": list(faixa_salarial.values())
        },
        
        "TP_ST_CONCLUSAO": {
            "nome": "Situação do Ensino Médio",
            "mapeamento": conclusao_ensino_medio_mapping,
            "ordem": list(conclusao_ensino_medio_mapping.values())
        },
        
        "TP_ESCOLA": {
            "nome": "Tipo de Escola",
            "mapeamento": tipo_escola_mapping,
            "ordem": list(tipo_escola_mapping.values())
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

    # Mapeamento de regiões - Norte, Nordeste e Centro Oeste (MS e DF) REMOVIDO do dataset
    regioes_mapping = {
        "Sul": ["PR", "RS", "SC"],
        "Sudeste": ["SP", "RJ", "ES", "MG"],
        "Centro-Oeste": ["GO", "MT"],
    }

    # Configurações de visualização
    CONFIG_VISUALIZACAO = {
        'altura_padrao_grafico': 500,
        'opacidade_padrao': 0.7,
        'angulo_eixo_x': -45,
        'tamanho_marcador': 6,
        'min_pontos_regressao': 10,
        'min_valores_unicos': 5,
        'largura_linha': 2
    }
    
    MAPEAMENTO_FAIXAS_SALARIAIS = {
        0: "0 - Nenhuma Renda",
        1: "1 - Até 1 SM",
        2: "2 - 1 a 2 SM",
        3: "3 - 2 a 3 SM",
        4: "4 - 3 a 5 SM",
        5: "5 - 5 a 10 SM",
        6: "6 - 10 a 20 SM",
        7: "7 - Mais de 20 SM"
    }
    
    LIMIARES = {
        'correlacao_fraca': 0.3,
        'correlacao_moderada': 0.7,
        'variabilidade_baixa': 8,
        'variabilidade_moderada': 15,
        'min_pontos_regressao': 10
    }

    # Configurações para processamento de dados
    CONFIG_PROCESSAMENTO = {
        'max_amostras_scatter': 50000,  # Limite de pontos em gráficos de dispersão
        'tamanho_lote': 10,             # Número de categorias processadas por lote
        'tamanho_lote_estados': 5,      # Número de estados processados por lote
        'max_categorias_alerta': 50,    # Limite para alerta de muitas categorias
        'limiar_agrupamento': 100,      # Usar agrupamento para menos de X categorias
        'nivel_amostragem_padrao': 'normal'  # Nível de amostragem padrão
    }

    # Limiares para interpretação e validação
    LIMIARES_PROCESSAMENTO = {
        'min_completude_dados': 0.5,    # Mínimo de completude para colunas (50%)
        'min_amostras_correlacao': 30,  # Mínimo de amostras para calcular correlação
        'max_outliers_percentual': 0.05 # Máximo de outliers permitidos (5%)
    }

    # Limiares para interpretação estatística
    LIMIARES_ESTATISTICOS = {
        'correlacao_fraca': 0.3,
        'correlacao_moderada': 0.7,
        'correlacao_forte': 0.8,
        'variabilidade_baixa': 8,
        'variabilidade_moderada': 15
    }

    # Opções de amostragem para diferentes níveis de detalhamento
    OPCOES_AMOSTRAGEM = {
        'ultra_rapida': 0.01,
        'rapida': 0.05, 
        'normal': 0.25,
        'detalhada': 0.5,
        'completa': 1.0
    }

    # Mapeamento de desempenho para cálculos específicos
    MAPEAMENTO_DESEMPENHO = {
        'faixas_notas': {
            'muito_baixo': (0, 300),
            'baixo': (300, 500),
            'medio': (500, 700),
            'alto': (700, 850),
            'muito_alto': (850, 1000)
        },
        'faixas_percentual': {
            'fundo': (0, 0.2),    # Inferior (0-20%)
            'baixo': (0.2, 0.4),  # Baixo (20-40%)
            'medio': (0.4, 0.6),  # Médio (40-60%)
            'alto': (0.6, 0.8),   # Alto (60-80%)
            'topo': (0.8, 1.0)    # Superior (80-100%)
        }
    }
    
    return {
        'colunas_notas': colunas_notas,
        'competencia_mapping': competencia_mapping,
        'race_mapping': race_mapping,
        'sexo_mapping': sexo_mapping,
        'dependencia_escola_mapping': dependencia_escola_mapping,
        'tipo_escola_mapping': tipo_escola_mapping,
        'variaveis_sociais': variaveis_sociais,
        'acesso_internet_mapping': acesso_internet_mapping,
        'conclusao_ensino_medio_mapping': conclusao_ensino_medio_mapping,
        'variaveis_categoricas': variaveis_categoricas,
        'desempenho_mapping': desempenho_mapping,
        'infraestrutura_mapping': infraestrutura_mapping,
        'faixa_etaria_mapping': faixa_etaria_mapping,
        'escolaridade_pai_mae_mapping': escolaridade_pai_mae_mapping,
        'regioes_mapping': regioes_mapping,
        'faixa_salarial': faixa_salarial,
        'config_visualizacao': CONFIG_VISUALIZACAO,
        'mapeamento_faixas_salariais': MAPEAMENTO_FAIXAS_SALARIAIS,
        'limiares': LIMIARES,
        'opcoes_amostragem': OPCOES_AMOSTRAGEM,
        'config_processamento': CONFIG_PROCESSAMENTO,
        'limiares_processamento': LIMIARES_PROCESSAMENTO,
        'limiares_estatisticos': LIMIARES_ESTATISTICOS,
        'mapeamento_desempenho': MAPEAMENTO_DESEMPENHO
    }