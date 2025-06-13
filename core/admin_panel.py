"""
Painel de administração avançado para o Dashboard.
Fornece ferramentas de debug, monitoramento e configuração.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .performance_monitor import performance_monitor
from .cache_manager import cache_manager
from .error_handler import error_handler
from .data_manager import data_manager
from .config import PERFORMANCE_CONFIG, SECURITY_CONFIG, UI_CONFIG


class AdminPanel:
    """Painel de administração para o Dashboard."""
    
    def __init__(self):
        """Inicializa o painel."""
        self.enabled = False
    
    def show_admin_panel(self) -> None:
        """Exibe o painel de administração na sidebar."""
        if not st.sidebar.checkbox("🔧 Painel Admin", value=False):
            return
        
        self.enabled = True
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠️ Administração")
        
        # Abas do painel admin
        admin_tab = st.sidebar.radio(
            "Seção:",
            ["Performance", "Cache", "Erros", "Configurações", "Sistema"],
            key="admin_tab"
        )
        
        if admin_tab == "Performance":
            self._show_performance_panel()
        elif admin_tab == "Cache":
            self._show_cache_panel()
        elif admin_tab == "Erros":
            self._show_error_panel()
        elif admin_tab == "Configurações":
            self._show_config_panel()
        elif admin_tab == "Sistema":
            self._show_system_panel()
    
    def _show_performance_panel(self) -> None:
        """Exibe painel de performance."""
        st.sidebar.markdown("### 📊 Performance")
        
        # Resumo de performance
        perf_summary = performance_monitor.get_performance_summary()
        
        # Métricas principais
        st.sidebar.metric(
            "Duração da Sessão",
            f"{perf_summary.get('session_duration_minutes', 0):.1f} min"
        )
        
        st.sidebar.metric(
            "Uso de Memória",
            f"{perf_summary.get('avg_memory_usage_mb', 0):.0f} MB"
        )
        
        st.sidebar.metric(
            "Taxa de Cache",
            f"{perf_summary.get('cache_hit_rate_percent', 0):.1f}%"
        )
        
        # Saúde do sistema
        health = performance_monitor.get_health_status()
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '🚨'
        }
        
        st.sidebar.write(f"{status_emoji.get(health['status'], '❓')} Status: {health['status']}")
        
        if health['alerts']:
            st.sidebar.warning(f"Alertas: {', '.join(health['alerts'])}")
        
        # Botões de ação
        if st.sidebar.button("📈 Ver Detalhes", key="perf_details"):
            self._show_detailed_performance()
        
        if st.sidebar.button("🔄 Resetar Métricas", key="reset_metrics"):
            performance_monitor.reset_metrics()
            st.sidebar.success("Métricas resetadas!")
    
    def _show_cache_panel(self) -> None:
        """Exibe painel de cache."""
        st.sidebar.markdown("### 💾 Cache")
        
        # Estatísticas do cache
        cache_stats = cache_manager.get_performance_stats()
        
        st.sidebar.metric(
            "Hit Rate",
            f"{cache_stats.get('hit_rate_percent', 0):.1f}%"
        )
        
        memory_stats = cache_stats.get('memory_stats', {})
        st.sidebar.metric(
            "Uso do Cache",
            f"{memory_stats.get('size_mb', 0):.1f} MB"
        )
        
        st.sidebar.metric(
            "Items Cached",
            memory_stats.get('items_count', 0)
        )
        
        # Botões de ação
        if st.sidebar.button("🗑️ Limpar Cache", key="clear_cache"):
            cache_manager.clear_cache()
            data_manager.clear_cache()
            st.sidebar.success("Cache limpo!")
        
        if st.sidebar.button("📋 Ver Items", key="cache_items"):
            self._show_cache_items(memory_stats)
    
    def _show_error_panel(self) -> None:
        """Exibe painel de erros."""
        st.sidebar.markdown("### 🚨 Erros")
        
        # Resumo de erros
        error_summary = error_handler.get_error_summary()
        
        st.sidebar.metric(
            "Total de Erros",
            error_summary.get('total_errors', 0)
        )
        
        # Últimos erros
        recent_errors = error_summary.get('recent_errors', [])
        if recent_errors:
            st.sidebar.write("**Últimos erros:**")
            for i, error in enumerate(recent_errors[-3:]):  # Últimos 3
                st.sidebar.write(f"{i+1}. {error[:50]}...")
        
        # Botões de ação
        if st.sidebar.button("📋 Ver Todos", key="all_errors"):
            self._show_all_errors(error_summary)
        
        if st.sidebar.button("🧹 Limpar Log", key="clear_errors"):
            error_handler.reset_error_tracking()
            st.sidebar.success("Log de erros limpo!")
    
    def _show_config_panel(self) -> None:
        """Exibe painel de configurações."""
        st.sidebar.markdown("### ⚙️ Configurações")
        
        # Configurações editáveis
        st.sidebar.write("**Performance:**")
        
        new_cache_enabled = st.sidebar.checkbox(
            "Cache Habilitado",
            value=PERFORMANCE_CONFIG.ENABLE_CACHE,
            key="config_cache"
        )
        
        new_gc_enabled = st.sidebar.checkbox(
            "GC Automático",
            value=PERFORMANCE_CONFIG.FORCE_GC_AFTER_TAB,
            key="config_gc"
        )
        
        new_lazy_loading = st.sidebar.checkbox(
            "Lazy Loading",
            value=PERFORMANCE_CONFIG.LAZY_LOADING,
            key="config_lazy"
        )
        
        # Aplicar configurações (simulado)
        if st.sidebar.button("💾 Aplicar", key="apply_config"):
            st.sidebar.info("Configurações aplicadas para esta sessão")
    
    def _show_system_panel(self) -> None:
        """Exibe painel do sistema."""
        st.sidebar.markdown("### 🖥️ Sistema")
        
        # Informações do sistema
        memory_info = data_manager.get_memory_info()
        
        if 'error' not in memory_info:
            st.sidebar.metric(
                "Memória Total",
                f"{memory_info.get('system_memory_gb', 0):.1f} GB"
            )
            
            st.sidebar.metric(
                "Memória Usada",
                f"{memory_info.get('used_memory_gb', 0):.1f} GB"
            )
            
            st.sidebar.metric(
                "Uso %",
                f"{memory_info.get('memory_percent', 0):.1f}%"
            )
        else:
            st.sidebar.warning(memory_info['error'])
        
        # Informações da aplicação
        st.sidebar.write("**Aplicação:**")
        st.sidebar.write(f"Versão: {UI_CONFIG.VERSION}")
        st.sidebar.write(f"Última atualização: {UI_CONFIG.LAST_UPDATE}")
        
        # Botões de sistema
        if st.sidebar.button("🧹 Limpeza Geral", key="full_cleanup"):
            self._perform_full_cleanup()
        
        if st.sidebar.button("📊 Relatório Completo", key="full_report"):
            self._generate_full_report()
    
    def _show_detailed_performance(self) -> None:
        """Exibe performance detalhada no main area."""
        if not self.enabled:
            return
        
        st.subheader("📊 Análise Detalhada de Performance")
        
        # Métricas detalhadas
        detailed_metrics = performance_monitor.get_detailed_metrics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Tempos de Renderização (ms):**")
            render_times = detailed_metrics.get('render_times', {})
            for tab, times in render_times.items():
                if times:
                    avg_time = sum(times) / len(times) * 1000
                    st.write(f"- {tab}: {avg_time:.1f}ms")
        
        with col2:
            st.write("**Uso de Memória (MB):**")
            memory_usage = detailed_metrics.get('memory_usage', [])
            if memory_usage:
                st.line_chart(memory_usage[-20:])  # Últimos 20 pontos
        
        # Cache stats
        st.write("**Estatísticas de Cache:**")
        cache_stats = detailed_metrics.get('cache_stats', {})
        st.json(cache_stats)
    
    def _show_cache_items(self, memory_stats: Dict[str, Any]) -> None:
        """Exibe items do cache."""
        if not self.enabled:
            return
        
        st.subheader("💾 Items no Cache")
        
        cache_keys = memory_stats.get('keys', [])
        if cache_keys:
            st.write(f"Total de items: {len(cache_keys)}")
            
            for i, key in enumerate(cache_keys):
                st.write(f"{i+1}. {key}")
        else:
            st.info("Cache vazio")
    
    def _show_all_errors(self, error_summary: Dict[str, Any]) -> None:
        """Exibe todos os erros."""
        if not self.enabled:
            return
        
        st.subheader("🚨 Log de Erros")
        
        all_errors = error_summary.get('all_errors', [])
        if all_errors:
            for i, error in enumerate(all_errors):
                with st.expander(f"Erro {i+1}"):
                    st.code(error)
        else:
            st.info("Nenhum erro registrado")
    
    def _perform_full_cleanup(self) -> None:
        """Executa limpeza completa do sistema."""
        try:
            # Limpar caches
            cache_manager.clear_cache()
            data_manager.clear_cache()
            
            # Forçar garbage collection
            collected = performance_monitor.force_gc_and_record()
            
            # Resetar métricas
            performance_monitor.reset_metrics()
            error_handler.reset_error_tracking()
            
            st.sidebar.success(f"✅ Limpeza concluída! {collected} objetos removidos.")
            
        except Exception as e:
            st.sidebar.error(f"Erro na limpeza: {e}")
    
    def _generate_full_report(self) -> None:
        """Gera relatório completo do sistema."""
        if not self.enabled:
            return
        
        st.subheader("📋 Relatório Completo do Sistema")
        
        # Coletar todas as informações
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance': performance_monitor.get_detailed_metrics(),
            'cache': cache_manager.get_performance_stats(),
            'errors': error_handler.get_error_summary(),
            'memory': data_manager.get_memory_info(),
            'config': {
                'performance': {
                    'enable_cache': PERFORMANCE_CONFIG.ENABLE_CACHE,
                    'lazy_loading': PERFORMANCE_CONFIG.LAZY_LOADING,
                    'force_gc': PERFORMANCE_CONFIG.FORCE_GC_AFTER_TAB,
                },
                'security': {
                    'validate_inputs': SECURITY_CONFIG.VALIDATE_INPUTS,
                    'max_states': SECURITY_CONFIG.MAX_STATES_SELECTION,
                }
            }
        }
        
        # Exibir relatório
        st.json(report)
        
        # Botão para download
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Baixar Relatório",
            data=report_json,
            file_name=f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


# Instância global
admin_panel = AdminPanel()
