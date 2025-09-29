#!/usr/bin/env python3
"""Тест вкладки акций"""


def test_stocks_tab():
    """Тестирует вкладку акций"""
    print("🔄 Тестируем вкладку акций...")

    try:
        # Импортируем необходимые модули
        from app.adapters.tinkoff_adapter import BrokerManager
        from app.models.broker_models import StockTransactionIn
        from app.services.broker_service import StockService

        # Создаем сервисы
        stock_service = StockService()
        broker_manager = BrokerManager()

        print("✅ Сервисы созданы")

        # Проверяем брокеров
        brokers = broker_manager.get_all_brokers()
        print(f"✅ Брокеры: {len(brokers)} найдено")
        for broker in brokers:
            print(f"   - {broker.name} (ID: {broker.id})")

        # Проверяем инструменты
        instruments = stock_service.get_broker_instruments("tinkoff")
        print(f"✅ Инструменты: {len(instruments)} найдено")

        # Проверяем позиции
        positions = stock_service.calculate_stock_positions()
        print(f"✅ Позиции: {len(positions)} найдено")

        # Проверяем транзакции
        transactions = stock_service.get_stock_transactions()
        print(f"✅ Транзакции: {len(transactions)} найдено")

        # Проверяем статистику
        stats = stock_service.get_stock_portfolio_stats()
        print(f"✅ Статистика: общая стоимость {stats.total_value:.2f} ₽")

        print("\n🎉 ВКЛАДКА АКЦИЙ РАБОТАЕТ!")
        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА ВКЛАДКИ АКЦИЙ: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_stocks_tab()
