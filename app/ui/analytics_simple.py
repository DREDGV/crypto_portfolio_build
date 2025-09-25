"""
Упрощенная аналитика портфеля - компактная версия
"""

from nicegui import ui
from app.core.services import list_transactions, get_portfolio_stats, positions_fifo


def create_analytics_tab():
    """Создает упрощенную вкладку аналитики"""
    with ui.column().classes("w-full p-4 max-h-[calc(100vh-200px)] overflow-y-auto"):
        ui.label("📊 Аналитика портфеля").classes("text-2xl font-bold text-gray-800 mb-4")
        
        # Диагностическая информация
        with ui.card().classes("p-3 bg-yellow-50 border-l-4 border-yellow-400 mb-4"):
            ui.label("🔍 Диагностика").classes("text-sm font-semibold text-yellow-800 mb-2")
            diagnostic_info = ui.column().classes("text-xs text-yellow-700")
            
            def update_diagnostic():
                diagnostic_info.clear()
                with diagnostic_info:
                    try:
                        from app.adapters.prices import get_current_price
                        
                        # Тестируем получение цен
                        btc_price = get_current_price("BTC")
                        eth_price = get_current_price("ETH")
                        
                        ui.label(f"BTC цена: ${btc_price}")
                        ui.label(f"ETH цена: ${eth_price}")
                        
                        # Проверяем позиции
                        positions = positions_fifo()
                        ui.label(f"Позиций в портфеле: {len(positions)}")
                        
                        for pos in positions[:3]:  # Показываем первые 3
                            ui.label(f"{pos['coin']}: {pos['quantity']} @ ${pos['avg_cost']}")
                            
                    except Exception as e:
                        ui.label(f"Ошибка диагностики: {e}")
            
            update_diagnostic()
            with ui.row().classes("gap-2 mt-2"):
                ui.button("🔄 Обновить диагностику", icon="refresh").classes("text-xs").on("click", update_diagnostic)
                ui.button("🗑️ Очистить кэш", icon="delete").classes("text-xs bg-red-100 text-red-700").on("click", lambda: clear_portfolio_cache())
            
            def clear_portfolio_cache():
                try:
                    from app.core.cache import cache_manager
                    cache_manager.delete("portfolio_stats")
                    ui.notify("✅ Кэш портфеля очищен", type="positive")
                    update_diagnostic()
                except Exception as e:
                    ui.notify(f"❌ Ошибка очистки кэша: {e}", type="negative")
        
        # Основные метрики в одной карточке
        with ui.card().classes("p-4 bg-gradient-to-r from-blue-50 to-green-50 w-full"):
            ui.label("📈 Основные показатели").classes("text-lg font-semibold text-blue-800 mb-3")
            
            metrics_container = ui.column().classes("w-full")
            
            def refresh_metrics():
                metrics_container.clear()
                with metrics_container:
                    try:
                        # Получаем данные
                        transactions = list_transactions()
                        portfolio_stats = get_portfolio_stats()
                        positions = positions_fifo()
                        
                        # Простые расчеты
                        from app.core.taxonomy import INBOUND_POSITION_TYPES, normalize_transaction_type
                        total_invested = sum(
                            tx['quantity'] * tx['price']
                            for tx in transactions
                            if normalize_transaction_type(tx.get('type')) in INBOUND_POSITION_TYPES
                        )
                        # ИСПРАВЛЕНИЕ: правильный путь к total_value
                        current_value = portfolio_stats.get('totals', {}).get('total_value', 0)
                        total_pnl = current_value - total_invested
                        roi_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
                        
                    except Exception as e:
                        # print(f"DEBUG: Ошибка в refresh_metrics: {e}")
                        # Показываем ошибку пользователю
                        ui.label(f"❌ Ошибка загрузки данных: {e}").classes("text-red-500 text-center")
                        return
                    
                    # Отображаем в компактном виде
                    with ui.row().classes("w-full gap-6"):
                        with ui.column().classes("flex-1 text-center"):
                            ui.label("💰 Инвестировано").classes("text-sm text-gray-500")
                            ui.label(f"${total_invested:.2f}").classes("text-xl font-bold text-blue-600")
                        
                        with ui.column().classes("flex-1 text-center"):
                            ui.label("📊 Текущая стоимость").classes("text-sm text-gray-500")
                            ui.label(f"${current_value:.2f}").classes("text-xl font-bold text-green-600")
                        
                        with ui.column().classes("flex-1 text-center"):
                            ui.label("📈 P&L").classes("text-sm text-gray-500")
                            ui.label(f"${total_pnl:.2f}").classes(f"text-xl font-bold {'text-green-600' if total_pnl >= 0 else 'text-red-600'}")
                        
                        with ui.column().classes("flex-1 text-center"):
                            ui.label("🎯 ROI").classes("text-sm text-gray-500")
                            ui.label(f"{roi_percent:.1f}%").classes(f"text-xl font-bold {'text-green-600' if roi_percent >= 0 else 'text-red-600'}")
                    
                    # Дополнительная информация
                    with ui.row().classes("w-full gap-6 mt-4"):
                        with ui.column().classes("flex-1 text-center"):
                            ui.label("📝 Сделок").classes("text-sm text-gray-500")
                            ui.label(f"{len(transactions)}").classes("text-lg font-semibold text-gray-700")
                        
                        with ui.column().classes("flex-1 text-center"):
                            ui.label("🪙 Монет").classes("text-sm text-gray-500")
                            ui.label(f"{len(positions)}").classes("text-lg font-semibold text-gray-700")
                        
                        with ui.column().classes("flex-1 text-center"):
                            ui.label("🏆 Стратегия").classes("text-sm text-gray-500")
                            from app.core.taxonomy import normalize_strategy, STRATEGY_META
                            strategies = [normalize_strategy(tx.get('strategy', 'unknown')) for tx in transactions]
                            main_strategy = max(set(strategies), key=strategies.count) if strategies else 'unknown'
                            strategy_label = STRATEGY_META.get(main_strategy).label if main_strategy in STRATEGY_META else main_strategy
                            ui.label(f"{strategy_label}").classes("text-lg font-semibold text-purple-600")
            
            refresh_metrics()
        
        # Позиции (если есть)
        with ui.card().classes("p-4 bg-green-50 w-full mt-4"):
            ui.label("🪙 Текущие позиции").classes("text-lg font-semibold text-green-800 mb-3")
            
            positions_container = ui.column().classes("w-full min-h-[200px]")
            
            def refresh_positions():
                positions_container.clear()
                with positions_container:
                    # ИСПРАВЛЕНИЕ: используем обогащенные позиции из статистики портфеля
                    portfolio_stats = get_portfolio_stats()
                    positions = portfolio_stats.get('top_positions', [])
                    
                    if positions:
                        for pos in positions:
                            coin = pos['coin']
                            qty = pos.get('quantity', 0)
                            current_price = pos.get('price', 0)  # Уже обогащенная цена
                            avg_cost = pos.get('avg_cost', 0)
                            current_value = pos.get('value', 0)  # Уже рассчитанная стоимость
                            cost_basis = pos.get('cost_basis', 0)  # Уже рассчитанная базовая стоимость
                            pnl = pos.get('unreal_pnl', 0)  # Уже рассчитанный P&L
                            pnl_percent = pos.get('unreal_pct', 0)  # Уже рассчитанный процент
                            
                            with ui.row().classes("w-full justify-between items-center p-3 bg-white rounded-lg mb-3 shadow-sm border"):
                                with ui.column().classes("flex-1 min-w-[120px]"):
                                    ui.label(f"{coin}").classes("font-semibold text-gray-800 text-lg")
                                    ui.label(f"{qty:.4f} @ ${avg_cost:.2f}").classes("text-sm text-gray-600")
                                
                                with ui.column().classes("flex-1 text-center min-w-[100px]"):
                                    ui.label(f"${current_price:.2f}").classes("font-semibold text-blue-600 text-lg")
                                    ui.label("Текущая цена").classes("text-xs text-gray-500")
                                
                                with ui.column().classes("flex-1 text-center min-w-[100px]"):
                                    ui.label(f"${current_value:.2f}").classes("font-semibold text-green-600 text-lg")
                                    ui.label("Стоимость").classes("text-xs text-gray-500")
                                
                                with ui.column().classes("flex-1 text-center min-w-[120px]"):
                                    ui.label(f"${pnl:.2f}").classes(f"font-semibold {'text-green-600' if pnl >= 0 else 'text-red-600'} text-lg")
                                    ui.label(f"({pnl_percent:+.1f}%)").classes(f"text-sm {'text-green-600' if pnl >= 0 else 'text-red-600'}")
                    else:
                        ui.label("Нет открытых позиций").classes("text-gray-500 italic")
            
            refresh_positions()
        
        # Кнопки управления
        with ui.row().classes("w-full justify-center gap-3 mt-6"):
            ui.button("🔄 Обновить данные", icon="refresh").classes("bg-blue-500 text-white px-6 py-2").on("click", lambda: (
                refresh_metrics(),
                refresh_positions(),
                ui.notify("Данные обновлены!", type="positive")
            ))
            ui.button("🗑️ Очистить кэш", icon="delete").classes("bg-red-500 text-white px-6 py-2").on("click", lambda: clear_all_cache())
        
        def clear_all_cache():
            try:
                from app.core.cache import cache_manager
                cache_manager.delete("portfolio_stats")
                cache_manager.clear()  # Очищаем весь кэш
                ui.notify("✅ Весь кэш очищен", type="positive")
                refresh_metrics()
                refresh_positions()
            except Exception as e:
                ui.notify(f"❌ Ошибка очистки кэша: {e}", type="negative")
        
        # Автообновление каждые 30 секунд
        ui.timer(30, lambda: (
            refresh_metrics(),
            refresh_positions()
        ))
