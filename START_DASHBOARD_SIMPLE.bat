@echo off
title LLM Maze Dashboard
color 0A

echo.
echo ===============================================================================
echo                        LLM MAZE DASHBOARD LAUNCHER
echo ===============================================================================
echo.
echo This will start the web dashboard for running maze experiments
echo.
echo Step 1: Setting up environment...

cd /d "%~dp0\llm_maze_research"

echo Note: Make sure your OpenAI API key is set in llm_maze_research/.env
echo Current Directory: %CD%
echo.

echo Step 2: Installing required packages (this may take a moment)...
python -m pip install uvicorn fastapi python-dotenv --quiet
if errorlevel 1 (
    echo ERROR: Failed to install packages!
    echo.
    echo Please check that Python is installed correctly.
    pause
    exit /b 1
)

echo Packages: INSTALLED
echo.

echo Step 3: Starting server...
echo ===============================================================================
echo.
echo Dashboard will be available at: http://localhost:8000/dashboard
echo.
echo The server is now running. Keep this window open!
echo Press Ctrl+C to stop the server
echo.
echo ===============================================================================
echo.

timeout /t 3 /nobreak >nul
start http://localhost:8000/dashboard

python -m uvicorn api.main:app --reload --port 8000

echo.
echo ===============================================================================
echo Server stopped.
echo ===============================================================================
pause
