@echo off
title Full LLM Overreliance Experiments
color 0A

echo.
echo ===============================================================================
echo           COMPREHENSIVE TOOL OVERRELIANCE EXPERIMENTS
echo ===============================================================================
echo.
echo This will run experiments across multiple configurations:
echo.
echo CONFIGURATIONS:
echo   - Baseline (no tool): 10x10 medium maze
echo   - With noisy tool: 45%%, 75%%, 100%% noise
echo   - 10 episodes per configuration
echo   - Max 100 steps per episode (n^2)
echo.
echo TOTAL: 40 episodes (4 configs x 10 episodes)
echo.
echo ESTIMATED:
echo   - Time: 1-1.5 hours
echo   - Cost: $4-6
echo.
echo OUTPUTS:
echo   - Baseline Success Rate (BSR)
echo   - Tooled Success Rate (TSR) at each noise level
echo   - Stepwise Accuracy
echo   - Blind Reliance Index (BRI)
echo   - Complete JSON results file
echo.
echo ===============================================================================
echo.
echo Press Ctrl+C now to cancel, or
pause

cd /d "%~dp0"

echo.
echo Starting experiments...
echo.

python run_full_experiments.py

echo.
echo ===============================================================================
echo Experiments complete!
echo ===============================================================================
echo.

pause
