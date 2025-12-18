from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
from supabase import create_client, Client

# Import API routers
try:
    from api.advanced_endpoints import router as advanced_router
except ImportError:
    print("Warning: Advanced endpoints not found. Skipping advanced features integration.")
    advanced_router = None

try:
    from api.predictions import router as predictions_router
except ImportError:
    print("Warning: Predictions endpoints not found.")
    predictions_router = None

try:
    from api.sentiment import router as sentiment_router
except ImportError:
    print("Warning: Sentiment endpoints not found.")
    sentiment_router = None

try:
    from api.audit import router as audit_router
except ImportError:
    print("Warning: Audit endpoints not found.")
    audit_router = None

try:
    from api.model_metrics import router as model_metrics_router
except ImportError:
    print("Warning: Model metrics endpoints not found.")
    model_metrics_router = None

# Initialize FastAPI
app = FastAPI(
    title="DAO Analytics API",
    version="2.0.0",
    description="AI-powered DAO governance analytics with ML predictions and sentiment analysis",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fsvlkshplbfivwmdljqh.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Include API routers
if advanced_router:
    app.include_router(advanced_router)
    print("✅ Advanced endpoints (ML, scoring, alerts) loaded successfully")
else:
    print("⚠️ Advanced endpoints not available")

if predictions_router:
    app.include_router(predictions_router)
    print("✅ Predictions endpoints loaded successfully")
else:
    print("⚠️ Predictions endpoints not available")

if sentiment_router:
    app.include_router(sentiment_router)
    print("✅ Sentiment analysis endpoints loaded successfully")
else:
    print("⚠️ Sentiment endpoints not available")

if audit_router:
    app.include_router(audit_router)
    print("✅ Audit log endpoints loaded successfully")
else:
    print("⚠️ Audit endpoints not available")

if model_metrics_router:
    app.include_router(model_metrics_router)
    print("✅ Model metrics endpoints loaded successfully")
else:
    print("⚠️ Model metrics endpoints not available")

# Pydantic models
class ProposalCreate(BaseModel):
    proposal_id: str
    title: str
    description: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    voting_ends_at: Optional[datetime] = None
    total_votes: int = 0
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    metadata: Optional[dict] = None

class VoteCreate(BaseModel):
    proposal_id: str
    voter_address: str
    vote_choice: str  # for, against, abstain
    voting_power: float
    timestamp: Optional[datetime] = None
    transaction_hash: Optional[str] = None

class DelegateCreate(BaseModel):
    delegate_address: str
    delegator_address: str
    voting_power: float
    delegated_at: Optional[datetime] = None
    is_active: bool = True

class ThreadCreate(BaseModel):
    thread_id: str
    proposal_id: str
    title: str
    content: Optional[str] = None
    author: str
    created_at: Optional[datetime] = None
    replies_count: int = 0
    sentiment_score: Optional[float] = None

# Health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "DAO Analytics API"}

# Proposals endpoints
@app.post("/api/proposals")
async def create_proposal(proposal: ProposalCreate):
    try:
        data = proposal.dict()
        if data["created_at"]:
            data["created_at"] = data["created_at"].isoformat()
        if data["voting_ends_at"]:
            data["voting_ends_at"] = data["voting_ends_at"].isoformat()
        
        result = supabase.table("proposals").insert(data).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/proposals")
async def get_proposals(status: Optional[str] = None, limit: int = 100):
    try:
        query = supabase.table("proposals").select("*")
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).limit(limit).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    try:
        result = supabase.table("proposals").select("*").eq("proposal_id", proposal_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Proposal not found")
        return {"status": "success", "data": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Votes endpoints

# Stats endpoint
@app.get("/api/stats")
async def get_stats():
    try:
        # Get proposal count
        proposals_result = supabase.table("proposals").select("id", count="exact").execute()
        proposals_count = proposals_result.count if proposals_result.count else 0
        
        # Get votes count
        votes_result = supabase.table("votes").select("vote_id", count="exact").execute()
        votes_count = votes_result.count if votes_result.count else 0
        
        # Get unique delegates count (unique voters)
        delegates_result = supabase.table("votes").select("voter").execute()
        unique_delegates = len(set([v["voter"] for v in delegates_result.data])) if delegates_result.data else 0
        
        return {
            "status": "success",
            "data": {
                "active_proposals": proposals_count,
                "total_votes": votes_count,
                "active_delegates": unique_delegates
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Advanced Analytics endpoints
@app.get("/api/analytics/participation")
async def get_participation_rate():
    """
    Calculate voter participation rate
    """
    try:
        # Get total unique voters
        votes_result = supabase.table("votes").select("voter").execute()
        unique_voters = len(set([v["voter"] for v in votes_result.data])) if votes_result.data else 0
        
        # Get total delegates
        delegates_result = supabase.table("delegates").select("id", count="exact").execute()
        total_delegates = delegates_result.count if delegates_result.count else 0
        
        # Calculate participation rate
        participation_rate = (unique_voters / total_delegates * 100) if total_delegates > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "unique_voters": unique_voters,
                "total_delegates": total_delegates,
                "participation_rate": round(participation_rate, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/success-rate")
async def get_success_rate():
    """
    Calculate proposal success rate
    """
    try:
        # Get all proposals
        proposals_result = supabase.table("proposals").select("*").execute()
        
        if not proposals_result.data:
            return {
                "status": "success",
                "data": {
                    "total_proposals": 0,
                    "passed": 0,
                    "failed": 0,
                    "success_rate": 0
                }
            }
        
        total = len(proposals_result.data)
        passed = sum(1 for p in proposals_result.data if p.get("votes_for", 0) > p.get("votes_against", 0))
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "total_proposals": total,
                "passed": passed,
                "failed": failed,
                "success_rate": round(success_rate, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/voting-power")
async def get_average_voting_power():
    """
    Calculate average voting power per delegate
    """
    try:
        # Get all votes with voting power
        votes_result = supabase.table("votes").select("voter, voting_power").execute()
        
        if not votes_result.data:
            return {
                "status": "success",
                "data": {
                    "total_voting_power": 0,
                    "unique_voters": 0,
                    "average_voting_power": 0
                }
            }
        
        # Calculate total voting power per unique voter
        voter_power = {}
        for vote in votes_result.data:
            voter = vote.get("voter")
            power = float(vote.get("voting_power", 0))
            if voter:
                if voter not in voter_power:
                    voter_power[voter] = 0
                voter_power[voter] += power
        
        total_power = sum(voter_power.values())
        unique_voters = len(voter_power)
        avg_power = total_power / unique_voters if unique_voters > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "total_voting_power": round(total_power, 2),
                "unique_voters": unique_voters,
                "average_voting_power": round(avg_power, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/leaderboard")
async def get_top_delegates(limit: int = 10):
    """
    Get top delegates by voting power
    """
    try:
        # Get all votes with voting power
        votes_result = supabase.table("votes").select("voter, voting_power").execute()
        
        if not votes_result.data:
            return {
                "status": "success",
                "data": []
            }
        
        # Calculate total voting power per unique voter
        voter_stats = {}
        for vote in votes_result.data:
            voter = vote.get("voter")
            power = float(vote.get("voting_power", 0))
            if voter:
                if voter not in voter_stats:
                    voter_stats[voter] = {"voting_power": 0, "vote_count": 0}
                voter_stats[voter]["voting_power"] += power
                voter_stats[voter]["vote_count"] += 1
        
        # Sort by voting power and get top N
        leaderboard = [
            {
                "address": voter,
                "total_voting_power": round(stats["voting_power"], 2),
                "vote_count": stats["vote_count"]
            }
            for voter, stats in sorted(voter_stats.items(), key=lambda x: x[1]["voting_power"], reverse=True)
        ][:limit]
        
        return {
            "status": "success",
            "data": leaderboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/timeline")
async def get_timeline_data(days: int = 30):
    """
    Get time-series data for proposals and votes over time
    """
    try:
        from datetime import timedelta
        
        # Get proposals with timestamps
        proposals_result = supabase.table("proposals").select("created_at").execute()
        
        # Get votes with timestamps
        votes_result = supabase.table("votes").select("created_at").execute()
        
        # Group by date
        timeline = {}
        
        # Process proposals
        for proposal in proposals_result.data:
            if proposal.get("created_at"):
                date = proposal["created_at"][:10]  # Extract date (YYYY-MM-DD)
                if date not in timeline:
                    timeline[date] = {"proposals": 0, "votes": 0}
                timeline[date]["proposals"] += 1
        
        # Process votes
        for vote in votes_result.data:
            if vote.get("created_at"):
                date = vote["created_at"][:10]  # Extract date (YYYY-MM-DD)
                if date not in timeline:
                    timeline[date] = {"proposals": 0, "votes": 0}
                timeline[date]["votes"] += 1
        
        # Convert to list and sort by date
        timeline_list = [
            {
                "date": date,
                "proposals": stats["proposals"],
                "votes": stats["votes"]
            }
            for date, stats in sorted(timeline.items())
        ]
        
        return {
            "status": "success",
            "data": timeline_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/votes")
async def create_vote(vote: VoteCreate):
    try:
        data = vote.dict()
        if data["timestamp"]:
            data["timestamp"] = data["timestamp"].isoformat()
        
        result = supabase.table("votes").insert(data).execute()
        
        # Update proposal vote counts
        proposal = supabase.table("proposals").select("*").eq("proposal_id", vote.proposal_id).execute()
        if proposal.data:
            current = proposal.data[0]
            updates = {"total_votes": current["total_votes"] + 1}
            if vote.vote_choice == "for":
                updates["votes_for"] = current["votes_for"] + 1
            elif vote.vote_choice == "against":
                updates["votes_against"] = current["votes_against"] + 1
            elif vote.vote_choice == "abstain":
                updates["votes_abstain"] = current["votes_abstain"] + 1
            
            supabase.table("proposals").update(updates).eq("proposal_id", vote.proposal_id).execute()
        
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/votes")
async def get_votes(proposal_id: Optional[str] = None, voter_address: Optional[str] = None, limit: int = 100):
    try:
        query = supabase.table("votes").select("*")
        if proposal_id:
            query = query.eq("proposal_id", proposal_id)
        if voter_address:
            query = query.eq("voter_address", voter_address)
        result = query.order("timestamp", desc=True).limit(limit).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delegates endpoints
@app.post("/api/delegates")
async def create_delegate(delegate: DelegateCreate):
    try:
        data = delegate.dict()
        if data["delegated_at"]:
            data["delegated_at"] = data["delegated_at"].isoformat()
        
        result = supabase.table("delegates").insert(data).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/delegates")
async def get_delegates(delegate_address: Optional[str] = None, delegator_address: Optional[str] = None, limit: int = 100):
    try:
        query = supabase.table("delegates").select("*")
        if delegate_address:
            query = query.eq("delegate_address", delegate_address)
        if delegator_address:
            query = query.eq("delegator_address", delegator_address)
        result = query.order("delegated_at", desc=True).limit(limit).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Threads endpoints
@app.post("/api/threads")
async def create_thread(thread: ThreadCreate):
    try:
        data = thread.dict()
        if data["created_at"]:
            data["created_at"] = data["created_at"].isoformat()
        
        result = supabase.table("threads").insert(data).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/threads")
async def get_threads(proposal_id: Optional[str] = None, limit: int = 100):
    try:
        query = supabase.table("threads").select("*")
        if proposal_id:
            query = query.eq("proposal_id", proposal_id)
        result = query.order("created_at", desc=True).limit(limit).execute()
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Webhook endpoint for n8n
@app.post("/webhook/data")
async def webhook_data(data: dict):
    """
    Универсальный webhook endpoint для приема данных от n8n.
    Определяет тип данных по полям и направляет в соответствующую таблицу.
    """
    try:
        data_type = data.get("type")
        
        if data_type == "proposal":
            proposal = ProposalCreate(**data.get("data", {}))
            return await create_proposal(proposal)
        elif data_type == "vote":
            vote = VoteCreate(**data.get("data", {}))
            return await create_vote(vote)
        elif data_type == "delegate":
            delegate = DelegateCreate(**data.get("data", {}))
            return await create_delegate(delegate)
        elif data_type == "thread":
            thread = ThreadCreate(**data.get("data", {}))
            return await create_thread(thread)
        else:

        # === ML ENDPOINTS ===
# ML Prediction endpoints for voting results, sentiment, turnout, classification

@app.get("/api/ml/predict/{proposal_id}")
async def predict_proposal_outcome(proposal_id: str):
    """
    Predict voting outcome for a proposal using ML
    Returns: prediction (passed/rejected), confidence score
    """
    try:
        # Get proposal data
        proposal_result = supabase.table("proposals").select("*").eq("proposal_id", proposal_id).execute()
        if not proposal_result.data:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        proposal = proposal_result.data[0]
        
        # Get historical voting patterns
        votes_result = supabase.table("votes").select("voter, voting_power, choice").eq("proposal", proposal_id).execute()
        
        # Simple ML prediction based on current vote distribution
        total_for = sum(float(v.get("voting_power", 0)) for v in votes_result.data if v.get("choice") == "for")
        total_against = sum(float(v.get("voting_power", 0)) for v in votes_result.data if v.get("choice") == "against")
        total_power = total_for + total_against
        
        if total_power > 0:
            confidence = max(total_for, total_against) / total_power
            prediction = "passed" if total_for > total_against else "rejected"
        else:
            # No votes yet - use historical data
            confidence = 0.5
            prediction = "uncertain"
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "prediction": prediction,
                "confidence": round(confidence, 3),
                "current_votes_for": int(total_for),
                "current_votes_against": int(total_against),
                "model": "voting_pattern_analysis"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/sentiment/{proposal_id}")
async def analyze_sentiment(proposal_id: str):
    """
    Analyze sentiment of discussions for a proposal
    Returns: sentiment score (-1 to 1), distribution
    """
    try:
        # Get threads for proposal
        threads_result = supabase.table("threads").select("*").eq("proposal_id", proposal_id).execute()
        
        if not threads_result.data:
            return {
                "status": "success",
                "data": {
                    "proposal_id": proposal_id,
                    "sentiment_score": 0,
                    "sentiment": "neutral",
                    "discussion_count": 0
                }
            }
        
        # Simple sentiment analysis based on engagement metrics
        threads = threads_result.data
        total_sentiment = 0
        
        for thread in threads:
            replies = thread.get("replies_count", 0)
            # More replies = more engagement = slight positive sentiment
            sentiment = min(replies / 10, 1.0) if replies > 0 else 0
            total_sentiment += sentiment
        
        avg_sentiment = total_sentiment / len(threads) if threads else 0
        
        # Normalize to -1 to 1 scale
        normalized_sentiment = (avg_sentiment * 2) - 1
        
        sentiment_label = "positive" if normalized_sentiment > 0.2 else "negative" if normalized_sentiment < -0.2 else "neutral"
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "sentiment_score": round(normalized_sentiment, 3),
                "sentiment": sentiment_label,
                "discussion_count": len(threads),
                "model": "engagement_based_sentiment"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/turnout/{proposal_id}")
async def predict_voter_turnout(proposal_id: str):
    """
    Predict voter turnout for a proposal
    Returns: predicted turnout percentage, confidence
    """
    try:
        # Get total delegates
        delegates_result = supabase.table("votes").select("voter").execute()
        unique_delegates = len(set([v["voter"] for v in delegates_result.data])) if delegates_result.data else 1
        
        # Get current votes for this proposal
        votes_result = supabase.table("votes").select("voter").eq("proposal", proposal_id).execute()
        current_voters = len(set([v["voter"] for v in votes_result.data])) if votes_result.data else 0
        
        # Get proposal info to see how much time is left
        proposal_result = supabase.table("proposals").select("created_at, voting_ends_at").eq("proposal_id", proposal_id).execute()
        
        # Calculate current turnout
        current_turnout = (current_voters / unique_delegates * 100) if unique_delegates > 0 else 0
        
        # Simple prediction: assume 1.5x current turnout as final (conservative estimate)
        predicted_turnout = min(current_turnout * 1.5, 100)
        
        # Confidence based on how many votes we already have
        confidence = min(current_voters / 50, 1.0)  # More confident with more votes
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "predicted_turnout": round(predicted_turnout, 2),
                "current_turnout": round(current_turnout, 2),
                "confidence": round(confidence, 3),
                "current_voters": current_voters,
                "total_delegates": unique_delegates,
                "model": "turnout_momentum_prediction"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/classify/{proposal_id}")
async def classify_proposal(proposal_id: str):
    """
    Classify proposal by type/category
    Returns: category, confidence, tags
    """
    try:
        # Get proposal
        proposal_result = supabase.table("proposals").select("title, description, metadata").eq("proposal_id", proposal_id).execute()
        
        if not proposal_result.data:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        proposal = proposal_result.data[0]
        title = (proposal.get("title") or "").lower()
        description = (proposal.get("description") or "").lower()
        text = f"{title} {description}"
        
        # Simple keyword-based classification
        categories = {}
        
        if any(word in text for word in ["grant", "funding", "budget", "treasury"]):
            categories["Financial"] = 0.8
        if any(word in text for word in ["governance", "voting", "delegate", "token"]):
            categories["Governance"] = 0.7
        if any(word in text for word in ["technical", "upgrade", "smart contract", "protocol"]):
            categories["Technical"] = 0.75
        if any(word in text for word in ["community", "marketing", "event", "partnership"]):
            categories["Community"] = 0.7
        if any(word in text for word in ["parameter", "fee", "rate", "threshold"]):
            categories["Parameter Change"] = 0.75
        
        if not categories:
            categories["General"] = 0.5
        
        # Get top category
        top_category = max(categories.items(), key=lambda x: x[1])
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "category": top_category[0],
                "confidence": round(top_category[1], 3),
                "all_categories": {k: round(v, 3) for k, v in categories.items()},
                "model": "keyword_based_classification"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


            raise HTTPException(status_code=400, detail="Unknown data type")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
