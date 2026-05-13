#!/bin/bash
# Tableau Data Refresh Cron Job
# Created: 2026-04-29 19:20:32
# Description: Automated data refresh for Tableau dashboards

cd "D:\Project_App\soccer-prediction"

echo "Starting Tableau data refresh at $(date)"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Run the refresh script
python tableau_refresh.py --mode scheduled

if [ $? -eq 0 ]; then
    echo "Tableau data refresh completed successfully"
else
    echo "Tableau data refresh failed with error code $?"
fi

echo "Finished at $(date)"
