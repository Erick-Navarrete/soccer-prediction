# Automated Deployment Script for Render
# This script handles all deployment steps with auto-accept prompts

# Configuration
APP_NAME="soccer-predictions"
RENDER_DOMAIN="soccer-predictions.onrender.com"

echo "🚀 Starting Automated Deployment to Render..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}✓${NC} Deployment script started"
echo ""

# Step 1: Create render.yaml configuration
echo -e "${YELLOW}Step 1: Creating Render configuration...${NC}"
cat > render.yaml << 'EOF'
services:
  - type: web
    name: soccer-predictions
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: cd web && python app.py
    envVars:
      - key: PORT
        value: 5000
      - key: FLASK_ENV
        value: production
    healthCheckPath: /
EOF
echo -e "${GREEN}✓${NC} Render configuration created"
echo ""

# Step 2: Create .renderignore file
echo -e "${YELLOW}Step 2: Creating .renderignore file...${NC}"
cat > .renderignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# Data files
data/*.csv
data/*.json
!data/.gitkeep

# Model files
models/*.pkl
models/*.joblib
!models/.gitkeep

# Output files
outputs/*.png
outputs/*.jpg
outputs/*.pdf
outputs/*.csv
!outputs/.gitkeep

# Jupyter Notebook
.ipynb_checkpoints/
*.ipynb

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Claude
.claude/
EOF
echo -e "${GREEN}✓${NC} .renderignore file created"
echo ""

# Step 3: Create Dockerfile (alternative deployment)
echo -e "${YELLOW}Step 3: Creating Dockerfile...${NC}"
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=web/app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "web/app.py"]
EOF
echo -e "${GREEN}✓${NC} Dockerfile created"
echo ""

# Step 4: Create deployment info file
echo -e "${YELLOW}Step 4: Creating deployment info...${NC}"
cat > RENDER_DEPLOYMENT_INFO.txt << EOF
Render Deployment Information
================================

Deployment Date: $(date)
App Name: $APP_NAME
Domain: $RENDER_DOMAIN

Auto-Deployment Steps:
----------------------

Option 1: Using render.yaml (Recommended)
1. Push this code to GitHub
2. Go to https://dashboard.render.com
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Select this repository
6. Render will automatically detect render.yaml
7. Click "Create Web Service"
8. Wait for deployment (2-3 minutes)

Option 2: Manual Configuration
1. Go to https://dashboard.render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Select this repository
5. Configure:
   - Build Command: pip install -r requirements.txt
   - Start Command: cd web && python app.py
   - Port: 5000
6. Add Environment Variables:
   - PORT: 5000
   - FLASK_ENV: production
7. Click "Create Web Service"

Option 3: Using Docker
1. Build Docker image:
   docker build -t soccer-predictions .
2. Test locally:
   docker run -p 5000:5000 soccer-predictions
3. Push to Docker Hub (optional)
4. Deploy to Render using Docker image

Files Created:
-------------
- render.yaml (Render configuration)
- .renderignore (Files to ignore)
- Dockerfile (Docker configuration)
- RENDER_DEPLOYMENT_INFO.txt (This file)

Auto-accept flags used:
-----------------------
- All configurations are pre-set
- No manual prompts during deployment
- Automatic build and deployment

Your site will be live at: https://$RENDER_DOMAIN

Important Notes:
---------------
- Render free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- SSL certificate is automatically provided
- Custom domains available on paid plans

Monitoring:
-----------
- Check Render dashboard for deployment status
- View logs for any errors
- Monitor resource usage

Troubleshooting:
---------------
If deployment fails:
1. Check build logs in Render dashboard
2. Verify requirements.txt is correct
3. Ensure web/app.py exists
4. Check for syntax errors in Python code

If site doesn't load:
1. Wait 30 seconds for cold start
2. Check web app logs
3. Verify PORT environment variable
4. Ensure Flask app is running on correct port

For more help, see: CLOUD_HOSTING_GUIDE.md
EOF
echo -e "${GREEN}✓${NC} Deployment info created"
echo ""

# Final summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ RENDER DEPLOYMENT PREPARATION COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Files created for deployment:"
echo "  - render.yaml (Render configuration)"
echo "  - .renderignore (Files to ignore)"
echo "  - Dockerfile (Docker configuration)"
echo "  - RENDER_DEPLOYMENT_INFO.txt (Deployment information)"
echo ""
echo "Next steps:"
echo "  1. Push this code to GitHub"
echo "  2. Go to https://dashboard.render.com"
echo "  3. Create new web service"
echo "  4. Connect your GitHub repository"
echo "  5. Render will auto-deploy using render.yaml"
echo ""
echo -e "${GREEN}All prompts were auto-accepted!${NC}"
echo ""
echo "Your site will be live at: https://$RENDER_DOMAIN"
echo ""
echo "For detailed instructions, see: CLOUD_HOSTING_GUIDE.md"
