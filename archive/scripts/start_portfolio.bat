@echo off
title Crypto Portfolio Manager
color 0A

echo.
echo ========================================
echo   🚀 Crypto Portfolio Manager
echo ========================================
echo.

REM Переходим в директорию скрипта
cd /d "%~dp0"

REM Запускаем лаунчер
echo Запускаем приложение...
python launch_app.py

echo.
echo Приложение остановлено.
pause
