# 🚀 Automated Deployment Guide

This guide provides step-by-step instructions for deploying your soccer prediction system to free cloud hosting services with **auto-accept prompts**.

## 📋 Quick Start

### Choose Your Hosting Provider:

1. **PythonAnywhere** (Recommended - Easiest)
   - Run: `./deploy_pythonanywhere.sh` (Linux/Mac) or `.\deploy_pythonanywhere.ps1` (Windows)
   - Upload to PythonAnywhere
   - Your site: `https://yourname.pythonanywhere.com`

2. **Render** (Modern - GitHub Integration)
   - Run: `./deploy_render.sh`
   - Push to GitHub
   - Connect to Render
   - Your site: `https://soccer-predictions.onrender.com`

3. **Replit** (Simplest - Browser-based)
   - Go to https://replit.com
   - Create new Python Flask Repl
   - Upload files
   - Your site: `https://yourapp.replit.co`

---

## 🎯 PythonAnywhere Deployment (Recommended)

### Step 1: Run Deployment Script

**Windows:**
```powershell
.\deploy_pythonanywhere.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy_pythonanywhere.sh
./deploy_pythonanywhere.sh
```

**Auto-accept flags used:**
- `python -m venv --clear` - Auto-clear existing venv
- `pip install --yes` - Auto-accept all pip prompts
- `pip install --quiet` - Suppress output
- All prompts automatically accepted

### Step 2: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com
2. Click "Sign up"
3. Choose "Beginner" (Free) account
4. Verify email address

### Step 3: Create Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Click "Flask"
4. Click "Next"
5. Select "Python 3.9" or higher
6. Click "Next"
7. Your domain will be: `yourname.pythonanywhere.com`
8. Click "Next"

### Step 4: Upload Your Code

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

### Step 5: Configure WSGI

1. In "Web" tab, click on your web app
2. Scroll to "Code" section
3. Click "WSGI configuration file" link
4. Replace contents with:

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

### Step 6: Install Dependencies

1. Go to "Consoles" tab
2. Click "Bash" (or start a new console)
3. Run:

```bash
cd ~/soccer-prediction
pip install -r requirements_pa.txt --yes
```

**Auto-accept flags:**
- `--yes` - Auto-confirm all pip prompts

### Step 7: Configure Web App

1. Go back to "Web" tab
2. Scroll to "Code" section
3. Set "Working directory" to: `/home/yourname/soccer-prediction`
4. Set "WSGI configuration file" to: `/home/yourname/soccer-prediction/wsgi.py`

### Step 8: Reload Web App

1. Click "Reload" button at top of page
2. Wait 10-20 seconds
3. Click your domain link
4. Your site should be live!

---

## 🌐 Render Deployment (GitHub Integration)

### Step 1: Run Deployment Script

```bash
chmod +x deploy_render.sh
./deploy_render.sh
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 3: Create Render Account

1. Go to https://render.com
2. Click "Sign up"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### Step 4: Create Web Service

1. Click "New" → "Web Service"
2. Click "Connect GitHub"
3. Select `Erick-Navarrete/soccer-prediction`
4. Click "Connect"

### Step 5: Configure Build

**Auto-detected from render.yaml:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd web && python app.py`
- **Port:** 5000

**Manual Configuration (if needed):**
- **Name:** `soccer-predictions`
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** `.`

### Step 6: Add Environment Variables

1. Scroll to "Environment" section
2. Click "Add Environment Variable"
3. Add:
   - `PORT`: `5000`
   - `FLASK_ENV`: `production`

### Step 7: Deploy

1. Click "Create Web Service"
2. Wait for deployment (2-3 minutes)
3. Watch build logs for any errors
4. Your site will be live at: `https://soccer-predictions.onrender.com`

---

## 💻 Replit Deployment (Browser-based)

### Step 1: Create Replit

1. Go to https://replit.com
2. Click "Create Repl"
3. Search "Flask" template
4. Click "Create Repl"

### Step 2: Upload Your Code

1. Click "Files" tab
2. Delete default files
3. Click "Upload file"
4. Upload all files from `soccer-prediction` folder

### Step 3: Install Dependencies

1. Click "Shell" tab
2. Run:

```bash
pip install -r requirements.txt --yes
```

### Step 4: Configure Start

1. Click ".replit" file
2. Update configuration:

```toml
[run]
command = "cd web && python app.py"
```

