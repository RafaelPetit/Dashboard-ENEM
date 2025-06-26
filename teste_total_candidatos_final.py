#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final da correção do total de candidatos no histograma
Verifica se o valor 2.628.593 está sendo exibido corretamente.
"""

import pandas as pd
from pages.analise_geral import get_all_data_geral
from utils.estatisticas.analise_geral import analisar_distribuicao_notas
from utils.visualizacao.graficos_geral import criar_histograma

def teste_total_candidatos_final():
    """Teste final do total de candidatos"""
    
    print("=" * 60)
    print("TESTE FINAL: TOTAL DE CANDIDATOS NO HISTOGRAMA")
    print("=" * 60)
    
    try:
        # 1. Carregar dados completos
        print("1. Carregando dados completos...")
        dados_completos = get_all_data_geral()
        total_real = len(dados_completos)
        print(f"   ✅ Total real no dataset: {total_real:,}")
        
        # 2. Testar análise de distribuição
        print("\n2. Testando análise de distribuição...")
        coluna_teste = 'NU_NOTA_CN'  # Ciências da Natureza
        
        if coluna_teste in dados_completos.columns:
            estatisticas = analisar_distribuicao_notas(dados_completos, coluna_teste)
            
            total_candidatos = estatisticas.get('total_candidatos', 0)
            total_validos = estatisticas.get('total_valido', 0)
            total_invalidos = estatisticas.get('total_invalido', 0)
            
            print(f"   ✅ Total candidatos nas estatísticas: {total_candidatos:,}")
            print(f"   ✅ Total com notas válidas: {total_validos:,}")
            print(f"   ✅ Total sem notas válidas: {total_invalidos:,}")
            
            # 3. Verificar se soma está correta
            print("\n3. Verificando integridade dos dados...")
            soma_verificacao = total_validos + total_invalidos
            
            if soma_verificacao == total_candidatos == total_real:
                print(f"   ✅ SUCESSO: Soma correta ({total_validos:,} + {total_invalidos:,} = {soma_verificacao:,})")
            else:
                print(f"   ❌ ERRO: Soma incorreta")
                print(f"      Esperado: {total_real:,}")
                print(f"      Calculado: {soma_verificacao:,}")
                
            # 4. Testar criação do histograma
            print("\n4. Testando criação do histograma...")
            
            # Filtrar apenas dados válidos para o histograma
            dados_validos = dados_completos[dados_completos[coluna_teste] > 0]
            
            fig = criar_histograma(
                dados_validos,
                coluna_teste,
                "Ciências da Natureza",
                estatisticas
            )
            
            print(f"   ✅ Histograma criado com sucesso")
            print(f"   ✅ Dados para visualização: {len(dados_validos):,} registros")
            print(f"   ✅ Total exibido na legenda: {total_candidatos:,} candidatos")
            
            # 5. Resultado final
            print("\n" + "=" * 60)
            print("RESULTADO FINAL:")
            print("=" * 60)
            
            if total_candidatos == 2628593:
                print("🎉 SUCESSO TOTAL! 🎉")
                print("✅ O histograma agora mostra o total correto de candidatos:")
                print(f"   📊 Total de Candidatos: {total_candidatos:,}")
                print("✅ Incluindo candidatos ausentes (sem notas)")
                print("✅ A correção está funcionando perfeitamente!")
            else:
                print("❌ PROBLEMA AINDA EXISTE")
                print(f"   Valor mostrado: {total_candidatos:,}")
                print(f"   Valor esperado: 2,628,593")
                
        else:
            print(f"   ❌ Coluna {coluna_teste} não encontrada")
            print(f"   Colunas disponíveis: {list(dados_completos.columns)[:10]}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_total_candidatos_final()
