#!/usr/bin/env python3
"""
Запуск Шага 1: Улучшение статистических карточек
"""

import os
import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def main():
    """Запуск первого шага улучшений"""
    print("🚀 Crypto Portfolio Manager - Шаг 1")
    print("=" * 50)
    print("✅ Улучшение статистических карточек")
    print("✅ Добавление градиентов")
    print("✅ Сохранение всей функциональности")
    print("=" * 50)
    
    # Проверяем Python
    print(f"🐍 Python: {sys.version.split()[0]")
    
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
    print("\n🎯 Запуск первого шага...")
    print("🌐 Откройте http://localhost:8086 в браузере")
    print("=" * 50)
    
    try:
        from app.main_step1 import ui
        ui.run(
            host="127.0.0.1",
            port=8086,
            reload=False,
            show=True,
            title="Crypto Portfolio — Step 1",
            favicon="🚀",
        )
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return

if __name__ == "__main__":
    main()
