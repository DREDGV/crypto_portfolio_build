# HANDOFF для Cursor — Crypto Portfolio Manager

## 1) TL;DR / Зачем приложение

Локальный (офлайн-дружественный) инструмент учёта криптопортфеля:

- хранит все сделки (покупка/продажа/переводы/обмены) + заметки/источник/стратегию;
- считает позиции по FIFO, среднюю цену, PnL (нереализ. и реализ.);
- подхватывает текущие цены (CoinGecko Simple Price);
- удобный UI с вкладками, фильтрами, редактированием, CSV-экспортом.

**Цель** — быстрый контроль, принятие решений и отсутствие «пропущенной прибыли».

**Ограничения**: без платных сервисов, без серверов, всё локально (Windows 11, Python 3.13).

## 2) Текущий стек и запуск

**Python 3.13**, NiceGUI (веб-UI локально), SQLite + SQLModel, httpx, python-dotenv.

**Доп. зависимость в requirements.txt**: nicegui, sqlmodel, sqlalchemy, aiosqlite, pydantic>=2, httpx, python-dotenv.

**Запуск (Windows)**:
- Первый раз: `setup_once.bat` (виртуалка + зависимости)
- Разработка с авто-перезагрузкой: `run_dev.bat` (ENV DEV=1)
- Прод: `run_prod.bat`
- Открывается `http://127.0.0.1:8080`

**.env пример (не обязателен)**:
```
APP_PORT=8080
REPORT_CURRENCY=USD
LOCAL_TIMEZONE=Europe/Moscow
```

## 3) Структура проекта (папки/файлы)

```
app/
  main.py                 # точки входа NiceGUI и роуты
  ui/pages.py             # все экраны и вкладки (Overview/Positions/Transactions)
  core/models.py          # модели SQLModel и DTO
  core/services.py        # бизнес-логика: CRUD, FIFO, PnL, экспорт CSV
  adapters/prices.py      # CoinGecko Simple Price (+ кэш 60с)
  storage/db.py           # SQLite/SQLModel init (data/portfolio.db)
data/
  backups/                # бэкапы БД
  exports/                # CSV-экспорт
scripts (в корне)
  setup_once.bat / run_dev.bat / run_prod.bat
.vscode/launch.json       # профиль запуска (для Cursor/VS Code)
```

## 4) Данные и бизнес-правила

### Модель Transaction (SQLModel)

**Поля**:
- `id: int PK`
- `coin: str` (например, BTC, ETH; храним в UPPER)
- `type: str` — одно из: buy, sell, exchange_in, exchange_out, deposit, withdrawal
- `quantity: float` (план: перевести на Decimal)
- `price: float` (в валюте отчёта; по умолчанию USD)
- `ts_utc: datetime` (авто now UTC)
- `strategy: str` — long, mid, short, scalp
- `source: str | None` — биржа/кошелёк
- `notes: str | None`

DTO для ввода: `TransactionIn` (те же поля, кроме id/ts).

### FIFO и PnL

- **Ключ лота**: `(coin, strategy)` — позиции раздельно по стратегии, чтобы соответствовать твоему сценарию «несколько корзин».
- **Приход**: buy / exchange_in / deposit — добавляет лоты `{qty, price}`.
- **Расход**: sell / exchange_out / withdrawal — списывает из очереди FIFO, реализованный PnL = `qty * (sell_price - lot_price)`.
- **Позиция**: сумма остатков лотов; `avg_cost = cost_basis / qty`.
- **Нереализованный PnL**: `(current_price * qty) - cost_basis`, % = `(price - avg_cost)/avg_cost * 100`.
- **Реализованный PnL** накапливается по ключу `(coin, strategy)`.

## 5) Интеграция цен (CoinGecko)

**adapters/prices.py**:
- эндпоинт: `GET /api/v3/simple/price?ids={id}&vs_currencies={quote}`
- карта тикеров → id (BTC->bitcoin, XLM->stellar, …)
- кэш на 60 секунд в памяти, таймаут клиента 8с, ошибка → None (UI покажет 0).

## 6) UI (NiceGUI)

**Вкладки**:
- **Overview** — сводные чипы (total value, unrealized PnL, realized PnL) + таблица позиций (FIFO + цены)
- **Positions** — те же позиции, кнопка «Экспорт позиций (CSV)»
- **Transactions** — форма добавления сделки (все поля, autocomplete=off, чтобы Edge не открывал «кошелёк»), таблица со сделками + ✏️ редактирование и 🗑️ удаление, «Экспорт сделок (CSV)»

**Глобальные фильтры** (над вкладками): по монете и стратегии; применяются к позициям и сделкам.

## 7) Что уже работает

