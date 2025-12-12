@echo off
title LLM Maze Experiment - With Progress Tracking
color 0A

echo.
echo ===============================================================================
echo                  LLM MAZE EXPERIMENT - WITH PROGRESS TRACKING
echo ===============================================================================
echo.
echo Configuration:
echo   - 10 episodes
echo   - 16x16 medium difficulty mazes
echo   - GPT-3.5-turbo
echo   - 30%% noise level
echo   - Conversation memory enabled
echo.
echo Expected time: 15-20 minutes (rate limits may slow it down)
echo Expected cost: ~$0.10-0.20
echo.
echo You'll now see progress like:
echo   Starting Episode 1/10
echo   Episode 1 Complete: SUCCESS or FAILED
echo.
echo Press Ctrl+C at any time to stop
echo.
echo ===============================================================================
echo.

cd /d "%~dp0"

python test_conversation_memory.py

echo.
echo ===============================================================================
echo Experiment Complete!
echo ===============================================================================
echo.
echo Check your OpenAI API usage at:
echo https://platform.openai.com/usage
echo.

pause
