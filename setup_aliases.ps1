# Скрипт для настройки алиасов PowerShell
# Запустите: . .\setup_aliases.ps1

Write-Host "🔧 Настройка алиасов для Crypto Portfolio Manager..." -ForegroundColor Green

# Алиас для Git
Set-Alias git "C:\Program Files\Git\bin\git.exe"

# Алиасы для работы с проектом
function Start-Portfolio { python run_app.py }
function Start-Portfolio-Quick { python quick_start.py }
function Start-Portfolio-Dev { $env:DEV="1"; python run_app.py }
function Stop-Portfolio { python stop_app.py }
function Check-Portfolio { python check_app.py }
function Test-Portfolio { python test_app.py }

# Алиасы для Git операций
function Git-Status { git status }
function Git-Add { git add . }
function Git-Commit { param($message) git commit -m $message }
function Git-Push { git push origin master }
function Git-Pull { git pull origin master }
function Git-Log { git log --oneline -10 }

# Алиасы для работы с версиями
function Get-Version { Get-Content VERSION }
function Update-Version { python version_manager.py }

# Алиасы для тестирования
function Test-Dependencies { python -c "import nicegui, sqlmodel, httpx; print('All dependencies OK')" }
function Test-Imports { python -c "from app.main import app_info; print('App imports OK')" }

Write-Host "✅ Алиасы настроены!" -ForegroundColor Green
Write-Host ""
Write-Host "Доступные команды:" -ForegroundColor Yellow
Write-Host "  Start-Portfolio      - Запустить приложение" -ForegroundColor Cyan
Write-Host "  Start-Portfolio-Quick - Быстрый запуск" -ForegroundColor Cyan
Write-Host "  Start-Portfolio-Dev  - Запуск в режиме разработки" -ForegroundColor Cyan
Write-Host "  Stop-Portfolio       - Остановить приложение" -ForegroundColor Cyan
Write-Host "  Check-Portfolio      - Проверить статус" -ForegroundColor Cyan
Write-Host "  Test-Portfolio       - Запустить тесты" -ForegroundColor Cyan
Write-Host ""
Write-Host "Git команды:" -ForegroundColor Yellow
Write-Host "  Git-Status           - Статус репозитория" -ForegroundColor Cyan
Write-Host "  Git-Add              - Добавить изменения" -ForegroundColor Cyan
Write-Host "  Git-Commit 'message' - Сделать коммит" -ForegroundColor Cyan
Write-Host "  Git-Push             - Отправить на GitHub" -ForegroundColor Cyan
Write-Host "  Git-Pull             - Получить изменения" -ForegroundColor Cyan
Write-Host ""
Write-Host "Тестирование:" -ForegroundColor Yellow
Write-Host "  Test-Dependencies    - Проверить зависимости" -ForegroundColor Cyan
Write-Host "  Test-Imports         - Проверить импорты" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Приложение доступно по адресу: http://127.0.0.1:8080" -ForegroundColor Green
