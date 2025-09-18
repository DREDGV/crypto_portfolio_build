#!/usr/bin/env python3
"""
Простой тест функции update_source_name
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.services import update_source_name, get_sources_with_frequency

def test_update():
    print("🧪 Тест функции update_source_name")
    print("=" * 40)
    
    # Получаем текущие источники
    print("До обновления:")
    sources = get_sources_with_frequency()
    for source, freq in sources[:3]:
        print(f"  {source} ({freq} раз)")
    
    # Пытаемся обновить первый источник
    if sources:
        old_name = sources[0][0]
        new_name = f"{old_name}_TEST"
        
        print(f"\nОбновляем: {old_name} -> {new_name}")
        success = update_source_name(old_name, new_name)
        print(f"Результат: {'Успех' if success else 'Ошибка'}")
        
        # Проверяем результат
        print("\nПосле обновления:")
        sources = get_sources_with_frequency()
        for source, freq in sources[:3]:
            print(f"  {source} ({freq} раз)")
    
    print("\n✅ Тест завершен")

if __name__ == "__main__":
    test_update()
