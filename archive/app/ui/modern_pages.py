"""
Современные страницы для Crypto Portfolio Manager

ARCHIVED UI: Этот модуль больше не используется активной версией UI.
Актуальный UI: app/ui/pages_step2.py
Дата архивации: 2025-09-22
"""

import os
from nicegui import ui
from app.core.models import TransactionIn
from app.core.services import (
    add_transaction,
    delete_transaction,
    enrich_positions_with_market,
    export_positions_csv,
    export_transactions_csv,
    get_portfolio_stats,
    get_transaction,
    get_transaction_stats,
    list_transactions,
    positions_fifo,
    update_transaction,
)
from app.ui.layout_improvements import (
    create_modern_dialog,
    create_modern_form_field,
    create_modern_table,
    create_success_toast,
    create_error_toast,
    create_info_toast,
)

CURRENCY = os.getenv("REPORT_CURRENCY", "USD").upper()
TYPES = ["buy", "sell", "exchange_in", "exchange_out", "deposit", "withdrawal"]
STRATS = ["long", "mid", "short", "scalp"]

# Иконки для типов транзакций
TYPE_ICONS = {
    "buy": "📈",
    "sell": "📉", 
    "exchange_in": "↗️",
    "exchange_out": "↘️",
    "deposit": "💰",
    "withdrawal": "💸",
}

# Иконки для стратегий
STRATEGY_ICONS = {"long": "🦅", "mid": "⚖️", "short": "⚡", "scalp": "🎯"}


def create_overview_page():
    """Создает страницу обзора портфеля"""
    with ui.column().classes("w-full space-y-6"):
        # Заголовок
        with ui.row().classes("items-center justify-between"):
            ui.label("Обзор портфеля").classes("text-3xl font-bold text-gray-800")
            with ui.button("Обновить", icon="refresh").classes(
                "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
            ):
                pass
        
        # Статистические карточки
        with ui.row().classes("gap-6 mb-8"):
            create_portfolio_stat_card("Общая стоимость", "$0.00", "💰", "primary")
            create_portfolio_stat_card("Дневной PnL", "+$0.00", "📈", "success")
            create_portfolio_stat_card("Нереализованный PnL", "+$0.00", "💎", "info")
            create_portfolio_stat_card("Реализованный PnL", "+$0.00", "✅", "warning")
        
        # Графики и аналитика
        with ui.row().classes("gap-6"):
            # График стоимости портфеля
            with ui.card().classes("flex-1 p-6 bg-white shadow-sm rounded-lg"):
                ui.label("Стоимость портфеля").classes("text-lg font-semibold text-gray-800 mb-4")
                with ui.row().classes("h-64 items-center justify-center bg-gray-50 rounded-lg"):
                    ui.label("График в разработке").classes("text-gray-500")
            
            # Топ позиции
            with ui.card().classes("flex-1 p-6 bg-white shadow-sm rounded-lg"):
                ui.label("Топ позиции").classes("text-lg font-semibold text-gray-800 mb-4")
                with ui.column().classes("space-y-3"):
                    for i in range(3):
                        with ui.row().classes("items-center justify-between p-3 bg-gray-50 rounded-lg"):
                            ui.label(f"Позиция {i+1}").classes("font-medium text-gray-700")
                            ui.label("$0.00").classes("text-green-600 font-semibold")


