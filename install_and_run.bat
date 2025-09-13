@echo off
echo ========================================
echo   УСТАНОВКА И ЗАПУСК ПРИЛОЖЕНИЯ
echo ========================================

echo.
echo 1. Активируем виртуальную среду...
call .venv\Scripts\activate.bat

echo.
echo 2. Устанавливаем зависимости...
pip install -r requirements.txt

echo.
echo 3. Создаем тестовые данные...
python create_test_data.py

echo.
echo 4. Запускаем приложение...
echo Приложение будет доступно по адресу: http://127.0.0.1:8080
echo Для остановки нажмите Ctrl+C
echo.
python -m app.main

pause
