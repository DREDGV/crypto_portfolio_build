"""
UI для системы алертов
"""

from datetime import datetime

from nicegui import ui

from app.core.services import get_portfolio_stats
from app.models.alert_models import AlertRuleIn, AlertRuleUpdate, AlertStatus, AlertType
from app.services.alert_exporter import AlertExporter
from app.services.alert_service import AlertService

alert_service = AlertService()
alert_exporter = AlertExporter()


def get_portfolio_symbols():
    """Получить все символы из портфеля"""
    try:
        stats = get_portfolio_stats()
        symbols = set()

        # Добавляем криптовалюты
        for position in stats.get("positions", []):
            if position.get("symbol"):
                symbols.add(position["symbol"].upper())

        # Добавляем акции (если есть)
        # TODO: Добавить получение акций из StockService

        return sorted(list(symbols))
    except Exception as e:
        print(f"Ошибка получения символов портфеля: {e}")
        return []


def get_popular_symbols():
    """Получить список популярных символов"""
    return [
        "BTC",
        "ETH",
        "BNB",
        "ADA",
        "SOL",
        "DOT",
        "MATIC",
        "AVAX",
        "SBER",
        "GAZP",
        "LKOH",
        "YNDX",
        "NVTK",
        "AFLT",
        "QIWI",
    ]


