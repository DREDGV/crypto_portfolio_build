#!/usr/bin/env python3
"""Проверка статуса приложения без подтверждений"""

import subprocess
import sys
import time

import requests


def check_status():
    """Проверяет статус приложения"""
    try:
        response = requests.get("http://127.0.0.1:8080", timeout=2)
        if response.status_code == 200:
            print("✅ Приложение работает на http://127.0.0.1:8080")
            return True
        else:
            print(f"⚠️ Приложение отвечает с кодом {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Приложение не запущено")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def kill_existing_processes():
    """Завершает существующие процессы на порту 8080"""
    try:
        # Находим процессы на порту 8080
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True, timeout=10
        )

        lines = result.stdout.split("\n")
        pids = []

        for line in lines:
            if ":8080" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    pids.append(pid)

        # Завершаем процессы
        for pid in pids:
            try:
                subprocess.run(
                    ["taskkill", "/PID", pid, "/F"], capture_output=True, timeout=5
                )
                print(f"🔄 Завершен процесс {pid}")
            except:
                pass

    except Exception as e:
        print(f"⚠️ Не удалось завершить процессы: {e}")


def main():
    print("🔍 Проверка статуса приложения...")

    if check_status():
        print("✅ Все готово!")
    else:
        print("🔄 Попытка освободить порт...")
        kill_existing_processes()
        time.sleep(2)

        if check_status():
            print("✅ Порт освобожден!")
        else:
            print("❌ Требуется перезапуск приложения")


if __name__ == "__main__":
    main()
