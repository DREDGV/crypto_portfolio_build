#!/usr/bin/env python3
"""
Минимальный тест приложения
"""
import sys
import os

# Добавляем текущую папку в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Проверяем импорты...")
    
    # Проверяем NiceGUI
    from nicegui import ui
    print("✅ NiceGUI импортирован успешно")
    
    # Проверяем наши модули
    from app.core.models import Transaction, TransactionIn
    print("✅ Модели импортированы успешно")
    
    from app.core.services import add_transaction, list_transactions
    print("✅ Сервисы импортированы успешно")
    
    from app.storage.db import init_db
    print("✅ База данных импортирована успешно")
    
    print("\n🎉 Все импорты работают!")
    
    # Создаем простое приложение
    @ui.page('/')
    def main_page():
        ui.label('Тест приложения').classes('text-2xl font-bold')
        ui.label('Если вы видите это сообщение, приложение работает!')
        
        # Показываем информацию о базе данных
        init_db()
        transactions = list_transactions()
        ui.label(f'Сделок в базе: {len(transactions)}')
    
    print("🚀 Запускаем приложение...")
    ui.run(host='127.0.0.1', port=8080, show=True, title='Test App')
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
