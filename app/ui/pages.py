import os

from nicegui import ui

from app.core.models import TransactionIn
from app.core.services import (
    add_transaction,
    delete_transaction,
    enrich_positions_with_market,
    export_positions_csv,
    export_transactions_csv,
    get_portfolio_stats,
    get_transaction,
    get_transaction_stats,
    list_transactions,
    positions_fifo,
    update_transaction,
)

CURRENCY = os.getenv("REPORT_CURRENCY", "USD").upper()
TYPES = ["buy", "sell", "exchange_in", "exchange_out", "deposit", "withdrawal"]
STRATS = ["long", "mid", "short", "scalp"]

# Иконки для типов транзакций
TYPE_ICONS = {
    "buy": "📈",
    "sell": "📉",
    "exchange_in": "↗️",
    "exchange_out": "↘️",
    "deposit": "💰",
    "withdrawal": "💸",
}

# Иконки для стратегий
STRATEGY_ICONS = {"long": "🦅", "mid": "⚖️", "short": "⚡", "scalp": "🎯"}


# Цвета для PnL
def get_pnl_color(value):
    if value > 0:
        return "text-green-600"
    elif value < 0:
        return "text-red-600"
    else:
        return "text-gray-600"


def table_row_with_actions(row, refresh_callback=None):
    rid = int(row["id"])
    with ui.row().classes("gap-1"):
        ui.button("✏️", on_click=lambda: open_edit_dialog(row, refresh_callback)).props(
            "flat size=sm"
        ).tooltip("Редактировать")
        ui.button(
            "🗑️",
            on_click=lambda: (
                delete_transaction(rid),
                ui.notify("Удалено", color="positive"),
                refresh_callback() if refresh_callback else None,
            ),
        ).props("flat size=sm").tooltip("Удалить")


def open_edit_dialog(row, refresh_callback=None):
    data = get_transaction(int(row["id"]))
    with ui.dialog() as dialog, ui.card().classes("min-w-[500px] p-6"):
        # Заголовок с иконкой
        with ui.row().classes("items-center gap-2 mb-4"):
            ui.icon("edit").classes("text-blue-600 text-xl")
            ui.label(f'Редактировать сделку #{data["id"]}').classes(
                "text-lg font-bold text-gray-800"
            )

        # Форма в две колонки
        with ui.grid(columns=2).classes("gap-4"):
            # Левая колонка
            with ui.column().classes("gap-3"):
                e_coin = (
                    ui.input("Монета", placeholder="BTC, ETH, SOL...")
                    .props("uppercase")
                    .classes("w-full")
                )
                e_coin.value = data["coin"]

                e_type = ui.select(
                    TYPES, label="Тип операции", value=data["type"]
                ).classes("w-full")

                e_qty = (
                    ui.input("Количество", placeholder="0.0")
                    .props("type=number inputmode=decimal")
                    .classes("w-full")
                )
                e_qty.value = str(data["quantity"])

                e_price = (
                    ui.input("Цена за монету", placeholder="0.00")
                    .props("type=number inputmode=decimal")
                    .classes("w-full")
                )
                e_price.value = str(data["price"])

            # Правая колонка
            with ui.column().classes("gap-3"):
                e_strat = ui.select(
                    STRATS, label="Стратегия", value=data["strategy"]
                ).classes("w-full")

                e_src = ui.input(
                    "Источник", placeholder="Binance, Coinbase..."
                ).classes("w-full")
                e_src.value = data.get("source") or ""

                e_notes = ui.textarea(
                    "Заметки", placeholder="Дополнительная информация..."
                ).classes("w-full")
                e_notes.value = data.get("notes") or ""

        # Кнопки действий
        with ui.row().classes("justify-end gap-3 mt-6"):

            def save_changes():
                try:
                    update_transaction(
                        data["id"],
                        TransactionIn(
                            coin=(e_coin.value or "").upper().strip(),
                            type=e_type.value,
                            quantity=float(e_qty.value or 0),
                            price=float(e_price.value or 0),
                            strategy=e_strat.value,
                            source=(e_src.value or "").strip(),
                            notes=(e_notes.value or "").strip(),
                        ),
                    )
                    ui.notify("✅ Сделка успешно обновлена", type="positive")
                    dialog.close()
                    if refresh_callback:
                        refresh_callback()
                except Exception as e:
                    ui.notify(f"❌ Ошибка: {e}", type="negative")

            ui.button("Отмена", on_click=dialog.close).props("outline").classes(
                "px-4 py-2"
            )
            ui.button("Сохранить изменения", on_click=save_changes).props(
                "color=primary"
            ).classes("px-4 py-2")

        dialog.open()


