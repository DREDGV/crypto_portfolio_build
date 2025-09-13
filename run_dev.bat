@echo off
SETLOCAL
cd /d %~dp0
call .venv\Scripts\activate || goto :e
set DEV=1
python -m app.main
pause
exit /b 0
:e
echo Похоже, окружение ещё не создано. Сначала запусти setup_once.bat
pause
exit /b 1
