#!/usr/bin/env python3
"""Тест импорта pages.py"""

import sys
import traceback

try:
    print("Попытка импорта app.ui.pages...")
    import app.ui.pages

    print("OK: Импорт успешен!")
except SyntaxError as e:
    print(f"ERROR: Ошибка синтаксиса в строке {e.lineno}:")
    print(f"   {e.text}")
    print(f"   {' ' * (e.offset-1) if e.offset else ''}^")
    print(f"   {e.msg}")
except Exception as e:
    print(f"ERROR: Ошибка импорта: {e}")
    traceback.print_exc()
