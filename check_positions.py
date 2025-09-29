#!/usr/bin/env python3
"""Проверка и исправление позиций"""


def check_and_fix_positions():
    """Проверяет и исправляет позиции"""
    print("🔍 Проверка позиций...")

    try:
        from sqlmodel import Session

        from app.core.models import Transaction
        from app.core.services import get_portfolio_stats, positions_fifo
        from app.storage.db import engine

        # Проверяем транзакции в БД
        with Session(engine) as session:
            from sqlmodel import text

            transactions = session.exec(text("SELECT * FROM `transaction`")).all()
            print(f"📊 Транзакций в БД: {len(transactions)}")

            for tx in transactions:
                print(f"   - {tx.coin}: {tx.type} {tx.quantity} по ${tx.price}")

        # Проверяем расчет позиций
        print("\n🔄 Расчет позиций...")
        positions = positions_fifo()
        print(f"📊 Рассчитанных позиций: {len(positions)}")

        for pos in positions:
            print(f"   - {pos['coin']}: {pos['quantity']} по ${pos['avg_cost']:.2f}")

        # Проверяем статистику
        print("\n📊 Статистика портфеля...")
        stats = get_portfolio_stats()
        print(f"   📈 Позиций: {len(stats.get('positions', []))}")
        print(f"   📈 Транзакций: {stats.get('total_transactions', 0)}")
        print(
            f"   📈 Общая стоимость: ${stats.get('totals', {}).get('total_value', 0):.2f}"
        )

        return True

    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    check_and_fix_positions()
