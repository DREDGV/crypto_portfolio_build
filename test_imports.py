#!/usr/bin/env python3
"""Тест импортов приложения"""


def test_imports():
    try:
        print("🔄 Тестируем импорты...")

        # Тест основных модулей
        import app.core.services

        print("✅ app.core.services - OK")

        import app.core.models

        print("✅ app.core.models - OK")

        import app.storage.db

        print("✅ app.storage.db - OK")

        import app.adapters.prices

        print("✅ app.adapters.prices - OK")

        # Тест UI модулей
        import app.ui.pages_step2

        print("✅ app.ui.pages_step2 - OK")

        print("\n🎉 ВСЕ ИМПОРТЫ УСПЕШНЫ!")
        return True

    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False


if __name__ == "__main__":
    test_imports()
