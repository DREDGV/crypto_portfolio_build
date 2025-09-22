@echo off
setlocal enabledelayedexpansion

echo 🚀 Git Operations Script
echo ========================

cd /d "%~dp0"

if "%1"=="init" (
    echo Инициализация Git репозитория...
    git init
    echo ✅ Git репозиторий инициализирован
) else if "%1"=="status" (
    echo Проверка статуса Git...
    git status
) else if "%1"=="add" (
    echo Добавление файлов в Git...
    if "%2"=="" (
        git add .
        echo ✅ Все файлы добавлены
    ) else (
        git add %2
        echo ✅ Файл %2 добавлен
    )
) else if "%1"=="commit" (
    echo Создание коммита...
    if "%2"=="" (
        git commit -m "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    ) else (
        git commit -m "%2"
    )
    echo ✅ Коммит создан
) else if "%1"=="push" (
    echo Отправка в удаленный репозиторий...
    git push
    echo ✅ Изменения отправлены
) else if "%1"=="log" (
    echo История коммитов...
    git log --oneline -10
) else (
    echo Использование:
    echo   git_operations.bat init
    echo   git_operations.bat status
    echo   git_operations.bat add [файл]
    echo   git_operations.bat commit [сообщение]
    echo   git_operations.bat push
    echo   git_operations.bat log
)

echo ========================
pause
