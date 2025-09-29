#!/usr/bin/env python3
"""Скрипт для добавления демо-данных российских акций"""

from datetime import datetime

from app.models.broker_models import StockInstrument, StockTransactionIn
from app.services.broker_service import StockService


def add_demo_instruments():
    """Добавляет демо-инструменты российских акций"""
    try:
        print("🔄 Добавление демо-инструментов...")

        stock_service = StockService()

        # Популярные российские акции
        demo_instruments = [
            StockInstrument(
                ticker="SBER",
                name="Сбербанк",
                sector="Финансы",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="GAZP",
                name="Газпром",
                sector="Энергетика",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="LKOH",
                name="Лукойл",
                sector="Энергетика",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="NVTK",
                name="Новатэк",
                sector="Энергетика",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="ROSN",
                name="Роснефть",
                sector="Энергетика",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="NLMK",
                name="НЛМК",
                sector="Металлургия",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="MAGN",
                name="Магнитогорский металлургический комбинат",
                sector="Металлургия",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="CHMF",
                name="Северсталь",
                sector="Металлургия",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="PLZL",
                name="Полюс",
                sector="Добыча полезных ископаемых",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="TATN",
                name="Татнефть",
                sector="Энергетика",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="YNDX",
                name="Яндекс",
                sector="Технологии",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="OZON",
                name="Озон",
                sector="Технологии",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="QIWI",
                name="Киви",
                sector="Финансы",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="MAIL",
                name="Mail.ru Group",
                sector="Технологии",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="VKCO",
                name="VK",
                sector="Технологии",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="AFLT",
                name="Аэрофлот",
                sector="Транспорт",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="SMLT",
                name="Самолет",
                sector="Транспорт",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="MGNT",
                name="Магнит",
                sector="Ритейл",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="RUAL",
                name="РУСАЛ",
                sector="Металлургия",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
            StockInstrument(
                ticker="ALRS",
                name="Алроса",
                sector="Добыча полезных ископаемых",
                lot_size=1,
                currency="RUB",
                broker_id="tinkoff",
                is_active=True,
            ),
        ]

        # Добавляем инструменты
        added_count = 0
        for instrument in demo_instruments:
            try:
                # Проверяем, существует ли инструмент
                existing = stock_service.get_broker_instruments(
                    "tinkoff", instrument.ticker
                )
                if not existing:
                    # Добавляем новый инструмент
                    from sqlmodel import Session

                    from app.storage.db import engine

                    with Session(engine) as session:
                        session.add(instrument)
                        session.commit()
                        added_count += 1
                        print(f"✅ Добавлен: {instrument.ticker} - {instrument.name}")
                else:
                    print(f"⚠️ Уже существует: {instrument.ticker}")

            except Exception as e:
                print(f"❌ Ошибка добавления {instrument.ticker}: {e}")

        print(f"\n✅ Добавлено {added_count} демо-инструментов")
        return True

    except Exception as e:
        print(f"❌ Ошибка добавления демо-инструментов: {e}")
        return False


def add_demo_transactions():
    """Добавляет демо-транзакции"""
    try:
        print("\n🔄 Добавление демо-транзакций...")

        stock_service = StockService()

        # Демо-транзакции
        demo_transactions = [
            StockTransactionIn(
                ticker="SBER",
                broker_id="tinkoff",
                quantity=10,
                price=250.50,
                commission=25.05,
                transaction_type="buy",
                transaction_date=datetime(2024, 1, 15),
            ),
            StockTransactionIn(
                ticker="GAZP",
                broker_id="tinkoff",
                quantity=50,
                price=180.25,
                commission=90.13,
                transaction_type="buy",
                transaction_date=datetime(2024, 2, 10),
            ),
            StockTransactionIn(
                ticker="LKOH",
                broker_id="tinkoff",
                quantity=5,
                price=4500.00,
                commission=225.00,
                transaction_type="buy",
                transaction_date=datetime(2024, 3, 5),
            ),
            StockTransactionIn(
                ticker="YNDX",
                broker_id="tinkoff",
                quantity=2,
                price=3200.75,
                commission=64.02,
                transaction_type="buy",
                transaction_date=datetime(2024, 4, 20),
            ),
        ]

        added_count = 0
        for transaction in demo_transactions:
            try:
                success = stock_service.add_stock_transaction(transaction)
                if success:
                    added_count += 1
                    print(
                        f"✅ Добавлена транзакция: {transaction.ticker} - {transaction.quantity} шт. по {transaction.price} ₽"
                    )
                else:
                    print(f"❌ Ошибка добавления транзакции: {transaction.ticker}")

            except Exception as e:
                print(f"❌ Ошибка добавления транзакции {transaction.ticker}: {e}")

        print(f"\n✅ Добавлено {added_count} демо-транзакций")
        return True

    except Exception as e:
        print(f"❌ Ошибка добавления демо-транзакций: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Добавление демо-данных для российских акций")
    print("=" * 50)

    # Добавляем инструменты
    instruments_success = add_demo_instruments()

    # Добавляем транзакции
    transactions_success = add_demo_transactions()

    if instruments_success and transactions_success:
        print("\n🎉 Демо-данные успешно добавлены!")
        print("Теперь вы можете:")
        print("1. Открыть вкладку 'Акции' в приложении")
        print("2. Увидеть список российских акций")
        print("3. Просмотреть демо-позиции")
        print("4. Добавить новые позиции")
    else:
        print("\n❌ Ошибка добавления демо-данных!")
