@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Быстрый тест приложения
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
echo Проверяем зависимости...
python -c "import nicegui, sqlmodel, httpx; print('Все зависимости установлены!')"
if %errorlevel% neq 0 (
    echo ОШИБКА: Не все зависимости установлены!
    echo Запустите test_setup.bat для установки
    pause
    exit /b 1
)

echo.
echo Тестируем импорт модулей...
python -c "
from app.core.models import Transaction, TransactionIn
from app.core.services import add_transaction, list_transactions, positions_fifo
from app.adapters.prices import get_current_price
from app.storage.db import init_db
print('Все модули импортируются успешно!')
"

echo.
echo Тестируем базу данных...
python -c "
from app.storage.db import init_db
init_db()
print('База данных инициализирована!')
"

echo.
echo Тестируем API цен...
python -c "
from app.adapters.prices import get_current_price
price = get_current_price('BTC')
if price:
    print(f'Цена BTC: ${price:,.2f}')
else:
    print('Не удалось получить цену BTC (возможно, нет интернета)')
"

echo.
echo ========================================
echo   Тест завершен! Запускаем приложение...
echo ========================================
echo.
echo Приложение будет доступно по адресу: http://127.0.0.1:8080
echo Для остановки нажмите Ctrl+C
echo.

set DEV=1
python -m app.main
