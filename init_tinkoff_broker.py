#!/usr/bin/env python3
"""Скрипт для инициализации брокера Тинькофф"""

from app.adapters.tinkoff_adapter import BrokerManager
from app.services.broker_service import StockService


def init_tinkoff_broker():
    """Инициализирует брокера Тинькофф в базе данных"""
    try:
        print("🔄 Инициализация брокера Тинькофф...")

        stock_service = StockService()
        broker_manager = BrokerManager()

        # Получаем информацию о брокере Тинькофф
        tinkoff_broker = broker_manager.get_broker("tinkoff")

        if tinkoff_broker:
            # Добавляем брокера в базу данных
            success = stock_service.add_broker(tinkoff_broker)
            if success:
                print("✅ Брокер Тинькофф добавлен в базу данных")

                # Синхронизируем инструменты
                print("🔄 Синхронизация инструментов...")
                count = stock_service.sync_broker_instruments("tinkoff")
                print(f"✅ Синхронизировано {count} инструментов")

                return True
            else:
                print("❌ Ошибка добавления брокера")
                return False
        else:
            print("❌ Брокер Тинькофф не найден")
            return False

    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False


if __name__ == "__main__":
    success = init_tinkoff_broker()
    if success:
        print("\n🎉 Инициализация завершена успешно!")
        print("Теперь вы можете использовать вкладку 'Акции' в приложении")
    else:
        print("\n❌ Инициализация завершена с ошибками!")
