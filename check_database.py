#!/usr/bin/env python3
"""Проверка состояния базы данных"""


def check_database():
    """Проверяет состояние базы данных"""
    print("🔍 Проверка состояния базы данных...")

    try:
        from sqlmodel import Session, text

        from app.storage.db import engine, init_db

        # Инициализируем БД
        init_db()
        print("✅ База данных инициализирована")

        # Проверяем таблицы
        with Session(engine) as session:
            result = session.exec(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result]
            print(f"📋 Таблицы в БД: {tables}")

            # Проверяем содержимое таблиц
            for table in tables:
                try:
                    count_result = session.exec(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.first()
                    print(f"   📊 {table}: {count} записей")
                except Exception as e:
                    print(f"   ❌ Ошибка проверки {table}: {e}")

        return True

    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    check_database()
