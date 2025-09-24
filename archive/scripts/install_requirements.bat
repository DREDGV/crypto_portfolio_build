@echo off
echo 🔧 Установка дополнительных инструментов для разработки...
echo.

REM Проверяем Python
echo Проверяем Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python не найден! Установите Python с python.org
    pause
    exit /b 1
)

REM Устанавливаем pip
echo 📦 Обновляем pip...
python -m pip install --upgrade pip

REM Устанавливаем зависимости проекта
echo 📦 Устанавливаем зависимости проекта...
python -m pip install -r requirements.txt

REM Устанавливаем дополнительные инструменты разработки
echo 🛠️ Устанавливаем инструменты разработки...
python -m pip install black flake8 pytest ipython jupyter

REM Устанавливаем глобальные инструменты
echo 🌐 Устанавливаем глобальные инструменты...
python -m pip install --user pipenv virtualenv

echo.
echo ✅ Установка завершена!
echo.
echo Следующие шаги:
echo 1. Перезапустите Cursor
echo 2. Нажмите "Select Interpreter" в статус-баре
echo 3. Выберите Python 3.11.x
echo 4. Запустите приложение: python launch_app.py
echo.
pause
