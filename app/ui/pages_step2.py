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

# Импорт модуля графиков
from app.ui.charts import (
    create_portfolio_distribution_chart,
    create_transactions_timeline_chart,
    create_strategy_performance_chart,
    create_source_activity_chart,
    get_portfolio_summary,
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


def open_enhanced_add_dialog():
    """Открывает улучшенный диалог добавления криптовалютной сделки"""
    quick_buttons_container = None
    with ui.dialog() as dialog, ui.card().classes("min-w-[700px] max-w-[900px] p-6"):
        # Заголовок диалога
        with ui.row().classes("items-center gap-2 mb-6 pb-4 border-b border-gray-200"):
            ui.icon("add_circle").classes("text-2xl text-green-600")
            ui.label("Добавить новую сделку").classes("text-2xl font-bold text-gray-800")
            ui.badge("Быстрый ввод", color="green").classes("ml-auto")

        # Переменные для формы (будут определены позже)
        coin = None
        qty = None
        price = None
        source = None
        notes = None

        def set_coin_value(coin_symbol):
            """Устанавливает значение монеты"""
            coin.value = coin_symbol

        def set_source_value(exchange_name):
            """Устанавливает значение источника"""
            source.value = exchange_name

        def refresh_sources_list():
            """Обновляет список источников в выпадающем списке"""
            try:
                # Получаем обновленный список источников
                sources_with_freq = get_sources_with_frequency()
                all_sources = [source for source, freq in sources_with_freq]
                
                # Обновляем опции выпадающего списка
                source.options = all_sources
                
                # Обновляем кнопки быстрого выбора
                top_sources = [source for source, freq in sources_with_freq[:3]]
                update_quick_source_buttons(top_sources)
                
            except Exception as e:
                print(f"Ошибка обновления списка источников: {e}")

        def update_quick_source_buttons(top_sources):
            """Обновляет кнопки быстрого выбора источников"""
            try:
                if quick_buttons_container:
                    # Очищаем контейнер кнопок
                    quick_buttons_container.clear()
                    
                    # Добавляем новые кнопки
                    if top_sources:
                        ui.label("Популярные источники:").classes("text-xs text-blue-600 font-medium")
                        with quick_buttons_container:
                            for source_name in top_sources:
                                ui.button(
                                    source_name,
                                    on_click=lambda s=source_name: set_source_value(s),
                                ).props("size=sm outline").classes(
                                    "text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-2 py-1 rounded"
                                )
            except Exception as e:
                print(f"Ошибка обновления кнопок быстрого выбора: {e}")

        def edit_source_name(old_name, mgmt_dialog, refresh_func):
            """Редактирует название источника"""
            print(f"DEBUG: Открываем диалог редактирования для источника: {old_name}")
            with ui.dialog() as edit_dialog, ui.card().classes("p-6"):
                ui.label(f"Редактировать: {old_name}").classes("text-lg font-semibold mb-4")
                
                new_name_input = ui.input("Новое название", value=old_name).classes("w-full mb-4")
                
                def save_changes():
                    print("DEBUG: Начало функции save_changes()")
                    new_name = new_name_input.value.strip()
                    print(f"DEBUG: Новое название: '{new_name}'")
                    
                    if not new_name:
                        ui.notify("Название не может быть пустым", type="negative")
                        return
                    
                    if new_name == old_name:
                        ui.notify("Название не изменилось", type="info")
                        edit_dialog.close()
                        return
                    
                    print(f"DEBUG: Обновляем источник '{old_name}' -> '{new_name}'")
                    # Обновляем в базе данных
                    success = update_source_name(old_name, new_name)
                    print(f"DEBUG: Результат обновления: {success}")
                    
                    if success:
                        ui.notify(f"Источник переименован: {old_name} -> {new_name}", type="positive")
                        edit_dialog.close()
                        # Принудительно обновляем список
                        print("DEBUG: Вызываем refresh_func() после успешного сохранения")
                        refresh_func()
                        # Без принудительного перезагруза страницы: UI обновится через refresh_both()
                    else:
                        ui.notify("Ошибка переименования", type="negative")
                
                with ui.row().classes("justify-end gap-3"):
                    ui.button("Отмена", on_click=edit_dialog.close)
                    ui.button("Сохранить", on_click=save_changes).classes("bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg")
                
                edit_dialog.open()

        def delete_source(source_name, mgmt_dialog, refresh_func):
            """Удаляет источник"""
            with ui.dialog() as delete_dialog, ui.card().classes("p-6"):
                ui.label(f"Удалить источник '{source_name}'?").classes("text-lg font-semibold mb-4")
                ui.label("Это удалит источник из всех сделок.").classes("text-sm text-gray-600 mb-4")
                
                def confirm_delete():
                    success = delete_source_from_transactions(source_name)
                    if success:
                        ui.notify(f"Источник '{source_name}' удален", type="positive")
                        delete_dialog.close()
                        refresh_func()
                        # Без перезагрузки страницы
                    else:
                        ui.notify("Ошибка удаления", type="negative")
                
                with ui.row().classes("justify-end gap-3"):
                    ui.button("Отмена", on_click=delete_dialog.close)
                    ui.button("Удалить", on_click=confirm_delete)
                
                delete_dialog.open()

        def move_source_up(source_name, mgmt_dialog, refresh_func):
            """Перемещает источник вверх в списке"""
            from app.core.services import move_source_up as move_up
            success = move_up(source_name)
            if success:
                ui.notify(f"Источник '{source_name}' перемещен вверх", type="positive")
                refresh_func()
                # Без перезагрузки: список обновлен выше
            else:
                ui.notify(f"Не удалось переместить '{source_name}' вверх", type="negative")

        def move_source_down(source_name, mgmt_dialog, refresh_func):
            """Перемещает источник вниз в списке"""
            from app.core.services import move_source_down as move_down
            success = move_down(source_name)
            if success:
                ui.notify(f"Источник '{source_name}' перемещен вниз", type="positive")
                refresh_func()
                # Без перезагрузки: список обновлен выше
            else:
                ui.notify(f"Не удалось переместить '{source_name}' вниз", type="negative")

        def add_new_source(mgmt_dialog, refresh_func):
            """Добавляет новый источник"""
            with ui.dialog() as add_dialog, ui.card().classes("p-6"):
                ui.label("Добавить новый источник").classes("text-lg font-semibold mb-4")
                
                new_source_input = ui.input("Название источника").classes("w-full mb-4")
                
                def add_source():
                    source_name = new_source_input.value.strip()
                    if not source_name:
                        ui.notify("Название не может быть пустым", type="negative")
                        return
                    
                    ui.notify(f"Источник '{source_name}' готов к использованию", type="positive")
                    add_dialog.close()
                    refresh_func()
                
                with ui.row().classes("justify-end gap-3"):
                    ui.button("Отмена", on_click=add_dialog.close)
                    ui.button("Добавить", on_click=add_source)
                
                add_dialog.open()

        def open_sources_management_dialog():
            """Открывает диалог управления источниками"""
            mgmt_dialog = ui.dialog()
            sources_container = None
            
            def refresh_mgmt_sources_list():
                """Обновляет список источников в диалоге"""
                nonlocal sources_container
                if sources_container:
                    print("DEBUG: Обновляем список источников...")
                    # Получаем обновленные источники
                    sources_with_freq = get_sources_with_frequency()
                    print(f"DEBUG: Получено {len(sources_with_freq)} источников: {sources_with_freq}")
                    
                    # Очищаем контейнер и пересоздаем содержимое
                    sources_container.clear()
                    print("DEBUG: Контейнер очищен")
                    
                    # Пересоздаем все элементы
                    for i, (source_name, frequency) in enumerate(sources_with_freq):
                        with sources_container:
                            with ui.row().classes("items-center gap-3 p-3 bg-gray-50 rounded-lg"):
                                # Номер по популярности
                                ui.label(f"{i+1}.").classes("text-sm font-bold text-gray-600 w-8")
                                
                                # Название источника
                                ui.label(source_name).classes("flex-1 text-sm font-medium")
                                
                                # Частота использования
                                ui.label(f"({frequency} раз)").classes("text-xs text-gray-500")
                                
                                # Кнопки управления
                                with ui.row().classes("gap-1"):
                                    ui.button("✏️", on_click=lambda s=source_name: edit_source_name(s, mgmt_dialog, refresh_both)).props("size=sm flat").classes("text-blue-600")
                                    ui.button("🗑️", on_click=lambda s=source_name: delete_source(s, mgmt_dialog, refresh_both)).props("size=sm flat").classes("text-red-600")
                                    if i > 0:
                                        ui.button("⬆️", on_click=lambda s=source_name: move_source_up(s, mgmt_dialog, refresh_both)).props("size=sm flat").classes("text-green-600")
                                    if i < len(sources_with_freq) - 1:
                                        ui.button("⬇️", on_click=lambda s=source_name: move_source_down(s, mgmt_dialog, refresh_both)).props("size=sm flat").classes("text-green-600")
                    print("DEBUG: Список источников обновлен")

            # Обновляет и выпадающий список в форме, и список в диалоге
            def refresh_both():
                try:
                    refresh_sources_list()  # обновляет селект и топ‑кнопки в форме
                except Exception as _:
                    pass
                refresh_mgmt_sources_list()
            
            with mgmt_dialog, ui.card().classes("min-w-[600px] max-w-[800px] p-6"):
                # Заголовок
                with ui.row().classes("items-center gap-2 mb-6 pb-4 border-b border-gray-200"):
                    ui.icon("settings").classes("text-2xl text-blue-600")
                    ui.label("Управление источниками").classes("text-2xl font-bold text-gray-800")
                
                # Список источников с возможностью редактирования
                with ui.column().classes("space-y-3"):
                    ui.label("Источники (сортировка по популярности):").classes("text-sm font-medium text-gray-700")
                    
                    sources_container = ui.column().classes("space-y-3")
                    refresh_mgmt_sources_list()  # Инициализируем список
                
                # Кнопки действий
                with ui.row().classes("justify-end gap-3 mt-6 pt-4 border-t border-gray-200"):
                    ui.button("Закрыть", on_click=mgmt_dialog.close).classes(
                        "bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg"
                    )
                    ui.button("Добавить источник", on_click=lambda: add_new_source(mgmt_dialog, refresh_both)).classes(
                        "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
                    )
                
                mgmt_dialog.open()

        def show_sources_statistics():
            """Показывает статистику использования источников"""
            with ui.dialog() as stats_dialog, ui.card().classes("min-w-[500px] max-w-[700px] p-6"):
                # Заголовок
                with ui.row().classes("items-center gap-2 mb-6 pb-4 border-b border-gray-200"):
                    ui.icon("analytics").classes("text-2xl text-green-600")
                    ui.label("Статистика источников").classes("text-2xl font-bold text-gray-800")
                
                # Получаем статистику из базы данных
                stats = get_source_statistics()
                total_transactions = stats["total_transactions"]
                unique_sources = stats["unique_sources"]
                top_sources = stats["top_sources"]
                
                # Общая статистика
                with ui.card().classes("p-4 bg-blue-50 mb-4"):
                    ui.label("Общая статистика").classes("text-lg font-semibold text-blue-800 mb-2")
                    ui.label(f"Всего сделок: {total_transactions}").classes("text-sm text-blue-700")
                    ui.label(f"Уникальных источников: {unique_sources}").classes("text-sm text-blue-700")
                
                # Топ источников
                with ui.column().classes("space-y-2"):
                    ui.label("Топ источников:").classes("text-sm font-medium text-gray-700")
                    
                    if top_sources:
                        for i, (source_name, frequency) in enumerate(top_sources):
                            if frequency > 0:
                                percentage = (frequency / total_transactions * 100) if total_transactions > 0 else 0
                                with ui.row().classes("items-center gap-3 p-2 bg-gray-50 rounded"):
                                    ui.label(f"{i+1}.").classes("text-sm font-bold text-gray-600 w-8")
                                    ui.label(source_name).classes("flex-1 text-sm font-medium")
                                    ui.label(f"{frequency} ({percentage:.1f}%)").classes("text-xs text-gray-500")
                                    
                                    # Прогресс-бар
                                    with ui.column().classes("flex-1"):
                                        ui.linear_progress(percentage / 100).classes("h-2")
                    else:
                        ui.label("Нет данных о сделках").classes("text-sm text-gray-500 italic")
                
                # Кнопка закрытия
                with ui.row().classes("justify-end mt-6 pt-4 border-t border-gray-200"):
                    ui.button("Закрыть", on_click=stats_dialog.close).classes(
                        "bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg"
                    )
                
                stats_dialog.open()

        def get_current_price():
            """Получает текущую цену монеты"""
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
                        f"❌ Не удалось получить цену для {coin_symbol}",
                        type="negative",
                    )

            except Exception as e:
                ui.notify(f"❌ Ошибка получения цены: {e}", type="negative")

        def on_add():
            """Добавляет сделку"""
            # Валидация полей
            if not coin.value or not coin.value.strip():
                ui.notify("❌ Введите символ монеты", type="negative")
                return

            if not qty.value or float(qty.value) <= 0:
                ui.notify("❌ Введите корректное количество", type="negative")
                return

            if not price.value or float(price.value) <= 0:
                ui.notify("❌ Введите корректную цену", type="negative")
                return

            try:
                # Получаем значения из полей
                coin_symbol = (coin.value or "").upper().strip()
                quantity = float(qty.value or 0)
                price_value = float(price.value or 0)
                source_name = (source.value or "").strip()
                notes_value = (notes.value or "").strip()
                
                # Создаем объект транзакции
                data = TransactionIn(
                    coin=coin_symbol,
                    type=ttype.value,
                    quantity=quantity,
                    price=price_value,
                    strategy=strategy.value,
                    source=source_name,
                    notes=notes_value,
                )
                
                # Добавляем транзакцию в базу данных
                result = add_transaction(data)
                
                if result:
                    ui.notify("✅ Сделка успешно добавлена", type="positive")
                    dialog.close()
                    # Обновляем страницу
                    refresh()
                else:
                    ui.notify("❌ Ошибка при сохранении сделки", type="negative")
                    
            except ValueError as e:
                ui.notify(f"❌ Ошибка в данных: {e}", type="negative")
            except Exception as e:
                ui.notify(f"❌ Ошибка: {e}", type="negative")

        # Форма в две колонки
        with ui.grid(columns=2).classes("gap-6"):
            # Левая колонка - основные поля
            with ui.column().classes("gap-4"):
                # Монета с автодополнением и кнопками быстрого выбора
                with ui.column().classes("gap-1"):
                    ui.label("💰 Монета *").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    
                    # Поле ввода монеты
                    coin = (
                        ui.input(placeholder="BTC, ETH, SOL...")
                        .props(
                            "uppercase autocomplete=off autocorrect=off autocapitalize=off spellcheck=false"
                        )
                        .classes("w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent")
                        .on("keydown.escape", lambda: None)  # Временно отключено
                        .on("keydown.ctrl+enter", on_add)
                    )
                    
                    # Кнопки быстрого выбора для популярных монет
                    with ui.row().classes("gap-2 mt-2 flex-wrap"):
                        ui.label("Популярные:").classes("text-xs text-blue-600 font-medium self-center")
                        
                        # Получаем монеты из истории торговли
                        try:
                            transactions = list_transactions()
                            coin_counts = {}
                            for tx in transactions:
                                coin_symbol = tx.get("coin", "").strip().upper()
                                if coin_symbol:
                                    coin_counts[coin_symbol] = coin_counts.get(coin_symbol, 0) + 1
                            
                            # Базовые популярные монеты
                            popular_coins = ["BTC", "ETH", "SOL", "ADA", "DOT", "MATIC", "AVAX", "LINK"]
                            
                            # Добавляем популярные монеты с частотой 0
                            for pop_coin in popular_coins:
                                if pop_coin not in coin_counts:
                                    coin_counts[pop_coin] = 0
                            
                            # Сортируем по частоте использования (по убыванию)
                            sorted_coins = sorted(
                                coin_counts.items(), key=lambda x: x[1], reverse=True
                            )
                            
                            # Показываем топ-6 монет
                            for coin_symbol, frequency in sorted_coins[:6]:
                                ui.button(
                                    coin_symbol,
                                    on_click=lambda c=coin_symbol: set_coin_value(c),
                                ).props("size=sm outline").classes(
                                    "text-xs bg-green-100 hover:bg-green-200 text-green-700 px-2 py-1 rounded"
                                )
                        except Exception:
                            # Fallback кнопки
                            for coin_symbol in ["BTC", "ETH", "SOL", "ADA", "DOT", "MATIC"]:
                                ui.button(
                                    coin_symbol,
                                    on_click=lambda c=coin_symbol: set_coin_value(c),
                                ).props("size=sm outline").classes(
                                    "text-xs bg-green-100 hover:bg-green-200 text-green-700 px-2 py-1 rounded"
                                )
                    
                    ui.label("Введите символ криптовалюты или используйте кнопки").classes(
                        "text-xs text-gray-500"
                    )

                # Тип операции с иконками
                with ui.column().classes("gap-1"):
                    ui.label("📊 Тип операции *").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    ttype = ui.select(
                        TYPES, label="Выберите тип", value="buy"
                    ).classes("w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent")
                    ui.label("buy = покупка, sell = продажа").classes(
                        "text-xs text-gray-500"
                    )

                # Количество с валидацией
                with ui.column().classes("gap-1"):
                    ui.label("📦 Количество *").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    qty = (
                        ui.input(placeholder="0.0")
                        .props(
                            "type=number inputmode=decimal autocomplete=off step=0.000001"
                        )
                        .classes("w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent")
                        .on("keydown.escape", lambda: None)  # Временно отключено
                        .on("keydown.ctrl+enter", on_add)
                    )
                    ui.label("Количество монет").classes(
                        "text-xs text-gray-500"
                    )

                # Цена с кнопкой "текущая цена"
                with ui.column().classes("gap-1"):
                    with ui.row().classes("items-center gap-2"):
                        ui.label("💵 Цена за монету *").classes(
                            "text-sm font-medium text-gray-700"
                        )
                        ui.button(
                            "📊 Текущая цена", on_click=get_current_price
                        ).props("size=sm outline").classes("text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-2 py-1 rounded").tooltip(
                            "Получить актуальную цену с CoinGecko API"
                        )
                    price = (
                        ui.input(placeholder="0.00")
                        .props(
                            "type=number inputmode=decimal autocomplete=off step=0.01"
                        )
                        .classes("w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent")
                        .on("keydown.escape", lambda: None)  # Временно отключено
                        .on("keydown.ctrl+enter", on_add)
                    )
                    ui.label(f"Цена в {CURRENCY}").classes(
                        "text-xs text-gray-500"
                    )

            # Правая колонка - дополнительные поля
            with ui.column().classes("gap-4"):
                # Стратегия
                with ui.column().classes("gap-1"):
                    ui.label("🎯 Стратегия *").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    strategy = ui.select(
                        STRATS, label="Выберите стратегию", value="long"
                    ).classes("w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent")
                    ui.label("long = долгосрочная, short = краткосрочная").classes(
                        "text-xs text-gray-500"
                    )

                # Источник с выпадающим списком, кнопками быстрого выбора и управлением
                with ui.column().classes("gap-1"):
                    ui.label("🏢 Источник").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    
                    # Используем функцию из services.py
                    
                    # Получаем источники
                    sources_with_freq = get_sources_with_frequency()
                    all_sources = [source for source, freq in sources_with_freq]
                    top_sources = [source for source, freq in sources_with_freq[:3]]  # Топ-3 для кнопок
                    
                    # Выпадающий список с возможностью ввода
                    source = ui.select(
                        all_sources, 
                        label="Выберите или введите источник",
                        with_input=True,
                        new_value_mode="add-unique"
                    ).classes("w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent")
                    
                    # Кнопки быстрого выбора для топ-3 источников
                    quick_buttons_container = ui.column().classes("mt-2")
                    if top_sources:
                        ui.label("Популярные источники:").classes("text-xs text-blue-600 font-medium")
                        with quick_buttons_container:
                            for source_name in top_sources:
                                ui.button(
                                    source_name,
                                    on_click=lambda s=source_name: set_source_value(s),
                                ).props("size=sm outline").classes(
                                    "text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-2 py-1 rounded"
                                )
                    
                    # Кнопки управления источниками
                    with ui.row().classes("gap-2 mt-2"):
                        ui.button("⚙️ Управление", icon="settings").props("size=sm outline").classes(
                            "text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded"
                        ).on("click", lambda: open_sources_management_dialog())
                        ui.button("📊 Статистика", icon="analytics").props("size=sm outline").classes(
                            "text-xs bg-green-100 hover:bg-green-200 text-green-700 px-2 py-1 rounded"
                        ).on("click", lambda: show_sources_statistics())
                    
                    ui.label("Выберите из списка, используйте кнопки или введите новый").classes(
                        "text-xs text-gray-500"
                    )

                # Заметки
                with ui.column().classes("gap-1"):
                    ui.label("📝 Заметки").classes(
                        "text-sm font-medium text-gray-700"
                    )
                    notes = (
                        ui.textarea(placeholder="Дополнительная информация...")
                        .classes("w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent")
                        .on("keydown.escape", lambda: None)  # Временно отключено
                        .on("keydown.ctrl+enter", on_add)
                    )
                    ui.label("Необязательная информация").classes(
                        "text-xs text-gray-500"
                    )

                # Определяем функцию очистки формы после создания всех переменных
                def clear_form():
                    """Очищает форму"""
                    if coin:
                        coin.value = ""
                    if qty:
                        qty.value = ""
                    if price:
                        price.value = ""
                    if source:
                        source.value = ""
                    if notes:
                        notes.value = ""
                
                # Теперь обновляем обработчики событий с правильной функцией
                for element in [coin, qty, price, notes]:
                    if element:
                        element.on("keydown.escape", clear_form)



        # Кнопки действий
        with ui.row().classes("justify-end gap-3 mt-6 pt-4 border-t border-gray-200"):
            ui.button("Отмена", on_click=dialog.close).classes(
                "bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-2 rounded-lg transition-all duration-200"
            )


            ui.button("Добавить сделку", on_click=on_add, icon="add").classes(
                "bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg transition-all duration-200"
            )

    dialog.open()


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
    """Главная страница портфеля с улучшенными карточками и полным функционалом ввода"""
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
                    .on("click", lambda: open_enhanced_add_dialog())
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
                    ).on("click", lambda: open_enhanced_add_dialog())
                    
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
                    ui.tab("charts", "📈 Графики").classes("px-4 py-2")
                    ui.tab("alerts", "🔔 Алерты").classes("px-4 py-2")
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
                                
                                # Получаем список сделок
                                try:
                                    transactions = list_transactions()
                                    if transactions:
                                        # Создаем таблицу сделок
                                        columns = [
                                            {"name": "id", "label": "ID", "field": "id", "sortable": True},
                                            {"name": "coin", "label": "Монета", "field": "coin", "sortable": True},
                                            {"name": "type", "label": "Тип", "field": "type", "sortable": True},
                                            {"name": "quantity", "label": "Количество", "field": "quantity", "sortable": True},
                                            {"name": "price", "label": "Цена", "field": "price", "sortable": True},
                                            {"name": "source", "label": "Источник", "field": "source", "sortable": True},
                                            {"name": "strategy", "label": "Стратегия", "field": "strategy", "sortable": True},
                                            {"name": "created_at", "label": "Дата", "field": "created_at", "sortable": True},
                                            {"name": "notes", "label": "Заметки", "field": "notes", "sortable": True},
                                        ]
                                        
                                        ui.table(
                                            columns=columns,
                                            rows=transactions,
                                            row_key="id"
                                        ).classes("w-full")
                                    else:
                                        with ui.row().classes("h-48 items-center justify-center bg-gray-50 rounded-lg"):
                                            ui.label("Нет сделок").classes("text-gray-500")
                                except Exception as e:
                                    with ui.row().classes("h-48 items-center justify-center bg-gray-50 rounded-lg"):
                                        ui.label(f"Ошибка загрузки: {e}").classes("text-red-500")

                    # Вкладка графиков
                    with ui.tab_panel("charts"):
                        create_charts_tab()

                    # Вкладка алертов
                    with ui.tab_panel("alerts"):
                        create_alerts_tab()

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