def create_alerts_tab():
    """Создать вкладку с алертами"""

    # Контейнер для алертов
    alerts_container = ui.column().classes("w-full")

    # Контейнер для истории срабатываний
    triggers_container = ui.column().classes("w-full")

    # Контейнер для уведомлений
    notifications_container = ui.column().classes("w-full")

    def refresh_alerts():
        """Обновить список алертов"""
        alerts_container.clear()
        load_alerts()

    def load_notifications():
        """Загрузить активные уведомления"""
        with notifications_container:
            # Заголовок
            ui.label("🔔 Активные уведомления").classes(
                "text-2xl font-bold mb-4 text-gray-800"
            )

            # Получаем непрочитанные срабатывания
            triggers = alert_service.get_alert_triggers(is_read=False, limit=10)

            if not triggers:
                ui.label("Нет новых уведомлений").classes("text-gray-500 italic")
                return

            # Список уведомлений
            for trigger in triggers:
                create_notification_card(trigger)

    def create_notification_card(trigger):
        """Создать карточку уведомления"""
        with ui.card().classes("w-full mb-3 p-4 bg-blue-50 border-l-4 border-blue-400"):
            with ui.row().classes("w-full items-center"):
                # Основная информация
                with ui.column().classes("flex-1"):
                    # Символ и время
                    with ui.row().classes("items-center gap-2 mb-2"):
                        ui.label(f"🔔 {trigger.symbol}").classes(
                            "text-lg font-bold text-blue-600"
                        )
                        ui.label(
                            trigger.triggered_at.strftime("%d.%m.%Y %H:%M:%S")
                        ).classes("text-sm text-gray-500")

                    # Цены
                    ui.label(
                        f"Цена: {trigger.current_price} | Порог: {trigger.threshold_value}"
                    ).classes("text-sm font-medium")

                    # Сообщение
                    if trigger.message:
                        ui.label(trigger.message).classes("text-sm text-gray-700 mt-1")

                # Кнопки управления
                with ui.column().classes("gap-2"):
                    # Отметить как прочитанное
                    ui.button(
                        "✅", on_click=lambda t=trigger: mark_notification_read(t)
                    ).classes("text-sm bg-green-500 text-white")

                    # Перейти к алерту
                    ui.button(
                        "👁️", on_click=lambda t=trigger: view_alert_details(t)
                    ).classes("text-sm bg-blue-500 text-white")

    def mark_notification_read(trigger):
        """Отметить уведомление как прочитанное"""
        try:
            alert_service.mark_trigger_as_read(trigger.id)
            ui.notify("Уведомление отмечено как прочитанное", type="positive")
            refresh_notifications()
        except Exception as e:
            ui.notify(f"Ошибка: {e}", type="negative")

    def view_alert_details(trigger):
        """Показать детали алерта"""
        try:
            alert_rule = alert_service.get_alert_rule(trigger.alert_rule_id)
            if alert_rule:
                ui.notify(
                    f"Алерт: {alert_rule.symbol} {alert_rule.alert_type.value} {alert_rule.threshold_value}",
                    type="info",
                )
        except Exception as e:
            ui.notify(f"Ошибка получения деталей: {e}", type="negative")

    def refresh_notifications():
        """Обновить уведомления"""
        notifications_container.clear()
        load_notifications()

    def refresh_triggers():
        """Обновить историю срабатываний"""
        triggers_container.clear()
        load_triggers()

    def load_alerts():
        """Загрузить список алертов"""
        with alerts_container:
            # Заголовок
            ui.label("🔔 Правила алертов").classes(
                "text-2xl font-bold mb-4 text-gray-800"
            )

            # Кнопки управления
            with ui.row().classes("w-full mb-4 gap-2"):
                ui.button(
                    "➕ Создать алерт", icon="add", on_click=open_create_alert_dialog
                ).classes("bg-blue-500 text-white")
                ui.button(
                    "🔄 Обновить", icon="refresh", on_click=refresh_alerts
                ).classes("bg-gray-500 text-white")
                ui.button(
                    "📤 Экспорт", icon="download", on_click=open_export_dialog
                ).classes("bg-green-500 text-white")
                ui.button(
                    "📥 Импорт", icon="upload", on_click=open_import_dialog
                ).classes("bg-purple-500 text-white")

            # Получаем алерты
            alerts = alert_service.get_alert_rules()

            if not alerts:
                ui.label("Нет созданных алертов").classes("text-gray-500 italic")
                return

            # Список алертов
            for alert in alerts:
                create_alert_card(alert)

    def load_triggers():
        """Загрузить историю срабатываний"""
        with triggers_container:
            # Заголовок
            ui.label("📊 История срабатываний").classes(
                "text-2xl font-bold mb-4 text-gray-800"
            )

            # Кнопки управления
            with ui.row().classes("w-full mb-4 gap-2"):
                ui.button(
                    "🔄 Обновить", icon="refresh", on_click=refresh_triggers
                ).classes("bg-gray-500 text-white")
                ui.button(
                    "✅ Отметить все как прочитанные",
                    icon="done",
                    on_click=mark_all_read,
                ).classes("bg-green-500 text-white")

            # Получаем срабатывания
            triggers = alert_service.get_alert_triggers(limit=50)

            if not triggers:
                ui.label("Нет срабатываний").classes("text-gray-500 italic")
                return

            # Список срабатываний
            for trigger in triggers:
                create_trigger_card(trigger)

    def create_alert_card(alert):
        """Создать карточку алерта"""
        with ui.card().classes("w-full mb-3 p-4"):
            with ui.row().classes("w-full items-center"):
                # Основная информация
                with ui.column().classes("flex-1"):
                    # Символ и тип
                    with ui.row().classes("items-center gap-2 mb-2"):
                        ui.label(f"📈 {alert.symbol}").classes(
                            "text-lg font-bold text-blue-600"
                        )

                        # Преобразуем тип алерта в понятное название
                        alert_type_names = {
                            AlertType.PRICE_ABOVE: "Цена выше",
                            AlertType.PRICE_BELOW: "Цена ниже",
                            AlertType.PRICE_CHANGE_PERCENT: "Изменение %",
                        }
                        alert_type_name = alert_type_names.get(
                            alert.alert_type, alert.alert_type.value
                        )

                        ui.label(f"[{alert_type_name}]").classes(
                            "text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded"
                        )

                        # Статус
                        status_color = {
                            AlertStatus.ACTIVE: "bg-green-100 text-green-800",
                            AlertStatus.PAUSED: "bg-yellow-100 text-yellow-800",
                            AlertStatus.TRIGGERED: "bg-red-100 text-red-800",
                            AlertStatus.EXPIRED: "bg-gray-100 text-gray-800",
                        }
                        ui.label(alert.status.value).classes(
                            f"text-xs px-2 py-1 rounded {status_color.get(alert.status, 'bg-gray-100')}"
                        )

                    # Пороговое значение
                    ui.label(f"Порог: {alert.threshold_value}").classes(
                        "text-sm text-gray-600"
                    )

                    # Сообщение
                    if alert.message:
                        ui.label(f"Сообщение: {alert.message}").classes(
                            "text-sm text-gray-600"
                        )

                    # Время создания
                    ui.label(
                        f"Создан: {alert.created_at.strftime('%d.%m.%Y %H:%M')}"
                    ).classes("text-xs text-gray-500")

                # Кнопки управления
                with ui.column().classes("gap-2"):
                    # Переключить статус
                    toggle_text = "⏸️" if alert.is_active else "▶️"
                    ui.button(
                        toggle_text, on_click=lambda a=alert: toggle_alert(a)
                    ).classes("text-sm")

                    # Редактировать
                    ui.button(
                        "✏️", on_click=lambda a=alert: open_edit_alert_dialog(a)
                    ).classes("text-sm")

                    # Удалить
                    ui.button("🗑️", on_click=lambda a=alert: delete_alert(a)).classes(
                        "text-sm text-red-600"
                    )

    def create_trigger_card(trigger):
        """Создать карточку срабатывания"""
        read_class = "" if trigger.is_read else "bg-blue-50 border-l-4 border-blue-400"

        with ui.card().classes(f"w-full mb-2 p-3 {read_class}"):
            with ui.row().classes("w-full items-center"):
                # Основная информация
                with ui.column().classes("flex-1"):
                    # Символ и время
                    with ui.row().classes("items-center gap-2 mb-1"):
                        ui.label(f"📈 {trigger.symbol}").classes(
                            "font-bold text-blue-600"
                        )
                        ui.label(
                            trigger.triggered_at.strftime("%d.%m.%Y %H:%M:%S")
                        ).classes("text-sm text-gray-500")

                    # Цены
                    ui.label(
                        f"Цена: {trigger.current_price} | Порог: {trigger.threshold_value}"
                    ).classes("text-sm")

                    # Сообщение
                    if trigger.message:
                        ui.label(trigger.message).classes("text-sm text-gray-600")

                # Кнопка "прочитано"
                if not trigger.is_read:
                    ui.button(
                        "✅", on_click=lambda t=trigger: mark_trigger_read(t)
                    ).classes("text-sm")

    def open_create_alert_dialog():
        """Открыть диалог создания алерта"""
        with ui.dialog() as dialog, ui.card().classes(
            "w-[800px] max-w-[90vw] max-h-[85vh] p-4"
        ):
            ui.label("Создать новый алерт").classes("text-xl font-bold mb-3")

            # Контейнер с прокруткой для содержимого
            with ui.column().classes("w-full overflow-y-auto"):
                # Получаем символы из портфеля и популярные
                portfolio_symbols = get_portfolio_symbols()
                popular_symbols = get_popular_symbols()

                # Символ актива (на всю ширину)
                with ui.row().classes("w-full mb-2"):
                    with ui.column().classes("w-full"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label("Символ актива").classes("text-sm font-medium")
                            ui.icon("help_outline").tooltip(
                                "Введите тикер актива (BTC, ETH, SBER)"
                            )
                        symbol_input = (
                            ui.input(placeholder="BTC, ETH, SBER")
                            .classes("w-full")
                            .props("dense outlined")
                        )

                # Быстрый выбор символов - компактно
                with ui.column().classes("w-full mb-2"):
                    ui.label("Быстрый выбор:").classes("text-sm font-medium mb-1")

                    # Символы из портфеля
                    if portfolio_symbols:
                        with ui.row().classes("flex-wrap gap-1 mb-1"):
                            ui.label("Портфель:").classes("text-xs text-gray-500")
                            for symbol in portfolio_symbols[:8]:
                                ui.button(
                                    symbol,
                                    on_click=lambda s=symbol: symbol_input.set_value(s),
                                ).classes(
                                    "text-xs px-1 py-0 bg-blue-100 hover:bg-blue-200"
                                )

                    # Популярные символы
                    with ui.row().classes("flex-wrap gap-1"):
                        ui.label("Популярные:").classes("text-xs text-gray-500")
                        for symbol in popular_symbols[:8]:
                            ui.button(
                                symbol,
                                on_click=lambda s=symbol: symbol_input.set_value(s),
                            ).classes("text-xs px-1 py-0 bg-gray-100 hover:bg-gray-200")

                # Двухколоночная компоновка полей
                with ui.row().classes("grid grid-cols-2 gap-3 w-full mb-2"):
                    # Тип алерта (колонка 1)
                    with ui.column().classes("w-full"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label("Тип алерта").classes("text-sm font-medium")
                            ui.icon("help_outline").tooltip(
                                "Выберите условие срабатывания алерта"
                            )
                        alert_type_select = (
                            ui.select(
                                [
                                    "Цена выше",
                                    "Цена ниже",
                                    "Изменение цены на %",
                                ],
                                value="Цена выше",
                            )
                            .classes("w-full")
                            .props("dense outlined")
                        )

                    # Пороговое значение (колонка 2)
                    with ui.column().classes("w-full"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label("Пороговое значение").classes(
                                "text-sm font-medium"
                            )
                            ui.icon("help_outline").tooltip(
                                "Цена или процент для срабатывания"
                            )
                        threshold_input = (
                            ui.number("", value=0.0, min=0)
                            .classes("w-full")
                            .props("dense outlined")
                        )

                # Кулердаун и сообщение
                with ui.row().classes("grid grid-cols-2 gap-3 w-full mb-2"):
                    # Кулердаун (колонка 1)
                    with ui.column().classes("w-full"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label("Кулердаун (мин)").classes("text-sm font-medium")
                            ui.icon("help_outline").tooltip(
                                "Время ожидания перед повторным срабатыванием"
                            )
                        cooldown_input = (
                            ui.number("", value=60, min=1)
                            .classes("w-full")
                            .props("dense outlined")
                        )

                    # Сообщение (колонка 2, но на всю ширину)
                    with ui.column().classes("col-span-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label("Сообщение (необязательно)").classes(
                                "text-sm font-medium"
                            )
                            ui.icon("help_outline").tooltip(
                                "Текст уведомления при срабатывании"
                            )
                        message_input = (
                            ui.textarea(placeholder="Алерт сработал!")
                            .classes("w-full")
                            .props("dense outlined auto-grow")
                        )

                # Быстрые шаблоны - компактно
                with ui.column().classes("w-full mb-2"):
                    ui.label("Быстрые шаблоны:").classes("text-sm font-medium mb-1")
                    with ui.row().classes("flex-wrap gap-1"):
                        ui.button(
                            "Bitcoin $50k+",
                            on_click=lambda: apply_template(
                                "BTC", "Цена выше", 50000, "Bitcoin достиг $50,000!"
                            ),
                        ).classes("text-xs px-1 py-0 bg-orange-100 hover:bg-orange-200")

                        ui.button(
                            "Ethereum $3k+",
                            on_click=lambda: apply_template(
                                "ETH", "Цена выше", 3000, "Ethereum достиг $3,000!"
                            ),
                        ).classes("text-xs px-1 py-0 bg-blue-100 hover:bg-blue-200")

                        ui.button(
                            "SBER $200+",
                            on_click=lambda: apply_template(
                                "SBER", "Цена выше", 200, "Сбербанк достиг 200₽!"
                            ),
                        ).classes("text-xs px-1 py-0 bg-green-100 hover:bg-green-200")

            def apply_template(symbol, alert_type_str, threshold, message):
                """Применить шаблон алерта"""
                symbol_input.set_value(symbol)
                alert_type_select.set_value(alert_type_str)
                threshold_input.set_value(threshold)
                message_input.set_value(message)

            # Липкая панель действий внизу
            with ui.row().classes("w-full gap-2 mt-2 sticky bottom-0 bg-white pt-2"):
                ui.button("Создать", on_click=lambda: create_alert()).classes(
                    "bg-blue-500 text-white flex-1"
                )
                ui.button("Отмена", on_click=dialog.close).classes(
                    "bg-gray-500 text-white flex-1"
                )

            def create_alert():
                try:
                    if not symbol_input.value.strip():
                        ui.notify("Введите символ актива", type="negative")
                        return

                    if threshold_input.value <= 0:
                        ui.notify(
                            "Пороговое значение должно быть больше 0", type="negative"
                        )
                        return

                    # Преобразуем строковое значение в enum
                    alert_type_mapping = {
                        "Цена выше": AlertType.PRICE_ABOVE,
                        "Цена ниже": AlertType.PRICE_BELOW,
                        "Изменение цены на %": AlertType.PRICE_CHANGE_PERCENT,
                    }

                    alert_type = alert_type_mapping.get(alert_type_select.value)
                    if not alert_type:
                        ui.notify("Выберите тип алерта", type="negative")
                        return

                    alert_data = AlertRuleIn(
                        symbol=symbol_input.value.strip().upper(),
                        alert_type=alert_type,
                        threshold_value=threshold_input.value,
                        message=message_input.value or None,
                        cooldown_minutes=int(cooldown_input.value),
                    )

                    alert_service.create_alert_rule(alert_data)
                    ui.notify("Алерт создан успешно!", type="positive")
                    dialog.close()
                    refresh_alerts()

                except Exception as e:
                    ui.notify(f"Ошибка создания алерта: {e}", type="negative")

        dialog.open()

    def open_edit_alert_dialog(alert):
        """Открыть диалог редактирования алерта"""
        with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
            ui.label("Редактировать алерт").classes("text-xl font-bold mb-4")

            # Форма
            threshold_input = ui.number(
                "Пороговое значение", value=alert.threshold_value
            ).classes("w-full mb-3")
            message_input = ui.input("Сообщение", value=alert.message or "").classes(
                "w-full mb-3"
            )
            cooldown_input = ui.number(
                "Кулердаун (минуты)", value=alert.cooldown_minutes
            ).classes("w-full mb-3")

            is_active_checkbox = ui.checkbox("Активен", value=alert.is_active).classes(
                "w-full mb-3"
            )

            with ui.row().classes("w-full gap-2"):
                ui.button("Сохранить", on_click=lambda: update_alert()).classes(
                    "bg-blue-500 text-white flex-1"
                )
                ui.button("Отмена", on_click=dialog.close).classes(
                    "bg-gray-500 text-white flex-1"
                )

            def update_alert():
                try:
                    update_data = AlertRuleUpdate(
                        threshold_value=threshold_input.value,
                        message=message_input.value or None,
                        cooldown_minutes=int(cooldown_input.value),
                        is_active=is_active_checkbox.value,
                    )

                    alert_service.update_alert_rule(alert.id, update_data)
                    ui.notify("Алерт обновлен!", type="positive")
                    dialog.close()
                    refresh_alerts()

                except Exception as e:
                    ui.notify(f"Ошибка обновления алерта: {e}", type="negative")

        dialog.open()

    def toggle_alert(alert):
        """Переключить статус алерта"""
        try:
            alert_service.toggle_alert_rule(alert.id)
            ui.notify("Статус алерта изменен", type="positive")
            refresh_alerts()
        except Exception as e:
            ui.notify(f"Ошибка изменения статуса: {e}", type="negative")

    def delete_alert(alert):
        """Удалить алерт"""
        try:
            alert_service.delete_alert_rule(alert.id)
            ui.notify("Алерт удален", type="positive")
            refresh_alerts()
        except Exception as e:
            ui.notify(f"Ошибка удаления алерта: {e}", type="negative")

    def mark_trigger_read(trigger):
        """Отметить срабатывание как прочитанное"""
        try:
            alert_service.mark_trigger_as_read(trigger.id)
            ui.notify("Отмечено как прочитанное", type="positive")
            refresh_triggers()
        except Exception as e:
            ui.notify(f"Ошибка: {e}", type="negative")

    def mark_all_read():
        """Отметить все срабатывания как прочитанные"""
        try:
            count = alert_service.mark_all_triggers_as_read()
            ui.notify(f"Отмечено {count} срабатываний как прочитанные", type="positive")
            refresh_triggers()
        except Exception as e:
            ui.notify(f"Ошибка: {e}", type="negative")

    def open_export_dialog():
        """Открыть диалог экспорта алертов"""
        with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
            ui.label("Экспорт алертов").classes("text-xl font-bold mb-4")

            # Получаем все алерты
            alerts = alert_service.get_alert_rules()

            if not alerts:
                ui.label("Нет алертов для экспорта").classes("text-gray-500")
                ui.button("Закрыть", on_click=dialog.close).classes(
                    "bg-gray-500 text-white"
                )
                dialog.open()
                return

            # Статистика экспорта
            stats = alert_exporter.get_export_stats(alerts)

            ui.label(f"Будет экспортировано {stats['total_alerts']} алертов:").classes(
                "text-sm mb-2"
            )
            ui.label(f"• Активных: {stats['active_alerts']}").classes(
                "text-xs text-gray-600"
            )
            ui.label(f"• Криптовалюты: {stats['crypto_alerts']}").classes(
                "text-xs text-gray-600"
            )
            ui.label(f"• Акции: {stats['stock_alerts']}").classes(
                "text-xs text-gray-600"
            )

            # Выбор формата
            format_select = ui.select(
                ["JSON (рекомендуется)", "CSV"],
                value="JSON (рекомендуется)",
                label="Формат экспорта",
            ).classes("w-full mb-4")

            with ui.row().classes("w-full gap-2"):
                ui.button("Экспортировать", on_click=lambda: export_alerts()).classes(
                    "bg-green-500 text-white flex-1"
                )
                ui.button("Отмена", on_click=dialog.close).classes(
                    "bg-gray-500 text-white flex-1"
                )

            def export_alerts():
                try:
                    # Преобразуем строковое значение в формат
                    format_mapping = {"JSON (рекомендуется)": "json", "CSV": "csv"}

                    export_format = format_mapping.get(format_select.value, "json")

                    if export_format == "json":
                        data = alert_exporter.export_alerts_to_json(alerts)
                        filename = f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    else:
                        data = alert_exporter.export_alerts_to_csv(alerts)
                        filename = f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                    # Создаем файл для скачивания
                    ui.download(data, filename, "application/octet-stream")
                    ui.notify(f"Экспорт завершен: {filename}", type="positive")
                    dialog.close()

                except Exception as e:
                    ui.notify(f"Ошибка экспорта: {e}", type="negative")

        dialog.open()

    def open_import_dialog():
        """Открыть диалог импорта алертов"""
        with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
            ui.label("Импорт алертов").classes("text-xl font-bold mb-4")

            ui.label("Выберите файл для импорта:").classes("text-sm mb-4")

            # Поле для загрузки файла
            ui.upload(
                on_upload=lambda e: handle_file_upload(e),
                max_file_size=1024 * 1024,  # 1MB
            ).classes("w-full mb-4")

            ui.label("Поддерживаемые форматы: JSON, CSV").classes(
                "text-xs text-gray-500 mb-4"
            )

            with ui.row().classes("w-full gap-2"):
                ui.button("Отмена", on_click=dialog.close).classes(
                    "bg-gray-500 text-white flex-1"
                )

            def handle_file_upload(e):
                try:
                    file_content = e.content.read().decode("utf-8")

                    if e.name.endswith(".json"):
                        imported_alerts = alert_exporter.import_alerts_from_json(
                            file_content
                        )
                    elif e.name.endswith(".csv"):
                        ui.notify("Импорт CSV пока не поддерживается", type="warning")
                        return
                    else:
                        ui.notify("Неподдерживаемый формат файла", type="negative")
                        return

                    ui.notify(
                        f"Импортировано {len(imported_alerts)} алертов", type="positive"
                    )
                    dialog.close()
                    refresh_alerts()

                except Exception as e:
                    ui.notify(f"Ошибка импорта: {e}", type="negative")

        dialog.open()

    # Создаем табы
    with ui.tabs().classes("w-full") as tabs:
        notifications_tab = ui.tab("🔔 Уведомления")
        alerts_tab = ui.tab("📋 Алерты")
        triggers_tab = ui.tab("📊 История")

    with ui.tab_panels(tabs, value=notifications_tab).classes("w-full"):
        with ui.tab_panel(notifications_tab):
            load_notifications()

        with ui.tab_panel(alerts_tab):
            load_alerts()

        with ui.tab_panel(triggers_tab):
            load_triggers()

    return alerts_container
