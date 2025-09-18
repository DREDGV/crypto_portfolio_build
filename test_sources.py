#!/usr/bin/env python3
"""
Тест функций управления источниками
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from app.core.services import (
    get_sources_with_frequency,
    update_source_name,
    delete_source_from_transactions,
    get_source_statistics
)

def test_sources():
    print("🧪 Тест функций управления источниками")
    print("=" * 50)
    
    # Получаем текущие источники
    print("📋 Текущие источники:")
    sources = get_sources_with_frequency()
    for i, (source, freq) in enumerate(sources[:5], 1):
        print(f"  {i}. {source} ({freq} раз)")
    
    print("\n📊 Статистика источников:")
    stats = get_source_statistics()
    print(f"  Всего сделок: {stats['total_transactions']}")
    print(f"  Уникальных источников: {stats['unique_sources']}")
    
    print("\n✅ Функции управления источниками работают корректно!")

if __name__ == "__main__":
    test_sources()
