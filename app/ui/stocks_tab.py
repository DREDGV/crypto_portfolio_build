"""
Вкладка для работы с акциями
"""

from typing import Any, Optional

try:
    from nicegui import ui as nicegui_ui
except ModuleNotFoundError:
    # Provide a stub so static analyzers still see ui attributes when NiceGUI is missing.
    class _UnavailableUI:
        def __getattr__(self, name: str) -> Any:
            raise RuntimeError("NiceGUI must be installed to use the stocks tab.")

    nicegui_ui = _UnavailableUI()


def create_stocks_tab(ui: Optional[Any] = None):
    """Создает вкладку для работы с акциями"""
    ui = ui or nicegui_ui
    with ui.column().classes("w-full p-4 max-h-[calc(100vh-200px)] overflow-y-auto"):
        # Заголовок
        with ui.row().classes("items-center gap-3 mb-6"):
            ui.icon("trending_up").classes("text-3xl text-blue-600")
            ui.label("Акции").classes("text-3xl font-bold text-gray-800")

        # Информационная карточка
        with ui.card().classes(
            "w-full p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 mb-6"
        ):
            ui.label("📈 Функционал акций в разработке").classes(
                "text-xl font-bold text-blue-800 mb-2"
            )
            ui.label(
                "Эта вкладка предназначена для отслеживания и анализа акций."
            ).classes("text-gray-700 mb-3")

            with ui.column().classes("gap-2 mt-4"):
                ui.label("📋 Планируемые функции:").classes(
                    "font-semibold text-gray-800"
                )
                ui.label("• Добавление и управление позициями по акциям").classes(
                    "text-gray-700"
                )
                ui.label("• Расчет прибыли и убытков по методу FIFO").classes(
                    "text-gray-700"
                )
                ui.label("• Получение актуальных цен через API").classes(
                    "text-gray-700"
                )
                ui.label("• Анализ дивидендов и корпоративных событий").classes(
                    "text-gray-700"
                )
                ui.label("• Графики и аналитика по акциям").classes("text-gray-700")

        # Разделитель
        ui.separator().classes("my-6")

        # Прототип функционала
        with ui.column().classes("w-full gap-4"):
            ui.label("Добавить акцию").classes("text-xl font-semibold text-gray-800")

            with ui.grid(columns=2).classes("gap-4 w-full"):
                # Поле для ввода тикера акции
                with ui.column().classes("gap-1"):
                    ui.label("Тикер акции").classes("text-sm font-medium text-gray-700")
                    ticker = ui.input(
                        placeholder="Например: AAPL, GOOGL, MSFT"
                    ).classes(
                        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    )

                # Поле для количества
                with ui.column().classes("gap-1"):
                    ui.label("Количество").classes("text-sm font-medium text-gray-700")
                    quantity = (
                        ui.input(value="0")
                        .classes(
                            "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        )
                        .props("type=number")
                    )

                # Поле для цены покупки
                with ui.column().classes("gap-1"):
                    ui.label("Цена покупки").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    purchase_price = (
                        ui.input(value="0.00")
                        .classes(
                            "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        )
                        .props("type=number step=0.01")
                    )

                # Поле для даты покупки
                with ui.column().classes("gap-1"):
                    ui.label("Дата покупки").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    purchase_date = (
                        ui.input(value="")
                        .classes(
                            "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        )
                        .props("type=date")
                    )

            # Кнопка добавления
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Добавить акцию", icon="add").classes(
                    "px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-all duration-200"
                ).on("click", lambda: ui.notify("Функционал в разработке", type="info"))

        # Разделитель
        ui.separator().classes("my-6")

        # Список акций (заглушка)
        with ui.column().classes("w-full"):
            ui.label("Ваши акции").classes("text-xl font-semibold text-gray-800 mb-4")

            # Таблица с акциями (заглушка)
            with ui.card().classes("w-full p-4"):
                ui.label("Список акций будет отображаться здесь").classes(
                    "text-gray-500 italic"
                )

                # Пример данных
                columns = [
                    {
                        "name": "ticker",
                        "label": "Тикер",
                        "field": "ticker",
                        "align": "left",
                    },
                    {
                        "name": "quantity",
                        "label": "Количество",
                        "field": "quantity",
                        "align": "right",
                    },
                    {
                        "name": "purchase_price",
                        "label": "Цена покупки",
                        "field": "purchase_price",
                        "align": "right",
                    },
                    {
                        "name": "current_price",
                        "label": "Текущая цена",
                        "field": "current_price",
                        "align": "right",
                    },
                    {"name": "pnl", "label": "P&L", "field": "pnl", "align": "right"},
                ]

                rows = [
                    {
                        "ticker": "AAPL",
                        "quantity": 10,
                        "purchase_price": 150.00,
                        "current_price": 175.50,
                        "pnl": 255.00,
                    },
                    {
                        "ticker": "GOOGL",
                        "quantity": 5,
                        "purchase_price": 2750.00,
                        "current_price": 2800.00,
                        "pnl": 250.00,
                    },
                ]

                table = ui.table(columns=columns, rows=rows, row_key="ticker").classes(
                    "w-full"
                )
