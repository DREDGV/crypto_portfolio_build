"""
UI компоненты для экспорта и импорта данных
"""

from nicegui import ui
import json
from app.core.export_import import (
    export_transactions_csv, export_portfolio_json, 
    import_transactions_csv, import_portfolio_json,
    get_export_statistics, validate_csv_format
)


def create_export_import_tab():
    """Создает вкладку для экспорта и импорта данных"""
    with ui.column().classes("w-full space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto p-4"):
        ui.label("📤📥 Экспорт/Импорт данных").classes("text-2xl font-bold text-gray-800")
        
        # Статистика экспорта
        with ui.card().classes("p-4 bg-blue-50 border-l-4 border-blue-400 w-full"):
            ui.label("📊 Статистика данных").classes("text-lg font-semibold text-blue-800 mb-2")
            
            stats_container = ui.column().classes("w-full")
            
            def refresh_export_stats():
                stats = get_export_statistics()
                stats_container.clear()
                with stats_container:
                    ui.label(f"Всего транзакций: {stats['total_transactions']}").classes("text-gray-700")
                    ui.label(f"Общая стоимость: ${stats['total_value']:.2f}").classes("text-gray-700")
                    ui.label(f"Монет в портфеле: {stats['portfolio_coins']}").classes("text-gray-700")
                    ui.label(f"Активных алертов: {stats['active_alerts']}").classes("text-gray-700")
                    ui.label(f"Источников: {stats['sources_count']}").classes("text-gray-700")
            
            refresh_export_stats()
        
        # Экспорт данных
        with ui.card().classes("p-6 bg-green-50 border-l-4 border-green-400 w-full"):
            ui.label("📤 Экспорт данных").classes("text-xl font-bold text-green-800 mb-4")
            
            with ui.row().classes("w-full gap-4"):
                # Экспорт CSV
                with ui.column().classes("flex-1"):
                    ui.label("Экспорт транзакций в CSV").classes("text-md font-semibold text-gray-700 mb-2")
                    ui.label("Формат для Excel и других табличных редакторов").classes("text-sm text-gray-600 mb-3")
                    
                    def export_csv():
                        try:
                            csv_data = export_transactions_csv()
                            if csv_data:
                                # Создаем и скачиваем файл
                                ui.download(csv_data, f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
                                ui.notify("CSV файл успешно экспортирован!", type="positive")
                            else:
                                ui.notify("Нет данных для экспорта", type="warning")
                        except Exception as e:
                            ui.notify(f"Ошибка экспорта CSV: {str(e)}", type="negative")
                    
                    ui.button("📄 Экспорт CSV", icon="download", color="green").classes("w-full").on("click", export_csv)
                
                # Экспорт JSON
                with ui.column().classes("flex-1"):
                    ui.label("Полный бэкап в JSON").classes("text-md font-semibold text-gray-700 mb-2")
                    ui.label("Включает все данные портфеля").classes("text-sm text-gray-600 mb-3")
                    
                    def export_json():
                        try:
                            json_data = export_portfolio_json()
                            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
                            ui.download(json_str, f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "application/json")
                            ui.notify("JSON бэкап успешно создан!", type="positive")
                        except Exception as e:
                            ui.notify(f"Ошибка экспорта JSON: {str(e)}", type="negative")
                    
                    ui.button("💾 Экспорт JSON", icon="backup", color="blue").classes("w-full").on("click", export_json)
        
        # Импорт данных
        with ui.card().classes("p-6 bg-orange-50 border-l-4 border-orange-400 w-full"):
            ui.label("📥 Импорт данных").classes("text-xl font-bold text-orange-800 mb-4")
            
            with ui.row().classes("w-full gap-4"):
                # Импорт CSV
                with ui.column().classes("flex-1"):
                    ui.label("Импорт транзакций из CSV").classes("text-md font-semibold text-gray-700 mb-2")
                    ui.label("Загрузите CSV файл с транзакциями").classes("text-sm text-gray-600 mb-3")
                    
                    csv_upload = ui.upload(
                        on_upload=lambda e: handle_csv_upload(e),
                        auto_upload=True,
                        max_file_size=10 * 1024 * 1024  # 10MB
                    ).classes("w-full")
                
                # Импорт JSON
                with ui.column().classes("flex-1"):
                    ui.label("Восстановление из JSON бэкапа").classes("text-md font-semibold text-gray-700 mb-2")
                    ui.label("Полное восстановление портфеля").classes("text-sm text-gray-600 mb-3")
                    
                    json_upload = ui.upload(
                        on_upload=lambda e: handle_json_upload(e),
                        auto_upload=True,
                        max_file_size=50 * 1024 * 1024  # 50MB
                    ).classes("w-full")
        
        # Результаты импорта
        import_results_container = ui.column().classes("w-full")
        
        def handle_csv_upload(e):
            """Обработка загрузки CSV файла"""
            try:
                # Читаем содержимое файла
                content = e.content.read().decode('utf-8')
                
                # Валидируем формат
                validation = validate_csv_format(content)
                if not validation['valid']:
                    ui.notify(f"Ошибка валидации CSV: {'; '.join(validation['errors'])}", type="negative")
                    return
                
                # Импортируем данные
                result = import_transactions_csv(content)
                
                # Показываем результаты
                show_import_results(result, "CSV")
                
            except Exception as e:
                ui.notify(f"Ошибка обработки CSV файла: {str(e)}", type="negative")
        
        def handle_json_upload(e):
            """Обработка загрузки JSON файла"""
            try:
                # Читаем и парсим JSON
                content = e.content.read().decode('utf-8')
                json_data = json.loads(content)
                
                # Импортируем данные
                result = import_portfolio_json(json_data)
                
                # Показываем результаты
                show_import_results(result, "JSON")
                
            except json.JSONDecodeError as e:
                ui.notify(f"Ошибка парсинга JSON: {str(e)}", type="negative")
            except Exception as e:
                ui.notify(f"Ошибка обработки JSON файла: {str(e)}", type="negative")
        
        def show_import_results(result: dict, file_type: str):
            """Показывает результаты импорта"""
            import_results_container.clear()
            
            with import_results_container:
                if result['success']:
                    with ui.card().classes("p-4 bg-green-50 border-l-4 border-green-400 w-full"):
                        ui.label(f"✅ Импорт {file_type} завершен успешно!").classes("text-lg font-semibold text-green-800 mb-2")
                        
                        if file_type == "CSV":
                            ui.label(f"Импортировано транзакций: {result['imported']}").classes("text-gray-700")
                        else:  # JSON
                            ui.label(f"Импортировано транзакций: {result['imported_transactions']}").classes("text-gray-700")
                            ui.label(f"Импортировано алертов: {result['imported_alerts']}").classes("text-gray-700")
                        
                        if result.get('warnings'):
                            ui.label("Предупреждения:").classes("text-yellow-700 font-semibold mt-2")
                            for warning in result['warnings']:
                                ui.label(f"⚠️ {warning}").classes("text-yellow-600")
                        
                        # Обновляем статистику
                        refresh_export_stats()
                        ui.notify(f"Импорт {file_type} завершен успешно!", type="positive")
                else:
                    with ui.card().classes("p-4 bg-red-50 border-l-4 border-red-400 w-full"):
                        ui.label(f"❌ Ошибка импорта {file_type}").classes("text-lg font-semibold text-red-800 mb-2")
                        
                        ui.label("Ошибки:").classes("text-red-700 font-semibold")
                        for error in result['errors']:
                            ui.label(f"• {error}").classes("text-red-600")
                        
                        if result.get('warnings'):
                            ui.label("Предупреждения:").classes("text-yellow-700 font-semibold mt-2")
                            for warning in result['warnings']:
                                ui.label(f"⚠️ {warning}").classes("text-yellow-600")
                        
                        ui.notify(f"Ошибка импорта {file_type}", type="negative")
        
        # Инструкции
        with ui.card().classes("p-4 bg-gray-50 border-l-4 border-gray-400 w-full"):
            ui.label("📋 Инструкции").classes("text-lg font-semibold text-gray-800 mb-2")
            
            with ui.column().classes("space-y-2"):
                ui.label("📄 CSV формат:").classes("text-md font-semibold text-gray-700")
                ui.label("• Обязательные колонки: Монета, Количество, Цена").classes("text-sm text-gray-600")
                ui.label("• Дополнительные: Источник, Тип, Заметки").classes("text-sm text-gray-600")
                ui.label("• Тип: 'buy' или 'sell'").classes("text-sm text-gray-600")
                
                ui.label("💾 JSON формат:").classes("text-md font-semibold text-gray-700 mt-3")
                ui.label("• Полный бэкап всех данных портфеля").classes("text-sm text-gray-600")
                ui.label("• Включает транзакции, алерты, статистику").classes("text-sm text-gray-600")
                ui.label("• Используйте для полного восстановления").classes("text-sm text-gray-600")


# Импорт datetime для использования в функциях
from datetime import datetime
