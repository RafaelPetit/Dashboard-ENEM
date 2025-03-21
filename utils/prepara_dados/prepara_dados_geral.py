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
    Prepara os dados para o gráfico de faltas por estado e área de conhecimento.
    
    Parâmetros:
    -----------
    microdados_estados : DataFrame
        DataFrame com os dados dos candidatos
    estados_selecionados : lista
        Lista de estados selecionados para análise
    colunas_presenca : dict
        Dicionário mapeando as colunas de presença com seus nomes para exibição
        
    Retorna:
    --------
    DataFrame: Dados preparados para o gráfico de linha de faltas
    """
    dados_grafico = []
    dados_gerais = []  # Lista separada para os dados gerais
    
    for estado in estados_selecionados:
        dados_estado = microdados_estados[microdados_estados['SG_UF_PROVA'] == estado]
        total_candidatos = len(dados_estado)
        
        if total_candidatos == 0:
            continue  # Pular estados sem candidatos
        
        # Contar faltas gerais (quem faltou em pelo menos uma prova)
        # Calcular faltas gerais como proxy caso a coluna não exista
        if 'TP_PRESENCA_GERAL' in dados_estado.columns:
            faltas_gerais = len(dados_estado[dados_estado['TP_PRESENCA_GERAL'] == 0])
        else:
            # Considerar ausente se faltou em qualquer uma das provas principais
            faltas_cn = len(dados_estado[dados_estado['TP_PRESENCA_CN'] == 0]) if 'TP_PRESENCA_CN' in dados_estado.columns else 0
            faltas_ch = len(dados_estado[dados_estado['TP_PRESENCA_CH'] == 0]) if 'TP_PRESENCA_CH' in dados_estado.columns else 0
            faltas_lc = len(dados_estado[dados_estado['TP_PRESENCA_LC'] == 0]) if 'TP_PRESENCA_LC' in dados_estado.columns else 0
            faltas_mt = len(dados_estado[dados_estado['TP_PRESENCA_MT'] == 0]) if 'TP_PRESENCA_MT' in dados_estado.columns else 0
            
            # União (não soma) das faltas
            faltas_gerais = max(faltas_cn, faltas_ch, faltas_lc, faltas_mt)
        
        percentual_faltas_gerais = (faltas_gerais / total_candidatos * 100) if total_candidatos > 0 else 0
        
        # Armazenar dados gerais em lista separada
        dados_gerais.append({
            'Estado': estado,
            'Área': 'Geral (qualquer prova)',
            'Percentual de Faltas': percentual_faltas_gerais
        })
        
        # Contar faltas por área específica
        for coluna, nome_area in colunas_presenca.items():
            # Para a redação, precisamos tratar de forma especial
            if coluna == 'TP_PRESENCA_REDACAO':
                # Verificar se temos a coluna de nota de redação
                if 'NU_NOTA_REDACAO' in dados_estado.columns:
                    # Considerar como falta se a nota é 0, nula, ou menor ou igual a zero
                    faltas_redacao = len(dados_estado[(dados_estado['NU_NOTA_REDACAO'].isna()) | 
                                                      (dados_estado['NU_NOTA_REDACAO'] <= 0)])
                    percentual_faltas_area = (faltas_redacao / total_candidatos * 100) if total_candidatos > 0 else 0
                    
                    dados_grafico.append({
                        'Estado': estado,
                        'Área': 'Redação',
                        'Percentual de Faltas': percentual_faltas_area
                    })
            elif coluna in dados_estado.columns:
                faltas_area = len(dados_estado[dados_estado[coluna] == 0])
                percentual_faltas_area = (faltas_area / total_candidatos * 100) if total_candidatos > 0 else 0
                
                dados_grafico.append({
                    'Estado': estado,
                    'Área': nome_area,
                    'Percentual de Faltas': percentual_faltas_area
                })
    
    # Combinar os DataFrames com dados gerais primeiro
    df_geral = pd.DataFrame(dados_gerais)
    df_areas = pd.DataFrame(dados_grafico)
    df_final = pd.concat([df_geral, df_areas], ignore_index=True)
    
    return df_final