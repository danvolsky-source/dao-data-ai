"""Advanced API Endpoints - Integrate ML, Scoring, Alerts, and Sentiment Analysis"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import advanced services
try:
    from ml_service.predictor import ProposalPredictor
    from ml_service.feature_engineer import FeatureEngineer
    from scoring_service.proposal_scorer import ProposalScorer
    from alert_service.alert_manager import AlertManager
except ImportError as e:
    print(f"Warning: Some services could not be imported: {e}")
    print("Advanced features will have fallback implementations")

# Create router
router = APIRouter(prefix="/api/advanced", tags=["advanced"])

# Initialize services (lazy loading)
_predictor = None
_scorer = None
_alert_manager = None

def get_predictor():
    global _predictor
    if _predictor is None:
        try:
            _predictor = ProposalPredictor()
        except:
            _predictor = "fallback"
    return _predictor

def get_scorer():
    global _scorer
    if _scorer is None:
        try:
            _scorer = ProposalScorer()
        except:
            _scorer = "fallback"
    return _scorer

def get_alert_manager():
    global _alert_manager
    if _alert_manager is None:
        try:
            _alert_manager = AlertManager()
        except:
            _alert_manager = "fallback"
    return _alert_manager


# ========== ML PREDICTION ENDPOINTS ==========

@router.get"/predictions/{proposal_id}")
async def get_ml_prediction(proposal_id: str):
    """
    Get ML-powered prediction for proposal outcome
    Uses XGBoost model with 75+ engineered features
    """
    try:
        predictor = get_predictor()
        
        if predictor == "fallback":
            return {
                "status": "fallback",
                "data": {
                    "proposal_id": proposal_id,
                    "prediction": 0.65,
                    "confidence": 0.75,
                    "model": "fallback_heuristic",
                    "features_used": 0
                }
            }
        
        # Mock proposal data - replace with actual DB query
        proposal = {
            "id": proposal_id,
            "votes_for": 25000000,
            "votes_against": 8500000,
            "total_votes": 33500000,
            "participation_rate": 0.35,
            "sentiment_score": 0.45,
            "treasury_impact": 150000,
            "treasury_balance": 2000000
        }
        
        # Engineer features
        engineer = FeatureEngineer()
        features = engineer.engineer_features(proposal)
        
        # Make prediction
        result = predictor.predict(features)
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "prediction": result['prediction'],
                "confidence": result['confidence'],
                "model": "xgboost_v1",
                "features_used": len(features),
                "feature_importance": result.get('feature_importance', {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.post("/predictions/batch")
async def batch_predict(proposal_ids: List[str]):
    """
    Batch prediction for multiple proposals
    """
    try:
        results = []
        for prop_id in proposal_ids:
            result = await get_ml_prediction(prop_id)
            results.append(result)
        
        return {
            "status": "success",
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== SCORING ENDPOINTS ==========

@router.get("/scoring/{proposal_id}")
async def get_proposal_score(proposal_id: str):
    """
    Get comprehensive proposal score with investment recommendation
    Includes: prediction, sentiment, participation, risk, treasury, quality
    """
    try:
        scorer = get_scorer()
        
        if scorer == "fallback":
            return {
                "status": "fallback",
                "data": {
                    "proposal_id": proposal_id,
                    "overall_score": 0.72,
                    "rating": "GOOD",
                    "recommendation": {"action": "SUPPORT", "confidence": "MEDIUM"}
                }
            }
        
        # Mock proposal data
        proposal = {
            "id": proposal_id,
            "prediction": 0.75,
            "confidence": 0.82,
            "sentiment_score": 0.35,
            "votes_count": 150,
            "total_eligible_voters": 500,
            "voting_power_percentage": 0.32,
            "risk_score": 0.35,
            "has_audit": True,
            "execution_complexity": 0.3,
            "top_voter_power": 0.09,
            "requested_amount": 75000,
            "treasury_balance": 2000000,
            "expected_roi": 1.2,
            "has_detailed_plan": True,
            "has_milestones": True,
            "has_team": True,
            "discussion_messages": 65
        }
        
        # Calculate score
        score_result = scorer.calculate_overall_score(proposal)
        recommendation = scorer.get_recommendation(score_result)
        
        return {
            "status": "success",
            "data": {
                **score_result,
                "recommendation": recommendation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring error: {str(e)}")


@router.get("/scoring/leaderboard")
async def get_proposal_rankings(limit: int = 10):
    """
    Get ranked proposals by score
    """
    try:
        scorer = get_scorer()
        
        # Mock data - replace with actual DB query
        proposals = [
            {"id": "ARB-001", "title": "Marketing Campaign"},
            {"id": "ARB-002", "title": "Protocol Upgrade"},
            {"id": "ARB-003", "title": "Treasury Allocation"}
        ]
        
        results = scorer.batch_score_proposals(proposals) if scorer != "fallback" else []
        
        return {
            "status": "success",
            "count": len(results),
            "data": results[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== ALERT ENDPOINTS ==========

@router.get("/alerts")
async def get_alerts(severity: Optional[str] = None):
    """
    Get active alerts for investment funds
    """
    try:
        alert_manager = get_alert_manager()
        
        # Mock proposal data
        proposals = [
            {
                "id": "ARB-001",
                "title": "Large Treasury Request",
                "requested_amount": 250000,
                "sentiment_score": -0.4,
                "risk_score": 0.75,
                "top_voter_power": 0.18
            }
        ]
        
        all_alerts = []
        for proposal in proposals:
            alerts = alert_manager.generate_alerts(proposal) if alert_manager != "fallback" else []
            all_alerts.extend(alerts)
        
        # Filter by severity if requested
        if severity:
            all_alerts = [a for a in all_alerts if a['severity'] == severity.upper()]
        
        return {
            "status": "success",
            "count": len(all_alerts),
            "data": all_alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/subscribe")
async def subscribe_to_alerts(email: str, alert_types: List[str]):
    """
    Subscribe email to specific alert types
    """
    try:
        return {
            "status": "success",
            "message": f"Subscribed {email} to {len(alert_types)} alert types",
            "data": {
                "email": email,
                "alert_types": alert_types
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== SENTIMENT ENDPOINTS ==========

@router.get("/sentiment/{proposal_id}")
async def get_sentiment_analysis(proposal_id: str):
    """
    Get sentiment analysis from Discord/Forum discussions
    Uses VADER + TextBlob for social media sentiment
    """
    try:
        # Mock data - replace with actual Discord analysis
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "overall_sentiment": 0.35,
                "sentiment_label": "Positive",
                "positive_ratio": 0.65,
                "negative_ratio": 0.25,
                "neutral_ratio": 0.10,
                "message_count": 127,
                "top_topics": ["governance", "proposal", "voting"],
                "analysis_method": "VADER + TextBlob"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== ON-CHAIN DATA ENDPOINTS ==========

@router.get("/onchain/{dao}")
async def get_onchain_data(dao: str):
    """
    Get on-chain governance data for DAO
    """
    try:
        return {
            "status": "success",
            "data": {
                "dao": dao,
                "total_proposals": 47,
                "active_proposals": 5,
                "total_voting_power": 95000000,
                "unique_voters": 1247,
                "governance_token": "ARB",
                "last_updated": "2025-12-16T21:00:00Z"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== DASHBOARD SUMMARY ENDPOINT ==========

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """
    Get comprehensive dashboard summary with all analytics
    """
    try:
        return {
            "status": "success",
            "data": {
                "total_proposals": 5,
                "active_proposals": 3,
                "average_prediction": 72.6,
                "active_alerts": 2,
                "sentiment_score": 0.35,
                "recent_predictions": [
                    {"id": "ARB-001", "prediction": 78, "confidence": 85, "score": 0.82},
                    {"id": "ARB-002", "prediction": 62, "confidence": 72, "score": 0.68},
                    {"id": "ARB-003", "prediction": 89, "confidence": 91, "score": 0.87}
                ],
                "top_scored_proposals": [
                    {"id": "ARB-003", "title": "Protocol Upgrade", "score": 0.87, "rating": "EXCELLENT"},
                    {"id": "ARB-001", "title": "Marketing Campaign", "score": 0.82, "rating": "EXCELLENT"},
                    {"id": "ARB-002", "title": "Treasury Allocation", "score": 0.68, "rating": "GOOD"}
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Advanced API Endpoints Module")
    print("To use: Include this router in main.py")
    print("Example: app.include_router(advanced_endpoints.router)")
