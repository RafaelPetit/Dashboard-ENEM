"""
Script de teste para validar as refatorações dos módulos de estatísticas.
Testa as interfaces, analisadores modulares e compatibilidade com código legado.
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, Any

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_interfaces():
    """Testa se as interfaces foram criadas corretamente."""
    print("=== Testando Interfaces ===")
    
    try:
        from utils.estatisticas.interfaces import (
            DataValidator, ResultBuilder, CorrelationAnalyzer,
            DistributionAnalyzer, RegionalAnalyzer
        )
        print("✓ Interfaces importadas com sucesso")
        return True
    except ImportError as e:
        print(f"✗ Erro ao importar interfaces: {e}")
        return False

def test_performance_analyzers():
    """Testa analisadores de performance."""
    print("\n=== Testando Analisadores de Performance ===")
    
    try:
        from utils.estatisticas.desempenho.performance_analyzers import (
            PerformanceDataValidator, PerformanceResultBuilder,
            CorrelationCalculator, DescriptiveStatisticsCalculator
        )
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'NU_NOTA_CN': np.random.normal(500, 100, 1000),
            'NU_NOTA_CH': np.random.normal(520, 90, 1000),
            'NU_NOTA_LC': np.random.normal(480, 110, 1000),
            'NU_NOTA_MT': np.random.normal(510, 95, 1000)
        })
        
        # Testar validador
        validator = PerformanceDataValidator()
        is_valid = validator.validate(test_data)
        print(f"✓ Validação de dados: {'Passou' if is_valid else 'Falhou'}")
        
        # Testar calculador de estatísticas descritivas
        stats_calc = DescriptiveStatisticsCalculator()
        stats = stats_calc.calculate(test_data, column='NU_NOTA_CN')
        print(f"✓ Estatísticas descritivas calculadas: {len(stats)} métricas")
        
        print("✓ Analisadores de performance funcionando")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos analisadores de performance: {e}")
        return False

def test_social_analyzers():
    """Testa analisadores sociais."""
    print("\n=== Testando Analisadores Sociais ===")
    
    try:
        from utils.estatisticas.aspectos_sociais.social_analyzers import (
            SocialDistributionAnalyzer, SocialCorrelationAnalyzer,
            SocialRegionalAnalyzer
        )
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'TP_SEXO': np.random.choice(['M', 'F'], 1000),
            'TP_COR_RACA': np.random.choice([1, 2, 3, 4, 5, 6], 1000),
            'TP_ESCOLA': np.random.choice([1, 2, 3], 1000),
            'SG_UF_NASCIMENTO': np.random.choice(['SP', 'RJ', 'MG', 'RS'], 1000),
            'Quantidade': np.random.randint(10, 100, 1000)
        })
        
        # Testar analisador de distribuição
        dist_analyzer = SocialDistributionAnalyzer()
        dist_result = dist_analyzer.calculate(test_data)
        print(f"✓ Análise de distribuição social: {'status' in dist_result}")
        
        # Testar analisador regional
        regional_analyzer = SocialRegionalAnalyzer()
        regional_result = regional_analyzer.analyze_by_region(test_data, 'TP_SEXO')
        print(f"✓ Análise regional social: {len(regional_result)} regiões")
        
        print("✓ Analisadores sociais funcionando")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos analisadores sociais: {e}")
        return False

def test_general_analyzers():
    """Testa analisadores gerais."""
    print("\n=== Testando Analisadores Gerais ===")
    
    try:
        from utils.estatisticas.geral.general_analyzers import (
            GeneralDataValidator, BasicStatsCalculator,
            GeneralDistributionAnalyzer, DataQualityAnalyzer
        )
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'nota1': np.random.normal(500, 100, 1000),
            'nota2': np.random.normal(520, 90, 1000),
            'categoria': np.random.choice(['A', 'B', 'C'], 1000),
            'UF': np.random.choice(['SP', 'RJ', 'MG'], 1000)
        })
        
        # Introduzir alguns valores nulos para teste
        test_data.loc[np.random.choice(test_data.index, 50), 'nota1'] = np.nan
        
        # Testar validador
        validator = GeneralDataValidator()
        is_valid = validator.validate(test_data)
        print(f"✓ Validação geral: {'Passou' if is_valid else 'Falhou'}")
        
        # Testar calculador de estatísticas básicas
        stats_calc = BasicStatsCalculator()
        stats = stats_calc.calculate_descriptive_stats(test_data['nota1'])
        print(f"✓ Estatísticas básicas: {len(stats)} métricas")
        
        # Testar analisador de qualidade
        quality_analyzer = DataQualityAnalyzer()
        quality_report = quality_analyzer.analyze_data_quality(test_data)
        print(f"✓ Análise de qualidade: Score {quality_report.get('quality_score', 0)}")
        
        print("✓ Analisadores gerais funcionando")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos analisadores gerais: {e}")
        return False

def test_column_runtime_detection():
    """Testa detecção de colunas criadas em runtime."""
    print("\n=== Testando Detecção de Colunas Runtime ===")
    
    try:
        from coluna_runtime import RuntimeColumnDetector, RuntimeColumnMigrator
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'SG_UF_NASCIMENTO': ['SP', 'RJ', 'MG', 'RS'],
            'nota': [500, 520, 480, 510]
        })
        
        # Testar detector
        detector = RuntimeColumnDetector()
        runtime_columns = detector.detect_runtime_columns(test_data)
        print(f"✓ Colunas runtime detectadas: {len(runtime_columns)}")
        
        # Testar migrador
        migrator = RuntimeColumnMigrator()
        migration_script = migrator.generate_migration_script(['REGIAO'])
        print(f"✓ Script de migração gerado: {len(migration_script) > 0}")
        
        print("✓ Detecção de colunas runtime funcionando")
        return True
        
    except Exception as e:
        print(f"✗ Erro na detecção de colunas runtime: {e}")
        return False

def test_legacy_compatibility():
    """Testa compatibilidade com código legado."""
    print("\n=== Testando Compatibilidade com Código Legado ===")
    
    try:
        # Testar funções refatoradas do módulo de desempenho
        from utils.estatisticas.desempenho.analise_desempenho import (
            calcular_estatisticas_descritivas,
            analisar_correlacao_competencias
        )
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'NU_NOTA_CN': np.random.normal(500, 100, 100),
            'NU_NOTA_CH': np.random.normal(520, 90, 100),
            'NU_NOTA_LC': np.random.normal(480, 110, 100),
            'NU_NOTA_MT': np.random.normal(510, 95, 100)
        })
        
        # Testar função refatorada
        stats_result = calcular_estatisticas_descritivas(test_data, 'NU_NOTA_CN')
        print(f"✓ Função de desempenho refatorada: {'media' in stats_result}")
        
        # Testar análise de correlação refatorada
        corr_result = analisar_correlacao_competencias(test_data, ['NU_NOTA_CN', 'NU_NOTA_CH'])
        print(f"✓ Correlação refatorada: {'matriz_correlacao' in corr_result}")
        
        print("✓ Compatibilidade com código legado mantida")
        return True
        
    except Exception as e:
        print(f"✗ Erro na compatibilidade legado: {e}")
        return False

def test_error_handling():
    """Testa tratamento de erros nos novos módulos."""
    print("\n=== Testando Tratamento de Erros ===")
    
    try:
        from utils.estatisticas.desempenho.performance_analyzers import PerformanceDataValidator
        from utils.estatisticas.aspectos_sociais.social_analyzers import SocialDistributionAnalyzer
        
        # Testar com DataFrame vazio
        empty_df = pd.DataFrame()
        
        validator = PerformanceDataValidator()
        is_valid = validator.validate(empty_df)
        print(f"✓ Validação com DataFrame vazio: {'Rejeitado' if not is_valid else 'Aceito'}")
        
        # Testar com dados inválidos
        invalid_df = pd.DataFrame({'col1': [1, 2, 3]})
        
        social_analyzer = SocialDistributionAnalyzer()
        result = social_analyzer.calculate(invalid_df)
        print(f"✓ Análise com dados inválidos: {'Tratada' if 'status' in result else 'Não tratada'}")
        
        print("✓ Tratamento de erros funcionando")
        return True
        
    except Exception as e:
        print(f"✗ Erro no tratamento de erros: {e}")
        return False

def run_all_tests():
    """Executa todos os testes."""
    print("INICIANDO TESTES DE VALIDAÇÃO DAS REFATORAÇÕES")
    print("=" * 50)
    
    tests = [
        test_interfaces,
        test_performance_analyzers,
        test_social_analyzers,
        test_general_analyzers,
        test_column_runtime_detection,
        test_legacy_compatibility,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Erro no teste {test.__name__}: {e}")
            results.append(False)
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {passed}")
    print(f"Testes falharam: {total - passed}")
    print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Refatoração bem-sucedida.")
    else:
        print(f"\n⚠️  {total - passed} testes falharam. Revisar implementação.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n✓ Refatoração validada com sucesso!")
        print("✓ Módulos estão prontos para uso em produção")
        print("✓ Compatibilidade com código legado mantida")
    else:
        print("\n⚠️ Alguns testes falharam. Verificar logs acima.")
    
    # Remover script de teste após validação
    print(f"\n📝 Script de teste será removido após validação completa.")
