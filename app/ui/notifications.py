"""
UI компоненты для системы уведомлений
"""
from nicegui import ui
from typing import List, Dict
from app.core.notifications import Notification, get_notification_manager


class NotificationUI:
    """UI компонент для отображения уведомлений"""
    
    def __init__(self):
        self.notification_manager = get_notification_manager()
        self.notification_container = None
        self.notification_badge = None
        self.notification_count = 0
        
    def create_notification_badge(self) -> ui.element:
        """Создание бейджа с количеством уведомлений"""
        with ui.button(icon="notifications", color="primary") as badge_btn:
            self.notification_badge = ui.badge("0", color="red").classes("absolute -top-2 -right-2")
            badge_btn.on("click", self.show_notifications_dialog)
        
        return badge_btn
    
    def show_notifications_dialog(self):
        """Показ диалога с уведомлениями"""
        notifications = self.notification_manager.get_notifications(20)
        
        with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl max-h-[80vh]"):
            ui.label("🔔 Уведомления").classes("text-xl font-bold mb-4")
            
            if not notifications:
                ui.label("Нет новых уведомлений").classes("text-gray-500 text-center py-8")
            else:
                # Кнопки управления
                with ui.row().classes("justify-between items-center mb-4"):
                    ui.label(f"Всего уведомлений: {len(notifications)}")
                    with ui.row():
                        ui.button("Очистить все", icon="clear_all", color="red").on(
                            "click", lambda: self.clear_all_notifications(dialog)
                        )
                        ui.button("Закрыть", icon="close").on("click", dialog.close)
                
                # Список уведомлений
                with ui.column().classes("w-full space-y-2 max-h-[60vh] overflow-y-auto"):
                    for notification in reversed(notifications):  # Показываем новые сверху
                        self._create_notification_item(notification)
            
            dialog.open()
    
    def _create_notification_item(self, notification: Notification):
        """Создание элемента уведомления"""
        # Определяем цвет и иконку по типу
        color_map = {
            'success': 'green',
            'info': 'blue', 
            'warning': 'orange',
            'error': 'red'
        }
        
        icon_map = {
            'success': 'check_circle',
            'info': 'info',
            'warning': 'warning',
            'error': 'error'
        }
        
        color = color_map.get(notification.type, 'blue')
        icon = icon_map.get(notification.type, 'info')
        
        with ui.card().classes(f"w-full border-l-4 border-{color}-500"):
            with ui.row().classes("items-start gap-3"):
                ui.icon(icon).classes(f"text-{color}-500 mt-1")
                
                with ui.column().classes("flex-1"):
                    ui.label(notification.title).classes("font-semibold text-gray-800")
                    ui.label(notification.message).classes("text-sm text-gray-600")
                    
                    # Время уведомления
                    time_str = notification.timestamp.strftime("%d.%m.%Y %H:%M:%S")
                    ui.label(time_str).classes("text-xs text-gray-400 mt-1")
                
                # Кнопка закрытия
                ui.button(icon="close", size="sm", color="gray").classes("mt-1").on(
                    "click", lambda n=notification: self._remove_notification(n)
                )
    
    def _remove_notification(self, notification: Notification):
        """Удаление конкретного уведомления"""
        if notification in self.notification_manager.notifications:
            self.notification_manager.notifications.remove(notification)
            self._update_badge()
    
    def clear_all_notifications(self, dialog):
        """Очистка всех уведомлений"""
        self.notification_manager.clear_notifications()
        self._update_badge()
        dialog.close()
        ui.notify("Все уведомления очищены", type="info")
    
    def _update_badge(self):
        """Обновление бейджа с количеством уведомлений"""
        self.notification_count = len(self.notification_manager.notifications)
        if self.notification_badge:
            self.notification_badge.text = str(self.notification_count)
            if self.notification_count == 0:
                self.notification_badge.visible = False
            else:
                self.notification_badge.visible = True
    
    def setup_notification_handler(self):
        """Настройка обработчика уведомлений"""
        def handle_notification(notification: Notification):
            """Обработка нового уведомления"""
            self._update_badge()
            
            # Показываем всплывающее уведомление только если мы в UI контексте
            try:
                ui.notify(
                    notification.message,
                    type=notification.type,
                    position="top-right",
                    timeout=5000
                )
            except Exception as e:
                # Игнорируем ошибки UI из фонового потока
                pass
        
        # Подписываемся на уведомления
        self.notification_manager.subscribe(handle_notification)
        
        # Обновляем бейдж при инициализации
        self._update_badge()


