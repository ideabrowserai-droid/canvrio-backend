@echo off
REM Windows Deployment Script for CannTech Daily Sync
REM Usage: windows_deploy.bat daily_exports\daily_sync_XXXXXX.sql

if "%~1"=="" (
    echo Usage: windows_deploy.bat sql_file
    echo Example: windows_deploy.bat daily_exports\daily_sync_20250905_145005.sql
    pause
    exit /b 1
)

set SQL_FILE=%~1

if not exist "%SQL_FILE%" (
    echo Error: SQL file %SQL_FILE% not found!
    pause
    exit /b 1
)

echo ===================================
echo CannTech Windows Deployment Script
echo ===================================
echo.
echo SQL File: %SQL_FILE%
echo Time: %date% %time%
echo.

REM Check if sqlite3 is available
sqlite3 -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: sqlite3 not found in PATH
    echo.
    echo Please install SQLite3 or use Python method:
    echo python -c "import sqlite3; exec(open('%SQL_FILE%', 'r').read().replace(';', '; cursor.execute('''').replace('cursor.execute('''')', 'cursor.execute(stmt) if stmt.strip() and not stmt.strip().startswith(\"--\") else None for stmt in ['''').replace(''' for stmt in [', '']; [cursor.execute(stmt) if stmt.strip() and not stmt.strip().startswith(\"--\") else None for stmt in '''').replace('''])', ''']); conn.commit(); conn.close()])'))"
    echo.
    echo Or follow manual deployment steps in the _DEPLOY.md file
    pause
    exit /b 1
)

echo [1/4] Backing up current database...
if exist content.db (
    copy content.db content_backup_%date:~-4%%date:~4,2%%date:~7,2%.db >nul
    echo     Backup created: content_backup_%date:~-4%%date:~4,2%%date:~7,2%.db
) else (
    echo     No existing database found
)

echo.
echo [2/4] Executing SQL import...
sqlite3 content.db < "%SQL_FILE%"
if errorlevel 1 (
    echo     ERROR: SQL import failed!
    pause
    exit /b 1
) else (
    echo     SQL import successful!
)

echo.
echo [3/4] Verifying import...
for /f %%i in ('sqlite3 content.db "SELECT COUNT(*) FROM content_feeds WHERE compliance_status='approved';"') do set APPROVED_COUNT=%%i
echo     Approved content count: %APPROVED_COUNT%

echo.
echo [4/4] Testing production API...
curl -s https://canvrio-backend.onrender.com/api/content/latest?limit=1 > api_test_result.json
if errorlevel 1 (
    echo     Warning: Could not test production API (curl not available)
    echo     Manually test: https://canvrio-backend.onrender.com/api/content/latest?limit=3
) else (
    echo     Production API test completed - check api_test_result.json
)

echo.
echo ===================================
echo DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ===================================
echo.
echo Local database now has %APPROVED_COUNT% approved items
echo.
echo Next steps:
echo 1. Upload your updated content.db to production server
echo 2. Verify frontend at https://canvrio.ca shows fresh content
echo.
pause