@echo off
echo 🔧 Настройка алиасов для Crypto Portfolio Manager...

REM Алиас для Git
set "GIT_PATH=C:\Program Files\Git\bin\git.exe"

echo ✅ Алиасы настроены!
echo.
echo Доступные команды:
echo   start_portfolio.bat      - Запустить приложение
echo   quick_start.bat          - Быстрый запуск
echo   stop_app.bat             - Остановить приложение
echo   check_app.bat            - Проверить статус
echo   test_app.bat             - Запустить тесты
echo.
echo Git команды:
echo   git status               - Статус репозитория
echo   git add .                - Добавить изменения
echo   git commit -m "message"  - Сделать коммит
echo   git push origin master   - Отправить на GitHub
echo   git pull origin master   - Получить изменения
echo.
echo 🌐 Приложение доступно по адресу: http://127.0.0.1:8080
echo.
pause
