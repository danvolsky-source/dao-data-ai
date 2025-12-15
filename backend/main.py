from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
from supabase import create_client, Client

# Initialize FastAPI
app = FastAPI(title="DAO Analytics API", version="1.0.0")

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

@app.get("/api/voting-timeline")
async def get_voting_timeline(): 
        try:
        # Get votes count per day for last 30 days
        result = supabase.table("votes").select("created_at").execute()
        
        # Group by date in Python
        from collections import defaultdict
        votes_by_date = defaultdict(int)
        
        for vote in result.data:
            if vote.get('created_at'):
                date = vote['created_at'].split('T')[0]  # Get date part only
                votes_by_date[date] += 1
        
        # Convert to list and sort
        timeline_data = [{
            "date": date,
            "count": count
        } for date, count in sorted(votes_by_date.items(), reverse=True)[:30]]
        
        return {
            "status": "success",
            "data": timeline_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))f create_vote(vote: VoteCreate):
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
            raise HTTPException(status_code=400, detail="Unknown data type")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
