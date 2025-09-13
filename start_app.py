#!/usr/bin/env python3
"""
Простой скрипт для запуска приложения
"""

import sys
import os

def main():
    print("🚀 Запуск Crypto Portfolio Manager...")
    print("=" * 50)
    
    # Проверяем Python
    print(f"🐍 Python версия: {sys.version}")
    
    # Проверяем зависимости
    print("\n📦 Проверяем зависимости...")
    try:
        import nicegui
        print("✅ NiceGUI")
    except ImportError:
        print("❌ NiceGUI не установлен")
        print("Установите: pip install nicegui")
        return
    
    try:
        import sqlmodel
        print("✅ SQLModel")
    except ImportError:
        print("❌ SQLModel не установлен")
        print("Установите: pip install sqlmodel")
        return
    
    try:
        import httpx
        print("✅ httpx")
    except ImportError:
        print("❌ httpx не установлен")
        print("Установите: pip install httpx")
        return
    
    # Проверяем модули приложения
    print("\n🔧 Проверяем модули приложения...")
    try:
        from app.core.models import Transaction, TransactionIn
        print("✅ Модели данных")
    except ImportError as e:
        print(f"❌ Модели данных: {e}")
        return
    
    try:
        from app.core.services import add_transaction, list_transactions, positions_fifo
        print("✅ Сервисы")
    except ImportError as e:
        print(f"❌ Сервисы: {e}")
        return
    
    try:
        from app.adapters.prices import get_current_price
        print("✅ Адаптер цен")
    except ImportError as e:
        print(f"❌ Адаптер цен: {e}")
        return
    
    try:
        from app.storage.db import init_db
        print("✅ База данных")
    except ImportError as e:
        print(f"❌ База данных: {e}")
        return
    
    try:
        from app.ui.pages import portfolio_page
        print("✅ UI страницы")
    except ImportError as e:
        print(f"❌ UI страницы: {e}")
        return
    
    # Инициализируем базу данных
    print("\n💾 Инициализируем базу данных...")
    try:
        init_db()
        print("✅ База данных готова")
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return
    
    # Запускаем приложение
    print("\n🌐 Запускаем веб-сервер...")
    print("=" * 50)
    print("🎉 Приложение запущено!")
    print("📱 Откройте браузер: http://127.0.0.1:8080")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        from app.main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
