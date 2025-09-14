@echo off
echo 🚀 Setting up GitHub repository for DTE Rajasthan System...
echo.

echo [1/5] Initializing Git repository...
git init

echo [2/5] Adding all files...
git add .

echo [3/5] Creating initial commit...
git commit -m "Initial commit: DTE Rajasthan Student Dropout Prediction System"

echo [4/5] Instructions for GitHub setup:
echo.
echo 1. Go to https://github.com/new
echo 2. Create a new repository named "dte-rajasthan-dropout-prediction"
echo 3. Copy the repository URL (e.g., https://github.com/yourusername/dte-rajasthan-dropout-prediction.git)
echo 4. Run these commands:
echo.
echo    git remote add origin YOUR_REPOSITORY_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo [5/5] Ready for GitHub! Follow the instructions above.
echo.
pause