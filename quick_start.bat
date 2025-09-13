@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Быстрый запуск приложения
echo ========================================

echo.
echo Проверяем Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.13 с https://python.org
    pause
    exit /b 1
)

echo.
echo Создаем виртуальное окружение (если нужно)...
if not exist .venv (
    echo Создаем виртуальное окружение...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ОШИБКА: Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
)

echo.
echo Активируем виртуальное окружение...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

echo.
echo Устанавливаем зависимости...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости
    pause
    exit /b 1
)

echo.
echo Создаем папки для данных...
if not exist data mkdir data
if not exist data\backups mkdir data\backups
if not exist data\exports mkdir data\exports

echo.
echo ========================================
echo   Запускаем приложение...
echo ========================================
echo.
echo Приложение будет доступно по адресу: http://127.0.0.1:8080
echo Для остановки нажмите Ctrl+C
echo.

set DEV=1
python -m app.main
