import time
import httpx

_cache: dict[tuple[str, str], tuple[float, float]] = {}

ID_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'XLM': 'stellar',
    'USDT': 'tether',
    'SOL': 'solana',
    'BNB': 'binancecoin',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'DOGE': 'dogecoin',
    'TRX': 'tron',
    'TON': 'the-open-network',
}

def get_current_price(symbol: str, quote: str = 'USD') -> float | None:
    """Возвращает текущую цену через CoinGecko Simple Price."""
    if not symbol:
        return None
    sym = symbol.upper(); q = quote.lower(); key = (sym, q); now = time.time()
    if key in _cache and now - _cache[key][1] < 60:
        return _cache[key][0]
    coin_id = ID_MAP.get(sym, sym.lower())
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {'ids': coin_id, 'vs_currencies': q}
    try:
        with httpx.Client(timeout=8.0) as client:
            r = client.get(url, params=params); r.raise_for_status(); data = r.json()
            price = float(data.get(coin_id, {}).get(q, 0.0))
            if price > 0:
                _cache[key] = (price, now); return price
            return None
    except Exception:
        return None
