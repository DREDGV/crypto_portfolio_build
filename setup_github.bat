@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Настройка GitHub репозитория
echo ========================================

echo.
echo Проверяем наличие Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Git не установлен!
    echo Пожалуйста, установите Git с https://git-scm.com/
    echo После установки перезапустите этот скрипт.
    pause
    exit /b 1
)

echo Git найден! Продолжаем...

echo.
echo Инициализируем Git репозиторий...
git init
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось инициализировать Git репозиторий
    pause
    exit /b 1
)

echo.
echo Добавляем все файлы...
git add .
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось добавить файлы
    pause
    exit /b 1
)

echo.
echo Создаем первый коммит...
git commit -m "Initial commit: Crypto Portfolio Manager"
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось создать коммит
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Git репозиторий готов!
echo ========================================
echo.
echo Теперь выполните следующие шаги:
echo.
echo 1. Перейдите на https://github.com
echo 2. Нажмите "New repository"
echo 3. Название: crypto-portfolio-manager
echo 4. Описание: Веб-приложение для управления криптовалютным портфелем
echo 5. Выберите Public или Private
echo 6. НЕ добавляйте README, .gitignore или лицензию
echo 7. Нажмите "Create repository"
echo.
echo После создания репозитория выполните команды:
echo.
echo git remote add origin https://github.com/YOUR_USERNAME/crypto-portfolio-manager.git
echo git branch -M main
echo git push -u origin main
echo.
echo (Замените YOUR_USERNAME на ваш GitHub username)
echo.
pause
