"""
Sentiment Analysis API Routes with Regulatory Compliance
Provides aggregated sentiment analysis from multiple sources
"""
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import os
from datetime import datetime, timedelta
from supabase import create_client, Client

# Import regulatory components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from regulatory.audit_logger import AuditLogger
from regulatory.disclaimers import wrap_response_with_disclaimer

# Initialize router
router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Initialize audit logger
audit_logger = AuditLogger(supabase) if supabase else None


# Pydantic models
class SentimentAnalysis(BaseModel):
    """Sentiment analysis response model"""
    proposal_id: str
    source: str
    sentiment_score: float = Field(..., ge=-1, le=1)
    message_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    analyzed_at: str
    metadata: Optional[Dict[str, Any]] = {}


class SentimentCreate(BaseModel):
    """Model for creating sentiment analysis entry"""
    proposal_id: str
    source: str = Field(..., description="Source: discord, forum, twitter, telegram, aggregated")
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment score from -1 to 1")
    message_count: int = Field(..., ge=0)
    positive_count: int = Field(..., ge=0)
    negative_count: int = Field(..., ge=0)
    neutral_count: int = Field(..., ge=0)
    metadata: Optional[Dict[str, Any]] = {}


@router.get("/{proposal_id}", response_model=Dict[str, Any])
async def get_sentiment_analysis(
    proposal_id: str,
    request: Request,
    source: Optional[str] = Query(None, description="Filter by source (discord, forum, twitter, etc.)")
):
    """
    Get sentiment analysis for a specific proposal
    
    ⚠️ REGULATORY DISCLAIMER:
    Sentiment analysis is based on public messages and may NOT reflect
    the true sentiment of the entire community. Use as ONE factor in
    your research, not as the sole basis for decisions.
    
    - NOT investment advice
    - NOT a complete view of community sentiment
    - Based on automated NLP analysis which may have errors
    
    Args:
        proposal_id: Unique identifier for the proposal
        source: Optional filter by source (discord, forum, twitter, telegram)
        request: FastAPI request object
    
    Returns:
        Sentiment analysis data with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Get client info for audit logging
        client_ip = request.client.host if request.client else "unknown"
        
        # Build query
        query = supabase.table("sentiment_analysis").select("*").eq("proposal_id", proposal_id)
        
        if source:
            query = query.eq("source", source)
        
        query = query.order("analyzed_at", desc=True)
        
        response = query.execute()
        
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No sentiment analysis found for proposal {proposal_id}"
            )
        
        # Log audit trail
        if audit_logger:
            await audit_logger.log_action(
                action="sentiment_viewed",
                resource_type="sentiment",
                user_id="anonymous",
                resource_id=proposal_id,
                ip_address=client_ip,
                details={"source_filter": source}
            )
        
        # Calculate aggregated sentiment if multiple sources
        if len(response.data) > 1:
            total_messages = sum(s.get("message_count", 0) for s in response.data)
            weighted_sentiment = sum(
                s.get("sentiment_score", 0) * s.get("message_count", 0) 
                for s in response.data
            ) / total_messages if total_messages > 0 else 0
            
            result = {
                "proposal_id": proposal_id,
                "aggregated_sentiment": round(weighted_sentiment, 4),
                "total_messages": total_messages,
                "sources": len(response.data),
                "by_source": response.data,
                "sentiment_trend": _get_sentiment_trend(weighted_sentiment)
            }
        else:
            sentiment_data = response.data[0]
            result = {
                "proposal_id": proposal_id,
                "source": sentiment_data.get("source"),
                "sentiment_score": sentiment_data.get("sentiment_score"),
                "message_count": sentiment_data.get("message_count"),
                "positive_count": sentiment_data.get("positive_count"),
                "negative_count": sentiment_data.get("negative_count"),
                "neutral_count": sentiment_data.get("neutral_count"),
                "analyzed_at": sentiment_data.get("analyzed_at"),
                "sentiment_trend": _get_sentiment_trend(sentiment_data.get("sentiment_score", 0)),
                "metadata": sentiment_data.get("metadata", {})
            }
        
        return wrap_response_with_disclaimer(result, "sentiment")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sentiment analysis: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_sentiment_analysis(
    sentiment: SentimentCreate,
    request: Request
):
    """
    Create a new sentiment analysis entry (Internal use only)
    
    Args:
        sentiment: Sentiment analysis data
        request: FastAPI request object
    
    Returns:
        Created sentiment analysis with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Validate sentiment data
        if sentiment.positive_count + sentiment.negative_count + sentiment.neutral_count != sentiment.message_count:
            raise HTTPException(
                status_code=400,
                detail="Sum of positive, negative, and neutral counts must equal message_count"
            )
        
        # Prepare data
        sentiment_data = {
            "proposal_id": sentiment.proposal_id,
            "source": sentiment.source,
            "sentiment_score": sentiment.sentiment_score,
            "message_count": sentiment.message_count,
            "positive_count": sentiment.positive_count,
            "negative_count": sentiment.negative_count,
            "neutral_count": sentiment.neutral_count,
            "analyzed_at": datetime.utcnow().isoformat(),
            "metadata": sentiment.metadata
        }
        
        # Insert into database
        response = supabase.table("sentiment_analysis").insert(sentiment_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create sentiment analysis")
        
        # Log audit trail
        if audit_logger:
            await audit_logger.log_sentiment_analysis(
                proposal_id=sentiment.proposal_id,
                source=sentiment.source,
                sentiment_score=sentiment.sentiment_score,
                message_count=sentiment.message_count
            )
        
        return wrap_response_with_disclaimer(response.data[0], "sentiment")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sentiment analysis: {str(e)}")


@router.get("/aggregate/{proposal_id}", response_model=Dict[str, Any])
async def get_aggregated_sentiment(proposal_id: str):
    """
    Get aggregated sentiment across all sources for a proposal
    
    Combines sentiment from Discord, forums, Twitter, etc. into a single score.
    Weighted by message count for more accurate representation.
    
    ⚠️ DISCLAIMER: Aggregated sentiment may still not represent full community opinion
    
    Args:
        proposal_id: Unique identifier for the proposal
    
    Returns:
        Aggregated sentiment with breakdown by source
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Fetch all sentiment data for proposal
        response = (
            supabase.table("sentiment_analysis")
            .select("*")
            .eq("proposal_id", proposal_id)
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No sentiment data found for proposal {proposal_id}"
            )
        
        # Calculate aggregated metrics
        total_messages = sum(s.get("message_count", 0) for s in response.data)
        total_positive = sum(s.get("positive_count", 0) for s in response.data)
        total_negative = sum(s.get("negative_count", 0) for s in response.data)
        total_neutral = sum(s.get("neutral_count", 0) for s in response.data)
        
        # Weighted sentiment score
        weighted_sentiment = sum(
            s.get("sentiment_score", 0) * s.get("message_count", 0) 
            for s in response.data
        ) / total_messages if total_messages > 0 else 0
        
        # Calculate ratios
        positive_ratio = total_positive / total_messages if total_messages > 0 else 0
        negative_ratio = total_negative / total_messages if total_messages > 0 else 0
        neutral_ratio = total_neutral / total_messages if total_messages > 0 else 0
        
        # Group by source
        by_source = {}
        for s in response.data:
            source = s.get("source", "unknown")
            by_source[source] = {
                "sentiment_score": s.get("sentiment_score"),
                "message_count": s.get("message_count"),
                "positive_count": s.get("positive_count"),
                "negative_count": s.get("negative_count"),
                "neutral_count": s.get("neutral_count"),
                "analyzed_at": s.get("analyzed_at")
            }
        
        result = {
            "proposal_id": proposal_id,
            "aggregated_sentiment_score": round(weighted_sentiment, 4),
            "sentiment_trend": _get_sentiment_trend(weighted_sentiment),
            "total_messages_analyzed": total_messages,
            "positive_ratio": round(positive_ratio, 4),
            "negative_ratio": round(negative_ratio, 4),
            "neutral_ratio": round(neutral_ratio, 4),
            "sources_count": len(by_source),
            "by_source": by_source,
            "last_analyzed": max(s.get("analyzed_at", "") for s in response.data)
        }
        
        return wrap_response_with_disclaimer(result, "sentiment")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating aggregated sentiment: {str(e)}")


@router.get("/trending/proposals", response_model=Dict[str, Any])
async def get_trending_sentiment():
    """
    Get sentiment trends across recent proposals
    
    Shows which proposals have the most positive/negative sentiment.
    Useful for identifying controversial or popular proposals.
    
    Returns:
        List of proposals sorted by sentiment activity
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Get sentiment from last 30 days
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        response = (
            supabase.table("sentiment_analysis")
            .select("*")
            .gte("analyzed_at", thirty_days_ago)
            .execute()
        )
        
        if not response.data:
            return wrap_response_with_disclaimer({
                "message": "No recent sentiment data available",
                "proposals": []
            }, "sentiment")
        
        # Group by proposal_id
        by_proposal = {}
        for s in response.data:
            proposal_id = s.get("proposal_id")
            if proposal_id not in by_proposal:
                by_proposal[proposal_id] = {
                    "proposal_id": proposal_id,
                    "total_messages": 0,
                    "sentiment_scores": [],
                    "sources": set()
                }
            by_proposal[proposal_id]["total_messages"] += s.get("message_count", 0)
            by_proposal[proposal_id]["sentiment_scores"].append(
                (s.get("sentiment_score", 0), s.get("message_count", 0))
            )
            by_proposal[proposal_id]["sources"].add(s.get("source"))
        
        # Calculate weighted sentiment for each proposal
        trending = []
        for proposal_id, data in by_proposal.items():
            total_messages = data["total_messages"]
            weighted_sentiment = sum(
                score * count for score, count in data["sentiment_scores"]
            ) / total_messages if total_messages > 0 else 0
            
            trending.append({
                "proposal_id": proposal_id,
                "sentiment_score": round(weighted_sentiment, 4),
                "total_messages": total_messages,
                "sources_count": len(data["sources"]),
                "sentiment_trend": _get_sentiment_trend(weighted_sentiment)
            })
        
        # Sort by total messages (activity)
        trending.sort(key=lambda x: x["total_messages"], reverse=True)
        
        result = {
            "period": "last_30_days",
            "total_proposals": len(trending),
            "most_active": trending[:10],
            "most_positive": sorted(trending, key=lambda x: x["sentiment_score"], reverse=True)[:5],
            "most_negative": sorted(trending, key=lambda x: x["sentiment_score"])[:5]
        }
        
        return wrap_response_with_disclaimer(result, "sentiment")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending sentiment: {str(e)}")


def _get_sentiment_trend(sentiment_score: float) -> str:
    """
    Convert sentiment score to human-readable trend
    
    Args:
        sentiment_score: Sentiment score from -1 to 1
    
    Returns:
        Trend description
    """
    if sentiment_score >= 0.5:
        return "Very Positive"
    elif sentiment_score >= 0.2:
        return "Positive"
    elif sentiment_score >= -0.2:
        return "Neutral"
    elif sentiment_score >= -0.5:
        return "Negative"
    else:
        return "Very Negative"
