#!/usr/bin/env python3
"""Запуск теста через subprocess"""

import subprocess
import sys

try:
    result = subprocess.run(
        [sys.executable, "test_import.py"], capture_output=True, text=True, timeout=10
    )
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print(f"Exit code: {result.returncode}")
except Exception as e:
    print(f"Ошибка запуска: {e}")
