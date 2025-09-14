@echo off
echo 🐍 Simple Python 3.13 Setup (Auto-Updates)
echo.

echo [1/3] Uninstalling current Python...
echo Go to: Settings > Apps > Search "Python" > Uninstall Python 3.11
pause

echo [2/3] Installing Python 3.13 from Microsoft Store (Auto-Updates)...
start ms-windows-store://pdp/?ProductId=9NCVDN91XZQP
echo.
echo Click "Install" in the Microsoft Store
echo This version auto-updates automatically!
pause

echo [3/3] Alternative: Direct Download
echo If Store doesn't work, opening python.org...
start https://www.python.org/downloads/release/python-3130/
echo Download "Windows installer (64-bit)" and check "Add to PATH"
pause

echo.
echo ✅ After installation, restart your terminal and run:
echo    python --version
echo.
pause