def show_about_page():
    """Показывает страницу 'О программе' с информацией о версии и ченджлоге."""
    from app.core.version import get_app_info

    app_info = get_app_info()

    # Создаем полноэкранный контент
    with ui.column().classes("w-full h-screen overflow-hidden"):
        # Заголовок страницы
        with ui.row().classes(
            "items-center justify-between mb-1 p-2 bg-blue-50 border-b"
        ):
            with ui.row().classes("items-center gap-2"):
                ui.icon("info").classes("text-base text-blue-600")
                ui.label("О программе").classes("text-base font-bold text-gray-800")
            ui.button(icon="arrow_back").props("flat round").on(
                "click", lambda: ui.navigate.to("/")
            )

        # Содержимое с табами
        with ui.tabs().classes("w-full text-xs px-2 py-0") as tabs:
            ui.tab("Общая информация", icon="info").classes("px-2 py-1 text-xs")
            ui.tab("История изменений", icon="history").classes("px-2 py-1 text-xs")
            ui.tab("Концепция", icon="lightbulb").classes("px-2 py-1 text-xs")
            ui.tab("Планы развития", icon="trending_up").classes("px-2 py-1 text-xs")

        with ui.tab_panels(tabs, value="Общая информация").classes(
            "w-full h-[calc(100vh-60px)]"
        ):
            # Общая информация
            with ui.tab_panel("Общая информация"):
                with ui.scroll_area().classes("h-full w-full"):
                    with ui.column().classes("p-6 space-y-4"):
                        # Основная информация
                        with ui.card().classes(
                            "p-4 bg-gradient-to-r from-blue-50 to-indigo-50"
                        ):
                            ui.label(f"📱 {app_info['name']}").classes(
                                "text-base font-bold text-blue-800"
                            )
                            ui.label(f"🔢 Версия: {app_info['version']}").classes(
                                "text-sm text-gray-700"
                            )
                            ui.label(f"📝 {app_info['description']}").classes(
                                "text-sm text-gray-600"
                            )

                        # Технические детали
                        with ui.card().classes("p-4"):
                            ui.label("🔧 Технические детали").classes(
                                "text-sm font-semibold mb-2"
                            )
                            with ui.column().classes("space-y-1 text-sm"):
                                ui.label("• Архитектура: Clean Architecture")
                                ui.label("• База данных: SQLite с SQLModel")
                                ui.label("• UI: NiceGUI с современным дизайном")
                                ui.label("• API: Множественные источники цен")
                                ui.label("• Экспорт: CSV форматы")

                        # Источники данных
                        with ui.card().classes("p-4"):
                            ui.label("📊 Источники данных").classes(
                                "text-sm font-semibold mb-2"
                            )
                            with ui.column().classes("space-y-1 text-sm"):
                                ui.label("• CoinGecko (основной)")
                                ui.label("• Binance, Coinbase, Kraken")
                                ui.label("• OKX, CoinPaprika")
                                ui.label("• CoinMarketCap (готов к подключению)")

            # История изменений
            with ui.tab_panel("История изменений"):
                with ui.scroll_area().classes("h-full w-full"):
                    with ui.column().classes("p-4"):
                        ui.html(
                            f"""
                        <style>
                        .about-content h1 {{ font-size: 1.5rem !important; font-weight: 700 !important; margin: 1rem 0 0.5rem 0 !important; color: #1f2937 !important; }}
                        .about-content h2 {{ font-size: 1.3rem !important; font-weight: 600 !important; margin: 0.8rem 0 0.4rem 0 !important; color: #374151 !important; }}
                        .about-content h3 {{ font-size: 1.1rem !important; font-weight: 600 !important; margin: 0.6rem 0 0.3rem 0 !important; color: #4b5563 !important; }}
                        .about-content p {{ font-size: 0.875rem !important; margin: 0.3rem 0 !important; line-height: 1.5 !important; }}
                        .about-content ul {{ font-size: 0.875rem !important; margin: 0.3rem 0 !important; }}
                        .about-content li {{ font-size: 0.875rem !important; margin: 0.2rem 0 !important; line-height: 1.4 !important; }}
                        .about-content strong {{ font-weight: 600 !important; }}
                        </style>
                        <div class="about-content">
                        {app_info["changelog"]}
                        </div>
                        """
                        )

            # Концепция
            with ui.tab_panel("Концепция"):
                with ui.scroll_area().classes("h-full w-full"):
                    with ui.column().classes("p-4"):
                        ui.html(
                            f"""
                        <style>
                        .about-content h1 {{ font-size: 1.5rem !important; font-weight: 700 !important; margin: 1rem 0 0.5rem 0 !important; color: #1f2937 !important; }}
                        .about-content h2 {{ font-size: 1.3rem !important; font-weight: 600 !important; margin: 0.8rem 0 0.4rem 0 !important; color: #374151 !important; }}
                        .about-content h3 {{ font-size: 1.1rem !important; font-weight: 600 !important; margin: 0.6rem 0 0.3rem 0 !important; color: #4b5563 !important; }}
                        .about-content p {{ font-size: 0.875rem !important; margin: 0.3rem 0 !important; line-height: 1.5 !important; }}
                        .about-content ul {{ font-size: 0.875rem !important; margin: 0.3rem 0 !important; }}
                        .about-content li {{ font-size: 0.875rem !important; margin: 0.2rem 0 !important; line-height: 1.4 !important; }}
                        .about-content strong {{ font-weight: 600 !important; }}
                        </style>
                        <div class="about-content">
                        {app_info["concept"]}
                        </div>
                        """
                        )

            # Планы развития
            with ui.tab_panel("Планы развития"):
                with ui.scroll_area().classes("h-full w-full"):
                    with ui.column().classes("p-4"):
                        ui.html(
                            f"""
                        <style>
                        .about-content h1 {{ font-size: 1.5rem !important; font-weight: 700 !important; margin: 1rem 0 0.5rem 0 !important; color: #1f2937 !important; }}
                        .about-content h2 {{ font-size: 1.3rem !important; font-weight: 600 !important; margin: 0.8rem 0 0.4rem 0 !important; color: #374151 !important; }}
                        .about-content h3 {{ font-size: 1.1rem !important; font-weight: 600 !important; margin: 0.6rem 0 0.3rem 0 !important; color: #4b5563 !important; }}
                        .about-content p {{ font-size: 0.875rem !important; margin: 0.3rem 0 !important; line-height: 1.5 !important; }}
                        .about-content ul {{ font-size: 0.875rem !important; margin: 0.3rem 0 !important; }}
                        .about-content li {{ font-size: 0.875rem !important; margin: 0.2rem 0 !important; line-height: 1.4 !important; }}
                        .about-content strong {{ font-weight: 600 !important; }}
                        </style>
                        <div class="about-content">
                        {app_info["tasks"]}
                        </div>
                        """
                        )

        # Кнопки внизу
        with ui.row().classes("justify-between items-center p-3 bg-gray-50 border-t"):
            ui.label("💡 Совет: Используйте колесо мыши для прокрутки").classes(
                "text-xs text-gray-600"
            )
            with ui.row().classes("gap-2"):
                ui.button("Назад", icon="arrow_back").classes("px-4 py-1 text-sm").on(
                    "click", lambda: ui.navigate.to("/")
                )


