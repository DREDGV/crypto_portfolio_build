@echo off
echo ========================================
echo   ДИАГНОСТИКА ПРИЛОЖЕНИЯ
echo ========================================

echo.
echo 1. Проверяем Python...
python --version

echo.
echo 2. Проверяем виртуальную среду...
call .venv\Scripts\activate.bat

echo.
echo 3. Проверяем установленные пакеты...
pip list | findstr nicegui
pip list | findstr pydantic

echo.
echo 4. Проверяем структуру проекта...
dir app
dir app\core
dir app\ui

echo.
echo 5. Пробуем импортировать модули...
python -c "from nicegui import ui; print('NiceGUI OK')"
python -c "from app.core.models import Transaction; print('Models OK')"
python -c "from app.core.services import add_transaction; print('Services OK')"

echo.
echo 6. Запускаем приложение...
python -m app.main

pause
