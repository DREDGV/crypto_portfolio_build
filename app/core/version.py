"""
Модуль для работы с версиями и ченджлогами
Следует стандарту Semantic Versioning (SemVer)
"""

import os
import re
from datetime import datetime
from pathlib import Path


def get_version() -> str:
    """Возвращает текущую версию приложения."""
    try:
        version_file = Path(__file__).parent.parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return "1.0.0"
    except Exception:
        return "1.0.0"


def get_app_name() -> str:
    """Возвращает название приложения."""
    return "Crypto Portfolio Manager"


def get_app_description() -> str:
    """Возвращает описание приложения."""
    return "Управление криптовалютным портфелем с аналитикой и отслеживанием PnL"


def get_changelog() -> str:
    """Возвращает содержимое ченджлога."""
    try:
        changelog_file = Path(__file__).parent.parent.parent / "CHANGELOG.md"
        if changelog_file.exists():
            return changelog_file.read_text(encoding="utf-8")
        return "Ченджлог недоступен"
    except Exception:
        return "Ошибка загрузки ченджлога"


def get_concept() -> str:
    """Возвращает содержимое концепции."""
    try:
        concept_file = Path(__file__).parent.parent.parent / "CONCEPT.md"
        if concept_file.exists():
            return concept_file.read_text(encoding="utf-8")
        return "Концепция недоступна"
    except Exception:
        return "Ошибка загрузки концепции"


def get_tasks() -> str:
    """Возвращает содержимое задач."""
    try:
        tasks_file = Path(__file__).parent.parent.parent / "TASKS.md"
        if tasks_file.exists():
            return tasks_file.read_text(encoding="utf-8")
        return "Задачи недоступны"
    except Exception:
        return "Ошибка загрузки задач"


def parse_version(version: str) -> tuple[int, int, int]:
    """Парсит версию в формате MAJOR.MINOR.PATCH."""
    try:
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError("Неверный формат версии")
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return (1, 0, 0)


def increment_version(version: str, version_type: str) -> str:
    """
    Увеличивает версию согласно типу изменения.

    Args:
        version: Текущая версия (например, "1.2.3")
        version_type: Тип изменения ("major", "minor", "patch")

    Returns:
        Новая версия
    """
    major, minor, patch = parse_version(version)

    if version_type == "major":
        return f"{major + 1}.0.0"
    elif version_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif version_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError("Неверный тип версии. Используйте: major, minor, patch")


def is_valid_version(version: str) -> bool:
    """Проверяет, является ли строка валидной версией SemVer."""
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def get_version_info() -> dict:
    """Возвращает детальную информацию о версии."""
    version = get_version()
    major, minor, patch = parse_version(version)

    return {
        "version": version,
        "major": major,
        "minor": minor,
        "patch": patch,
        "is_valid": is_valid_version(version),
        "is_stable": major > 0,
        "is_development": patch == 0 and minor == 0 and major == 0,
    }


def get_app_info() -> dict:
    """Возвращает полную информацию о приложении."""
    return {
        "name": get_app_name(),
        "version": get_version(),
        "description": get_app_description(),
        "changelog": get_changelog(),
        "concept": get_concept(),
        "tasks": get_tasks(),
        "version_info": get_version_info(),
    }
