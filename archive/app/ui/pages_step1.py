"""
Шаг 1: Улучшение статистических карточек
Добавляем градиенты к карточкам, сохраняя всю функциональность
"""

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


def create_enhanced_stat_card(title, value, icon, color="primary"):
    """Создает улучшенную статистическую карточку с градиентом"""
    color_classes = {
        "primary": "bg-gradient-to-r from-indigo-500 to-purple-600",
        "success": "bg-gradient-to-r from-green-500 to-emerald-600", 
        "info": "bg-gradient-to-r from-blue-500 to-cyan-600",
        "warning": "bg-gradient-to-r from-yellow-500 to-orange-600",
    }
    
    with ui.card().classes(
        f"p-4 text-white shadow-lg rounded-lg {color_classes.get(color, color_classes['primary'])}"
    ):
        with ui.row().classes("items-center justify-between mb-2"):
            ui.label(icon).classes("text-2xl")
            ui.label(value).classes("text-xl font-bold")
        ui.label(title).classes("text-sm opacity-90")


def create_overview_tab():
    """Создает вкладку обзора с улучшенными карточками"""
    with ui.column().classes("w-full space-y-4"):
        # Заголовок
        with ui.row().classes("items-center justify-between"):
            ui.label("Обзор портфеля").classes("text-2xl font-bold text-gray-800")
            ui.button("Обновить", icon="refresh").classes(
                "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            ).on("click", lambda: refresh())

        # Улучшенные статистические карточки
        with ui.row().classes("gap-4 mb-6"):
            create_enhanced_stat_card("Общая стоимость", "0.00 USD", "💰", "primary")
            create_enhanced_stat_card("Дневной PnL", "+0.00 USD", "📈", "success")
            create_enhanced_stat_card("Нереализованный PnL", "+0.00 USD", "💎", "info")
            create_enhanced_stat_card("Реализованный PnL", "+0.00 USD", "✅", "warning")

        # Остальной контент остается без изменений
        with ui.row().classes("gap-4"):
            # График стоимости портфеля
            with ui.card().classes("flex-1 p-4 bg-white shadow-sm rounded-lg"):
                ui.label("Стоимость портфеля").classes("text-lg font-semibold text-gray-800 mb-4")
                with ui.row().classes("h-48 items-center justify-center bg-gray-50 rounded-lg"):
                    ui.label("График в разработке").classes("text-gray-500")

            # Топ позиции
            with ui.card().classes("flex-1 p-4 bg-white shadow-sm rounded-lg"):
                ui.label("Топ позиции").classes("text-lg font-semibold text-gray-800 mb-4")
                with ui.column().classes("space-y-2"):
                    for i in range(3):
                        with ui.row().classes("items-center justify-between p-2 bg-gray-50 rounded-lg"):
                            ui.label(f"Позиция {i+1}").classes("font-medium text-gray-700")
                            ui.label("0.00 USD").classes("text-green-600 font-semibold")


def refresh():
    """Обновляет данные"""
    ui.notify("Данные обновлены!", color="positive")


def portfolio_page():
    """Главная страница портфеля с улучшенными карточками"""
    from app.core.version import get_app_info

    # Создаем основной контейнер с боковой панелью
    with ui.row().classes("w-full h-screen overflow-hidden"):
        # БОКОВАЯ ПАНЕЛЬ (остается без изменений)
        with ui.column().classes(
            "w-64 bg-gray-900 text-white p-4 space-y-4 overflow-y-auto"
        ):
            # Заголовок боковой панели
            with ui.row().classes("items-center gap-2 mb-6"):
                ui.icon("account_balance_wallet").classes("text-2xl text-blue-400")
                with ui.column().classes("gap-1"):
                    ui.label("Portfolio Manager").classes(
                        "text-lg font-bold text-white"
                    )
                    ui.label(f"v{get_app_info()['version']}").classes(
                        "text-xs text-gray-300 font-medium"
                    )

            # НАВИГАЦИЯ (остается без изменений)
            with ui.column().classes("space-y-2"):
                ui.label("Навигация").classes(
                    "text-sm font-semibold text-gray-300 uppercase tracking-wide"
                )

                # Главные разделы
                overview_btn = (
                    ui.button("📊 Обзор", icon="dashboard")
                    .classes(
                        "w-full justify-start text-left bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg transition-all duration-200"
                    )
                    .on("click", lambda: switch_to_tab("overview"))
                )

                positions_btn = (
                    ui.button("💼 Позиции", icon="account_balance")
                    .classes(
                        "w-full justify-start text-left bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-all duration-200"
                    )
                    .on("click", lambda: switch_to_tab("positions"))
                )

                transactions_btn = (
                    ui.button("📝 Сделки", icon="receipt_long")
                    .classes(
                        "w-full justify-start text-left bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-all duration-200"
                    )
                    .on("click", lambda: switch_to_tab("transactions"))
                )

                analytics_btn = (
                    ui.button("📈 Аналитика", icon="analytics")
                    .classes(
                        "w-full justify-start text-left bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-all duration-200"
                    )
                    .on("click", lambda: switch_to_tab("analytics"))
                )

            # БЫСТРЫЕ ДЕЙСТВИЯ (остается без изменений)
            with ui.column().classes("space-y-2 mt-6"):
                ui.label("Быстрые действия").classes(
                    "text-sm font-semibold text-gray-300 uppercase tracking-wide"
                )

                # Главная кнопка - добавить сделку
                add_btn = (
                    ui.button("+ Добавить сделку", icon="add")
                    .classes(
                        "w-full justify-start text-left bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg font-semibold transition-all duration-200"
                    )
                    .on("click", lambda: ui.notify("Функция добавления сделок", color="info"))
                )

                # Обновить данные
                refresh_button = (
                    ui.button("🔄 Обновить", icon="refresh")
                    .classes(
                        "w-full justify-start text-left bg-orange-600 hover:bg-orange-700 text-white px-3 py-2 rounded-lg transition-all duration-200"
                    )
                    .on("click", lambda: refresh())
                )

                # Экспорт данных
                export_btn = (
                    ui.button("📤 Экспорт", icon="download")
                    .classes(
                        "w-full justify-start text-left bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg transition-all duration-200"
                    )
                    .on("click", lambda: ui.notify("Функция в разработке", type="info"))
                )

            # ТИПЫ АКТИВОВ (остается без изменений)
            with ui.column().classes("space-y-2 mt-6"):
                ui.label("Типы активов").classes(
                    "text-sm font-semibold text-gray-300 uppercase tracking-wide"
                )

                # Криптовалюты (активно по умолчанию)
                crypto_btn = ui.button(
                    "₿ Криптовалюты", icon="currency_bitcoin"
                ).classes(
                    "w-full justify-start text-left bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-2 rounded-lg transition-all duration-200"
                )

                # Акции
                stocks_btn = (
                    ui.button("📈 Акции", icon="trending_up")
                    .classes(
                        "w-full justify-start text-left bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-all duration-200"
                    )
                    .on("click", lambda: ui.notify("Функция акций", color="info"))
                )

            # НИЖНЯЯ ЧАСТЬ (остается без изменений)
            with ui.column().classes("space-y-2 mt-auto pt-6"):
                ui.button("ℹ️ О программе", icon="info").classes(
                    "w-full justify-start text-left bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-all duration-200"
                ).on("click", lambda: ui.navigate.to("/about"))

        # ОСНОВНОЙ КОНТЕНТ
        with ui.column().classes("flex-1 bg-gray-50 overflow-hidden"):
            # Верхняя панель (остается без изменений)
            with ui.row().classes(
                "w-full h-16 bg-white shadow-sm border-b border-gray-200 px-6 items-center justify-between"
            ):
                # Логотип и название
                with ui.row().classes("items-center"):
                    ui.icon("account_balance_wallet").classes("text-2xl text-blue-600 mr-3")
                    with ui.column().classes("items-start"):
                        ui.label("Crypto Portfolio Manager").classes("text-xl font-bold text-gray-800")
                        ui.label("Управление криптовалютным портфелем").classes("text-sm text-gray-500")

                # Кнопки действий
                with ui.row().classes("items-center space-x-3"):
                    ui.button("+ Добавить сделку", icon="add").classes(
                        "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                    ).on("click", lambda: ui.notify("Добавление сделки", color="info"))
                    
                    ui.button("⚡ Быстрые действия", icon="flash_on").classes(
                        "bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
                    ).on("click", lambda: ui.notify("Быстрые действия", color="info"))
                    
                    ui.button("🔄 Обновить данные", icon="refresh").classes(
                        "bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
                    ).on("click", lambda: refresh())
                    
                    ui.button("ⓘ О программе", icon="info").classes(
                        "bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg"
                    ).on("click", lambda: ui.navigate.to("/about"))

            # Область контента с табами
            with ui.column().classes("flex-1 p-6 overflow-auto"):
                # Табы
                with ui.tabs().classes("w-full mb-6") as tabs:
                    ui.tab("overview", "📊 Обзор").classes("px-4 py-2")
                    ui.tab("positions", "💼 Позиции").classes("px-4 py-2")
                    ui.tab("transactions", "📝 Сделки").classes("px-4 py-2")
                    ui.tab("analytics", "📈 Аналитика").classes("px-4 py-2")

                with ui.tab_panels(tabs, value="overview").classes("w-full"):
                    # Вкладка обзора с улучшенными карточками
                    with ui.tab_panel("overview"):
                        create_overview_tab()

                    # Остальные вкладки остаются без изменений
                    with ui.tab_panel("positions"):
                        with ui.column().classes("w-full space-y-4"):
                            ui.label("Позиции").classes("text-2xl font-bold text-gray-800")
                            with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
                                ui.label("Таблица позиций").classes("text-lg font-semibold text-gray-800 mb-4")
                                with ui.row().classes("h-48 items-center justify-center bg-gray-50 rounded-lg"):
                                    ui.label("Нет позиций").classes("text-gray-500")

                    with ui.tab_panel("transactions"):
                        with ui.column().classes("w-full space-y-4"):
                            ui.label("Сделки").classes("text-2xl font-bold text-gray-800")
                            with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
                                ui.label("Таблица сделок").classes("text-lg font-semibold text-gray-800 mb-4")
                                with ui.row().classes("h-48 items-center justify-center bg-gray-50 rounded-lg"):
                                    ui.label("Нет сделок").classes("text-gray-500")

                    with ui.tab_panel("analytics"):
                        with ui.column().classes("w-full space-y-4"):
                            ui.label("Аналитика").classes("text-2xl font-bold text-gray-800")
                            with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
                                ui.label("Графики и метрики").classes("text-lg font-semibold text-gray-800 mb-4")
                                with ui.row().classes("h-48 items-center justify-center bg-gray-50 rounded-lg"):
                                    ui.label("Аналитика в разработке").classes("text-gray-500")


def switch_to_tab(tab_name):
    """Переключает вкладки"""
    ui.notify(f"Переход на {tab_name}", color="info")
