@echo off
echo 🚀 Запуск Crypto Portfolio Manager...
echo.

REM Переходим в директорию проекта
cd /d "%~dp0"

REM Запускаем приложение
echo Запускаем приложение...
python app/main.py

echo.
echo Приложение остановлено.
pause
