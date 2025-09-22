# 🖥️ Настройка нового ПК для Crypto Portfolio Manager

## 🎯 Что нужно установить

### 1. 🐍 Python (ОБЯЗАТЕЛЬНО!)

**Проблема**: Python из Microsoft Store имеет ограничения
**Решение**: Установите полноценный Python

#### Скачивание:
1. Перейдите на https://www.python.org/downloads/
2. Скачайте **Python 3.11.x** (последняя стабильная)
3. Запустите установщик

#### Установка:
- ✅ **ВАЖНО**: Отметьте "Add Python to PATH"
- ✅ Выберите "Install for all users"
- ✅ Выберите "Customize installation"
- ✅ Отметьте все опции в "Optional Features"
- ✅ В "Advanced Options" отметьте все галочки

#### Проверка:
```bash
# Откройте новый PowerShell и проверьте:
python --version
# Должно показать: Python 3.11.x
```

### 2. 📦 Расширения для Cursor

Установите в Cursor (Ctrl+Shift+X):

#### Обязательные:
- **Python** (Microsoft) - основное расширение
- **Pylance** (Microsoft) - языковой сервер  
- **Python Debugger** (Microsoft) - отладчик

#### Рекомендуемые:
- **GitLens** - для работы с Git
- **Thunder Client** - тестирование API
- **Auto Rename Tag** - для HTML/XML
- **Bracket Pair Colorizer** - подсветка скобок
- **Material Icon Theme** - красивые иконки
- **One Dark Pro** - темная тема

### 3. ⚙️ Настройка интерпретатора

1. В Cursor нажмите **"Select Interpreter"** (оранжевая кнопка в статус-баре)
2. Выберите Python 3.11.x (НЕ из Microsoft Store)
3. Путь должен быть: `C:\Python311\python.exe` или `C:\Users\Marina\AppData\Local\Programs\Python\Python311\python.exe`

### 4. 🔧 Установка зависимостей

#### Автоматически:
```bash
# Запустите batch файл:
install_requirements.bat
```

#### Вручную:
```bash
# Обновите pip
python -m pip install --upgrade pip

# Установите зависимости проекта
python -m pip install -r requirements.txt

# Установите инструменты разработки
python -m pip install black flake8 pytest ipython jupyter
```

### 5. 🧪 Проверка установки

```bash
# Проверьте Python
python --version

# Проверьте pip
pip --version

# Проверьте зависимости
python -c "import nicegui, sqlmodel, httpx; print('Все зависимости установлены!')"

# Проверьте приложение
python -c "from app.main import app_info; print('Приложение готово!')"
```

## 🚀 Запуск приложения

После установки:

### Способ 1 (Рекомендуемый):
```bash
python launch_app.py
```

### Способ 2 (Batch файл):
```bash
start_portfolio.bat
```

### Способ 3 (Через Cursor):
1. Откройте терминал в Cursor (Ctrl+`)
2. Выполните: `python launch_app.py`
3. Браузер откроется автоматически

## 🔧 Устранение проблем

### Проблема: "Select Interpreter" в статус-баре
**Решение**: 
1. Нажмите на кнопку
2. Выберите Python 3.11.x
3. Перезапустите Cursor

### Проблема: Python не найден
**Решение**:
1. Переустановите Python с python.org
2. Обязательно отметьте "Add Python to PATH"
3. Перезапустите PowerShell

### Проблема: Модули не импортируются
**Решение**:
```bash
# Переустановите зависимости
python -m pip install -r requirements.txt --force-reinstall
```

### Проблема: Приложение не запускается
**Решение**:
1. Проверьте интерпретатор в Cursor
2. Запустите `python launch_app.py`
3. Проверьте логи в терминале

## 📋 Чек-лист установки

- [ ] Python 3.11.x установлен с python.org
- [ ] Python добавлен в PATH
- [ ] Расширения Python установлены в Cursor
- [ ] Интерпретатор выбран в Cursor
- [ ] Зависимости установлены (`pip install -r requirements.txt`)
- [ ] Приложение запускается (`python launch_app.py`)
- [ ] Браузер открывается на http://127.0.0.1:8080

## 🎉 Готово!

После выполнения всех шагов ваше приложение будет работать корректно!

**Основные команды:**
- `python launch_app.py` - запуск приложения
- `python -m pip install -r requirements.txt` - установка зависимостей
- `git status` - проверка Git
- `python -c "import nicegui; print('OK')"` - проверка Python

Удачной разработки! 🚀
