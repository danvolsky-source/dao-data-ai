# 🏛️ DAO Analytics Platform

> Real-time governance analytics platform for DAOs with AI-powered insights

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)

## 📖 Overview

DAO Analytics Platform is a comprehensive solution for tracking and analyzing DAO governance activities in real-time. It aggregates proposals, votes, delegate information, and discussion threads from multiple DAOs, providing actionable insights through an intuitive dashboard.

### ✨ Key Features

- 📊 **Real-time Analytics** - Track proposals, votes, and delegate activity as it happens
- 🤖 **AI-Powered Insights** - Sentiment analysis and predictive modeling for proposal outcomes
- 🔗 **Multi-Chain Support** - Works across different blockchain networks
- 🎨 **Modern UI** - Dark-themed fintech design with responsive layout
- 🚀 **RESTful API** - Easy integration with existing tools
- 🔔 **Webhook Support** - Automated data collection via n8n integration

## 🏗️ Architecture

```
┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  n8n    │─────▶│ FastAPI  │─────▶│ Supabase │◀─────│ Frontend │
│Workflow │      │ Backend  │      │PostgreSQL│      │   HTML   │
└─────────┘      └──────────┘      └──────────┘      └──────────┘
   Data            REST API          Database         Dashboard
Collection
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Supabase account (free tier works)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/danvolsky-source/dao-data-ai.git
cd dao-data-ai
```

### 2. Set Up Database

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **SQL Editor** and run the schema:

```sql
-- Proposals table
CREATE TABLE proposals (
    id BIGSERIAL PRIMARY KEY,
    proposal_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    voting_ends_at TIMESTAMPTZ,
    total_votes INTEGER DEFAULT 0,
    votes_for INTEGER DEFAULT 0,
    votes_against INTEGER DEFAULT 0,
    votes_abstain INTEGER DEFAULT 0,
    metadata JSONB
);

-- Votes table
CREATE TABLE votes (
    id BIGSERIAL PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    voter_address TEXT NOT NULL,
    vote_choice TEXT NOT NULL,
    voting_power DECIMAL NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    transaction_hash TEXT,
    UNIQUE(proposal_id, voter_address)
);

-- Delegates table
CREATE TABLE delegates (
    id BIGSERIAL PRIMARY KEY,
    delegate_address TEXT NOT NULL,
    delegator_address TEXT NOT NULL,
    voting_power DECIMAL NOT NULL,
    delegated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(delegate_address, delegator_address)
);

-- Threads table  
CREATE TABLE threads (
    id BIGSERIAL PRIMARY KEY,
    thread_id TEXT UNIQUE NOT NULL,
    proposal_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    replies_count INTEGER DEFAULT 0,
    sentiment_score DECIMAL
);

-- Create indexes for performance
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_created ON proposals(created_at DESC);
CREATE INDEX idx_votes_proposal ON votes(proposal_id);
CREATE INDEX idx_votes_voter ON votes(voter_address);
CREATE INDEX idx_delegates_address ON delegates(delegate_address);
CREATE INDEX idx_threads_proposal ON threads(proposal_id);
```

4. Get your API credentials:
   - Go to **Settings** → **API**
   - Copy **Project URL** and **anon/public key**

### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key-here"

# Run the server
python main.py
```

Backend will start on `http://localhost:8000`

### 4. Set Up Frontend

1. Open `index.html` in your browser, or
2. Serve it with a simple HTTP server:

```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve .
```

3. Update API endpoint in `index.html`:
   - Find `const API_BASE = 'https://your-backend-api.com'`
   - Replace with your backend URL

## 📚 API Documentation

### Proposals

#### Get All Proposals
```http
GET /api/proposals?status=active&limit=100
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "proposal_id": "prop_001",
      "title": "Treasury Allocation Q1 2025",
      "status": "active",
      "total_votes": 150,
      "votes_for": 100,
      "votes_against": 50
    }
  ]
}
```

#### Get Specific Proposal
```http
GET /api/proposals/{proposal_id}
```

#### Create Proposal
```http
POST /api/proposals
Content-Type: application/json

{
  "proposal_id": "prop_002",
  "title": "Increase Marketing Budget",
  "description": "Allocate 50k for Q1 marketing",
  "status": "active"
}
```

### Votes

#### Record Vote
```http
POST /api/votes
Content-Type: application/json

{
  "proposal_id": "prop_001",
  "voter_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "vote_choice": "for",
  "voting_power": 1000,
  "transaction_hash": "0xabc123..."
}
```

#### Get Votes
```http
GET /api/votes?proposal_id=prop_001&limit=100
```

### Delegates

#### Get Delegations
```http
GET /api/delegates?delegate_address=0x123...&limit=100
```

#### Record Delegation
```http
POST /api/delegates
Content-Type: application/json

{
  "delegate_address": "0x123...",
  "delegator_address": "0x456...",
  "voting_power": 5000,
  "is_active": true
}
```

### Threads

#### Get Discussion Threads
```http
GET /api/threads?proposal_id=prop_001
```

#### Create Thread
```http
POST /api/threads
Content-Type: application/json

{
  "thread_id": "thread_001",
  "proposal_id": "prop_001",
  "title": "Discussion about budget allocation",
  "author": "0x789...",
  "content": "I think we should..."
}
```

### Webhook

#### Universal Data Ingestion
```http
POST /webhook/data
Content-Type: application/json

{
  "type": "proposal",
  "data": {
    "proposal_id": "prop_003",
    "title": "New Proposal",
    "status": "active"
  }
}
```

Supported types: `proposal`, `vote`, `delegate`, `thread`

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI 0.109.0, Python 3.9+ |
| **Database** | PostgreSQL via Supabase |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Charts** | Chart.js |
| **Automation** | n8n (optional) |
| **Deployment** | Railway/Fly.io (backend), Vercel (frontend) |

## 📁 Project Structure

```
dao-data-ai/
├── backend/
│   ├── main.py              # FastAPI application (228 lines)
│   └── requirements.txt     # Python dependencies
├── index.html               # Landing page (389 lines)
├── README.md                # This file
└── .env.example             # Environment variables template
```

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here
PORT=8000
```

## 🚢 Deployment

### Deploy Backend to Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and deploy:
```bash
railway login
cd backend
railway init
railway up
```

3. Add environment variables in Railway dashboard

### Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel --prod
```

3. Update API endpoint in deployed frontend

### Deploy Backend to Fly.io (Alternative)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and launch
fly auth login
cd backend
fly launch

# Set secrets
fly secrets set SUPABASE_URL=your_url
fly secrets set SUPABASE_KEY=your_key

# Deploy
fly deploy
```

## 📊 Features Roadmap

- ✅ Real-time proposal tracking
- ✅ Vote aggregation
- ✅ Delegate management  
- ✅ Discussion threads
- ✅ REST API
- ✅ Webhook integration
- ✅ Dark UI theme
- ✅ Responsive design
- 🔄 AI sentiment analysis (in progress)
- 🔄 Predictive modeling
- 📅 Multi-DAO support
- 📅 Advanced analytics dashboard
- 📅 Email notifications
- 📅 Mobile app

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

For questions and support:
- Open an issue on [GitHub](https://github.com/danvolsky-source/dao-data-ai/issues)
- Join our [Discord community](#)

## 🙏 Acknowledgments

- Built with ❤️ for the DAO ecosystem
- Powered by [Supabase](https://supabase.com)
- API framework by [FastAPI](https://fastapi.tiangolo.com)
- Charts by [Chart.js](https://www.chartjs.org)

---

**⭐ Star this repo if you find it useful!**
