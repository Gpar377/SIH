# 🚀 Deployment Guide

## Quick GitHub Setup

### 1. Run Setup Script
```bash
setup_github.bat
```

### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `dte-rajasthan-dropout-prediction`
3. Description: `Student dropout prediction system for DTE Rajasthan`
4. Set to Public or Private
5. Click "Create repository"

### 3. Connect to GitHub
```bash
git remote add origin https://github.com/YOURUSERNAME/dte-rajasthan-dropout-prediction.git
git branch -M main
git push -u origin main
```

## 🌐 Live Deployment Options

### Option 1: Render (Free)
1. Connect GitHub repo to Render
2. Build command: `pip install -r requirements.txt`
3. Start command: `cd backend && python main.py`

### Option 2: Railway (Free)
1. Connect GitHub repo to Railway
2. Auto-deploys on push
3. Gets free domain

### Option 3: Heroku
1. Create Procfile: `web: cd backend && python main.py`
2. Deploy via GitHub integration

## 📋 Environment Setup

### Production Environment Variables
```env
PORT=8000
ENVIRONMENT=production
DEBUG=false
```

### Database
- SQLite files included in repo
- No external database needed
- Automatic backup on deployment

## ✅ Deployment Checklist

- [x] .gitignore created
- [x] README.md updated
- [x] Requirements.txt ready
- [x] Database files excluded
- [x] Setup script created
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Live deployment configured

## 🔧 Post-Deployment

1. Test all endpoints: `/health`, `/docs`, `/`
2. Upload sample data
3. Verify dashboard functionality
4. Check mobile responsiveness