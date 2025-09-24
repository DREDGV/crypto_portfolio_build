#!/usr/bin/env python3
"""
Отладка проблем с редактированием источников
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

def debug_sources():
    print("🔍 Отладка проблем с редактированием источников")
    print("=" * 60)
    
    try:
        from app.core.services import get_sources_with_frequency, list_transactions
        
        # Проверяем транзакции
        print("📋 Проверяем транзакции в базе данных:")
        transactions = list_transactions()
        print(f"Всего транзакций: {len(transactions)}")
        
        if transactions:
            print("Первые 3 транзакции:")
            for i, tx in enumerate(transactions[:3], 1):
                print(f"  {i}. {tx.get('coin', 'N/A')} - {tx.get('source', 'N/A')}")
        
        # Проверяем источники
        print("\n📋 Проверяем источники:")
        sources = get_sources_with_frequency()
        print(f"Всего источников: {len(sources)}")
        
        for i, (source, freq) in enumerate(sources[:5], 1):
            print(f"  {i}. {source} ({freq} раз)")
        
        print("\n✅ Отладка завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка отладки: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sources()