- ✅ CRUD сделок (create/list/update/delete)
- ✅ FIFO-агрегация в позиции по (coin, strategy)
- ✅ Нереализованный/реализованный PnL, средняя цена, текущая стоимость
- ✅ Подтяжка цен с CoinGecko (с кэшем)
- ✅ Экспорт CSV: transactions_*.csv, positions_*.csv
- ✅ Простые бэкапы БД (копия data/portfolio.db в data/backups — доступно в коде, кнопку можно добавить)
- ✅ Отключено автозаполнение полей ввода

**Недавняя правка**: добавлены функции `export_transactions_csv` и `export_positions_csv` в `core/services.py` (раньше их недоставало; теперь ок).

## 8) Планы и приоритеты (предлагаемая дорожная карта)

### Итерация 1 — «пользовательские фичи»

**Алерты (локально)**:
- правила: по цене, по % изменения, по нереализ. PnL;
- периодический опрос (APScheduler уже в зависимостях) + всплывающее уведомление в UI;
- (опционально) TelegramWebhook/бот (если захочешь, но можно отложить).

**Аналитика**:
- мини-графики цены/стоимости позиции (7д/30д), PnL по периодам;
- кэш исторических цен (экономим лимиты CoinGecko).

**Импорт CSV**:
- маппинг колонок + предпросмотр;
- базовая нормализация (мульт. запятые, локали).

**Сохранённые фильтры/виды** (быстрый доступ).

### Итерация 2 — «структура портфеля»

**Мультипортфели**: таблица portfolio + FK в Transaction, возможность иметь «Долгосрочный», «Средний», «Скальпинг» как разные портфели (стратегия остаётся, но портфель — надстройка). Миграция: все записи → default.

**Капитал-менеджмент** (рекомендации по «лестнице закупок»):
- конфиги %/ступеней;
- индикатор страха/жадности (бесплатный API) как сигнал (агрегируем, не торгуем автоматически).

### Итерация 3 — «качество и долговечность»

**Точность**: перейти c float на Decimal (Pydantic + SQLModel), единый quantize.

**Тесты** (pytest): юнит для FIFO/PNL, адаптера цен (мок).

**Экспорт/импорт бэкапов** (zip с БД и настройками).

**Упаковка** (PyInstaller) → exe «портативно» по желанию.

## 9) Решения по дизайну и конвенции

- Тикеры всегда UPPER (`.upper().strip()` при вводе)
- Стратегии и типы — из фиксированного списка
- Время в БД — UTC; в UI — локальное (формат `'%Y-%m-%d %H:%M:%S'`)
- Числа: пока float (переход на Decimal в итерации 3)
- Из UI выключено autocomplete (Edge Wallet не мешает)
- Роутинг NiceGUI: `/#/portfolio`, вкладки внутри одной страницы

## 10) Известные грабли (учтено)

- **ImportError** из-за отсутствия функций экспорта — исправлено (проверить, что в проекте есть `export_transactions_csv` и `export_positions_csv`)
- **Edge Wallet автозаполнение** — решено `autocomplete=off`
- **Версии Python 3.13 + SQLModel + Pydantic v2** — всё совместимо (мы используем актуальные пакеты)

## 11) Что нужно Cursor на старте

1. Подтянуть зависимости и запустить `run_dev.bat` (или через `python -m app.main` с ENV DEV=1)
2. Пройтись по файлам:
   - `app/core/services.py` — понять FIFO/экспорт, точки расширения
   - `app/ui/pages.py` — где добавлять вкладки «Alerts», «Analytics», «Import CSV»
   - `app/adapters/prices.py` — доработать кэш/фолбэки/мультивалютность
3. Согласовать дорожную карту (см. п.8) и брать задачи по порядку

## 12) Мини-бэклог задач (готовые формулировки)

### Alerts
Модель `AlertRule` (id, coin, strategy?, kind: price|unreal_pct|unreal_abs, operator, threshold, active, last_trigger_at), планировщик проверки каждые N секунд, UI CRUD + тост-нотификации.

### Analytics
Компонент графика (NiceGUI: Plotly/Highcharts) для стоимости портфеля, PnL по периодам; сервис `history_service.py` (агрегация дневных срезов).

### Import CSV
Загрузка файла, сопоставление колонок (coin, type, qty, price, ts, strategy, source, notes), dry-run, запись пачкой.

### Multi-portfolio
Таблица `Portfolio(id, name)`, FK в `Transaction.portfolio_id`, селектор активного портфеля в шапке, миграция в default.

### Decimal
Переход и миграция, единый слой форматирования.

### Тесты
Юниты на FIFO, реализацию realized/unrealized PnL; мок httpx.
