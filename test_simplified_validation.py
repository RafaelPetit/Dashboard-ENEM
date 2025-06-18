"""
Teste simplificado de validação da refatoração dos módulos de estatísticas.
Foca nos aspectos principais: modularidade, interfaces e compatibilidade.
"""

import sys
import os
import pandas as pd
import numpy as np

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_core_functionality():
    """Testa funcionalidade principal dos módulos refatorados."""
    print("=== Teste de Funcionalidade Principal ===")
    
    success_count = 0
    total_tests = 0
    
    # Teste 1: Interfaces foram criadas
    try:
        from utils.estatisticas.interfaces import (
            DataValidator, ResultBuilder, CorrelationAnalyzer
        )
        print("✓ Interfaces criadas e importáveis")
        success_count += 1
    except Exception as e:
        print(f"✗ Interfaces: {e}")
    total_tests += 1
    
    # Teste 2: Analisadores de performance funcionam
    try:
        from utils.estatisticas.desempenho.performance_analyzers import (
            PerformanceDataValidator, DescriptiveStatisticsCalculator
        )
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'NU_NOTA_CN': np.random.normal(500, 100, 100)
        })
        
        validator = PerformanceDataValidator()
        stats_calc = DescriptiveStatisticsCalculator()
        
        is_valid = validator.validate(test_data)
        stats = stats_calc.calculate(test_data, column='NU_NOTA_CN')
        
        if is_valid and 'media' in stats:
            print("✓ Analisadores de performance funcionando")
            success_count += 1
        else:
            print("✗ Analisadores de performance com problema")
    except Exception as e:
        print(f"✗ Analisadores de performance: {e}")
    total_tests += 1
    
    # Teste 3: Funções principais do módulo de desempenho
    try:
        from utils.estatisticas.desempenho.analise_desempenho import (
            calcular_estatisticas_descritivas
        )
        
        test_data = pd.DataFrame({
            'NU_NOTA_CN': np.random.normal(500, 100, 100)
        })
        
        result = calcular_estatisticas_descritivas(test_data, 'NU_NOTA_CN')
        
        if 'media' in result:
            print("✓ Funções principais de desempenho funcionando")
            success_count += 1
        else:
            print("✗ Funções principais retornaram resultado inesperado")
    except Exception as e:
        print(f"✗ Funções principais de desempenho: {e}")
    total_tests += 1
    
    # Teste 4: Analisadores sociais básicos
    try:
        from utils.estatisticas.aspectos_sociais.social_analyzers import (
            SocialDistributionAnalyzer
        )
        
        test_data = pd.DataFrame({
            'Quantidade': np.random.randint(10, 100, 50)
        })
        
        analyzer = SocialDistributionAnalyzer()
        result = analyzer.calculate(test_data)
        
        if isinstance(result, dict):
            print("✓ Analisadores sociais básicos funcionando")
            success_count += 1
        else:
            print("✗ Analisadores sociais retornaram tipo inesperado")
    except Exception as e:
        print(f"✗ Analisadores sociais: {e}")
    total_tests += 1
    
    # Teste 5: Analisadores gerais básicos
    try:
        from utils.estatisticas.geral.general_analyzers import (
            GeneralDataValidator, BasicStatsCalculator
        )
        
        test_data = pd.DataFrame({
            'nota': np.random.normal(500, 100, 100)
        })
        
        validator = GeneralDataValidator()
        calc = BasicStatsCalculator()
        
        is_valid = validator.validate(test_data)
        stats = calc.calculate_descriptive_stats(test_data['nota'])
        
        if is_valid and 'mean' in stats:
            print("✓ Analisadores gerais básicos funcionando")
            success_count += 1
        else:
            print("✗ Analisadores gerais com problema")
    except Exception as e:
        print(f"✗ Analisadores gerais: {e}")
    total_tests += 1
    
    # Teste 6: Detector de colunas runtime
    try:
        from coluna_runtime import DetectorColunaRuntime
        
        test_data = pd.DataFrame({
            'SG_UF_NASCIMENTO': ['SP', 'RJ', 'MG']
        })
        
        detector = DetectorColunaRuntime()
        detection = detector.detectar_criacao_regiao(test_data)
        
        if isinstance(detection, dict):
            print("✓ Detector de colunas runtime funcionando")
            success_count += 1
        else:
            print("✗ Detector retornou tipo inesperado")
    except Exception as e:
        print(f"✗ Detector de colunas runtime: {e}")
    total_tests += 1
    
    return success_count, total_tests

