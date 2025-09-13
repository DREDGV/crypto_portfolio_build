#!/usr/bin/env python3
"""
Скрипт для создания тестовых данных
"""

from app.core.services import add_transaction
from app.core.models import TransactionIn
import datetime

def create_test_data():
    """Создает тестовые данные для демонстрации"""
    
    print("Создаем тестовые данные...")
    
    # Добавляем тестовые сделки
    test_txs = [
        TransactionIn(
            coin='BTC', 
            type='buy', 
            quantity=0.1, 
            price=45000, 
            strategy='long', 
            source='Binance', 
            notes='Тестовая покупка'
        ),
        TransactionIn(
            coin='BTC', 
            type='buy', 
            quantity=0.05, 
            price=42000, 
            strategy='long', 
            source='Binance', 
            notes='Добавка'
        ),
        TransactionIn(
            coin='ETH', 
            type='buy', 
            quantity=1.0, 
            price=3000, 
            strategy='mid', 
            source='Coinbase', 
            notes='Средний срок'
        ),
        TransactionIn(
            coin='ETH', 
            type='buy', 
            quantity=0.5, 
            price=2800, 
            strategy='mid', 
            source='Coinbase', 
            notes='Добавка'
        ),
        TransactionIn(
            coin='SOL', 
            type='buy', 
            quantity=10, 
            price=100, 
            strategy='short', 
            source='FTX', 
            notes='Краткосрок'
        ),
        TransactionIn(
            coin='BTC', 
            type='sell', 
            quantity=0.03, 
            price=50000, 
            strategy='long', 
            source='Binance', 
            notes='Частичная продажа'
        ),
    ]
    
    success_count = 0
    for tx in test_txs:
        try:
            add_transaction(tx)
            print(f'✅ Добавлена сделка: {tx.coin} {tx.type} {tx.quantity} @ ${tx.price:,}')
            success_count += 1
        except Exception as e:
            print(f'❌ Ошибка добавления сделки: {e}')
    
    print(f'\n🎉 Создано {success_count} тестовых сделок!')

if __name__ == "__main__":
    create_test_data()
