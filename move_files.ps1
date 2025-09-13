# Переместить все файлы из crypto_portfolio_build в корневую папку
$sourceDir = "crypto_portfolio_build"
$targetDir = "."

# Получаем все элементы из исходной папки
$items = Get-ChildItem -Path $sourceDir -Force

foreach ($item in $items) {
    $targetPath = Join-Path $targetDir $item.Name
    
    # Если файл/папка уже существует в целевой папке, удаляем его
    if (Test-Path $targetPath) {
        Remove-Item $targetPath -Recurse -Force
    }
    
    # Перемещаем элемент
    Move-Item -Path $item.FullName -Destination $targetDir -Force
    Write-Host "Перемещен: $($item.Name)"
}

Write-Host "Все файлы перемещены из crypto_portfolio_build в корневую папку"

# Удаляем пустую папку crypto_portfolio_build
if ((Get-ChildItem -Path $sourceDir -Force | Measure-Object).Count -eq 0) {
    Remove-Item $sourceDir -Force
    Write-Host "Удалена пустая папка: $sourceDir"
}
