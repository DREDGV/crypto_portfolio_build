#!/usr/bin/env python3
"""
Исправленный лаунчер для Crypto Portfolio Manager
Решает проблемы с Python из Microsoft Store
"""

import sys
import os
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

def print_status(message, status="info"):
    """Печатает статус с эмодзи"""
    icons = {
        "info": "ℹ️",
        "success": "✅", 
        "error": "❌",
        "warning": "⚠️",
        "loading": "🔄"
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")

def check_python():
    """Проверяет Python и зависимости"""
    print_status("Проверяем Python...", "loading")
    
    try:
        # Проверяем версию Python
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print_status(f"Требуется Python 3.8+, текущая версия: {version.major}.{version.minor}", "error")
            return False
        
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - OK", "success")
        
        # Проверяем основные зависимости
        required_modules = ['nicegui', 'sqlmodel', 'httpx', 'pydantic']
        for module in required_modules:
            try:
                __import__(module)
                print_status(f"{module} - OK", "success")
            except ImportError:
                print_status(f"{module} - НЕ УСТАНОВЛЕН", "error")
                return False
        
        return True
        
    except Exception as e:
        print_status(f"Ошибка проверки Python: {e}", "error")
        return False

def check_app_modules():
    """Проверяет модули приложения"""
    print_status("Проверяем модули приложения...", "loading")
    
    try:
        # Добавляем текущую директорию в путь
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Проверяем импорты
        from app.core.version import get_app_info
        from app.storage.db import init_db
        from app.core.models import Transaction
        from app.core.services import add_transaction
        from app.adapters.prices import get_current_price
        
        print_status("Все модули приложения - OK", "success")
        
        # Получаем информацию о приложении
        app_info = get_app_info()
        print_status(f"Приложение: {app_info['name']} v{app_info['version']}", "info")
        
        return True
        
    except Exception as e:
        print_status(f"Ошибка импорта модулей: {e}", "error")
        return False

def init_database():
    """Инициализирует базу данных"""
    print_status("Инициализируем базу данных...", "loading")
    
    try:
        from app.storage.db import init_db
        init_db()
        print_status("База данных готова", "success")
        return True
    except Exception as e:
        print_status(f"Ошибка инициализации БД: {e}", "error")
        return False

def open_browser_delayed():
    """Открывает браузер с задержкой"""
    time.sleep(3)
    try:
        webbrowser.open('http://127.0.0.1:8080')
        print_status("Браузер открыт: http://127.0.0.1:8080", "success")
    except Exception as e:
        print_status(f"Не удалось открыть браузер: {e}", "warning")

def launch_app():
    """Запускает основное приложение"""
    print_status("Запускаем приложение...", "loading")
    
    try:
        # Открываем браузер в отдельном потоке
        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Импортируем и запускаем приложение
        from app.main import main as app_main
        app_main()
        
    except KeyboardInterrupt:
        print_status("Приложение остановлено пользователем", "info")
    except Exception as e:
        print_status(f"Ошибка запуска приложения: {e}", "error")
        import traceback
        traceback.print_exc()

def main():
    """Главная функция"""
    print("🚀 Crypto Portfolio Manager - Лаунчер")
    print("=" * 50)
    
    # Проверяем Python
    if not check_python():
        print_status("Проверка Python не пройдена", "error")
        input("Нажмите Enter для выхода...")
        return 1
    
    # Проверяем модули приложения
    if not check_app_modules():
        print_status("Проверка модулей не пройдена", "error")
        input("Нажмите Enter для выхода...")
        return 1
    
    # Инициализируем базу данных
    if not init_database():
        print_status("Инициализация БД не пройдена", "error")
        input("Нажмите Enter для выхода...")
        return 1
    
    print("\n" + "=" * 50)
    print_status("Все проверки пройдены! Запускаем приложение...", "success")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем приложение
    try:
        launch_app()
    except Exception as e:
        print_status(f"Критическая ошибка: {e}", "error")
        input("Нажмите Enter для выхода...")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
