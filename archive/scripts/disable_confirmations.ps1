# Отключаем подтверждения в PowerShell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser -Force
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Отключаем подтверждения для команд
$ConfirmPreference = 'None'

Write-Host "✅ Подтверждения отключены" -ForegroundColor Green
Write-Host "Теперь можно запускать приложение без остановок" -ForegroundColor Yellow
