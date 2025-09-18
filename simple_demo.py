#!/usr/bin/env python3
"""
Простая демонстрация улучшений UI
"""

from nicegui import ui

def create_old_style():
    """Создает старый стиль"""
    with ui.column().classes("w-full p-4 bg-gray-100"):
        ui.label("❌ СТАРЫЙ СТИЛЬ").classes("text-2xl font-bold text-red-600 mb-4")
        
        # Старая боковая панель
        with ui.row().classes("gap-4 mb-6"):
            with ui.column().classes("w-64 h-64 bg-gray-900 text-white p-4"):
                ui.label("Portfolio Manager").classes("text-lg font-bold mb-4")
                ui.button("Dashboard").classes("w-full justify-start mb-2 bg-gray-700")
                ui.button("Portfolio").classes("w-full justify-start mb-2 bg-gray-700")
                ui.button("Transactions").classes("w-full justify-start mb-2 bg-gray-700")
                ui.button("Analytics").classes("w-full justify-start mb-2 bg-gray-700")
            
            # Старые карточки
            with ui.column().classes("flex-1 space-y-4"):
                with ui.card().classes("p-4 bg-white"):
                    ui.label("Общая стоимость").classes("text-sm text-gray-600")
                    ui.label("$0.00").classes("text-xl font-bold")
                
                with ui.card().classes("p-4 bg-white"):
                    ui.label("Дневной PnL").classes("text-sm text-gray-600")
                    ui.label("+$0.00").classes("text-xl font-bold")
                
                with ui.card().classes("p-4 bg-white"):
                    ui.label("Позиций").classes("text-sm text-gray-600")
                    ui.label("0").classes("text-xl font-bold")


def create_new_style():
    """Создает новый стиль"""
    with ui.column().classes("w-full p-4 bg-gray-50"):
        ui.label("✅ НОВЫЙ СТИЛЬ").classes("text-2xl font-bold text-green-600 mb-4")
        
        # Новая боковая панель
        with ui.row().classes("gap-4 mb-6"):
            with ui.column().classes("w-72 h-64 bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white p-4 rounded-lg shadow-xl"):
                with ui.row().classes("items-center mb-4"):
                    ui.icon("account_balance_wallet").classes("text-2xl text-indigo-400 mr-2")
                    ui.label("Portfolio Manager").classes("text-lg font-bold")
                
                with ui.button().classes("w-full justify-start p-3 mb-2 rounded-lg hover:bg-slate-700 transition-all duration-200"):
                    with ui.row().classes("items-center w-full"):
                        ui.label("📊").classes("text-lg mr-3")
                        with ui.column().classes("flex-1 text-left"):
                            ui.label("Обзор").classes("font-medium text-white")
                            ui.label("Статистика портфеля").classes("text-xs text-slate-400")
                
                with ui.button().classes("w-full justify-start p-3 mb-2 rounded-lg hover:bg-slate-700 transition-all duration-200"):
                    with ui.row().classes("items-center w-full"):
                        ui.label("💼").classes("text-lg mr-3")
                        with ui.column().classes("flex-1 text-left"):
                            ui.label("Позиции").classes("font-medium text-white")
                            ui.label("Текущие позиции").classes("text-xs text-slate-400")
            
            # Новые карточки
            with ui.column().classes("flex-1 space-y-4"):
                with ui.card().classes("p-6 text-white shadow-lg rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600"):
                    with ui.row().classes("items-center justify-between mb-3"):
                        ui.label("💰").classes("text-3xl")
                        ui.label("$12,450.00").classes("text-2xl font-bold")
                    ui.label("Общая стоимость").classes("text-sm opacity-90")
                
                with ui.card().classes("p-6 text-white shadow-lg rounded-lg bg-gradient-to-r from-green-500 to-emerald-600"):
                    with ui.row().classes("items-center justify-between mb-3"):
                        ui.label("📈").classes("text-3xl")
                        ui.label("+$245.30").classes("text-2xl font-bold")
                    ui.label("Дневной PnL").classes("text-sm opacity-90")
                
                with ui.card().classes("p-6 text-white shadow-lg rounded-lg bg-gradient-to-r from-blue-500 to-cyan-600"):
                    with ui.row().classes("items-center justify-between mb-3"):
                        ui.label("💼").classes("text-3xl")
                        ui.label("15").classes("text-2xl font-bold")
                    ui.label("Позиций").classes("text-sm opacity-90")


@ui.page("/")
def main():
    with ui.column().classes("w-full min-h-screen bg-gray-50"):
        # Заголовок
        with ui.row().classes("w-full p-6 bg-white shadow-sm border-b border-gray-200"):
            ui.label("🎨 Сравнение дизайнов Crypto Portfolio Manager").classes("text-3xl font-bold text-gray-800")
        
        # Сравнение
        with ui.column().classes("w-full p-6 space-y-8"):
            create_old_style()
            create_new_style()
            
            # Заключение
            with ui.card().classes("w-full p-6 bg-white shadow-sm rounded-lg"):
                ui.label("🎯 Заключение").classes("text-2xl font-bold text-gray-800 mb-4")
                with ui.column().classes("space-y-2 text-gray-700"):
                    ui.label("✅ Новый дизайн более современный и привлекательный")
                    ui.label("✅ Лучшая навигация с иконками и описаниями")
                    ui.label("✅ Градиентные карточки выглядят профессионально")
                    ui.label("✅ Улучшенная читаемость и визуальная иерархия")
                    ui.label("✅ Плавные анимации и hover-эффекты")


if __name__ == "__main__":
    print("🎨 Простая демонстрация улучшений UI")
    print("=" * 50)
    print("Откройте http://localhost:8082 в браузере")
    print("=" * 50)
    
    ui.run(
        host="127.0.0.1",
        port=8082,
        reload=False,
        show=True,
        title="UI Comparison Demo",
        favicon="🎨",
    )
