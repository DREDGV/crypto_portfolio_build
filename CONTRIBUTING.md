# CONTRIBUTING (для Cursor/соавторов)

## Процесс
1) Распаковать/клонировать в одну папку (напр. `C:\CryptoPortfolio\`).  
2) `setup_once.bat` один раз, затем `run_dev.bat` — автоперезагрузка UI.  
3) Коммиты маленькими порциями.

## Ветки и коммиты
- Ветки фич/фиксов: `feat/alerts`, `fix/csv-export`, `chore/docs` и т.п.
- Сообщения:
  - `feat: добавлен Alerts`
  - `fix: исправлен экспорт CSV`
  - `refactor: ...`
  - `docs: ...`
  - `test: ...`
  - `chore: ...`

## Код-стайл
- Python ≥ 3.13, Pydantic v2, SQLModel.
- Типизация по возможности.
- Ошибки не глотаем — уведомляем UI/логируем.
- Сейчас `float`, позже миграция на `Decimal`.
- Вводы в UI — `autocomplete=off`.

## Где править
- Бизнес-логика (FIFO, экспорт, импорт, алерты): `app/core/services.py` (и рядом новые файлы).
- UI (вкладки/формы/таблицы/диалоги): `app/ui/pages.py`.
- Цены: `app/adapters/prices.py`.
- БД: `app/storage/db.py`.

## Тестирование
- Добавить `pytest` и покрыть: FIFO/PnL, адаптер цен (моки httpx).

## Roadmap (кратко)
- Итерация 1: Alerts, Analytics, Import CSV, Saved Views.
- Итерация 2: Multi-portfolio, Capital Management.
- Итерация 3: Decimal, Tests, Zip-backup, PyInstaller.

## Известные грабли
- Старые сборки без экспорт-функций → `ImportError` (сейчас есть в `services.py`).
- Автоподстановка Edge Wallet — отключено.
