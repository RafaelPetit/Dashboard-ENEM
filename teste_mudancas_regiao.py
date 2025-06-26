#!/usr/bin/env python3
"""
Teste para validar as mudanças de remoção do Sudeste e otimização do regiao_utils
"""
import sys
import pandas as pd

def test_regiao_changes():
    """Testa as mudanças relacionadas à remoção do Sudeste"""
    print("🧪 TESTANDO MUDANÇAS NA ESTRUTURA DE REGIÕES")
    print("=" * 50)
    
    try:
        # 1. Testar importação dos módulos
        print("1️⃣ Testando imports...")
        from utils.helpers.regiao_utils import REGIOES_BRASIL, agrupar_por_regiao
        from utils.mappings import get_mappings
        print("✅ Imports bem-sucedidos")
        
        # 2. Verificar se Sudeste foi removido
        print("\n2️⃣ Verificando remoção do Sudeste...")
        if 'Sudeste' not in REGIOES_BRASIL:
            print("✅ Sudeste removido de REGIOES_BRASIL")
        else:
            print("❌ Sudeste ainda presente em REGIOES_BRASIL")
            return False
            
        # 3. Verificar mapeamentos
        mappings = get_mappings()
        regioes_mapping = mappings['regioes_mapping']
        
        if 'Sudeste' not in regioes_mapping:
            print("✅ Sudeste removido de regioes_mapping")
        else:
            print("❌ Sudeste ainda presente em regioes_mapping")
            return False
        
        # 4. Verificar estados do Sudeste não estão nos mapeamentos
        estados_sudeste = ['ES', 'MG', 'RJ', 'SP']
        estados_presentes = []
        for regiao, estados in regioes_mapping.items():
            estados_presentes.extend(estados)
            
        sudeste_encontrado = any(estado in estados_presentes for estado in estados_sudeste)
        if not sudeste_encontrado:
            print("✅ Estados do Sudeste removidos dos mapeamentos")
        else:
            print("❌ Alguns estados do Sudeste ainda presentes")
            return False
        
        # 5. Testar nova função agrupar_por_regiao
        print("\n5️⃣ Testando nova função agrupar_por_regiao...")
        
        # Criar um DataFrame de teste com coluna Regiao já existente
        df_teste = pd.DataFrame({
            'Estado': ['AC', 'AM', 'PA'],
            'Regiao': ['Norte', 'Norte', 'Norte'],
            'Média': [500, 520, 510]
        })
        
        resultado = agrupar_por_regiao(df_teste)
        
        if 'Regiao' in resultado.columns:
            print("✅ Função mantém coluna Regiao existente")
        else:
            print("❌ Função não mantém coluna Regiao")
            return False
            
        if len(resultado) == len(df_teste):
            print("✅ DataFrame retornado sem modificações desnecessárias")
        else:
            print("❌ DataFrame foi modificado incorretamente")
            return False
        
        # 6. Listar regiões disponíveis
        print(f"\n6️⃣ Regiões disponíveis: {list(regioes_mapping.keys())}")
        print(f"   Total de estados: {len(estados_presentes)}")
        
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sudeste removido com sucesso")
        print("✅ Função agrupar_por_regiao otimizada")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = test_regiao_changes()
    sys.exit(0 if sucesso else 1)
