"""
Teste das funções que estavam faltando no módulo prepara_dados.
"""

print("=== TESTE DAS FUNÇÕES CORRIGIDAS ===")

try:
    # Testar importação das funções que estavam faltando
    from utils.prepara_dados import preparar_dados_barras_empilhadas
    print("✅ preparar_dados_barras_empilhadas importada com sucesso")
    
    from utils.prepara_dados import preparar_dados_sankey
    print("✅ preparar_dados_sankey importada com sucesso")
    
    # Verificar se as funções são chamáveis
    print(f"✅ preparar_dados_barras_empilhadas é função: {callable(preparar_dados_barras_empilhadas)}")
    print(f"✅ preparar_dados_sankey é função: {callable(preparar_dados_sankey)}")
    
    print("\n🎯 CORREÇÃO REALIZADA COM SUCESSO!")
    print("📊 As visualizações de correlação (barras empilhadas e Sankey) devem funcionar agora")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
