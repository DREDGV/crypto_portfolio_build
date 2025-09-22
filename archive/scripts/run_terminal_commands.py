#!/usr/bin/env python3
"""
Скрипт для выполнения команд терминала через Python
Обходит проблемы с терминалом Cursor
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Выполняет команду и возвращает результат"""
    if cwd is None:
        cwd = Path.cwd()
    
    print(f"🔧 Выполняем команду: {command}")
    print(f"📁 Рабочая директория: {cwd}")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            command,
            shell=shell,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print("📤 Вывод:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ Ошибки:")
            print(result.stderr)
        
        print(f"✅ Код завершения: {result.returncode}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Команда превысила время ожидания (30 сек)")
        return False
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        return False

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование: python run_terminal_commands.py <команда>")
        print("Примеры:")
        print("  python run_terminal_commands.py 'git status'")
        print("  python run_terminal_commands.py 'python --version'")
        print("  python run_terminal_commands.py 'dir'")
        return
    
    command = " ".join(sys.argv[1:])
    success = run_command(command)
    
    if success:
        print("🎉 Команда выполнена успешно!")
    else:
        print("💥 Команда завершилась с ошибкой!")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()
