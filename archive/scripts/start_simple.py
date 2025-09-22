#!/usr/bin/env python3
"""
Максимально простой запуск приложения
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 Простой запуск Crypto Portfolio Manager")
    print("=" * 40)
    
    # Проверяем виртуальное окружение
    if not os.path.exists(".venv/Scripts/python.exe"):
        print("❌ Виртуальное окружение не найдено!")
        print("Создайте его командой: python -m venv .venv")
        return
    
    # Останавливаем старые процессы
    print("🔄 Останавливаем старые процессы...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, check=False)
        time.sleep(1)
    except:
        pass
    
    # Запускаем приложение
    print("🚀 Запускаем приложение...")
    print("🌐 Откройте http://localhost:8086 в браузере")
    print("=" * 40)
    
    try:
        subprocess.run([".venv/Scripts/python.exe", "app/main_step2.py"])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