def create_positions_page():
    """Создает страницу позиций"""
    with ui.column().classes("w-full space-y-6"):
        # Заголовок и фильтры
        with ui.row().classes("items-center justify-between"):
            ui.label("Позиции").classes("text-3xl font-bold text-gray-800")
            with ui.row().classes("items-center space-x-3"):
                with ui.select(["Все монеты", "BTC", "ETH", "SOL"]).classes(
                    "w-40 p-2 border border-gray-300 rounded-lg"
                ):
                    pass
                with ui.button("Экспорт", icon="download").classes(
                    "bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
                ):
                    pass
        
        # Таблица позиций
        with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
            columns = [
                {"name": "coin", "label": "Монета", "field": "coin", "sortable": True},
                {"name": "strategy", "label": "Стратегия", "field": "strategy", "sortable": True},
                {"name": "quantity", "label": "Количество", "field": "quantity", "sortable": True},
                {"name": "avg_cost", "label": "Средняя цена", "field": "avg_cost", "sortable": True},
                {"name": "current_price", "label": "Текущая цена", "field": "current_price", "sortable": True},
                {"name": "value", "label": "Стоимость", "field": "value", "sortable": True},
                {"name": "pnl", "label": "PnL", "field": "pnl", "sortable": True},
                {"name": "pnl_pct", "label": "PnL %", "field": "pnl_pct", "sortable": True},
            ]
            
            table = create_modern_table(columns, [])
            
            # Заглушка для пустой таблицы
            with ui.row().classes("h-64 items-center justify-center"):
                ui.label("Нет позиций").classes("text-gray-500 text-lg")


def create_transactions_page():
    """Создает страницу сделок"""
    with ui.column().classes("w-full space-y-6"):
        # Заголовок и действия
        with ui.row().classes("items-center justify-between"):
            ui.label("Сделки").classes("text-3xl font-bold text-gray-800")
            with ui.row().classes("items-center space-x-3"):
                with ui.button("Добавить сделку", icon="add").classes(
                    "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
                ).on_click(lambda: open_add_transaction_dialog()):
                    pass
                with ui.button("Экспорт", icon="download").classes(
                    "bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
                ):
                    pass
        
        # Фильтры
        with ui.card().classes("w-full p-4 bg-white shadow-sm rounded-lg"):
            with ui.row().classes("items-center space-x-4"):
                create_modern_form_field("Монета", "select", options=["Все", "BTC", "ETH", "SOL"])
                create_modern_form_field("Тип", "select", options=["Все", "Покупка", "Продажа"])
                create_modern_form_field("Стратегия", "select", options=["Все", "Long", "Mid", "Short", "Scalp"])
                with ui.button("Применить", icon="filter_list").classes(
                    "bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
                ):
                    pass
        
        # Таблица сделок
        with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
            columns = [
                {"name": "id", "label": "ID", "field": "id", "sortable": True},
                {"name": "coin", "label": "Монета", "field": "coin", "sortable": True},
                {"name": "type", "label": "Тип", "field": "type", "sortable": True},
                {"name": "quantity", "label": "Количество", "field": "quantity", "sortable": True},
                {"name": "price", "label": "Цена", "field": "price", "sortable": True},
                {"name": "strategy", "label": "Стратегия", "field": "strategy", "sortable": True},
                {"name": "date", "label": "Дата", "field": "date", "sortable": True},
                {"name": "actions", "label": "Действия", "field": "actions"},
            ]
            
            table = create_modern_table(columns, [])
            
            # Заглушка для пустой таблицы
            with ui.row().classes("h-64 items-center justify-center"):
                ui.label("Нет сделок").classes("text-gray-500 text-lg")


def create_analytics_page():
    """Создает страницу аналитики"""
    with ui.column().classes("w-full space-y-6"):
        # Заголовок
        ui.label("Аналитика").classes("text-3xl font-bold text-gray-800")
        
        # Карточки с метриками
        with ui.row().classes("gap-6 mb-8"):
            create_analytics_card("Sharpe Ratio", "0.00", "📊", "primary")
            create_analytics_card("Max Drawdown", "0.00%", "📉", "error")
            create_analytics_card("Volatility", "0.00%", "📈", "warning")
            create_analytics_card("Win Rate", "0.00%", "🎯", "success")
        
        # Графики
        with ui.row().classes("gap-6"):
            # График PnL
            with ui.card().classes("flex-1 p-6 bg-white shadow-sm rounded-lg"):
                ui.label("PnL по времени").classes("text-lg font-semibold text-gray-800 mb-4")
                with ui.row().classes("h-64 items-center justify-center bg-gray-50 rounded-lg"):
                    ui.label("График в разработке").classes("text-gray-500")
            
            # Распределение по монетам
            with ui.card().classes("flex-1 p-6 bg-white shadow-sm rounded-lg"):
                ui.label("Распределение по монетам").classes("text-lg font-semibold text-gray-800 mb-4")
                with ui.row().classes("h-64 items-center justify-center bg-gray-50 rounded-lg"):
                    ui.label("График в разработке").classes("text-gray-500")


