@echo off
title LLM Debug Test
color 0A

echo.
echo ===============================================================================
echo                         DEBUG TEST - 1 Episode
echo ===============================================================================
echo.
echo This will run 1 easy episode and show LLM responses
echo Expected time: 1-2 minutes
echo.
echo ===============================================================================
echo.

cd /d "%~dp0"

python test_single_episode.py

echo.
echo ===============================================================================
echo Debug test complete!
echo ===============================================================================
echo.

pause
