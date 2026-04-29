# Free Cloud Hosting Guide for Soccer Prediction System

## 🌐 Your Website is Now Live!

**Local Access:** http://localhost:5000
**Network Access:** http://192.168.68.66:5000

## 🚀 Free Cloud Hosting Options

### 1. PythonAnywhere (Recommended - Easiest)

**Pros:**
- ✅ Completely free tier available
- ✅ Designed specifically for Python apps
- ✅ Easy setup with web interface
- ✅ Your own domain: `yourname.pythonanywhere.com`
- ✅ No credit card required

**Free Tier Limits:**
- 1 web app
- 512MB storage
- Python 3.8+
- 24/7 uptime

**Setup Steps:**

1. **Create Account:**
   - Go to https://www.pythonanywhere.com
   - Sign up for free account

2. **Create Web App:**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Flask" framework
   - Select Python 3.9 or higher
   - Your domain will be: `yourname.pythonanywhere.com`

3. **Upload Your Code:**
   - Go to "Files" tab
   - Upload your entire `soccer-prediction` folder
   - Or use git: `git clone https://github.com/Erick-Navarrete/soccer-prediction.git`

4. **Configure WSGI:**
   - Edit WSGI file in web app configuration
   - Add this code:
   ```python
   import sys
   sys.path.insert(0, '/home/yourname/soccer-prediction')
   sys.path.insert(0, '/home/yourname/soccer-prediction/web')

   from web.app import app as application
   ```

5. **Install Dependencies:**
   - Go to "Consoles" tab
   - Start Bash console
   - Run:
   ```bash
   cd soccer-prediction
   pip install -r requirements.txt
   ```

6. **Reload Web App:**
   - Go to "Web" tab
   - Click "Reload" button

**Your site will be live at:** `https://yourname.pythonanywhere.com`

---

### 2. Render (Modern Option)

**Pros:**
- ✅ Free tier with SSL
- ✅ Automatic deployment from GitHub
- ✅ Modern interface
- ✅ Your own domain: `yourapp.onrender.com`

**Free Tier Limits:**
- 512MB RAM
- 0.1 CPU
- Sleeps after 15min inactivity
- Takes ~30sec to wake up

**Setup Steps:**

1. **Create Account:**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select `Erick-Navarrete/soccer-prediction`

3. **Configure Build:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd web && python app.py`
   - **Port:** 5000

4. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: soccer-predictions
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: cd web && python app.py
       envVars:
         - key: PORT
           value: 5000
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)

**Your site will be live at:** `https://soccer-predictions.onrender.com`

---

### 3. Replit (Simplest - Browser-Based)

**Pros:**
- ✅ Completely free
- ✅ No installation required
- ✅ Browser-based IDE
- ✅ Instant deployment
- ✅ Your own domain: `yourapp.replit.co`

**Free Tier Limits:**
- 512MB RAM
- 0.5 vCPU
- Always on (with Replit Premium)

**Setup Steps:**

1. **Create Repl:**
   - Go to https://replit.com
   - Click "Create Repl"
   - Choose "Python, Flask" template

2. **Upload Your Code:**
   - Upload all files from `soccer-prediction` folder
   - Or copy-paste the code

3. **Install Dependencies:**
   - Open Shell tab
   - Run: `pip install -r requirements.txt`

4. **Configure Start:**
   - Click "Run" button
   - Replit will automatically detect Flask app

5. **Deploy:**
   - Click "Deploy" button
   - Choose "Public" deployment

**Your site will be live at:** `https://yourapp.replit.co`

---

### 4. Railway (Modern & Fast)

**Pros:**
- ✅ Free tier available
- ✅ Fast deployment
- ✅ GitHub integration
- ✅ Automatic SSL

**Free Tier Limits:**
- $5 free credit/month
- 512MB RAM
- Sleeps after inactivity

**Setup Steps:**

1. **Create Account:**
   - Go to https://railway.app
   - Sign up with GitHub

2. **New Project:**
   - Click "New Project"
   - "Deploy from GitHub repo"
   - Select your repository

3. **Configure:**
   - Railway will detect Flask automatically
   - Set environment variables if needed

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment

**Your site will be live at:** `https://yourapp.up.railway.app`

---

## 📱 Historical Predictions Feature

Your updated web interface now includes:

### New Features:
- **Historical Tab**: View past predictions vs actual results
- **Accuracy Tracking**: See how well predictions performed
- **Visual Indicators**: Green checkmarks for correct, red X for incorrect
- **Score Display**: Shows actual match scores
- **Statistics Dashboard**: Overall accuracy and prediction counts

### How to Use:
1. Open http://192.168.68.66:5000
2. Click on "Historical" tab
3. See past predictions with outcomes
4. Click "Update" to refresh historical data

### API Endpoints:
- `GET /api/historical` - Get historical predictions
- `GET /api/historical/stats` - Get accuracy statistics
- `GET /api/historical/update` - Update historical data

---

## 🎯 Quick Comparison

| Service | Free Tier | Domain | Difficulty | Uptime |
|---------|-----------|--------|------------|--------|
| **PythonAnywhere** | 512MB | `.pythonanywhere.com` | Easy | 24/7 |
| **Render** | 512MB | `.onrender.com` | Medium | Sleeps |
| **Replit** | 512MB | `.replit.co` | Very Easy | Always on* |
| **Railway** | $5 credit | `.up.railway.app` | Medium | Sleeps |

*Replit always-on requires paid plan

---

## 💡 Recommended Choice

**For Beginners:** PythonAnywhere
- Easiest setup
- Reliable 24/7 uptime
- Good documentation

**For Developers:** Render
- Modern interface
- GitHub integration
- Automatic SSL

**For Quick Testing:** Replit
- Browser-based
- No installation
- Instant results

---

## 🔧 Troubleshooting

### Common Issues:

**"Module not found" errors:**
- Make sure all dependencies are installed
- Check Python version compatibility
- Verify file paths in WSGI configuration

**"Port already in use":**
- Change port in app.py
- Kill existing processes

**"Site not loading":**
- Check web app logs
- Verify WSGI configuration
- Ensure dependencies are installed

**"Historical predictions empty":**
- Run main.py first to generate data
- Check file permissions
- Verify data file exists

---

## 📊 Next Steps

1. **Choose a hosting provider** (I recommend PythonAnywhere)
2. **Follow the setup steps** for your chosen provider
3. **Test your deployed site**
4. **Share the link** with friends and family
5. **Monitor performance** using the built-in analytics

---

## 🌍 Share Your Site

Once deployed, you'll have a public URL like:
- `https://yourname.pythonanywhere.com`
- `https://soccer-predictions.onrender.com`
- `https://yourapp.replit.co`

Share this link anywhere:
- Social media
- Email
- Text messages
- QR codes

---

## 💰 Paid Options (If Needed)

If you outgrow free tiers:

**PythonAnywhere:**
- $5/month for more resources
- Custom domains
- Better performance

**Render:**
- $7/month for always-on
- More RAM/CPU
- Faster builds

**Replit:**
- $7/month for always-on
- More storage
- Faster performance

---

## 🎉 You're Ready to Go!

Your soccer prediction system is now:
- ✅ Fully functional locally
- ✅ Mobile-friendly interface
- ✅ Historical predictions feature
- ✅ Ready for cloud deployment
- ✅ Updated on GitHub

**Choose your hosting provider and deploy today!**

For help with specific hosting setup, feel free to ask!
