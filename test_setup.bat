@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Настройка тестовой среды
echo ========================================

echo.
echo Проверяем Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.13 с https://python.org
    echo Убедитесь, что Python добавлен в PATH
    pause
    exit /b 1
)

echo Python найден! Создаем виртуальное окружение...

if not exist .venv (
    echo Создаем виртуальное окружение...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ОШИБКА: Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
) else (
    echo Виртуальное окружение уже существует
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
echo Обновляем pip...
python -m pip install --upgrade pip

echo.
echo Устанавливаем зависимости...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости
    pause
    exit /b 1
)

echo.
echo Создаем тестовые данные...
python -c "from app.core.services import add_transaction; from app.core.models import TransactionIn; import datetime; 
# Добавляем тестовые сделки
test_txs = [
    TransactionIn(coin='BTC', type='buy', quantity=0.1, price=45000, strategy='long', source='Binance', notes='Тестовая покупка'),
    TransactionIn(coin='BTC', type='buy', quantity=0.05, price=42000, strategy='long', source='Binance', notes='Добавка'),
    TransactionIn(coin='ETH', type='buy', quantity=1.0, price=3000, strategy='mid', source='Coinbase', notes='Средний срок'),
    TransactionIn(coin='ETH', type='buy', quantity=0.5, price=2800, strategy='mid', source='Coinbase', notes='Добавка'),
    TransactionIn(coin='SOL', type='buy', quantity=10, price=100, strategy='short', source='FTX', notes='Краткосрок'),
    TransactionIn(coin='BTC', type='sell', quantity=0.03, price=50000, strategy='long', source='Binance', notes='Частичная продажа'),
]
for tx in test_txs:
    try:
        add_transaction(tx)
        print(f'Добавлена сделка: {tx.coin} {tx.type} {tx.quantity} @ {tx.price}')
    except Exception as e:
        print(f'Ошибка добавления сделки: {e}')
print('Тестовые данные созданы!')
"

echo.
echo ========================================
echo   Готово! Теперь можно запускать:
echo ========================================
echo.
echo   run_dev.bat     - режим разработки
echo   run_prod.bat    - обычный режим
echo   test_app.bat    - быстрый тест
echo.
pause
