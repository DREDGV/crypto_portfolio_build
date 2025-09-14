#!/usr/bin/env python3
"""Тест приложения"""

import subprocess
import sys
import time


def test_app():
    try:
        # Запускаем приложение
        print("Запуск приложения...")
        process = subprocess.Popen(
            [sys.executable, "-m", "app.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Ждем
        time.sleep(5)

        # Проверяем статус
        if process.poll() is None:
            print("OK: Приложение запущено")
            print("Откройте http://127.0.0.1:8080 в браузере")
            print("Версия должна быть видна в боковой панели")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"ERROR: Приложение не запустилось")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    test_app()
