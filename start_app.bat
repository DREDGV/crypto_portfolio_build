@echo off
echo 🚀 Запуск Crypto Portfolio Manager
echo ====================================

REM Остановка предыдущих процессов Python
taskkill /f /im python.exe >nul 2>&1

REM Очистка кэша Python
if exist __pycache__ rmdir /s /q __pycache__ >nul 2>&1
if exist app\__pycache__ rmdir /s /q app\__pycache__ >nul 2>&1
if exist app\core\__pycache__ rmdir /s /q app\core\__pycache__ >nul 2>&1
if exist app\ui\__pycache__ rmdir /s /q app\ui\__pycache__ >nul 2>&1
if exist app\storage\__pycache__ rmdir /s /q app\storage\__pycache__ >nul 2>&1

REM Удаление .pyc файлов
del /s /q *.pyc >nul 2>&1
del /s /q app\*.pyc >nul 2>&1
del /s /q app\core\*.pyc >nul 2>&1
del /s /q app\ui\*.pyc >nul 2>&1
del /s /q app\storage\*.pyc >nul 2>&1

echo ✅ Кэш очищен
echo ✅ Процессы остановлены
echo.

REM Запуск приложения
echo 🌐 Запуск приложения на http://localhost:8086
echo ====================================
set APP_PORT=8086
.venv\Scripts\python.exe -m app.main_step2

pause