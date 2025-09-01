@echo off
REM Canvrio Automated Content Refresh
REM Runs content aggregation every 4 hours during business days

echo Starting Canvrio content refresh...
echo %date% %time%

REM Navigate to project directory
cd "C:\Users\kg\Desktop\canvrio-backend"

REM Activate virtual environment
call venv312\Scripts\activate.bat

REM Run content aggregation
python content_aggregator.py

REM Log completion
echo Content refresh completed at %date% %time%
echo.

REM Keep window open for debugging (remove in production)
pause