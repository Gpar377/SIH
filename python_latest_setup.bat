@echo off
echo 🐍 Python 3.13 Setup with Auto-Updates
echo.

echo [1/5] Uninstalling old Python versions...
echo Go to: Settings > Apps > Search "Python" > Uninstall ALL versions
echo Press any key when done...
pause

echo [2/5] Installing Chocolatey (for auto-updates)...
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

echo [3/5] Installing Python 3.13 via Chocolatey...
choco install python --version=3.13.0 -y

echo [4/5] Setting up auto-update...
echo Creating update script...
echo choco upgrade python -y > update_python.bat
echo.

echo [5/5] Verification...
python --version
pip --version

echo.
echo ✅ Setup Complete!
echo 📋 To update Python anytime: run "update_python.bat"
echo 🔄 Or run: choco upgrade python -y
echo.
pause