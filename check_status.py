#!/usr/bin/env python3
"""
Быстрая проверка статуса приложения
"""

import socket
import subprocess
import sys


def check_port(port=8080):
    """Проверяет, занят ли порт"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            return result == 0
    except:
        return False


def check_python_processes():
    """Проверяет запущенные Python процессы"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe"],
            capture_output=True,
            text=True,
        )
        return "python.exe" in result.stdout
    except:
        return False


def main():
    """Основная функция проверки"""
    print("🔍 ПРОВЕРКА СТАТУСА ПРИЛОЖЕНИЯ")
    print("=" * 40)

    # Проверяем порт
    port_status = check_port(8080)
    print(f"🌐 Порт 8080: {'✅ Занят' if port_status else '❌ Свободен'}")

    # Проверяем Python процессы
    python_running = check_python_processes()
    print(f"🐍 Python процессы: {'✅ Запущены' if python_running else '❌ Не найдены'}")

    # Общий статус
    if port_status:
        print("\n✅ Приложение работает!")
        print("🌐 Откройте: http://127.0.0.1:8080")
    else:
        print("\n❌ Приложение не запущено")
        print("🚀 Запустите: python quick_start.py")


if __name__ == "__main__":
    main()
