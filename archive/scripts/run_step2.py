import subprocess
import sys

print("🚀 Запуск Crypto Portfolio Manager - Шаг 2")
print("=" * 50)
print("✅ Новый дизайн + Полный функционал ввода")
print("✅ Автодополнение монет и бирж")
print("✅ Кнопка 'Текущая цена' из 5-6 источников")
print("✅ Улучшенные статистические карточки")
print("=" * 50)

# Проверяем Python
print(f"🐍 Python: {sys.version.split()[0]}")

# Проверяем зависимости
required_modules = ["nicegui", "sqlmodel", "httpx", "pydantic", "dotenv"]
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
        print(f"✅ {module} - OK")
    except ImportError:
        missing_modules.append(module)
        print(f"❌ {module} - НЕ УСТАНОВЛЕН")

if missing_modules:
    print(f"❌ Отсутствуют модули: {', '.join(missing_modules)}")
    print("Установите их командой:")
    print(f"pip install {' '.join(missing_modules)}")
    sys.exit(1)

# Запускаем main_step2.py
subprocess.run([sys.executable, "app/main_step2.py"])
