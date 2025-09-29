# 🔧 Настройка API Тинькофф Инвестиции

## 📋 Получение токена API

### 1. Регистрация в Тинькофф Инвестиции
1. Откройте [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/)
2. Зарегистрируйтесь или войдите в аккаунт
3. Откройте раздел "API" в личном кабинете

### 2. Получение токена
1. Перейдите в раздел "API" → "Токены"
2. Создайте новый токен для чтения данных
3. Скопируйте полученный токен

### 3. Настройка в приложении

Создайте файл `.env` в корне проекта:
```env
TINKOFF_API_TOKEN=your_token_here
```

## 🔌 Использование API

### Получение всех акций
```python
import requests
import os

def get_tinkoff_shares():
    """Получает все акции через API Тинькофф"""
    token = os.getenv('TINKOFF_API_TOKEN')
    
    url = "https://invest-public-api.tinkoff.ru/rest/"
    endpoint = "tinkoff.public.invest.api.contract.v1.InstrumentsService/Shares"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "class_code": "TQBR",  # Московская биржа
        "page": 1,
        "page_size": 1000
    }
    
    response = requests.post(f"{url}{endpoint}", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('instruments', [])
    else:
        print(f"Ошибка API: {response.status_code}")
        return []
```

### Получение текущих цен
```python
def get_tinkoff_prices(tickers):
    """Получает текущие цены акций"""
    token = os.getenv('TINKOFF_API_TOKEN')
    
    url = "https://invest-public-api.tinkoff.ru/rest/"
    endpoint = "tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "figi": tickers  # Список FIGI идентификаторов
    }
    
    response = requests.post(f"{url}{endpoint}", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('lastPrices', [])
    else:
        print(f"Ошибка API: {response.status_code}")
        return []
```

## 🌐 Альтернативные источники данных

### 1. Московская биржа (MOEX) - Бесплатно
```python
def get_moex_securities():
    """Получает данные с Московской биржи"""
    url = "https://iss.moex.com/iss/securities.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('securities', {}).get('data', [])
    return []
```

### 2. Finam API - Бесплатно
```python
def get_finam_data():
    """Получает данные через Finam API"""
    # Finam предоставляет бесплатный доступ к данным
    # Документация: https://finam.ru/profile/moex-akcii/
    pass
```

### 3. Yahoo Finance - Бесплатно
```python
import yfinance as yf

def get_yahoo_prices(tickers):
    """Получает цены через Yahoo Finance"""
    prices = {}
    for ticker in tickers:
        try:
            # Для российских акций добавляем .ME
            yahoo_ticker = f"{ticker}.ME"
            stock = yf.Ticker(yahoo_ticker)
            price = stock.history(period="1d")['Close'].iloc[-1]
            prices[ticker] = float(price)
        except:
            prices[ticker] = None
    return prices
```

## 📊 Рекомендации по реализации

### 1. Кэширование данных
```python
import time
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_price(ticker, timestamp):
    """Кэширует цены на 5 минут"""
    return get_real_price(ticker)

def get_price_with_cache(ticker):
    """Получает цену с кэшированием"""
    current_time = int(time.time() // 300) * 300  # Округляем до 5 минут
    return get_cached_price(ticker, current_time)
```

### 2. Обработка ошибок
```python
def safe_get_price(ticker):
    """Безопасное получение цены с fallback"""
    try:
        # Пытаемся получить через Тинькофф API
        price = get_tinkoff_price(ticker)
        if price:
            return price
    except:
        pass
    
    try:
        # Fallback на Yahoo Finance
        price = get_yahoo_price(ticker)
        if price:
            return price
    except:
        pass
    
    # Последний fallback - мок данные
    return get_mock_price(ticker)
```

### 3. Обновление данных
```python
def update_stocks_data():
    """Обновляет данные акций"""
    # Получаем свежие данные
    stocks = get_tinkoff_shares()
    
    # Обновляем базу данных
    for stock in stocks:
        update_stock_in_db(stock)
    
    # Получаем актуальные цены
    tickers = [stock['ticker'] for stock in stocks]
    prices = get_tinkoff_prices(tickers)
    
    # Обновляем цены
    for price_data in prices:
        update_price_in_db(price_data)
```

## 🚀 Следующие шаги

1. **Получите токен Тинькофф API** (если есть аккаунт)
2. **Настройте переменные окружения** в `.env` файле
3. **Реализуйте методы** для получения реальных данных
4. **Добавьте кэширование** для оптимизации запросов
5. **Настройте автоматическое обновление** данных

## ⚠️ Важные замечания

- **Лимиты API**: Тинькофф API имеет лимиты на количество запросов
- **Кэширование**: Обязательно кэшируйте данные, чтобы не превышать лимиты
- **Fallback**: Всегда имейте резервные источники данных
- **Обновление**: Настройте регулярное обновление данных (каждые 5-15 минут)
