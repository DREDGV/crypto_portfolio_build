#!/usr/bin/env python3
"""Тест новых модулей для работы с акциями"""

def test_new_modules():
    try:
        print("🔄 Тестируем новые модули...")
        
        # Тест моделей брокеров
        from app.models.broker_models import Broker, StockInstrument, StockTransaction
        print("✅ app.models.broker_models - OK")
        
        # Тест адаптера Тинькофф
        from app.adapters.tinkoff_adapter import TinkoffAdapter, BrokerManager
        print("✅ app.adapters.tinkoff_adapter - OK")
        
        # Тест сервиса брокеров
        from app.services.broker_service import StockService
        print("✅ app.services.broker_service - OK")
        
        # Тест UI вкладки акций
        from app.ui.stocks_tab import create_stocks_tab
        print("✅ app.ui.stocks_tab - OK")
        
        print("\n🎉 ВСЕ НОВЫЕ МОДУЛИ УСПЕШНЫ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

if __name__ == "__main__":
    test_new_modules()
