#!/usr/bin/env python3
"""Скрипт для обновления приложения с GitHub"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
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
    print("🚀 Обновление приложения с GitHub...")
    print("=" * 50)
    
    # Получаем текущую дату
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Проверяем статус
    print("📊 Проверка текущего статуса...")
    run_command("git status", "Статус репозитория")
    
    # 2. Сохраняем локальные изменения (если есть)
    print("\n💾 Сохранение локальных изменений...")
    run_command("git stash push -m 'Локальные изменения перед обновлением'", "Сохранение изменений")
    
    # 3. Получаем последние изменения
    print("\n📥 Загрузка изменений с GitHub...")
    if not run_command("git fetch origin", "Получение изменений"):
        return False
    
    # 4. Обновляем локальную ветку
    print("\n🔄 Обновление локальной ветки...")
    if not run_command("git pull origin master", "Обновление ветки"):
        return False
    
    # 5. Получаем теги
    print("\n🏷️ Обновление тегов...")
    run_command("git fetch --tags", "Получение тегов")
    
    # 6. Показываем последние коммиты
    print("\n📋 Последние коммиты:")
    run_command("git log --oneline -5", "История коммитов")
    
    # 7. Показываем текущую версию
    print("\n📱 Текущая версия:")
    try:
        with open("VERSION", "r") as f:
            version = f.read().strip()
            print(f"   Версия: {version}")
    except:
        print("   Версия: не определена")
    
    # 8. Показываем последний тег
    print("\n🏷️ Последний тег:")
    run_command("git describe --tags --abbrev=0", "Последний тег")
    
    print("=" * 50)
    print("🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
    print(f"📅 Время обновления: {current_date}")
    print("🔗 Репозиторий обновлен с GitHub")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Приложение успешно обновлено!")
        print("\n🚀 Для запуска приложения используйте:")
        print("   python -m app.main")
        print("   или")
        print("   start_app.bat")
    else:
        print("❌ Обновление завершено с ошибками!")
        sys.exit(1)
