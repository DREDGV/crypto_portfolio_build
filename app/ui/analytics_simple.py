"""
Упрощенная аналитика портфеля - компактная версия
"""

from nicegui import ui
from app.core.services import list_transactions, get_portfolio_stats, positions_fifo


def create_analytics_tab():
    """Создает упрощенную вкладку аналитики"""
    with ui.column().classes("w-full h-full overflow-y-auto p-4"):
        ui.label("📊 Аналитика портфеля").classes("text-2xl font-bold text-gray-800 mb-4")
        
        # Основные метрики в одной карточке
        with ui.card().classes("p-4 bg-gradient-to-r from-blue-50 to-green-50 w-full"):
            ui.label("📈 Основные показатели").classes("text-lg font-semibold text-blue-800 mb-3")
            
            metrics_container = ui.column().classes("w-full")
            
            def refresh_metrics():
                metrics_container.clear()
                with metrics_container:
                    # Получаем данные
                    transactions = list_transactions()
                    portfolio_stats = get_portfolio_stats()
                    positions = positions_fifo()
                    
                    # Простые расчеты
                    total_invested = sum(tx['quantity'] * tx['price'] for tx in transactions if tx['type'] in ['buy', 'deposit', 'exchange_in'])
                    current_value = portfolio_stats.get('total_value', 0)
                    total_pnl = current_value - total_invested
                    roi_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
                    
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
                            strategies = [tx.get('strategy', 'unknown') for tx in transactions]
                            main_strategy = max(set(strategies), key=strategies.count) if strategies else 'unknown'
                            ui.label(f"{main_strategy}").classes("text-lg font-semibold text-purple-600")
            
            refresh_metrics()
        
        # Позиции (если есть)
        with ui.card().classes("p-4 bg-green-50 w-full mt-4"):
            ui.label("🪙 Текущие позиции").classes("text-lg font-semibold text-green-800 mb-3")
            
            positions_container = ui.column().classes("w-full")
            
            def refresh_positions():
                positions_container.clear()
                with positions_container:
                    positions = positions_fifo()
                    
                    if positions:
                        for pos in positions:
                            coin = pos['coin']
                            qty = pos.get('quantity', 0)
                            current_price = pos.get('current_price', 0)
                            avg_cost = pos.get('avg_cost', 0)
                            current_value = qty * current_price
                            cost_basis = qty * avg_cost
                            pnl = current_value - cost_basis
                            pnl_percent = (pnl / cost_basis * 100) if cost_basis > 0 else 0
                            
                            with ui.row().classes("w-full justify-between items-center p-2 bg-white rounded mb-2"):
                                with ui.column().classes("flex-1"):
                                    ui.label(f"{coin}").classes("font-semibold text-gray-800")
                                    ui.label(f"{qty:.4f} @ ${avg_cost:.2f}").classes("text-sm text-gray-600")
                                
                                with ui.column().classes("flex-1 text-center"):
                                    ui.label(f"${current_price:.2f}").classes("font-semibold text-blue-600")
                                    ui.label("Текущая цена").classes("text-xs text-gray-500")
                                
                                with ui.column().classes("flex-1 text-center"):
                                    ui.label(f"${current_value:.2f}").classes("font-semibold text-green-600")
                                    ui.label("Стоимость").classes("text-xs text-gray-500")
                                
                                with ui.column().classes("flex-1 text-center"):
                                    ui.label(f"${pnl:.2f}").classes(f"font-semibold {'text-green-600' if pnl >= 0 else 'text-red-600'}")
                                    ui.label(f"({pnl_percent:+.1f}%)").classes(f"text-sm {'text-green-600' if pnl >= 0 else 'text-red-600'}")
                    else:
                        ui.label("Нет открытых позиций").classes("text-gray-500 italic")
            
            refresh_positions()
        
        # Кнопка обновления
        with ui.row().classes("w-full justify-center mt-6"):
            ui.button("🔄 Обновить данные", icon="refresh").classes("bg-blue-500 text-white px-6 py-2").on("click", lambda: (
                refresh_metrics(),
                refresh_positions(),
                ui.notify("Данные обновлены!", type="positive")
            ))
        
        # Автообновление каждые 30 секунд
        ui.timer(30, lambda: (
            refresh_metrics(),
            refresh_positions()
        ))
