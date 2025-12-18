"""
Prediction API Routes with Regulatory Compliance
Provides ML-powered predictions for DAO proposals with comprehensive disclaimers
"""
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import os
from datetime import datetime
from supabase import create_client, Client

# Import regulatory components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from regulatory.audit_logger import AuditLogger
from regulatory.disclaimers import (
    get_api_disclaimer,
    get_confidence_warning,
    wrap_response_with_disclaimer
)

# Initialize router
router = APIRouter(prefix="/api/predictions", tags=["predictions"])

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Initialize audit logger
audit_logger = AuditLogger(supabase) if supabase else None


# Pydantic models
class PredictionResponse(BaseModel):
    """Prediction response model"""
    proposal_id: str
    prediction_type: str
    predicted_value: float
    confidence_score: float
    model_version: str
    prediction_text: str
    created_at: str
    disclaimer: str
    confidence_warning: Optional[str] = None


class PredictionCreate(BaseModel):
    """Model for creating a new prediction"""
    proposal_id: str = Field(..., description="Unique identifier for the proposal")
    prediction_type: str = Field(..., description="Type of prediction: 'outcome', 'sentiment', 'risk'")
    predicted_value: float = Field(..., ge=0, le=1, description="Predicted probability (0-1)")
    confidence_score: float = Field(..., ge=0, le=1, description="Model confidence (0-1)")
    model_version: str = Field(..., description="Version of the ML model used")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


@router.get("/{proposal_id}", response_model=Dict[str, Any])
async def get_prediction(
    proposal_id: str,
    request: Request,
    prediction_type: Optional[str] = Query("outcome", description="Type of prediction to retrieve")
):
    """
    Get ML prediction for a specific proposal
    
    ⚠️ REGULATORY DISCLAIMER:
    This is analytical information for educational purposes only.
    - NOT investment advice
    - NOT trading signals
    - NOT financial recommendations
    
    Predictions are based on historical data and ML models.
    Past performance does not guarantee future results.
    
    Args:
        proposal_id: Unique identifier for the proposal
        prediction_type: Type of prediction ('outcome', 'sentiment', 'risk')
        request: FastAPI request object for audit logging
    
    Returns:
        Prediction data with comprehensive disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Get client info for audit logging
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Fetch prediction from database
        response = (
            supabase.table("predictions")
            .select("*")
            .eq("proposal_id", proposal_id)
            .eq("prediction_type", prediction_type)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No {prediction_type} prediction found for proposal {proposal_id}"
            )
        
        prediction = response.data[0]
        
        # Log audit trail
        if audit_logger:
            await audit_logger.log_prediction_request(
                proposal_id=proposal_id,
                user_id="anonymous",
                confidence=prediction.get("confidence_score"),
                model_version=prediction.get("model_version"),
                ip_address=client_ip
            )
        
        # Prepare response with disclaimer
        confidence = prediction.get("confidence_score", 0)
        prediction_text = "Likely to pass" if prediction.get("predicted_value", 0) > 0.5 else "Likely to fail"
        
        result = {
            "proposal_id": prediction["proposal_id"],
            "prediction_type": prediction["prediction_type"],
            "predicted_value": float(prediction["predicted_value"]),
            "confidence_score": float(confidence),
            "model_version": prediction["model_version"],
            "prediction_text": prediction_text,
            "created_at": prediction["created_at"],
            "accuracy_status": prediction.get("accuracy_status", "pending"),
            "metadata": prediction.get("metadata", {})
        }
        
        # Add confidence warning if needed
        confidence_warning = get_confidence_warning(confidence)
        if confidence_warning:
            result["confidence_warning"] = confidence_warning
        
        # Wrap with disclaimer
        return wrap_response_with_disclaimer(result, "prediction")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching prediction: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_prediction(
    prediction: PredictionCreate,
    request: Request
):
    """
    Create a new prediction (Internal use only - requires authentication)
    
    Args:
        prediction: Prediction data to create
        request: FastAPI request object
    
    Returns:
        Created prediction with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Prepare prediction data
        prediction_data = {
            "proposal_id": prediction.proposal_id,
            "prediction_type": prediction.prediction_type,
            "predicted_value": prediction.predicted_value,
            "confidence_score": prediction.confidence_score,
            "model_version": prediction.model_version,
            "accuracy_status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "metadata": prediction.metadata
        }
        
        # Insert into database
        response = supabase.table("predictions").insert(prediction_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create prediction")
        
        # Log audit trail
        if audit_logger:
            await audit_logger.log_action(
                action="prediction_created",
                resource_type="prediction",
                resource_id=prediction.proposal_id,
                details={
                    "prediction_type": prediction.prediction_type,
                    "confidence": prediction.confidence_score,
                    "model_version": prediction.model_version
                }
            )
        
        return wrap_response_with_disclaimer(response.data[0], "prediction")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating prediction: {str(e)}")


@router.get("/live-tracking/accuracy", response_model=Dict[str, Any])
async def get_live_tracking():
    """
    Get live tracking of prediction accuracy
    
    Shows real-time performance of ML models on completed proposals.
    This data is provided for transparency and does NOT guarantee future accuracy.
    
    ⚠️ DISCLAIMER:
    Live tracking shows past performance only.
    Past performance does not guarantee future results.
    Use this data to understand model limitations.
    
    Returns:
        Accuracy metrics with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Get all predictions with known outcomes
        response = (
            supabase.table("predictions")
            .select("*")
            .neq("accuracy_status", "pending")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
        
        predictions = response.data
        
        if not predictions:
            return wrap_response_with_disclaimer({
                "message": "No completed predictions available yet",
                "total_tracked": 0,
                "accuracy": 0
            }, "tracking")
        
        # Calculate metrics
        total = len(predictions)
        correct = sum(1 for p in predictions if p.get("accuracy_status") == "correct")
        accuracy = correct / total if total > 0 else 0
        
        # Group by prediction type
        by_type = {}
        for pred in predictions:
            pred_type = pred.get("prediction_type", "unknown")
            if pred_type not in by_type:
                by_type[pred_type] = {"total": 0, "correct": 0}
            by_type[pred_type]["total"] += 1
            if pred.get("accuracy_status") == "correct":
                by_type[pred_type]["correct"] += 1
        
        # Calculate accuracy by type
        for pred_type in by_type:
            total_type = by_type[pred_type]["total"]
            correct_type = by_type[pred_type]["correct"]
            by_type[pred_type]["accuracy"] = correct_type / total_type if total_type > 0 else 0
        
        result = {
            "total_tracked": total,
            "correct_predictions": correct,
            "overall_accuracy": round(accuracy, 4),
            "accuracy_by_type": by_type,
            "recent_predictions": predictions[:10],  # Last 10 predictions
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return wrap_response_with_disclaimer(result, "tracking")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live tracking data: {str(e)}")


@router.get("/proposal/{proposal_id}/history", response_model=Dict[str, Any])
async def get_prediction_history(proposal_id: str):
    """
    Get prediction history for a specific proposal
    
    Shows all predictions made for a proposal over time.
    Useful for tracking how predictions evolved.
    
    Args:
        proposal_id: Unique identifier for the proposal
    
    Returns:
        List of predictions with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        response = (
            supabase.table("predictions")
            .select("*")
            .eq("proposal_id", proposal_id)
            .order("created_at", desc=True)
            .execute()
        )
        
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for proposal {proposal_id}"
            )
        
        result = {
            "proposal_id": proposal_id,
            "total_predictions": len(response.data),
            "predictions": response.data
        }
        
        return wrap_response_with_disclaimer(result, "prediction")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching prediction history: {str(e)}")
