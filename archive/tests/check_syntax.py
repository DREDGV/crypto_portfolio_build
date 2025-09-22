#!/usr/bin/env python3
"""Проверка синтаксиса файла pages.py"""

try:
    import app.ui.pages

    print("✅ Синтаксис корректен")
except SyntaxError as e:
    print(f"❌ Ошибка синтаксиса: {e}")
    print(f"Строка {e.lineno}: {e.text}")
except Exception as e:
    print(f"❌ Другая ошибка: {e}")
