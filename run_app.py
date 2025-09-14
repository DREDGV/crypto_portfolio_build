#!/usr/bin/env python3
"""
Crypto Portfolio Manager - Единый файл запуска
Простое и надежное приложение для управления криптопортфелем
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Проверяет версию Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    print(f"✅ Python версия: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Проверяет установленные зависимости"""
    required_packages = [
        'nicegui',
        'sqlmodel', 
        'sqlalchemy',
        'aiosqlite',
        'pydantic',
        'httpx',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Установите недостающие пакеты:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_app_modules():
    """Проверяет модули приложения"""
    try:
        from app.core.models import Transaction, TransactionIn
        print("✅ Модели данных")
    except ImportError as e:
        print(f"❌ Модели данных: {e}")
        return False
    
    try:
        from app.core.services import add_transaction, list_transactions, positions_fifo
        print("✅ Сервисы")
    except ImportError as e:
        print(f"❌ Сервисы: {e}")
        return False
    
    try:
        from app.adapters.prices import get_current_price
        print("✅ Адаптер цен")
    except ImportError as e:
        print(f"❌ Адаптер цен: {e}")
        return False
    
    try:
        from app.storage.db import init_db
        print("✅ База данных")
    except ImportError as e:
        print(f"❌ База данных: {e}")
        return False
    
    try:
        from app.ui.pages import portfolio_page
        print("✅ UI страницы")
    except ImportError as e:
        print(f"❌ UI страницы: {e}")
        return False
    
    return True

def create_directories():
    """Создает необходимые директории"""
    directories = ['data', 'data/backups', 'data/exports']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Директория: {directory}")

def main():
    """Главная функция запуска"""
    print("🚀 Crypto Portfolio Manager")
    print("=" * 50)
    
    # Проверяем Python
    if not check_python_version():
        return 1
    
    # Проверяем зависимости
    print("\n📦 Проверяем зависимости...")
    if not check_dependencies():
        return 1
    
    # Проверяем модули приложения
    print("\n🔧 Проверяем модули приложения...")
    if not check_app_modules():
        return 1
    
    # Создаем директории
    print("\n📁 Создаем директории...")
    create_directories()
    
    # Инициализируем базу данных
    print("\n💾 Инициализируем базу данных...")
    try:
        from app.storage.db import init_db
        init_db()
        print("✅ База данных готова")
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return 1
    
    # Запускаем приложение
    print("\n🌐 Запускаем веб-сервер...")
    print("=" * 50)
    print("🎉 Приложение запущено!")
    print("📱 Откройте браузер: http://127.0.0.1:8080")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        from app.main import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
