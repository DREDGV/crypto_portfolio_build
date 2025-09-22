#!/usr/bin/env python3
"""
Демонстрация современного UI для Crypto Portfolio Manager
"""

import sys
from pathlib import Path
from nicegui import ui

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def create_demo_page():
    """Создает демонстрационную страницу с современным дизайном"""
    
    # Основной контейнер
    with ui.row().classes("w-full h-screen overflow-hidden"):
        # Боковая панель
        create_demo_sidebar()
        
        # Основной контент
        with ui.column().classes("flex-1 flex flex-col"):
            # Верхняя панель
            create_demo_header()
            
            # Область контента
            with ui.column().classes("flex-1 p-6 bg-gray-50 overflow-auto"):
                create_demo_content()


def create_demo_sidebar():
    """Создает демонстрационную боковую панель"""
    with ui.column().classes(
        "w-72 h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 "
        "text-white shadow-2xl border-r border-slate-700"
    ):
        # Логотип
        with ui.row().classes("items-center p-6 border-b border-slate-700"):
            ui.icon("account_balance_wallet").classes("text-3xl text-indigo-400 mr-3")
            with ui.column().classes("flex-1"):
                ui.label("Crypto Portfolio").classes("text-xl font-bold text-white")
                ui.label("v1.3.0").classes("text-sm text-slate-400")
        
        # Навигация
        with ui.column().classes("flex-1 p-4"):
            nav_items = [
                ("📊", "Обзор", "Общая статистика портфеля"),
                ("💼", "Позиции", "Текущие позиции"),
                ("📝", "Сделки", "История транзакций"),
                ("📈", "Аналитика", "Графики и метрики"),
                ("⚙️", "Настройки", "Конфигурация"),
            ]
            
            for icon, title, description in nav_items:
                with ui.button().classes(
                    "w-full justify-start p-4 mb-2 rounded-lg hover:bg-slate-700 transition-all duration-200"
                ):
                    with ui.row().classes("items-center w-full"):
                        ui.label(icon).classes("text-xl mr-3")
                        with ui.column().classes("flex-1 text-left"):
                            ui.label(title).classes("font-medium text-white")
                            ui.label(description).classes("text-xs text-slate-400")
        
        # Быстрые действия
        with ui.column().classes("p-4 border-t border-slate-700"):
            ui.label("Быстрые действия").classes("text-sm font-medium text-slate-400 mb-3")
            
            actions = [
                ("➕", "Добавить сделку"),
                ("🔄", "Обновить данные"),
                ("📥", "Экспорт"),
            ]
            
            for icon, title in actions:
                with ui.button().classes(
                    "w-full justify-start p-3 mb-2 rounded-lg bg-slate-700 hover:bg-slate-600 "
                    "transition-all duration-200 text-left"
                ):
                    ui.label(icon).classes("text-lg mr-3")
                    ui.label(title).classes("text-sm text-white")


def create_demo_header():
    """Создает демонстрационный заголовок"""
    with ui.row().classes(
        "w-full h-16 bg-white shadow-sm border-b border-gray-200 px-6 "
        "items-center justify-between sticky top-0 z-10"
    ):
        # Логотип и название
        with ui.row().classes("items-center"):
            ui.icon("account_balance_wallet").classes("text-2xl text-indigo-600 mr-3")
            with ui.column().classes("items-start"):
                ui.label("Crypto Portfolio Manager").classes("text-xl font-bold text-gray-800")
                ui.label("v1.3.0").classes("text-sm text-gray-500")
        
        # Поиск и действия
        with ui.row().classes("items-center space-x-4"):
            # Поиск
            with ui.input("Поиск...").classes(
                "w-64 px-4 py-2 border border-gray-300 rounded-lg "
                "focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
            ):
                pass
            
            # Кнопки действий
            with ui.button("Обновить", icon="refresh").classes(
                "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-all duration-200"
            ):
                pass
            
            with ui.button("Настройки", icon="settings").classes(
                "bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-all duration-200"
            ):
                pass


def create_demo_content():
    """Создает демонстрационный контент"""
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
            create_demo_stat_card("Общая стоимость", "$12,450.00", "💰", "primary")
            create_demo_stat_card("Дневной PnL", "+$245.30", "📈", "success")
            create_demo_stat_card("Нереализованный PnL", "+$1,230.50", "💎", "info")
            create_demo_stat_card("Реализованный PnL", "+$890.20", "✅", "warning")
        
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
                    positions = [
                        ("BTC", "$5,230.00", "+12.5%"),
                        ("ETH", "$3,450.00", "+8.3%"),
                        ("SOL", "$1,890.00", "+15.2%"),
                    ]
                    
                    for coin, value, change in positions:
                        with ui.row().classes("items-center justify-between p-3 bg-gray-50 rounded-lg"):
                            ui.label(coin).classes("font-medium text-gray-700")
                            with ui.row().classes("items-center space-x-2"):
                                ui.label(value).classes("text-green-600 font-semibold")
                                ui.label(change).classes("text-green-500 text-sm")
        
        # Таблица позиций
        with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
            ui.label("Позиции").classes("text-lg font-semibold text-gray-800 mb-4")
            
            # Заголовки таблицы
            with ui.row().classes("bg-gray-50 p-3 rounded-lg mb-2 font-medium text-gray-700"):
                ui.label("Монета").classes("flex-1")
                ui.label("Количество").classes("flex-1")
                ui.label("Средняя цена").classes("flex-1")
                ui.label("Текущая цена").classes("flex-1")
                ui.label("PnL").classes("flex-1")
                ui.label("PnL %").classes("flex-1")
            
            # Строки таблицы
            demo_positions = [
                ("BTC", "0.5", "$45,000", "$52,300", "+$3,650", "+16.2%"),
                ("ETH", "2.0", "$2,800", "$3,450", "+$1,300", "+23.2%"),
                ("SOL", "10.0", "$120", "$189", "+$690", "+57.5%"),
            ]
            
            for coin, qty, avg_price, current_price, pnl, pnl_pct in demo_positions:
                with ui.row().classes("p-3 border-b border-gray-100 hover:bg-gray-50 transition-colors"):
                    ui.label(coin).classes("flex-1 font-medium text-gray-700")
                    ui.label(qty).classes("flex-1 text-gray-600")
                    ui.label(avg_price).classes("flex-1 text-gray-600")
                    ui.label(current_price).classes("flex-1 text-gray-600")
                    ui.label(pnl).classes("flex-1 text-green-600 font-semibold")
                    ui.label(pnl_pct).classes("flex-1 text-green-500 font-semibold")


def create_demo_stat_card(title, value, icon, color):
    """Создает демонстрационную статистическую карточку"""
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


@ui.page("/")
def demo():
    create_demo_page()


if __name__ == "__main__":
    print("🎨 Демонстрация современного UI")
    print("=" * 40)
    print("Откройте http://localhost:8081 в браузере")
    print("=" * 40)
    
    ui.run(
        host="127.0.0.1",
        port=8081,
        reload=False,
        show=True,
        title="Crypto Portfolio — UI Demo",
        favicon="🎨",
    )