def create_notifications_tab():
    """Создание вкладки уведомлений"""
    notification_ui = NotificationUI()
    notification_ui.setup_notification_handler()
    
    with ui.column().classes("w-full h-full overflow-y-auto p-4"):
        ui.label("🔔 Система уведомлений").classes("text-2xl font-bold text-gray-800 mb-6")
        
        # Статус системы
        with ui.card().classes("w-full p-4 mb-6"):
            ui.label("📊 Статус системы").classes("text-lg font-semibold mb-3")
            
            with ui.row().classes("items-center gap-4"):
                status_icon = ui.icon("check_circle", color="green")
                ui.label("Система уведомлений активна").classes("text-green-600")
                
                # Кнопка бейджа уведомлений
                notification_ui.create_notification_badge()
        
        # Настройки уведомлений
        with ui.card().classes("w-full p-4 mb-6"):
            ui.label("⚙️ Настройки").classes("text-lg font-semibold mb-3")
            
            with ui.row().classes("items-center gap-4"):
                ui.label("Интервал проверки алертов:")
                interval_input = ui.number("30", min=10, max=300).classes("w-20")
                ui.label("секунд")
                
                ui.button("Применить", icon="save").on("click", lambda: ui.notify(
                    f"Интервал изменен на {interval_input.value} секунд", type="info"
                ))
        
        # Тестовые уведомления
        with ui.card().classes("w-full p-4 mb-6"):
            ui.label("🧪 Тестовые уведомления").classes("text-lg font-semibold mb-3")
            
            with ui.row().classes("gap-2"):
                ui.button("Успех", color="green").on("click", lambda: 
                    notification_ui.notification_manager.create_manual_notification(
                        "✅ Тест успеха", "Это тестовое уведомление об успехе", "success"
                    )
                )
                
                ui.button("Информация", color="blue").on("click", lambda: 
                    notification_ui.notification_manager.create_manual_notification(
                        "ℹ️ Тест информации", "Это тестовое информационное уведомление", "info"
                    )
                )
                
                ui.button("Предупреждение", color="orange").on("click", lambda: 
                    notification_ui.notification_manager.create_manual_notification(
                        "⚠️ Тест предупреждения", "Это тестовое предупреждение", "warning"
                    )
                )
                
                ui.button("Ошибка", color="red").on("click", lambda: 
                    notification_ui.notification_manager.create_manual_notification(
                        "❌ Тест ошибки", "Это тестовое уведомление об ошибке", "error"
                    )
                )
        
        # Статистика
        with ui.card().classes("w-full p-4"):
            ui.label("📈 Статистика").classes("text-lg font-semibold mb-3")
            
            stats_container = ui.column().classes("w-full")
            
            def refresh_stats():
                stats_container.clear()
                with stats_container:
                    notifications = notification_ui.notification_manager.get_notifications()
                    
                    # Подсчет по типам
                    type_counts = {}
                    for notif in notifications:
                        type_counts[notif.type] = type_counts.get(notif.type, 0) + 1
                    
                    ui.label(f"Всего уведомлений: {len(notifications)}").classes("text-sm")
                    
                    for notif_type, count in type_counts.items():
                        ui.label(f"{notif_type}: {count}").classes("text-sm text-gray-600")
            
            refresh_stats()
            ui.button("🔄 Обновить", icon="refresh").on("click", refresh_stats)
    
    return notification_ui
