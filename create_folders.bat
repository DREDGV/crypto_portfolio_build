@echo off
SETLOCAL
cd /d %~dp0

echo Создаем необходимые папки...

if not exist data mkdir data
if not exist data\backups mkdir data\backups
if not exist data\exports mkdir data\exports

echo Папки созданы!
pause
