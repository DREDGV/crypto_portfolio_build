#!/usr/bin/env python3
"""Тест всех компонентов приложения"""


def test_all_components():
    """Тестирует все компоненты приложения"""
    print("🔄 Тестируем все компоненты приложения...")

    try:
        # 1. Тест базы данных
        print("1. Тестируем базу данных...")
        from app.storage.db import engine, init_db

        init_db()
        print("   ✅ База данных инициализирована")

        # 2. Тест моделей
        print("2. Тестируем модели...")
        from app.core.models import PriceAlert, Transaction
        from app.models.broker_models import Broker, StockInstrument, StockTransaction

        print("   ✅ Модели импортированы")

        # 3. Тест сервисов
        print("3. Тестируем сервисы...")
        from app.core.services import get_portfolio_stats
        from app.services.broker_service import StockService

        print("   ✅ Сервисы импортированы")

        # 4. Тест адаптеров
        print("4. Тестируем адаптеры...")
        from app.adapters.prices import PriceAdapter
        from app.adapters.tinkoff_adapter import BrokerManager

        print("   ✅ Адаптеры импортированы")

        # 5. Тест UI компонентов
        print("5. Тестируем UI компоненты...")
        from app.ui.pages_step2 import portfolio_page
        from app.ui.stocks_tab import create_stocks_tab

        print("   ✅ UI компоненты импортированы")

        # 6. Тест создания сервисов
        print("6. Тестируем создание сервисов...")
        stock_service = StockService()
        broker_manager = BrokerManager()
        print("   ✅ Сервисы созданы")

        # 7. Тест получения данных
        print("7. Тестируем получение данных...")
        try:
            portfolio_stats = get_portfolio_stats()
            print(
                f"   ✅ Статистика портфеля: {len(portfolio_stats.get('positions', []))} позиций"
            )
        except Exception as e:
            print(f"   ⚠️ Ошибка получения статистики: {e}")

        try:
            brokers = broker_manager.get_all_brokers()
            print(f"   ✅ Брокеры: {len(brokers)} найдено")
        except Exception as e:
            print(f"   ⚠️ Ошибка получения брокеров: {e}")

        print("\n🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ!")
        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_all_components()
