@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Очистка тестовых данных
echo ========================================

echo.
echo ВНИМАНИЕ: Это удалит ВСЕ данные из базы!
echo.
set /p confirm="Вы уверены? (y/N): "
if /i not "%confirm%"=="y" (
    echo Отменено
    pause
    exit /b 0
)

echo.
echo Активируем виртуальное окружение...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ОШИБКА: Виртуальное окружение не найдено!
    pause
    exit /b 1
)

echo.
echo Очищаем базу данных...
python -c "
import os
import sqlite3
from app.storage.db import DB_PATH

# Удаляем базу данных
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print('База данных удалена!')
else:
    print('База данных не найдена')

# Пересоздаем пустую базу
from app.storage.db import init_db
init_db()
print('Создана новая пустая база данных!')
"

echo.
echo Очистка завершена!
pause
