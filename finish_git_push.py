#!/usr/bin/env python3
"""Завершение git push операций"""

import subprocess
import sys


def run_git_command(command, description):
    """Выполняет git команду"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
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
    print("🚀 Завершаем git операции...")
    print("=" * 40)

    # 1. Создаем тег
    if not run_git_command(
        'git tag -a v1.3.0 -m "Версия 1.3.0: Поддержка акций"', "Создание тега v1.3.0"
    ):
        print("⚠️ Продолжаем без тега...")

    # 2. Пушим изменения
    if not run_git_command("git push origin master", "Пуш изменений"):
        return False

    # 3. Пушим теги
    if not run_git_command("git push origin --tags", "Пуш тегов"):
        print("⚠️ Теги не удалось отправить, но изменения отправлены")

    print("=" * 40)
    print("🎉 ОПЕРАЦИИ ЗАВЕРШЕНЫ!")
    print("📋 Версия: 1.3.0")
    print("🔗 Изменения отправлены на GitHub")
    print("=" * 40)

    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Все готово!")
    else:
        print("❌ Есть ошибки!")
        sys.exit(1)

