#!/usr/bin/env python3
"""
Тест редактирования источников
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from app.core.services import (
    get_sources_with_frequency,
    update_source_name,
    add_transaction
)
from app.core.models import TransactionIn

def test_edit_sources():
    print("🧪 Тест редактирования источников")
    print("=" * 50)
    
    # Получаем текущие источники
    print("📋 Текущие источники:")
    sources = get_sources_with_frequency()
    for i, (source, freq) in enumerate(sources[:5], 1):
        print(f"  {i}. {source} ({freq} раз)")
    
    # Добавляем тестовую транзакцию с источником "TestExchange"
    print("\n➕ Добавляем тестовую транзакцию...")
    try:
        test_transaction = TransactionIn(
            coin="BTC",
            type="buy",
            quantity=0.001,
            price=50000.0,
            strategy="long",
            source="TestExchange",
            notes="Тестовая транзакция"
        )
        add_transaction(test_transaction)
        print("✅ Тестовая транзакция добавлена")
    except Exception as e:
        print(f"❌ Ошибка добавления транзакции: {e}")
    
    # Проверяем источники после добавления
    print("\n📋 Источники после добавления транзакции:")
    sources = get_sources_with_frequency()
    for i, (source, freq) in enumerate(sources[:5], 1):
        print(f"  {i}. {source} ({freq} раз)")
    
    # Пытаемся переименовать источник
    print("\n✏️ Тестируем переименование источника...")
    old_name = "TestExchange"
    new_name = "TestExchangeRenamed"
    
    success = update_source_name(old_name, new_name)
    if success:
        print(f"✅ Источник '{old_name}' переименован в '{new_name}'")
    else:
        print(f"❌ Ошибка переименования источника")
    
    # Проверяем источники после переименования
    print("\n📋 Источники после переименования:")
    sources = get_sources_with_frequency()
    for i, (source, freq) in enumerate(sources[:5], 1):
        print(f"  {i}. {source} ({freq} раз)")
    
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    test_edit_sources()
