"""
Система кэширования для оптимизации производительности
"""
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps


class CacheManager:
    """Менеджер кэша с TTL (Time To Live)"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 300  # 5 минут по умолчанию
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        if key not in self._cache:
            return None
        
        cache_entry = self._cache[key]
        if time.time() > cache_entry['expires_at']:
            # Кэш истек
            del self._cache[key]
            return None
        
        return cache_entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кэш"""
        if ttl is None:
            ttl = self._default_ttl
        
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
    
    def invalidate(self, key: str) -> None:
        """Удалить значение из кэша"""
        if key in self._cache:
            del self._cache[key]
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Удалить все ключи, содержащие паттерн"""
        keys_to_remove = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кэша"""
        current_time = time.time()
        active_entries = 0
        expired_entries = 0
        
        for entry in self._cache.values():
            if current_time > entry['expires_at']:
                expired_entries += 1
            else:
                active_entries += 1
        
        return {
            'total_entries': len(self._cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'memory_usage': sum(len(str(entry['value'])) for entry in self._cache.values())
        }


# Глобальный экземпляр кэша
cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Декоратор для кэширования результатов функций
    
    Args:
        ttl: Время жизни кэша в секундах
        key_prefix: Префикс для ключа кэша
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Создаем ключ кэша на основе функции и аргументов
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str = None, key: str = None):
    """
    Инвалидировать кэш
    
    Args:
        pattern: Паттерн для удаления (например, "portfolio_*")
        key: Конкретный ключ для удаления
    """
    if key:
        cache_manager.invalidate(key)
    elif pattern:
        cache_manager.invalidate_pattern(pattern)
    else:
        cache_manager.clear()


# Специальные функции для кэширования данных портфеля
def cache_portfolio_stats(stats: Dict[str, Any]) -> None:
    """Кэшировать статистику портфеля"""
    cache_manager.set("portfolio_stats", stats, ttl=60)  # 1 минута


def get_cached_portfolio_stats() -> Optional[Dict[str, Any]]:
    """Получить кэшированную статистику портфеля"""
    return cache_manager.get("portfolio_stats")


def cache_transactions(transactions: list, limit: int = None) -> None:
    """Кэшировать список сделок"""
    key = f"transactions_{limit}" if limit else "transactions_all"
    cache_manager.set(key, transactions, ttl=120)  # 2 минуты


def get_cached_transactions(limit: int = None) -> Optional[list]:
    """Получить кэшированный список сделок"""
    key = f"transactions_{limit}" if limit else "transactions_all"
    return cache_manager.get(key)


def cache_sources(sources: list) -> None:
    """Кэшировать список источников"""
    cache_manager.set("sources", sources, ttl=600)  # 10 минут


def get_cached_sources() -> Optional[list]:
    """Получить кэшированный список источников"""
    return cache_manager.get("sources")


def cache_price_alerts(alerts: list) -> None:
    """Кэшировать список алертов"""
    cache_manager.set("price_alerts", alerts, ttl=60)  # 1 минута


def get_cached_price_alerts() -> Optional[list]:
    """Получить кэшированный список алертов"""
    return cache_manager.get("price_alerts")


# Функция для очистки кэша при изменении данных
def invalidate_data_cache():
    """Очистить кэш данных при изменении"""
    cache_manager.invalidate_pattern("portfolio_*")
    cache_manager.invalidate_pattern("transactions_*")
    cache_manager.invalidate("sources")
    cache_manager.invalidate("price_alerts")
