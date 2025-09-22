@echo off
echo 🚀 Запуск Crypto Portfolio Manager
echo ====================================

REM Останавливаем все процессы Python
taskkill /f /im python.exe >nul 2>&1

REM Ждем 2 секунды
timeout /t 2 /nobreak >nul

REM Запускаем приложение (Step 2)
set APP_PORT=8086
.venv\Scripts\python.exe -m app.main_step2

pause