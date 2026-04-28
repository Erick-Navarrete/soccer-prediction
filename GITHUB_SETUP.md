# GitHub Setup Instructions for Erick-Navarrete

Your GitHub profile: https://github.com/Erick-Navarrete

## Step 1: Install Git (if not already installed)

### Windows
1. Download Git from https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart your terminal/command prompt

### Verify Installation
```bash
git --version
```

## Step 2: Configure Git

Set your git username and email:
```bash
git config --global user.name "Erick Navarrete"
git config --global user.email "your.email@example.com"
```

## Step 3: Navigate to Your Project

```bash
cd D:\Project_App\soccer-prediction
```

## Step 4: Initialize Git Repository

```bash
git init
```

## Step 5: Create a New GitHub Repository

1. Go to https://github.com/new
2. Repository name: `soccer-prediction` (or your preferred name)
3. Description: `Comprehensive football match prediction system with ML models, Polymarket integration, and Claude API`
4. Make it **Public** or **Private** (your choice)
5. **Don't** initialize with README, .gitignore, or license
6. Click "Create repository"
7. Copy the repository URL (will be something like: `https://github.com/Erick-Navarrete/soccer-prediction.git`)

## Step 6: Add Files and Make Initial Commit

Add all files to git:
```bash
git add .
```

Create initial commit:
```bash
git commit -m "Initial commit: Soccer prediction system with ML models, Polymarket integration, and Claude API"
```

## Step 7: Connect to Your GitHub Repository

Replace `YOUR_REPO_NAME` with the actual repository name you created:

```bash
git remote add origin https://github.com/Erick-Navarrete/YOUR_REPO_NAME.git
```

For example, if you named it `soccer-prediction`:
```bash
git remote add origin https://github.com/Erick-Navarrete/soccer-prediction.git
```

## Step 8: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

You'll be prompted for your GitHub username and password/token.

## Step 9: Verify on GitHub

1. Go to https://github.com/Erick-Navarrete
2. Click on your new repository
3. Verify all files are uploaded

## Authentication Setup (Recommended)

### Option 1: Personal Access Token (Recommended)

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Note: Description "Soccer Prediction System"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

When pushing, use the token as your password.

### Option 2: GitHub CLI (Easier)

```bash
# Install GitHub CLI
winget install --id GitHub.cli

# Authenticate
gh auth login

# Follow the prompts
```

Then you can push without entering credentials each time.

## Quick Commands Reference

### Check Status
```bash
git status
```

### View Changes
```bash
git diff
```

### Add Specific Files
```bash
git add filename.py
```

### Commit Changes
```bash
git commit -m "Your commit message"
```

### Push Changes
```bash
git push
```

### Pull Latest Changes
```bash
git pull origin main
```

### View Commit History
```bash
git log --oneline
```

## Common Issues and Solutions

### Issue: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/Erick-Navarrete/YOUR_REPO_NAME.git
```

### Issue: "Authentication failed"
Use Personal Access Token instead of password:
1. Generate token as shown above
2. When prompted for password, paste the token

### Issue: "Push rejected"
```bash
git pull origin main
git push origin main
```

### Issue: "Nothing to commit"
```bash
# Check if there are changes
git status

# If no changes, make some edits first
```

## Your Repository URL

After creating the repository, your URL will be:
```
https://github.com/Erick-Navarrete/YOUR_REPO_NAME
```

Replace `YOUR_REPO_NAME` with the actual name you chose.

## Next Steps After Setup

### 1. Clone on Another Machine
```bash
git clone https://github.com/Erick-Navarrete/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Run the System
```bash
python src/main.py
```

### 4. Make Changes and Push
```bash
# Make changes to files
git add .
git commit -m "Update feature"
git push
```

## Repository Features to Enable

After pushing, consider enabling:

1. **Issues**: For bug tracking and feature requests
2. **Wiki**: For additional documentation
3. **Projects**: For task management
4. **Actions**: For automated workflows
5. **Pages**: For hosting documentation

## Sharing Your Repository

To share with others:
- Public: Anyone can view and clone
- Private: Only you and collaborators can access

To add collaborators:
1. Go to repository Settings
2. Click "Collaborators"
3. Click "Add people"
4. Enter their GitHub username

## Backup Strategy

Your repository is now backed up on GitHub. To ensure you don't lose work:

```bash
# Regular commits
git add .
git commit -m "Backup commit"
git push
```

## Branching Strategy (Optional)

For development:

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "Add new feature"

# Push branch
git push -u origin feature/new-feature

# Create Pull Request on GitHub
# Merge to main after review
```

## Summary

Your soccer prediction system is now ready to be pushed to GitHub at:
```
https://github.com/Erick-Navarrete/YOUR_REPO_NAME
```

Follow the steps above to complete the setup and start collaborating!
