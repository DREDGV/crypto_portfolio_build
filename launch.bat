@echo off
echo ========================================
echo 🚀 Crypto Portfolio Manager - Запуск
echo ========================================

REM Останавливаем все процессы Python
echo Останавливаем предыдущие процессы...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1

REM Ждем 2 секунды
timeout /t 2 /nobreak >nul

REM Проверяем наличие виртуального окружения
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Виртуальное окружение не найдено!
    echo Создаем виртуальное окружение...
    py -3 -m venv .venv
    echo Устанавливаем зависимости...
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe -m pip install nicegui
)

REM Устанавливаем порт
set APP_PORT=8086

REM Запускаем приложение
echo Запускаем приложение на порту %APP_PORT%...
echo Откройте http://127.0.0.1:%APP_PORT% в браузере
echo ========================================

.venv\Scripts\python.exe -m app.main_step2

pause
