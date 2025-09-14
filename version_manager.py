#!/usr/bin/env python3
"""
Скрипт для управления версиями Crypto Portfolio Manager
Следует стандарту Semantic Versioning (SemVer)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Добавляем путь к модулям приложения
sys.path.append(str(Path(__file__).parent))

from app.core.version import (
    get_version,
    increment_version,
    is_valid_version,
    parse_version,
)


def update_version_file(new_version: str) -> None:
    """Обновляет файл VERSION с новой версией."""
    version_file = Path("VERSION")
    version_file.write_text(f"{new_version}\n", encoding="utf-8")
    print(f"✅ Версия обновлена в файле VERSION: {new_version}")


def update_changelog(new_version: str, changes: str) -> None:
    """Обновляет CHANGELOG.md с новой версией и изменениями."""
    changelog_file = Path("CHANGELOG.md")

    # Читаем существующий контент
    if changelog_file.exists():
        content = changelog_file.read_text(encoding="utf-8")
    else:
        content = "# История изменений\n\n"

    # Добавляем новую версию
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"""
## [{new_version}] - {today}

{changes}

"""

    # Вставляем новую запись после заголовка
    lines = content.split("\n")
    if len(lines) > 2:
        lines.insert(2, new_entry)
    else:
        lines.append(new_entry)

    changelog_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Changelog обновлен для версии {new_version}")


def show_version_info() -> None:
    """Показывает информацию о текущей версии."""
    current_version = get_version()
    major, minor, patch = parse_version(current_version)

    print("📋 ИНФОРМАЦИЯ О ВЕРСИИ")
    print("=" * 40)
    print(f"Текущая версия: {current_version}")
    print(f"Major: {major}")
    print(f"Minor: {minor}")
    print(f"Patch: {patch}")
    print(f"Валидная версия: {'✅' if is_valid_version(current_version) else '❌'}")
    print(f"Стабильная версия: {'✅' if major > 0 else '❌'}")

    # Показываем возможные следующие версии
    print("\n🔄 ВОЗМОЖНЫЕ СЛЕДУЮЩИЕ ВЕРСИИ:")
    print(f"Patch: {increment_version(current_version, 'patch')}")
    print(f"Minor: {increment_version(current_version, 'minor')}")
    print(f"Major: {increment_version(current_version, 'major')}")


def bump_version(version_type: str, changes: str = "") -> None:
    """Увеличивает версию и обновляет файлы."""
    current_version = get_version()

    if not is_valid_version(current_version):
        print(f"❌ Ошибка: Текущая версия '{current_version}' невалидна")
        return

    new_version = increment_version(current_version, version_type)

    print(f"🔄 Обновление версии: {current_version} → {new_version}")

    # Обновляем файлы
    update_version_file(new_version)

    if changes:
        update_changelog(new_version, changes)
    else:
        print("⚠️  Changelog не обновлен (не указаны изменения)")

    print(f"\n✅ Версия успешно обновлена до {new_version}")


def main():
    """Главная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Менеджер версий Crypto Portfolio Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python version_manager.py info                    # Показать информацию о версии
  python version_manager.py bump patch             # Увеличить patch версию
  python version_manager.py bump minor             # Увеличить minor версию
  python version_manager.py bump major             # Увеличить major версию
  python version_manager.py bump patch -c "Исправление бага"  # С изменениями
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Команда info
    subparsers.add_parser("info", help="Показать информацию о текущей версии")

    # Команда bump
    bump_parser = subparsers.add_parser("bump", help="Увеличить версию")
    bump_parser.add_argument(
        "type", choices=["major", "minor", "patch"], help="Тип изменения версии"
    )
    bump_parser.add_argument("-c", "--changes", help="Описание изменений для changelog")

    args = parser.parse_args()

    if args.command == "info":
        show_version_info()
    elif args.command == "bump":
        bump_version(args.type, args.changes or "")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
