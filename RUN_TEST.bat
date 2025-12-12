@echo off
echo ========================================
echo Testing OpenAI API Key
echo ========================================
echo.

cd /d "%~dp0"

echo Note: Make sure your OpenAI API key is set in llm_maze_research/.env
echo.
echo Running test...
echo.

python check_api_key.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Test passed! Running full experiment...
    echo ========================================
    echo.
    python test_conversation_memory.py
)

pause
