# Скрипт для исправления политик выполнения PowerShell
# Запускать от имени администратора

Write-Host "🔧 Исправление политик выполнения PowerShell..." -ForegroundColor Green

# Проверяем текущую политику
$currentPolicy = Get-ExecutionPolicy
Write-Host "Текущая политика выполнения: $currentPolicy" -ForegroundColor Yellow

# Устанавливаем политику для текущего пользователя
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ Политика выполнения установлена: RemoteSigned" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка установки политики: $($_.Exception.Message)" -ForegroundColor Red
}

# Проверяем новую политику
$newPolicy = Get-ExecutionPolicy
Write-Host "Новая политика выполнения: $newPolicy" -ForegroundColor Green

# Проверяем доступность Git
try {
    $gitVersion = git --version
    Write-Host "✅ Git доступен: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git не найден в PATH" -ForegroundColor Red
    Write-Host "Установите Git с https://git-scm.com/download/win" -ForegroundColor Yellow
}

Write-Host "🎉 Настройка завершена!" -ForegroundColor Green
Write-Host "Перезапустите Cursor для применения изменений." -ForegroundColor Cyan

