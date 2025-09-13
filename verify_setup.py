#!/usr/bin/env python3
"""
Скрипт для проверки настройки приложения
"""

import sys
import os

def check_python_version():
    """Проверяет версию Python"""
    print(f"🐍 Python версия: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        return False
    print("✅ Версия Python подходит")
    return True

def check_dependencies():
    """Проверяет установленные зависимости"""
    print("\n📦 Проверяем зависимости...")
    
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
            if package == 'dotenv':
                import python_dotenv
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Запустите: pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def check_app_modules():
    """Проверяет импорт модулей приложения"""
    print("\n🔧 Проверяем модули приложения...")
    
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
    
    print("✅ Все модули приложения импортируются")
    return True

def check_database():
    """Проверяет базу данных"""
    print("\n💾 Проверяем базу данных...")
    
    try:
        from app.storage.db import init_db, DB_PATH
        init_db()
        
        if os.path.exists(DB_PATH):
            print("✅ База данных создана")
        else:
            print("❌ База данных не найдена")
            return False
            
        # Проверяем, что можем работать с данными
        from app.core.services import list_transactions
        transactions = list_transactions()
        print(f"✅ В базе {len(transactions)} сделок")
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False
    
    return True

def check_api():
    """Проверяет API цен"""
    print("\n🌐 Проверяем API цен...")
    
    try:
        from app.adapters.prices import get_current_price
        price = get_current_price('BTC')
        
        if price:
            print(f"✅ API цен работает (BTC: ${price:,.2f})")
        else:
            print("⚠️ API цен недоступен (возможно, нет интернета)")
            
    except Exception as e:
        print(f"❌ Ошибка API цен: {e}")
        return False
    
    return True

def main():
    """Основная функция проверки"""
    print("=" * 50)
    print("🔍 ПРОВЕРКА НАСТРОЙКИ ПРИЛОЖЕНИЯ")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_app_modules,
        check_database,
        check_api
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("Приложение готово к запуску!")
        print("\nЗапустите: quick_start.bat")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ!")
        print("Исправьте ошибки и запустите проверку снова")
    print("=" * 50)

if __name__ == "__main__":
    main()
