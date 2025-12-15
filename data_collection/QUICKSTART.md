# Quickstart: Run Arbitrum DAO Data Collectors

This guide will help you start collecting Arbitrum DAO data in 5 minutes.

## Prerequisites

- Python 3.8+
- Supabase account (free tier works)
- Git

## Step 1: Get Supabase Credentials

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Create a new project (or use existing)
3. Go to **Project Settings** → **API**
4. Copy two values:
   - **Project URL** (starts with `https://`)
   - **service_role key** (under "Project API keys")

## Step 2: Setup Database

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy-paste the entire content of `schema.sql` from this folder
4. Click **Run** to create all tables

## Step 3: Clone & Configure

```bash
# Clone repository
git clone https://github.com/danvolsky-source/dao-data-ai.git
cd dao-data-ai/data_collection

# Install dependencies  
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

Edit `.env` file:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
```

## Step 4: Run Collectors

### Option A: Collect Snapshot Data (Fastest - ~30 seconds)

```bash
python collectors/snapshot_collector.py
```

**What it does:**
- Fetches 100 latest Arbitrum proposals from Snapshot
- Collects all votes for each proposal
- Stores in `snapshot_proposals` and `snapshot_votes` tables

**Expected output:**
```
Collecting Arbitrum DAO proposals from Snapshot...
✓ Collected 100 proposals
✓ Collecting votes for proposal: 0x1234...
✓ Stored 1,247 votes
Total: 100 proposals, 52,391 votes
```

### Option B: Collect Forum Data (~2 minutes)

```bash
python scrapers/forum_scraper.py
```

**What it does:**
- Scrapes governance.arbitrum.foundation forum
- Extracts proposal discussions and comments
- Links forum threads to Snapshot proposals via AIP numbers
- Stores in `forum_threads` and `forum_posts` tables

**Expected output:**
```
Scraping Arbitrum governance forum...
✓ Found 50 proposal threads
✓ Extracted 1,234 comments
✓ Linked 45 threads to Snapshot proposals
```

### Option C: Collect On-Chain Events (~5 minutes)

```bash
python collectors/onchain_collector.py  
```

**What it does:**
- Connects to Arbitrum RPC
- Fetches ProposalExecuted and VoteCast events from Governor contract
- Tracks execution status and on-chain voting
- Stores in `onchain_events` table

**Expected output:**
```
Starting Arbitrum on-chain collector...
Governor: 0xf07DeD9dC292157749B6Fd268E37DF6EA38395B9
Connected to Arbitrum: True

Syncing from block 150000000 to 152345678
Processing blocks 150000000 - 150001000...
✓ Stored execution for proposal 12345
✓ Stored vote from 0x1234... on proposal 12345
Total events collected: 3,421
```

## Step 5: Verify Data

Go to Supabase **Table Editor** and check:
- `snapshot_proposals` - Should have ~100 rows
- `snapshot_votes` - Should have ~50,000 rows  
- `forum_threads` - Should have ~50 rows
- `onchain_events` - Should have ~3,000 rows

Or run this query in **SQL Editor**:
```sql
SELECT 
  'proposals' as table_name, COUNT(*) FROM snapshot_proposals
UNION ALL
SELECT 
  'votes', COUNT(*) FROM snapshot_votes
UNION ALL
SELECT 
  'forum_threads', COUNT(*) FROM forum_threads
UNION ALL
SELECT 
  'onchain_events', COUNT(*) FROM onchain_events;
```

## Troubleshooting

### "Module not found" error
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "Invalid API key" error
- Make sure you copied the **service_role** key, not anon key
- Check `.env` file has correct SUPABASE_URL and SUPABASE_KEY
- No quotes needed around values in .env

### "Table does not exist" error
- Run `schema.sql` in Supabase SQL Editor first
- Make sure you clicked **Run** after pasting the schema

### Slow collection
- Normal! Snapshot: ~30s, Forum: ~2min, On-chain: ~5min
- Rate limiting is intentional to respect API limits

## Next Steps

1. **Schedule regular runs**: Set up cron job to run collectors daily
2. **Explore data**: Check Supabase Table Editor
3. **Build analytics**: Use the data for ML models or dashboards
4. **API access**: Data is available via your deployment at dao-data-ai.vercel.app/api/stats

## Data Update Frequency

- **Snapshot**: Run daily (new proposals + votes)
- **Forum**: Run daily (new discussions)
- **On-chain**: Run daily (new executions)

## Need Help?

Open an issue on GitHub: https://github.com/danvolsky-source/dao-data-ai/issues
