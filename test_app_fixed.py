#!/usr/bin/env python3
"""
Тестовое приложение для проверки исправлений
"""
import os
import sys

# Добавляем текущую папку в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nicegui import ui
    from app.core.services import list_transactions
    from app.storage.db import init_db
    
    print("🔍 Проверяем данные...")
    
    # Инициализируем БД
    init_db()
    
    # Получаем транзакции
    transactions = list_transactions()
    print(f"✅ Найдено транзакций: {len(transactions)}")
    
    # Проверяем первую транзакцию
    if transactions:
        first_tx = transactions[0]
        print(f"✅ Первая транзакция: {first_tx}")
        
        # Проверяем типы данных
        for key, value in first_tx.items():
            print(f"  {key}: {type(value).__name__} = {value}")
    
    # Создаем простое приложение
    @ui.page('/')
    def main_page():
        ui.label('Тест приложения').classes('text-2xl font-bold')
        ui.label('Если вы видите это сообщение, приложение работает!')
        
        # Показываем информацию о транзакциях
        ui.label(f'Сделок в базе: {len(transactions)}')
        
        if transactions:
            ui.label('Первая сделка:')
            first_tx = transactions[0]
            ui.label(f"  {first_tx['coin']} {first_tx['type']} {first_tx['quantity']} @ ${first_tx['price']}")
    
    print("🚀 Запускаем приложение на порту 8081...")
    ui.run(host='127.0.0.1', port=8081, show=True, title='Test App Fixed')
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
