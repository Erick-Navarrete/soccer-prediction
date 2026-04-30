@echo off
REM Tableau Data Refresh Task
REM Created: 2026-04-29 19:20:32
REM Description: Automated data refresh for Tableau dashboards

cd /d "D:\Project_App\soccer-prediction"

echo Starting Tableau data refresh at %date% %time%

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

REM Run the refresh script
python tableau_refresh.py --mode scheduled

if %errorlevel% equ 0 (
    echo Tableau data refresh completed successfully
) else (
    echo Tableau data refresh failed with error code %errorlevel%
)

echo Finished at %date% %time%
