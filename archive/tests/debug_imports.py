#!/usr/bin/env python3
"""
Отладка импортов приложения
"""

import sys
import os
from pathlib import Path

print("🔍 Отладка импортов...")
print(f"Python версия: {sys.version}")
print(f"Текущая директория: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}")

try:
    print("\n1. Проверяем базовые импорты...")
    import nicegui
    print(f"✅ NiceGUI: {nicegui.__version__}")
    
    import sqlmodel
    print("✅ SQLModel")
    
    import httpx
    print("✅ HTTPX")
    
    import pydantic
    print(f"✅ Pydantic: {pydantic.__version__}")
    
    print("\n2. Проверяем импорты приложения...")
    
    # Добавляем текущую директорию в путь
    sys.path.insert(0, os.getcwd())
    
    from app.core.version import get_app_info
    print("✅ app.core.version")
    
    from app.storage.db import init_db
    print("✅ app.storage.db")
    
    from app.core.models import Transaction
    print("✅ app.core.models")
    
    from app.core.services import add_transaction
    print("✅ app.core.services")
    
    from app.adapters.prices import get_current_price
    print("✅ app.adapters.prices")
    
    print("\n3. Инициализируем базу данных...")
    init_db()
    print("✅ База данных инициализирована")
    
    print("\n4. Получаем информацию о приложении...")
    app_info = get_app_info()
    print(f"✅ Приложение: {app_info['name']} v{app_info['version']}")
    
    print("\n🎉 Все импорты успешны!")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
