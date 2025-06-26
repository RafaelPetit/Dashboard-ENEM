#!/usr/bin/env python3
"""
Teste para validar as mudanças na legenda do histograma
"""
import sys
import pandas as pd

def test_histograma_changes():
    """Testa as mudanças na legenda do histograma"""
    print("🧪 TESTANDO MUDANÇAS NA LEGENDA DO HISTOGRAMA")
    print("=" * 50)
    
    try:
        # 1. Testar importação dos módulos
        print("1️⃣ Testando imports...")
        from utils.estatisticas.analise_geral import analisar_distribuicao_notas
        from utils.visualizacao.graficos_geral import criar_histograma, _adicionar_caixa_estatisticas
        import plotly.graph_objects as go
        print("✅ Imports bem-sucedidos")
        
        # 2. Criar dados de teste
        print("\n2️⃣ Criando dados de teste...")
        df_teste = pd.DataFrame({
            'NU_NOTA_MT': [0, 450, 500, 600, 750, 0, 800, 900, 0, 650]  # Inclui zeros (ausentes)
        })
        
        total_registros = len(df_teste)
        total_com_nota = len(df_teste[df_teste['NU_NOTA_MT'] > 0])
        print(f"   📊 Total de registros: {total_registros}")
        print(f"   📈 Registros com nota válida: {total_com_nota}")
        print(f"   📉 Registros sem nota (ausentes): {total_registros - total_com_nota}")
        
        # 3. Testar análise de distribuição
        print("\n3️⃣ Testando análise de distribuição...")
        estatisticas = analisar_distribuicao_notas(df_teste, 'NU_NOTA_MT')
        
        # Verificar se os campos estão presentes
        campos_obrigatorios = ['total_valido', 'total_candidatos', 'media', 'mediana', 'min_valor', 'max_valor']
        for campo in campos_obrigatorios:
            if campo in estatisticas:
                print(f"   ✅ {campo}: {estatisticas[campo]}")
            else:
                print(f"   ❌ {campo}: AUSENTE")
                return False
        
        # 4. Verificar se total_candidatos está correto
        print("\n4️⃣ Verificando contagem de candidatos...")
        if estatisticas['total_candidatos'] == total_registros:
            print(f"   ✅ Total de candidatos correto: {estatisticas['total_candidatos']}")
        else:
            print(f"   ❌ Total incorreto. Esperado: {total_registros}, Obtido: {estatisticas['total_candidatos']}")
            return False
            
        if estatisticas['total_valido'] == total_com_nota:
            print(f"   ✅ Total com notas válidas correto: {estatisticas['total_valido']}")
        else:
            print(f"   ❌ Total válido incorreto. Esperado: {total_com_nota}, Obtido: {estatisticas['total_valido']}")
            return False
        
        # 5. Testar criação do histograma (simulação)
        print("\n5️⃣ Testando criação de anotação...")
        fig = go.Figure()
        fig_com_stats = _adicionar_caixa_estatisticas(fig, estatisticas)
        
        # Verificar se a anotação foi adicionada
        if len(fig_com_stats.layout.annotations) > 0:
            print("   ✅ Anotação com estatísticas adicionada")
            anotacao = fig_com_stats.layout.annotations[0]
            texto = anotacao.text
            
            # Verificar se contém apenas os campos desejados
            if "Total de Candidatos:" in texto:
                print("   ✅ Campo 'Total de Candidatos' presente")
            else:
                print("   ❌ Campo 'Total de Candidatos' ausente")
                return False
                
            if "Média:" in texto and "Mediana:" in texto:
                print("   ✅ Campos 'Média' e 'Mediana' presentes")
            else:
                print("   ❌ Campos básicos ausentes")
                return False
                
            # Verificar se campos indesejados foram removidos
            campos_removidos = ['Desvio Padrão:', 'Curtose:', 'Assimetria:', 'P25:', 'P50:', 'P75:', 'P90:']
            campos_encontrados = [campo for campo in campos_removidos if campo in texto]
            
            if not campos_encontrados:
                print("   ✅ Campos desnecessários removidos com sucesso")
            else:
                print(f"   ❌ Campos ainda presentes: {campos_encontrados}")
                return False
        else:
            print("   ❌ Nenhuma anotação encontrada")
            return False
        
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Legenda simplificada com sucesso")
        print("✅ Total de candidatos corrigido")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = test_histograma_changes()
    sys.exit(0 if sucesso else 1)
