#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы API получения цен
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.adapters.prices import get_current_price, get_price_info


def test_price_api():
    """Тестирует API получения цен"""
    print("🧪 ТЕСТИРОВАНИЕ API ПОЛУЧЕНИЯ ЦЕН")
    print("=" * 50)

    # Тестовые монеты
    test_coins = ["BTC", "ETH", "SOL", "ADA", "DOT", "LINK", "UNI", "MATIC"]

    print(f"📅 Время тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Источник данных: CoinGecko API")
    print(f"💰 Валюта: USD")
    print()

    for coin in test_coins:
        print(f"🔍 Тестируем {coin}...")

        # Тест простой функции
        price = get_current_price(coin)
        if price:
            print(f"   ✅ Цена: ${price:,.2f}")
        else:
            print(f"   ❌ Не удалось получить цену")

        # Тест расширенной функции
        price_info = get_price_info(coin)
        if price_info:
            print(f"   📊 Детали:")
            print(f"      💵 Цена: ${price_info['price']:,.2f}")
            if price_info.get("change_24h") is not None:
                change = price_info["change_24h"]
                if change > 0:
                    print(f"      📈 Изменение за 24ч: +{change:.2f}%")
                elif change < 0:
                    print(f"      📉 Изменение за 24ч: {change:.2f}%")
                else:
                    print(f"      ➡️ Изменение за 24ч: 0.00%")
            else:
                print(f"      ❓ Изменение за 24ч: недоступно")

            if price_info.get("last_updated"):
                last_update = datetime.fromtimestamp(price_info["last_updated"])
                print(
                    f"      🕐 Последнее обновление: {last_update.strftime('%H:%M:%S')}"
                )

            print(f"      💾 Из кэша: {'Да' if price_info.get('cached') else 'Нет'}")
        else:
            print(f"   ❌ Не удалось получить детальную информацию")

        print()

    print("✅ Тестирование завершено!")


if __name__ == "__main__":
    test_price_api()
