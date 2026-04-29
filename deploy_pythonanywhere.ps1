# Automated Deployment Script for PythonAnywhere (Windows PowerShell)
# This script handles all deployment steps with auto-accept prompts

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Automated Deployment to PythonAnywhere..." -ForegroundColor Green
Write-Host ""

# Configuration
$APP_NAME = "soccer-predictions"
$PYTHON_VERSION = "python39"
$DOMAIN = "yourname.pythonanywhere.com"  # Change this to your username

Write-Host "✓ Deployment script started" -ForegroundColor Green
Write-Host ""

# Step 1: Create virtual environment (auto-accept)
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv --clear
Write-Host "✓ Virtual environment created" -ForegroundColor Green
Write-Host ""

# Step 2: Activate virtual environment
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Step 3: Upgrade pip (auto-accept)
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
pip install --upgrade pip --quiet --yes
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Step 4: Install dependencies (auto-accept)
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet --yes
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 5: Create necessary directories
Write-Host "Step 5: Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "outputs" | Out-Null
New-Item -ItemType Directory -Force -Path "outputs\predictions" | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Step 6: Set environment variables
Write-Host "Step 6: Setting environment variables..." -ForegroundColor Yellow
$env:FLASK_APP = "web/app.py"
$env:FLASK_ENV = "production"
Write-Host "✓ Environment variables set" -ForegroundColor Green
Write-Host ""

# Step 7: Test the application
Write-Host "Step 7: Testing application..." -ForegroundColor Yellow
python -c "from web.app import app; print('✓ Application imports successfully')"
Write-Host "✓ Application tested" -ForegroundColor Green
Write-Host ""

# Step 8: Create WSGI file
Write-Host "Step 8: Creating WSGI configuration..." -ForegroundColor Yellow
$wsgiContent = @"
import sys
import os

# Add project directory to Python path
project_home = '/home/' + os.path.split(os.getcwd())[0].split('/')[-1]
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Add web directory to path
web_dir = os.path.join(project_home, 'web')
if web_dir not in sys.path:
    sys.path = [web_dir] + sys.path

# Import Flask app
from app import app as application

# Make sure the app is in production mode
application.config['DEBUG'] = False
"@

Set-Content -Path "wsgi.py" -Value $wsgiContent
Write-Host "✓ WSGI configuration created" -ForegroundColor Green
Write-Host ""

# Step 9: Create startup script
Write-Host "Step 9: Creating startup script..." -ForegroundColor Yellow
$startupContent = @"
#!/bin/bash
source venv/bin/activate
export FLASK_APP=web/app.py
export FLASK_ENV=production
gunicorn --workers=3 --bind=0.0.0.0:5000 wsgi:application
"@

Set-Content -Path "start.sh" -Value $startupContent
Write-Host "✓ Startup script created" -ForegroundColor Green
Write-Host ""

# Step 10: Create requirements file for PythonAnywhere
Write-Host "Step 10: Creating PythonAnywhere requirements..." -ForegroundColor Yellow
$requirementsContent = @"
flask>=3.0.0
gunicorn>=21.0.0
pandas>=2.1.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
"@

Set-Content -Path "requirements_pa.txt" -Value $requirementsContent
Write-Host "✓ PythonAnywhere requirements created" -ForegroundColor Green
Write-Host ""

# Step 11: Create deployment info file
Write-Host "Step 11: Creating deployment info..." -ForegroundColor Yellow
$deploymentInfo = @"
PythonAnywhere Deployment Information
========================================

Deployment Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
App Name: $APP_NAME
Python Version: $PYTHON_VERSION
Domain: $DOMAIN

Next Steps:
-----------
1. Go to PythonAnywhere Web tab
2. Upload this entire folder
3. Create a new web app with Flask framework
4. Use the WSGI configuration file: wsgi.py
5. Set working directory to: /home/yourname/$APP_NAME
6. Install requirements: pip install -r requirements_pa.txt
7. Click "Reload" button

Your site will be live at: https://$DOMAIN

Files Created:
-------------
- wsgi.py (WSGI configuration)
- start.sh (Startup script)
- requirements_pa.txt (PythonAnywhere requirements)
- DEPLOYMENT_INFO.txt (This file)

Auto-accept flags used:
-----------------------
- pip install --yes
- python -m venv --clear
- All prompts automatically accepted

Troubleshooting:
---------------
If you see "Module not found" errors:
1. Make sure virtual environment is activated
2. Run: pip install -r requirements_pa.txt

If the site doesn't load:
1. Check web app error logs
2. Verify WSGI file path
3. Click "Reload" button

For more help, see: CLOUD_HOSTING_GUIDE.md
"@

Set-Content -Path "DEPLOYMENT_INFO.txt" -Value $deploymentInfo
Write-Host "✓ Deployment info created" -ForegroundColor Green
Write-Host ""

# Final summary
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ DEPLOYMENT PREPARATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files created for deployment:"
Write-Host "  - wsgi.py (WSGI configuration)"
Write-Host "  - start.sh (Startup script)"
Write-Host "  - requirements_pa.txt (PythonAnywhere requirements)"
Write-Host "  - DEPLOYMENT_INFO.txt (Deployment information)"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Upload this folder to PythonAnywhere"
Write-Host "  2. Create a new Flask web app"
Write-Host "  3. Use wsgi.py as WSGI configuration"
Write-Host "  4. Install requirements: pip install -r requirements_pa.txt"
Write-Host "  5. Click 'Reload' button"
Write-Host ""
Write-Host "All prompts were auto-accepted!" -ForegroundColor Green
Write-Host ""
Write-Host "For detailed instructions, see: CLOUD_HOSTING_GUIDE.md"
