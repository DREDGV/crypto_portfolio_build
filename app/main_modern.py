#!/usr/bin/env python3
"""
Crypto Portfolio Manager - Современная версия
Улучшенный UI/UX с современным дизайном
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
from app.ui.modern_pages import (
    create_overview_page,
    create_positions_page,
    create_transactions_page,
    create_analytics_page,
)
from app.ui.layout_improvements import ModernLayout

# Загружаем переменные окружения
load_dotenv()

# Инициализируем базу данных
init_db()

# Получаем информацию о приложении
app_info = get_app_info()

# Глобальные переменные
current_page = "overview"
layout = None


def create_modern_header():
    """Создает современный заголовок"""
    with ui.row().classes(
        "w-full h-16 bg-white shadow-sm border-b border-gray-200 px-6 "
        "items-center justify-between sticky top-0 z-10"
    ):
        # Логотип и название
        with ui.row().classes("items-center"):
            ui.icon("account_balance_wallet").classes("text-2xl text-indigo-600 mr-3")
            with ui.column().classes("items-start"):
                ui.label(app_info["name"]).classes("text-xl font-bold text-gray-800")
                ui.label(f"v{app_info['version']}").classes("text-sm text-gray-500")
        
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


def create_modern_sidebar():
    """Создает современную боковую панель"""
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
                ("⚙️", "Настройки", "settings", "Конфигурация"),
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
            
            actions = [
                ("➕", "Добавить сделку", "add_transaction"),
                ("🔄", "Обновить данные", "refresh_data"),
                ("📥", "Экспорт", "export_data"),
            ]
            
            for icon, title, action in actions:
                with ui.button().classes(
                    "w-full justify-start p-3 mb-2 rounded-lg bg-slate-700 hover:bg-slate-600 "
                    "transition-all duration-200 text-left"
                ).on_click(lambda a=action: handle_quick_action(a)):
                    ui.label(icon).classes("text-lg mr-3")
                    ui.label(title).classes("text-sm text-white")


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
        elif route == "settings":
            create_settings_page()
        else:
            create_overview_page()
    
    ui.notify(f"Переход на {route}", color="info")


def handle_quick_action(action):
    """Обработка быстрых действий"""
    if action == "add_transaction":
        from app.ui.modern_pages import open_add_transaction_dialog
        open_add_transaction_dialog()
    elif action == "refresh_data":
        ui.notify("Обновление данных...", color="info")
        # Здесь будет логика обновления данных
    elif action == "export_data":
        ui.notify("Экспорт данных...", color="info")
        # Здесь будет логика экспорта


def create_settings_page():
    """Создает страницу настроек"""
    with ui.column().classes("w-full space-y-6"):
        ui.label("Настройки").classes("text-3xl font-bold text-gray-800")
        
        with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
            ui.label("Настройки приложения").classes("text-lg font-semibold text-gray-800 mb-4")
            
            with ui.column().classes("space-y-4"):
                with ui.row().classes("items-center justify-between"):
                    ui.label("Валюта отчётов").classes("text-gray-700")
                    with ui.select(["USD", "EUR", "RUB"]).classes("w-32"):
                        pass
                
                with ui.row().classes("items-center justify-between"):
                    ui.label("Темная тема").classes("text-gray-700")
                    ui.switch()
                
                with ui.row().classes("items-center justify-between"):
                    ui.label("Уведомления").classes("text-gray-700")
                    ui.switch()


def create_main_layout():
    """Создает основной макет приложения"""
    global content_container
    
    # Основной контейнер
    with ui.row().classes("w-full h-screen overflow-hidden"):
        # Боковая панель (слева)
        create_modern_sidebar()
        
        # Основной контент (справа)
        with ui.column().classes("flex-1 flex flex-col"):
            # Верхняя панель
            create_modern_header()
            
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
PORT = int(os.getenv("APP_PORT", "8080"))

# Запускаем приложение
if __name__ == "__main__":
    ui.run(
        host="127.0.0.1",
        port=PORT,
        reload=DEV,
        show=True,
        title="Crypto Portfolio — Modern",
        favicon="🚀",
    )
