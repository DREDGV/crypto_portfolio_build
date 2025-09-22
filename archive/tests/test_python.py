#!/usr/bin/env python3
"""
Простой тест Python
"""

print("🐍 Тест Python")
print(f"Версия Python: {__import__('sys').version}")
print(f"Путь к Python: {__import__('sys').executable}")

try:
    import nicegui
    print("✅ NiceGUI установлен")
except ImportError:
    print("❌ NiceGUI НЕ установлен")

try:
    import sqlmodel
    print("✅ SQLModel установлен")
except ImportError:
    print("❌ SQLModel НЕ установлен")

try:
    import httpx
    print("✅ HTTPX установлен")
except ImportError:
    print("❌ HTTPX НЕ установлен")

print("\n🎯 Для установки зависимостей выполните:")
print("python -m pip install nicegui sqlmodel httpx pydantic python-dotenv")
