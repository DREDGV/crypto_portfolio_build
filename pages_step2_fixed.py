"""
Шаг 2: Восстановление полного функционала ввода сделок
Добавляем автодополнение, кнопку "текущая цена" и все удобства
"""

import os

from nicegui import ui

from app.core.models import TransactionIn, PriceAlertIn
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
    get_sources_with_frequency,
    update_source_name,
    delete_source_from_transactions,
    get_source_statistics,
    # Алерты
    add_price_alert,
    get_price_alerts,
    update_price_alert,
    delete_price_alert,
    check_price_alerts,
    get_alert_statistics,
)
from app.core.taxonomy import TYPE_META, STRATEGY_META, iter_type_meta, iter_strategy_meta
from app.core.version import get_app_info

# Импорт модуля графиков (временно отключен)
# from app.ui.charts import (
#     create_portfolio_distribution_chart,
#     create_transactions_timeline_chart,
#     create_strategy_performance_chart,
#     create_source_activity_chart,
#     get_portfolio_summary,
# )

# Импорт мониторинга кэша
from app.ui.cache_monitor import create_cache_monitor_tab

# Импорт экспорта/импорта
from app.ui.export_import import create_export_import_tab

# Импорт аналитики
from app.ui.analytics_simple import create_analytics_tab
# from app.ui.advanced_analytics import create_advanced_analytics_tab

# Импорт уведомлений (временно отключено)
# from app.ui.notifications import create_notifications_tab

CURRENCY = os.getenv("REPORT_CURRENCY", "USD").upper()




# Цвета для PnL
def get_pnl_color(value):
    if value > 0:
        return "text-green-600"
    elif value < 0:
        return "text-red-600"
    else:
        return "text-gray-600"


def render_required_label(label_text: str, helper_text: str | None = None):
    """Рендерит заголовок обязательного поля с пометкой."""
    ui.html(
        f'<span class="text-sm font-medium text-gray-700">{label_text} '
        "<span class=\"text-red-500 font-semibold\">*</span></span>"
    )
    if helper_text:
        ui.label(helper_text).classes("text-xs text-red-500 font-medium")


def create_enhanced_stat_card(title, value, icon, color="primary"):
    """Создает улучшенную статистическую карточку с градиентом"""
    color_classes = {
        "primary": "bg-gradient-to-r from-indigo-500 to-purple-600",
        "success": "bg-gradient-to-r from-green-500 to-emerald-600", 
        "info": "bg-gradient-to-r from-blue-500 to-cyan-600",
        "warning": "bg-gradient-to-r from-yellow-500 to-orange-600",
    }
    
    with ui.card().classes(
        f"p-6 text-white shadow-xl rounded-xl border border-white/20 hover:shadow-2xl transition-all duration-300 {color_classes.get(color, color_classes['primary'])}"
    ):
        with ui.column().classes("text-center"):
            ui.label(icon).classes("text-4xl mb-3")
            ui.label(value).classes("text-2xl font-bold mb-2")
            ui.label(title).classes("text-sm opacity-90 font-medium")


def open_enhanced_add_dialog():
    """Простой диалог добавления сделки"""
    with ui.dialog() as dialog, ui.card().classes("min-w-[500px] max-w-[600px] p-6"):
        ui.label("Добавить новую сделку").classes("text-xl font-bold mb-4")
        
        # Простые поля формы
        coin = ui.input(label="Монета (например: BTC)", placeholder="BTC").classes("w-full mb-3")
        qty = ui.number(label="Количество", placeholder="0.0", format="%.8f").classes("w-full mb-3")
        price = ui.number(label="Цена за единицу", placeholder="0.0", format="%.2f").classes("w-full mb-3")
        source = ui.input(label="Источник (биржа)", placeholder="Binance").classes("w-full mb-3")
        
        # Простые селекты
        ttype = ui.select(
            options=["trade_buy", "trade_sell", "transfer_in", "transfer_out"],
            value="trade_buy",
            label="Тип операции"
        ).classes("w-full mb-3")
        
        strategy = ui.select(
            options=["long_term", "swing", "scalp", "arbitrage"],
            value="long_term", 
            label="Стратегия"
        ).classes("w-full mb-3")
        
        notes = ui.textarea(label="Заметки (необязательно)", placeholder="Дополнительная информация").classes("w-full mb-4")
        
        # Кнопки
        with ui.row().classes("gap-3 justify-end"):
            ui.button("Отмена").on("click", dialog.close)
            
            def on_add():
                try:
                    if not coin.value or not qty.value or not price.value or not source.value:
                        ui.notify("Заполните все обязательные поля", color="error")
                        return
                    
                    transaction_data = TransactionIn(
                        coin=coin.value.strip().upper(),
                        quantity=float(qty.value),
                        price=float(price.value),
                        type=ttype.value,
                        strategy=strategy.value,
                        source=source.value.strip(),
                        notes=notes.value.strip() if notes.value else None,
                    )
                    
                    result = add_transaction(transaction_data)
                    if result:
                        ui.notify("Сделка добавлена!", color="positive")
                        dialog.close()
                        ui.open("/")
                    else:
                        ui.notify("Ошибка добавления", color="error")
                        
                except Exception as e:
                    ui.notify(f"Ошибка: {e}", color="error")
            
            ui.button("Добавить", icon="add").classes("bg-green-500 text-white").on("click", on_add)
    
    dialog.open()


def create_compact_stat_card(title: str, value: str, subtitle: str, icon: str = "info"):
    """Компактная карточка для метрик обзора"""
    with ui.card().classes(
        "w-full p-4 bg-white shadow-sm rounded-lg border border-gray-200 hover:shadow-md transition-all duration-200"
    ):
        with ui.row().classes("items-center gap-3"):
            ui.icon(icon).classes("text-xl text-blue-500")
            with ui.column().classes("gap-1"):
                ui.label(title).classes("text-xs text-gray-500 uppercase tracking-wide")
                ui.label(value).classes("text-lg font-semibold text-gray-900")
                if subtitle:
                    ui.label(subtitle).classes("text-xs text-gray-500")


def portfolio_page():
    """Простая главная страница портфеля"""
    with ui.column().classes("w-full p-6"):
        ui.label("Crypto Portfolio Manager").classes("text-3xl font-bold mb-6")
        
        # Кнопка добавления сделки
        ui.button("+ Добавить сделку", icon="add").classes("bg-green-500 text-white px-6 py-3").on("click", lambda: open_enhanced_add_dialog())
        
        # Простая информация о портфеле
        with ui.card().classes("p-4 mt-4"):
            ui.label("Информация о портфеле").classes("text-lg font-semibold mb-2")
            try:
                stats = get_portfolio_stats()
                ui.label(f"Всего позиций: {stats.get('summary', {}).get('total_positions', 0)}")
                ui.label(f"Общая стоимость: ${stats.get('totals', {}).get('total_value', 0):.2f}")
            except Exception as e:
                ui.label(f"Ошибка загрузки данных: {e}")


@ui.page("/")
def main_page():
    """Главная страница с портфелем"""
    portfolio_page()
