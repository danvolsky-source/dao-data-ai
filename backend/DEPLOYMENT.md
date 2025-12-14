# 🚀 Backend Deployment Guide

This guide will help you deploy the DAO Analytics Platform backend API to production.

## Prerequisites

- GitHub account with this repository
- Supabase project (already set up)
- Railway account (free tier available) OR Fly.io account

---

## Option 1: Deploy to Railway (Recommended)

### Why Railway?
- ✅ Free tier with 500 hours/month
- ✅ Automatic deployments from GitHub
- ✅ Built-in PostgreSQL (though we use Supabase)
- ✅ Simple environment variable management
- ✅ HTTPS by default

### Step-by-Step Instructions

#### 1. Install Railway CLI

```bash
# Using npm
npm install -g @railway/cli

# Or using Homebrew (Mac)
brew install railway
```

#### 2. Login to Railway

```bash
railway login
```

This will open your browser for authentication.

#### 3. Initialize Project

```bash
cd backend
railway init
```

Select "Create new project" and give it a name like `dao-analytics-api`

#### 4. Add Environment Variables

```bash
# Add Supabase URL
railway variables set SUPABASE_URL=https://fsvlkshplbfivwmdljqh.supabase.co

# Add Supabase Key (get from Supabase dashboard)
railway variables set SUPABASE_KEY=your_anon_key_here

# Set port
railway variables set PORT=8000
```

Or set them in Railway dashboard:
1. Go to https://railway.app/dashboard
2. Select your project
3. Go to "Variables" tab
4. Add:
   - `SUPABASE_URL`: `https://fsvlkshplbfivwmdljqh.supabase.co`
   - `SUPABASE_KEY`: Your anon key from Supabase
   - `PORT`: `8000`

#### 5. Deploy

```bash
railway up
```

#### 6. Get Your Deployment URL

```bash
railway domain
```

Or find it in Railway dashboard under "Settings" → "Domains"

Your API will be available at: `https://your-project.railway.app`

---

## Option 2: Deploy to Fly.io

### Step-by-Step Instructions

#### 1. Install Fly CLI

```bash
# Mac/Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. Login to Fly.io

```bash
fly auth login
```

#### 3. Create fly.toml

Create a file `fly.toml` in the `backend` directory:

```toml
app = "dao-analytics-api"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"
  buildpacks = ["gcr.io/paketo-buildpacks/python"]

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

#### 4. Launch App

```bash
cd backend
fly launch --no-deploy
```

#### 5. Set Secrets

```bash
fly secrets set SUPABASE_URL=https://fsvlkshplbfivwmdljqh.supabase.co
fly secrets set SUPABASE_KEY=your_anon_key_here
```

#### 6. Deploy

```bash
fly deploy
```

Your API will be available at: `https://dao-analytics-api.fly.dev`

---

## Option 3: Deploy to Heroku

### Step-by-Step Instructions

#### 1. Install Heroku CLI

```bash
# Mac
brew tap heroku/brew && brew install heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. Create Procfile

Create a file `Procfile` in the `backend` directory:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 3. Create runtime.txt

Create `runtime.txt`:

```
python-3.11.7
```

#### 4. Login and Create App

```bash
cd backend
heroku login
heroku create dao-analytics-api
```

#### 5. Set Config Vars

```bash
heroku config:set SUPABASE_URL=https://fsvlkshplbfivwmdljqh.supabase.co
heroku config:set SUPABASE_KEY=your_anon_key_here
```

#### 6. Deploy

```bash
git push heroku main
```

---

## Post-Deployment Steps

### 1. Test Your API

```bash
# Test health endpoint
curl https://your-api-url.com/

# Test proposals endpoint
curl https://your-api-url.com/api/proposals
```

### 2. Update Frontend

Update the API URL in your frontend code:

**In `index.html`:**
```javascript
const API_BASE = 'https://your-api-url.com';
```

**In `arbitrum-dao-dashboard`:**
```javascript
const SUPABASE_URL = 'https://fsvlkshplbfivwmdljqh.supabase.co';
const SUPABASE_KEY = 'your_anon_key_here';
```

### 3. Enable CORS (if needed)

The backend already has CORS enabled for all origins. In production, you might want to restrict it:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dao-data-ai.vercel.app",
        "https://danvolsky-source.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Monitor Your Deployment

**Railway:**
- Dashboard: https://railway.app/dashboard
- Logs: `railway logs`

**Fly.io:**
- Dashboard: https://fly.io/dashboard
- Logs: `fly logs`

**Heroku:**
- Dashboard: https://dashboard.heroku.com
- Logs: `heroku logs --tail`

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Make sure `requirements.txt` is in the same directory

### Issue: "Port already in use"
**Solution:** Check `PORT` environment variable is set correctly

### Issue: "Supabase connection failed"
**Solution:** Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct

### Issue: "CORS errors"
**Solution:** Check CORS middleware configuration in `main.py`

---

## GitHub Actions (Automatic Deployment)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm i -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Quick Reference

### Railway Commands
```bash
railway login          # Login to Railway
railway init           # Initialize project
railway up             # Deploy
railway logs           # View logs
railway variables      # List environment variables
railway domain         # Get deployment URL
```

### Fly.io Commands
```bash
fly auth login         # Login to Fly.io
fly launch             # Create app
fly deploy             # Deploy
fly logs               # View logs
fly secrets list       # List secrets
fly status             # Check app status
```

---

## Next Steps

1. ✅ Deploy backend using one of the options above
2. ✅ Get your production API URL
3. ✅ Update frontend with production URL
4. ✅ Test all API endpoints
5. ✅ Set up monitoring and alerts
6. ✅ Configure custom domain (optional)

---

## Support

If you encounter issues:
- Check logs for error messages
- Verify environment variables are set correctly
- Test locally first: `python main.py`
- Open an issue on GitHub

---

**Congratulations! Your DAO Analytics API is now live! 🎉**
