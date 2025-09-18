#!/usr/bin/env python3
"""
Crypto Portfolio Manager - Шаг 1: Улучшение статистических карточек
Добавляем градиенты к карточкам, сохраняя всю функциональность
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
from app.ui.pages_step1 import portfolio_page

# Загружаем переменные окружения
load_dotenv()

# Инициализируем базу данных
init_db()

# Получаем информацию о приложении
app_info = get_app_info()


# Создаем страницы
@ui.page("/")
def index_page():
    ui.navigate.to("/portfolio")


@ui.page("/portfolio")
def portfolio():
    portfolio_page()


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
PORT = int(os.getenv("APP_PORT", "8086"))

# Запускаем приложение
if __name__ == "__main__":
    ui.run(
        host="127.0.0.1",
        port=PORT,
        reload=DEV,
        show=True,
        title="Crypto Portfolio — Step 1",
        favicon="🚀",
    )
