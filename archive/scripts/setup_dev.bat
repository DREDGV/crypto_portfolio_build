@echo off
echo 🔧 Настройка среды разработки...
echo.

echo 📦 Установка расширений Cursor...
echo Установите следующие расширения в Cursor:
echo - Python (Microsoft)
echo - Pylance (Microsoft) 
echo - Black Formatter (Microsoft)
echo - isort (Microsoft)
echo - Flake8 (Microsoft)
echo - Tailwind CSS IntelliSense (Tailwind Labs)
echo - GitLens (GitKraken)
echo - Error Lens (Alexander)
echo.

echo 📋 Установка инструментов разработки...
pip install -r requirements-dev.txt

echo.
echo ✅ Настройка завершена!
echo.
echo 🎯 Следующие шаги:
echo 1. Установите расширения в Cursor
echo 2. Перезапустите Cursor
echo 3. Начните разработку!
echo.
pause
