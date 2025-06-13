"""
Sistema de métricas e monitoramento para o Dashboard.
Coleta estatísticas de uso, performance e detecção de problemas.
"""

import time
import psutil
import gc
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque

from .config import PERFORMANCE_CONFIG
from .core_types import DataFrameType


@dataclass
class PerformanceMetrics:
    """Métricas de performance coletadas."""
    
    # Timing
    render_times: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    load_times: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    filter_times: List[float] = field(default_factory=list)
    
    # Memory
    memory_usage: List[float] = field(default_factory=list)
    memory_peaks: List[float] = field(default_factory=list)
    gc_collections: int = 0
    
    # Cache
    cache_hits: int = 0
    cache_misses: int = 0
    cache_evictions: int = 0
    
    # User interactions
    tab_switches: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    filter_changes: int = 0
    error_count: int = 0
    
    # Session info
    session_start: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """Monitor de performance para o Dashboard."""
    
    def __init__(self, max_history: int = 1000):
        """
        Inicializa o monitor.
        
        Args:
            max_history: Máximo de entradas no histórico
        """
        self.metrics = PerformanceMetrics()
        self.max_history = max_history
        self._timers: Dict[str, float] = {}
        self._memory_baseline = psutil.virtual_memory().used
        
        # Histórico recente para análise de tendências
        self._recent_render_times = deque(maxlen=50)
        self._recent_memory_usage = deque(maxlen=100)
    
    def start_timer(self, operation: str) -> None:
        """Inicia timer para uma operação."""
        self._timers[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """
        Finaliza timer e registra tempo.
        
        Args:
            operation: Nome da operação
            
        Returns:
            Tempo decorrido em segundos
        """
        if operation not in self._timers:
            return 0.0
        
        elapsed = time.time() - self._timers[operation]
        del self._timers[operation]
        
        # Registrar tempo baseado no tipo de operação
        if 'render' in operation.lower():
            tab_name = operation.replace('render_', '').replace('_tab', '')
            self.metrics.render_times[tab_name].append(elapsed)
            self._recent_render_times.append(elapsed)
        elif 'load' in operation.lower():
            self.metrics.load_times[operation].append(elapsed)
        elif 'filter' in operation.lower():
            self.metrics.filter_times.append(elapsed)
        
        # Manter histórico limitado
        self._limit_history()
        
        return elapsed
    
    def record_memory_usage(self) -> float:
        """
        Registra uso atual de memória.
        
        Returns:
            Uso de memória em MB
        """
        current_memory = psutil.virtual_memory().used
        memory_mb = current_memory / (1024 * 1024)
        
        self.metrics.memory_usage.append(memory_mb)
        self._recent_memory_usage.append(memory_mb)
        
        # Detectar picos de memória
        if len(self.metrics.memory_usage) > 1:
            previous = self.metrics.memory_usage[-2]
            if memory_mb > previous * 1.2:  # 20% de aumento
                self.metrics.memory_peaks.append(memory_mb)
        
        self._limit_history()
        return memory_mb
    
    def record_tab_switch(self, tab_name: str) -> None:
        """Registra mudança de aba."""
        self.metrics.tab_switches[tab_name] += 1
        self.metrics.last_activity = datetime.now()
    
    def record_filter_change(self) -> None:
        """Registra mudança nos filtros."""
        self.metrics.filter_changes += 1
        self.metrics.last_activity = datetime.now()
    
    def record_cache_hit(self) -> None:
        """Registra hit no cache."""
        self.metrics.cache_hits += 1
    
    def record_cache_miss(self) -> None:
        """Registra miss no cache."""
        self.metrics.cache_misses += 1
    
    def record_error(self) -> None:
        """Registra ocorrência de erro."""
        self.metrics.error_count += 1
    
    def force_gc_and_record(self) -> int:
        """
        Força garbage collection e registra.
        
        Returns:
            Número de objetos coletados
        """
        collected = gc.collect()
        self.metrics.gc_collections += 1
        return collected
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo de performance.
        
        Returns:
            Dicionário com métricas principais
        """
        now = datetime.now()
        session_duration = now - self.metrics.session_start
        
        # Calcular médias
        avg_render_times = {}
        for tab, times in self.metrics.render_times.items():
            if times:
                avg_render_times[tab] = sum(times) / len(times)
        
        avg_memory = sum(self.metrics.memory_usage) / len(self.metrics.memory_usage) if self.metrics.memory_usage else 0
        
        # Cache hit rate
        total_cache_requests = self.metrics.cache_hits + self.metrics.cache_misses
        cache_hit_rate = (self.metrics.cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        return {
            'session_duration_minutes': session_duration.total_seconds() / 60,
            'avg_render_times_ms': {tab: time * 1000 for tab, time in avg_render_times.items()},
            'avg_memory_usage_mb': avg_memory,
            'peak_memory_mb': max(self.metrics.memory_usage) if self.metrics.memory_usage else 0,
            'cache_hit_rate_percent': cache_hit_rate,
            'total_tab_switches': sum(self.metrics.tab_switches.values()),
            'total_filter_changes': self.metrics.filter_changes,
            'total_errors': self.metrics.error_count,
            'gc_collections': self.metrics.gc_collections
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Avalia saúde do sistema.
        
        Returns:
            Status de saúde e alertas
        """
        alerts = []
        status = "healthy"
        
        # Verificar memória
        if self.metrics.memory_usage:
            current_memory = self.metrics.memory_usage[-1]
            if current_memory > 1000:  # > 1GB
                alerts.append("Alto uso de memória")
                status = "warning"
            
            if len(self.metrics.memory_peaks) > 5:
                alerts.append("Muitos picos de memória detectados")
                status = "warning"
        
        # Verificar performance de renderização
        if self._recent_render_times:
            avg_render = sum(self._recent_render_times) / len(self._recent_render_times)
            if avg_render > 5.0:  # > 5 segundos
                alerts.append("Renderização lenta detectada")
                status = "warning"
        
        # Verificar cache
        total_requests = self.metrics.cache_hits + self.metrics.cache_misses
        if total_requests > 20:
            hit_rate = self.metrics.cache_hits / total_requests
            if hit_rate < 0.3:  # < 30%
                alerts.append("Taxa de cache baixa")
                status = "warning"
        
        # Verificar erros
        if self.metrics.error_count > 10:
            alerts.append("Muitos erros detectados")
            status = "critical"
        
        return {
            'status': status,
            'alerts': alerts,
            'last_check': datetime.now().isoformat()
        }
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Retorna métricas detalhadas para debug."""
        return {
            'render_times': dict(self.metrics.render_times),
            'load_times': dict(self.metrics.load_times),
            'filter_times': self.metrics.filter_times[-10:],  # Últimos 10
            'memory_usage': self.metrics.memory_usage[-20:],  # Últimos 20
            'tab_switches': dict(self.metrics.tab_switches),
            'cache_stats': {
                'hits': self.metrics.cache_hits,
                'misses': self.metrics.cache_misses,
                'evictions': self.metrics.cache_evictions
            },
            'session_info': {
                'start': self.metrics.session_start.isoformat(),
                'last_activity': self.metrics.last_activity.isoformat(),
                'total_errors': self.metrics.error_count
            }
        }
    
    def reset_metrics(self) -> None:
        """Reseta todas as métricas."""
        self.metrics = PerformanceMetrics()
        self._recent_render_times.clear()
        self._recent_memory_usage.clear()
    
    def _limit_history(self) -> None:
        """Limita tamanho do histórico para evitar vazamentos de memória."""
        # Limitar listas de tempo
        for tab_times in self.metrics.render_times.values():
            if len(tab_times) > self.max_history:
                tab_times[:] = tab_times[-self.max_history:]
        
        for load_times in self.metrics.load_times.values():
            if len(load_times) > self.max_history:
                load_times[:] = load_times[-self.max_history:]
        
        # Limitar outras listas
        if len(self.metrics.filter_times) > self.max_history:
            self.metrics.filter_times = self.metrics.filter_times[-self.max_history:]
        
        if len(self.metrics.memory_usage) > self.max_history:
            self.metrics.memory_usage = self.metrics.memory_usage[-self.max_history:]


class ContextTimer:
    """Context manager para timing automático."""
    
    def __init__(self, monitor: PerformanceMonitor, operation: str):
        """
        Inicializa timer de contexto.
        
        Args:
            monitor: Monitor de performance
            operation: Nome da operação
        """
        self.monitor = monitor
        self.operation = operation
    
    def __enter__(self):
        self.monitor.start_timer(self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.monitor.end_timer(self.operation)


# Instância global
performance_monitor = PerformanceMonitor()


# Decorador para timing automático
def timed_operation(operation_name: str):
    """
    Decorador para timing automático de funções.
    
    Args:
        operation_name: Nome da operação para métricas
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with ContextTimer(performance_monitor, operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
