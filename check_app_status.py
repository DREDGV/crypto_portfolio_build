#!/usr/bin/env python3
"""Проверка статуса приложения"""

import time

import requests


def check_app():
    try:
        response = requests.get("http://127.0.0.1:8080", timeout=3)
        if response.status_code == 200:
            print("✅ Приложение работает на http://127.0.0.1:8080")
            print("🌐 Откройте браузер и перейдите по этой ссылке")
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


if __name__ == "__main__":
    print("🔍 Проверка статуса приложения...")
    check_app()
