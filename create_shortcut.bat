@echo off
echo Создание ярлыка на рабочем столе...

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Crypto Portfolio.lnk'); $Shortcut.TargetPath = '%CD%\start.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Crypto Portfolio Manager'; $Shortcut.Save()"

echo ✅ Ярлык создан на рабочем столе!
pause
