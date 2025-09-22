#!/usr/bin/env python3
"""
Простой тест для диагностики проблем
"""

print("🚀 Начинаем диагностику...")

try:
    print("1. Проверяем Python...")
    import sys
    print(f"   Python версия: {sys.version}")
    
    print("2. Проверяем основные модули...")
    import os
    print("   ✅ os")
    
    print("3. Проверяем NiceGUI...")
    import nicegui
    print(f"   ✅ nicegui версия: {nicegui.__version__}")
    
    print("4. Проверяем SQLModel...")
    import sqlmodel
    print("   ✅ sqlmodel")
    
    print("5. Проверяем HTTPX...")
    import httpx
    print("   ✅ httpx")
    
    print("6. Проверяем импорты приложения...")
    from app.core.version import get_app_info
    app_info = get_app_info()
    print(f"   ✅ Приложение: {app_info['name']} v{app_info['version']}")
    
    print("7. Проверяем базу данных...")
    from app.storage.db import init_db
    init_db()
    print("   ✅ База данных инициализирована")
    
    print("\n🎉 Все проверки пройдены успешно!")
    print("Приложение готово к запуску.")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
