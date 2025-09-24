"""
Новая страница "О программе" с удобной навигацией
"""

from nicegui import ui
from app.core.version import get_app_info
from pathlib import Path


def show_about_page():
    """Показывает страницу 'О программе' с удобной навигацией по разделам."""
    app_info = get_app_info()

    # Добавляем стили для удобного чтения
    ui.add_head_html('''
    <style>
    .about-page {
        background: #f8fafc;
        min-height: 100vh;
        padding: 0;
        margin: 0;
    }
    .about-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 0 0 10px 10px;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 5px rgba(0,0,0,0.1);
    }
    .nav-sidebar {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        min-width: 250px;
        max-width: 300px;
    }
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        border-left: 3px solid transparent;
    }
    .nav-item:hover {
        background: #f1f5f9;
        border-left-color: #667eea;
    }
    .nav-item.active {
        background: #e0e7ff;
        border-left-color: #667eea;
        font-weight: 600;
    }
    .content-area {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        flex: 1;
        margin-left: 1rem;
        overflow-y: auto;
        max-height: calc(100vh - 200px);
    }
    .content-section {
        display: none;
    }
    .content-section.active {
        display: block;
    }
    .version-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.8rem;
    }
    .tech-stack {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .tech-item {
        background: rgba(255,255,255,0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    /* Компактная типографика для контента */
    .content-text { 
        font-size: 14px; 
        line-height: 1.5; 
        color: #374151;
        max-width: none;
    }
    .content-text h1 { 
        font-size: 1.5rem; 
        margin: 1rem 0 0.5rem 0; 
        font-weight: 700; 
        color: #1f2937;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.25rem;
    }
    .content-text h2 { 
        font-size: 1.25rem; 
        margin: 0.75rem 0 0.5rem 0; 
        font-weight: 600; 
        color: #374151;
    }
    .content-text h3 { 
        font-size: 1.1rem; 
        margin: 0.5rem 0 0.25rem 0; 
        font-weight: 600; 
        color: #4b5563;
    }
    .content-text p { 
        margin: 0.5rem 0; 
        text-align: justify;
    }
    .content-text ul, .content-text ol { 
        margin: 0.5rem 0 0.5rem 1.5rem; 
    }
    .content-text li { 
        margin: 0.25rem 0; 
    }
    .content-text code { 
        background: #f3f4f6; 
        padding: 0.2rem 0.5rem; 
        border-radius: 4px; 
        font-family: 'Courier New', monospace;
    }
    .content-text pre {
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 6px;
        border-left: 3px solid #667eea;
        overflow-x: auto;
        margin: 0.5rem 0;
        font-size: 13px;
    }
    .content-text blockquote { 
        border-left: 3px solid #667eea; 
        padding-left: 0.75rem; 
        color: #6b7280; 
        margin: 0.5rem 0; 
        font-style: italic;
    }
    .content-text table { 
        border-collapse: collapse; 
        width: 100%; 
        margin: 0.5rem 0; 
        border: 1px solid #e5e7eb;
        font-size: 13px;
    }
    .content-text th, .content-text td { 
        border: 1px solid #e5e7eb; 
        padding: 0.5rem; 
        text-align: left;
    }
    .content-text th {
        background: #f9fafb;
        font-weight: 600;
    }
    </style>
    ''')

    with ui.column().classes("about-page w-full h-screen overflow-hidden"):
        # Заголовок
        with ui.column().classes("about-header w-full"):
            with ui.row().classes("items-center justify-between"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("folder", size="1.5rem").classes("text-white")
                    ui.label("Crypto Portfolio Manager").classes("text-lg font-bold text-white")
                    ui.label(f"v{app_info['version']}").classes("version-badge")
                
                with ui.row().classes("items-center gap-2"):
                    ui.label("Python + NiceGUI").classes("tech-item")
                    ui.label("SQLite + SQLModel").classes("tech-item")
                    ui.icon("info", size="1rem").classes("text-white")

        # Основной контент с боковой навигацией
        with ui.row().classes("flex-1 w-full px-4 gap-4"):
            # Боковая навигация
            with ui.column().classes("nav-sidebar"):
                ui.label("📚 Разделы").classes("text-lg font-bold mb-4 text-gray-700")
                
                # Создаем кнопки навигации
                nav_buttons = {}
                sections = [
                    ("📋 Общая информация", "general", "description"),
                    ("🕒 История изменений", "changelog", "history"), 
                    ("🏗️ Архитектура", "architecture", "schema"),
                    ("📜 Требования", "requirements", "rule"),
                    ("📋 Бэклог", "backlog", "list"),
                    ("💡 Концепция", "concept", "lightbulb"),
                    ("💡 Концепция 2", "concept2", "emoji_objects"),
                    ("🚀 Планы развития", "roadmap", "rocket_launch")
                ]
                
                for title, section_id, icon in sections:
                    btn = ui.button(title).classes("nav-item w-full justify-start")
                    nav_buttons[section_id] = btn
                
                # Кнопка "Назад"
                with ui.row().classes("mt-6 pt-4 border-t border-gray-200"):
                    ui.button("← Назад к портфелю", icon="arrow_back").classes("w-full").on_click(lambda: ui.navigate.to("/"))

            # Область контента
            with ui.column().classes("content-area"):
                # Загружаем контент для каждого раздела
                content_data = {}
                
                # Общая информация (README.md)
                try:
                    readme_path = Path(__file__).parent.parent.parent / "README.md"
                    content_data["general"] = readme_path.read_text(encoding="utf-8") if readme_path.exists() else "README.md недоступен"
                except Exception:
                    content_data["general"] = "Ошибка загрузки README.md"
                
                # Остальные разделы
                content_data["changelog"] = app_info.get("changelog", "Ченджлог недоступен")
                content_data["architecture"] = app_info.get("architecture", "Архитектура недоступна")
                content_data["requirements"] = app_info.get("requirements", "Требования недоступны")
                content_data["backlog"] = app_info.get("backlog", "Бэклог недоступен")
                content_data["concept"] = app_info.get("concept", "Концепция недоступна")
                content_data["concept2"] = app_info.get("concept2", "CONCEPT2 недоступен")
                content_data["roadmap"] = app_info.get("roadmap", "Планы развития недоступны")
                
                # Создаем контейнеры для контента
                content_containers = {}
                for title, section_id, icon in sections:
                    with ui.column().classes("content-section") as container:
                        content_containers[section_id] = container
                
                # Функция переключения разделов
                def switch_section(section_id):
                    # Убираем активный класс со всех кнопок и контейнеров
                    for btn in nav_buttons.values():
                        btn.classes(remove="active")
                    for container in content_containers.values():
                        container.classes(remove="active")
                    
                    # Добавляем активный класс к выбранным элементам
                    nav_buttons[section_id].classes(add="active")
                    content_containers[section_id].classes(add="active")
                    
                    # Очищаем и заполняем контейнер контентом
                    content_containers[section_id].clear()
                    with content_containers[section_id]:
                        ui.markdown(content_data[section_id]).classes("content-text")
                
                # Привязываем обработчики событий
                for section_id, btn in nav_buttons.items():
                    btn.on_click(lambda s=section_id: switch_section(s))
                
                # Показываем первый раздел по умолчанию
                switch_section("general")