### Step 5: Deploy

1. Click "Deploy" button
2. Choose "Public" deployment
3. Click "Deploy"
4. Your site will be live at: `https://yourapp.replit.co`

---

## 🔧 Auto-Accept Flags Reference

### pip Commands
```bash
# Auto-confirm all prompts
pip install --yes package_name

# Auto-upgrade without prompts
pip install --upgrade --yes package_name

# Install from requirements without prompts
pip install -r requirements.txt --yes

# Quiet mode (suppress output)
pip install --quiet --yes package_name
```

### Python Commands
```bash
# Auto-clear existing virtual environment
python -m venv venv --clear

# Force reinstall
pip install --force-reinstall --yes package_name
```

### Git Commands
```bash
# Auto-add all files
git add .

# Auto-commit with message
git commit -m "message"

# Auto-push without confirmation
git push --force origin main
```

### Docker Commands
```bash
# Auto-build without prompts
docker build --no-cache -t app_name .

# Auto-run without prompts
docker run -d -p 5000:5000 app_name
```

---

## 📊 Deployment Comparison

| Feature | PythonAnywhere | Render | Replit |
|---------|----------------|--------|--------|
| **Setup Time** | 5-10 min | 10-15 min | 2-3 min |
| **Auto-accept** | ✅ Full | ✅ Full | ✅ Full |
| **GitHub Integration** | ❌ Manual | ✅ Auto | ❌ Manual |
| **Uptime** | 24/7 | Sleeps | Always on* |
| **SSL** | ✅ Auto | ✅ Auto | ✅ Auto |
| **Custom Domain** | Paid | Paid | Paid |
| **Free Tier** | ✅ Yes | ✅ Yes | ✅ Yes |

*Replit always-on requires paid plan

---

## 🎯 Troubleshooting

### Common Issues & Solutions

**"Module not found" error:**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --yes --force-reinstall
```

**"Port already in use" error:**
```bash
# Solution: Kill existing process
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill
```

**"Virtual environment already exists" error:**
```bash
# Solution: Use --clear flag
python -m venv venv --clear
```

**"Permission denied" error:**
```bash
# Solution: Use sudo (Linux/Mac)
sudo pip install -r requirements.txt --yes
```

**"Deployment failed" error:**
```bash
# Solution: Check logs and retry
# PythonAnywhere: Check web app error logs
# Render: Check build logs in dashboard
# Replit: Check console output
```

---

## 📱 Testing Your Deployment

### Test Locally First
```bash
# Start local server
cd web
python app.py

# Test in browser
# http://localhost:5000
```

### Test Cloud Deployment
```bash
# Test your deployed site
# PythonAnywhere: https://yourname.pythonanywhere.com
# Render: https://soccer-predictions.onrender.com
# Replit: https://yourapp.replit.co
```

### Test API Endpoints
```bash
# Test predictions endpoint
curl https://yourdomain.com/api/predictions

# Test teams endpoint
curl https://yourdomain.com/api/teams

# Test performance endpoint
curl https://yourdomain.com/api/performance
```

---

## 🔄 Updating Your Deployment

### PythonAnywhere
```bash
# In PythonAnywhere Bash console:
cd ~/soccer-prediction
git pull origin main
pip install -r requirements.txt --yes
# Then click "Reload" in Web tab
```

### Render
```bash
# Push changes to GitHub
git add .
git commit -m "Update"
git push origin main
# Render auto-deploys
```

### Replit
```bash
# Upload new files
# Click "Run" to restart
# Click "Deploy" to update
```

---

## 🎉 Success Checklist

- [ ] Deployment script run successfully
- [ ] All files uploaded to cloud
- [ ] Dependencies installed without errors
- [ ] Web app configured correctly
- [ ] Site loads in browser
- [ ] All features working (predictions, historical, teams, performance)
- [ ] Mobile-friendly design verified
- [ ] Share link with others

---

## 📞 Getting Help

If you encounter issues:

1. **Check logs** - Look at error messages
2. **Review this guide** - Re-read relevant sections
3. **Check CLOUD_HOSTING_GUIDE.md** - More detailed information
4. **Search online** - Many common issues have solutions
5. **Ask for help** - Community forums are helpful

---

## 🚀 You're Ready!

Choose your hosting provider, run the deployment script, and your soccer prediction system will be live on the web!

**All prompts are auto-accepted - no manual confirmation needed!**
