#!/usr/bin/env python3
"""
Простой перезапуск приложения
"""

import subprocess
import sys
import time

def main():
    print("🔄 Перезапуск приложения...")
    
    # Останавливаем старые процессы
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, check=False)
        time.sleep(1)
    except:
        pass
    
    # Запускаем приложение
    print("🚀 Запуск...")
    subprocess.run([sys.executable, "app/main_step2.py"])

if __name__ == "__main__":
    main()
