# Архитектура

## Технологии
Python 3.13, NiceGUI (локальный веб-UI), SQLite + SQLModel/SQLAlchemy, httpx (CoinGecko), APScheduler (алерты/снапшоты), python-dotenv.

## Модули
- **UI (`app/ui/pages.py`)** — вкладки Overview/Positions/Transactions/(Alerts/Analytics), формы, таблицы, фильтры, экспорт.
- **Core (`app/core/services.py`)** — CRUD сделок; FIFO/PNL; экспорт CSV; (позже) алерты, импорт, снапшоты.
- **Adapters (`app/adapters/prices.py`)** — CoinGecko Simple Price, кэш, фолбэки.
- **Storage (`app/storage/db.py`)** — SQLite init, индексы, миграции.
- **Models (`app/core/models.py`)** — `Transaction` (сейчас) + `Portfolio`, `AlertRule`, `PriceStore`, `DailySnapshot` (план).

## Данные (нынешние и план)
- **Transaction:** `id, coin, type, quantity, price, ts_utc, strategy, source, notes`.
- **Portfolio (план):** `id, name` + FK в `Transaction`.
- **AlertRule (план):** `coin, strategy?, kind, op, threshold, cooldown, active, last_trigger_at`.
- **PriceStore (план):** кэш исторических цен.
- **DailySnapshot (план):** `date, portfolio_value, unrealized_pnl, realized_pnl`.

## Конфигурация
`.env`: `APP_PORT`, `REPORT_CURRENCY`, `LOCAL_TIMEZONE`. Порт можно переопределять в запуске.

## Безопасность
Нет внешних логинов/ключей, не отправляем пользовательские данные. Бэкапы локальные, позже — zip/шифрование.

## Тестирование
Юнит-тесты FIFO/PNL; моки CoinGecko; интеграционные тесты экспорта. Позже — CI.

## Упаковка
PyInstaller Portable .exe (по желанию на поздней стадии).
