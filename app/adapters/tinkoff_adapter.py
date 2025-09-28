"""
Адаптер для работы с API Тинькофф Инвестиции
"""

import os
import time
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.broker_models import Broker, StockInstrument, BrokerIn, StockInstrumentIn

logger = logging.getLogger(__name__)


class TinkoffAdapter:
    """Адаптер для работы с API Тинькофф Инвестиции"""
    
    def __init__(self):
        self.api_url = "https://invest-public-api.tinkoff.ru/rest"
        self.token = os.getenv("TINKOFF_TOKEN", "")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
        
        # Кэш для инструментов и цен
        self._instruments_cache = {}
        self._prices_cache = {}
        self._cache_ttl = {
            "instruments": 24 * 60 * 60,  # 24 часа
            "prices": 5 * 60,  # 5 минут
        }
    
    def _is_cache_valid(self, cache_key: str, ttl_key: str) -> bool:
        """Проверяет валидность кэша"""
        if cache_key not in self._instruments_cache:
            return False
        
        cache_time = self._instruments_cache[cache_key].get("timestamp", 0)
        ttl = self._cache_ttl[ttl_key]
        return time.time() - cache_time < ttl
    
    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Получает данные из кэша"""
        if cache_key in self._instruments_cache:
            return self._instruments_cache[cache_key]["data"]
        return None
    
    def _set_cached_data(self, cache_key: str, data: Any) -> None:
        """Сохраняет данные в кэш"""
        self._instruments_cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def authenticate(self) -> bool:
        """Проверяет аутентификацию в API"""
        try:
            response = self.session.get(f"{self.api_url}/tinkoff.public.invest.api.contract.v1.InstrumentsService/GetCountries")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка аутентификации в Тинькофф API: {e}")
            return False
    
    def get_instruments(self, force_refresh: bool = False) -> List[StockInstrument]:
        """Получает список всех доступных инструментов"""
        cache_key = "tinkoff_instruments"
        
        if not force_refresh and self._is_cache_valid(cache_key, "instruments"):
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Получаем акции
            response = self.session.post(
                f"{self.api_url}/tinkoff.public.invest.api.contract.v1.InstrumentsService/Shares",
                json={"instrument_status": "INSTRUMENT_STATUS_BASE"}
            )
            
            if response.status_code != 200:
                logger.error(f"Ошибка получения инструментов: {response.status_code}")
                return []
            
            data = response.json()
            instruments = []
            
            for item in data.get("instruments", []):
                instrument = StockInstrument(
                    ticker=item.get("ticker", ""),
                    name=item.get("name", ""),
                    sector=item.get("sector", ""),
                    lot_size=item.get("lot", 1),
                    currency=item.get("currency", "RUB"),
                    broker_id="tinkoff",
                    is_active=True
                )
                instruments.append(instrument)
            
            # Сохраняем в кэш
            self._set_cached_data(cache_key, instruments)
            
            logger.info(f"Получено {len(instruments)} инструментов от Тинькофф")
            return instruments
            
        except Exception as e:
            logger.error(f"Ошибка получения инструментов от Тинькофф: {e}")
            # Возвращаем кэшированные данные если есть
            cached_data = self._get_cached_data(cache_key)
            return cached_data or []
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Получает текущую цену инструмента"""
        cache_key = f"price_{ticker}"
        
        if self._is_cache_valid(cache_key, "prices"):
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
        
        try:
            response = self.session.post(
                f"{self.api_url}/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices",
                json={"figi": [ticker]}  # В реальном API нужно использовать FIGI
            )
            
            if response.status_code != 200:
                logger.error(f"Ошибка получения цены для {ticker}: {response.status_code}")
                return None
            
            data = response.json()
            last_prices = data.get("lastPrices", [])
            
            if last_prices:
                price = last_prices[0].get("price", {}).get("units", 0)
                # Конвертируем в рубли (цена в копейках)
                price_rub = price / 100.0
                
                # Сохраняем в кэш
                self._set_cached_data(cache_key, price_rub)
                
                return price_rub
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения цены для {ticker}: {e}")
            # Возвращаем кэшированную цену если есть
            cached_data = self._get_cached_data(cache_key)
            return cached_data
    
    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Получает цены для нескольких инструментов"""
        prices = {}
        
        for ticker in tickers:
            price = self.get_current_price(ticker)
            if price is not None:
                prices[ticker] = price
        
        return prices
    
    def get_instrument_info(self, ticker: str) -> Optional[StockInstrument]:
        """Получает информацию об инструменте"""
        instruments = self.get_instruments()
        
        for instrument in instruments:
            if instrument.ticker == ticker:
                return instrument
        
        return None
    
    def search_instruments(self, query: str) -> List[StockInstrument]:
        """Поиск инструментов по названию или тикеру"""
        instruments = self.get_instruments()
        query_lower = query.lower()
        
        results = []
        for instrument in instruments:
            if (query_lower in instrument.ticker.lower() or 
                query_lower in instrument.name.lower()):
                results.append(instrument)
        
        return results
    
    def get_popular_instruments(self, limit: int = 20) -> List[StockInstrument]:
        """Получает популярные инструменты (топ по объему торгов)"""
        instruments = self.get_instruments()
        
        # Сортируем по названию для демонстрации
        # В реальном API можно получить данные по объему торгов
        popular_tickers = [
            "SBER", "GAZP", "LKOH", "NVTK", "ROSN",
            "NLMK", "MAGN", "CHMF", "PLZL", "TATN",
            "YNDX", "OZON", "QIWI", "MAIL", "VKCO",
            "AFLT", "SMLT", "MGNT", "RUAL", "ALRS"
        ]
        
        popular = []
        for ticker in popular_tickers[:limit]:
            for instrument in instruments:
                if instrument.ticker == ticker:
                    popular.append(instrument)
                    break
        
        return popular
    
    def get_broker_info(self) -> Broker:
        """Получает информацию о брокере Тинькофф"""
        return Broker(
            id="tinkoff",
            name="Тинькофф Инвестиции",
            api_url=self.api_url,
            is_active=True,
            description="Официальный брокер Тинькофф Банка"
        )


class BrokerManager:
    """Менеджер для работы с брокерами"""
    
    def __init__(self):
        self.adapters = {
            "tinkoff": TinkoffAdapter()
        }
    
    def get_broker(self, broker_id: str) -> Optional[Broker]:
        """Получает информацию о брокере"""
        if broker_id == "tinkoff":
            return self.adapters["tinkoff"].get_broker_info()
        return None
    
    def get_all_brokers(self) -> List[Broker]:
        """Получает список всех доступных брокеров"""
        brokers = []
        for adapter in self.adapters.values():
            brokers.append(adapter.get_broker_info())
        return brokers
    
    def get_instruments(self, broker_id: str) -> List[StockInstrument]:
        """Получает инструменты брокера"""
        if broker_id in self.adapters:
            return self.adapters[broker_id].get_instruments()
        return []
    
    def get_current_price(self, broker_id: str, ticker: str) -> Optional[float]:
        """Получает текущую цену от брокера"""
        if broker_id in self.adapters:
            return self.adapters[broker_id].get_current_price(ticker)
        return None
    
    def get_multiple_prices(self, broker_id: str, tickers: List[str]) -> Dict[str, float]:
        """Получает цены для нескольких инструментов"""
        if broker_id in self.adapters:
            return self.adapters[broker_id].get_multiple_prices(tickers)
        return {}
    
    def search_instruments(self, broker_id: str, query: str) -> List[StockInstrument]:
        """Поиск инструментов у брокера"""
        if broker_id in self.adapters:
            return self.adapters[broker_id].search_instruments(query)
        return []
    
    def get_popular_instruments(self, broker_id: str, limit: int = 20) -> List[StockInstrument]:
        """Получает популярные инструменты брокера"""
        if broker_id in self.adapters:
            return self.adapters[broker_id].get_popular_instruments(limit)
        return []
