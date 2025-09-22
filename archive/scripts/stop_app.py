#!/usr/bin/env python3
"""
Быстрая остановка приложения
"""

import subprocess
import sys


def stop_app():
    """Останавливает приложение"""
    print("🛑 Остановка приложения...")

    try:
        # Останавливаем все Python процессы
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Приложение остановлено")
        else:
            print("⚠️ Процессы не найдены или уже остановлены")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    stop_app()
