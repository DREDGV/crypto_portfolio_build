# PowerShell скрипт для запуска приложения
# Отключаем подтверждения выполнения

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

Write-Host "🚀 Запуск приложения..." -ForegroundColor Green
Write-Host ""

try {
    # Запускаем приложение
    python -m app.main
    
    Write-Host ""
    Write-Host "✅ Приложение остановлено" -ForegroundColor Green
}
catch {
    Write-Host "❌ Ошибка: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
