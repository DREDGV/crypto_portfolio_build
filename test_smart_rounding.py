#!/usr/bin/env python3
"""
Тестовый скрипт для проверки умного округления цен
"""

import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.adapters.prices import get_aggregated_price, get_smart_rounded_price


def test_smart_rounding():
    """Тестирует умное округление цен"""
    print("🧪 ТЕСТИРОВАНИЕ УМНОГО ОКРУГЛЕНИЯ ЦЕН")
    print("=" * 50)

    # Тестовые цены для разных типов монет
    test_cases = [
        # (символ, цена, ожидаемое округление)
        ("BTC", 115866.254321, 2),  # Дорогие монеты - 2 знака
        ("ETH", 4670.54321, 2),  # Дорогие монеты - 2 знака
        ("LINK", 24.804866932415734, 2),  # Средние монеты - 2 знака
        ("SOL", 247.523456, 2),  # Средние монеты - 2 знака
        ("ADA", 0.9203456, 4),  # Дешевые монеты - 4 знака
        ("DOGE", 0.28854321, 4),  # Дешевые монеты - 4 знака
        ("SHIB", 0.000023456, 6),  # Очень дешевые - 6 знаков
    ]

    print("📊 Тестирование округления:")
    print()

    for symbol, price, expected_decimals in test_cases:
        rounded = get_smart_rounded_price(price, symbol)
        actual_decimals = len(str(rounded).split(".")[-1]) if "." in str(rounded) else 0

        print(f"🔍 {symbol}: ${price:,.8f} → ${rounded:,.8f}")
        print(f"   Ожидаемо: {expected_decimals} знаков, получено: {actual_decimals}")

        if actual_decimals == expected_decimals:
            print(f"   ✅ Правильно округлено")
        else:
            print(f"   ❌ Неправильное округление")
        print()

    print("🧪 Тестирование реальных данных:")
    print()

    # Тестируем на реальных данных
    test_coins = ["LINK", "BTC", "ETH", "ADA"]

    for coin in test_coins:
        print(f"🔍 Тестируем {coin}...")
        result = get_aggregated_price(coin)

        if result:
            price = result["price"]
            print(f"   💵 Цена: ${price}")
            print(f"   📊 Источников: {result['source_count']}")
            print(f"   🏢 Источники: {', '.join(result['sources'])}")

            if "price_range" in result:
                price_range = result["price_range"]
                print(f"   📊 Диапазон: ${price_range['min']} - ${price_range['max']}")
                print(f"   📏 Разброс: ${price_range['spread']}")
        else:
            print(f"   ❌ Не удалось получить данные")

        print()

    print("✅ Тестирование завершено!")


if __name__ == "__main__":
    test_smart_rounding()
