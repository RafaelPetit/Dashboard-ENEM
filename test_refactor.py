"""
Script de teste para verificar a nova arquitetura modular.

Este script testa rapidamente se as novas classes e interfaces
estão funcionando corretamente sem afetar o código principal.
"""

import pandas as pd
import numpy as np
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def criar_dados_teste():
    """Cria um DataFrame de teste simples."""
    np.random.seed(42)
    
    n_registros = 1000
    estados = ['SP', 'RJ', 'MG', 'PR', 'RS']
    sexos = ['M', 'F']
    racas = [1, 2, 3, 4, 5]
    
    dados = {
        'SG_UF_PROVA': np.random.choice(estados, n_registros),
        'TP_SEXO': np.random.choice(sexos, n_registros),
        'TP_COR_RACA': np.random.choice(racas, n_registros),
        'TP_DEPENDENCIA_ADM_ESC': np.random.choice([1, 2, 3, 4], n_registros),
        'NU_NOTA_CN': np.random.normal(500, 100, n_registros).clip(0, 1000),
        'NU_NOTA_CH': np.random.normal(500, 100, n_registros).clip(0, 1000),
        'NU_NOTA_LC': np.random.normal(500, 100, n_registros).clip(0, 1000),
        'NU_NOTA_MT': np.random.normal(500, 100, n_registros).clip(0, 1000),
        'NU_NOTA_REDACAO': np.random.normal(500, 100, n_registros).clip(0, 1000),
        'TP_PRESENCA_GERAL': np.random.choice([0, 1], n_registros, p=[0.1, 0.9]),
        'Q001': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F'], n_registros),
        'Q002': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F'], n_registros)
    }
    
    return pd.DataFrame(dados)


def testar_classes_base():
    """Testa as classes base."""
    print("🔧 Testando classes base...")
    
    try:
        from utils.prepara_dados.base import BaseDataProcessor, CacheableProcessor, ProcessorFactory
        from utils.prepara_dados.common_utils import MappingManager, StatisticalCalculator
        
        # Testar MappingManager
        mapping_manager = MappingManager()
        mappings = mapping_manager.get_mappings()
        
        assert 'competencia_mapping' in mappings
        assert 'config_processamento' in mappings
        print("✅ MappingManager funcionando")
        
        # Testar StatisticalCalculator
        stats_calc = StatisticalCalculator()
        dados_teste = pd.Series([1, 2, 3, 4, 5])
        media = stats_calc.calculate_mean(dados_teste)
        
        assert abs(media - 3.0) < 0.01
        print("✅ StatisticalCalculator funcionando")
        
        # Testar ProcessorFactory
        factory = ProcessorFactory()
        assert factory is not None
        print("✅ ProcessorFactory funcionando")
        
        print("✅ Classes base: OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas classes base: {e}\n")
        return False


def testar_processadores_geral():
    """Testa os processadores de análises gerais."""
    print("📊 Testando processadores gerais...")
    
    try:
        from utils.prepara_dados.geral.data_manager import GeneralDataManager
        from utils.mappings import get_mappings
        
        # Criar dados de teste
        df_teste = criar_dados_teste()
        mappings = get_mappings()
        
        # Testar gerenciador geral
        manager = GeneralDataManager()
        
        # Testar preparação de histograma
        resultado = manager.prepare_histogram_data(
            data=df_teste,
            coluna='NU_NOTA_MT',
            competencia_mapping=mappings['competencia_mapping']
        )
        
        assert not resultado[0].empty
        print("✅ Preparação de histograma funcionando")
        
        # Testar métricas principais
        metricas = manager.prepare_main_metrics(
            data=df_teste,
            estados_selecionados=['SP', 'RJ'],
            colunas_notas=mappings['colunas_notas']
        )
        
        assert 'total_candidatos' in metricas
        print("✅ Métricas principais funcionando")
        
        print("✅ Processadores gerais: OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos processadores gerais: {e}\n")
        return False


