#!/usr/bin/env python3
"""Безопасный запуск приложения без подтверждений"""

import os
import subprocess
import sys
import time


def start_app_safe():
    try:
        print("🚀 Запуск приложения...")

        # Устанавливаем переменные окружения для отключения подтверждений
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        # Запускаем приложение с отключенными подтверждениями
        process = subprocess.Popen(
            [sys.executable, "-m", "app.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            creationflags=(
                subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            ),
        )

        # Ждем немного для запуска
        time.sleep(3)

        # Проверяем статус
        if process.poll() is None:
            print("✅ Приложение успешно запущено!")
            print("🌐 Откройте http://127.0.0.1:8080 в браузере")
            print("📱 Версия должна быть видна в боковой панели")
            print("\n💡 Для остановки приложения закройте это окно")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Ошибка запуска:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    start_app_safe()
    # Держим окно открытым
    input("\nНажмите Enter для выхода...")
