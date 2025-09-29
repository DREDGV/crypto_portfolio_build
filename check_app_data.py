#!/usr/bin/env python3
"""Проверка данных в приложении"""


def check_app_data():
    """Проверяет данные в приложении"""
    print("🔍 Проверка данных в приложении...")

    try:
        # Проверяем криптовалютные данные
        print("\n1. Проверяем криптовалютные данные...")
        from app.core.services import get_portfolio_stats

        portfolio_stats = get_portfolio_stats()
        print(f"   📊 Позиции криптовалют: {len(portfolio_stats.get('positions', []))}")
        print(f"   📊 Всего транзакций: {portfolio_stats.get('total_transactions', 0)}")

        # Проверяем данные акций
        print("\n2. Проверяем данные акций...")
        from app.services.broker_service import StockService

        stock_service = StockService()

        brokers = stock_service.get_all_brokers()
        print(f"   📊 Брокеры: {len(brokers)}")

        instruments = stock_service.get_broker_instruments("tinkoff")
        print(f"   📊 Инструменты: {len(instruments)}")

        positions = stock_service.calculate_stock_positions()
        print(f"   📊 Позиции акций: {len(positions)}")

        transactions = stock_service.get_stock_transactions()
        print(f"   📊 Транзакции акций: {len(transactions)}")

        # Показываем детали
        if positions:
            print("\n   📋 Детали позиций акций:")
            for pos in positions:
                print(
                    f"      - {pos.ticker}: {pos.quantity} шт. по {pos.average_price:.2f} ₽"
                )

        if portfolio_stats.get("positions"):
            print("\n   📋 Детали позиций криптовалют:")
            for pos in portfolio_stats.get("positions", []):
                print(
                    f"      - {pos.get('coin', 'N/A')}: {pos.get('quantity', 0)} по ${pos.get('avg_cost', 0):.2f}"
                )

        print("\n✅ Проверка завершена")
        return True

    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    check_app_data()
