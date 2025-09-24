@echo off
setlocal enabledelayedexpansion

echo 🔧 Выполнение команды: %*
echo ================================

cd /d "%~dp0"

if "%1"=="git" (
    echo Выполняем Git команду...
    git %2 %3 %4 %5 %6 %7 %8 %9
) else if "%1"=="python" (
    echo Выполняем Python команду...
    python %2 %3 %4 %5 %6 %7 %8 %9
) else if "%1"=="pip" (
    echo Выполняем pip команду...
    pip %2 %3 %4 %5 %6 %7 %8 %9
) else (
    echo Выполняем общую команду...
    %*
)

echo ================================
echo ✅ Команда выполнена
pause
