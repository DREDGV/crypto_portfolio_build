#!/usr/bin/env python3
"""Скрипт для коммита и пуша изменений на GitHub"""

import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - ошибка")
            if result.stderr.strip():
                print(f"   {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - таймаут")
        return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def main():
    print("🚀 Начинаем коммит и пуш изменений...")
    print("=" * 50)
    
    # Получаем текущую дату
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Добавляем все файлы
    if not run_command("git add .", "Добавление файлов"):
        return False
    
    # 2. Проверяем статус
    run_command("git status", "Проверка статуса")
    
    # 3. Создаем коммит
    commit_message = f"""feat: Добавлена поддержка акций v1.3.0

🚀 НОВЫЙ ФУНКЦИОНАЛ:
- 📈 Полная поддержка акций (добавление, отслеживание, анализ)
- 🏢 Модели данных для транзакций, позиций и цен акций
- 💰 Адаптеры цен (Yahoo Finance, Alpha Vantage, заглушки)
- 🎨 UI диалог для добавления акций с полной формой
- 📊 Сервисы для работы с акциями

🎨 УЛУЧШЕНИЯ ИНТЕРФЕЙСА:
- 📱 Боковая панель с навигацией и быстрыми действиями
- 🔄 Переключение вкладок через боковую панель
- 📈 Кнопка "Акции" для быстрого доступа
- 🎯 Приоритизация важных функций

🔧 ТЕХНИЧЕСКИЕ УЛУЧШЕНИЯ:
- 📦 Модульная архитектура для акций и криптовалют
- 🔌 Унифицированные адаптеры цен
- 💾 Поддержка транзакций с акциями в БД
- 🎨 Переиспользуемые UI компоненты

📋 ПОДДЕРЖИВАЕМЫЕ АКЦИИ:
- AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, NFLX и др.

🎯 ТИПЫ ОПЕРАЦИЙ:
- Покупка, продажа, дивиденды, сплит, бонус

🌐 БИРЖИ:
- NASDAQ, NYSE, AMEX, OTC

💱 ВАЛЮТЫ:
- USD, EUR, RUB

Версия: 1.3.0
Дата: {current_date}"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Создание коммита"):
        return False
    
    # 4. Создаем тег
    if not run_command("git tag -a v1.3.0 -m 'Версия 1.3.0: Поддержка акций'", "Создание тега"):
        return False
    
    # 5. Пушим изменения
    if not run_command("git push origin main", "Пуш изменений"):
        return False
    
    # 6. Пушим теги
    if not run_command("git push origin --tags", "Пуш тегов"):
        return False
    
    print("=" * 50)
    print("🎉 ВСЕ ИЗМЕНЕНИЯ УСПЕШНО ОТПРАВЛЕНЫ НА GITHUB!")
    print("📋 Версия: 1.3.0")
    print("📅 Дата:", current_date)
    print("🔗 Репозиторий: https://github.com/your-username/crypto_portfolio_latest_now")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Процесс завершен успешно!")
    else:
        print("❌ Процесс завершен с ошибками!")
        sys.exit(1)
