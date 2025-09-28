#!/usr/bin/env python3
"""Скрипт для миграции базы данных с новыми таблицами"""

import os
import shutil
from datetime import datetime

def backup_database():
    """Создает резервную копию базы данных"""
    db_path = "data/portfolio.db"
    if os.path.exists(db_path):
        backup_path = f"data/backups/portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.makedirs("data/backups", exist_ok=True)
        shutil.copy2(db_path, backup_path)
        print(f"✅ Создана резервная копия: {backup_path}")
        return backup_path
    return None

def recreate_database():
    """Пересоздает базу данных с новыми таблицами"""
    try:
        print("🔄 Пересоздание базы данных...")
        
        # Создаем резервную копию
        backup_path = backup_database()
        
        # Удаляем старую базу данных
        db_path = "data/portfolio.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Старая база данных удалена")
        
        # Инициализируем новую базу данных
        from app.storage.db import init_db
        init_db()
        print("✅ Новая база данных создана")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка пересоздания базы данных: {e}")
        return False

if __name__ == "__main__":
    success = recreate_database()
    if success:
        print("\n🎉 База данных успешно пересоздана!")
        print("Теперь можно запустить инициализацию брокера")
    else:
        print("\n❌ Ошибка пересоздания базы данных!")