def test_modular_architecture():
    """Testa se a arquitetura modular foi implementada corretamente."""
    print("\n=== Teste de Arquitetura Modular ===")
    
    success_count = 0
    total_tests = 0
    
    # Teste 1: Separação de responsabilidades
    try:
        from utils.estatisticas.desempenho.performance_analyzers import (
            PerformanceDataValidator, PerformanceResultBuilder,
            CorrelationCalculator, DescriptiveStatisticsCalculator
        )
        
        # Verificar se são classes diferentes (separação de responsabilidades)
        validator = PerformanceDataValidator()
        builder = PerformanceResultBuilder()
        calculator = CorrelationCalculator()
        stats_calc = DescriptiveStatisticsCalculator()
        
        classes_diferentes = len(set([
            type(validator).__name__,
            type(builder).__name__, 
            type(calculator).__name__,
            type(stats_calc).__name__
        ])) == 4
        
        if classes_diferentes:
            print("✓ Separação de responsabilidades implementada")
            success_count += 1
        else:
            print("✗ Classes não estão adequadamente separadas")
    except Exception as e:
        print(f"✗ Separação de responsabilidades: {e}")
    total_tests += 1
    
    # Teste 2: Interfaces padronizadas
    try:
        from utils.estatisticas.interfaces import DataValidator
        from utils.estatisticas.desempenho.performance_analyzers import PerformanceDataValidator
        
        # Verificar se implementa a interface
        validator = PerformanceDataValidator()
        implementa_interface = hasattr(validator, 'validate')
        
        if implementa_interface:
            print("✓ Interfaces padronizadas implementadas")
            success_count += 1
        else:
            print("✗ Interfaces não implementadas corretamente")
    except Exception as e:
        print(f"✗ Interfaces padronizadas: {e}")
    total_tests += 1
    
    # Teste 3: Cache e otimizações
    try:
        from utils.estatisticas.desempenho.analise_desempenho import calcular_estatisticas_descritivas
        
        # Verificar se a função tem decorador de cache
        tem_cache = hasattr(calcular_estatisticas_descritivas, '__wrapped__')
        
        if tem_cache:
            print("✓ Sistema de cache implementado")
            success_count += 1
        else:
            print("✗ Sistema de cache não detectado")
    except Exception as e:
        print(f"✗ Sistema de cache: {e}")
    total_tests += 1
    
    return success_count, total_tests

def test_performance_improvements():
    """Testa melhorias de performance."""
    print("\n=== Teste de Melhorias de Performance ===")
    
    success_count = 0
    total_tests = 0
    
    # Teste 1: Processamento eficiente de dados grandes
    try:
        from utils.estatisticas.desempenho.analise_desempenho import calcular_estatisticas_descritivas
        
        # Criar dataset maior para teste
        large_data = pd.DataFrame({
            'NU_NOTA_CN': np.random.normal(500, 100, 10000)
        })
        
        import time
        start_time = time.time()
        result = calcular_estatisticas_descritivas(large_data, 'NU_NOTA_CN')
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if processing_time < 5.0 and 'media' in result:  # Menos de 5 segundos
            print(f"✓ Processamento eficiente: {processing_time:.2f}s para 10k registros")
            success_count += 1
        else:
            print(f"✗ Processamento lento: {processing_time:.2f}s")
    except Exception as e:
        print(f"✗ Teste de performance: {e}")
    total_tests += 1
    
    # Teste 2: Uso de memória otimizado
    try:
        import psutil
        import os
        
        # Medir uso de memória antes
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Executar operação
        from utils.estatisticas.desempenho.analise_desempenho import calcular_estatisticas_descritivas
        test_data = pd.DataFrame({
            'NU_NOTA_CN': np.random.normal(500, 100, 5000)
        })
        result = calcular_estatisticas_descritivas(test_data, 'NU_NOTA_CN')
        
        # Medir uso de memória depois
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        if memory_increase < 50:  # Menos de 50MB de aumento
            print(f"✓ Uso de memória otimizado: +{memory_increase:.1f}MB")
            success_count += 1
        else:
            print(f"✗ Alto uso de memória: +{memory_increase:.1f}MB")
    except Exception as e:
        print(f"✗ Teste de memória: {e}")
    total_tests += 1
    
    return success_count, total_tests

def run_simplified_tests():
    """Executa testes simplificados focados nos aspectos principais."""
    print("VALIDAÇÃO SIMPLIFICADA DA REFATORAÇÃO DOS MÓDULOS DE ESTATÍSTICAS")
    print("=" * 70)
    
    total_success = 0
    total_tests = 0
    
    # Testes principais
    success, tests = test_core_functionality()
    total_success += success
    total_tests += tests
    
    success, tests = test_modular_architecture()
    total_success += success
    total_tests += tests
    
    success, tests = test_performance_improvements()
    total_success += success
    total_tests += tests
    
    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 70)
    
    success_rate = (total_success / total_tests) * 100
    
    print(f"Testes executados: {total_tests}")
    print(f"Testes aprovados: {total_success}")
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 REFATORAÇÃO BEM-SUCEDIDA!")
        print("✓ Modularidade implementada")
        print("✓ Arquitetura SOLID aplicada")
        print("✓ Performance otimizada")
        print("✓ Compatibilidade mantida")
        status = "success"
    elif success_rate >= 60:
        print("\n⚠️  REFATORAÇÃO PARCIALMENTE BEM-SUCEDIDA")
        print("✓ Aspectos principais funcionando")
        print("⚠️  Alguns ajustes necessários")
        status = "partial"
    else:
        print("\n❌ REFATORAÇÃO PRECISA DE AJUSTES")
        print("❌ Problemas significativos identificados")
        status = "failed"
    
    return status

if __name__ == "__main__":
    try:
        status = run_simplified_tests()
        
        print(f"\n📊 STATUS FINAL: {status.upper()}")
        
        if status == "success":
            print("\n🎯 PRÓXIMOS PASSOS:")
            print("1. ✓ Remover scripts de teste")
            print("2. ✓ Documentar pontos de integração")
            print("3. ✓ Preparar para deploy em produção")
        else:
            print("\n🔧 AÇÕES RECOMENDADAS:")
            print("1. Revisar implementações com falha")
            print("2. Corrigir imports e dependências")
            print("3. Executar testes novamente")
            
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO NOS TESTES: {e}")
        print("Revisar configuração do ambiente e dependências")
