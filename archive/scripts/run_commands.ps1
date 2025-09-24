# PowerShell скрипт для выполнения команд с обходом политик
param(
    [string]$Command = "",
    [string]$WorkingDir = "."
)

# Устанавливаем рабочую директорию
Set-Location $WorkingDir

# Выполняем команду
if ($Command -ne "") {
    Write-Host "Выполняем команду: $Command" -ForegroundColor Green
    try {
        Invoke-Expression $Command
    } catch {
        Write-Host "Ошибка выполнения команды: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Использование: .\run_commands.ps1 -Command 'git status' -WorkingDir '.'" -ForegroundColor Yellow
}
