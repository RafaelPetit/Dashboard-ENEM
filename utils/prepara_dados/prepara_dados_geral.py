import pandas as pd
import numpy as np
from utils.data_loader import calcular_seguro

def prepara_dados_histograma(df, coluna, competencia_mapping):
    """
    Prepara os dados para o histograma de notas.
    
    Parâmetros:
    -----------
    df : DataFrame
        DataFrame com os dados dos candidatos
    coluna : str
        Nome da coluna (área de conhecimento) a ser analisada
    competencia_mapping : dict
        Dicionário com mapeamento das colunas para nomes legíveis
        
    Retorna:
    --------
    tuple: (DataFrame filtrado, nome da coluna, nome da área)
    """
    # Filtrar valores inválidos (notas -1 e 0) para análises mais precisas
    df_valido = df[df[coluna] > 0].copy()
    
    # Obter nome amigável da área de conhecimento
    nome_area = competencia_mapping[coluna]
    
    return df_valido, coluna, nome_area

def prepara_dados_grafico_faltas(microdados_estados, estados_selecionados, colunas_presenca):
    """
    Prepara os dados para o gráfico de faltas por estado e dia de prova.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os microdados dos candidatos
    estados_selecionados : lista
        Lista de estados selecionados para análise
    colunas_presenca : dict
        Dicionário mapeando as colunas de presença (mantido para compatibilidade)
        
    Retorna:
    --------
    DataFrame: Dados preparados para o gráfico de faltas por dia de prova
    """
    dados_grafico = []
    
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        total_candidatos = len(dados_estado)
        
        if total_candidatos == 0:
            continue  # Pular estados sem candidatos
        
        # Verificar se a coluna TP_PRESENCA_GERAL existe
        if 'TP_PRESENCA_GERAL' in dados_estado.columns:
            # Contar faltas em ambos os dias (valor 0)
            faltas_ambos_dias = len(dados_estado[dados_estado['TP_PRESENCA_GERAL'] == 0])
            
            # Contar faltas apenas no segundo dia (valor 1 - presente só no primeiro)
            faltas_dia2 = len(dados_estado[dados_estado['TP_PRESENCA_GERAL'] == 1])
            
            # Contar faltas apenas no primeiro dia (valor 2 - presente só no segundo)
            faltas_dia1 = len(dados_estado[dados_estado['TP_PRESENCA_GERAL'] == 2])
            
            # Calcular percentuais
            percentual_faltas_ambos = (faltas_ambos_dias / total_candidatos * 100) if total_candidatos > 0 else 0
            percentual_faltas_dia1 = (faltas_dia1 / total_candidatos * 100) if total_candidatos > 0 else 0
            percentual_faltas_dia2 = (faltas_dia2 / total_candidatos * 100) if total_candidatos > 0 else 0
            
            # Adicionar dados para ambos os dias
            dados_grafico.append({
                'Estado': estado,
                'Tipo de Falta': 'Faltou nos dois dias',
                'Percentual de Faltas': percentual_faltas_ambos
            })
            
            # Adicionar dados para o primeiro dia
            dados_grafico.append({
                'Estado': estado,
                'Tipo de Falta': 'Faltou no primeiro dia',
                'Percentual de Faltas': percentual_faltas_dia1
            })
            
            # Adicionar dados para o segundo dia
            dados_grafico.append({
                'Estado': estado,
                'Tipo de Falta': 'Faltou no segundo dia',
                'Percentual de Faltas': percentual_faltas_dia2
            })
            
    return pd.DataFrame(dados_grafico)