from typing import Any

from nicegui import ui


class DesignSystem:
    """Современная дизайн-система для Crypto Portfolio"""

    # Цветовая палитра
    COLORS = {
        "primary": "#6366f1",  # Индиго
        "secondary": "#8b5cf6",  # Фиолетовый
        "success": "#10b981",  # Изумрудный
        "warning": "#f59e0b",  # Янтарный
        "error": "#ef4444",  # Красный
        "info": "#3b82f6",  # Синий
        "dark": "#1f2937",  # Темно-серый
        "light": "#f9fafb",  # Светло-серый
        "white": "#ffffff",  # Белый
        "black": "#000000",  # Черный
        "gray": {
            50: "#f9fafb",
            100: "#f3f4f6",
            200: "#e5e7eb",
            300: "#d1d5db",
            400: "#9ca3af",
            500: "#6b7280",
            600: "#4b5563",
            700: "#374151",
            800: "#1f2937",
            900: "#111827",
        },
    }

    # Типографика
    TYPOGRAPHY = {
        "h1": "text-4xl font-bold text-gray-900",
        "h2": "text-3xl font-semibold text-gray-800",
        "h3": "text-2xl font-medium text-gray-700",
        "h4": "text-xl font-medium text-gray-600",
        "body": "text-base text-gray-600",
        "small": "text-sm text-gray-500",
        "caption": "text-xs text-gray-400",
    }

    # Отступы
    SPACING = {
        "xs": "p-1",
        "sm": "p-2",
        "md": "p-4",
        "lg": "p-6",
        "xl": "p-8",
        "2xl": "p-12",
    }

    # Тени
    SHADOWS = {
        "sm": "shadow-sm",
        "md": "shadow-md",
        "lg": "shadow-lg",
        "xl": "shadow-xl",
        "2xl": "shadow-2xl",
    }

    # Скругления
    RADIUS = {
        "sm": "rounded-sm",
        "md": "rounded-md",
        "lg": "rounded-lg",
        "xl": "rounded-xl",
        "full": "rounded-full",
    }


def create_modern_card(
    title: str, content: Any, color: str = "white", **kwargs
) -> ui.card:
    """Создает современную карточку с градиентом"""
    gradient_colors = {
        "primary": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "success": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "warning": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "error": "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
        "info": "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
        "white": "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
    }

    with ui.card().classes("w-full transition-all duration-300 hover:shadow-lg").style(
        f'background: {gradient_colors.get(color, gradient_colors["white"])}'
    ):
        if color != "white":
            ui.label(title).classes("text-white text-xl font-semibold mb-4")
        else:
            ui.label(title).classes("text-gray-800 text-xl font-semibold mb-4")

        if hasattr(content, "__call__"):
            content()
        else:
            if color != "white":
                ui.label(str(content)).classes("text-white text-2xl font-bold")
            else:
                ui.label(str(content)).classes("text-gray-700 text-2xl font-bold")

    return ui.card


def create_modern_button(
    text: str, color: str = "primary", size: str = "md", **kwargs
) -> ui.button:
    """Создает современную кнопку с анимацией"""
    color_styles = {
        "primary": "background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white;",
        "secondary": "background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); color: white;",
        "success": "background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;",
        "warning": "background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white;",
        "error": "background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white;",
        "info": "background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white;",
    }

    size_classes = {
        "sm": "px-3 py-2 text-sm",
        "md": "px-6 py-3 text-base",
        "lg": "px-8 py-4 text-lg",
    }

    return ui.button(
        text, style=color_styles.get(color, color_styles["primary"]), **kwargs
    ).classes(
        f'{size_classes.get(size, size_classes["md"])} rounded-lg font-medium transition-all duration-200 hover:opacity-90 hover:scale-105'
    )


def create_modern_input(label: str, **kwargs) -> ui.input:
    """Создает современное поле ввода"""
    return ui.input(label, **kwargs).classes(
        "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
    )


def create_modern_table(columns: list, **kwargs) -> ui.table:
    """Создает современную таблицу"""
    return ui.table(columns=columns, **kwargs).classes(
        "w-full bg-white rounded-lg shadow-md overflow-hidden border border-gray-200"
    )


def create_sidebar() -> ui.column:
    """Создает современную боковую панель"""
    with ui.column().classes(
        "w-64 h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white p-6 shadow-xl"
    ):
        # Логотип с анимацией
        with ui.row().classes("items-center mb-8"):
            ui.icon("account_balance_wallet").classes("text-3xl text-indigo-400 mr-3")
            ui.label("Crypto Portfolio").classes("text-2xl font-bold text-indigo-400")

        # Навигация
        nav_items = [
            ("Dashboard", "dashboard", ""),
            ("Portfolio", "portfolio", "💼"),
            ("Transactions", "transactions", ""),
            ("Analytics", "analytics", "📊"),
            ("Settings", "settings", "⚙️"),
        ]

        for item, route, icon in nav_items:
            with ui.button(
                item, icon=icon, on_click=lambda r=route: ui.navigate.to(f"/{r}")
            ).classes(
                "w-full justify-start mb-2 text-left bg-transparent hover:bg-gray-700 rounded-lg transition-all duration-200"
            ):
                pass

        # Разделитель
        ui.separator().classes("my-6 bg-gray-600")

        # Быстрые действия
        ui.label("Quick Actions").classes("text-sm font-medium text-gray-400 mb-4")

        with ui.button("Add Transaction", icon="add").classes(
            "w-full justify-start mb-2 text-left bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-all duration-200"
        ):
            pass

        with ui.button("Export Data", icon="download").classes(
            "w-full justify-start mb-2 text-left bg-transparent hover:bg-gray-700 rounded-lg transition-all duration-200"
        ):
            pass

    return ui.column


def create_modern_header() -> ui.row:
    """Создает современный заголовок"""
    with ui.row().classes(
        "w-full h-16 bg-white shadow-md px-6 items-center justify-between border-b border-gray-200"
    ):
        # Логотип и название
        with ui.row().classes("items-center"):
            ui.icon("account_balance_wallet").classes("text-2xl text-indigo-600 mr-3")
            ui.label("Crypto Portfolio").classes("text-xl font-bold text-gray-800")

        # Поиск
        with ui.input("Search...").classes(
            "w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
        ):
            pass

        # Настройки и профиль
        with ui.row().classes("items-center space-x-4"):
            with ui.button("Settings", icon="settings").classes(
                "bg-transparent hover:bg-gray-100 rounded-lg transition-all duration-200"
            ):
                pass
            with ui.button("Profile", icon="person").classes(
                "bg-transparent hover:bg-gray-100 rounded-lg transition-all duration-200"
            ):
                pass

    return ui.row


def create_modern_footer() -> ui.row:
    """Создает современный подвал"""
    with ui.row().classes(
        "w-full h-12 bg-gray-100 text-gray-600 text-sm items-center justify-center border-t border-gray-200"
    ):
        ui.label("Crypto Portfolio v1.0.0 | Made with ❤️ using NiceGUI")

    return ui.row


def create_loading_spinner() -> ui.spinner:
    """Создает современный спиннер загрузки"""
    return ui.spinner("dots", size="lg", color="indigo-600")


def create_notification(message: str, type: str = "info", duration: int = 3000):
    """Создает современное уведомление"""
    color_map = {
        "success": "positive",
        "error": "negative",
        "warning": "warning",
        "info": "info",
    }

    ui.notify(message, color=color_map.get(type, "info"), timeout=duration)
