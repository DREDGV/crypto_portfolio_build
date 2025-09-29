#!/usr/bin/env python3
"""Исправление базы данных"""


def fix_database():
    """Исправляет проблему с таблицей transaction"""
    print("🔧 Исправление базы данных...")

    try:
        import os
        import shutil
        from datetime import datetime

        # Путь к базе данных
        db_path = "data/portfolio.db"

        # Создаем резервную копию
        if os.path.exists(db_path):
            backup_dir = "data/backups"
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"portfolio_backup_{timestamp}.db")
            shutil.copy2(db_path, backup_path)
            print(f"✅ Создана резервная копия: {backup_path}")

            # Удаляем старую базу
            os.remove(db_path)
            print("✅ Старая база данных удалена")

        # Пересоздаем базу данных
        from app.storage.db import init_db

        init_db()
        print("✅ Новая база данных создана")

        # Добавляем демо-данные криптовалют
        print("\n🔄 Добавление демо-данных криптовалют...")
        from app.core.models import TransactionIn
        from app.core.services import add_transaction

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
                    print(f"✅ Добавлена: {tx.coin}")
                else:
                    print(f"❌ Ошибка: {tx.coin}")
            except Exception as e:
                print(f"❌ Ошибка {tx.coin}: {e}")

        # Восстанавливаем данные акций
        print("\n🔄 Восстановление данных акций...")
        from datetime import datetime, timedelta

        from app.models.broker_models import Broker, StockInstrument, StockTransactionIn
        from app.services.broker_service import StockService

        stock_service = StockService()

        # Добавляем брокера
        tinkoff_broker = Broker(
            id="tinkoff",
            name="Тинькофф Инвестиции",
            api_url="https://invest-public-api.tinkoff.ru/rest",
            is_active=True,
            description="Российский брокер Тинькофф",
        )

        try:
            stock_service.add_broker(tinkoff_broker)
            print("✅ Брокер Тинькофф добавлен")
        except:
            print("ℹ️ Брокер Тинькофф уже существует")

        # Синхронизируем инструменты
        count = stock_service.sync_broker_instruments("tinkoff")
        print(f"✅ Синхронизировано {count} инструментов")

        # Добавляем демо-транзакции акций
        demo_stock_transactions = [
            StockTransactionIn(
                ticker="SBER",
                broker_id="tinkoff",
                quantity=10,
                price=250.50,
                commission=25.05,
                transaction_type="buy",
                transaction_date=datetime.utcnow() - timedelta(days=30),
            ),
            StockTransactionIn(
                ticker="GAZP",
                broker_id="tinkoff",
                quantity=50,
                price=180.25,
                commission=90.13,
                transaction_type="buy",
                transaction_date=datetime.utcnow() - timedelta(days=20),
            ),
            StockTransactionIn(
                ticker="LKOH",
                broker_id="tinkoff",
                quantity=5,
                price=4500.00,
                commission=225.00,
                transaction_type="buy",
                transaction_date=datetime.utcnow() - timedelta(days=10),
            ),
            StockTransactionIn(
                ticker="YNDX",
                broker_id="tinkoff",
                quantity=2,
                price=3200.75,
                commission=64.02,
                transaction_type="buy",
                transaction_date=datetime.utcnow() - timedelta(days=5),
            ),
        ]

        for tx in demo_stock_transactions:
            try:
                success = stock_service.add_stock_transaction(tx)
                if success:
                    print(f"✅ Добавлена акция: {tx.ticker}")
                else:
                    print(f"❌ Ошибка акции: {tx.ticker}")
            except Exception as e:
                print(f"❌ Ошибка акции {tx.ticker}: {e}")

        # Проверяем результат
        print("\n📊 Проверка результата...")
        from app.core.services import get_portfolio_stats

        stats = get_portfolio_stats()
        print(f"   📈 Позиций криптовалют: {len(stats.get('positions', []))}")
        print(f"   📈 Всего транзакций: {stats.get('total_transactions', 0)}")

        positions = stock_service.calculate_stock_positions()
        print(f"   📈 Позиций акций: {len(positions)}")

        print("\n🎉 База данных исправлена и заполнена!")
        return True

    except Exception as e:
        print(f"❌ Ошибка исправления БД: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    fix_database()
