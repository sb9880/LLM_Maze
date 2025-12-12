@echo off
title LLM Maze Test
color 0A

echo.
echo ===============================================================================
echo                     TESTING CONVERSATION MEMORY FIX
echo ===============================================================================
echo.
echo This will run 10 episodes on 16x16 medium mazes with GPT-3.5-turbo
echo Expected time: 5-10 minutes
echo Expected cost: ~$0.10-0.20
echo.
echo ===============================================================================
echo.

cd /d "%~dp0"

echo Starting test...
echo.

python test_conversation_memory.py

echo.
echo ===============================================================================
echo Test Complete!
echo ===============================================================================
echo.
echo Check your OpenAI API usage at:
echo https://platform.openai.com/usage
echo.

pause
