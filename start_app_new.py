import os
import sys
from nicegui import ui
from app.core.services import list_transactions
from app.storage.db import init_db
from dotenv import load_dotenv
from app.ui.pages import portfolio_page

# Инициализируем базу данных
init_db()

print("🚀 Запускаем приложение с новым дизайном...")

# Регистрируем страницы
ui.page('/')(portfolio_page)
ui.page('/portfolio')(portfolio_page)

# Запускаем на свободном порту
port = 8081  # Используем порт 8081
print(f" Приложение доступно на http://127.0.0.1:{port}")
ui.run(host='127.0.0.1', port=port, show=True, title='Crypto Portfolio — Modern UI')