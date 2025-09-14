#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы агрегации цен
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.adapters.prices import get_aggregated_price


def test_aggregated_system():
    """Тестирует систему агрегации цен"""
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ АГРЕГАЦИИ ЦЕН")
    print("=" * 60)

    # Тестовые монеты
    test_coins = ["LINK", "BTC", "ETH", "SOL", "ADA"]

    print(f"📅 Время тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Источники: CoinGecko, Binance, CoinPaprika, Coinbase, Kraken, OKX")
    print(f"💰 Валюта: USD")
    print(f"🔍 Фильтрация: исключение выбросов >20% от медианы")
    print()

    for coin in test_coins:
        print(f"🔍 Тестируем {coin}...")

        # Получаем агрегированные данные
        result = get_aggregated_price(coin)

        if result:
            print(f"   📊 Результат:")
            print(f"      💵 Средняя цена: ${result['price']:,.2f}")
            print(f"      📈 Источников: {result['source_count']}")
            print(f"      🏢 Источники: {', '.join(result['sources'])}")

            if "price_range" in result:
                price_range = result["price_range"]
                print(
                    f"      📊 Диапазон: ${price_range['min']:,.2f} - ${price_range['max']:,.2f}"
                )
                print(f"      📏 Разброс: ${price_range['spread']:,.2f}")

                if price_range["spread"] > 0:
                    spread_percent = (price_range["spread"] / result["price"]) * 100
                    print(f"      📊 Разброс: {spread_percent:.1f}%")

            print(f"      💾 Из кэша: {'Да' if result.get('cached') else 'Нет'}")
        else:
            print(f"   ❌ Не удалось получить данные")

        print()

    print("✅ Тестирование завершено!")


if __name__ == "__main__":
    test_aggregated_system()
