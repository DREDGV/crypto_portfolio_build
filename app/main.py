from nicegui import ui
from app.storage.db import init_db
from app.ui.pages import portfolio_page
from dotenv import load_dotenv; load_dotenv()
import os

init_db()

with ui.header().classes('items-center justify-between px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'):
    with ui.row().classes('items-center gap-3'):
        ui.icon('account_balance_wallet').classes('text-2xl')
        ui.label('Crypto Portfolio').classes('text-xl font-bold')
        ui.label('Local').classes('text-sm bg-white bg-opacity-20 px-2 py-1 rounded-full')
    
    with ui.row().classes('gap-4'):
        ui.link('📊 Портфель', '#/portfolio').classes('text-white hover:text-blue-200 px-3 py-2 rounded-lg hover:bg-white hover:bg-opacity-10 transition-colors')
        ui.link('⚙️ Настройки', '#/settings').classes('text-white hover:text-blue-200 px-3 py-2 rounded-lg hover:bg-white hover:bg-opacity-10 transition-colors')

@ui.page('/')
def index_page():
    ui.navigate.to('/portfolio')

@ui.page('/portfolio')
def portfolio():
    portfolio_page()

@ui.page('/settings')
def settings_page():
    with ui.column().classes('max-w-4xl mx-auto p-6'):
        # Заголовок
        with ui.row().classes('items-center gap-3 mb-6'):
            ui.icon('settings').classes('text-3xl text-blue-600')
            ui.label('Настройки').classes('text-3xl font-bold text-gray-800')
        
        # Карточки настроек
        with ui.grid(columns=2).classes('gap-6'):
            # Настройки валюты
            with ui.card().classes('p-6'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('attach_money').classes('text-xl text-green-600')
                    ui.label('Валюта отчётов').classes('text-lg font-semibold')
                
                ui.label('Текущая валюта: USD').classes('text-gray-600 mb-2')
                ui.label('Изменение валюты будет доступно в следующих версиях').classes('text-sm text-gray-500')
            
            # Настройки уведомлений
            with ui.card().classes('p-6'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('notifications').classes('text-xl text-orange-600')
                    ui.label('Уведомления').classes('text-lg font-semibold')
                
                ui.label('Алерты будут доступны в следующих версиях').classes('text-gray-600 mb-2')
                ui.label('Настройка уведомлений о изменениях цен и PnL').classes('text-sm text-gray-500')
            
            # Настройки экспорта
            with ui.card().classes('p-6'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('download').classes('text-xl text-purple-600')
                    ui.label('Экспорт данных').classes('text-lg font-semibold')
                
                ui.label('CSV экспорт доступен').classes('text-gray-600 mb-2')
                ui.label('Экспорт сделок и позиций в CSV формате').classes('text-sm text-gray-500')
            
            # Информация о приложении
            with ui.card().classes('p-6'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('info').classes('text-xl text-blue-600')
                    ui.label('О приложении').classes('text-lg font-semibold')
                
                ui.label('Версия: 1.0.0').classes('text-gray-600 mb-2')
                ui.label('Локальное приложение для учёта криптопортфеля').classes('text-sm text-gray-500')

DEV = os.getenv('DEV','0') == '1'
ui.run(host='127.0.0.1', port=int(os.getenv('APP_PORT','8080')), reload=DEV, show=True, title='Crypto Portfolio — Local')
