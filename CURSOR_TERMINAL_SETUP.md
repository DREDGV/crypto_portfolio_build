# 🔧 Настройка терминала Cursor

## Проблема
Команды в терминале Cursor отменяются или не выполняются.

## Решения

### 1. 📁 Конфигурационные файлы созданы
- `.vscode/settings.json` - настройки для VS Code/Cursor
- `.cursor/settings.json` - настройки для Cursor
- `fix_powershell_policies.ps1` - скрипт исправления PowerShell
- `test_terminal.bat` - тест терминала

### 2. 🔄 Перезапуск Cursor
1. Закройте Cursor полностью
2. Откройте Cursor заново
3. Откройте терминал (Ctrl+`)

### 3. ⚙️ Ручная настройка профиля терминала
1. В Cursor: `Ctrl+Shift+P`
2. Введите: "Terminal: Select Default Profile"
3. Выберите "Command Prompt" вместо PowerShell

### 4. 🛠️ Исправление политик PowerShell (если нужно)
1. Откройте PowerShell от имени администратора
2. Выполните: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force`
3. Перезапустите Cursor

### 5. 🧪 Тестирование
Запустите `test_terminal.bat` для проверки работы терминала.

## Альтернативные решения

### Вариант A: Использовать Command Prompt
- В терминале Cursor выберите профиль "Command Prompt"
- Команды должны выполняться без проблем

### Вариант B: Использовать Git Bash
- Установите Git for Windows
- Выберите профиль "Git Bash" в терминале

### Вариант C: Внешний терминал
- Используйте отдельное окно cmd или PowerShell
- Выполняйте команды там

## Проверка работы
После настройки выполните:
```bash
git status
python --version
echo "Тест"
```

Если команды выполняются без ошибок - настройка успешна!

