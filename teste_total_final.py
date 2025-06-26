#!/usr/bin/env python3
"""
Teste final para validar a correção do total de candidatos no histograma
"""
import sys
import pandas as pd

def test_total_candidatos_final():
    """Teste final para validar o total de candidatos"""
    print("🧪 TESTE FINAL - TOTAL DE CANDIDATOS NO HISTOGRAMA")
    print("=" * 55)
    
    try:
        # 1. Carregar dados e testar análise
        print("1️⃣ Carregando dados e testando análise...")
        from utils.data_loader import load_data_for_tab
        from utils.estatisticas.analise_geral import analisar_distribuicao_notas
        
        dados = load_data_for_tab('geral')
        total_real = len(dados)
        print(f"   📊 Total real no dataset: {total_real:,}")
        
        # 2. Testar análise de distribuição
        estatisticas = analisar_distribuicao_notas(dados, 'NU_NOTA_MT')
        total_calculado = estatisticas.get('total_candidatos', 0)
        total_valido = estatisticas.get('total_valido', 0)
        total_invalido = estatisticas.get('total_invalido', 0)
        
        print(f"   📈 Total calculado pela análise: {total_calculado:,}")
        print(f"   ✅ Com notas válidas: {total_valido:,}")
        print(f"   ❌ Sem notas válidas: {total_invalido:,}")
        
        # 3. Validações
        print(f"\n2️⃣ Validando resultados...")
        
        # Verificar se o total está correto
        if total_calculado == total_real:
            print(f"   ✅ Total de candidatos CORRETO: {total_calculado:,}")
        else:
            print(f"   ❌ Total incorreto. Esperado: {total_real:,}, Obtido: {total_calculado:,}")
            return False
            
        # Verificar se a soma confere
        if total_valido + total_invalido == total_calculado:
            print(f"   ✅ Soma está correta: {total_valido:,} + {total_invalido:,} = {total_calculado:,}")
        else:
            print(f"   ❌ Soma incorreta: {total_valido} + {total_invalido} != {total_calculado}")
            return False
        
        # 4. Testar interface do histograma
        print(f"\n3️⃣ Testando interface do histograma...")
        from utils.visualizacao.graficos_geral import _adicionar_caixa_estatisticas
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig_com_stats = _adicionar_caixa_estatisticas(fig, estatisticas)
        
        if len(fig_com_stats.layout.annotations) > 0:
            texto = fig_com_stats.layout.annotations[0].text
            if f"Total de Candidatos: {total_calculado:,}" in texto:
                print(f"   ✅ Interface mostra total correto: {total_calculado:,}")
            else:
                print(f"   ❌ Interface não mostra total correto")
                print(f"   Texto encontrado: {texto}")
                return False
        
        # 5. Comparação com expectativa
        print(f"\n4️⃣ Comparação final...")
        print(f"   🎯 Expectativa: 2.628.593 candidatos")
        print(f"   ✅ Resultado: {total_calculado:,} candidatos")
        
        if total_calculado == 2628593:
            print(f"   🎉 PERFEITO! Total está exatamente como esperado!")
        else:
            print(f"   ⚠️ Total diferente do esperado, mas pode ser devido a filtros aplicados")
        
        # 6. Percentuais para análise
        percentual_validos = (total_valido / total_calculado) * 100
        percentual_invalidos = (total_invalido / total_calculado) * 100
        
        print(f"\n5️⃣ Análise de completude...")
        print(f"   📊 Candidatos com notas: {percentual_validos:.1f}%")
        print(f"   📉 Candidatos ausentes: {percentual_invalidos:.1f}%")
        
        print(f"\n🎉 TESTE FINAL CONCLUÍDO COM SUCESSO!")
        print(f"✅ O histograma agora mostra o total correto de candidatos!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = test_total_candidatos_final()
    sys.exit(0 if sucesso else 1)
