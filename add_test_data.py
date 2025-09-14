#!/usr/bin/env python3
"""
Скрипт для добавления тестовых транзакций в базу данных
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select

from app.core.models import Transaction
from app.storage.db import engine


def add_test_transactions():
    """Добавляет тестовые транзакции в базу данных"""

    # Подключаемся к базе данных

    with Session(engine) as session:
        # Проверяем, есть ли уже транзакции
        existing = session.exec(select(Transaction)).first()
        if existing:
            print(
                "❌ В базе уже есть транзакции. Пропускаем добавление тестовых данных."
            )
            return

        # Создаем тестовые транзакции
        test_transactions = [
            # Bitcoin транзакции
            Transaction(
                symbol="BTC",
                transaction_type="buy",
                amount=Decimal("0.5"),
                price=Decimal("45000.00"),
                timestamp=datetime.now() - timedelta(days=30),
                notes="Покупка Bitcoin на минимуме",
            ),
            Transaction(
                symbol="BTC",
                transaction_type="buy",
                amount=Decimal("0.3"),
                price=Decimal("48000.00"),
                timestamp=datetime.now() - timedelta(days=20),
                notes="Докупка Bitcoin",
            ),
            Transaction(
                symbol="BTC",
                transaction_type="sell",
                amount=Decimal("0.2"),
                price=Decimal("52000.00"),
                timestamp=datetime.now() - timedelta(days=10),
                notes="Частичная продажа Bitcoin",
            ),
            # Ethereum транзакции
            Transaction(
                symbol="ETH",
                transaction_type="buy",
                amount=Decimal("2.0"),
                price=Decimal("3200.00"),
                timestamp=datetime.now() - timedelta(days=25),
                notes="Покупка Ethereum",
            ),
            Transaction(
                symbol="ETH",
                transaction_type="buy",
                amount=Decimal("1.5"),
                price=Decimal("2800.00"),
                timestamp=datetime.now() - timedelta(days=15),
                notes="Докупка Ethereum на коррекции",
            ),
            # Cardano транзакции
            Transaction(
                symbol="ADA",
                transaction_type="buy",
                amount=Decimal("1000"),
                price=Decimal("0.45"),
                timestamp=datetime.now() - timedelta(days=40),
                notes="Покупка Cardano",
            ),
            Transaction(
                symbol="ADA",
                transaction_type="buy",
                amount=Decimal("500"),
                price=Decimal("0.38"),
                timestamp=datetime.now() - timedelta(days=35),
                notes="Докупка Cardano",
            ),
            # Solana транзакции
            Transaction(
                symbol="SOL",
                transaction_type="buy",
                amount=Decimal("10"),
                price=Decimal("95.00"),
                timestamp=datetime.now() - timedelta(days=20),
                notes="Покупка Solana",
            ),
            Transaction(
                symbol="SOL",
                transaction_type="sell",
                amount=Decimal("3"),
                price=Decimal("110.00"),
                timestamp=datetime.now() - timedelta(days=5),
                notes="Частичная продажа Solana",
            ),
            # Polkadot транзакции
            Transaction(
                symbol="DOT",
                transaction_type="buy",
                amount=Decimal("50"),
                price=Decimal("6.80"),
                timestamp=datetime.now() - timedelta(days=45),
                notes="Покупка Polkadot",
            ),
            Transaction(
                symbol="DOT",
                transaction_type="buy",
                amount=Decimal("30"),
                price=Decimal("5.20"),
                timestamp=datetime.now() - timedelta(days=30),
                notes="Докупка Polkadot",
            ),
            # Chainlink транзакции
            Transaction(
                symbol="LINK",
                transaction_type="buy",
                amount=Decimal("100"),
                price=Decimal("12.50"),
                timestamp=datetime.now() - timedelta(days=35),
                notes="Покупка Chainlink",
            ),
            Transaction(
                symbol="LINK",
                transaction_type="buy",
                amount=Decimal("50"),
                price=Decimal("10.80"),
                timestamp=datetime.now() - timedelta(days=25),
                notes="Докупка Chainlink",
            ),
            # Uniswap транзакции
            Transaction(
                symbol="UNI",
                transaction_type="buy",
                amount=Decimal("200"),
                price=Decimal("4.20"),
                timestamp=datetime.now() - timedelta(days=28),
                notes="Покупка Uniswap",
            ),
            Transaction(
                symbol="UNI",
                transaction_type="sell",
                amount=Decimal("50"),
                price=Decimal("5.80"),
                timestamp=datetime.now() - timedelta(days=8),
                notes="Частичная продажа Uniswap",
            ),
        ]

        # Добавляем транзакции в базу
        for transaction in test_transactions:
            session.add(transaction)

        session.commit()
        print(f"✅ Добавлено {len(test_transactions)} тестовых транзакций")
        print("\n📊 Тестовые данные включают:")
        print("   • Bitcoin (BTC) - 3 транзакции")
        print("   • Ethereum (ETH) - 2 транзакции")
        print("   • Cardano (ADA) - 2 транзакции")
        print("   • Solana (SOL) - 2 транзакции")
        print("   • Polkadot (DOT) - 2 транзакции")
        print("   • Chainlink (LINK) - 2 транзакции")
        print("   • Uniswap (UNI) - 2 транзакции")
        print("\n🎯 Теперь можете протестировать все функции приложения!")


if __name__ == "__main__":
    add_test_transactions()
