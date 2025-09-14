@echo off
echo Committing version 1.2.5...
git add .
git commit -m "v1.2.5: Fix font sizes in About dialog"
echo Pushing to GitHub...
git push origin main
echo Done!
