#!/usr/bin/env python3
"""
Перезапуск с отладочной информацией
"""

import subprocess
import sys
import time

def main():
    print("🔄 Перезапуск с отладочной информацией...")
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
    
    # Запускаем отладку
    print("🔍 Запускаем отладку источников...")
    try:
        subprocess.run([sys.executable, "debug_sources.py"], check=True)
    except Exception as e:
        print(f"❌ Ошибка отладки: {e}")
    
    print("\n🚀 Запускаем приложение...")
    print("🌐 Откройте http://localhost:8086 в браузере")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "app/main_step2.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