def testar_processadores_aspectos_sociais():
    """Testa os processadores de aspectos sociais."""
    print("👥 Testando processadores de aspectos sociais...")
    
    try:
        from utils.prepara_dados.aspectos_sociais.data_manager import SocialDataManager
        from utils.mappings import get_mappings
        
        # Criar dados de teste
        df_teste = criar_dados_teste()
        mappings = get_mappings()
        
        # Testar gerenciador social
        manager = SocialDataManager()
        
        # Testar distribuição social
        resultado = manager.prepare_social_distribution(
            data=df_teste,
            aspecto_social='TP_SEXO'
        )
        
        assert not resultado.empty
        print("✅ Distribuição social funcionando")
        
        # Testar análise socioeconômica
        resultado_socio = manager.prepare_socioeconomic_analysis(
            data=df_teste,
            aspecto_social='Q001',
            variaveis_categoricas=mappings['variaveis_categoricas']
        )
        
        assert not resultado_socio.empty
        print("✅ Análise socioeconômica funcionando")
        
        print("✅ Processadores aspectos sociais: OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos processadores aspectos sociais: {e}\n")
        return False


def testar_processadores_desempenho():
    """Testa os processadores de desempenho."""
    print("📈 Testando processadores de desempenho...")
    
    try:
        from utils.prepara_dados.desempenho.data_manager import PerformanceDataManager
        from utils.mappings import get_mappings
        
        # Criar dados de teste
        df_teste = criar_dados_teste()
        mappings = get_mappings()
        
        # Testar gerenciador de desempenho
        manager = PerformanceDataManager()
        
        # Testar análise comparativa
        resultado = manager.prepare_comparative_analysis(
            data=df_teste,
            variavel_selecionada='TP_SEXO',
            variaveis_categoricas=mappings['variaveis_categoricas'],
            colunas_notas=mappings['colunas_notas'],
            competencia_mapping=mappings['competencia_mapping']
        )
        
        assert not resultado.empty
        assert 'Categoria' in resultado.columns
        assert 'Competência' in resultado.columns
        assert 'Média' in resultado.columns
        print("✅ Análise comparativa funcionando")
        
        # Testar análise de estados
        resultado_estados = manager.prepare_state_performance(
            data=df_teste,
            estados_selecionados=['SP', 'RJ'],
            colunas_notas=mappings['colunas_notas'],
            competencia_mapping=mappings['competencia_mapping']
        )
        
        assert not resultado_estados.empty
        print("✅ Análise por estados funcionando")
        
        print("✅ Processadores desempenho: OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos processadores desempenho: {e}\n")
        return False


def testar_compatibilidade():
    """Testa a compatibilidade com as funções antigas."""
    print("🔄 Testando compatibilidade com API antiga...")
    
    try:
        # Testar imports de compatibilidade
        from utils.prepara_dados import (
            preparar_dados_histograma,
            preparar_dados_comparativo,
            prepare_social_data,
            prepare_performance_data
        )
        
        # Criar dados de teste
        df_teste = criar_dados_teste()
        from utils.mappings import get_mappings
        mappings = get_mappings()
        
        # Testar função de histograma
        resultado_hist = preparar_dados_histograma(
            df=df_teste,
            coluna='NU_NOTA_MT',
            competencia_mapping=mappings['competencia_mapping']
        )
        
        assert len(resultado_hist) == 3  # Deve retornar tupla com 3 elementos
        print("✅ Função preparar_dados_histograma funcionando")
        
        # Testar função de desempenho
        resultado_perf = preparar_dados_comparativo(
            microdados_full=df_teste,
            variavel_selecionada='TP_SEXO',
            variaveis_categoricas=mappings['variaveis_categoricas'],
            colunas_notas=mappings['colunas_notas'],
            competencia_mapping=mappings['competencia_mapping']
        )
        
        assert not resultado_perf.empty
        print("✅ Função preparar_dados_comparativo funcionando")
        
        print("✅ Compatibilidade: OK\n")
        return True
        
    except Exception as e:
        print(f"❌ Erro na compatibilidade: {e}\n")
        return False


def executar_todos_testes():
    """Executa todos os testes."""
    print("🚀 Iniciando testes da nova arquitetura modular\n")
    
    testes = [
        testar_classes_base,
        testar_processadores_geral,
        testar_processadores_aspectos_sociais,
        testar_processadores_desempenho,
        testar_compatibilidade
    ]
    
    resultados = []
    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Erro inesperado em {teste.__name__}: {e}")
            resultados.append(False)
    
    # Resumo final
    sucessos = sum(resultados)
    total = len(resultados)
    
    print(f"📋 Resumo dos testes:")
    print(f"✅ Sucessos: {sucessos}/{total}")
    print(f"❌ Falhas: {total - sucessos}/{total}")
    
    if sucessos == total:
        print("\n🎉 Todos os testes passaram! A refatoração está funcionando corretamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    return sucessos == total


if __name__ == "__main__":
    executar_todos_testes()
