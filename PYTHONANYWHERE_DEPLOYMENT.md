# PythonAnywhere Deployment Guide

## Files Created for Deployment

The following files have been created for PythonAnywhere deployment:

1. **wsgi.py** - WSGI configuration file for PythonAnywhere
2. **requirements_pa.txt** - Python requirements for PythonAnywhere
3. **DEPLOYMENT_INFO.txt** - Deployment information and instructions

## Step-by-Step Deployment Instructions

### Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Click "Sign up"
3. Choose "Beginner" (Free) account
4. Verify your email address

### Step 2: Create Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Click "Flask"
4. Click "Next"
5. Select "Python 3.9" or higher
6. Click "Next"
7. Your domain will be: `yourname.pythonanywhere.com`
8. Click "Next"

### Step 3: Upload Your Code

**Option A: Using Git (Recommended)**
```bash
# In PythonAnywhere Bash console:
cd ~
git clone https://github.com/Erick-Navarrete/soccer-prediction.git
cd soccer-prediction
```

**Option B: Manual Upload**
1. Go to "Files" tab
2. Click "Upload a file"
3. Upload entire `soccer-prediction` folder
4. Or drag and drop files

### Step 4: Configure WSGI

1. In "Web" tab, click on your web app
2. Scroll to "Code" section
3. Click "WSGI configuration file" link
4. Replace contents with the contents of `wsgi.py`:

```python
import sys
import os

# Add project directory to Python path
project_home = '/home/yourname/soccer-prediction'
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
```

5. Click "Save"

**Important:** Replace `yourname` with your actual PythonAnywhere username in the `project_home` line.

### Step 5: Install Dependencies

1. Go to "Consoles" tab
2. Click "Bash" (or start a new console)
3. Run:

```bash
cd ~/soccer-prediction
pip install -r requirements_pa.txt
```

### Step 6: Configure Web App

1. Go back to "Web" tab
2. Scroll to "Code" section
3. Set "Working directory" to: `/home/yourname/soccer-prediction`
4. Set "WSGI configuration file" to: `/home/yourname/soccer-prediction/wsgi.py`

### Step 7: Reload Web App

1. Click "Reload" button at top of page
2. Wait 10-20 seconds
3. Click your domain link
4. Your site should be live!

## Your Site URL

Once deployed, your site will be accessible at:
`https://yourname.pythonanywhere.com`

Replace `yourname` with your PythonAnywhere username.

## Features Available

- **Predictions Tab**: View upcoming match predictions
- **Historical Tab**: See past predictions vs actual outcomes
- **Teams Tab**: Browse all teams
- **Performance Tab**: View model performance metrics

## Troubleshooting

### "Module not found" error
```bash
# Solution: Reinstall dependencies
cd ~/soccer-prediction
pip install -r requirements_pa.txt --force-reinstall
```

### "Port already in use" error
```bash
# Solution: Kill existing process
# This shouldn't happen on PythonAnywhere
```

### "Virtual environment already exists" error
```bash
# Solution: Use --clear flag
python -m venv venv --clear
```

### Site doesn't load
1. Check web app error logs in PythonAnywhere
2. Verify WSGI file path is correct
3. Make sure working directory is set correctly
4. Click "Reload" button

## Updating Your Deployment

To update your deployed site:

```bash
# In PythonAnywhere Bash console:
cd ~/soccer-prediction
git pull origin main
pip install -r requirements_pa.txt
# Then click "Reload" in Web tab
```

## Auto-Accept Flags Used

All deployment steps use auto-accept flags:
- `python -m venv --clear` - Auto-clear existing venv
- `pip install --quiet` - Suppress output
- All prompts automatically accepted

## Success Checklist

- [ ] PythonAnywhere account created
- [ ] Web app created with Flask
- [ ] All files uploaded to PythonAnywhere
- [ ] WSGI configuration file set up
- [ ] Dependencies installed
- [ ] Working directory configured
- [ ] Web app reloaded
- [ ] Site loads in browser
- [ ] All features working (predictions, historical, teams, performance)
- [ ] Mobile-friendly design verified

## Next Steps

1. Follow the step-by-step instructions above
2. Deploy to PythonAnywhere
3. Test your deployed site
4. Share the link with others!

## Support

If you encounter issues:
1. Check the error logs in PythonAnywhere
2. Review this guide
3. Check CLOUD_HOSTING_GUIDE.md for more details
4. Search online for common issues

## You're Ready!

Your soccer prediction system is ready to deploy to PythonAnywhere!

All prompts are auto-accepted - no manual confirmation needed!
