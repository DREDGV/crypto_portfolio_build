"""
Система уведомлений для Crypto Portfolio Manager
"""
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Callable
from dataclasses import dataclass
from app.core.services import check_price_alerts


@dataclass
class Notification:
    """Класс для представления уведомления"""
    id: str
    title: str
    message: str
    type: str  # 'success', 'info', 'warning', 'error'
    timestamp: datetime
    data: Dict = None


class NotificationManager:
    """Менеджер уведомлений"""
    
    def __init__(self):
        self.notifications: List[Notification] = []
        self.subscribers: List[Callable] = []
        self.is_running = False
        self.alert_check_thread = None
        self.last_alert_check = None
        
    def subscribe(self, callback: Callable):
        """Подписка на уведомления"""
        if callback not in self.subscribers:
            self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Отписка от уведомлений"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def add_notification(self, notification: Notification):
        """Добавление нового уведомления"""
        self.notifications.append(notification)
        self._notify_subscribers(notification)
    
    def _notify_subscribers(self, notification: Notification):
        """Уведомление всех подписчиков"""
        for callback in self.subscribers:
            try:
                callback(notification)
            except Exception as e:
                print(f"Ошибка уведомления подписчика: {e}")
    
    def get_notifications(self, limit: int = 10) -> List[Notification]:
        """Получение последних уведомлений"""
        return self.notifications[-limit:] if self.notifications else []
    
    def clear_notifications(self):
        """Очистка всех уведомлений"""
        self.notifications.clear()
    
    def start_alert_monitoring(self, check_interval: int = 30):
        """Запуск мониторинга алертов"""
        if self.is_running:
            return
            
        self.is_running = True
        self.alert_check_thread = threading.Thread(
            target=self._monitor_alerts,
            args=(check_interval,),
            daemon=True
        )
        self.alert_check_thread.start()
    
    def stop_alert_monitoring(self):
        """Остановка мониторинга алертов"""
        self.is_running = False
        if self.alert_check_thread:
            self.alert_check_thread.join(timeout=5)
    
    def _monitor_alerts(self, check_interval: int):
        """Мониторинг алертов в отдельном потоке"""
        while self.is_running:
            try:
                # Проверяем алерты
                triggered_alerts = check_price_alerts()
                
                for alert_data in triggered_alerts:
                    notification = self._create_alert_notification(alert_data)
                    self.add_notification(notification)
                
                # Ждем перед следующей проверкой
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"Ошибка мониторинга алертов: {e}")
                time.sleep(check_interval)
    
    def _create_alert_notification(self, alert_data: Dict) -> Notification:
        """Создание уведомления о сработавшем алерте"""
        coin = alert_data.get('coin', 'Unknown')
        target_price = alert_data.get('target_price', 0)
        current_price = alert_data.get('current_price', 0)
        alert_type = alert_data.get('alert_type', 'above')
        notes = alert_data.get('notes', '')
        
        # Определяем тип уведомления
        if alert_type == 'above':
            title = f"🚀 {coin} вырос!"
            message = f"{coin} достиг ${current_price:.2f} (цель: ${target_price:.2f})"
            notification_type = 'success'
        else:
            title = f"📉 {coin} упал!"
            message = f"{coin} упал до ${current_price:.2f} (цель: ${target_price:.2f})"
            notification_type = 'warning'
        
        if notes:
            message += f"\nЗаметка: {notes}"
        
        return Notification(
            id=f"alert_{alert_data.get('alert_id', 'unknown')}_{int(time.time())}",
            title=title,
            message=message,
            type=notification_type,
            timestamp=datetime.now(),
            data=alert_data
        )
    
    def create_manual_notification(self, title: str, message: str, 
                                 notification_type: str = 'info') -> Notification:
        """Создание ручного уведомления"""
        notification = Notification(
            id=f"manual_{int(time.time())}",
            title=title,
            message=message,
            type=notification_type,
            timestamp=datetime.now()
        )
        self.add_notification(notification)
        return notification


# Глобальный экземпляр менеджера уведомлений
notification_manager = NotificationManager()


def get_notification_manager() -> NotificationManager:
    """Получение глобального менеджера уведомлений"""
    return notification_manager


def start_notifications():
    """Запуск системы уведомлений"""
    notification_manager.start_alert_monitoring()


def stop_notifications():
    """Остановка системы уведомлений"""
    notification_manager.stop_alert_monitoring()


def add_notification(title: str, message: str, notification_type: str = 'info'):
    """Быстрое добавление уведомления"""
    notification_manager.create_manual_notification(title, message, notification_type)
