@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Проверка настройки приложения
echo ========================================

echo.
echo Активируем виртуальное окружение...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ОШИБКА: Виртуальное окружение не найдено!
    echo Сначала запустите quick_start.bat
    pause
    exit /b 1
)

echo.
echo Запускаем проверку...
python verify_setup.py

echo.
pause
