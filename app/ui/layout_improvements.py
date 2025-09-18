"""
Улучшения макета и структуры UI для Crypto Portfolio Manager
"""

from nicegui import ui
from app.ui.design_system import DesignSystem

class ModernLayout:
    """Современный макет приложения"""
    
    def __init__(self):
        self.ds = DesignSystem()
        self.current_page = "portfolio"
    
    def create_main_layout(self):
        """Создает основной макет приложения"""
        
        # Основной контейнер
        with ui.row().classes("w-full h-screen overflow-hidden"):
            # Боковая панель (слева)
            self.create_sidebar()
            
            # Основной контент (справа)
            with ui.column().classes("flex-1 flex flex-col"):
                # Верхняя панель
                self.create_top_bar()
                
                # Область контента
                with ui.column().classes("flex-1 p-6 bg-gray-50 overflow-auto"):
                    self.create_content_area()
    
    def create_sidebar(self):
        """Создает улучшенную боковую панель"""
        with ui.column().classes(
            "w-72 h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 "
            "text-white shadow-2xl border-r border-slate-700"
        ):
            # Логотип и заголовок
            with ui.row().classes("items-center p-6 border-b border-slate-700"):
                ui.icon("account_balance_wallet").classes("text-3xl text-indigo-400 mr-3")
                with ui.column().classes("flex-1"):
                    ui.label("Crypto Portfolio").classes("text-xl font-bold text-white")
                    ui.label("v1.3.0").classes("text-sm text-slate-400")
            
            # Навигация
            with ui.column().classes("flex-1 p-4"):
                self.create_navigation()
            
            # Быстрые действия
            with ui.column().classes("p-4 border-t border-slate-700"):
                self.create_quick_actions()
    
    def create_navigation(self):
        """Создает навигационное меню"""
        nav_items = [
            ("📊", "Обзор", "overview", "Общая статистика портфеля"),
            ("💼", "Позиции", "positions", "Текущие позиции"),
            ("📝", "Сделки", "transactions", "История транзакций"),
            ("📈", "Аналитика", "analytics", "Графики и метрики"),
            ("⚙️", "Настройки", "settings", "Конфигурация"),
        ]
        
        for icon, title, route, description in nav_items:
            is_active = route == self.current_page
            bg_class = "bg-indigo-600" if is_active else "hover:bg-slate-700"
            
            with ui.button().classes(
                f"w-full justify-start p-4 mb-2 rounded-lg transition-all duration-200 {bg_class}"
            ).on_click(lambda r=route: self.navigate_to(r)):
                with ui.row().classes("items-center w-full"):
                    ui.label(icon).classes("text-xl mr-3")
                    with ui.column().classes("flex-1 text-left"):
                        ui.label(title).classes("font-medium text-white")
                        ui.label(description).classes("text-xs text-slate-400")
    
    def create_quick_actions(self):
        """Создает быстрые действия"""
        ui.label("Быстрые действия").classes("text-sm font-medium text-slate-400 mb-3")
        
        actions = [
            ("➕", "Добавить сделку", "add_transaction"),
            ("🔄", "Обновить данные", "refresh_data"),
            ("📥", "Экспорт", "export_data"),
        ]
        
        for icon, title, action in actions:
            with ui.button().classes(
                "w-full justify-start p-3 mb-2 rounded-lg bg-slate-700 hover:bg-slate-600 "
                "transition-all duration-200 text-left"
            ).on_click(lambda a=action: self.handle_quick_action(a)):
                ui.label(icon).classes("text-lg mr-3")
                ui.label(title).classes("text-sm text-white")
    
    def create_top_bar(self):
        """Создает верхнюю панель"""
        with ui.row().classes(
            "w-full h-16 bg-white shadow-sm border-b border-gray-200 px-6 "
            "items-center justify-between"
        ):
            # Заголовок страницы
            with ui.row().classes("items-center"):
                ui.label("Портфель").classes("text-2xl font-bold text-gray-800")
                ui.badge("Активен", color="green").classes("ml-3")
            
            # Поиск и фильтры
            with ui.row().classes("items-center space-x-4"):
                # Поиск
                with ui.input("Поиск...").classes(
                    "w-64 px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                ):
                    pass
                
                # Кнопки действий
                with ui.button("Фильтры", icon="filter_list").classes(
                    "bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg"
                ):
                    pass
                
                with ui.button("Обновить", icon="refresh").classes(
                    "bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
                ):
                    pass
    
    def create_content_area(self):
        """Создает область контента"""
        # Статистические карточки
        with ui.row().classes("mb-6 gap-4"):
            self.create_stat_card("Общая стоимость", "$0.00", "💰", "primary")
            self.create_stat_card("Дневной PnL", "+$0.00", "📈", "success")
            self.create_stat_card("Позиций", "0", "💼", "info")
            self.create_stat_card("Сделок", "0", "📝", "warning")
        
        # Основной контент
        with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
            ui.label("Содержимое страницы").classes("text-lg font-medium text-gray-800")
    
    def create_stat_card(self, title, value, icon, color):
        """Создает статистическую карточку"""
        color_classes = {
            "primary": "bg-gradient-to-r from-indigo-500 to-purple-600",
            "success": "bg-gradient-to-r from-green-500 to-emerald-600",
            "info": "bg-gradient-to-r from-blue-500 to-cyan-600",
            "warning": "bg-gradient-to-r from-yellow-500 to-orange-600",
        }
        
        with ui.card().classes(
            f"flex-1 p-4 text-white shadow-lg rounded-lg {color_classes.get(color, color_classes['primary'])}"
        ):
            with ui.row().classes("items-center justify-between mb-2"):
                ui.label(icon).classes("text-2xl")
                ui.label(value).classes("text-2xl font-bold")
            ui.label(title).classes("text-sm opacity-90")
    
    def navigate_to(self, route):
        """Навигация между страницами"""
        self.current_page = route
        ui.notify(f"Переход на {route}", color="info")
    
    def handle_quick_action(self, action):
        """Обработка быстрых действий"""
        actions = {
            "add_transaction": lambda: ui.notify("Добавление сделки", color="info"),
            "refresh_data": lambda: ui.notify("Обновление данных", color="success"),
            "export_data": lambda: ui.notify("Экспорт данных", color="info"),
        }
        actions.get(action, lambda: None)()


def create_modern_dialog(title, content_func, width="600px"):
    """Создает современный диалог"""
    with ui.dialog() as dialog, ui.card().classes(f"w-full max-w-{width} p-6"):
        # Заголовок
        with ui.row().classes("items-center justify-between mb-6 pb-4 border-b border-gray-200"):
            ui.label(title).classes("text-xl font-bold text-gray-800")
            with ui.button(icon="close").classes("text-gray-400 hover:text-gray-600"):
                dialog.close()
        
        # Содержимое
        content_func()
    
    return dialog


def create_modern_form_field(label, input_type="text", **kwargs):
    """Создает современное поле формы"""
    with ui.column().classes("mb-4"):
        ui.label(label).classes("text-sm font-medium text-gray-700 mb-2")
        
        if input_type == "select":
            return ui.select(**kwargs).classes(
                "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            )
        elif input_type == "textarea":
            return ui.textarea(**kwargs).classes(
                "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            )
        else:
            return ui.input(**kwargs).classes(
                "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            )


def create_modern_table(columns, rows=None, **kwargs):
    """Создает современную таблицу"""
    table = ui.table(
        columns=columns,
        rows=rows or [],
        **kwargs
    ).classes(
        "w-full bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
    )
    
    # Стилизация заголовков
    table.add_slot('header', '''
        <q-tr class="bg-gray-50">
            <q-th v-for="col in props.cols" :key="col.name" class="text-gray-700 font-medium">
                {{ col.label }}
            </q-th>
        </q-tr>
    ''')
    
    return table


def create_loading_overlay():
    """Создает оверлей загрузки"""
    with ui.column().classes(
        "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    ):
        with ui.card().classes("p-8 bg-white rounded-lg shadow-xl"):
            ui.spinner("dots", size="lg", color="indigo-600")
            ui.label("Загрузка...").classes("mt-4 text-gray-600")


def create_success_toast(message):
    """Создает уведомление об успехе"""
    ui.notify(message, color="positive", timeout=3000, position="top-right")


def create_error_toast(message):
    """Создает уведомление об ошибке"""
    ui.notify(message, color="negative", timeout=5000, position="top-right")


def create_info_toast(message):
    """Создает информационное уведомление"""
    ui.notify(message, color="info", timeout=3000, position="top-right")
