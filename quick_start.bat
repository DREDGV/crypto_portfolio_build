@echo off
echo 🚀 Быстрый запуск Crypto Portfolio
taskkill /f /im python.exe >nul 2>&1
set APP_PORT=8086
.venv\Scripts\python.exe -m app.main_step2
