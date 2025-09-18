#!/usr/bin/env python3
"""
Перезапуск приложения с исправлениями
"""

import subprocess
import sys
import time

def main():
    print("🔄 Перезапуск приложения с исправлениями...")
    print("=" * 50)
    
    # Останавливаем все процессы Python
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, check=False)
        print("✅ Остановлены предыдущие процессы")
    except:
        pass
    
    # Ждем немного
    time.sleep(2)
    
    # Запускаем приложение
    print("🚀 Запуск исправленной версии...")
    try:
        subprocess.run([sys.executable, "app/main_step2.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
