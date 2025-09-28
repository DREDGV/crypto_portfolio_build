"""
Вкладка для работы с российскими акциями
"""

from typing import Any, Optional, List
import logging

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
        from app.services.broker_service import StockService
        from app.models.broker_models import StockTransactionIn, Broker
        from app.adapters.tinkoff_adapter import BrokerManager
        
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
                ui.label("📋 Доступные функции:").classes(
                    "font-semibold text-gray-800"
                )
                ui.label("• Выбор брокера (Тинькофф, Сбер, ВТБ)").classes(
                    "text-gray-700"
                )
                ui.label("• Просмотр доступных акций").classes(
                    "text-gray-700"
                )
                ui.label("• Добавление позиций с автозаполнением").classes(
                    "text-gray-700"
                )
                ui.label("• Расчет прибыли и убытков").classes(
                    "text-gray-700"
                )
                ui.label("• Аналитика портфеля акций").classes("text-gray-700")

        # Выбор брокера
        with ui.card().classes("w-full p-4 mb-6"):
            ui.label("Выбор брокера").classes("text-lg font-semibold text-gray-800 mb-4")
            
            # Dropdown для выбора брокера
            broker_select = ui.select(
                options={},
                label="Брокер",
                placeholder="Выберите брокера..."
            ).classes("w-full mb-4")
            
            # Кнопка синхронизации инструментов
            sync_button = ui.button(
                "🔄 Синхронизировать инструменты",
                icon="sync"
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
                            {"name": "ticker", "label": "Тикер", "field": "ticker", "align": "left"},
                            {"name": "name", "label": "Название", "field": "name", "align": "left"},
                            {"name": "sector", "label": "Сектор", "field": "sector", "align": "left"},
                            {"name": "lot_size", "label": "Лот", "field": "lot_size", "align": "center"},
                            {"name": "currency", "label": "Валюта", "field": "currency", "align": "center"},
                            {"name": "actions", "label": "Действия", "field": "actions", "align": "center"},
                        ]
                        
                        rows = []
                        for instrument in instruments:
                            rows.append({
                                "ticker": instrument.ticker,
                                "name": instrument.name,
                                "sector": instrument.sector or "-",
                                "lot_size": instrument.lot_size,
                                "currency": instrument.currency,
                                "actions": f"add_{instrument.ticker}"
                            })
                        
                        table = ui.table(
                            columns=columns,
                            rows=rows,
                            row_key="ticker"
                        ).classes("w-full")
                        
                        # Обработчик поиска
                        def filter_instruments():
                            query = search_input.value.lower()
                            if query:
                                filtered_rows = [
                                    row for row in rows
                                    if query in row["ticker"].lower() or query in row["name"].lower()
                                ]
                            else:
                                filtered_rows = rows
                            table.rows = filtered_rows
                        
                        search_input.on("input", filter_instruments)
                        
                    else:
                        ui.label("Инструменты не найдены").classes("text-gray-500 italic")
                        
            except Exception as e:
                logger.error(f"Ошибка загрузки инструментов: {e}")
                ui.notify(f"Ошибка загрузки инструментов: {e}", type="negative")
        
        # Обновляем список при изменении брокера
        broker_select.on("change", load_instruments)

        # Добавление позиции
        with ui.card().classes("w-full p-4 mb-6"):
            ui.label("Добавить позицию").classes("text-lg font-semibold text-gray-800 mb-4")
            
            with ui.grid(columns=2).classes("gap-4 w-full"):
                # Тикер
                ticker_input = ui.input(
                    label="Тикер акции",
                    placeholder="Например: SBER, GAZP, LKOH"
                ).classes("w-full")
                
                # Количество
                quantity_input = ui.input(
                    label="Количество акций",
                    value="1"
                ).classes("w-full").props("type=number min=1")
                
                # Цена
                price_input = ui.input(
                    label="Цена за акцию",
                    value="0.00"
                ).classes("w-full").props("type=number step=0.01 min=0")
                
                # Комиссия
                commission_input = ui.input(
                    label="Комиссия",
                    value="0.00"
                ).classes("w-full").props("type=number step=0.01 min=0")
                
                # Тип операции
                type_select = ui.select(
                    options={"buy": "Покупка", "sell": "Продажа"},
                    label="Тип операции",
                    value="buy"
                ).classes("w-full")
                
                # Дата
                date_input = ui.input(
                    label="Дата сделки"
                ).classes("w-full").props("type=date")
            
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
                        ui.notify(f"Текущая цена {ticker}: {price:.2f} ₽", type="positive")
                    else:
                        ui.notify(f"Цена для {ticker} не найдена", type="warning")
                except Exception as e:
                    logger.error(f"Ошибка получения цены: {e}")
                    ui.notify(f"Ошибка получения цены: {e}", type="negative")
            
            ui.button(
                "💰 Получить текущую цену",
                icon="attach_money"
            ).classes("px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg mb-4").on("click", get_current_price)
            
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
                        transaction_date=date_input.value if date_input.value else None
                    )
                    
                    success = stock_service.add_stock_transaction(transaction)
                    if success:
                        ui.notify("✅ Позиция добавлена успешно", type="positive")
                        # Очищаем форму
                        ticker_input.value = ""
                        quantity_input.value = "1"
                        price_input.value = "0.00"
                        commission_input.value = "0.00"
                        load_positions()
                    else:
                        ui.notify("❌ Ошибка добавления позиции", type="negative")
                        
                except Exception as e:
                    logger.error(f"Ошибка добавления позиции: {e}")
                    ui.notify(f"Ошибка добавления позиции: {e}", type="negative")
            
            ui.button(
                "➕ Добавить позицию",
                icon="add"
            ).classes("px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg").on("click", add_position)

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
                            {"name": "ticker", "label": "Тикер", "field": "ticker", "align": "left"},
                            {"name": "broker", "label": "Брокер", "field": "broker_name", "align": "left"},
                            {"name": "quantity", "label": "Количество", "field": "quantity", "align": "right"},
                            {"name": "avg_price", "label": "Ср. цена", "field": "average_price", "align": "right"},
                            {"name": "current_price", "label": "Текущая", "field": "current_price", "align": "right"},
                            {"name": "value", "label": "Стоимость", "field": "total_value", "align": "right"},
                            {"name": "pnl", "label": "P&L", "field": "unrealized_pnl", "align": "right"},
                            {"name": "pnl_percent", "label": "P&L %", "field": "unrealized_pnl_percent", "align": "right"},
                        ]
                        
                        rows = []
                        for position in positions:
                            rows.append({
                                "ticker": position.ticker,
                                "broker_name": position.broker_name,
                                "quantity": f"{position.quantity:,}",
                                "average_price": f"{position.average_price:.2f} ₽",
                                "current_price": f"{position.current_price:.2f} ₽" if position.current_price else "-",
                                "total_value": f"{position.total_value:.2f} ₽" if position.total_value else "-",
                                "unrealized_pnl": f"{position.unrealized_pnl:.2f} ₽" if position.unrealized_pnl else "-",
                                "unrealized_pnl_percent": f"{position.unrealized_pnl_percent:.2f}%" if position.unrealized_pnl_percent else "-",
                            })
                        
                        ui.table(
                            columns=columns,
                            rows=rows,
                            row_key="ticker"
                        ).classes("w-full")
                        
                        # Статистика
                        total_value = sum(p.total_value or 0 for p in positions)
                        total_pnl = sum(p.unrealized_pnl or 0 for p in positions)
                        
                        with ui.row().classes("gap-4 mt-4"):
                            ui.badge(f"Общая стоимость: {total_value:.2f} ₽").classes("px-3 py-1 bg-blue-100 text-blue-800")
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