def portfolio_page():
    # Импортируем модуль версий
    from app.core.version import get_app_info

    # Заголовок с иконкой и версией
    with ui.row().classes("items-center justify-between mb-6"):
        with ui.row().classes("items-center gap-3"):
            ui.icon("account_balance_wallet").classes("text-3xl text-blue-600")
            ui.label("Crypto Portfolio Manager").classes(
                "text-3xl font-bold text-gray-800"
            )
            ui.badge(f"v{get_app_info()['version']}", color="blue").classes("text-sm")

        # Кнопки управления
        with ui.row().classes("gap-2"):
            refresh_button = (
                ui.button("🔄 Обновить данные", icon="refresh")
                .classes("bg-green-100 text-green-700 hover:bg-green-200")
                .on("click", lambda: refresh())
            )

            ui.button("О программе", icon="info").classes(
                "bg-blue-100 text-blue-700 hover:bg-blue-200"
            ).on("click", lambda: ui.navigate.to("/about"))

    # Карточка с фильтрами
    with ui.card().classes("p-4 mb-6 bg-gradient-to-r from-blue-50 to-indigo-50"):
        ui.label("Фильтры").classes("text-lg font-semibold mb-3 text-gray-700")
        with ui.row().classes("gap-4 items-end"):
            with ui.column().classes("gap-1"):
                ui.label("Монета").classes("text-sm font-medium text-gray-600")
                coin_filter = (
                    ui.input(placeholder="BTC, ETH, SOL...")
                    .props(
                        "uppercase autocomplete=off autocorrect=off autocapitalize=off spellcheck=false"
                    )
                    .classes("w-48")
                )

            with ui.column().classes("gap-1"):
                ui.label("Стратегия").classes("text-sm font-medium text-gray-600")
                strat_filter = ui.select(["(все)"] + STRATS, value="(все)").classes(
                    "w-32"
                )

        def reset_filters():
            coin_filter.value = ""
            strat_filter.value = "(все)"
            refresh()

            ui.button("Сбросить", on_click=reset_filters).props("outline").classes(
                "px-4 py-2"
            )

    # Вкладки с иконками
    tabs = ui.tabs().classes("mb-4")
    with tabs:
        ui.tab("overview", "📊 Обзор")
        ui.tab("positions", "💼 Позиции")
        ui.tab("transactions", "📝 Сделки")
        ui.tab("alerts", "🔔 Алерты")
        ui.tab("analytics", "📈 Аналитика")

    with ui.tab_panels(tabs, value="overview").classes("w-full"):
        with ui.tab_panel("overview"):
            # Заголовок вкладки
            with ui.row().classes("items-center gap-2 mb-4"):
                ui.icon("dashboard").classes("text-xl text-blue-600")
                ui.label("Обзор портфеля").classes("text-xl font-bold text-gray-800")

            # Карточки со сводкой
            with ui.row().classes("gap-4 mb-6"):
                with ui.card().classes(
                    "p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500"
                ):
                    with ui.column().classes("gap-1"):
                        ui.label("Общая стоимость").classes(
                            "text-sm font-medium text-gray-600"
                        )
                        total_value_chip = ui.label("—").classes(
                            "text-2xl font-bold text-green-700"
                        )

                with ui.card().classes(
                    "p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border-l-4 border-blue-500"
                ):
                    with ui.column().classes("gap-1"):
                        ui.label("Нереализованный PnL").classes(
                            "text-sm font-medium text-gray-600"
                        )
                        total_unreal_chip = ui.label("—").classes("text-2xl font-bold")

                with ui.card().classes(
                    "p-4 bg-gradient-to-r from-purple-50 to-violet-50 border-l-4 border-purple-500"
                ):
                    with ui.column().classes("gap-1"):
                        ui.label("Реализованный PnL").classes(
                            "text-sm font-medium text-gray-600"
                        )
                        total_real_chip = ui.label("—").classes("text-2xl font-bold")

            # Дополнительная аналитика
            with ui.grid(columns=3).classes("gap-4 mb-6"):
                # Статистика по монетам
                with ui.card().classes(
                    "p-4 bg-gradient-to-r from-orange-50 to-red-50 border-l-4 border-orange-500"
                ):
                    with ui.column().classes("gap-2"):
                        ui.label("📊 Статистика").classes(
                            "text-sm font-medium text-gray-600"
                        )
                        coins_count_chip = ui.label("—").classes(
                            "text-lg font-bold text-orange-700"
                        )
                        positions_count_chip = ui.label("—").classes(
                            "text-sm text-gray-600"
                        )

                # Топ монета
                with ui.card().classes(
                    "p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-l-4 border-indigo-500"
                ):
                    with ui.column().classes("gap-2"):
                        ui.label("🏆 Топ позиция").classes(
                            "text-sm font-medium text-gray-600"
                        )
                        top_coin_chip = ui.label("—").classes(
                            "text-lg font-bold text-indigo-700"
                        )
                        top_pnl_chip = ui.label("—").classes("text-sm text-gray-600")

                # Активность
                with ui.card().classes(
                    "p-4 bg-gradient-to-r from-teal-50 to-cyan-50 border-l-4 border-teal-500"
                ):
                    with ui.column().classes("gap-2"):
                        ui.label("⚡ Активность").classes(
                            "text-sm font-medium text-gray-600"
                        )
                        transactions_count_chip = ui.label("—").classes(
                            "text-lg font-bold text-teal-700"
                        )
                        strategies_count_chip = ui.label("—").classes(
                            "text-sm text-gray-600"
                        )

            # Детальная аналитика
            with ui.grid(columns=2).classes("gap-6 mb-6"):
                # Статистика по монетам
                with ui.card().classes("p-4"):
                    with ui.row().classes("items-center gap-2 mb-3"):
                        ui.icon("currency_exchange").classes("text-lg text-blue-600")
                        ui.label("Распределение по монетам").classes(
                            "text-lg font-semibold text-gray-700"
                        )
                    coins_table = (
                        ui.table(
                            columns=[
                                {
                                    "name": "coin",
                                    "label": "Монета",
                                    "field": "coin",
                                    "align": "left",
                                },
                                {
                                    "name": "value",
                                    "label": "Стоимость",
                                    "field": "value",
                                    "align": "right",
                                    "format": "currency",
                                },
                                {
                                    "name": "pnl",
                                    "label": "PnL",
                                    "field": "pnl",
                                    "align": "right",
                                    "format": "currency",
                                },
                                {
                                    "name": "count",
                                    "label": "Позиций",
                                    "field": "count",
                                    "align": "center",
                                },
                            ],
                            rows=[],
                            row_key="coin",
                        )
                        .classes("w-full")
                        .props("dense bordered")
                    )

                # Статистика по стратегиям
                with ui.card().classes("p-4"):
                    with ui.row().classes("items-center gap-2 mb-3"):
                        ui.icon("trending_up").classes("text-lg text-green-600")
                        ui.label("Распределение по стратегиям").classes(
                            "text-lg font-semibold text-gray-700"
                        )
                    strategies_table = (
                        ui.table(
                            columns=[
                                {
                                    "name": "strategy",
                                    "label": "Стратегия",
                                    "field": "strategy",
                                    "align": "left",
                                },
                                {
                                    "name": "value",
                                    "label": "Стоимость",
                                    "field": "value",
                                    "align": "right",
                                    "format": "currency",
                                },
                                {
                                    "name": "pnl",
                                    "label": "PnL",
                                    "field": "pnl",
                                    "align": "right",
                                    "format": "currency",
                                },
                                {
                                    "name": "count",
                                    "label": "Позиций",
                                    "field": "count",
                                    "align": "center",
                                },
                            ],
                            rows=[],
                            row_key="strategy",
                        )
                        .classes("w-full")
                        .props("dense bordered")
                    )

            # Заголовок таблицы позиций
            with ui.row().classes("items-center gap-2 mb-3"):
                ui.icon("table_chart").classes("text-lg text-gray-600")
                ui.label("Все позиции (FIFO, цены CoinGecko)").classes(
                    "text-lg font-semibold text-gray-700"
                )
            pos_cols = [
                {
                    "name": "coin",
                    "label": "💰 Монета",
                    "field": "coin",
                    "align": "left",
                },
                {
                    "name": "strategy",
                    "label": "🎯 Стратегия",
                    "field": "strategy",
                    "align": "center",
                },
                {
                    "name": "quantity",
                    "label": "📊 Количество",
                    "field": "quantity",
                    "align": "right",
                    "format": "number",
                },
                {
                    "name": "avg_cost",
                    "label": "💵 Средняя цена",
                    "field": "avg_cost",
                    "align": "right",
                    "format": "currency",
                },
                {
                    "name": "price",
                    "label": f"📈 Цена ({CURRENCY})",
                    "field": "price",
                    "align": "right",
                    "format": "currency",
                },
                {
                    "name": "value",
                    "label": "💎 Стоимость",
                    "field": "value",
                    "align": "right",
                    "format": "currency",
                },
                {
                    "name": "unreal_pnl",
                    "label": "📊 Нереализ. PnL",
                    "field": "unreal_pnl",
                    "align": "right",
                    "format": "currency",
                },
                {
                    "name": "unreal_pct",
                    "label": "📈 Нереализ. %",
                    "field": "unreal_pct",
                    "align": "right",
                    "format": "percentage",
                },
                {
                    "name": "realized",
                    "label": "💰 Реализ. PnL",
                    "field": "realized",
                    "align": "right",
                    "format": "currency",
                },
            ]
            pos_table1 = (
                ui.table(columns=pos_cols, rows=[], row_key="key")
                .classes("w-full mt-2")
                .props("dense bordered")
            )

        with ui.tab_panel("positions"):
            # Заголовок вкладки
            with ui.row().classes("items-center justify-between mb-4"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("account_balance").classes("text-xl text-blue-600")
                    ui.label("Позиции").classes("text-xl font-bold text-gray-800")

                with ui.row().classes("gap-2"):
                    ui.button("📥 Экспорт CSV", on_click=lambda: export_pos()).props(
                        "color=primary icon=download"
                    ).classes("px-4 py-2")
                    ui.button("🔄 Обновить", on_click=lambda: refresh()).props(
                        "outline icon=refresh"
                    ).classes("px-4 py-2")

            pos_table2 = (
                ui.table(columns=pos_cols, rows=[], row_key="key")
                .classes("w-full")
                .props("dense bordered")
            )

        with ui.tab_panel("transactions"):
            # Заголовок вкладки
            with ui.row().classes("items-center justify-between mb-4"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("receipt_long").classes("text-xl text-blue-600")
                    ui.label("Сделки").classes("text-xl font-bold text-gray-800")

                ui.button("📥 Экспорт CSV", on_click=lambda: export_tx()).props(
                    "color=primary icon=download"
                ).classes("px-4 py-2")

            # Улучшенная форма добавления сделки
            with ui.card().classes(
                "w-full mb-6 p-6 bg-gradient-to-r from-blue-50 to-indigo-50"
            ):
                with ui.row().classes("items-center gap-2 mb-4"):
                    ui.icon("add_circle").classes("text-lg text-blue-600")
                    ui.label("Добавить новую сделку").classes(
                        "text-lg font-semibold text-gray-800"
                    )
                    ui.badge("Быстрый ввод", color="blue").classes("ml-auto")

                # Функции для быстрых действий (определяем ДО использования)
                def set_coin_value(coin_symbol):
                    coin.value = coin_symbol
                    # NiceGUI не поддерживает focus() для Input

                def set_source_value(exchange_name):
                    source.value = exchange_name
                    # NiceGUI не поддерживает focus() для Input

                def get_current_price():
                    if not coin.value or not coin.value.strip():
                        ui.notify("❌ Сначала введите символ монеты", type="negative")
                        return

                    try:
                        from app.adapters.prices import get_aggregated_price

                        coin_symbol = coin.value.upper().strip()

                        # Получаем агрегированную цену из нескольких источников
                        ui.notify(
                            f"🔄 Собираем цены {coin_symbol} из нескольких источников...",
                            type="info",
                        )

                        price_data = get_aggregated_price(coin_symbol)

                        if price_data and price_data["price"]:
                            current_price = price_data["price"]
                            price.value = str(current_price)

                            # Формируем детальное сообщение
                            sources = price_data["sources"]
                            source_count = price_data["source_count"]

                            message = (
                                f"✅ Средняя цена {coin_symbol}: ${current_price:,.2f}"
                            )

                            # Добавляем информацию об источниках
                            if source_count > 1:
                                message += f" (из {source_count} источников: {', '.join(sources)})"
                            else:
                                message += f" (источник: {sources[0]})"

                            # Добавляем информацию о разбросе цен
                            if "price_range" in price_data:
                                price_range = price_data["price_range"]
                                spread = price_range["spread"]
                                if spread > 0:
                                    spread_percent = (spread / current_price) * 100
                                    message += f" [разброс: ${spread:.2f} ({spread_percent:.1f}%)]"

                            # Добавляем информацию о кэше
                            if price_data.get("cached"):
                                message += " (из кэша)"
                            else:
                                message += " (актуально)"

                            ui.notify(message, type="positive")
                        else:
                            ui.notify(
                                f"❌ Не удалось получить цену для {coin_symbol}. Проверьте правильность символа.",
                                type="negative",
                            )
                    except Exception as e:
                        ui.notify(f"❌ Ошибка получения цены: {e}", type="negative")

                def clear_form():
                    coin.value = ""
                    qty.value = ""
                    price.value = ""
                    source.value = ""
                    notes.value = ""
                    ttype.value = "buy"
                    strategy.value = "long"
                    # coin.focus()  # NiceGUI не поддерживает focus()

                def save_draft():
                    # Сохраняем в localStorage браузера
                    ui.notify("💾 Черновик сохранен", type="info")

                def on_add():
                    # Валидация полей
                    if not coin.value or not coin.value.strip():
                        ui.notify("❌ Введите символ монеты", type="negative")
                        # coin.focus()  # NiceGUI не поддерживает focus()
                        return

                    if not qty.value or float(qty.value or 0) <= 0:
                        ui.notify("❌ Введите корректное количество", type="negative")
                        # qty.focus()  # NiceGUI не поддерживает focus()
                        return

                    if not price.value or float(price.value or 0) <= 0:
                        ui.notify("❌ Введите корректную цену", type="negative")
                        # price.focus()  # NiceGUI не поддерживает focus()
                        return

                    try:
                        data = TransactionIn(
                            coin=(coin.value or "").upper().strip(),
                            type=ttype.value,
                            quantity=float(qty.value or 0),
                            price=float(price.value or 0),
                            strategy=strategy.value,
                            source=(source.value or "").strip(),
                            notes=(notes.value or "").strip(),
                        )
                        add_transaction(data)
                        ui.notify("✅ Сделка успешно добавлена", type="positive")
                        clear_form()
                        refresh()

                        # Обновляем списки популярных монет и бирж
                        ui.notify(
                            "🔄 Списки популярных монет и бирж обновлены", type="info"
                        )
                    except Exception as e:
                        ui.notify(f"❌ Ошибка: {e}", type="negative")

                # Быстрые кнопки для популярных монет (включая историю торговли)
                with ui.row().classes("gap-2 mb-4"):
                    ui.label("Популярные монеты:").classes(
                        "text-sm text-gray-600 self-center"
                    )

                    # Получаем монеты из истории торговли
                    def get_trading_history_coins():
                        """Получает монеты из истории торговли, отсортированные по частоте использования"""
                        try:
                            transactions = list_transactions()
                            coin_counts = {}
                            for tx in transactions:
                                coin = tx.get("coin", "").upper()
                                if coin:
                                    coin_counts[coin] = coin_counts.get(coin, 0) + 1

                            # Сортируем по частоте использования (по убыванию)
                            sorted_coins = sorted(
                                coin_counts.items(), key=lambda x: x[1], reverse=True
                            )
                            return [coin for coin, count in sorted_coins]
                        except Exception:
                            return []

                    # Базовые популярные монеты
                    base_popular_coins = [
                        "BTC",
                        "ETH",
                        "SOL",
                        "ADA",
                        "DOT",
                        "LINK",
                        "UNI",
                        "MATIC",
                    ]

                    # Получаем монеты из истории торговли
                    history_coins = get_trading_history_coins()

                    # Объединяем и убираем дубликаты, приоритет у истории торговли
                    all_coins = []
                    seen = set()

                    # Сначала добавляем монеты из истории (максимум 6)
                    for coin in history_coins[:6]:
                        if coin not in seen:
                            all_coins.append(coin)
                            seen.add(coin)

                    # Затем добавляем базовые популярные монеты (максимум 4)
                    for coin in base_popular_coins:
                        if coin not in seen and len(all_coins) < 10:
                            all_coins.append(coin)
                            seen.add(coin)

                    # Создаем кнопки для монет
                    for coin_symbol in all_coins:
                        # Определяем стиль кнопки (история торговли vs базовые)
                        is_from_history = coin_symbol in history_coins[:6]
                        button_style = (
                            "size=sm outline" if not is_from_history else "size=sm"
                        )
                        button_class = (
                            "text-xs"
                            if not is_from_history
                            else "text-xs font-semibold"
                        )

                        # Добавляем иконку для монет из истории торговли
                        button_text = (
                            f"⭐ {coin_symbol}" if is_from_history else coin_symbol
                        )
                        tooltip_text = (
                            "Из истории торговли"
                            if is_from_history
                            else "Популярная монета"
                        )

                        ui.button(
                            button_text,
                            on_click=lambda c=coin_symbol: set_coin_value(c),
                        ).props(button_style).classes(button_class).tooltip(
                            tooltip_text
                        )

                    # Подсказки по горячим клавишам и кнопка обновления
                    with ui.row().classes(
                        "ml-auto gap-4 text-xs text-gray-500 items-center"
                    ):
                        ui.label("💡 Подсказки:")
                        ui.label("Enter = следующий")
                        ui.label("Ctrl+Enter = добавить")
                        ui.label("Esc = очистить")

                        # Кнопка обновления списков
                        ui.button(
                            "🔄 Обновить списки",
                            on_click=lambda: ui.notify(
                                "🔄 Списки обновлены", type="info"
                            ),
                        ).props("size=sm outline").classes("text-xs")

                with ui.grid(columns=2).classes("gap-4"):
                    # Левая колонка - основные поля
                    with ui.column().classes("gap-3"):
                        # Монета с автодополнением
                        with ui.column().classes("gap-1"):
                            ui.label("💰 Монета *").classes(
                                "text-sm font-medium text-gray-700"
                            )
                            coin = (
                                ui.input(placeholder="BTC, ETH, SOL...")
                                .props(
                                    "uppercase autocomplete=off autocorrect=off autocapitalize=off spellcheck=false"
                                )
                                .classes("w-full")
                                .on(
                                    "keydown.enter", lambda: None
                                )  # NiceGUI не поддерживает focus()
                                .on("keydown.escape", clear_form)
                                .on("keydown.ctrl+enter", on_add)
                            )
                            ui.label("Введите символ криптовалюты").classes(
                                "text-xs text-gray-500"
                            )

                        # Тип операции с иконками
                        with ui.column().classes("gap-1"):
                            ui.label("📊 Тип операции *").classes(
                                "text-sm font-medium text-gray-700"
                            )
                            ttype = ui.select(
                                TYPES, label="Выберите тип", value="buy"
                            ).classes("w-full")
                            ui.label("buy = покупка, sell = продажа").classes(
                                "text-xs text-gray-500"
                            )

                        # Количество с валидацией
                        with ui.column().classes("gap-1"):
                            ui.label("📈 Количество *").classes(
                                "text-sm font-medium text-gray-700"
                            )
                            qty = (
                                ui.input(placeholder="0.0")
                                .props(
                                    "type=number inputmode=decimal autocomplete=off step=0.00000001"
                                )
                                .classes("w-full")
                                .on(
                                    "keydown.enter", lambda: None
                                )  # NiceGUI не поддерживает focus()
                                .on("keydown.escape", clear_form)
                                .on("keydown.ctrl+enter", on_add)
                            )
                            ui.label("Количество монет для покупки/продажи").classes(
                                "text-xs text-gray-500"
                            )

                        # Цена с валидацией
                        with ui.column().classes("gap-1"):
                            with ui.row().classes("items-center gap-2"):
                                ui.label("💵 Цена за монету *").classes(
                                    "text-sm font-medium text-gray-700"
                                )
                                ui.button(
                                    "📊 Текущая цена", on_click=get_current_price
                                ).props("size=sm outline").classes("text-xs").tooltip(
                                    "Получить актуальную цену с CoinGecko API"
                                )
                            price = (
                                ui.input(placeholder="0.00")
                                .props(
                                    "type=number inputmode=decimal autocomplete=off step=0.01"
                                )
                                .classes("w-full")
                                .on(
                                    "keydown.enter", lambda: None
                                )  # NiceGUI не поддерживает focus()
                                .on("keydown.escape", clear_form)
                                .on("keydown.ctrl+enter", on_add)
                            )
                            ui.label(f"Цена в {CURRENCY}").classes(
                                "text-xs text-gray-500"
                            )

                    # Правая колонка - дополнительные поля
                    with ui.column().classes("gap-3"):
                        # Стратегия
                        with ui.column().classes("gap-1"):
                            ui.label("🎯 Стратегия").classes(
                                "text-sm font-medium text-gray-700"
                            )
                            strategy = ui.select(
                                STRATS, label="Выберите стратегию", value="long"
                            ).classes("w-full")
                            ui.label("long = долгосрочная, scalp = скальпинг").classes(
                                "text-xs text-gray-500"
                            )

                        # Источник
                        with ui.column().classes("gap-1"):
                            with ui.row().classes("items-center gap-2"):
                                ui.label("🏢 Источник").classes(
                                    "text-sm font-medium text-gray-700"
                                )
                                # Быстрые кнопки для популярных бирж (включая историю торговли)
                                with ui.row().classes("gap-1"):
                                    # Получаем биржи из истории торговли
                                    def get_trading_history_exchanges():
                                        """Получает биржи из истории торговли, отсортированные по частоте использования"""
                                        try:
                                            transactions = list_transactions()
                                            exchange_counts = {}
                                            for tx in transactions:
                                                source = tx.get("source", "").strip()
                                                if source:
                                                    exchange_counts[source] = (
                                                        exchange_counts.get(source, 0)
                                                        + 1
                                                    )

                                            # Сортируем по частоте использования (по убыванию)
                                            sorted_exchanges = sorted(
                                                exchange_counts.items(),
                                                key=lambda x: x[1],
                                                reverse=True,
                                            )
                                            return [
                                                exchange
                                                for exchange, count in sorted_exchanges
                                            ]
                                        except Exception:
                                            return []

                                    # Базовые популярные биржи
                                    base_popular_exchanges = [
                                        "Binance",
                                        "Coinbase",
                                        "Kraken",
                                        "KuCoin",
                                    ]

                                    # Получаем биржи из истории торговли
                                    history_exchanges = get_trading_history_exchanges()

                                    # Объединяем и убираем дубликаты, приоритет у истории торговли
                                    all_exchanges = []
                                    seen = set()

                                    # Сначала добавляем биржи из истории (максимум 4)
                                    for exchange in history_exchanges[:4]:
                                        if exchange not in seen:
                                            all_exchanges.append(exchange)
                                            seen.add(exchange)

                                    # Затем добавляем базовые популярные биржи (максимум 2)
                                    for exchange in base_popular_exchanges:
                                        if (
                                            exchange not in seen
                                            and len(all_exchanges) < 6
                                        ):
                                            all_exchanges.append(exchange)
                                            seen.add(exchange)

                                    # Создаем кнопки для бирж
                                    for exchange in all_exchanges:
                                        # Определяем стиль кнопки (история торговли vs базовые)
                                        is_from_history = (
                                            exchange in history_exchanges[:4]
                                        )
                                        button_style = (
                                            "size=sm outline"
                                            if not is_from_history
                                            else "size=sm"
                                        )
                                        button_class = (
                                            "text-xs"
                                            if not is_from_history
                                            else "text-xs font-semibold"
                                        )

                                        # Добавляем иконку для бирж из истории торговли
                                        button_text = (
                                            f"⭐ {exchange}"
                                            if is_from_history
                                            else exchange
                                        )
                                        tooltip_text = (
                                            "Из истории торговли"
                                            if is_from_history
                                            else "Популярная биржа"
                                        )

                                        ui.button(
                                            button_text,
                                            on_click=lambda e=exchange: set_source_value(
                                                e
                                            ),
                                        ).props(button_style).classes(
                                            button_class
                                        ).tooltip(
                                            tooltip_text
                                        )
                            source = (
                                ui.input(placeholder="Binance, Coinbase, Kraken...")
                                .props("autocomplete=off")
                                .classes("w-full")
                                .on(
                                    "keydown.enter", lambda: None
                                )  # NiceGUI не поддерживает focus()
                                .on("keydown.escape", clear_form)
                                .on("keydown.ctrl+enter", on_add)
                            )
                            ui.label("Биржа или платформа").classes(
                                "text-xs text-gray-500"
                            )

                        # Заметки
                        with ui.column().classes("gap-1"):
                            ui.label("📝 Заметки").classes(
                                "text-sm font-medium text-gray-700"
                            )
                            notes = (
                                ui.textarea(placeholder="Дополнительная информация...")
                                .classes("w-full")
                                .props("rows=3")
                                .on("keydown.escape", clear_form)
                                .on("keydown.ctrl+enter", on_add)
                            )
                            ui.label("Любая дополнительная информация").classes(
                                "text-xs text-gray-500"
                            )

                # Кнопки действий
                with ui.row().classes("justify-between items-center mt-4"):
                    with ui.row().classes("gap-2"):
                        ui.button("🧹 Очистить", on_click=clear_form).props(
                            "outline"
                        ).classes("px-4 py-2")
                        ui.button("💾 Сохранить черновик", on_click=save_draft).props(
                            "outline"
                        ).classes("px-4 py-2")

                    with ui.row().classes("gap-2"):
                        ui.button("❌ Отмена", on_click=clear_form).props(
                            "outline"
                        ).classes("px-4 py-2")
                        ui.button("✅ Добавить сделку", on_click=on_add).props(
                            "color=primary"
                        ).classes("px-6 py-2")

            # таблица сделок с экшенами
            cols = [
                {
                    "name": "id",
                    "label": "#",
                    "field": "id",
                    "align": "center",
                    "sortable": True,
                },
                {
                    "name": "coin",
                    "label": "💰 Монета",
                    "field": "coin",
                    "align": "left",
                },
                {"name": "type", "label": "📊 Тип", "field": "type", "align": "center"},
                {
                    "name": "quantity",
                    "label": "📈 Количество",
                    "field": "quantity",
                    "align": "right",
                    "format": "number",
                },
                {
                    "name": "price",
                    "label": "💵 Цена",
                    "field": "price",
                    "align": "right",
                    "format": "currency",
                },
                {
                    "name": "ts_local",
                    "label": "📅 Дата/время",
                    "field": "ts_local",
                    "align": "center",
                },
                {
                    "name": "strategy",
                    "label": "🎯 Стратегия",
                    "field": "strategy",
                    "align": "center",
                },
                {
                    "name": "source",
                    "label": "🏢 Источник",
                    "field": "source",
                    "align": "left",
                },
                {
                    "name": "notes",
                    "label": "📝 Заметки",
                    "field": "notes",
                    "align": "left",
                },
                {
                    "name": "actions",
                    "label": "⚙️ Действия",
                    "field": "actions",
                    "align": "center",
                },
            ]
            tx_table = (
                ui.table(columns=cols, rows=[], row_key="id")
                .classes("w-full")
                .props("dense bordered")
            )

            # Используем строковый template для actions колонки
            tx_table.add_slot(
                "body-cell-actions",
                """
                <q-td :props="props" auto-width>
                    <q-btn flat size="sm" icon="edit" color="primary" @click="$parent.$emit('edit', props.row)" />
                    <q-btn flat size="sm" icon="delete" color="negative" @click="$parent.$emit('delete', props.row)" />
                </q-td>
            """,
            )

            # Добавляем обработчики событий
            def handle_edit(e):
                open_edit_dialog(e.args, refresh)

            def handle_delete(e):
                delete_transaction(int(e.args["id"]))
                ui.notify("✅ Сделка удалена", type="positive")
                refresh()

            tx_table.on("edit", handle_edit)
            tx_table.on("delete", handle_delete)

        with ui.tab_panel("alerts"):
            # Заголовок вкладки
            with ui.row().classes("items-center gap-2 mb-4"):
                ui.icon("notifications").classes("text-xl text-blue-600")
                ui.label("Алерты").classes("text-xl font-bold text-gray-800")

            # Заглушка для будущей функциональности
            with ui.card().classes(
                "p-8 text-center bg-gradient-to-r from-yellow-50 to-orange-50"
            ):
                ui.icon("construction").classes("text-4xl text-yellow-600 mb-4")
                ui.label("Функция в разработке").classes(
                    "text-xl font-semibold text-gray-700 mb-2"
                )
                ui.label(
                    "Здесь будут настройки уведомлений о изменениях цен и PnL"
                ).classes("text-gray-600")

        with ui.tab_panel("analytics"):
            # Заголовок вкладки
            with ui.row().classes("items-center gap-2 mb-4"):
                ui.icon("analytics").classes("text-xl text-blue-600")
                ui.label("Аналитика").classes("text-xl font-bold text-gray-800")

            # Заглушка для будущей функциональности
            with ui.card().classes(
                "p-8 text-center bg-gradient-to-r from-purple-50 to-pink-50"
            ):
                ui.icon("show_chart").classes("text-4xl text-purple-600 mb-4")
                ui.label("Функция в разработке").classes(
                    "text-xl font-semibold text-gray-700 mb-2"
                )
                ui.label(
                    "Здесь будут графики стоимости портфеля и детальная аналитика"
                ).classes("text-gray-600")

    # Экспорт-helpers
    def export_tx():
        try:
            path = export_transactions_csv()
            ui.notify(f"✅ Экспорт сделок завершен: {path}", type="positive")
        except Exception as e:
            ui.notify(f"❌ Ошибка экспорта: {e}", type="negative")

    def export_pos():
        try:
            base = positions_fifo()
            base = apply_filters_positions(base, coin_filter.value, strat_filter.value)
            enriched, _ = enrich_positions_with_market(base, quote=CURRENCY)
            path = export_positions_csv(enriched)
            ui.notify(f"✅ Экспорт позиций завершен: {path}", type="positive")
        except Exception as e:
            ui.notify(f"❌ Ошибка экспорта: {e}", type="negative")

    # Применение фильтров
    def apply_filters_tx(rows, coin_val, strat_val):
        coin_val = (coin_val or "").upper().strip()
        filtered = []
        for r in rows:
            if coin_val and r["coin"] != coin_val:
                continue
            if strat_val != "(все)" and r["strategy"] != strat_val:
                continue
            filtered.append(r)
        return filtered

    def apply_filters_positions(rows, coin_val, strat_val):
        coin_val = (coin_val or "").upper().strip()
        out = []
        for r in rows:
            if coin_val and r["coin"] != coin_val:
                continue
            if strat_val != "(все)" and r["strategy"] != strat_val:
                continue
            out.append(r)
        return out

    # Обновление всех блоков
    def refresh():
        # Показываем индикатор загрузки
        refresh_button.props("loading")
        refresh_button.text = "🔄 Обновление..."

        try:
            # позиции для обзора и вкладки «позиции»
            base_positions = positions_fifo()
            base_filtered = apply_filters_positions(
                base_positions, coin_filter.value, strat_filter.value
            )
            enriched, totals = enrich_positions_with_market(
                base_filtered, quote=CURRENCY
            )
            pos_table1.rows = enriched
            pos_table1.update()
            pos_table2.rows = enriched
            pos_table2.update()

            # сводка с форматированием
            total_value_chip.text = f'{totals["total_value"]:,.2f} {CURRENCY}'

            # Нереализованный PnL с цветом
            unreal_value = totals["total_unreal"]
            unreal_pct = totals["total_unreal_pct"]
            total_unreal_chip.text = (
                f"{unreal_value:+,.2f} {CURRENCY} ({unreal_pct:+.2f}%)"
            )
            # Обновляем стили через props
            total_unreal_chip._props["class"] = (
                f"text-2xl font-bold {get_pnl_color(unreal_value)}"
            )

            # Реализованный PnL с цветом
            realized_value = totals["total_realized"]
            total_real_chip.text = f"{realized_value:+,.2f} {CURRENCY}"
            # Обновляем стили через props
            total_real_chip._props["class"] = (
                f"text-2xl font-bold {get_pnl_color(realized_value)}"
            )

            # Дополнительная аналитика
            portfolio_stats = get_portfolio_stats()
            transaction_stats = get_transaction_stats()

            # Статистика
            coins_count_chip.text = f'{portfolio_stats["summary"]["total_coins"]} монет'
            positions_count_chip.text = (
                f'{portfolio_stats["summary"]["total_positions"]} позиций'
            )

            # Топ позиция
            if portfolio_stats["top_positions"]:
                top_pos = portfolio_stats["top_positions"][0]
                top_coin_chip.text = f'{top_pos["coin"]} ({top_pos["strategy"]})'
                top_pnl = top_pos["unreal_pnl"] + top_pos["realized"]
                top_pnl_chip.text = f"{top_pnl:+,.2f} {CURRENCY}"
            else:
                top_coin_chip.text = "Нет данных"
                top_pnl_chip.text = "—"

            # Активность
            transactions_count_chip.text = (
                f'{transaction_stats["total_transactions"]} сделок'
            )
            strategies_count_chip.text = (
                f'{portfolio_stats["summary"]["total_strategies"]} стратегий'
            )

            # Таблицы аналитики
            coins_data = []
            for coin, stats in portfolio_stats["coin_stats"].items():
                coins_data.append(
                    {
                        "coin": coin,
                        "value": stats["total_value"],
                        "pnl": stats["total_pnl"],
                        "count": stats["positions_count"],
                    }
                )
            coins_table.rows = sorted(
                coins_data, key=lambda x: x["value"], reverse=True
            )
            coins_table.update()

            strategies_data = []
            for strategy, stats in portfolio_stats["strategy_stats"].items():
                strategies_data.append(
                    {
                        "strategy": strategy,
                        "value": stats["total_value"],
                        "pnl": stats["total_pnl"],
                        "count": stats["positions_count"],
                    }
                )
            strategies_table.rows = sorted(
                strategies_data, key=lambda x: x["value"], reverse=True
            )
            strategies_table.update()

            # сделки
            rows = list_transactions()
            rows = apply_filters_tx(rows, coin_filter.value, strat_filter.value)
            tx_table.rows = rows
            tx_table.update()

        except Exception as e:
            ui.notify(f"❌ Ошибка обновления данных: {e}", type="negative")
        finally:
            # Восстанавливаем кнопку
            refresh_button.props(remove="loading")
            refresh_button.text = "🔄 Обновить данные"

    # Загружаем данные при инициализации страницы
    refresh()  # Загружаем данные при открытии страницы
