# Sistema de Limpeza de Memória e Navegação - ENEM Dashboard

## 📋 Resumo das Melhorias Implementadas

### 🎯 Problema Identificado
O dashboard estava apresentando problemas de memória no deploy do Streamlit Cloud devido a:
- Falta de limpeza automática de cache ao trocar páginas
- Acúmulo de dados no session_state
- Ausência de monitoramento de uso de memória
- Falta de tratamento de erros em operações de limpeza

### ✅ Soluções Implementadas

#### 1. Sistema de Navegação Inteligente (`utils/page_utils.py`)

**Classe PageManager:**
- Registra automaticamente mudanças de página
- Executa limpeza automática ao trocar de página
- Mantém histórico de navegação
- Tratamento robusto de erros

**Função safe_page_execution:**
- Wrapper para execução segura de páginas
- Limpeza automática em caso de erro
- Logging detalhado para debug
- Liberação de recursos garantida

#### 2. Sistema de Cache Otimizado (`utils/helpers/cache_utils.py`)

**Funções de Limpeza:**
- `clear_all_cache()`: Limpa caches e session_state seletivamente
- `clear_page_specific_cache()`: Limpeza específica por página
- `deep_cleanup()`: Limpeza profunda com múltiplas coletas de lixo
- `emergency_cleanup()`: Limpeza agressiva para situações críticas

**Monitoramento:**
- `get_memory_usage()`: Monitora uso de memória do sistema
- `monitor_session_state_size()`: Analisa tamanho do session_state
- `check_memory_and_cleanup()`: Verificação automática e limpeza inteligente

#### 3. Melhorias nas Páginas

**Todas as páginas agora:**
- Usam `safe_page_execution()` para execução segura
- Implementam verificação de memória antes de carregar dados
- Liberam explicitamente objetos grandes após uso
- Tratam erros graciosamente com fallbacks

#### 4. Configurações por Tipo de Página

**PAGE_CONFIGS:**
- Dashboard: Cache de 1 hora, até 10 entradas
- Analysis: Cache de 30 minutos, até 5 entradas  
- Visualization: Cache de 15 minutos, até 3 entradas

### 🔧 Como Funciona

#### Fluxo de Navegação:
1. Usuário acessa uma página
2. `safe_page_execution()` registra a navegação
3. Se houve mudança de página, `PageManager` executa limpeza
4. Página carrega dados com verificação de memória
5. Objetos são explicitamente liberados após uso

#### Estratégia de Limpeza:
1. **Limpeza Específica**: Remove cache da página anterior
2. **Verificação Automática**: Checa uso de memória e session_state
3. **Limpeza Inteligente**: 
   - Normal: < 80% memória
   - Profunda: 80-90% memória
   - Emergência: > 90% memória

### 📊 Monitoramento

#### Logs Importantes:
- `[PAGE_MANAGER]`: Eventos de navegação e limpeza
- `[CACHE_UTILS]`: Operações de cache e memória
- `[DEEP_CLEANUP]`: Limpezas profundas
- `[EMERGENCY_CLEANUP]`: Limpezas de emergência

#### Métricas Monitoradas:
- Uso de memória do sistema (%)
- Tamanho do session_state (MB)
- Número de objetos em cache
- Tempo de limpeza

### 🚀 Para Produção

#### Configurações Recomendadas:
```python
# Em produção, configure:
DEBUG_MODE = False  # Desabilita logs verbosos
MEMORIA_LIMITE_AVISO = 0.7  # Reduz limite para 70%
```

#### Monitoramento:
1. Acompanhe logs `[PAGE_MANAGER]` e `[CACHE_UTILS]`
2. Monitore warnings de memória alta
3. Verifique se limpezas de emergência são frequentes

#### Troubleshooting:
- **Memória alta persistente**: Verifique se dados grandes estão sendo mantidos em session_state
- **Limpezas de emergência frequentes**: Considere reduzir tamanho dos datasets ou aumentar TTL do cache
- **Erros de navegação**: Verifique logs de `[SAFE_PAGE_EXECUTION]`

### 📋 Checklist de Deploy

- ✅ Todas as páginas usam `safe_page_execution()`
- ✅ Limpeza automática funcionando
- ✅ Monitoramento de memória ativo
- ✅ Tratamento de erros implementado
- ✅ Logs de debug configurados
- ✅ Session state sendo limpo seletivamente
- ✅ Cache com TTL apropriado
- ✅ Objetos grandes liberados explicitamente

### 🔍 Comandos de Teste

```bash
# Testar importações
python -c "from utils.page_utils import safe_page_execution; from utils.helpers.cache_utils import deep_cleanup; print('OK')"

# Testar limpeza de memória
python -c "from utils.helpers.cache_utils import check_memory_and_cleanup; check_memory_and_cleanup()"

# Executar dashboard
streamlit run Dashboard.py
```

### 💡 Próximos Passos

1. **Monitoramento em Produção**: Implementar alertas para uso de memória > 85%
2. **Otimização de Dados**: Considerar lazy loading para datasets muito grandes
3. **Cache Persistente**: Avaliar uso de Redis para cache externo
4. **Métricas Detalhadas**: Implementar dashboard de monitoramento de performance

---

## 🏗️ Arquitetura Técnica

### Diagrama de Fluxo:
```
Usuário → Página → safe_page_execution() → register_page_navigation() 
                     ↓
                 PageManager.cleanup_previous_page()
                     ↓
                 check_memory_and_cleanup()
                     ↓
        [Normal/Deep/Emergency] cleanup → release_memory()
```

### Responsabilidades:
- **PageManager**: Coordena navegação e limpeza
- **cache_utils**: Executa limpezas e monitora memória  
- **safe_page_execution**: Garante execução segura
- **Páginas**: Liberam recursos explicitamente

Esta implementação garante que o dashboard seja resiliente a problemas de memória e funcione adequadamente no ambiente restrito do Streamlit Cloud.
