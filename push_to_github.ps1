Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EduAlert - Pushing to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Step 1: Initializing Git repository..." -ForegroundColor Yellow
git init

Write-Host ""
Write-Host "Step 2: Adding remote repository..." -ForegroundColor Yellow
git remote add origin https://github.com/Gpar377/SIH.git

Write-Host ""
Write-Host "Step 3: Adding all files..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "Step 4: Creating commit..." -ForegroundColor Yellow
git commit -m "Complete rebrand to EduAlert: New logo, Made with ❤️ footer on ALL pages, removed copyright"

Write-Host ""
Write-Host "Step 5: Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Push completed! Check https://github.com/Gpar377/SIH" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Read-Host "Press Enter to continue..."