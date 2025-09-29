#!/usr/bin/env python3
"""Добавление демо-данных криптовалют"""


def add_crypto_demo_data():
    """Добавляет демо-данные криптовалют"""
    print("🚀 Добавление демо-данных криптовалют...")

    try:
        from datetime import datetime, timedelta

        from app.core.models import TransactionIn
        from app.core.services import add_transaction

        # Демо-транзакции криптовалют
        demo_transactions = [
            TransactionIn(
                coin="BTC",
                type="buy",
                quantity=0.1,
                price=45000.00,
                source="Binance",
                strategy="long",
                notes="Покупка Bitcoin",
            ),
            TransactionIn(
                coin="ETH",
                type="buy",
                quantity=2.0,
                price=3000.00,
                source="Coinbase",
                strategy="long",
                notes="Покупка Ethereum",
            ),
            TransactionIn(
                coin="SOL",
                type="buy",
                quantity=50.0,
                price=100.00,
                source="Binance",
                strategy="long",
                notes="Покупка Solana",
            ),
            TransactionIn(
                coin="ADA",
                type="buy",
                quantity=1000.0,
                price=0.50,
                source="Kraken",
                strategy="long",
                notes="Покупка Cardano",
            ),
            TransactionIn(
                coin="DOT",
                type="buy",
                quantity=100.0,
                price=25.00,
                source="Binance",
                strategy="long",
                notes="Покупка Polkadot",
            ),
        ]

        added_count = 0
        for tx in demo_transactions:
            try:
                success = add_transaction(tx)
                if success:
                    added_count += 1
                    print(
                        f"✅ Добавлена транзакция: {tx.coin} - {tx.quantity} по ${tx.price}"
                    )
                else:
                    print(f"❌ Ошибка добавления: {tx.coin}")
            except Exception as e:
                print(f"❌ Ошибка добавления {tx.coin}: {e}")

        print(f"\n🎉 Добавлено {added_count} демо-транзакций криптовалют!")

        # Проверяем результат
        from app.core.services import get_portfolio_stats

        stats = get_portfolio_stats()
        print(f"📊 Теперь позиций криптовалют: {len(stats.get('positions', []))}")
        print(f"📊 Всего транзакций: {stats.get('total_transactions', 0)}")

        return True

    except Exception as e:
        print(f"❌ Ошибка добавления демо-данных: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    add_crypto_demo_data()
