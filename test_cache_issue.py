#!/usr/bin/env python3
"""
Teste para identificar e resolver o problema de cache do Streamlit.
"""

import streamlit as st
import pandas as pd
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import_geral():
    """Testa importação da aba geral."""
    try:
        from tabs.geral import render_geral
        print("✓ Importação da aba geral bem-sucedida")
        return True
    except Exception as e:
        print(f"✗ Erro na importação da aba geral: {e}")
        return False

def test_import_cache_utils():
    """Testa importação do cache utils."""
    try:
        from utils.helpers.cache_utils import optimized_cache, release_memory
        print("✓ Importação do cache_utils bem-sucedida")
        return True
    except Exception as e:
        print(f"✗ Erro na importação do cache_utils: {e}")
        return False

def test_import_prepara_dados():
    """Testa importação das funções de preparação de dados."""
    try:
        from utils.prepara_dados import (
            preparar_dados_histograma,
            preparar_dados_grafico_faltas,
            preparar_dados_media_geral_estados,
            preparar_dados_comparativo_areas,
            preparar_dados_evasao
        )
        print("✓ Importação das funções de preparação de dados bem-sucedida")
        return True
    except Exception as e:
        print(f"✗ Erro na importação das funções de preparação: {e}")
        return False

def test_simple_cache_function():
    """Testa uma função simples com cache."""
    try:
        @st.cache_data
        def simple_test_function(x: int) -> int:
            return x * 2
        
        result = simple_test_function(5)
        print(f"✓ Função simples com cache funcionou: {result}")
        return True
    except Exception as e:
        print(f"✗ Erro na função simples com cache: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste de Identificação do Problema de Cache ===")
    
    tests = [
        test_import_cache_utils,
        test_import_prepara_dados,
        test_import_geral,
        test_simple_cache_function
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"=== Resumo dos Testes ===")
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("✓ Todos os testes passaram! Problema de cache pode estar na execução do Streamlit.")
    else:
        print("✗ Alguns testes falharam. Verificar erros acima.")