def refresh():
    """Обновляет данные на странице"""
    try:
        # Получаем статистику портфеля
        stats = get_portfolio_stats()
        
        # Обновляем статистические карточки
        # Это упрощенная версия - в реальном приложении нужно обновлять UI элементы
        ui.notify("Данные обновлены!", color="positive")
        
        # Можно добавить обновление таблиц и других элементов
        # ui.run_javascript("location.reload()")  # Простое обновление страницы
        
    except Exception as e:
        ui.notify(f"Ошибка обновления: {e}", color="negative")


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
                        {app_info["roadmap"]}
                        </div>
                        """
                        )


def create_alerts_tab():
    """Создает вкладку с алертами по ценам"""
    with ui.column().classes("w-full space-y-4"):
        ui.label("🔔 Алерты по ценам").classes("text-2xl font-bold text-gray-800")
        
        # Кнопки управления
        with ui.row().classes("gap-3 mb-4"):
            ui.button("➕ Добавить алерт", icon="add").classes("bg-blue-500 text-white").on("click", lambda: open_add_alert_dialog())
            ui.button("🔄 Проверить алерты", icon="refresh").classes("bg-green-500 text-white").on("click", lambda: check_alerts())
            ui.button("📊 Статистика", icon="analytics").classes("bg-purple-500 text-white").on("click", lambda: show_alert_statistics())
        
        # Список алертов
        with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
            ui.label("Активные алерты").classes("text-lg font-semibold text-gray-800 mb-4")
            
            # Контейнер для списка алертов
            alerts_container = ui.column().classes("w-full")
            
            def refresh_alerts_list():
                """Обновляет список алертов"""
                alerts_container.clear()
                
                try:
                    alerts = get_price_alerts(active_only=True)
                    if alerts:
                        for alert in alerts:
                            with alerts_container:
                                with ui.card().classes("p-3 mb-2 border-l-4 border-blue-400"):
                                    with ui.row().classes("items-center justify-between"):
                                        with ui.column().classes("flex-1"):
                                            ui.label(f"💰 {alert.coin}").classes("font-semibold text-gray-800")
                                            ui.label(f"Цель: {alert.target_price} {CURRENCY} ({alert.alert_type})").classes("text-sm text-gray-600")
                                            if alert.notes:
                                                ui.label(f"Заметка: {alert.notes}").classes("text-xs text-gray-500")
                                        with ui.row().classes("gap-2"):
                                            ui.button("✏️", on_click=lambda a=alert: edit_alert(a)).props("size=sm flat").classes("text-blue-600")
                                            ui.button("🗑️", on_click=lambda a=alert: delete_alert(a)).props("size=sm flat").classes("text-red-600")
                    else:
                        with alerts_container:
                            with ui.row().classes("h-32 items-center justify-center bg-gray-50 rounded-lg"):
                                ui.label("Нет активных алертов").classes("text-gray-500")
                except Exception as e:
                    with alerts_container:
                        with ui.row().classes("h-32 items-center justify-center bg-gray-50 rounded-lg"):
                            ui.label(f"Ошибка загрузки: {e}").classes("text-red-500")
            
            # Инициализируем список
            refresh_alerts_list()
            
            # Функции для работы с алертами
            def open_add_alert_dialog():
                """Открывает диалог добавления алерта"""
                with ui.dialog() as dialog, ui.card().classes("p-6 w-96"):
                    ui.label("Добавить алерт по цене").classes("text-lg font-semibold mb-4")
                    
                    coin_input = ui.input("Монета (например, BTC)").classes("w-full mb-3")
                    price_input = ui.number("Целевая цена").classes("w-full mb-3")
                    
                    with ui.row().classes("w-full mb-3"):
                        ui.label("Тип алерта:").classes("text-sm font-medium")
                        alert_type_select = ui.select(
                            ["above", "below"], 
                            value="above",
                            label="Выберите тип"
                        ).classes("w-full")
                    
                    notes_input = ui.textarea("Заметки (необязательно)").classes("w-full mb-4")
                    
                    def add_alert():
                        try:
                            coin = coin_input.value.strip().upper()
                            target_price = float(price_input.value)
                            alert_type = alert_type_select.value
                            notes = notes_input.value.strip() if notes_input.value else None
                            
                            if not coin or target_price <= 0:
                                ui.notify("Заполните все обязательные поля", type="negative")
                                return
                            
                            alert_data = PriceAlertIn(
                                coin=coin,
                                target_price=target_price,
                                alert_type=alert_type,
                                notes=notes
                            )
                            
                            add_price_alert(alert_data)
                            ui.notify(f"Алерт для {coin} создан", type="positive")
                            dialog.close()
                            refresh_alerts_list()
                            
                        except Exception as e:
                            ui.notify(f"Ошибка создания алерта: {e}", type="negative")
                    
                    with ui.row().classes("justify-end gap-3"):
                        ui.button("Отмена", on_click=dialog.close)
                        ui.button("Добавить", on_click=add_alert).classes("bg-blue-500 text-white")
                    
                    dialog.open()
            
            def edit_alert(alert):
                """Редактирует алерт"""
                ui.notify("Функция редактирования в разработке", type="info")
            
            def delete_alert(alert):
                """Удаляет алерт"""
                try:
                    if delete_price_alert(alert.id):
                        ui.notify(f"Алерт для {alert.coin} удален", type="positive")
                        refresh_alerts_list()
                    else:
                        ui.notify("Ошибка удаления алерта", type="negative")
                except Exception as e:
                    ui.notify(f"Ошибка: {e}", type="negative")
            
            def check_alerts():
                """Проверяет все алерты"""
                try:
                    triggered = check_price_alerts()
                    if triggered:
                        for alert in triggered:
                            ui.notify(
                                f"🔔 Алерт сработал! {alert['coin']}: {alert['current_price']} {CURRENCY} ({alert['alert_type']} {alert['target_price']})",
                                type="positive",
                                timeout=10000
                            )
                        refresh_alerts_list()
                    else:
                        ui.notify("Активных алертов не найдено", type="info")
                except Exception as e:
                    ui.notify(f"Ошибка проверки алертов: {e}", type="negative")
            
            def show_alert_statistics():
                """Показывает статистику алертов"""
                try:
                    stats = get_alert_statistics()
                    with ui.dialog() as dialog, ui.card().classes("p-6"):
                        ui.label("📊 Статистика алертов").classes("text-lg font-semibold mb-4")
                        
                        with ui.column().classes("space-y-2"):
                            ui.label(f"Всего алертов: {stats['total_alerts']}")
                            ui.label(f"Активных: {stats['active_alerts']}")
                            ui.label(f"Сработавших: {stats['triggered_alerts']}")
                        
                        with ui.row().classes("justify-end mt-4"):
                            ui.button("Закрыть", on_click=dialog.close)
                        
                        dialog.open()
                except Exception as e:
                    ui.notify(f"Ошибка получения статистики: {e}", type="negative")


def create_charts_tab():
    """Создает вкладку с графиками и визуализацией портфеля"""
    with ui.column().classes("w-full space-y-6"):
        ui.label("📈 Графики и визуализация").classes("text-2xl font-bold text-gray-800")
        
        # Кнопки управления
        with ui.row().classes("gap-3 mb-4"):
            ui.button("🔄 Обновить графики", icon="refresh").classes("bg-blue-500 text-white").on("click", lambda: refresh_all_charts())
            ui.button("📊 Сводка", icon="analytics").classes("bg-green-500 text-white").on("click", lambda: show_portfolio_summary())
        
        # Сводные карточки
        with ui.row().classes("w-full gap-4 mb-6"):
            summary = get_portfolio_summary()
            
            with ui.card().classes("p-4 bg-blue-50 border-l-4 border-blue-400"):
                ui.label("Всего сделок").classes("text-sm text-gray-600")
                ui.label(str(summary['total_transactions'])).classes("text-2xl font-bold text-blue-600")
            
            with ui.card().classes("p-4 bg-green-50 border-l-4 border-green-400"):
                ui.label("Уникальных монет").classes("text-sm text-gray-600")
                ui.label(str(summary['unique_coins'])).classes("text-2xl font-bold text-green-600")
            
            with ui.card().classes("p-4 bg-purple-50 border-l-4 border-purple-400"):
                ui.label("Активных позиций").classes("text-sm text-gray-600")
                ui.label(str(summary['active_positions'])).classes("text-2xl font-bold text-purple-600")
            
            with ui.card().classes("p-4 bg-orange-50 border-l-4 border-orange-400"):
                ui.label("Общий объем").classes("text-sm text-gray-600")
                ui.label(f"{summary['total_volume']:.2f} {CURRENCY}").classes("text-2xl font-bold text-orange-600")
        
        # Графики в сетке 2x2
        with ui.row().classes("w-full gap-4"):
            # Левая колонка
            with ui.column().classes("flex-1 space-y-4"):
                # Распределение портфеля
                with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
                    ui.label("Распределение портфеля").classes("text-lg font-semibold text-gray-800 mb-4")
                    portfolio_chart_container = ui.html("").classes("w-full")
                
                # Временная линия транзакций
                with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
                    ui.label("Временная линия транзакций").classes("text-lg font-semibold text-gray-800 mb-4")
                    timeline_chart_container = ui.html("").classes("w-full")
            
            # Правая колонка
            with ui.column().classes("flex-1 space-y-4"):
                # Производительность по стратегиям
                with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
                    ui.label("Производительность по стратегиям").classes("text-lg font-semibold text-gray-800 mb-4")
                    strategy_chart_container = ui.html("").classes("w-full")
                
                # Активность по источникам
                with ui.card().classes("p-4 bg-white shadow-sm rounded-lg"):
                    ui.label("Активность по источникам").classes("text-lg font-semibold text-gray-800 mb-4")
                    source_chart_container = ui.html("").classes("w-full")
        
        def refresh_all_charts():
            """Обновляет все графики"""
            try:
                ui.notify("Обновление графиков...", type="info")
                
                # Обновляем каждый график
                portfolio_chart_container.content = create_portfolio_distribution_chart()
                timeline_chart_container.content = create_transactions_timeline_chart()
                strategy_chart_container.content = create_strategy_performance_chart()
                source_chart_container.content = create_source_activity_chart()
                
                ui.notify("Графики обновлены!", type="positive")
            except Exception as e:
                ui.notify(f"Ошибка обновления графиков: {e}", type="negative")
        
        def show_portfolio_summary():
            """Показывает детальную сводку портфеля"""
            try:
                summary = get_portfolio_summary()
                
                with ui.dialog() as dialog, ui.card().classes("p-6 w-96"):
                    ui.label("📊 Сводка портфеля").classes("text-lg font-semibold mb-4")
                    
                    with ui.column().classes("space-y-3"):
                        ui.label(f"Всего сделок: {summary['total_transactions']}")
                        ui.label(f"Уникальных монет: {summary['unique_coins']}")
                        ui.label(f"Активных позиций: {summary['active_positions']}")
                        ui.label(f"Общий объем: {summary['total_volume']:.2f} {CURRENCY}")
                        ui.label(f"Средний размер сделки: {summary['avg_transaction_size']:.2f} {CURRENCY}")
                    
                    with ui.row().classes("justify-end mt-4"):
                        ui.button("Закрыть", on_click=dialog.close)
                    
                    dialog.open()
            except Exception as e:
                ui.notify(f"Ошибка получения сводки: {e}", type="negative")
        
        # Инициализируем графики при загрузке
        refresh_all_charts()


@ui.page("/")
def main_page():
    """Главная страница с портфелем"""
    portfolio_page()
