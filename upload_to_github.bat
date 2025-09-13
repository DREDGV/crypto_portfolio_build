@echo off
SETLOCAL
cd /d %~dp0

echo ========================================
echo   Загрузка на GitHub
echo ========================================

echo.
echo Введите ваш GitHub username:
set /p GITHUB_USERNAME=

if "%GITHUB_USERNAME%"=="" (
    echo ОШИБКА: Username не может быть пустым!
    pause
    exit /b 1
)

echo.
echo Подключаем к GitHub репозиторию...
git remote add origin https://github.com/%GITHUB_USERNAME%/crypto-portfolio-manager.git
if %errorlevel% neq 0 (
    echo ВНИМАНИЕ: Репозиторий уже подключен или произошла ошибка
    echo Пытаемся обновить URL...
    git remote set-url origin https://github.com/%GITHUB_USERNAME%/crypto-portfolio-manager.git
)

echo.
echo Переименовываем ветку в main...
git branch -M main

echo.
echo Загружаем код на GitHub...
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА: Не удалось загрузить код!
    echo.
    echo Возможные причины:
    echo 1. Репозиторий еще не создан на GitHub
    echo 2. Неправильный username
    echo 3. Проблемы с аутентификацией
    echo.
    echo Убедитесь, что:
    echo - Репозиторий создан на https://github.com/%GITHUB_USERNAME%/crypto-portfolio-manager
    echo - Вы авторизованы в Git (используйте Personal Access Token)
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   УСПЕШНО! Код загружен на GitHub!
echo ========================================
echo.
echo Ваш репозиторий доступен по адресу:
echo https://github.com/%GITHUB_USERNAME%/crypto-portfolio-manager
echo.
pause
