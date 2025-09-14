#!/usr/bin/env python3
"""Проверка статуса приложения"""

import time

import requests


def check_app():
    try:
        response = requests.get("http://127.0.0.1:8080", timeout=2)
        if response.status_code == 200:
            print("OK: Приложение работает на http://127.0.0.1:8080")
            return True
        else:
            print(f"ERROR: Приложение отвечает с кодом {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Приложение не запущено")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    check_app()
