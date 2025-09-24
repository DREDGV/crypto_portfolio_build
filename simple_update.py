#!/usr/bin/env python3
"""Простое обновление с GitHub"""

import subprocess
import sys


def run_git_command(command, description):
    """Выполняет git команду"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=60
        )
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
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False


def main():
    print("🚀 Простое обновление с GitHub...")
    print("=" * 40)

    # 1. Получаем изменения
    if not run_git_command("git fetch origin", "Получение изменений"):
        return False

    # 2. Обновляем ветку
    if not run_git_command("git pull origin master", "Обновление ветки"):
        return False

    # 3. Получаем теги
    run_git_command("git fetch --tags", "Получение тегов")

    # 4. Показываем статус
    run_git_command("git status", "Текущий статус")

    # 5. Показываем версию
    try:
        with open("VERSION", "r") as f:
            version = f.read().strip()
            print(f"\n📱 Текущая версия: {version}")
    except:
        print("\n📱 Версия: не определена")

    print("=" * 40)
    print("🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 40)

    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Приложение обновлено!")
    else:
        print("❌ Есть ошибки!")
        sys.exit(1)
