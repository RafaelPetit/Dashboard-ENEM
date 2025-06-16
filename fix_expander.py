"""
Script para corrigir a formatação de valores no expander_geral.py
"""

import re

def corrigir_formatacao_expander():
    """Corrige a formatação de valores no arquivo expander_geral.py"""
    
    with open('utils/expander/expander_geral.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir formatações problemáticas
    content = content.replace(
        'st.write(f"- **Percentil {p}:** {valor:.2f}")',
        'st.write(f"- **Percentil {p}:** {safe_format(valor, 2)}")'
    )
    
    # Substituir valores nos quartis
    content = content.replace(
        'percentis.get(25, 0),',
        'safe_format(percentis.get(25, 0), 2),'
    )
    content = content.replace(
        'percentis.get(50, 0),',
        'safe_format(percentis.get(50, 0), 2),'
    )
    content = content.replace(
        'percentis.get(75, 0)',
        'safe_format(percentis.get(75, 0), 2)'
    )
    
    with open('utils/expander/expander_geral.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Arquivo expander_geral.py corrigido com sucesso!")

if __name__ == "__main__":
    corrigir_formatacao_expander()
