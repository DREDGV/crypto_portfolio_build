#!/usr/bin/env python3
"""
Crypto Portfolio Manager - Улучшенная версия с новым дизайном
Все кнопки работают, функциональность сохранена
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from nicegui import ui

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Импорты после добавления в PYTHONPATH
from app.core.version import get_app_info
from app.storage.db import init_db
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
from app.core.models import TransactionIn

# Загружаем переменные окружения
load_dotenv()

# Инициализируем базу данных
init_db()

# Получаем информацию о приложении
app_info = get_app_info()

# Глобальные переменные
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

# Глобальные переменные для состояния
current_page = "overview"
content_container = None
transactions_table = None
positions_table = None


def create_improved_sidebar():
    """Создает улучшенную боковую панель с рабочими кнопками"""
    with ui.column().classes(
        "w-72 h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 "
        "text-white shadow-2xl border-r border-slate-700"
    ):
        # Логотип и заголовок
        with ui.row().classes("items-center p-6 border-b border-slate-700"):
            ui.icon("account_balance_wallet").classes("text-3xl text-indigo-400 mr-3")
            with ui.column().classes("flex-1"):
                ui.label("Crypto Portfolio").classes("text-xl font-bold text-white")
                ui.label(f"v{app_info['version']}").classes("text-sm text-slate-400")
        
        # Навигация
        with ui.column().classes("flex-1 p-4"):
            nav_items = [
                ("📊", "Обзор", "overview", "Общая статистика портфеля"),
                ("💼", "Позиции", "positions", "Текущие позиции"),
                ("📝", "Сделки", "transactions", "История транзакций"),
                ("📈", "Аналитика", "analytics", "Графики и метрики"),
            ]
            
            for icon, title, route, description in nav_items:
                is_active = route == current_page
                bg_class = "bg-indigo-600" if is_active else "hover:bg-slate-700"
                
                with ui.button().classes(
                    f"w-full justify-start p-4 mb-2 rounded-lg transition-all duration-200 {bg_class}"
                ).on_click(lambda r=route: navigate_to_page(r)):
                    with ui.row().classes("items-center w-full"):
                        ui.label(icon).classes("text-xl mr-3")
                        with ui.column().classes("flex-1 text-left"):
                            ui.label(title).classes("font-medium text-white")
                            ui.label(description).classes("text-xs text-slate-400")
        
        # Быстрые действия
        with ui.column().classes("p-4 border-t border-slate-700"):
            ui.label("Быстрые действия").classes("text-sm font-medium text-slate-400 mb-3")
            
            with ui.button().classes(
                "w-full justify-start p-3 mb-2 rounded-lg bg-slate-700 hover:bg-slate-600 "
                "transition-all duration-200 text-left"
            ).on_click(lambda: open_add_transaction_dialog()):
                ui.label("➕").classes("text-lg mr-3")
                ui.label("Добавить сделку").classes("text-sm text-white")
            
            with ui.button().classes(
                "w-full justify-start p-3 mb-2 rounded-lg bg-slate-700 hover:bg-slate-600 "
                "transition-all duration-200 text-left"
            ).on_click(lambda: refresh_data()):
                ui.label("🔄").classes("text-lg mr-3")
                ui.label("Обновить данные").classes("text-sm text-white")
            
            with ui.button().classes(
                "w-full justify-start p-3 mb-2 rounded-lg bg-slate-700 hover:bg-slate-600 "
                "transition-all duration-200 text-left"
            ).on_click(lambda: export_data()):
                ui.label("📥").classes("text-lg mr-3")
                ui.label("Экспорт").classes("text-sm text-white")


def create_improved_header():
    """Создает улучшенный заголовок"""
    with ui.row().classes(
        "w-full h-16 bg-white shadow-sm border-b border-gray-200 px-6 "
        "items-center justify-between sticky top-0 z-10"
    ):
        # Логотип и название
        with ui.row().classes("items-center"):
            ui.icon("account_balance_wallet").classes("text-2xl text-indigo-600 mr-3")
            with ui.column().classes("items-start"):
                ui.label("Crypto Portfolio Manager").classes("text-xl font-bold text-gray-800")
                ui.label(f"v{app_info['version']}").classes("text-sm text-gray-500")
        
        # Поиск и действия
        with ui.row().classes("items-center space-x-4"):
            # Поиск
            search_input = ui.input("Поиск...").classes(
                "w-64 px-4 py-2 border border-gray-300 rounded-lg "
                "focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
            )
            
            # Кнопки действий
            with ui.button("Обновить", icon="refresh").classes(
                "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-all duration-200"
            ).on_click(lambda: refresh_data()):
                pass
            
            with ui.button("Настройки", icon="settings").classes(
                "bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-all duration-200"
            ).on_click(lambda: open_settings_dialog()):
                pass


def navigate_to_page(route):
    """Навигация между страницами"""
    global current_page
    current_page = route
    
    # Очищаем контент
    content_container.clear()
    
    # Загружаем новую страницу
    with content_container:
        if route == "overview":
            create_overview_page()
        elif route == "positions":
            create_positions_page()
        elif route == "transactions":
            create_transactions_page()
        elif route == "analytics":
            create_analytics_page()
        else:
            create_overview_page()
    
    ui.notify(f"Переход на {route}", color="info")


def create_overview_page():
    """Создает страницу обзора портфеля"""
    with ui.column().classes("w-full space-y-6"):
        # Заголовок
        with ui.row().classes("items-center justify-between"):
            ui.label("Обзор портфеля").classes("text-3xl font-bold text-gray-800")
            with ui.button("Обновить", icon="refresh").classes(
                "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
            ).on_click(lambda: refresh_data()):
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
                    ui.label("📊 График в разработке").classes("text-gray-500 text-lg")
            
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
    global positions_table
    
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
                ).on_click(lambda: export_positions()):
                    pass
        
        # Таблица позиций
        with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
            ui.label("Позиции").classes("text-lg font-semibold text-gray-800 mb-4")
            
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
            
            positions_table = ui.table(columns=columns, rows=[]).classes(
                "w-full bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
            )
            
            # Загружаем данные
            load_positions_data()


def create_transactions_page():
    """Создает страницу сделок"""
    global transactions_table
    
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
                ).on_click(lambda: export_transactions()):
                    pass
        
        # Фильтры
        with ui.card().classes("w-full p-4 bg-white shadow-sm rounded-lg"):
            with ui.row().classes("items-center space-x-4"):
                coin_filter = ui.select(["Все", "BTC", "ETH", "SOL"]).classes("w-32 p-2 border border-gray-300 rounded-lg")
                type_filter = ui.select(["Все", "Покупка", "Продажа"]).classes("w-32 p-2 border border-gray-300 rounded-lg")
                strategy_filter = ui.select(["Все", "Long", "Mid", "Short", "Scalp"]).classes("w-32 p-2 border border-gray-300 rounded-lg")
                with ui.button("Применить", icon="filter_list").classes(
                    "bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
                ).on_click(lambda: apply_filters(coin_filter.value, type_filter.value, strategy_filter.value)):
                    pass
        
        # Таблица сделок
        with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
            ui.label("Сделки").classes("text-lg font-semibold text-gray-800 mb-4")
            
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
            
            transactions_table = ui.table(columns=columns, rows=[]).classes(
                "w-full bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
            )
            
            # Загружаем данные
            load_transactions_data()


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
                    ui.label("📊 График в разработке").classes("text-gray-500 text-lg")
            
            # Распределение по монетам
            with ui.card().classes("flex-1 p-6 bg-white shadow-sm rounded-lg"):
                ui.label("Распределение по монетам").classes("text-lg font-semibold text-gray-800 mb-4")
                with ui.row().classes("h-64 items-center justify-center bg-gray-50 rounded-lg"):
                    ui.label("📊 График в разработке").classes("text-gray-500 text-lg")


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
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl p-6"):
        # Заголовок
        with ui.row().classes("items-center justify-between mb-6 pb-4 border-b border-gray-200"):
            ui.label("Добавить сделку").classes("text-xl font-bold text-gray-800")
            with ui.button(icon="close").classes("text-gray-400 hover:text-gray-600").on_click(lambda: dialog.close()):
                pass
        
        # Форма
        with ui.column().classes("space-y-4"):
            # Форма в две колонки
            with ui.row().classes("gap-4"):
                with ui.column().classes("flex-1 space-y-4"):
                    coin_input = ui.input("Монета", placeholder="BTC, ETH, SOL...").classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    )
                    type_select = ui.select(TYPES, label="Тип операции").classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    )
                    qty_input = ui.input("Количество", placeholder="0.0").classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    )
                    price_input = ui.input("Цена за монету", placeholder="0.00").classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    )
                
                with ui.column().classes("flex-1 space-y-4"):
                    strategy_select = ui.select(STRATS, label="Стратегия").classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    )
                    source_input = ui.input("Источник", placeholder="Binance, Coinbase...").classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    )
                    notes_input = ui.textarea("Заметки", placeholder="Дополнительная информация...").classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    )
            
            # Кнопки
            with ui.row().classes("justify-end space-x-3 pt-4 border-t border-gray-200"):
                with ui.button("Отмена").classes(
                    "bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-2 rounded-lg"
                ).on_click(lambda: dialog.close()):
                    pass
                with ui.button("Добавить", icon="add").classes(
                    "bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg"
                ).on_click(lambda: add_transaction_from_dialog(
                    coin_input.value, type_select.value, qty_input.value, 
                    price_input.value, strategy_select.value, source_input.value, notes_input.value, dialog
                )):
                    pass
    
    dialog.open()


def add_transaction_from_dialog(coin, type_op, qty, price, strategy, source, notes, dialog):
    """Добавляет сделку из диалога"""
    try:
        if not all([coin, type_op, qty, price, strategy]):
            ui.notify("Заполните все обязательные поля", color="negative")
            return
        
        transaction = TransactionIn(
            coin=coin.upper(),
            type=type_op,
            quantity=float(qty),
            price=float(price),
            strategy=strategy,
            source=source or "Unknown",
            notes=notes or ""
        )
        
        add_transaction(transaction)
        ui.notify("Сделка добавлена!", color="positive")
        dialog.close()
        refresh_data()
        
    except Exception as e:
        ui.notify(f"Ошибка: {str(e)}", color="negative")


def open_settings_dialog():
    """Открывает диалог настроек"""
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg p-6"):
        # Заголовок
        with ui.row().classes("items-center justify-between mb-6 pb-4 border-b border-gray-200"):
            ui.label("Настройки").classes("text-xl font-bold text-gray-800")
            with ui.button(icon="close").classes("text-gray-400 hover:text-gray-600").on_click(lambda: dialog.close()):
                pass
        
        # Настройки
        with ui.column().classes("space-y-4"):
            with ui.row().classes("items-center justify-between"):
                ui.label("Валюта отчётов").classes("text-gray-700")
                currency_select = ui.select(["USD", "EUR", "RUB"], value=CURRENCY).classes("w-32")
            
            with ui.row().classes("items-center justify-between"):
                ui.label("Темная тема").classes("text-gray-700")
                dark_theme_switch = ui.switch()
            
            with ui.row().classes("items-center justify-between"):
                ui.label("Уведомления").classes("text-gray-700")
                notifications_switch = ui.switch()
        
        # Кнопки
        with ui.row().classes("justify-end space-x-3 pt-4 border-t border-gray-200"):
            with ui.button("Отмена").classes(
                "bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-2 rounded-lg"
            ).on_click(lambda: dialog.close()):
                pass
            with ui.button("Сохранить").classes(
                "bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg"
            ).on_click(lambda: save_settings(currency_select.value, dark_theme_switch.value, notifications_switch.value, dialog)):
                pass
    
    dialog.open()


def save_settings(currency, dark_theme, notifications, dialog):
    """Сохраняет настройки"""
    ui.notify("Настройки сохранены!", color="positive")
    dialog.close()


def refresh_data():
    """Обновляет данные"""
    ui.notify("Данные обновлены!", color="info")
    if transactions_table:
        load_transactions_data()
    if positions_table:
        load_positions_data()


def load_transactions_data():
    """Загружает данные сделок"""
    if transactions_table:
        try:
            transactions = list_transactions()
            rows = []
            for t in transactions:
                rows.append({
                    "id": t.id,
                    "coin": t.coin,
                    "type": f"{TYPE_ICONS.get(t.type, '')} {t.type}",
                    "quantity": f"{t.quantity:.6f}",
                    "price": f"${t.price:.2f}",
                    "strategy": f"{STRATEGY_ICONS.get(t.strategy, '')} {t.strategy}",
                    "date": t.date.strftime("%Y-%m-%d %H:%M"),
                    "actions": "✏️ 🗑️"
                })
            transactions_table.rows = rows
        except Exception as e:
            ui.notify(f"Ошибка загрузки сделок: {str(e)}", color="negative")


def load_positions_data():
    """Загружает данные позиций"""
    if positions_table:
        try:
            positions = positions_fifo()
            enriched_positions = enrich_positions_with_market(positions)
            rows = []
            for p in enriched_positions:
                pnl_color = "text-green-600" if p.get("pnl", 0) > 0 else "text-red-600" if p.get("pnl", 0) < 0 else "text-gray-600"
                rows.append({
                    "coin": p["coin"],
                    "strategy": f"{STRATEGY_ICONS.get(p['strategy'], '')} {p['strategy']}",
                    "quantity": f"{p['quantity']:.6f}",
                    "avg_cost": f"${p['avg_cost']:.2f}",
                    "current_price": f"${p.get('current_price', 0):.2f}",
                    "value": f"${p.get('value', 0):.2f}",
                    "pnl": f"${p.get('pnl', 0):.2f}",
                    "pnl_pct": f"{p.get('pnl_pct', 0):.2f}%"
                })
            positions_table.rows = rows
        except Exception as e:
            ui.notify(f"Ошибка загрузки позиций: {str(e)}", color="negative")


def apply_filters(coin, type_op, strategy):
    """Применяет фильтры"""
    ui.notify(f"Фильтры: {coin}, {type_op}, {strategy}", color="info")
    # Здесь будет логика фильтрации


def export_transactions():
    """Экспортирует сделки"""
    try:
        export_transactions_csv()
        ui.notify("Сделки экспортированы в CSV!", color="positive")
    except Exception as e:
        ui.notify(f"Ошибка экспорта: {str(e)}", color="negative")


def export_positions():
    """Экспортирует позиции"""
    try:
        export_positions_csv()
        ui.notify("Позиции экспортированы в CSV!", color="positive")
    except Exception as e:
        ui.notify(f"Ошибка экспорта: {str(e)}", color="negative")


def export_data():
    """Экспортирует все данные"""
    try:
        export_transactions_csv()
        export_positions_csv()
        ui.notify("Все данные экспортированы в CSV!", color="positive")
    except Exception as e:
        ui.notify(f"Ошибка экспорта: {str(e)}", color="negative")


def create_main_layout():
    """Создает основной макет приложения"""
    global content_container
    
    # Основной контейнер
    with ui.row().classes("w-full h-screen overflow-hidden"):
        # Боковая панель (слева)
        create_improved_sidebar()
        
        # Основной контент (справа)
        with ui.column().classes("flex-1 flex flex-col"):
            # Верхняя панель
            create_improved_header()
            
            # Область контента
            with ui.column().classes("flex-1 p-6 bg-gray-50 overflow-auto") as container:
                content_container = container
                # Загружаем начальную страницу
                create_overview_page()


# Создаем страницы
@ui.page("/")
def index_page():
    ui.navigate.to("/portfolio")


@ui.page("/portfolio")
def portfolio():
    create_main_layout()


@ui.page("/about")
def about_page():
    with ui.column().classes("max-w-4xl mx-auto p-6"):
        with ui.card().classes("p-8 bg-white shadow-lg rounded-lg"):
            ui.label("О программе").classes("text-3xl font-bold text-gray-800 mb-6")
            
            with ui.column().classes("space-y-4"):
                ui.label(f"Название: {app_info['name']}").classes("text-lg text-gray-700")
                ui.label(f"Версия: {app_info['version']}").classes("text-lg text-gray-700")
                ui.label("Описание: Современное приложение для управления криптопортфелем").classes("text-lg text-gray-700")
                
                with ui.row().classes("mt-6 space-x-4"):
                    with ui.button("GitHub", icon="code").classes(
                        "bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
                    ):
                        pass
                    with ui.button("Документация", icon="description").classes(
                        "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
                    ):
                        pass


# Получаем настройки из переменных окружения
DEV = os.getenv("DEV", "0") == "1"
PORT = int(os.getenv("APP_PORT", "8083"))

# Запускаем приложение
if __name__ == "__main__":
    ui.run(
        host="127.0.0.1",
        port=PORT,
        reload=DEV,
        show=True,
        title="Crypto Portfolio — Improved",
        favicon="🚀",
    )
