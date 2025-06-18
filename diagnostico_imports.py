#!/usr/bin/env python3
"""
Script de diagnóstico para verificar problemas de importação.
Testa especificamente a função calcular_estatisticas_comparativas.
"""

import sys
import os
import importlib
import traceback
from pathlib import Path

def diagnosticar_importacoes():
    """
    Executa diagnóstico completo das importações do módulo estatísticas.
    """
    print("=== DIAGNÓSTICO DE IMPORTAÇÕES ===")
    print(f"Python: {sys.version}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print()
    
    # Adicionar diretório atual ao path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Teste 1: Verificar se o arquivo existe
    print("1. Verificando arquivos...")
    analise_file = current_dir / "utils" / "estatisticas" / "desempenho" / "analise_desempenho.py"
    print(f"   Arquivo analise_desempenho.py existe: {analise_file.exists()}")
    
    init_file = current_dir / "utils" / "estatisticas" / "__init__.py"
    print(f"   Arquivo __init__.py existe: {init_file.exists()}")
    print()
    
    # Teste 2: Importação direta do módulo
    print("2. Testando importação direta do módulo...")
    try:
        import utils.estatisticas.desempenho.analise_desempenho as ad
        print("   ✓ Módulo analise_desempenho importado com sucesso")
        
        # Verificar se a função existe
        if hasattr(ad, 'calcular_estatisticas_comparativas'):
            print("   ✓ Função calcular_estatisticas_comparativas encontrada")
            func = getattr(ad, 'calcular_estatisticas_comparativas')
            print(f"   ✓ Tipo: {type(func)}")
            print(f"   ✓ Callable: {callable(func)}")
        else:
            print("   ✗ Função calcular_estatisticas_comparativas NÃO encontrada")
            
    except Exception as e:
        print(f"   ✗ Erro na importação direta: {e}")
        traceback.print_exc()
    print()
    
    # Teste 3: Importação via __init__.py
    print("3. Testando importação via __init__.py...")
    try:
        from utils.estatisticas import calcular_estatisticas_comparativas
        print("   ✓ Importação via __init__.py funcionou")
        print(f"   ✓ Tipo: {type(calcular_estatisticas_comparativas)}")
        print(f"   ✓ Módulo: {calcular_estatisticas_comparativas.__module__}")
    except Exception as e:
        print(f"   ✗ Erro na importação via __init__.py: {e}")
        traceback.print_exc()
    print()
    
    # Teste 4: Listar todas as funções disponíveis
    print("4. Listando funções disponíveis no módulo...")
    try:
        import utils.estatisticas.desempenho.analise_desempenho as ad
        functions = [name for name in dir(ad) if not name.startswith('_') and callable(getattr(ad, name))]
        print(f"   Funções encontradas ({len(functions)}):")
        for func in sorted(functions):
            print(f"     - {func}")
    except Exception as e:
        print(f"   ✗ Erro ao listar funções: {e}")
    print()
    
    # Teste 5: Verificar cache de módulos
    print("5. Verificando cache de módulos...")
    modules_estatisticas = [mod for mod in sys.modules.keys() if 'utils.estatisticas' in mod]
    print(f"   Módulos estatísticas em cache ({len(modules_estatisticas)}):")
    for mod in sorted(modules_estatisticas):
        print(f"     - {mod}")
    print()
    
    # Teste 6: Tentar recarregar módulos
    print("6. Testando recarga de módulos...")
    try:
        # Remover módulos do cache
        to_remove = [mod for mod in sys.modules.keys() if 'utils.estatisticas' in mod]
        for mod in to_remove:
            del sys.modules[mod]
        print(f"   ✓ Removidos {len(to_remove)} módulos do cache")
        
        # Reimportar
        from utils.estatisticas import calcular_estatisticas_comparativas
        print("   ✓ Reimportação após limpeza de cache funcionou")
    except Exception as e:
        print(f"   ✗ Erro na reimportação: {e}")
        traceback.print_exc()
    print()
    
    print("=== DIAGNÓSTICO CONCLUÍDO ===")

if __name__ == "__main__":
    diagnosticar_importacoes()
