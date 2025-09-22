#!/usr/bin/env python3
"""
Запуск улучшенной версии Crypto Portfolio Manager
Полный функционал + новый дизайн
"""

import os
import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def main():
    """Запуск улучшенной версии приложения"""
    print("🚀 Запуск Crypto Portfolio Manager - Улучшенная версия")
    print("=" * 60)
    print("✅ Новый дизайн + Полный функционал")
    print("✅ Все детали ввода сделок сохранены")
    print("=" * 60)
    
    # Проверяем Python
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Проверяем зависимости
    required_modules = ["nicegui", "sqlmodel", "httpx", "pydantic", "dotenv"]
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError:
            print(f"❌ {module} - НЕ УСТАНОВЛЕН")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Отсутствуют модули: {', '.join(missing_modules)}")
        print("Установите их командой:")
        print(f"pip install {' '.join(missing_modules)}")
        return
    
    # Запускаем приложение
    print("\n🎯 Запуск улучшенной версии...")
    print("🌐 Откройте http://localhost:8084 в браузере")
    print("=" * 60)
    
    try:
        from app.main_enhanced import ui
        ui.run(
            host="127.0.0.1",
            port=8084,
            reload=False,
            show=True,
            title="Crypto Portfolio — Enhanced",
            favicon="🚀",
        )
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return

if __name__ == "__main__":
    main()
