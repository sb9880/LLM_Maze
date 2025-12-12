@echo off
echo ========================================
echo Installing Required Python Packages
echo ========================================
echo.

cd /d "%~dp0"

echo Installing openai library...
python -m pip install openai python-dotenv

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.

pause
