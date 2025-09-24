"""
Мониторинг кэша для отладки и оптимизации
"""
from nicegui import ui
from app.core.cache import cache_manager
from app.adapters.prices import get_cache_stats, clean_expired_cache, preload_popular_coins


def create_cache_monitor_tab():
    """Создает вкладку мониторинга кэша"""
    with ui.column().classes("w-full space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto p-4"):
        ui.label("📊 Мониторинг кэша").classes("text-2xl font-bold text-gray-800")
        
        # Кнопки управления кэшем
        with ui.row().classes("gap-3 mb-4"):
            ui.button("🔄 Обновить статистику", icon="refresh").classes("bg-blue-500 text-white").on("click", lambda: refresh_cache_stats())
            ui.button("🗑️ Очистить кэш", icon="delete").classes("bg-red-500 text-white").on("click", lambda: clear_cache())
            ui.button("📈 Статистика производительности", icon="analytics").classes("bg-green-500 text-white").on("click", lambda: show_performance_stats())
            ui.button("🚀 Предзагрузить монеты", icon="rocket_launch").classes("bg-purple-500 text-white").on("click", lambda: preload_coins())
        
        # Статистика кэша
        with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
            ui.label("Статистика кэша").classes("text-lg font-semibold text-gray-800 mb-4")
            
            # Контейнер для статистики
            stats_container = ui.column().classes("w-full")
            
            def refresh_cache_stats():
                """Обновляет статистику кэша"""
                stats_container.clear()
                
                with stats_container:
                    try:
                        stats = cache_manager.get_stats()
                        
                        # Общая статистика
                        with ui.row().classes("w-full gap-4 mb-4"):
                            with ui.card().classes("p-3 bg-blue-50 border-l-4 border-blue-400 flex-1"):
                                ui.label("Всего записей").classes("text-sm text-gray-600")
                                ui.label(str(stats['total_entries'])).classes("text-xl font-bold text-blue-600")
                            
                            with ui.card().classes("p-3 bg-green-50 border-l-4 border-green-400 flex-1"):
                                ui.label("Активных записей").classes("text-sm text-gray-600")
                                ui.label(str(stats['active_entries'])).classes("text-xl font-bold text-green-600")
                            
                            with ui.card().classes("p-3 bg-red-50 border-l-4 border-red-400 flex-1"):
                                ui.label("Истекших записей").classes("text-sm text-gray-600")
                                ui.label(str(stats['expired_entries'])).classes("text-xl font-bold text-red-600")
                            
                            with ui.card().classes("p-3 bg-purple-50 border-l-4 border-purple-400 flex-1"):
                                ui.label("Использование памяти").classes("text-sm text-gray-600")
                                ui.label(f"{stats['memory_usage']} байт").classes("text-xl font-bold text-purple-600")
                        
                        # Детальная информация о кэше
                        with ui.expansion("Детальная информация", icon="info").classes("w-full"):
                            with ui.column().classes("space-y-2"):
                                ui.label("Содержимое кэша:").classes("font-semibold")
                                
                                if cache_manager._cache:
                                    for key, entry in cache_manager._cache.items():
                                        with ui.card().classes("p-2 bg-gray-50"):
                                            with ui.row().classes("justify-between items-center"):
                                                ui.label(f"Ключ: {key}").classes("font-mono text-sm")
                                                ui.label(f"TTL: {int(entry['expires_at'] - entry['created_at'])}с").classes("text-xs text-gray-500")
                                            
                                            # Показываем размер значения
                                            value_size = len(str(entry['value']))
                                            ui.label(f"Размер: {value_size} байт").classes("text-xs text-gray-500")
                                            
                                            # Показываем время создания
                                            import datetime
                                            created_time = datetime.datetime.fromtimestamp(entry['created_at']).strftime("%H:%M:%S")
                                            ui.label(f"Создано: {created_time}").classes("text-xs text-gray-500")
                                else:
                                    ui.label("Кэш пуст").classes("text-gray-500 italic")
                        
                    except Exception as e:
                        ui.label(f"Ошибка получения статистики: {e}").classes("text-red-500")
            
            def clear_cache():
                """Очищает весь кэш"""
                try:
                    cache_manager.clear()
                    ui.notify("Кэш очищен!", type="positive")
                    refresh_cache_stats()
                except Exception as e:
                    ui.notify(f"Ошибка очистки кэша: {e}", type="negative")
            
            def show_performance_stats():
                """Показывает статистику производительности"""
                with ui.dialog() as dialog, ui.card().classes("p-6 w-96"):
                    ui.label("📈 Статистика производительности").classes("text-lg font-semibold mb-4")
                    
                    with ui.column().classes("space-y-3"):
                        stats = cache_manager.get_stats()
                        
                        # Расчет эффективности кэша
                        total_entries = stats['total_entries']
                        active_entries = stats['active_entries']
                        hit_rate = (active_entries / total_entries * 100) if total_entries > 0 else 0
                        
                        ui.label(f"Эффективность кэша: {hit_rate:.1f}%")
                        ui.label(f"Активных записей: {active_entries}")
                        ui.label(f"Истекших записей: {stats['expired_entries']}")
                        ui.label(f"Использование памяти: {stats['memory_usage']} байт")
                        
                        # Рекомендации
                        ui.separator()
                        ui.label("Рекомендации:").classes("font-semibold")
                        
                        if hit_rate < 50:
                            ui.label("• Низкая эффективность кэша. Рассмотрите увеличение TTL.").classes("text-orange-600")
                        elif hit_rate > 90:
                            ui.label("• Высокая эффективность кэша. Отлично!").classes("text-green-600")
                        else:
                            ui.label("• Хорошая эффективность кэша.").classes("text-blue-600")
                        
                        if stats['memory_usage'] > 1024 * 1024:  # 1MB
                            ui.label("• Высокое использование памяти. Рассмотрите очистку.").classes("text-orange-600")
                    
                    with ui.row().classes("justify-end mt-4"):
                        ui.button("Закрыть", on_click=dialog.close)
                    
                    dialog.open()
            
            # Инициализируем статистику
            refresh_cache_stats()
        
        # Информация о кэшированных функциях
        with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
            ui.label("Кэшированные функции").classes("text-lg font-semibold text-gray-800 mb-4")
            
            with ui.column().classes("space-y-2"):
                ui.label("• get_portfolio_stats() - TTL: 60 секунд")
                ui.label("• list_transactions() - TTL: 120 секунд")
                ui.label("• get_sources_with_frequency() - TTL: 600 секунд")
                ui.label("• get_price_alerts() - TTL: 60 секунд")
                
                ui.separator()
                
                ui.label("Кэш автоматически инвалидируется при:").classes("font-semibold")
                ui.label("• Добавлении новой транзакции")
                ui.label("• Изменении источников")
                ui.label("• Обновлении алертов")
        
        # Кэш цен криптовалют
        with ui.card().classes("p-4 bg-white shadow-sm rounded-lg mt-4"):
            ui.label("💰 Кэш цен криптовалют").classes("text-lg font-semibold text-gray-800 mb-4")
            
            # Контейнер для статистики цен
            prices_stats_container = ui.column().classes("w-full")
            
            def refresh_prices_stats():
                """Обновляет статистику кэша цен"""
                prices_stats_container.clear()
                
                with prices_stats_container:
                    try:
                        stats = get_cache_stats()
                        
                        # Общая статистика кэша цен
                        with ui.row().classes("w-full gap-4 mb-4"):
                            with ui.card().classes("p-3 bg-blue-50 border-l-4 border-blue-400 flex-1"):
                                ui.label("Всего монет в кэше").classes("text-sm text-gray-600")
                                ui.label(str(stats['total_entries'])).classes("text-xl font-bold text-blue-600")
                            
                            with ui.card().classes("p-3 bg-green-50 border-l-4 border-green-400 flex-1"):
                                ui.label("Активных записей").classes("text-sm text-gray-600")
                                ui.label(str(stats['valid_entries'])).classes("text-xl font-bold text-green-600")
                            
                            with ui.card().classes("p-3 bg-red-50 border-l-4 border-red-400 flex-1"):
                                ui.label("Истекших записей").classes("text-sm text-gray-600")
                                ui.label(str(stats['expired_entries'])).classes("text-xl font-bold text-red-600")
                            
                            with ui.card().classes("p-3 bg-purple-50 border-l-4 border-purple-400 flex-1"):
                                ui.label("Эффективность").classes("text-sm text-gray-600")
                                hit_rate = stats['hit_rate'] * 100
                                ui.label(f"{hit_rate:.1f}%").classes("text-xl font-bold text-purple-600")
                        
                        # Статистика по источникам
                        if stats['sources']:
                            ui.label("Источники данных:").classes("text-sm font-semibold text-gray-700 mb-2")
                            for source, count in stats['sources'].items():
                                ui.label(f"• {source}: {count} записей").classes("text-sm text-gray-600")
                        
                    except Exception as e:
                        ui.label(f"Ошибка загрузки статистики: {e}").classes("text-red-500")
            
            def preload_coins():
                """Предзагружает популярные монеты"""
                try:
                    ui.notify("🔄 Начинаем предзагрузку монет...", type="info")
                    loaded_count = preload_popular_coins()
                    ui.notify(f"✅ Предзагружено {loaded_count} монет", type="positive")
                    refresh_prices_stats()
                except Exception as e:
                    ui.notify(f"❌ Ошибка предзагрузки: {e}", type="negative")
            
            def clear_prices_cache():
                """Очищает кэш цен"""
                try:
                    cleaned_count = clean_expired_cache()
                    ui.notify(f"🗑️ Очищено {cleaned_count} устаревших записей", type="positive")
                    refresh_prices_stats()
                except Exception as e:
                    ui.notify(f"❌ Ошибка очистки: {e}", type="negative")
            
            # Кнопки управления кэшем цен
            with ui.row().classes("gap-2 mb-4"):
                ui.button("🔄 Обновить", icon="refresh").classes("bg-blue-500 text-white").on("click", refresh_prices_stats)
                ui.button("🗑️ Очистить устаревшие", icon="delete").classes("bg-red-500 text-white").on("click", clear_prices_cache)
            
            # Загружаем статистику при открытии
            refresh_prices_stats()
