@echo off
echo 🗑️ Uninstalling Python 3.11 and 3.12
echo.

echo [1/4] Uninstalling Python 3.11...
wmic product where "name like 'Python 3.11%%'" call uninstall /nointeractive
echo.

echo [2/4] Uninstalling Python 3.12...
wmic product where "name like 'Python 3.12%%'" call uninstall /nointeractive
echo.

echo [3/4] Cleaning up Python Launcher...
wmic product where "name like 'Python Launcher'" call uninstall /nointeractive
echo.

echo [4/4] Manual cleanup (if needed):
echo Go to: Settings > Apps > Search "Python" > Uninstall any remaining
echo.

echo ✅ Python versions removed!
echo Now install Python 3.13 from Microsoft Store
pause