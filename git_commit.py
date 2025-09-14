#!/usr/bin/env python3
"""
Скрипт для коммита и пуша изменений в GitHub
"""
import subprocess
import sys

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {command}")
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {command}: {e}")
        return False

def main():
    print("🚀 Committing version 1.2.5...")
    
    # Добавляем все файлы
    if not run_command("git add ."):
        print("❌ Failed to add files")
        return
    
    # Коммитим изменения
    commit_message = "v1.2.5: Fix font sizes in About dialog - headers reduced from 48px to normal size, tabs optimized, CSS styles added"
    if not run_command(f'git commit -m "{commit_message}"'):
        print("❌ Failed to commit")
        return
    
    # Пушим в GitHub
    print("📤 Pushing to GitHub...")
    if not run_command("git push origin main"):
        print("❌ Failed to push")
        return
    
    print("✅ Successfully committed and pushed v1.2.5!")

if __name__ == "__main__":
    main()
