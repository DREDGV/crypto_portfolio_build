@echo off
echo Создание тега...
git tag -a v1.3.0 -m "Версия 1.3.0: Поддержка акций"
echo.
echo Пуш изменений...
git push origin master
echo.
echo Пуш тегов...
git push origin --tags
echo.
echo Готово!
pause

