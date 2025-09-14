Write-Host "Committing version 1.2.5..." -ForegroundColor Green
git add .
git commit -m "v1.2.5: Fix font sizes in About dialog - headers reduced from 48px to normal size, tabs optimized, CSS styles added"
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push origin main
Write-Host "Done!" -ForegroundColor Green
