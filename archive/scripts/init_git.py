#!/usr/bin/env python3
"""Скрипт для инициализации Git репозитория"""

import subprocess
import sys
import os

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - ошибка")
            if result.stderr.strip():
                print(f"   {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - таймаут")
        return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def main():
    print("🚀 Инициализация Git репозитория...")
    print("=" * 50)
    
    # Проверяем, есть ли уже .git папка
    if os.path.exists('.git'):
        print("✅ Git репозиторий уже инициализирован")
        return True
    
    # 1. Инициализируем Git репозиторий
    if not run_command("git init", "Инициализация Git репозитория"):
        return False
    
    # 2. Настраиваем пользователя (если нужно)
    run_command('git config user.name "Crypto Portfolio Manager"', "Настройка имени пользователя")
    run_command('git config user.email "portfolio@example.com"', "Настройка email")
    
    # 3. Добавляем все файлы
    if not run_command("git add .", "Добавление файлов"):
        return False
    
    # 4. Создаем первый коммит
    if not run_command('git commit -m "feat: Initial commit - Crypto Portfolio Manager v1.4.0"', "Создание первого коммита"):
        return False
    
    print("=" * 50)
    print("🎉 GIT РЕПОЗИТОРИЙ УСПЕШНО ИНИЦИАЛИЗИРОВАН!")
    print("📋 Версия: 1.4.0")
    print("🔗 Готов к работе с Git!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Инициализация завершена успешно!")
    else:
        print("❌ Инициализация завершена с ошибками!")
        sys.exit(1)
