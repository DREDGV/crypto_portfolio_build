# TASKS

## 1) Alerts (Итерация 1)
- Модель `AlertRule(id, coin, strategy?, kind: price|unreal_pct|unreal_abs, op, threshold, active, last_trigger_at)`.
- Проверка каждые N сек через APScheduler.
- Триггер → `ui.notify(...)`. (Опционально Telegram webhook/бот.)

## 2) Analytics
- Мини-графики стоимости/цены (7д/30д).
- Сервис кэша исторических цен (локальный JSON/SQLite).

## 3) Import CSV
- Загрузка файла → маппинг колонок (coin,type,qty,price,ts,strategy,source,notes) → предпросмотр → импорт.
- Нормализация чисел (запятые/точки).

## 4) Saved Views
- Сохранение/выбор наборов фильтров и видимости колонок.

## 5) Multi-portfolio (Итерация 2)
- Таблица `Portfolio(id, name)`; `Transaction.portfolio_id` (FK).
- Селектор активного портфеля в header.
- Миграция: все записи → `default`.

## 6) Decimal (Итерация 3)
- Переход на `Decimal` в моделях/сервисах, единый форматтер.

## 7) Tests
- pytest: FIFO/PnL, адаптер цен (моки httpx).
