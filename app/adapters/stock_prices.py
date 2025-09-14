#!/usr/bin/env python3
"""Адаптер для получения цен акций"""

import json
import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

import requests


class StockPriceAdapter:
    """Адаптер для получения цен акций с различных источников"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_price_alpha_vantage(self, symbol: str) -> Optional[Dict]:
        """Получает цену акции через Alpha Vantage API"""
        try:
            # Заглушка - в реальном приложении здесь будет реальный API ключ
            api_key = "demo"  # Замените на реальный ключ

            url = f"https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                return {
                    "price": float(quote.get("05. price", 0)),
                    "change_24h": float(quote.get("09. change", 0)),
                    "change_percent_24h": float(
                        quote.get("10. change percent", 0).replace("%", "")
                    ),
                    "volume": int(quote.get("06. volume", 0)),
                    "currency": "USD",
                    "exchange": "NASDAQ",
                }

            return None

        except Exception as e:
            print(f"Ошибка Alpha Vantage для {symbol}: {e}")
            return None

    def get_price_yahoo_finance(self, symbol: str) -> Optional[Dict]:
        """Получает цену акции через Yahoo Finance (неофициальный API)"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {"range": "1d", "interval": "1m", "includePrePost": "true"}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "chart" in data and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                meta = result.get("meta", {})

                current_price = meta.get("regularMarketPrice", 0)
                previous_close = meta.get("previousClose", 0)
                change_24h = current_price - previous_close
                change_percent_24h = (
                    (change_24h / previous_close * 100) if previous_close > 0 else 0
                )

                return {
                    "price": current_price,
                    "change_24h": change_24h,
                    "change_percent_24h": change_percent_24h,
                    "volume": meta.get("regularMarketVolume", 0),
                    "currency": "USD",
                    "exchange": "NASDAQ",
                }

            return None

        except Exception as e:
            print(f"Ошибка Yahoo Finance для {symbol}: {e}")
            return None

    def get_price_mock(self, symbol: str) -> Optional[Dict]:
        """Заглушка для получения цены акции (для тестирования)"""
        # Генерируем случайную цену для тестирования
        import random

        base_prices = {
            "AAPL": 150.0,
            "MSFT": 300.0,
            "GOOGL": 2500.0,
            "AMZN": 3000.0,
            "TSLA": 200.0,
            "META": 300.0,
            "NVDA": 400.0,
            "NFLX": 400.0,
        }

        base_price = base_prices.get(symbol.upper(), 100.0)
        # Добавляем случайное изменение ±5%
        change_percent = random.uniform(-5, 5)
        current_price = base_price * (1 + change_percent / 100)
        change_24h = current_price - base_price
        change_percent_24h = (change_24h / base_price * 100) if base_price > 0 else 0

        return {
            "price": round(current_price, 2),
            "change_24h": round(change_24h, 2),
            "change_percent_24h": round(change_percent_24h, 2),
            "volume": random.randint(1000000, 10000000),
            "currency": "USD",
            "exchange": "NASDAQ",
        }

    def get_price(self, symbol: str) -> Optional[Dict]:
        """Получает цену акции (пробует разные источники)"""
        # Сначала пробуем Yahoo Finance
        price_data = self.get_price_yahoo_finance(symbol)
        if price_data:
            return price_data

        # Если не получилось, пробуем Alpha Vantage
        price_data = self.get_price_alpha_vantage(symbol)
        if price_data:
            return price_data

        # Если ничего не работает, используем заглушку
        return self.get_price_mock(symbol)

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Получает цены для нескольких акций"""
        prices = {}

        for symbol in symbols:
            price_data = self.get_price(symbol)
            if price_data:
                prices[symbol] = price_data
            # Небольшая задержка между запросами
            time.sleep(0.1)

        return prices

    def search_stocks(self, query: str) -> List[Dict]:
        """Поиск акций по названию или символу"""
        # Заглушка - в реальном приложении здесь будет API поиска
        popular_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
            {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "exchange": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ"},
            {
                "symbol": "AMD",
                "name": "Advanced Micro Devices Inc.",
                "exchange": "NASDAQ",
            },
            {"symbol": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ"},
        ]

        query_lower = query.lower()
        results = []

        for stock in popular_stocks:
            if (
                query_lower in stock["symbol"].lower()
                or query_lower in stock["name"].lower()
            ):
                results.append(stock)

        return results[:10]  # Возвращаем максимум 10 результатов
