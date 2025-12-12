@echo off
REM Windows batch script to set OpenAI API key and run test

echo ========================================
echo OpenAI API Key Setup
echo ========================================
echo.

REM Prompt for API key
set /p APIKEY="Enter your OpenAI API key (starts with sk-): "

REM Set the environment variable
set OPENAI_API_KEY=%APIKEY%

echo.
echo API key set for this session!
echo.
echo Running test...
echo.

REM Run the test
python test_conversation_memory.py

pause
