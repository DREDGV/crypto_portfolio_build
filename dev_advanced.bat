@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Продвинутый режим разработки
echo ========================================

echo.
echo Активируем виртуальное окружение...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ОШИБКА: Виртуальное окружение не найдено!
    echo Сначала запустите test_setup.bat
    pause
    exit /b 1
)

echo.
echo Настройки разработки:
echo - Автоперезагрузка: ВКЛ
echo - Отладочные сообщения: ВКЛ
echo - Порт: 8080
echo - Хост: 127.0.0.1
echo.

set DEV=1
set DEBUG=1
set APP_PORT=8080
set REPORT_CURRENCY=USD

echo Запускаем приложение...
echo.
echo Доступные URL:
echo   http://127.0.0.1:8080 - основное приложение
echo   http://127.0.0.1:8080/portfolio - портфель
echo.
echo Для остановки нажмите Ctrl+C
echo.

python -m app.main
