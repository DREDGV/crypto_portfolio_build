@echo off
SETLOCAL
cd /d %~dp0
python -m venv .venv || goto :e
call .venv\Scripts\activate || goto :e
python -m pip install --upgrade pip || goto :e
pip install -r requirements.txt || goto :e
echo === Готово. Запускай run_dev.bat для разработки или run_prod.bat для обычного запуска.
pause
exit /b 0
:e
echo Ошибка установки. Проверь, что Python в PATH.
pause
exit /b 1
