@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Проверка состояния проекта
echo ========================================

echo.
echo 1. Проверяем Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo   ❌ Python не найден
) else (
    echo   ✅ Python установлен
)

echo.
echo 2. Проверяем виртуальное окружение...
if exist .venv (
    echo   ✅ Виртуальное окружение существует
) else (
    echo   ❌ Виртуальное окружение не найдено
)

echo.
echo 3. Проверяем зависимости...
call .venv\Scripts\activate.bat 2>nul
if %errorlevel% neq 0 (
    echo   ❌ Не удалось активировать виртуальное окружение
) else (
    echo   ✅ Виртуальное окружение активировано
    python -c "import nicegui, sqlmodel, httpx; print('   ✅ Все зависимости установлены')" 2>nul
    if %errorlevel% neq 0 (
        echo   ❌ Не все зависимости установлены
    )
)

echo.
echo 4. Проверяем базу данных...
if exist data\portfolio.db (
    echo   ✅ База данных существует
) else (
    echo   ⚠️  База данных не найдена (будет создана при первом запуске)
)

echo.
echo 5. Проверяем тестовые данные...
call .venv\Scripts\activate.bat 2>nul
python -c "
from app.core.services import list_transactions
txs = list_transactions()
print(f'   📊 Сделок в базе: {len(txs)}')
if len(txs) > 0:
    print('   ✅ Есть тестовые данные')
else:
    print('   ⚠️  Нет тестовых данных (запустите test_setup.bat)')
" 2>nul

echo.
echo 6. Проверяем API цен...
call .venv\Scripts\activate.bat 2>nul
python -c "
from app.adapters.prices import get_current_price
price = get_current_price('BTC')
if price:
    print(f'   ✅ API цен работает (BTC: ${price:,.2f})')
else:
    print('   ⚠️  API цен недоступен (проверьте интернет)')
" 2>nul

echo.
echo ========================================
echo   Рекомендации:
echo ========================================

if not exist .venv (
    echo - Запустите test_setup.bat для первоначальной настройки
)

call .venv\Scripts\activate.bat 2>nul
python -c "
from app.core.services import list_transactions
txs = list_transactions()
if len(txs) == 0:
    print('- Запустите test_setup.bat для создания тестовых данных')
" 2>nul

echo - Используйте dev_advanced.bat для разработки
echo - Используйте test_app.bat для быстрого тестирования
echo.
pause
