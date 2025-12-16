# DAO Data AI - Deployment Guide

## 🚀 Quick Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (free tier works)
- Supabase account (for database)

### Step 1: Fork/Clone Repository
```bash
git clone https://github.com/danvolsky-source/dao-data-ai.git
cd dao-data-ai
```

### Step 2: Set Up Supabase Database
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Get your credentials:
   - Project URL: `https://your-project.supabase.co`
   - Anon Key: From Settings > API

### Step 3: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard
1. Go to [Vercel](https://vercel.com)
2. Click "New Project"
3. Import `dao-data-ai` repository
4. Add Environment Variables:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```
5. Click "Deploy"

#### Option B: Deploy via CLI
```bash
npm install -g vercel
vercel login
vercel --prod
```

When prompted, add environment variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Step 4: Verify Deployment

After deployment, your app will be available at:
- Frontend: `https://dao-data-ai.vercel.app`
- Backend API: `https://dao-data-ai.vercel.app/api`

Test the API:
```bash
curl https://dao-data-ai.vercel.app/api/stats
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "active_proposals": 399,
    "total_votes": 314900,
    "active_delegates": 100
  }
}
```

## 📊 Architecture

```
dao-data-ai/
├── app/                    # Next.js frontend
│   └── page.tsx           # Main dashboard
├── backend/               # FastAPI backend
│   ├── main.py           # API endpoints
│   └── requirements.txt  # Python dependencies
├── vercel.json           # Vercel configuration
└── DEPLOYMENT.md         # This file
```

## 🔧 Configuration

### vercel.json
The `vercel.json` file configures both frontend and backend:
- **Backend**: FastAPI deployed as serverless functions
- **Frontend**: Next.js static site
- **Routing**: `/api/*` → backend, `/*` → frontend

### Environment Variables

Required:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key

## 🐛 Troubleshooting

### Dashboard shows no data
1. Check Supabase credentials in Vercel environment variables
2. Verify backend API is responding: `/api/stats`
3. Check browser console for CORS errors

### API returns 500 errors
1. Check Vercel function logs
2. Verify `requirements.txt` has all dependencies:
   ```
   fastapi==0.109.0
   uvicorn==0.27.0
   supabase==2.3.4
   pydantic==2.5.3
   python-dotenv==1.0.0
   ```

### CORS issues
The backend `main.py` already has CORS configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 Post-Deployment

### 1. Populate Database
Run the data collection scripts to populate Supabase:
```bash
cd data_collection
python snapshot_collector.py
```

### 2. Set Up Automation
Use GitHub Actions or Vercel Cron Jobs to:
- Sync data every 30 minutes
- Update ML predictions hourly
- Generate analytics reports daily

### 3. Monitor Performance
- Check Vercel Analytics dashboard
- Monitor Supabase database usage
- Review API response times

## 🎯 Next Steps

1. **Custom Domain**: Add your domain in Vercel settings
2. **Analytics**: Enable Vercel Analytics for traffic insights
3. **Monitoring**: Set up error tracking (Sentry)
4. **Scaling**: Upgrade Vercel plan if needed

## 📝 Notes

- Free Vercel tier supports up to 100GB bandwidth/month
- Supabase free tier includes 500MB database
- Backend functions have 10s execution limit (Hobby plan)

## 🆘 Support

Issues? Check:
1. [Vercel Documentation](https://vercel.com/docs)
2. [Supabase Documentation](https://supabase.com/docs)
3. [FastAPI Documentation](https://fastapi.tiangolo.com)

---

Built with ❤️ for DAO Governance Analytics
