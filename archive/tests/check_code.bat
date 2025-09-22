@echo off
echo 🔍 Проверка качества кода...
echo.

echo 📋 Форматирование кода с Black...
black app/ --line-length 88 --quiet

echo 📋 Сортировка импортов с isort...
isort app/ --profile black --quiet

echo 📋 Проверка стиля кода с Flake8...
flake8 app/ --config=setup.cfg --statistics

echo.
echo ✅ Проверка завершена!
pause
