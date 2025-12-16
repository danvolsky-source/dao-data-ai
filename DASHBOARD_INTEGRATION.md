# Dashboard Integration Guide

## Этап 3: Dashboard Integration Complete

This guide shows how to integrate all the advanced services (ML predictions, scoring, alerts, sentiment) into the frontend dashboard.

---

## New API Endpoints Available

All new endpoints are available at `/api/advanced/*`

### 1. ML Predictions
```typescript
// Get ML prediction for a proposal
GET /api/advanced/predictions/{proposal_id}

Response:
{
  "status": "success",
  "data": {
    "proposal_id": "ARB-001",
    "prediction": 0.78,
    "confidence": 0.85,
    "model": "xgboost_v1",
    "features_used": 75
  }
}

// Batch predictions
POST /api/advanced/predictions/batch
Body: ["ARB-001", "ARB-002", "ARB-003"]
```

### 2. Proposal Scoring
```typescript
// Get comprehensive score
GET /api/advanced/scoring/{proposal_id}

Response:
{
  "status": "success",
  "data": {
    "proposal_id": "ARB-001",
    "overall_score": 0.82,
    "rating": "EXCELLENT",
    "component_scores": {
      "prediction_confidence": 0.85,
      "sentiment": 0.75,
      "participation": 0.82,
      "risk_assessment": 0.78,
      "treasury_impact": 0.90,
      "execution_quality": 0.80
    },
    "recommendation": {
      "action": "STRONG_SUPPORT",
      "confidence": "HIGH",
      "message": "This proposal shows excellent metrics..."
    }
  }
}

// Get rankings
GET /api/advanced/scoring/leaderboard?limit=10
```

### 3. Alerts
```typescript
// Get active alerts
GET /api/advanced/alerts?severity=HIGH

Response:
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "type": "LARGE_TREASURY_REQUEST",
      "severity": "CRITICAL",
      "message": "Proposal ARB-001: Requesting $250,000 from treasury"
    },
    {
      "type": "NEGATIVE_SENTIMENT",
      "severity": "MEDIUM",
      "message": "Proposal ARB-001: Negative community sentiment (-0.4)"
    }
  ]
}

// Subscribe to alerts
POST /api/advanced/alerts/subscribe
Body: {"email": "fund@example.com", "alert_types": ["CRITICAL", "HIGH"]}
```

### 4. Sentiment Analysis
```typescript
// Get sentiment
GET /api/advanced/sentiment/{proposal_id}

Response:
{
  "status": "success",
  "data": {
    "proposal_id": "ARB-001",
    "overall_sentiment": 0.35,
    "sentiment_label": "Positive",
    "positive_ratio": 0.65,
    "negative_ratio": 0.25,
    "message_count": 127,
    "top_topics": ["governance", "proposal", "voting"],
    "analysis_method": "VADER + TextBlob"
  }
}
```

### 5. On-Chain Data
```typescript
// Get on-chain governance data
GET /api/advanced/onchain/arbitrum

Response:
{
  "status": "success",
  "data": {
    "dao": "arbitrum",
    "total_proposals": 47,
    "active_proposals": 5,
    "total_voting_power": 95000000,
    "unique_voters": 1247,
    "governance_token": "ARB"
  }
}
```

### 6. Dashboard Summary
```typescript
// Get complete dashboard summary
GET /api/advanced/dashboard/summary

Response:
{
  "status": "success",
  "data": {
    "total_proposals": 5,
    "active_proposals": 3,
    "average_prediction": 72.6,
    "active_alerts": 2,
    "sentiment_score": 0.35,
    "recent_predictions": [...],
    "top_scored_proposals": [...]
  }
}
```

---

## Frontend Integration Steps

### Step 1: Update API Service

Create `app/lib/advancedApi.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getPrediction(proposalId: string) {
  const res = await fetch(`${API_BASE}/api/advanced/predictions/${proposalId}`);
  return res.json();
}

export async function getScore(proposalId: string) {
  const res = await fetch(`${API_BASE}/api/advanced/scoring/${proposalId}`);
  return res.json();
}

export async function getAlerts(severity?: string) {
  const url = severity 
    ? `${API_BASE}/api/advanced/alerts?severity=${severity}`
    : `${API_BASE}/api/advanced/alerts`;
  const res = await fetch(url);
  return res.json();
}

export async function getSentiment(proposalId: string) {
  const res = await fetch(`${API_BASE}/api/advanced/sentiment/${proposalId}`);
  return res.json();
}

export async function getDashboardSummary() {
  const res = await fetch(`${API_BASE}/api/advanced/dashboard/summary`);
  return res.json();
}
```

### Step 2: Create New Components

#### `app/components/PredictionBadge.tsx`
```typescript
"use client";

interface PredictionBadgeProps {
  prediction: number;
  confidence: number;
}

export default function PredictionBadge({ prediction, confidence }: PredictionBadgeProps) {
  const percentage = Math.round(prediction * 100);
  const color = prediction > 0.7 ? 'green' : prediction > 0.5 ? 'yellow' : 'red';
  
  return (
    <div className={`badge badge-${color}`}>
      <span className="text-lg font-bold">{percentage}%</span>
      <span className="text-sm ml-2">Confidence: {Math.round(confidence * 100)}%</span>
    </div>
  );
}
```

