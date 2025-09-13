# Инструкция по загрузке на GitHub

## Шаг 1: Инициализация Git репозитория

Откройте командную строку или PowerShell в папке проекта и выполните:

```bash
# Инициализация git репозитория
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Crypto Portfolio Manager"
```

## Шаг 2: Создание репозитория на GitHub

1. Перейдите на [GitHub.com](https://github.com)
2. Нажмите кнопку "New repository" (зеленая кнопка)
3. Заполните форму:
   - **Repository name**: `crypto-portfolio-manager`
   - **Description**: `Веб-приложение для управления криптовалютным портфелем`
   - **Visibility**: Public (или Private, если хотите)
   - **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license" (мы уже создали эти файлы)
4. Нажмите "Create repository"

## Шаг 3: Подключение к GitHub

После создания репозитория GitHub покажет инструкции. Выполните:

```bash
# Добавление удаленного репозитория (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/crypto-portfolio-manager.git

# Переименование основной ветки в main (если нужно)
git branch -M main

# Загрузка кода на GitHub
git push -u origin main
```

## Шаг 4: Проверка

После выполнения всех команд ваш код будет доступен по адресу:
`https://github.com/YOUR_USERNAME/crypto-portfolio-manager`

## Дополнительные настройки

### Настройка Git (если еще не настроен)

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "ваш@email.com"
```

### Если возникли проблемы с аутентификацией

GitHub теперь требует Personal Access Token вместо пароля:

1. Перейдите в Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Создайте новый токен с правами `repo`
3. Используйте токен вместо пароля при push

## Альтернативный способ через GitHub Desktop

1. Скачайте [GitHub Desktop](https://desktop.github.com/)
2. Откройте проект в GitHub Desktop
3. Нажмите "Publish repository"
4. Следуйте инструкциям

## Структура файлов для GitHub

Убедитесь, что в репозитории есть следующие файлы:
- ✅ `README.md` - описание проекта
- ✅ `.gitignore` - исключения для git
- ✅ `requirements.txt` - зависимости Python
- ✅ `setup_once.bat` - скрипт установки
- ✅ `run_dev.bat` - запуск для разработки
- ✅ `run_prod.bat` - обычный запуск
- ✅ Папка `app/` с исходным кодом
