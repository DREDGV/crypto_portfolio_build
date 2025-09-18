# 🔧 Ручная настройка виртуальной среды

## ✅ Что уже сделано:
- ✅ Python 3.13.7 установлен
- ✅ Виртуальная среда `.venv` создана
- ✅ Cursor настроен для работы с виртуальной средой

## 🎯 Что нужно сделать вручную:

### 1. **Активируйте виртуальную среду в Cursor:**

1. **Нажмите "Select Interpreter"** в статус-баре Cursor
2. **Выберите**: `.venv\Scripts\python.exe` (из вашего проекта)
3. **Перезапустите Cursor**

### 2. **Установите зависимости в терминале Cursor:**

Откройте терминал в Cursor (Ctrl+`) и выполните:

```bash
# Активируйте виртуальную среду
.venv\Scripts\activate.bat

# Установите зависимости по одной
python -m pip install nicegui
python -m pip install sqlmodel  
python -m pip install httpx
python -m pip install pydantic
python -m pip install python-dotenv
```

### 3. **Проверьте установку:**

```bash
python -c "import nicegui, sqlmodel, httpx; print('✅ Все зависимости установлены!')"
```

### 4. **Запустите приложение:**

```bash
python launch_app.py
```

## 🔍 Альтернативный способ:

Если возникают проблемы, используйте полный путь:

```bash
# Установка
.venv\Scripts\python.exe -m pip install nicegui sqlmodel httpx pydantic python-dotenv

# Проверка
.venv\Scripts\python.exe -c "import nicegui; print('NiceGUI OK')"

# Запуск
.venv\Scripts\python.exe launch_app.py
```

## 🎉 После установки:

1. **Cursor будет использовать виртуальную среду**
2. **Все зависимости будут изолированы**
3. **Приложение запустится без проблем**

## 🆘 Если что-то не работает:

1. **Перезапустите Cursor**
2. **Проверьте интерпретатор** (должен быть `.venv\Scripts\python.exe`)
3. **Установите зависимости заново**
4. **Используйте полный путь к Python**

Удачной настройки! 🚀