#### `app/components/ScoreBadge.tsx`
```typescript
"use client";

interface ScoreBadgeProps {
  rating: string;
  score: number;
  recommendation: {
    action: string;
    confidence: string;
  };
}

export default function ScoreBadge({ rating, score, recommendation }: ScoreBadgeProps) {
  const colorMap = {
    'EXCELLENT': 'green',
    'GOOD': 'blue',
    'MODERATE': 'yellow',
    'POOR': 'orange',
    'CRITICAL': 'red'
  };
  
  return (
    <div className={`score-badge badge-${colorMap[rating]}`}>
      <div className="text-2xl font-bold">{rating}</div>
      <div className="text-lg">{Math.round(score * 100)}/100</div>
      <div className="text-sm mt-2">
        <strong>{recommendation.action}</strong>
        <span className="ml-2">({recommendation.confidence})</span>
      </div>
    </div>
  );
}
```

#### `app/components/AlertsList.tsx`
```typescript
"use client";
import { useEffect, useState } from 'react';
import { getAlerts } from '@/lib/advancedApi';

export default function AlertsList() {
  const [alerts, setAlerts] = useState([]);
  
  useEffect(() => {
    getAlerts().then(data => setAlerts(data.data || []));
  }, []);
  
  return (
    <div className="alerts-container">
      <h3 className="text-xl font-bold mb-4">Active Alerts</h3>
      {alerts.map((alert, idx) => (
        <div key={idx} className={`alert alert-${alert.severity.toLowerCase()}`}>
          <strong>[{alert.severity}] {alert.type}</strong>
          <p>{alert.message}</p>
        </div>
      ))}
    </div>
  );
}
```

#### `app/components/SentimentGauge.tsx`
```typescript
"use client";

interface SentimentGaugeProps {
  score: number;
  label: string;
}

export default function SentimentGauge({ score, label }: SentimentGaugeProps) {
  // Convert -1 to 1 scale to 0-100
  const percentage = ((score + 1) / 2) * 100;
  
  return (
    <div className="sentiment-gauge">
      <div className="text-lg font-semibold">{label}</div>
      <div className="gauge-bar">
        <div 
          className="gauge-fill" 
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="text-sm text-gray-600">Score: {score.toFixed(2)}</div>
    </div>
  );
}
```

### Step 3: Update Main Dashboard

#### `app/page.tsx` additions:
```typescript
import { getDashboardSummary } from '@/lib/advancedApi';
import AlertsList from '@/components/AlertsList';
import PredictionBadge from '@/components/PredictionBadge';
import ScoreBadge from '@/components/ScoreBadge';
import SentimentGauge from '@/components/SentimentGauge';

// Add to page component
const summary = await getDashboardSummary();

// Update proposals table to include predictions and scores
<table>
  <thead>
    <tr>
      <th>Title</th>
      <th>Status</th>
      <th>AI Prediction</th>
      <th>Score</th>
      <th>Sentiment</th>
    </tr>
  </thead>
  <tbody>
    {proposals.map(proposal => (
      <tr key={proposal.id}>
        <td>{proposal.title}</td>
        <td>{proposal.status}</td>
        <td>
          <PredictionBadge 
            prediction={proposal.prediction} 
            confidence={proposal.confidence} 
          />
        </td>
        <td>
          <ScoreBadge 
            rating={proposal.rating}
            score={proposal.score}
            recommendation={proposal.recommendation}
          />
        </td>
        <td>
          <SentimentGauge 
            score={proposal.sentiment_score}
            label={proposal.sentiment_label}
          />
        </td>
      </tr>
    ))}
  </tbody>
</table>

// Add alerts sidebar
<div className="sidebar">
  <AlertsList />
</div>
```

---

## Backend Integration

### Update `backend/main.py`:

```python
from api.advanced_endpoints import router as advanced_router

# Add this line after app initialization
app.include_router(advanced_router)
```

---

## Testing

### Test Endpoints:
```bash
# Test prediction
curl http://localhost:8000/api/advanced/predictions/ARB-001

# Test scoring
curl http://localhost:8000/api/advanced/scoring/ARB-001

# Test alerts
curl http://localhost:8000/api/advanced/alerts

# Test sentiment
curl http://localhost:8000/api/advanced/sentiment/ARB-001

# Test dashboard summary
curl http://localhost:8000/api/advanced/dashboard/summary
```

---

## Deployment

### Environment Variables (Vercel):
```bash
NEXT_PUBLIC_API_URL=https://api.dao-data-ai.com
DATABASE_URL=postgresql://...
ARBITRUM_RPC_URL=https://...
DISCORD_TOKEN=...
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=...
SMTP_PASSWORD=...
SENTRY_DSN=...
```

### Deploy:
```bash
# Push to GitHub
git add .
git commit -m "Integrate advanced analytics into dashboard"
git push

# Vercel will auto-deploy
```

---

## Status: ✅ Dashboard Integration Ready

All APIs and integration code are ready. The dashboard can now display:
- ✅ ML Predictions with confidence scores
- ✅ Comprehensive proposal scores and recommendations
- ✅ Real-time alerts for investment funds
- ✅ Sentiment analysis from Discord/Forums
- ✅ On-chain governance metrics
- ✅ Complete dashboard summary endpoint

**Next:** Frontend development to consume these APIs and display the advanced analytics.
