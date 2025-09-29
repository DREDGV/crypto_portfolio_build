#!/usr/bin/env python3
"""Полное восстановление данных"""


def restore_all_data():
    """Полностью восстанавливает все данные"""
    print("🚀 Полное восстановление данных...")

    try:
        from datetime import datetime, timedelta

        from sqlmodel import Session

        from app.core.models import TransactionIn
        from app.core.services import add_transaction
        from app.models.broker_models import Broker, StockInstrument, StockTransactionIn
        from app.services.broker_service import StockService
        from app.storage.db import engine, init_db

        # Инициализируем БД
        init_db()
        print("✅ База данных инициализирована")

        # Добавляем криптовалютные транзакции
        print("\n🔄 Добавление криптовалютных транзакций...")
        crypto_transactions = [
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

        crypto_added = 0
        for tx in crypto_transactions:
            try:
                success = add_transaction(tx)
                if success:
                    crypto_added += 1
                    print(f"✅ Крипто: {tx.coin}")
                else:
                    print(f"❌ Ошибка крипто: {tx.coin}")
            except Exception as e:
                print(f"❌ Ошибка крипто {tx.coin}: {e}")

        # Добавляем брокера и инструменты акций
        print("\n🔄 Добавление данных акций...")

        # Брокер
        tinkoff_broker = Broker(
            id="tinkoff",
            name="Тинькофф Инвестиции",
            api_url="https://invest-public-api.tinkoff.ru/rest",
            is_active=True,
            description="Российский брокер Тинькофф",
        )

        with Session(engine) as session:
            # Добавляем брокера
            existing_broker = session.get(Broker, "tinkoff")
            if not existing_broker:
                session.add(tinkoff_broker)
                session.commit()
                print("✅ Брокер добавлен")
            else:
                print("ℹ️ Брокер уже существует")

            # Добавляем инструменты
            instruments_data = [
                {
                    "ticker": "SBER",
                    "name": "Сбербанк",
                    "sector": "Финансы",
                    "lot_size": 10,
                    "currency": "RUB",
                },
                {
                    "ticker": "GAZP",
                    "name": "Газпром",
                    "sector": "Энергетика",
                    "lot_size": 10,
                    "currency": "RUB",
                },
                {
                    "ticker": "LKOH",
                    "name": "Лукойл",
                    "sector": "Энергетика",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "YNDX",
                    "name": "Яндекс",
                    "sector": "IT",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "NVTK",
                    "name": "Новатэк",
                    "sector": "Энергетика",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "ROSN",
                    "name": "Роснефть",
                    "sector": "Энергетика",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "NLMK",
                    "name": "НЛМК",
                    "sector": "Металлургия",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "MAGN",
                    "name": "Магнитогорский металлургический комбинат",
                    "sector": "Металлургия",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "CHMF",
                    "name": "Северсталь",
                    "sector": "Металлургия",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "PLZL",
                    "name": "Полюс",
                    "sector": "Золотодобыча",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "TATN",
                    "name": "Татнефть",
                    "sector": "Энергетика",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "OZON",
                    "name": "Озон",
                    "sector": "E-commerce",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "QIWI",
                    "name": "Киви",
                    "sector": "Финансы",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "VKCO",
                    "name": "VK",
                    "sector": "IT",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "AFLT",
                    "name": "Аэрофлот",
                    "sector": "Транспорт",
                    "lot_size": 10,
                    "currency": "RUB",
                },
                {
                    "ticker": "SMLT",
                    "name": "Самолет",
                    "sector": "Девелопмент",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "MGNT",
                    "name": "Магнит",
                    "sector": "Ритейл",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "MOEX",
                    "name": "Московская Биржа",
                    "sector": "Финансы",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "FIVE",
                    "name": "X5 Group",
                    "sector": "Ритейл",
                    "lot_size": 1,
                    "currency": "RUB",
                },
                {
                    "ticker": "TRNFP",
                    "name": "Транснефть",
                    "sector": "Энергетика",
                    "lot_size": 1,
                    "currency": "RUB",
                },
            ]

            instruments_added = 0
            for data in instruments_data:
                instrument = StockInstrument(broker_id="tinkoff", **data)
                session.add(instrument)
                instruments_added += 1

            session.commit()
            print(f"✅ Добавлено {instruments_added} инструментов")

        # Добавляем транзакции акций
        print("\n🔄 Добавление транзакций акций...")
        stock_service = StockService()

        stock_transactions = [
            StockTransactionIn(
                ticker="SBER",
                broker_id="tinkoff",
                quantity=10,
                price=250.50,
                commission=25.05,
                transaction_type="buy",
                transaction_date=datetime.now() - timedelta(days=30),
            ),
            StockTransactionIn(
                ticker="GAZP",
                broker_id="tinkoff",
                quantity=50,
                price=180.25,
                commission=90.13,
                transaction_type="buy",
                transaction_date=datetime.now() - timedelta(days=20),
            ),
            StockTransactionIn(
                ticker="LKOH",
                broker_id="tinkoff",
                quantity=5,
                price=4500.00,
                commission=225.00,
                transaction_type="buy",
                transaction_date=datetime.now() - timedelta(days=10),
            ),
            StockTransactionIn(
                ticker="YNDX",
                broker_id="tinkoff",
                quantity=2,
                price=3200.75,
                commission=64.02,
                transaction_type="buy",
                transaction_date=datetime.now() - timedelta(days=5),
            ),
        ]

        stock_added = 0
        for tx in stock_transactions:
            try:
                success = stock_service.add_stock_transaction(tx)
                if success:
                    stock_added += 1
                    print(f"✅ Акция: {tx.ticker}")
                else:
                    print(f"❌ Ошибка акции: {tx.ticker}")
            except Exception as e:
                print(f"❌ Ошибка акции {tx.ticker}: {e}")

        # Проверяем результат
        print("\n📊 Финальная проверка...")
        from app.core.services import get_portfolio_stats

        stats = get_portfolio_stats()

        positions = stock_service.calculate_stock_positions()

        print(f"   📈 Криптовалютных транзакций: {crypto_added}")
        print(f"   📈 Позиций криптовалют: {len(stats.get('positions', []))}")
        print(f"   📈 Всего транзакций: {stats.get('total_transactions', 0)}")
        print(f"   📈 Позиций акций: {len(positions)}")
        print(f"   📈 Транзакций акций: {stock_added}")

        print("\n🎉 ВСЕ ДАННЫЕ ВОССТАНОВЛЕНЫ!")
        return True

    except Exception as e:
        print(f"❌ Ошибка восстановления: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    restore_all_data()
