import subprocess
import os

# Переходим в директорию проекта
os.chdir(r"C:\Users\dr-ed\Downloads\crypto_portfolio_latest_now")

# Выполняем git команды
print("Adding files...")
subprocess.run(["git", "add", "."])

print("Committing...")
subprocess.run(["git", "commit", "-m", "v1.2.5: Fix font sizes in About dialog"])

print("Pushing...")
subprocess.run(["git", "push", "origin", "main"])

print("Done!")
