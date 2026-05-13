"""
Tableau Scheduler Configuration

This script sets up automated scheduling for Tableau data refresh.
Compatible with Windows Task Scheduler and cron jobs.

Author: Soccer Prediction System
Date: 2026-04-29
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outputs/tableau_data/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TableauScheduler:
    """Setup and manage automated scheduling for Tableau data refresh."""

    def __init__(self, project_root=None):
        """Initialize the scheduler."""
        if project_root is None:
            # Default to current directory
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(project_root)

        self.tableau_dir = self.project_root / "outputs" / "tableau_data"
        self.tableau_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Tableau directory: {self.tableau_dir}")

    def create_windows_task_scheduler_script(self):
        """Create a Windows Task Scheduler script."""
        logger.info("Creating Windows Task Scheduler script...")

        script_content = f"""@echo off
REM Tableau Data Refresh Task
REM Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
REM Description: Automated data refresh for Tableau dashboards

cd /d "{self.project_root}"

echo Starting Tableau data refresh at %date% %time%

REM Activate virtual environment if exists
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
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
"""

        script_path = self.project_root / "refresh_tableau_data.bat"
        with open(script_path, 'w') as f:
            f.write(script_content)

        logger.info(f"Windows Task Scheduler script created: {script_path}")
        return script_path

    def create_windows_task_scheduler_xml(self):
        """Create Windows Task Scheduler XML configuration."""
        logger.info("Creating Windows Task Scheduler XML...")

        xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</Date>
    <Author>Soccer Prediction System</Author>
    <Description>Automated data refresh for Tableau soccer prediction dashboards</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-04-29T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-21-0000000000-0000000000-0000000000-1000</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{self.project_root}\\refresh_tableau_data.bat"</Command>
      <WorkingDirectory>{self.project_root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        xml_path = self.tableau_dir / "tableau_refresh_task.xml"
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(xml_content)

        logger.info(f"Windows Task Scheduler XML created: {xml_path}")
        return xml_path

    def create_cron_job_script(self):
        """Create a cron job script for Linux/Mac."""
        logger.info("Creating cron job script...")

        script_content = f"""#!/bin/bash
# Tableau Data Refresh Cron Job
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Description: Automated data refresh for Tableau dashboards

cd "{self.project_root}"

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
"""

        script_path = self.project_root / "refresh_tableau_data.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)

        # Make script executable
        script_path.chmod(0o755)

        logger.info(f"Cron job script created: {script_path}")
        return script_path

    def create_cron_entry(self):
        """Create a cron entry for scheduling."""
        logger.info("Creating cron entry...")

        # Run daily at 6 AM
        cron_entry = f"0 6 * * * {self.project_root}/refresh_tableau_data.sh >> {self.tableau_dir}/cron.log 2>&1"

        logger.info(f"Cron entry: {cron_entry}")
        return cron_entry

    def create_schedule_config(self):
        """Create a comprehensive schedule configuration file."""
        logger.info("Creating schedule configuration...")

        config = {
            "scheduler_info": {
                "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "project_root": str(self.project_root),
                "tableau_dir": str(self.tableau_dir)
            },
            "schedule_options": {
                "daily": {
                    "description": "Run once daily at 6 AM",
                    "windows_command": f"schtasks /Create /TN \"Tableau Data Refresh\" /TR \"{self.project_root}\\refresh_tableau_data.bat\" /SC DAILY /ST 06:00",
                    "cron_entry": f"0 6 * * * {self.project_root}/refresh_tableau_data.sh"
                },
                "twice_daily": {
                    "description": "Run twice daily at 6 AM and 6 PM",
                    "windows_command": f"schtasks /Create /TN \"Tableau Data Refresh\" /TR \"{self.project_root}\\refresh_tableau_data.bat\" /SC DAILY /ST 06:00",
                    "cron_entry": f"0 6,18 * * * {self.project_root}/refresh_tableau_data.sh"
                },
                "hourly": {
                    "description": "Run every hour",
                    "windows_command": f"schtasks /Create /TN \"Tableau Data Refresh\" /TR \"{self.project_root}\\refresh_tableau_data.bat\" /SC HOURLY",
                    "cron_entry": f"0 * * * * {self.project_root}/refresh_tableau_data.sh"
                }
            },
            "manual_refresh": {
                "quick": f"python tableau_refresh.py --mode quick",
                "scheduled": f"python tableau_refresh.py --mode scheduled",
                "full": f"python tableau_refresh.py --mode full"
            },
            "files_created": {
                "windows_batch": str(self.project_root / "refresh_tableau_data.bat"),
                "linux_script": str(self.project_root / "refresh_tableau_data.sh"),
                "task_xml": str(self.tableau_dir / "tableau_refresh_task.xml")
            }
        }

        config_path = self.tableau_dir / "schedule_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Schedule configuration saved: {config_path}")
        return config

    def setup_windows_scheduler(self):
        """Setup Windows Task Scheduler."""
        logger.info("Setting up Windows Task Scheduler...")

        # Create necessary files
        batch_script = self.create_windows_task_scheduler_script()
        xml_config = self.create_windows_task_scheduler_xml()

        # Instructions for manual setup
        instructions = f"""
