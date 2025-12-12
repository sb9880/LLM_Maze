@echo off
echo ========================================
echo Running Maze Experiment with OpenAI
echo ========================================
echo.

cd /d "%~dp0"

echo Note: Make sure your OpenAI API key is set in llm_maze_research/.env
echo.
echo Running conversation memory test...
echo This will solve ONE 8x8 easy maze with GPT-3.5-turbo
echo Expected time: 30-60 seconds
echo Expected cost: ~$0.02-0.05
echo.

python test_conversation_memory.py

echo.
echo ========================================
echo Experiment Complete!
echo ========================================
echo.
echo Check your OpenAI usage at:
echo https://platform.openai.com/usage
echo.

pause
