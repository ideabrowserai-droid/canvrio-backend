@echo off
echo ========================================
echo Canvrio AI Debugging Environment Setup
echo ========================================
echo.

echo Step 1: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Make sure you're in the canvrio-backend directory
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

echo.
echo Step 2: Checking if ANTHROPIC_API_KEY is set...
if "%ANTHROPIC_API_KEY%"=="" (
    echo.
    echo WARNING: ANTHROPIC_API_KEY is not set!
    echo.
    echo To get your API key:
    echo 1. Go to https://console.anthropic.com/
    echo 2. Sign in to your Anthropic account
    echo 3. Navigate to API Keys section
    echo 4. Create a new API key or copy your existing one
    echo.
    set /p api_key="Please enter your Anthropic API key: "
    set ANTHROPIC_API_KEY=!api_key!
    echo.
    echo ✓ API key set for this session
) else (
    echo ✓ ANTHROPIC_API_KEY is already set
)

echo.
echo Step 3: Testing AI debugger connection...
python -c "
import os
import anthropic
try:
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    print('✓ AI Debugger connection test successful!')
    print('✓ Ready to run simple_main.py with AI debugging!')
except Exception as e:
    print(f'✗ Connection failed: {e}')
    print('Please check your API key and try again.')
"

echo.
echo Step 4: Ready to start your backend!
echo Run this command to start your server with AI debugging:
echo.
echo    python simple_main.py
echo.
echo The AI debugger will automatically analyze any unexpected errors
echo and log insights to claude_debug.log
echo.
pause