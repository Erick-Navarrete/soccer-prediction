#!/bin/bash
# Automated Deployment Script for PythonAnywhere
# This script handles all deployment steps with auto-accept prompts

set -e  # Exit on error

echo "🚀 Starting Automated Deployment to PythonAnywhere..."
echo ""

# Configuration
APP_NAME="soccer-predictions"
PYTHON_VERSION="python39"
DOMAIN="yourname.pythonanywhere.com"  # Change this to your username

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}✓${NC} Deployment script started"
echo ""

# Step 1: Create virtual environment (auto-accept)
echo -e "${YELLOW}Step 1: Creating virtual environment...${NC}"
python3 -m venv venv --clear
echo -e "${GREEN}✓${NC} Virtual environment created"
echo ""

# Step 2: Activate virtual environment
echo -e "${YELLOW}Step 2: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Step 3: Upgrade pip (auto-accept)
echo -e "${YELLOW}Step 3: Upgrading pip...${NC}"
pip install --upgrade pip --quiet --yes
echo -e "${GREEN}✓${NC} pip upgraded"
echo ""

# Step 4: Install dependencies (auto-accept)
echo -e "${YELLOW}Step 4: Installing dependencies...${NC}"
pip install -r requirements.txt --quiet --yes
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Step 5: Create necessary directories
echo -e "${YELLOW}Step 5: Creating directories...${NC}"
mkdir -p outputs
mkdir -p outputs/predictions
echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Step 6: Set environment variables
echo -e "${YELLOW}Step 6: Setting environment variables...${NC}"
export FLASK_APP=web/app.py
export FLASK_ENV=production
echo -e "${GREEN}✓${NC} Environment variables set"
echo ""

# Step 7: Test the application
echo -e "${YELLOW}Step 7: Testing application...${NC}"
python -c "from web.app import app; print('✓ Application imports successfully')"
echo -e "${GREEN}✓${NC} Application tested"
echo ""

# Step 8: Create WSGI file
echo -e "${YELLOW}Step 8: Creating WSGI configuration...${NC}"
cat > wsgi.py << 'EOF'
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
EOF
echo -e "${GREEN}✓${NC} WSGI configuration created"
echo ""

# Step 9: Create startup script
echo -e "${YELLOW}Step 9: Creating startup script...${NC}"
cat > start.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
export FLASK_APP=web/app.py
export FLASK_ENV=production
gunicorn --workers=3 --bind=0.0.0.0:5000 wsgi:application
EOF
chmod +x start.sh
echo -e "${GREEN}✓${NC} Startup script created"
echo ""

# Step 10: Create requirements file for PythonAnywhere
echo -e "${YELLOW}Step 10: Creating PythonAnywhere requirements...${NC}"
cat > requirements_pa.txt << 'EOF'
flask>=3.0.0
gunicorn>=21.0.0
pandas>=2.1.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
EOF
echo -e "${GREEN}✓${NC} PythonAnywhere requirements created"
echo ""

# Step 11: Create deployment info file
echo -e "${YELLOW}Step 11: Creating deployment info...${NC}"
cat > DEPLOYMENT_INFO.txt << EOF
PythonAnywhere Deployment Information
========================================

Deployment Date: $(date)
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
- python3 -m venv --clear
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
EOF
echo -e "${GREEN}✓${NC} Deployment info created"
echo ""

# Final summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ DEPLOYMENT PREPARATION COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Files created for deployment:"
echo "  - wsgi.py (WSGI configuration)"
echo "  - start.sh (Startup script)"
echo "  - requirements_pa.txt (PythonAnywhere requirements)"
echo "  - DEPLOYMENT_INFO.txt (Deployment information)"
echo ""
echo "Next steps:"
echo "  1. Upload this folder to PythonAnywhere"
echo "  2. Create a new Flask web app"
echo "  3. Use wsgi.py as WSGI configuration"
echo "  4. Install requirements: pip install -r requirements_pa.txt"
echo "  5. Click 'Reload' button"
echo ""
echo -e "${GREEN}All prompts were auto-accepted!${NC}"
echo ""
echo "For detailed instructions, see: CLOUD_HOSTING_GUIDE.md"