def create_portfolio_stat_card(title, value, icon, color):
    """Создает статистическую карточку портфеля"""
    color_classes = {
        "primary": "bg-gradient-to-r from-indigo-500 to-purple-600",
        "success": "bg-gradient-to-r from-green-500 to-emerald-600",
        "info": "bg-gradient-to-r from-blue-500 to-cyan-600",
        "warning": "bg-gradient-to-r from-yellow-500 to-orange-600",
    }
    
    with ui.card().classes(
        f"flex-1 p-6 text-white shadow-lg rounded-lg {color_classes.get(color, color_classes['primary'])}"
    ):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label(icon).classes("text-3xl")
            ui.label(value).classes("text-2xl font-bold")
        ui.label(title).classes("text-sm opacity-90")


def create_analytics_card(title, value, icon, color):
    """Создает карточку аналитики"""
    color_classes = {
        "primary": "bg-gradient-to-r from-indigo-500 to-purple-600",
        "success": "bg-gradient-to-r from-green-500 to-emerald-600",
        "info": "bg-gradient-to-r from-blue-500 to-cyan-600",
        "warning": "bg-gradient-to-r from-yellow-500 to-orange-600",
        "error": "bg-gradient-to-r from-red-500 to-pink-600",
    }
    
    with ui.card().classes(
        f"flex-1 p-6 text-white shadow-lg rounded-lg {color_classes.get(color, color_classes['primary'])}"
    ):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label(icon).classes("text-3xl")
            ui.label(value).classes("text-2xl font-bold")
        ui.label(title).classes("text-sm opacity-90")


def open_add_transaction_dialog():
    """Открывает диалог добавления сделки"""
    def content():
        with ui.column().classes("space-y-4"):
            # Форма в две колонки
            with ui.row().classes("gap-4"):
                with ui.column().classes("flex-1 space-y-4"):
                    coin_input = create_modern_form_field("Монета", placeholder="BTC, ETH, SOL...")
                    type_select = create_modern_form_field("Тип операции", "select", options=TYPES)
                    qty_input = create_modern_form_field("Количество", placeholder="0.0")
                    price_input = create_modern_form_field("Цена за монету", placeholder="0.00")
                
                with ui.column().classes("flex-1 space-y-4"):
                    strategy_select = create_modern_form_field("Стратегия", "select", options=STRATS)
                    source_input = create_modern_form_field("Источник", placeholder="Binance, Coinbase...")
                    notes_input = create_modern_form_field("Заметки", "textarea", placeholder="Дополнительная информация...")
            
            # Кнопки
            with ui.row().classes("justify-end space-x-3 pt-4 border-t border-gray-200"):
                with ui.button("Отмена").classes(
                    "bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-2 rounded-lg"
                ):
                    pass
                with ui.button("Добавить", icon="add").classes(
                    "bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg"
                ):
                    create_success_toast("Сделка добавлена!")
    
    dialog = create_modern_dialog("Добавить сделку", content)
    dialog.open()


def create_modern_portfolio_page():
    """Создает современную главную страницу портфеля"""
    with ui.column().classes("w-full h-full"):
        # Создаем современный макет
        from app.ui.layout_improvements import ModernLayout
        layout = ModernLayout()
        layout.create_main_layout()
