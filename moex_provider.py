#!/usr/bin/env python3
"""
Скрипт для получения актуальных данных акций с Московской биржи (MOEX)
Бесплатный альтернативный источник данных для Тинькофф Инвестиции
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class MOEXDataProvider:
    """Провайдер данных с Московской биржи"""

    def __init__(self):
        self.base_url = "https://iss.moex.com/iss"
        self.session = requests.Session()

    def get_all_securities(self) -> List[Dict[str, Any]]:
        """Получает все ценные бумаги с MOEX"""
        try:
            # Получаем все данные с пагинацией
            all_securities = []
            start = 0

            while True:
                url = f"{self.base_url}/securities.json"
                params = {"start": start}
                response = self.session.get(url, params=params)

                if response.status_code != 200:
                    break

                data = response.json()
                securities = data.get("securities", {}).get("data", [])

                if not securities:
                    break

                all_securities.extend(securities)
                start += len(securities)

                # Ограничиваем количество запросов
                if start > 1000:
                    break

            if all_securities:
                columns = data.get("securities", {}).get("columns", [])

                print(f"[DEBUG] Всего инструментов: {len(all_securities)}")
                print(f"[DEBUG] Колонки: {columns}")

                # Преобразуем в словари
                result = []
                for security in all_securities:
                    security_dict = dict(zip(columns, security))

                    # Фильтруем только акции (проверяем разные варианты)
                    security_type = security_dict.get("type", "").lower()
                    board = security_dict.get("primary_boardid", "")

                    # Проверяем разные варианты типов акций
                    is_share = (
                        "share" in security_type
                        or security_type == "common_share"
                        or security_type == "preferred_share"
                    )

                    if is_share and board == "TQBR":
                        result.append(
                            {
                                "ticker": security_dict.get("secid", ""),
                                "name": security_dict.get("name", ""),
                                "sector": security_dict.get(
                                    "group", ""
                                ),  # Используем group вместо sector
                                "currency": "RUB",  # По умолчанию рубли
                                "lot_size": 1,  # По умолчанию 1
                                "is_active": security_dict.get("is_traded", False),
                                "source": "MOEX",
                            }
                        )

                print(f"[DEBUG] Найдено акций: {len(result)}")
                logger.info(f"Получено {len(result)} акций с MOEX")
                return result
            else:
                logger.error(f"Ошибка получения данных с MOEX: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Ошибка при получении данных с MOEX: {e}")
            return []

    def get_current_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Получает текущие цены для списка тикеров"""
        try:
            prices = {}

            for ticker in tickers:
                try:
                    url = f"{self.base_url}/securities/{ticker}/candles.json"
                    params = {
                        "from": datetime.now().strftime("%Y-%m-%d"),
                        "till": datetime.now().strftime("%Y-%m-%d"),
                        "interval": 24,
                        "candles.columns": "close",
                    }

                    response = self.session.get(url, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        candles = data.get("candles", {}).get("data", [])

                        if candles:
                            # Берем последнюю цену закрытия
                            price = candles[-1][0]  # Первый элемент - цена закрытия
                            prices[ticker] = float(price)
                        else:
                            prices[ticker] = None
                    else:
                        prices[ticker] = None

                except Exception as e:
                    logger.warning(f"Не удалось получить цену для {ticker}: {e}")
                    prices[ticker] = None

            return prices

        except Exception as e:
            logger.error(f"Ошибка получения цен с MOEX: {e}")
            return {}

    def get_market_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Получает детальную информацию по инструменту"""
        try:
            url = f"{self.base_url}/securities/{ticker}.json"
            response = self.session.get(url)

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return None

        except Exception as e:
            logger.error(f"Ошибка получения данных по {ticker}: {e}")
            return None


def update_stocks_database():
    """Обновляет базу данных акций данными с MOEX"""
    try:
        from sqlmodel import Session

        from app.models.broker_models import StockInstrument
        from app.services.broker_service import StockService
        from app.storage.db import engine

        moex_provider = MOEXDataProvider()

        # Получаем данные с MOEX
        securities = moex_provider.get_all_securities()

        if not securities:
            print("[ERROR] Не удалось получить данные с MOEX")
            return

        # Обновляем базу данных
        with Session(engine) as session:
            updated_count = 0

            for security in securities:
                # Проверяем, существует ли инструмент
                existing = session.exec(
                    select(StockInstrument).where(
                        StockInstrument.ticker == security["ticker"],
                        StockInstrument.broker_id == "tinkoff",
                    )
                ).first()

                if existing:
                    # Обновляем существующий
                    existing.name = security["name"]
                    existing.sector = security["sector"]
                    existing.lot_size = security["lot_size"]
                    existing.currency = security["currency"]
                    existing.is_active = security["is_active"]
                    existing.updated_at = datetime.utcnow()
                else:
                    # Создаем новый
                    new_instrument = StockInstrument(
                        ticker=security["ticker"],
                        name=security["name"],
                        sector=security["sector"],
                        lot_size=security["lot_size"],
                        currency=security["currency"],
                        is_active=security["is_active"],
                        broker_id="tinkoff",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(new_instrument)

                updated_count += 1

            session.commit()
            print(f"[OK] Обновлено {updated_count} инструментов в базе данных")

    except Exception as e:
        logger.error(f"Ошибка обновления базы данных: {e}")
        print(f"[ERROR] Ошибка обновления базы данных: {e}")


def test_moex_connection():
    """Тестирует подключение к MOEX"""
    print("[TEST] Тестирование подключения к MOEX...")

    moex_provider = MOEXDataProvider()

    # Получаем несколько акций для теста
    securities = moex_provider.get_all_securities()

    if securities:
        print(f"[OK] Подключение успешно! Получено {len(securities)} акций")

        # Показываем первые 5 акций
        print("\n[DATA] Примеры акций:")
        for i, security in enumerate(securities[:5]):
            print(f"  {i+1}. {security['ticker']} - {security['name']}")

        # Тестируем получение цен
        test_tickers = [s["ticker"] for s in securities[:3]]
        print(f"\n[PRICE] Тестирование получения цен для {test_tickers}...")

        prices = moex_provider.get_current_prices(test_tickers)
        for ticker, price in prices.items():
            if price:
                print(f"  {ticker}: {price:.2f} RUB")
            else:
                print(f"  {ticker}: цена недоступна")
    else:
        print("[ERROR] Не удалось получить данные с MOEX")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_moex_connection()
        elif sys.argv[1] == "update":
            update_stocks_database()
        else:
            print("Использование: python moex_provider.py [test|update]")
    else:
        print("[INFO] MOEX Data Provider")
        print("Использование:")
        print("  python moex_provider.py test   - тестировать подключение")
        print("  python moex_provider.py update - обновить базу данных")
