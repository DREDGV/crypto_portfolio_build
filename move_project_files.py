#!/usr/bin/env python3
"""
Переместить все файлы проекта из crypto_portfolio_build в корневую папку
"""
import os
import shutil
import sys

def move_files():
    source_dir = "crypto_portfolio_build"
    target_dir = "."
    
    if not os.path.exists(source_dir):
        print(f"Папка {source_dir} не найдена")
        return
    
    print(f"Перемещаем файлы из {source_dir} в {target_dir}")
    
    # Получаем все элементы из исходной папки
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        target_path = os.path.join(target_dir, item)
        
        # Если файл/папка уже существует в целевой папке, удаляем его
        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
            print(f"Удален существующий: {item}")
        
        # Перемещаем элемент
        shutil.move(source_path, target_path)
        print(f"Перемещен: {item}")
    
    # Удаляем пустую папку crypto_portfolio_build
    if not os.listdir(source_dir):
        os.rmdir(source_dir)
        print(f"Удалена пустая папка: {source_dir}")
    
    print("✅ Все файлы успешно перемещены!")
    print("Теперь можно запускать приложение из корневой папки")

if __name__ == "__main__":
    try:
        move_files()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
