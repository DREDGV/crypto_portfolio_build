import json
import random
import time

import httpx

_cache: dict[tuple[str, str], tuple[float, float]] = {}

ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XLM": "stellar",
    "USDT": "tether",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "TRX": "tron",
    "TON": "the-open-network",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "MATIC": "matic-network",
    "AVAX": "avalanche-2",
    "ATOM": "cosmos",
    "NEAR": "near",
    "FTM": "fantom",
    "ALGO": "algorand",
    "VET": "vechain",
    "ICP": "internet-computer",
    "FIL": "filecoin",
    "THETA": "theta-token",
    "EOS": "eos",
    "AAVE": "aave",
    "SUSHI": "sushi",
    "COMP": "compound-governance-token",
    "YFI": "yearn-finance",
    "SNX": "havven",
    "MKR": "maker",
    "CRV": "curve-dao-token",
    "1INCH": "1inch",
    "BAT": "basic-attention-token",
    "ZRX": "0x",
    "ENJ": "enjincoin",
    "MANA": "decentraland",
    "SAND": "the-sandbox",
    "AXS": "axie-infinity",
    "CHZ": "chiliz",
    "FLOW": "flow",
    "XTZ": "tezos",
    "NEO": "neo",
    "QTUM": "qtum",
    "DASH": "dash",
    "ZEC": "zcash",
    "XMR": "monero",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
}


