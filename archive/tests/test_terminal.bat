@echo off
echo 🧪 Тестирование терминала Cursor
echo ================================

echo.
echo 1. Проверка текущей директории:
cd
echo.

echo 2. Проверка Git:
git --version
echo.

echo 3. Проверка Python:
python --version
echo.

echo 4. Проверка виртуального окружения:
if exist ".venv\Scripts\activate.bat" (
    echo ✅ Виртуальное окружение найдено
    .venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано
) else (
    echo ❌ Виртуальное окружение не найдено
)
echo.

echo 5. Тест простой команды:
echo "Тест выполнен успешно!"
echo.

echo 6. Проверка Git статуса:
git status
echo.

echo ================================
echo 🎉 Тестирование завершено!
pause