Windows Task Scheduler Setup Instructions:

1. Open Task Scheduler:
   - Press Win+R, type 'taskschd.msc', and press Enter

2. Import the task:
   - Right-click on 'Task Scheduler Library'
   - Select 'Import Task...'
   - Browse to: {xml_config}
   - Click Open

3. Or create manually:
   - Click 'Create Basic Task'
   - Name: 'Tableau Data Refresh'
   - Trigger: Daily
   - Start: 6:00 AM
   - Action: Start a program
   - Program/script: {batch_script}
   - Start in: {self.project_root}

4. Test the task:
   - Right-click on 'Tableau Data Refresh'
   - Select 'Run'

5. Monitor:
   - Check logs in: {self.tableau_dir}/refresh.log
"""

        instructions_path = self.tableau_dir / "windows_scheduler_instructions.txt"
        with open(instructions_path, 'w') as f:
            f.write(instructions)

        logger.info(f"Windows scheduler instructions created: {instructions_path}")
        return instructions

    def setup_linux_cron(self):
        """Setup Linux cron job."""
        logger.info("Setting up Linux cron job...")

        # Create necessary files
        shell_script = self.create_cron_job_script()
        cron_entry = self.create_cron_entry()

        # Instructions for manual setup
        instructions = f"""
Linux Cron Job Setup Instructions:

1. Make the script executable (already done):
   chmod +x {shell_script}

2. Open crontab:
   crontab -e

3. Add the following line:
   {cron_entry}

4. Save and exit

5. Test the script manually:
   {shell_script}

6. Monitor logs:
   tail -f {self.tableau_dir}/cron.log

Alternative: Run once daily at 6 AM
   {cron_entry}

Alternative: Run twice daily at 6 AM and 6 PM
   0 6,18 * * * {shell_script}

Alternative: Run every hour
   0 * * * * {shell_script}
"""

        instructions_path = self.tableau_dir / "linux_cron_instructions.txt"
        with open(instructions_path, 'w') as f:
            f.write(instructions)

        logger.info(f"Linux cron instructions created: {instructions_path}")
        return instructions

    def create_monitoring_dashboard(self):
        """Create a monitoring dashboard configuration."""
        logger.info("Creating monitoring dashboard configuration...")

        monitoring_config = {
            "dashboard_name": "Tableau Data Refresh Monitor",
            "refresh_schedule": "Daily at 6:00 AM",
            "last_refresh": None,
            "next_refresh": None,
            "status": "Active",
            "metrics_to_track": [
                "refresh_success_rate",
                "data_volume",
                "prediction_count",
                "processing_time",
                "error_count"
            ],
            "alert_thresholds": {
                "max_processing_time_minutes": 30,
                "min_prediction_count": 1,
                "max_error_rate_percent": 5
            },
            "log_files": [
                str(self.tableau_dir / "refresh.log"),
                str(self.tableau_dir / "scheduler.log"),
                str(self.tableau_dir / "cron.log")
            ],
            "data_files": [
                str(self.tableau_dir / "match_predictions.csv"),
                str(self.tableau_dir / "team_rankings.csv"),
                str(self.tableau_dir / "model_performance.csv")
            ]
        }

        monitoring_path = self.tableau_dir / "monitoring_config.json"
        with open(monitoring_path, 'w') as f:
            json.dump(monitoring_config, f, indent=2)

        logger.info(f"Monitoring configuration created: {monitoring_path}")
        return monitoring_config

    def setup_all(self):
        """Setup all scheduling components."""
        logger.info("="*60)
        logger.info("TABLEAU SCHEDULER SETUP")
        logger.info("="*60)

        try:
            # Create configuration
            config = self.create_schedule_config()

            # Setup Windows scheduler
            windows_instructions = self.setup_windows_scheduler()

            # Setup Linux cron
            linux_instructions = self.setup_linux_cron()

            # Create monitoring dashboard
            monitoring_config = self.create_monitoring_dashboard()

            logger.info("="*60)
            logger.info("SCHEDULER SETUP COMPLETE")
            logger.info("="*60)
            logger.info(f"Configuration files created in: {self.tableau_dir}")
            logger.info(f"Windows instructions: {self.tableau_dir}/windows_scheduler_instructions.txt")
            logger.info(f"Linux instructions: {self.tableau_dir}/linux_cron_instructions.txt")
            logger.info()
            logger.info("Next steps:")
            logger.info("1. Review the scheduler instructions for your platform")
            logger.info("2. Set up the scheduled task/cron job")
            logger.info("3. Test the refresh manually: python tableau_refresh.py --mode quick")
            logger.info("4. Monitor logs in the tableau_data directory")

            return True

        except Exception as e:
            logger.error(f"Error during scheduler setup: {e}")
            return False


def main():
    """Main function to run scheduler setup."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Tableau Scheduler Setup'
    )
    parser.add_argument(
        '--project-root',
        type=str,
        default=None,
        help='Project root directory (default: current directory)'
    )

    args = parser.parse_args()

    # Create scheduler
    scheduler = TableauScheduler(project_root=args.project_root)

    # Setup all components
    success = scheduler.setup_all()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()