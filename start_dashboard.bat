@echo off
echo ========================================
echo Starting LLM Maze Dashboard
echo ========================================
echo.

cd /d "%~dp0\llm_maze_research"

echo Note: Make sure your OpenAI API key is set in llm_maze_research/.env
echo.
echo.
echo Checking dependencies...
python -m pip install uvicorn fastapi --quiet

echo.
echo Starting dashboard server...
echo.
echo ========================================
echo Dashboard URL: http://localhost:8000/dashboard
echo ========================================
echo.
echo The dashboard will open in your browser...
echo Press Ctrl+C to stop the server
echo.

start http://localhost:8000/dashboard

python -m uvicorn api.main:app --reload --port 8000

pause
