#!/usr/bin/env python3
"""
Тестовый скрипт для проверки альтернативных источников цен
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.adapters.prices import (
    get_current_price_fallback,
    get_price_from_binance,
    get_price_from_coinpaprika,
)


def test_fallback_sources():
    """Тестирует альтернативные источники цен"""
    print("🧪 ТЕСТИРОВАНИЕ АЛЬТЕРНАТИВНЫХ ИСТОЧНИКОВ ЦЕН")
    print("=" * 60)

    # Тестовые монеты
    test_coins = ["LINK", "BTC", "ETH", "SOL", "ADA"]

    print(f"📅 Время тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Источники: CoinGecko, Binance, CoinPaprika")
    print(f"💰 Валюта: USD")
    print()

    for coin in test_coins:
        print(f"🔍 Тестируем {coin}...")

        # Тест Binance
        print(f"   📊 Binance:")
        binance_price = get_price_from_binance(coin)
        if binance_price:
            print(f"      ✅ ${binance_price:,.2f}")
        else:
            print(f"      ❌ Недоступно")

        # Тест CoinPaprika
        print(f"   📊 CoinPaprika:")
        paprika_price = get_price_from_coinpaprika(coin)
        if paprika_price:
            print(f"      ✅ ${paprika_price:,.2f}")
        else:
            print(f"      ❌ Недоступно")

        # Тест Fallback (все источники)
        print(f"   📊 Fallback (все источники):")
        fallback_price = get_current_price_fallback(coin)
        if fallback_price:
            print(f"      ✅ ${fallback_price:,.2f}")
        else:
            print(f"      ❌ Все источники недоступны")

        print()

    print("✅ Тестирование завершено!")


if __name__ == "__main__":
    test_fallback_sources()
