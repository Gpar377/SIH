@echo off
echo Deploying EduAlert to Railway...
git add .
git commit -m "Add Railway deployment config with full ML system"
git push origin main
echo.
echo ✅ Pushed to GitHub!
echo.
echo 🚀 Next steps:
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub
echo 3. Click "Deploy from GitHub repo"
echo 4. Select: Gpar377/SIH
echo 5. Railway will auto-deploy with ML libraries!
echo.
echo Your EduAlert will be live at: https://[project-name].railway.app
pause