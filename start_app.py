#!/usr/bin/env python3
"""Запуск приложения"""

import subprocess
import sys
import time


def start_app():
    try:
        print("Запуск приложения...")
        process = subprocess.Popen(
            [sys.executable, "-m", "app.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Ждем немного
        time.sleep(3)

        # Проверяем, запустилось ли
        if process.poll() is None:
            print("OK: Приложение запущено")
            print("Откройте http://127.0.0.1:8080 в браузере")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"ERROR: Приложение не запустилось")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None

    except Exception as e:
        print(f"ERROR: {e}")
        return None


if __name__ == "__main__":
    start_app()
