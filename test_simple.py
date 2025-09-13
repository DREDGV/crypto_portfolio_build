#!/usr/bin/env python3
"""
Простой тест приложения
"""

print("🔍 Тестируем импорт модулей...")

try:
    from app.core.models import Transaction, TransactionIn
    print("✅ Модели данных")
except Exception as e:
    print(f"❌ Модели данных: {e}")

try:
    from app.core.services import add_transaction, list_transactions, positions_fifo
    print("✅ Сервисы")
except Exception as e:
    print(f"❌ Сервисы: {e}")

try:
    from app.adapters.prices import get_current_price
    print("✅ Адаптер цен")
except Exception as e:
    print(f"❌ Адаптер цен: {e}")

try:
    from app.storage.db import init_db
    print("✅ База данных")
    init_db()
    print("✅ База данных инициализирована")
except Exception as e:
    print(f"❌ База данных: {e}")

try:
    from app.ui.pages import portfolio_page
    print("✅ UI страницы")
except Exception as e:
    print(f"❌ UI страницы: {e}")

print("\n🎯 Тестируем NiceGUI...")
try:
    from nicegui import ui
    print("✅ NiceGUI импортирован")
    
    # Создаем простую страницу
    @ui.page('/')
    def home():
        ui.label('Тест приложения').classes('text-2xl')
        ui.label('Если вы видите это сообщение, приложение работает!')
    
    print("✅ Страница создана")
    print("🌐 Запускаем сервер на http://127.0.0.1:8080")
    ui.run(host='127.0.0.1', port=8080, show=True)
    
except Exception as e:
    print(f"❌ NiceGUI: {e}")
    import traceback
    traceback.print_exc()
