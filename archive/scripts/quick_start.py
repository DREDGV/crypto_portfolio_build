#!/usr/bin/env python3
"""
Быстрый запуск приложения без лишних логов
"""

import os
import subprocess
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def quick_start():
    """Быстрый запуск приложения"""
    print("🚀 Запуск Crypto Portfolio...")

    try:
        # Запускаем приложение в фоне
        process = subprocess.Popen(
            [sys.executable, "-m", "app.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        print("✅ Приложение запущено!")
        print("🌐 Откройте браузер: http://127.0.0.1:8080")
        print("⏹️  Для остановки нажмите Ctrl+C")

        # Ждем завершения
        process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Остановка приложения...")
        process.terminate()
        print("✅ Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    quick_start()