def get_current_price(symbol: str, quote: str = "USD") -> float | None:
    """Возвращает текущую цену через CoinGecko Simple Price API.

    Args:
        symbol: Символ криптовалюты (например, 'BTC', 'ETH')
        quote: Валюта для отображения цены (по умолчанию 'USD')

    Returns:
        float | None: Текущая цена или None в случае ошибки
    """
    if not symbol:
        return None

    sym = symbol.upper()
    q = quote.lower()
    key = (sym, q)
    now = time.time()

    # Проверяем кэш (актуален 5 минут для улучшения производительности)
    if key in _cache and now - _cache[key][1] < 300:
        return _cache[key][0]

    # Получаем ID монеты для CoinGecko API
    coin_id = ID_MAP.get(sym, sym.lower())

    # URL для CoinGecko Simple Price API
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": q,
        "include_24hr_change": "true",  # Добавляем информацию об изменении за 24ч
        "include_last_updated_at": "true",  # Добавляем время последнего обновления
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

            if coin_id in data:
                coin_data = data[coin_id]
                price = float(coin_data.get(q, 0.0))

                if price > 0:
                    # Сохраняем в кэш с временной меткой
                    _cache[key] = (price, now)
                    return price
                else:
                    print(f"⚠️ Получена нулевая цена для {sym}")
                    return None
            else:
                print(f"⚠️ Монета {sym} не найдена в ответе API")
                return None

    except httpx.TimeoutException:
        print(f"⏰ Таймаут при получении цены для {sym}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"🌐 HTTP ошибка {e.response.status_code} при получении цены для {sym}")
        return None
    except Exception as e:
        print(f"❌ Ошибка при получении цены для {sym}: {e}")
        return None


def get_price_info(symbol: str, quote: str = "USD") -> dict | None:
    """Возвращает расширенную информацию о цене через CoinGecko API.

    Args:
        symbol: Символ криптовалюты (например, 'BTC', 'ETH')
        quote: Валюта для отображения цены (по умолчанию 'USD')

    Returns:
        dict | None: Словарь с информацией о цене или None в случае ошибки
        {
            'price': float,
            'change_24h': float,
            'last_updated': int,
            'cached': bool
        }
    """
    if not symbol:
        return None

    sym = symbol.upper()
    q = quote.lower()
    key = (sym, q)
    now = time.time()

    # Проверяем кэш (актуален 5 минут для улучшения производительности)
    if key in _cache and now - _cache[key][1] < 300:
        return {
            "price": _cache[key][0],
            "change_24h": None,
            "last_updated": int(_cache[key][1]),
            "cached": True,
        }

    # Получаем ID монеты для CoinGecko API
    coin_id = ID_MAP.get(sym, sym.lower())

    # URL для CoinGecko Simple Price API
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": q,
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

            if coin_id in data:
                coin_data = data[coin_id]
                price = float(coin_data.get(q, 0.0))
                change_24h = coin_data.get(f"{q}_24h_change")
                last_updated = coin_data.get("last_updated_at")

                if price > 0:
                    # Сохраняем в кэш
                    _cache[key] = (price, now)

                    return {
                        "price": price,
                        "change_24h": change_24h,
                        "last_updated": last_updated,
                        "cached": False,
                    }
                else:
                    return None
            else:
                return None

    except Exception as e:
        print(f"❌ Ошибка при получении информации о цене для {sym}: {e}")
        return None


def get_price_from_binance(symbol: str, quote: str = "USD") -> float | None:
    """Получает цену с Binance API как альтернативный источник."""
    try:
        # Конвертируем символы для Binance API
        binance_symbol = f"{symbol.upper()}USDT"
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": binance_symbol}

        with httpx.Client(timeout=5.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            return float(data.get("price", 0))
    except Exception as e:
        print(f"⚠️ Binance API ошибка для {symbol}: {e}")
        return None


def get_price_from_coinpaprika(symbol: str, quote: str = "USD") -> float | None:
    """Получает цену с CoinPaprika API как альтернативный источник."""
    try:
        # CoinPaprika использует ID монет, а не символы
        coin_id_map = {
            "BTC": "btc-bitcoin",
            "ETH": "eth-ethereum",
            "LINK": "link-chainlink",
            "SOL": "sol-solana",
            "ADA": "ada-cardano",
            "DOT": "dot-polkadot",
            "UNI": "uni-uniswap",
            "MATIC": "matic-polygon",
        }

        coin_id = coin_id_map.get(symbol.upper(), symbol.lower())
        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"

        with httpx.Client(timeout=5.0) as client:
            r = client.get(url)
            r.raise_for_status()
            data = r.json()
            quotes = data.get("quotes", {})
            usd_quote = quotes.get("USD", {})
            return float(usd_quote.get("price", 0))
    except Exception as e:
        print(f"⚠️ CoinPaprika API ошибка для {symbol}: {e}")
        return None


def get_price_from_coinbase(symbol: str, quote: str = "USD") -> float | None:
    """Получает цену с Coinbase API как альтернативный источник."""
    try:
        # Coinbase использует символы напрямую
        url = f"https://api.coinbase.com/v2/exchange-rates"
        params = {"currency": symbol.upper()}

        with httpx.Client(timeout=5.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            rates = data.get("data", {}).get("rates", {})
            usd_rate = rates.get("USD")
            if usd_rate:
                return float(usd_rate)
            return None
    except Exception as e:
        print(f"⚠️ Coinbase API ошибка для {symbol}: {e}")
        return None


def get_price_from_kraken(symbol: str, quote: str = "USD") -> float | None:
    """Получает цену с Kraken API как альтернативный источник."""
    try:
        # Kraken использует специальные символы
        kraken_symbol_map = {
            "BTC": "XXBTZUSD",
            "ETH": "XETHZUSD",
            "LINK": "LINKUSD",
            "SOL": "SOLUSD",
            "ADA": "ADAUSD",
            "DOT": "DOTUSD",
            "UNI": "UNIUSD",
            "MATIC": "MATICUSD",
        }

        kraken_symbol = kraken_symbol_map.get(symbol.upper())
        if not kraken_symbol:
            return None

        url = "https://api.kraken.com/0/public/Ticker"
        params = {"pair": kraken_symbol}

        with httpx.Client(timeout=5.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            result = data.get("result", {})
            if kraken_symbol in result:
                ticker = result[kraken_symbol]
                price = ticker.get("c", [0])[0]  # c[0] = last trade closed price
                return float(price)
            return None
    except Exception as e:
        print(f"⚠️ Kraken API ошибка для {symbol}: {e}")
        return None


def get_price_from_okx(symbol: str, quote: str = "USD") -> float | None:
    """Получает цену с OKX API как альтернативный источник."""
    try:
        # OKX использует символы с дефисом
        okx_symbol = f"{symbol.upper()}-USDT"
        url = "https://www.okx.com/api/v5/market/ticker"
        params = {"instId": okx_symbol}

        with httpx.Client(timeout=5.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            if data.get("code") == "0":
                tickers = data.get("data", [])
                if tickers:
                    ticker = tickers[0]
                    return float(ticker.get("last", 0))
            return None
    except Exception as e:
        print(f"⚠️ OKX API ошибка для {symbol}: {e}")
        return None


def get_price_from_coinmarketcap(symbol: str, quote: str = "USD") -> float | None:
    """Получает цену с CoinMarketCap API как альтернативный источник."""
    try:
        # CoinMarketCap использует ID монет
        cmc_id_map = {
            "BTC": "1",
            "ETH": "1027",
            "LINK": "1975",
            "SOL": "5426",
            "ADA": "2010",
            "DOT": "6636",
            "UNI": "7083",
            "MATIC": "3890",
            "BNB": "1839",
            "XRP": "52",
            "USDT": "825",
            "USDC": "3408",
            "DOGE": "74",
            "TRX": "1958",
        }

        cmc_id = cmc_id_map.get(symbol.upper())
        if not cmc_id:
            return None

        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        params = {"id": cmc_id, "convert": quote.upper()}
        headers = {"X-CMC_PRO_API_KEY": "YOUR_API_KEY_HERE"}  # Нужен API ключ

        # Пробуем без API ключа (ограниченный доступ)
        with httpx.Client(timeout=5.0) as client:
            r = client.get(url, params=params)
            if r.status_code == 200:
                data = r.json()
                if "data" in data and cmc_id in data["data"]:
                    quote_data = data["data"][cmc_id]["quote"][quote.upper()]
                    return float(quote_data["price"])
            return None
    except Exception as e:
        print(f"⚠️ CoinMarketCap API ошибка для {symbol}: {e}")
        return None


def get_smart_rounded_price(price: float, symbol: str) -> float:
    """Возвращает умно округленную цену в зависимости от символа монеты."""
    if not price or price <= 0:
        return 0.0

    # Определяем количество знаков после запятой в зависимости от цены
    if price >= 1000:
        # Для дорогих монет (BTC, ETH) - 2 знака
        return round(price, 2)
    elif price >= 100:
        # Для средних монет (LINK, SOL) - 2 знака
        return round(price, 2)
    elif price >= 1:
        # Для монет $1-100 - 2 знака
        return round(price, 2)
    elif price >= 0.01:
        # Для дешевых монет $0.01-1 - 4 знака
        return round(price, 4)
    else:
        # Для очень дешевых монет <$0.01 - 6 знаков
        return round(price, 6)


def get_aggregated_price(symbol: str, quote: str = "USD") -> dict | None:
    """Получает агрегированную цену из нескольких источников с фильтрацией."""
    if not symbol:
        return None

    sym = symbol.upper()
    q = quote.lower()
    key = (sym, q)
    now = time.time()

    # Проверяем кэш (актуален 5 минут для улучшения производительности)
    if key in _cache and now - _cache[key][1] < 300:
        cached_price = _cache[key][0]
        return {
            "price": cached_price,
            "sources": ["Кэш"],
            "source_count": 1,
            "average_price": cached_price,
            "cached": True,
        }

    # Все доступные источники
    sources = [
        ("CoinGecko", lambda: get_current_price(sym, q)),
        ("Binance", lambda: get_price_from_binance(sym, q)),
        ("CoinPaprika", lambda: get_price_from_coinpaprika(sym, q)),
        ("Coinbase", lambda: get_price_from_coinbase(sym, q)),
        ("Kraken", lambda: get_price_from_kraken(sym, q)),
        ("OKX", lambda: get_price_from_okx(sym, q)),
        ("CoinMarketCap", lambda: get_price_from_coinmarketcap(sym, q)),
    ]

    prices = []
    working_sources = []

    # Убираем отладочные сообщения для улучшения производительности
    # print(f"🔍 Собираем цены для {sym} из {len(sources)} источников...")

    for source_name, source_func in sources:
        try:
            price = source_func()
            if price and price > 0:
                prices.append(price)
                working_sources.append(source_name)
                # print(f"✅ {source_name}: ${price:,.2f}")
            else:
                # print(f"⚠️ {source_name}: недоступно")
                pass
        except Exception as e:
            # print(f"❌ {source_name}: {e}")
            continue

    if not prices:
        # print(f"❌ Все источники недоступны для {sym}")
        return None

    # Фильтруем выбросы (цены, сильно отличающиеся от медианы)
    if len(prices) >= 3:
        median_price = sorted(prices)[len(prices) // 2]
        # Исключаем цены, отличающиеся более чем на 20% от медианы
        filtered_prices = [
            p for p in prices if abs(p - median_price) / median_price <= 0.2
        ]
        if filtered_prices:
            prices = filtered_prices
            # print(f"🔍 Отфильтровано {len(prices)} из {len(prices) + len(sources) - len(working_sources)} цен")

    # Вычисляем среднюю цену
    average_price = sum(prices) / len(prices)

    # Применяем умное округление
    rounded_price = get_smart_rounded_price(average_price, sym)

    # Сохраняем в кэш (округляем для кэша тоже)
    _cache[key] = (rounded_price, now)

    result = {
        "price": rounded_price,
        "sources": working_sources,
        "source_count": len(working_sources),
        "average_price": rounded_price,
        "cached": False,
        "price_range": {
            "min": get_smart_rounded_price(min(prices), sym),
            "max": get_smart_rounded_price(max(prices), sym),
            "spread": get_smart_rounded_price(max(prices) - min(prices), sym),
        },
    }

    # print(f"📊 Средняя цена {sym}: ${average_price:,.2f} (из {len(working_sources)} источников)")
    return result


def get_current_price_fallback(symbol: str, quote: str = "USD") -> float | None:
    """Получает цену с использованием альтернативных источников (обратная совместимость)."""
    result = get_aggregated_price(symbol, quote)
    return result["price"] if result else None


def get_current_price_with_retry(
    symbol: str, quote: str = "USD", max_retries: int = 3
) -> float | None:
    """Получает текущую цену с повторными попытками и задержками.

    Args:
        symbol: Символ криптовалюты
        quote: Валюта для отображения цены
        max_retries: Максимальное количество попыток

    Returns:
        float | None: Текущая цена или None в случае ошибки
    """
    for attempt in range(max_retries):
        try:
            # Добавляем случайную задержку для избежания rate limiting
            if attempt > 0:
                delay = random.uniform(1.0, 3.0) * (attempt + 1)
                print(
                    f"⏳ Попытка {attempt + 1}/{max_retries}, задержка {delay:.1f}с..."
                )
                time.sleep(delay)

            price = get_current_price(symbol, quote)
            if price:
                return price

        except Exception as e:
            print(f"⚠️ Попытка {attempt + 1} неудачна: {e}")
            if attempt == max_retries - 1:
                print(f"❌ Все попытки исчерпаны для {symbol}")
                return None

    return None
