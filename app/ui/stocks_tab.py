"""
Вкладка для работы с российскими акциями
"""

import logging
from datetime import datetime
from typing import Any, Optional

try:
    from nicegui import ui as nicegui_ui
except ModuleNotFoundError:
    # Provide a stub so static analyzers still see ui attributes when NiceGUI is missing.
    class _UnavailableUI:
        def __getattr__(self, name: str) -> Any:
            raise RuntimeError("NiceGUI must be installed to use the stocks tab.")

    nicegui_ui = _UnavailableUI()

logger = logging.getLogger(__name__)


def create_stocks_tab(ui: Optional[Any] = None):
    """Создает вкладку для работы с акциями"""
    ui = ui or nicegui_ui

    # Импортируем сервисы
    try:
        from app.adapters.tinkoff_adapter import BrokerManager
        from app.models.broker_models import StockTransactionIn
        from app.services.broker_service import StockService

        stock_service = StockService()
        broker_manager = BrokerManager()
    except ImportError as e:
        logger.error(f"Ошибка импорта сервисов: {e}")
        ui.label("❌ Ошибка загрузки модулей акций").classes("text-red-500")
        return

    with ui.column().classes("w-full p-4 max-h-[calc(100vh-200px)] overflow-y-auto"):
        # Заголовок
        with ui.row().classes("items-center gap-3 mb-6"):
            ui.icon("trending_up").classes("text-3xl text-blue-600")
            ui.label("Российские акции").classes("text-3xl font-bold text-gray-800")

        # Информационная карточка
        with ui.card().classes(
            "w-full p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 mb-6"
        ):
            ui.label("📈 Управление российскими акциями").classes(
                "text-xl font-bold text-blue-800 mb-2"
            )
            ui.label(
                "Выберите брокера и добавьте позиции по российским акциям."
            ).classes("text-gray-700 mb-3")

            with ui.column().classes("gap-2 mt-4"):
                ui.label("📋 Доступные функции:").classes("font-semibold text-gray-800")
                ui.label("• Выбор брокера (Тинькофф, Сбер, ВТБ)").classes(
                    "text-gray-700"
                )
                ui.label("• Просмотр доступных акций").classes("text-gray-700")
                ui.label("• Добавление позиций с автозаполнением").classes(
                    "text-gray-700"
                )
                ui.label("• Расчет прибыли и убытков").classes("text-gray-700")
                ui.label("• Аналитика портфеля акций").classes("text-gray-700")

        # Выбор брокера
        with ui.card().classes("w-full p-4 mb-6"):
            ui.label("Выбор брокера").classes(
                "text-lg font-semibold text-gray-800 mb-4"
            )

            # Dropdown для выбора брокера
            broker_select = ui.select(options={}, label="Брокер").classes("w-full mb-4")

            # Кнопка синхронизации инструментов
            sync_button = ui.button(
                "🔄 Синхронизировать инструменты", icon="sync"
            ).classes("px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg")

            # Загружаем брокеров
            def load_brokers():
                try:
                    brokers = broker_manager.get_all_brokers()
                    broker_options = {broker.id: broker.name for broker in brokers}
                    broker_select.options = broker_options

                    if broker_options:
                        broker_select.value = list(broker_options.keys())[0]
                        ui.notify(f"Загружено {len(brokers)} брокеров", type="positive")
                    else:
                        ui.notify("Брокеры не найдены", type="warning")

                except Exception as e:
                    logger.error(f"Ошибка загрузки брокеров: {e}")
                    ui.notify(f"Ошибка загрузки брокеров: {e}", type="negative")

            # Синхронизация инструментов
            def sync_instruments():
                selected_broker = broker_select.value
                if not selected_broker:
                    ui.notify("Выберите брокера", type="warning")
                    return

                try:
                    sync_button.loading = True
                    count = stock_service.sync_broker_instruments(selected_broker)
                    ui.notify(f"Синхронизировано {count} инструментов", type="positive")
                    load_instruments()
                except Exception as e:
                    logger.error(f"Ошибка синхронизации: {e}")
                    ui.notify(f"Ошибка синхронизации: {e}", type="negative")
                finally:
                    sync_button.loading = False

            sync_button.on("click", sync_instruments)

            # Загружаем брокеров при инициализации
            load_brokers()

        # Список инструментов
        instruments_container = ui.column().classes("w-full mb-6")

        def load_instruments():
            selected_broker = broker_select.value
            if not selected_broker:
                return

            try:
                instruments = stock_service.get_broker_instruments(selected_broker)

                # Очищаем контейнер
                instruments_container.clear()

                with instruments_container:
                    ui.label(f"Доступные инструменты ({len(instruments)})").classes(
                        "text-lg font-semibold text-gray-800 mb-4"
                    )

                    if instruments:
                        # Поиск
                        search_input = ui.input(
                            placeholder="Поиск по тикеру или названию..."
                        ).classes("w-full mb-4")

                        # Таблица инструментов
                        columns = [
                            {
                                "name": "ticker",
                                "label": "Тикер",
                                "field": "ticker",
                                "align": "left",
                            },
                            {
                                "name": "name",
                                "label": "Название",
                                "field": "name",
                                "align": "left",
                            },
                            {
                                "name": "sector",
                                "label": "Сектор",
                                "field": "sector",
                                "align": "left",
                            },
                            {
                                "name": "lot_size",
                                "label": "Лот",
                                "field": "lot_size",
                                "align": "center",
                            },
                            {
                                "name": "currency",
                                "label": "Валюта",
                                "field": "currency",
                                "align": "center",
                            },
                            {
                                "name": "actions",
                                "label": "Действия",
                                "field": "actions",
                                "align": "center",
                            },
                        ]

                        rows = []
                        for instrument in instruments:
                            rows.append(
                                {
                                    "ticker": instrument.ticker,
                                    "name": instrument.name,
                                    "sector": instrument.sector or "-",
                                    "lot_size": instrument.lot_size,
                                    "currency": instrument.currency,
                                    "actions": f"add_{instrument.ticker}",
                                }
                            )

                        table = ui.table(
                            columns=columns, rows=rows, row_key="ticker"
                        ).classes("w-full")

                        # Обработчик поиска
                        def filter_instruments():
                            query = search_input.value.lower()
                            if query:
                                filtered_rows = [
                                    row
                                    for row in rows
                                    if query in row["ticker"].lower()
                                    or query in row["name"].lower()
                                ]
                            else:
                                filtered_rows = rows
                            table.rows = filtered_rows

                        search_input.on("input", filter_instruments)

                    else:
                        ui.label("Инструменты не найдены").classes(
                            "text-gray-500 italic"
                        )

            except Exception as e:
                logger.error(f"Ошибка загрузки инструментов: {e}")
                ui.notify(f"Ошибка загрузки инструментов: {e}", type="negative")

        # Обновляем список при изменении брокера
        broker_select.on("change", load_instruments)

        # Добавление позиции
        with ui.card().classes("w-full p-4 mb-6"):
            ui.label("Добавить позицию").classes(
                "text-lg font-semibold text-gray-800 mb-4"
            )

            # Улучшенный выбор акций
            with ui.card().classes(
                "w-full p-4 mb-4 bg-blue-50 border-l-4 border-blue-500"
            ):
                ui.label("🔍 Выбор акции").classes(
                    "text-lg font-semibold text-blue-800 mb-3"
                )

                # Поиск акций
                with ui.row().classes("w-full gap-2 mb-3"):
                    search_input = ui.input(
                        label="Поиск акции",
                        placeholder="Введите тикер или название (например: SBER, Сбербанк)",
                    ).classes("flex-1")

                    # Кнопки поиска акций
                    with ui.row().classes("w-full gap-2"):
                        search_all_btn = ui.button(
                            "🔍 Все акции Тинькофф", icon="search"
                        ).classes(
                            "flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
                        )

                        auto_load_btn = ui.button(
                            "⚡ Автозагрузка", icon="download"
                        ).classes(
                            "flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                        )

                        # Привязываем обработчики сразу после создания кнопок
                        search_all_btn.on("click", lambda: search_all_tinkoff_stocks())
                        auto_load_btn.on("click", lambda: auto_load_all_stocks())

                # Результаты поиска
                search_results_container = ui.column().classes("w-full")

                # Выбранная акция
                selected_stock_container = ui.column().classes("w-full mt-3")

                def search_stocks():
                    query = search_input.value.lower().strip()
                    if not query:
                        search_results_container.clear()
                        return

                    try:
                        # Сначала ищем в локальных инструментах
                        instruments = stock_service.get_broker_instruments("tinkoff")
                        matching_instruments = []

                        for instrument in instruments:
                            if (
                                query in instrument.ticker.lower()
                                or query in instrument.name.lower()
                            ):
                                matching_instruments.append(instrument)

                        # Если локальных результатов мало, ищем в MOEX
                        if len(matching_instruments) < 5:
                            try:
                                all_stocks = stock_service.get_all_tinkoff_stocks()
                                for stock in all_stocks:
                                    if (
                                        query in stock["ticker"].lower()
                                        or query in stock["name"].lower()
                                    ):
                                        # Создаем объект инструмента из MOEX данных
                                        from app.models.broker_models import (
                                            StockInstrument,
                                        )

                                        moex_instrument = StockInstrument(
                                            ticker=stock["ticker"],
                                            name=stock["name"],
                                            sector=stock.get("sector", ""),
                                            currency=stock.get("currency", "RUB"),
                                            lot_size=stock.get("lot_size", 1),
                                            broker_id="tinkoff",
                                        )
                                        matching_instruments.append(moex_instrument)
                            except Exception as e:
                                logger.warning(f"Ошибка поиска в MOEX: {e}")

                        # Показываем первые 15 результатов
                        matching_instruments = matching_instruments[:15]

                        search_results_container.clear()

                        if matching_instruments:
                            with search_results_container:
                                ui.label(
                                    f"Найдено {len(matching_instruments)} акций:"
                                ).classes("text-sm text-gray-600 mb-2")

                                for instrument in matching_instruments:
                                    with ui.row().classes(
                                        "w-full p-2 bg-white rounded border hover:bg-blue-50 cursor-pointer"
                                    ):
                                        ui.label(f"📈 {instrument.ticker}").classes(
                                            "font-bold text-blue-600 w-20"
                                        )
                                        ui.label(f"{instrument.name}").classes(
                                            "flex-1 text-gray-800"
                                        )
                                        ui.label(
                                            f"{instrument.sector or 'N/A'}"
                                        ).classes("text-sm text-gray-500 w-32")

                                        def select_instrument(inst=instrument):
                                            ticker_input.value = inst.ticker
                                            selected_stock_container.clear()
                                            with selected_stock_container:
                                                with ui.row().classes(
                                                    "w-full p-3 bg-green-50 rounded border border-green-200"
                                                ):
                                                    ui.icon("check_circle").classes(
                                                        "text-green-600 text-xl mr-2"
                                                    )
                                                    ui.label(
                                                        f"Выбрано: {inst.ticker} - {inst.name}"
                                                    ).classes(
                                                        "text-green-800 font-medium"
                                                    )
                                            search_results_container.clear()

                                        ui.button("Выбрать", icon="add").classes(
                                            "px-3 py-1 bg-blue-600 text-white text-xs"
                                        ).on("click", select_instrument)
                        else:
                            with search_results_container:
                                ui.label("Акции не найдены").classes(
                                    "text-gray-500 italic"
                                )

                    except Exception as e:
                        logger.error(f"Ошибка поиска акций: {e}")
                        ui.notify(f"Ошибка поиска: {e}", type="negative")

                def search_all_tinkoff_stocks():
                    """Поиск всех акций Тинькофф"""
                    try:
                        ui.notify("🔍 Начинаем загрузку акций...", type="info")
                        search_all_btn.loading = True

                        # Получаем расширенный список акций Тинькофф
                        all_tinkoff_stocks = stock_service.get_all_tinkoff_stocks()

                        ui.notify(
                            f"✅ Получено {len(all_tinkoff_stocks)} акций",
                            type="positive",
                        )

                        search_results_container.clear()

                        if all_tinkoff_stocks:
                            with search_results_container:
                                ui.label(
                                    f"📊 Все акции Тинькофф ({len(all_tinkoff_stocks)}):"
                                ).classes("text-lg font-semibold text-purple-800 mb-3")

                                # Группируем по секторам
                                sectors = {}
                                for stock in all_tinkoff_stocks:
                                    sector = stock.get("sector", "Другое")
                                    if sector not in sectors:
                                        sectors[sector] = []
                                    sectors[sector].append(stock)

                                for sector, stocks in sectors.items():
                                    with ui.expansion(
                                        f"📁 {sector} ({len(stocks)})", icon="folder"
                                    ).classes("w-full mb-2"):
                                        for stock in stocks[
                                            :20
                                        ]:  # Показываем первые 20 в секторе
                                            with ui.row().classes(
                                                "w-full p-2 bg-white rounded border hover:bg-purple-50 cursor-pointer mb-1"
                                            ):
                                                ui.label(
                                                    f"📈 {stock['ticker']}"
                                                ).classes(
                                                    "font-bold text-purple-600 w-20"
                                                )
                                                ui.label(f"{stock['name']}").classes(
                                                    "flex-1 text-gray-800"
                                                )
                                                ui.label(
                                                    f"{stock.get('currency', 'RUB')}"
                                                ).classes("text-sm text-gray-500 w-16")

                                                def select_tinkoff_stock(s=stock):
                                                    ticker_input.value = s["ticker"]
                                                    selected_stock_container.clear()
                                                    with selected_stock_container:
                                                        with ui.row().classes(
                                                            "w-full p-3 bg-green-50 rounded border border-green-200"
                                                        ):
                                                            ui.icon(
                                                                "check_circle"
                                                            ).classes(
                                                                "text-green-600 text-xl mr-2"
                                                            )
                                                            ui.label(
                                                                f"Выбрано: {s['ticker']} - {s['name']}"
                                                            ).classes(
                                                                "text-green-800 font-medium"
                                                            )
                                                    search_results_container.clear()

                                                ui.button(
                                                    "Выбрать", icon="add"
                                                ).classes(
                                                    "px-3 py-1 bg-purple-600 text-white text-xs"
                                                ).on(
                                                    "click", select_tinkoff_stock
                                                )

                                        if len(stocks) > 20:
                                            ui.label(
                                                f"... и еще {len(stocks) - 20} акций в этом секторе"
                                            ).classes(
                                                "text-sm text-gray-500 italic text-center"
                                            )
                        else:
                            with search_results_container:
                                ui.label("Не удалось загрузить акции Тинькофф").classes(
                                    "text-red-500 italic"
                                )

                        ui.notify(
                            f"✅ Загружено {len(all_tinkoff_stocks)} акций",
                            type="positive",
                        )

                    except Exception as e:
                        logger.error(f"Ошибка загрузки акций Тинькофф: {e}")
                        ui.notify(f"Ошибка загрузки: {e}", type="negative")
                    finally:
                        search_all_btn.loading = False

                def auto_load_all_stocks():
                    """Автозагрузка всех акций в базу данных"""
                    try:
                        ui.notify("⚡ Начинаем автозагрузку...", type="info")
                        auto_load_btn.loading = True

                        # Получаем все акции с MOEX
                        all_stocks = stock_service.get_all_tinkoff_stocks()

                        ui.notify(
                            f"📊 Получено {len(all_stocks)} акций для загрузки",
                            type="info",
                        )

                        if not all_stocks:
                            ui.notify(
                                "Не удалось получить акции с MOEX", type="negative"
                            )
                            return

                        # Загружаем акции в базу данных
                        loaded_count = 0
                        for stock in all_stocks:
                            try:
                                # Проверяем, есть ли уже такой инструмент
                                existing = stock_service.get_broker_instruments(
                                    "tinkoff"
                                )
                                if not any(
                                    instr.ticker == stock["ticker"]
                                    for instr in existing
                                ):
                                    # Создаем новый инструмент
                                    from datetime import datetime

                                    from sqlmodel import Session

                                    from app.models.broker_models import StockInstrument
                                    from app.storage.db import engine

                                    new_instrument = StockInstrument(
                                        ticker=stock["ticker"],
                                        name=stock["name"],
                                        sector=stock.get("sector", ""),
                                        currency=stock.get("currency", "RUB"),
                                        lot_size=stock.get("lot_size", 1),
                                        is_active=stock.get("is_active", True),
                                        broker_id="tinkoff",
                                        created_at=datetime.utcnow(),
                                        updated_at=datetime.utcnow(),
                                    )

                                    # Сохраняем в базу
                                    with Session(engine) as session:
                                        session.add(new_instrument)
                                        session.commit()

                                    loaded_count += 1
                            except Exception as e:
                                logger.warning(
                                    f"Ошибка загрузки {stock['ticker']}: {e}"
                                )

                        ui.notify(
                            f"✅ Загружено {loaded_count} новых акций в базу данных",
                            type="positive",
                        )

                        # Очищаем результаты поиска
                        search_results_container.clear()

                    except Exception as e:
                        logger.error(f"Ошибка автозагрузки: {e}")
                        ui.notify(f"Ошибка автозагрузки: {e}", type="negative")
                    finally:
                        auto_load_btn.loading = False

                search_input.on("input", search_stocks)

                # Быстрый выбор популярных акций
                ui.label("🔥 Популярные акции:").classes(
                    "text-sm font-medium text-gray-700 mt-4 mb-2"
                )

                popular_stocks = [
                    ("SBER", "Сбербанк", "🏦"),
                    ("GAZP", "Газпром", "⛽"),
                    ("LKOH", "Лукойл", "🛢️"),
                    ("YNDX", "Яндекс", "🔍"),
                    ("NVTK", "Новатэк", "⛽"),
                    ("ROSN", "Роснефть", "🛢️"),
                ]

                with ui.row().classes("flex-wrap gap-2"):
                    for ticker, name, icon in popular_stocks:

                        def quick_select(t=ticker, n=name, i=icon):
                            ticker_input.value = t
                            selected_stock_container.clear()
                            with selected_stock_container:
                                with ui.row().classes(
                                    "w-full p-3 bg-green-50 rounded border border-green-200"
                                ):
                                    ui.icon("check_circle").classes(
                                        "text-green-600 text-xl mr-2"
                                    )
                                    ui.label(f"Выбрано: {t} - {n}").classes(
                                        "text-green-800 font-medium"
                                    )
                            search_results_container.clear()

                        ui.button(f"{icon} {ticker}", icon="add").classes(
                            "px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-800 text-xs rounded"
                        ).on("click", quick_select)

            with ui.grid(columns=2).classes("gap-4 w-full"):
                # Тикер (теперь заполняется автоматически)
                ticker_input = ui.input(
                    label="Тикер акции",
                    placeholder="Выберите акцию выше или введите любой тикер (например: QIWI, AAPL)",
                ).classes("w-full")

                # Подсказка о возможности ввода любых акций
                ui.label(
                    "💡 Можно ввести любой тикер акции - инструмент будет создан автоматически"
                ).classes("text-xs text-blue-600 italic mt-1")

                # Количество
                quantity_input = (
                    ui.input(label="Количество акций", value="1")
                    .classes("w-full")
                    .props("type=number min=1")
                )

                # Цена
                price_input = (
                    ui.input(label="Цена за акцию", value="0.00")
                    .classes("w-full")
                    .props("type=number step=0.01 min=0")
                )

                # Комиссия
                commission_input = (
                    ui.input(label="Комиссия", value="0.00")
                    .classes("w-full")
                    .props("type=number step=0.01 min=0")
                )

                # Тип операции
                type_select = ui.select(
                    options={"buy": "Покупка", "sell": "Продажа"},
                    label="Тип операции",
                    value="buy",
                ).classes("w-full")

                # Дата
                date_input = (
                    ui.input(label="Дата сделки").classes("w-full").props("type=date")
                )

            # Кнопка получения текущей цены
            def get_current_price():
                ticker = ticker_input.value
                broker_id = broker_select.value

                if not ticker or not broker_id:
                    ui.notify("Введите тикер и выберите брокера", type="warning")
                    return

                try:
                    price = stock_service.get_current_price(broker_id, ticker)
                    if price:
                        price_input.value = f"{price:.2f}"
                        ui.notify(
                            f"Текущая цена {ticker}: {price:.2f} ₽", type="positive"
                        )
                    else:
                        ui.notify(f"Цена для {ticker} не найдена", type="warning")
                except Exception as e:
                    logger.error(f"Ошибка получения цены: {e}")
                    ui.notify(f"Ошибка получения цены: {e}", type="negative")

            ui.button("💰 Получить текущую цену", icon="attach_money").classes(
                "px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg mb-4"
            ).on("click", get_current_price)

            # Кнопка добавления
            def add_position():
                try:
                    transaction = StockTransactionIn(
                        ticker=ticker_input.value,
                        broker_id=broker_select.value,
                        quantity=int(quantity_input.value),
                        price=float(price_input.value),
                        commission=float(commission_input.value),
                        transaction_type=type_select.value,
                        transaction_date=date_input.value if date_input.value else None,
                    )

                    success = stock_service.add_stock_transaction(transaction)
                    if success:
                        ui.notify(
                            f"[OK] Позиция {transaction.ticker} добавлена успешно",
                            type="positive",
                        )
                        # Очищаем форму
                        ticker_input.value = ""
                        quantity_input.value = "1"
                        price_input.value = "0.00"
                        commission_input.value = "0.00"
                        load_positions()
                    else:
                        ui.notify("[ERROR] Ошибка добавления позиции", type="negative")

                except Exception as e:
                    logger.error(f"Ошибка добавления позиции: {e}")
                    ui.notify(f"Ошибка добавления позиции: {e}", type="negative")

            ui.button("➕ Добавить позицию", icon="add").classes(
                "px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
            ).on("click", add_position)

        # Текущие позиции
        positions_container = ui.column().classes("w-full")

        def load_positions():
            try:
                positions = stock_service.calculate_stock_positions()

                # Очищаем контейнер
                positions_container.clear()

                with positions_container:
                    ui.label(f"Текущие позиции ({len(positions)})").classes(
                        "text-lg font-semibold text-gray-800 mb-4"
                    )

                    if positions:
                        columns = [
                            {
                                "name": "ticker",
                                "label": "Тикер",
                                "field": "ticker",
                                "align": "left",
                            },
                            {
                                "name": "broker",
                                "label": "Брокер",
                                "field": "broker_name",
                                "align": "left",
                            },
                            {
                                "name": "quantity",
                                "label": "Количество",
                                "field": "quantity",
                                "align": "right",
                            },
                            {
                                "name": "avg_price",
                                "label": "Ср. цена",
                                "field": "average_price",
                                "align": "right",
                            },
                            {
                                "name": "current_price",
                                "label": "Текущая",
                                "field": "current_price",
                                "align": "right",
                            },
                            {
                                "name": "value",
                                "label": "Стоимость",
                                "field": "total_value",
                                "align": "right",
                            },
                            {
                                "name": "pnl",
                                "label": "P&L",
                                "field": "unrealized_pnl",
                                "align": "right",
                            },
                            {
                                "name": "pnl_percent",
                                "label": "P&L %",
                                "field": "unrealized_pnl_percent",
                                "align": "right",
                            },
                            {
                                "name": "first_purchase",
                                "label": "Первая покупка",
                                "field": "first_purchase_date",
                                "align": "center",
                            },
                            {
                                "name": "transactions",
                                "label": "Сделок",
                                "field": "transactions_count",
                                "align": "center",
                            },
                            {
                                "name": "actions",
                                "label": "Действия",
                                "field": "actions",
                                "align": "center",
                            },
                        ]

                        rows = []
                        for position in positions:
                            # Форматируем дату первой покупки
                            first_purchase_str = "-"
                            if position.first_purchase_date:
                                first_purchase_str = (
                                    position.first_purchase_date.strftime("%d.%m.%Y")
                                )

                            rows.append(
                                {
                                    "ticker": position.ticker,
                                    "broker_name": position.broker_name,
                                    "quantity": f"{position.quantity:,}",
                                    "average_price": f"{position.average_price:.2f} ₽",
                                    "current_price": (
                                        f"{position.current_price:.2f} ₽"
                                        if position.current_price
                                        else "-"
                                    ),
                                    "total_value": (
                                        f"{position.total_value:.2f} ₽"
                                        if position.total_value
                                        else "-"
                                    ),
                                    "unrealized_pnl": (
                                        f"{position.unrealized_pnl:.2f} ₽"
                                        if position.unrealized_pnl
                                        else "-"
                                    ),
                                    "unrealized_pnl_percent": (
                                        f"{position.unrealized_pnl_percent:.2f}%"
                                        if position.unrealized_pnl_percent
                                        else "-"
                                    ),
                                    "first_purchase_date": first_purchase_str,
                                    "transactions_count": str(
                                        position.transactions_count or 0
                                    ),
                                    "actions": f"edit_{position.ticker}_{position.broker_id}",  # Идентификатор для кнопок
                                }
                            )

                        # Создаем компактные карточки для каждой позиции
                        for position in positions:
                            with ui.card().classes(
                                "w-full p-3 mb-2 border-l-4 border-blue-500"
                            ):
                                # Компактная строка с основной информацией
                                with ui.row().classes(
                                    "w-full justify-between items-center"
                                ):
                                    # Левая часть - основная информация
                                    with ui.row().classes("items-center gap-4 flex-1"):
                                        # Тикер и брокер
                                        with ui.column().classes("items-start"):
                                            ui.label(f"📈 {position.ticker}").classes(
                                                "text-lg font-bold text-blue-600"
                                            )
                                            ui.label(f"{position.broker_name}").classes(
                                                "text-xs text-gray-500"
                                            )

                                        # Количество и средняя цена
                                        with ui.column().classes("items-center"):
                                            ui.label(
                                                f"{position.quantity:,} шт"
                                            ).classes("text-sm font-semibold")
                                            ui.label(
                                                f"@{position.average_price:.2f} ₽"
                                            ).classes("text-xs text-gray-600")

                                        # Текущая цена и стоимость
                                        with ui.column().classes("items-center"):
                                            current_price_str = (
                                                f"{position.current_price:.2f} ₽"
                                                if position.current_price
                                                else "N/A"
                                            )
                                            ui.label(current_price_str).classes(
                                                "text-sm font-medium"
                                            )
                                            ui.label(
                                                f"{position.total_value:.2f} ₽"
                                            ).classes(
                                                "text-sm font-semibold text-green-600"
                                            )

                                        # P&L
                                        with ui.column().classes("items-center"):
                                            pnl_color = (
                                                "text-green-600"
                                                if position.unrealized_pnl
                                                and position.unrealized_pnl > 0
                                                else "text-red-600"
                                            )
                                            ui.label(
                                                f"{position.unrealized_pnl:.2f} ₽"
                                            ).classes(
                                                f"text-sm font-semibold {pnl_color}"
                                            )
                                            ui.label(
                                                f"{position.unrealized_pnl_percent:.2f}%"
                                            ).classes(f"text-xs {pnl_color}")

                                        # Дополнительная информация
                                        with ui.column().classes("items-center"):
                                            first_purchase_str = (
                                                position.first_purchase_date.strftime(
                                                    "%d.%m.%Y"
                                                )
                                                if position.first_purchase_date
                                                else "N/A"
                                            )
                                            ui.label(f"С {first_purchase_str}").classes(
                                                "text-xs text-gray-500"
                                            )
                                            ui.label(
                                                f"{position.transactions_count or 0} сделок"
                                            ).classes("text-xs text-gray-500")

                                    # Правая часть - кнопки действий
                                    with ui.row().classes("gap-1"):
                                        ui.button("✏️", icon="edit").classes(
                                            "px-2 py-1 bg-blue-600 text-white text-xs"
                                        ).on(
                                            "click", lambda p=position: edit_position(p)
                                        )
                                        ui.button("📊", icon="history").classes(
                                            "px-2 py-1 bg-green-600 text-white text-xs"
                                        ).on(
                                            "click",
                                            lambda p=position: show_position_history(p),
                                        )
                                        ui.button("💰", icon="sell").classes(
                                            "px-2 py-1 bg-red-600 text-white text-xs"
                                        ).on(
                                            "click", lambda p=position: sell_position(p)
                                        )

                        # Статистика
                        total_value = sum(p.total_value or 0 for p in positions)
                        total_pnl = sum(p.unrealized_pnl or 0 for p in positions)

                        with ui.row().classes("gap-4 mt-4"):
                            ui.badge(f"Общая стоимость: {total_value:.2f} ₽").classes(
                                "px-3 py-1 bg-blue-100 text-blue-800"
                            )
                            ui.badge(f"Общий P&L: {total_pnl:.2f} ₽").classes(
                                f"px-3 py-1 {'bg-green-100 text-green-800' if total_pnl >= 0 else 'bg-red-100 text-red-800'}"
                            )
                    else:
                        ui.label("Позиции не найдены").classes("text-gray-500 italic")

            except Exception as e:
                logger.error(f"Ошибка загрузки позиций: {e}")
                ui.notify(f"Ошибка загрузки позиций: {e}", type="negative")

        # Загружаем позиции при инициализации
        load_positions()

        # Функции для работы с позициями
        def edit_position(position):
            """Редактирование позиции"""
            with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg"):
                ui.label(f"Управление позицией {position.ticker}").classes(
                    "text-lg font-semibold mb-4"
                )

                # Текущая информация о позиции
                with ui.card().classes("w-full p-3 mb-4 bg-gray-50"):
                    with ui.row().classes("w-full justify-between text-sm"):
                        ui.label(f"Количество: {position.quantity:,} шт")
                        ui.label(f"Средняя цена: {position.average_price:.2f} ₽")
                        ui.label(f"Стоимость: {position.total_value:.2f} ₽")

                # Вкладки для покупки и продажи
                with ui.tabs().classes("w-full mb-4") as tabs:
                    buy_tab = ui.tab("🛒 Покупка")
                    sell_tab = ui.tab("💰 Продажа")

                with ui.tab_panels(tabs, value=buy_tab).classes("w-full"):
                    # Вкладка покупки
                    with ui.tab_panel(buy_tab):
                        with ui.column().classes("gap-3 w-full"):
                            ui.label("Покупка дополнительных акций").classes(
                                "text-md font-medium text-green-600"
                            )

                            buy_quantity_input = ui.input(
                                label="Количество к покупке",
                                placeholder="Введите количество",
                            ).classes("w-full")

                            buy_price_input = ui.input(
                                label="Цена за акцию", placeholder="Введите цену"
                            ).classes("w-full")

                            buy_commission_input = ui.input(
                                label="Комиссия", value="0.00"
                            ).classes("w-full")

                            buy_date_input = (
                                ui.input(
                                    label="Дата сделки",
                                    value=datetime.now().strftime("%Y-%m-%d"),
                                )
                                .classes("w-full")
                                .props("type=date")
                            )

                            # Кнопки быстрой покупки
                            ui.label("Быстрый выбор:").classes(
                                "text-xs text-gray-600 mt-2"
                            )

                            # Кнопка быстрой покупки по текущей цене
                            if position.current_price:
                                ui.button(
                                    f"🔄 Купить по текущей цене ({position.current_price:.2f} ₽)",
                                    icon="refresh",
                                ).classes("w-full bg-green-100 text-green-800").tooltip(
                                    "Установить текущую рыночную цену"
                                ).on(
                                    "click",
                                    lambda: set_buy_price(
                                        position.current_price, buy_price_input
                                    ),
                                )

                            # Кнопки быстрого выбора количества
                            with ui.row().classes("w-full gap-2 mt-2"):
                                ui.button("+1", icon="add").classes(
                                    "flex-1 bg-green-100 text-green-800"
                                ).tooltip("Купить 1 дополнительную акцию").on(
                                    "click",
                                    lambda: buy_quantity_input.set_value("1"),
                                )
                                ui.button("+10", icon="add").classes(
                                    "flex-1 bg-green-100 text-green-800"
                                ).tooltip("Купить 10 дополнительных акций").on(
                                    "click",
                                    lambda: buy_quantity_input.set_value("10"),
                                )

                    # Вкладка продажи
                    with ui.tab_panel(sell_tab):
                        with ui.column().classes("gap-3 w-full"):
                            ui.label("Продажа акций").classes(
                                "text-md font-medium text-red-600"
                            )

                            sell_quantity_input = ui.input(
                                label="Количество к продаже",
                                value=str(position.quantity),
                                placeholder=f"Максимум: {position.quantity} шт",
                            ).classes("w-full")

                            sell_price_input = ui.input(
                                label="Цена продажи", placeholder="Введите цену"
                            ).classes("w-full")

                            sell_commission_input = ui.input(
                                label="Комиссия", value="0.00"
                            ).classes("w-full")

                            sell_date_input = (
                                ui.input(
                                    label="Дата сделки",
                                    value=datetime.now().strftime("%Y-%m-%d"),
                                )
                                .classes("w-full")
                                .props("type=date")
                            )

                            # Кнопки быстрой продажи с пояснениями
                            ui.label("Быстрый выбор количества:").classes(
                                "text-xs text-gray-600 mt-2"
                            )
                            with ui.row().classes("w-full gap-2"):
                                ui.button("50%", icon="percent").classes(
                                    "flex-1 bg-red-100 text-red-800"
                                ).tooltip("Продать половину от текущего количества").on(
                                    "click",
                                    lambda: set_sell_quantity(
                                        position.quantity // 2, sell_quantity_input
                                    ),
                                )
                                ui.button("100%", icon="all_inclusive").classes(
                                    "flex-1 bg-red-100 text-red-800"
                                ).tooltip("Продать все акции").on(
                                    "click",
                                    lambda: set_sell_quantity(
                                        position.quantity, sell_quantity_input
                                    ),
                                )

                # Кнопки действий
                with ui.row().classes("w-full gap-2 mt-4"):
                    ui.button("🛒 Купить", icon="shopping_cart").classes(
                        "flex-1 bg-green-600 text-white"
                    ).on(
                        "click",
                        lambda: save_transaction(
                            position,
                            "buy",
                            buy_quantity_input.value,
                            buy_price_input.value,
                            buy_commission_input.value,
                            buy_date_input.value,
                            dialog,
                        ),
                    )
                    ui.button("💰 Продать", icon="sell").classes(
                        "flex-1 bg-red-600 text-white"
                    ).on(
                        "click",
                        lambda: save_transaction(
                            position,
                            "sell",
                            sell_quantity_input.value,
                            sell_price_input.value,
                            sell_commission_input.value,
                            sell_date_input.value,
                            dialog,
                        ),
                    )
                    ui.button("Отмена", icon="cancel").classes(
                        "flex-1 bg-gray-500 text-white"
                    ).on("click", dialog.close)

            dialog.open()

        def set_buy_price(price, price_input):
            """Установить цену покупки"""
            price_input.value = str(price)

        def set_sell_quantity(quantity, quantity_input):
            """Установить количество продажи"""
            quantity_input.value = str(quantity)

        def save_transaction(
            position, transaction_type, quantity, price, commission, date, dialog
        ):
            """Сохранение транзакции"""
            try:
                if not quantity or not price:
                    ui.notify("Заполните количество и цену", type="warning")
                    return

                transaction = StockTransactionIn(
                    ticker=position.ticker,
                    broker_id=position.broker_id,
                    quantity=int(quantity),
                    price=float(price),
                    commission=float(commission or 0),
                    transaction_type=transaction_type,
                    transaction_date=date if date else None,
                )

                success = stock_service.add_stock_transaction(transaction)
                if success:
                    action_text = "покупка" if transaction_type == "buy" else "продажа"
                    ui.notify(
                        f"[OK] {action_text.capitalize()} {position.ticker} выполнена",
                        type="positive",
                    )
                    dialog.close()
                    load_positions()
                else:
                    ui.notify("[ERROR] Ошибка сохранения транзакции", type="negative")

            except Exception as e:
                logger.error(f"Ошибка сохранения транзакции: {e}")
                ui.notify(f"Ошибка: {e}", type="negative")

        def save_position_edit(
            position, quantity, price, commission, transaction_type, date, dialog
        ):
            """Сохранение изменений позиции"""
            try:
                transaction = StockTransactionIn(
                    ticker=position.ticker,
                    broker_id=position.broker_id,
                    quantity=int(quantity),
                    price=float(price),
                    commission=float(commission),
                    transaction_type=transaction_type,
                    transaction_date=date if date else None,
                )

                success = stock_service.add_stock_transaction(transaction)
                if success:
                    ui.notify(
                        f"[OK] Транзакция {position.ticker} добавлена", type="positive"
                    )
                    dialog.close()
                    load_positions()
                else:
                    ui.notify("[ERROR] Ошибка добавления транзакции", type="negative")

            except Exception as e:
                logger.error(f"Ошибка редактирования позиции: {e}")
                ui.notify(f"Ошибка редактирования: {e}", type="negative")

        def show_position_history(position):
            """Показать историю сделок по позиции"""
            with ui.dialog() as dialog, ui.card().classes("w-full max-w-5xl"):
                ui.label(f"История сделок {position.ticker}").classes(
                    "text-lg font-semibold mb-4"
                )

                try:
                    # Получаем все транзакции по этой позиции
                    transactions = stock_service.get_stock_transactions()
                    position_transactions = [
                        t
                        for t in transactions
                        if t.ticker == position.ticker
                        and t.broker_id == position.broker_id
                    ]

                    if position_transactions:
                        # Сортируем по дате (новые сверху)
                        position_transactions.sort(
                            key=lambda x: x.transaction_date or datetime.min,
                            reverse=True,
                        )

                        # Создаем детальную таблицу
                        with ui.table().classes("w-full text-sm"):
                            # Заголовки
                            with ui.table_head():
                                with ui.table_row():
                                    ui.table_header("Дата").classes("text-left")
                                    ui.table_header("Тип").classes("text-center")
                                    ui.table_header("Количество").classes("text-right")
                                    ui.table_header("Цена").classes("text-right")
                                    ui.table_header("Комиссия").classes("text-right")
                                    ui.table_header("Сумма").classes("text-right")
                                    ui.table_header("Остаток").classes("text-right")

                            # Строки данных
                            with ui.table_body():
                                running_quantity = 0
                                for t in position_transactions:
                                    # Вычисляем остаток после транзакции
                                    if t.transaction_type == "buy":
                                        running_quantity += t.quantity
                                    else:
                                        running_quantity -= t.quantity

                                    total_amount = t.quantity * t.price + (
                                        t.commission
                                        if t.transaction_type == "buy"
                                        else -t.commission
                                    )

                                    with ui.table_row():
                                        # Дата
                                        date_str = (
                                            t.transaction_date.strftime(
                                                "%d.%m.%Y %H:%M"
                                            )
                                            if t.transaction_date
                                            else "Неизвестно"
                                        )
                                        ui.table_cell(date_str).classes("text-xs")

                                        # Тип операции
                                        type_color = (
                                            "text-green-600"
                                            if t.transaction_type == "buy"
                                            else "text-red-600"
                                        )
                                        type_text = (
                                            "🛒 Покупка"
                                            if t.transaction_type == "buy"
                                            else "💰 Продажа"
                                        )
                                        ui.table_cell(type_text).classes(
                                            f"text-center font-medium {type_color}"
                                        )

                                        # Количество
                                        ui.table_cell(f"{t.quantity:,}").classes(
                                            "text-right"
                                        )

                                        # Цена
                                        ui.table_cell(f"{t.price:.2f} ₽").classes(
                                            "text-right"
                                        )

                                        # Комиссия
                                        ui.table_cell(f"{t.commission:.2f} ₽").classes(
                                            "text-right text-gray-500"
                                        )

                                        # Сумма
                                        amount_color = (
                                            "text-green-600"
                                            if t.transaction_type == "buy"
                                            else "text-red-600"
                                        )
                                        ui.table_cell(f"{total_amount:.2f} ₽").classes(
                                            f"text-right font-medium {amount_color}"
                                        )

                                        # Остаток
                                        ui.table_cell(f"{running_quantity:,}").classes(
                                            "text-right font-semibold"
                                        )

                        # Итоговая статистика
                        with ui.card().classes("w-full p-3 mt-4 bg-gray-50"):
                            total_bought = sum(
                                t.quantity
                                for t in position_transactions
                                if t.transaction_type == "buy"
                            )
                            total_sold = sum(
                                t.quantity
                                for t in position_transactions
                                if t.transaction_type == "sell"
                            )
                            total_commission = sum(
                                t.commission for t in position_transactions
                            )

                            with ui.row().classes("w-full justify-between text-sm"):
                                ui.label(f"Всего куплено: {total_bought:,} шт")
                                ui.label(f"Всего продано: {total_sold:,} шт")
                                ui.label(f"Текущий остаток: {position.quantity:,} шт")
                                ui.label(f"Общая комиссия: {total_commission:.2f} ₽")
                    else:
                        ui.label("История сделок не найдена").classes(
                            "text-gray-500 italic text-center py-8"
                        )

                except Exception as e:
                    logger.error(f"Ошибка загрузки истории: {e}")
                    ui.notify(f"Ошибка загрузки истории: {e}", type="negative")
                    ui.label(f"Ошибка: {e}").classes("text-red-500 text-center py-8")

                ui.button("Закрыть", icon="close").classes(
                    "w-full mt-4 bg-gray-500 text-white"
                ).on("click", dialog.close)

            dialog.open()

        def sell_position(position):
            """Продажа позиции"""
            with ui.dialog() as dialog, ui.card().classes("w-full max-w-md"):
                ui.label(f"Продажа позиции {position.ticker}").classes(
                    "text-lg font-semibold mb-4"
                )

                with ui.column().classes("gap-3 w-full"):
                    ui.label(f"Доступно к продаже: {position.quantity} шт")
                    ui.label(f"Средняя цена покупки: {position.average_price:.2f} ₽")

                    quantity_input = ui.input(
                        label="Количество к продаже", value=str(position.quantity)
                    ).classes("w-full")
                    price_input = ui.input(
                        label="Цена продажи", placeholder="Введите цену"
                    ).classes("w-full")
                    commission_input = ui.input(label="Комиссия", value="0.00").classes(
                        "w-full"
                    )
                    date_input = (
                        ui.input(
                            label="Дата сделки",
                            value=datetime.now().strftime("%Y-%m-%d"),
                        )
                        .classes("w-full")
                        .props("type=date")
                    )

                    with ui.row().classes("w-full gap-2"):
                        ui.button("Продать", icon="sell").classes(
                            "flex-1 bg-red-600 text-white"
                        ).on(
                            "click",
                            lambda: execute_sell(
                                position,
                                quantity_input.value,
                                price_input.value,
                                commission_input.value,
                                date_input.value,
                                dialog,
                            ),
                        )
                        ui.button("Отмена", icon="cancel").classes(
                            "flex-1 bg-gray-500 text-white"
                        ).on("click", dialog.close)

            dialog.open()

        def execute_sell(position, quantity, price, commission, date, dialog):
            """Выполнение продажи"""
            try:
                transaction = StockTransactionIn(
                    ticker=position.ticker,
                    broker_id=position.broker_id,
                    quantity=int(quantity),
                    price=float(price),
                    commission=float(commission),
                    transaction_type="sell",
                    transaction_date=date if date else None,
                )

                success = stock_service.add_stock_transaction(transaction)
                if success:
                    ui.notify(
                        f"[OK] Продажа {position.ticker} выполнена", type="positive"
                    )
                    dialog.close()
                    load_positions()
                else:
                    ui.notify("[ERROR] Ошибка продажи", type="negative")

            except Exception as e:
                logger.error(f"Ошибка продажи: {e}")
                ui.notify(f"Ошибка продажи: {e}", type="negative")
