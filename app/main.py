from nicegui import ui
from app.storage.db import init_db
from app.ui.pages import portfolio_page
from dotenv import load_dotenv; load_dotenv()
import os

init_db()

with ui.header().classes('items-center justify-between'):
    ui.label('Crypto Portfolio — Local').classes('text-lg font-bold')
    with ui.row():
        ui.link('Портфель', '#/portfolio')
        ui.link('Настройки', '#/settings')

@ui.page('/')
def index_page():
    ui.navigate.to('/portfolio')

@ui.page('/portfolio')
def portfolio():
    portfolio_page()

@ui.page('/settings')
def settings_page():
    ui.label('Настройки (скоро)').classes('text-md')

DEV = os.getenv('DEV','0') == '1'
ui.run(host='127.0.0.1', port=int(os.getenv('APP_PORT','8080')), reload=DEV, show=True, title='Crypto Portfolio — Local')
