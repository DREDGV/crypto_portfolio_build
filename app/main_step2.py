"""
Шаг 2: Восстановление полного функционала ввода сделок
Новый дизайн + Полный функционал ввода с автодополнением и кнопкой "текущая цена"
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from nicegui import ui
from app.storage.db import init_db
from app.ui.pages_step2 import portfolio_page, show_about_page

# Инициализация базы данных
init_db()

# Получаем настройки из переменных окружения
DEV = os.getenv("DEV", "0") == "1"
PORT = int(os.getenv("APP_PORT", "8086"))  # Используем порт 8086 для Шага 2

# Главная страница портфеля
@ui.page("/")
def index():
    portfolio_page()

# Страница "О программе"
@ui.page("/about")
def about():
    show_about_page()

# Запускаем приложение
if __name__ == "__main__":
    print("🚀 Шаг 2: Восстановление полного функционала ввода сделок")
    print("=" * 60)
    print("✅ Новый дизайн + Полный функционал ввода")
    print("✅ Автодополнение монет и бирж")
    print("✅ Кнопка 'Текущая цена' из 5-6 источников")
    print("✅ Улучшенные статистические карточки")
    print("=" * 60)
    print(f"🌐 Откройте http://localhost:{PORT} в браузере")
    print("=" * 60)
    
    ui.run(
        host="127.0.0.1",
        port=PORT,
        reload=DEV,
        show=True,
        title="Crypto Portfolio — Шаг 2: Полный функционал",
        favicon="🎯",
    )
