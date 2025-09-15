@echo off
echo Cleaning up repository and preparing for deployment...

REM Remove unnecessary files
if exist "*.tmp" del /q *.tmp
if exist "*.log" del /q *.log
if exist "__pycache__" rmdir /s /q __pycache__
if exist ".pytest_cache" rmdir /s /q .pytest_cache
if exist "temp" rmdir /s /q temp

REM Remove old deployment files
if exist "deploy_fixes.bat" del /q deploy_fixes.bat
if exist "deploy_lightweight.bat" del /q deploy_lightweight.bat
if exist "push_to_github.bat" del /q push_to_github.bat
if exist "push_to_github.ps1" del /q push_to_github.ps1

echo ✅ Cleaned up unnecessary files

REM Add all changes
git add .
git commit -m "🚀 Clean repository and add Railway deployment config"
git push origin main

echo.
echo ✅ Repository cleaned and pushed!
echo.
echo 🚀 Deploy on Railway:
echo 1. Go to https://railway.app
echo 2. Connect GitHub account
echo 3. Deploy from: Gpar377/SIH
echo 4. Your EduAlert will be live!
echo.
pause