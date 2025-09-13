# Crypto Portfolio — Local

Локальное приложение для учёта криптопортфеля без платных сервисов: хранит сделки, собирает позиции по FIFO, считает PnL, тянет текущие цены (CoinGecko), показывает сводку и позволяет редактировать/экспортировать данные. Работает на Windows 11 локально, без внешнего сервера.

## Возможности
- **Сделки**: покупка/продажа/обмен/депозит/вывод, поле стратегии (long/mid/short/scalp), источник (биржа/кошелёк), заметки.
- **Позиции**: агрегация по `(coin, strategy)` по **FIFO**, средняя цена, стоимость, нереализованный и реализованный PnL.
- **Цены**: CoinGecko *Simple Price* с кэшем 60 секунд.
- **Интерфейс**: вкладки *Overview / Positions / Transactions*, глобальные фильтры (монета/стратегия), редактирование и удаление сделок.
- **Экспорт**: CSV для сделок и позиций.
- **Бэкапы БД**: в `data/backups` (вызов из сервиса; кнопку можно добавить).

## Стек
Python 3.13, NiceGUI, SQLite + SQLModel/SQLAlchemy, httpx, python-dotenv.

`requirements.txt`:

```
nicegui
sqlmodel
sqlalchemy
aiosqlite
pydantic>=2
httpx
python-dotenv
```

## Быстрый старт (Windows)
1. Установи Python 3.13 (добавь в PATH).
2. В корне проекта:
   - Первый запуск: `setup_once.bat`
   - Режим разработки (автоперезагрузка): `run_dev.bat`
   - Обычный режим: `run_prod.bat`
3. Открой `http://127.0.0.1:8080`.

`.env` (необязательно):

```
APP_PORT=8080
REPORT_CURRENCY=USD
LOCAL_TIMEZONE=Europe/Moscow
```

## Структура проекта

```
app/
main.py # загрузка UI, роуты NiceGUI
ui/pages.py # интерфейс: вкладки, формы, таблицы
core/models.py # модели SQLModel и DTO
core/services.py # бизнес-логика: CRUD, FIFO, PnL, экспорт CSV
adapters/prices.py # CoinGecko Simple Price (+кэш 60с)
storage/db.py # инициализация SQLite (data/portfolio.db)
data/
backups/ # бэкапы
exports/ # экспорт CSV
.vscode/launch.json # профиль запуска для VS Code/Cursor
setup_once.bat / run_dev.bat / run_prod.bat
requirements.txt
```

## Модель данных
`Transaction` (SQLModel, таблица):
- `id: int PK`
- `coin: str` (UPPER)
- `type: str` — `buy | sell | exchange_in | exchange_out | deposit | withdrawal`
- `quantity: float` *(план: Decimal)*
- `price: float` — цена в валюте отчёта (по умолчанию USD)
- `ts_utc: datetime` (UTC now)
- `strategy: str` — `long | mid | short | scalp`
- `source: str | None`, `notes: str | None`

DTO `TransactionIn` — для ввода.

## FIFO и PnL
- Позиция ключуется как **(coin, strategy)** — разделяем долгосрок/средний/краткосрок/скальпинг.
- Приход (`buy`, `exchange_in`, `deposit`) добавляет лоты `{qty, price}`.
- Расход (`sell`, `exchange_out`, `withdrawal`) списывает FIFO, **реализованный PnL** = `qty * (sell_price - lot_price)`.
- Позиция = сумма остатков лотов; `avg_cost = cost_basis / qty`.
- **Нереализованный PnL** = `qty * price_now - cost_basis`; `% = (price_now - avg_cost) / avg_cost * 100`.

## Адаптер цен
`adapters/prices.py`:
- CoinGecko `/api/v3/simple/price?ids={id}&vs_currencies={quote}`
- карта тикеров → id (`BTC->bitcoin`, `XLM->stellar`, …)
- кэш в памяти 60с, таймаут 8с, ошибки → `None`.

## UI (NiceGUI)
- **Overview** — сводка (Total Value, Unrealized/Realized PnL) + таблица позиций.
- **Positions** — те же позиции, кнопка «Экспорт позиций (CSV)».
- **Transactions** — форма добавления, таблица с ✏️редактированием/🗑️удалением, «Экспорт сделок (CSV)».
- **Глобальные фильтры**: по монете и стратегии, применяются к позициям и сделкам.
- Вводы с `autocomplete=off` (чтобы Edge Wallet не вмешивался).

## Дорожная карта
**Итерация 1:** Alerts (APScheduler), Analytics (мини-графики + кэш исторических цен), Import CSV (маппинг и предпросмотр), Saved Views.  
**Итерация 2:** Multi-portfolio (таблица `Portfolio`, FK в `Transaction`), Capital Management (лестница закупок + индикаторы).  
**Итерация 3:** Decimal вместо float, pytest-тесты, zip-backup, PyInstaller.

## Нюансы
- Ранее отсутствовали функции экспорта → `ImportError`. **Исправлено**: `export_transactions_csv` и `export_positions_csv` есть в `app/core/services.py`.
- Edge Wallet автозаполнение отключено (`autocomplete=off`).
