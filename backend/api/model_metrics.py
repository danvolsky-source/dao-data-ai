"""
Model Metrics API Routes - Transparency and Regulatory Compliance
Provides public access to ML model performance metrics
"""
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import os
from datetime import datetime
from supabase import create_client, Client

# Import regulatory components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from regulatory.audit_logger import AuditLogger
from regulatory.disclaimers import wrap_response_with_disclaimer

# Initialize router
router = APIRouter(prefix="/api/models", tags=["models"])

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Initialize audit logger
audit_logger = AuditLogger(supabase) if supabase else None


# Pydantic models
class ModelMetrics(BaseModel):
    """Model metrics response"""
    model_name: str
    model_version: str
    accuracy: float = Field(..., ge=0, le=1)
    precision: float = Field(..., ge=0, le=1)
    recall: float = Field(..., ge=0, le=1)
    f1_score: float = Field(..., ge=0, le=1)
    backtesting_period: str
    total_predictions: int
    correct_predictions: int
    created_at: str


class ModelMetricsCreate(BaseModel):
    """Model for creating model metrics entry"""
    model_name: str
    model_version: str
    accuracy: float = Field(..., ge=0, le=1)
    precision: float = Field(..., ge=0, le=1)
    recall: float = Field(..., ge=0, le=1)
    f1_score: float = Field(..., ge=0, le=1)
    backtesting_period: str
    total_predictions: int = Field(..., ge=0)
    correct_predictions: int = Field(..., ge=0)
    metadata: Optional[Dict[str, Any]] = {}


@router.get("/metrics", response_model=Dict[str, Any])
async def get_all_model_metrics(
    request: Request,
    limit: int = Query(50, ge=1, le=100, description="Number of metrics to retrieve")
):
    """
    Get performance metrics for all ML models
    
    ⚠️ TRANSPARENCY NOTICE:
    We publish all model performance metrics for transparency.
    This shows the REAL accuracy of our predictions, not cherry-picked results.
    
    - Past performance does NOT guarantee future results
    - Models are continuously improved
    - Use these metrics to understand limitations
    
    Returns:
        List of model metrics with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        response = (
            supabase.table("model_metrics")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        if not response.data:
            return wrap_response_with_disclaimer({
                "message": "No model metrics available yet",
                "models": []
            }, "model")
        
        # Group by model name to get latest version
        by_model = {}
        for metric in response.data:
            model_name = metric.get("model_name")
            if model_name not in by_model:
                by_model[model_name] = {
                    "model_name": model_name,
                    "latest_version": metric.get("model_version"),
                    "latest_metrics": metric,
                    "versions": []
                }
            by_model[model_name]["versions"].append(metric)
        
        result = {
            "total_models": len(by_model),
            "models": list(by_model.values()),
            "all_metrics": response.data,
            "transparency_note": "All metrics shown are from backtesting on historical data"
        }
        
        # Log access for audit
        if audit_logger:
            await audit_logger.log_action(
                action="model_metrics_viewed",
                resource_type="model",
                user_id="anonymous",
                ip_address=request.client.host if request.client else "unknown"
            )
        
        return wrap_response_with_disclaimer(result, "model")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model metrics: {str(e)}")


@router.get("/metrics/{model_name}", response_model=Dict[str, Any])
async def get_model_metrics(
    model_name: str,
    request: Request,
    version: Optional[str] = Query(None, description="Specific model version")
):
    """
    Get performance metrics for a specific model
    
    Shows detailed performance data including:
    - Accuracy, Precision, Recall, F1 Score
    - Total predictions and correct predictions
    - Backtesting period
    
    Args:
        model_name: Name of the model
        version: Optional specific version
    
    Returns:
        Model metrics with transparency disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        query = supabase.table("model_metrics").select("*").eq("model_name", model_name)
        
        if version:
            query = query.eq("model_version", version)
        
        query = query.order("created_at", desc=True)
        
        response = query.execute()
        
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for model {model_name}"
            )
        
        # Get latest metrics
        latest = response.data[0]
        
        # Calculate average metrics across all versions
        avg_accuracy = sum(m.get("accuracy", 0) for m in response.data) / len(response.data)
        avg_precision = sum(m.get("precision", 0) for m in response.data) / len(response.data)
        avg_recall = sum(m.get("recall", 0) for m in response.data) / len(response.data)
        avg_f1 = sum(m.get("f1_score", 0) for m in response.data) / len(response.data)
        
        result = {
            "model_name": model_name,
            "latest_version": latest.get("model_version"),
            "latest_metrics": {
                "accuracy": latest.get("accuracy"),
                "precision": latest.get("precision"),
                "recall": latest.get("recall"),
                "f1_score": latest.get("f1_score"),
                "total_predictions": latest.get("total_predictions"),
                "correct_predictions": latest.get("correct_predictions"),
                "backtesting_period": latest.get("backtesting_period"),
                "created_at": latest.get("created_at")
            },
            "average_across_versions": {
                "accuracy": round(avg_accuracy, 4),
                "precision": round(avg_precision, 4),
                "recall": round(avg_recall, 4),
                "f1_score": round(avg_f1, 4)
            },
            "total_versions": len(response.data),
            "version_history": response.data
        }
        
        return wrap_response_with_disclaimer(result, "model")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model metrics: {str(e)}")


@router.post("/metrics", response_model=Dict[str, Any])
async def create_model_metrics(
    metrics: ModelMetricsCreate,
    request: Request
):
    """
    Create new model metrics entry (Internal use only)
    
    Called after model training/backtesting to record performance.
    
    Args:
        metrics: Model metrics data
        request: FastAPI request object
    
    Returns:
        Created metrics with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Validate that correct_predictions <= total_predictions
        if metrics.correct_predictions > metrics.total_predictions:
            raise HTTPException(
                status_code=400,
                detail="Correct predictions cannot exceed total predictions"
            )
        
        # Prepare data
        metrics_data = {
            "model_name": metrics.model_name,
            "model_version": metrics.model_version,
            "accuracy": metrics.accuracy,
            "precision": metrics.precision,
            "recall": metrics.recall,
            "f1_score": metrics.f1_score,
            "backtesting_period": metrics.backtesting_period,
            "total_predictions": metrics.total_predictions,
            "correct_predictions": metrics.correct_predictions,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metrics.metadata
        }
        
        # Insert into database
        response = supabase.table("model_metrics").insert(metrics_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create model metrics")
        
        # Log audit trail
        if audit_logger:
            await audit_logger.log_model_training(
                model_name=metrics.model_name,
                model_version=metrics.model_version,
                accuracy=metrics.accuracy,
                training_samples=metrics.total_predictions
            )
        
        return wrap_response_with_disclaimer(response.data[0], "model")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating model metrics: {str(e)}")


@router.get("/leaderboard", response_model=Dict[str, Any])
async def get_model_leaderboard():
    """
    Get leaderboard of best performing models
    
    Shows top models by accuracy for transparency.
    Helps users understand which models to trust more.
    
    Returns:
        Ranked list of models by performance
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Get latest metrics for each model
        response = supabase.table("model_metrics").select("*").order("created_at", desc=True).execute()
        
        if not response.data:
            return wrap_response_with_disclaimer({
                "message": "No model metrics available",
                "leaderboard": []
            }, "model")
        
        # Get latest version for each model
        latest_by_model = {}
        for metric in response.data:
            model_name = metric.get("model_name")
            if model_name not in latest_by_model:
                latest_by_model[model_name] = metric
        
        # Sort by accuracy
        leaderboard = sorted(
            latest_by_model.values(),
            key=lambda x: x.get("accuracy", 0),
            reverse=True
        )
        
        # Format leaderboard
        formatted_leaderboard = []
        for rank, model in enumerate(leaderboard, 1):
            formatted_leaderboard.append({
                "rank": rank,
                "model_name": model.get("model_name"),
                "model_version": model.get("model_version"),
                "accuracy": model.get("accuracy"),
                "precision": model.get("precision"),
                "recall": model.get("recall"),
                "f1_score": model.get("f1_score"),
                "total_predictions": model.get("total_predictions"),
                "backtesting_period": model.get("backtesting_period")
            })
        
        result = {
            "total_models": len(formatted_leaderboard),
            "leaderboard": formatted_leaderboard,
            "best_model": formatted_leaderboard[0] if formatted_leaderboard else None,
            "transparency_note": "Rankings based on backtesting. Real-world performance may vary."
        }
        
        return wrap_response_with_disclaimer(result, "model")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating leaderboard: {str(e)}")


@router.get("/comparison", response_model=Dict[str, Any])
async def compare_models(
    model_names: List[str] = Query(..., description="List of model names to compare")
):
    """
    Compare performance of multiple models
    
    Shows side-by-side comparison of model metrics.
    Helps users understand tradeoffs between models.
    
    Args:
        model_names: List of model names to compare
    
    Returns:
        Comparison data with disclaimer
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        if len(model_names) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 models required for comparison"
            )
        
        # Fetch latest metrics for each model
        comparison_data = []
        
        for model_name in model_names:
            response = (
                supabase.table("model_metrics")
                .select("*")
                .eq("model_name", model_name)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if response.data:
                comparison_data.append(response.data[0])
        
        if not comparison_data:
            raise HTTPException(
                status_code=404,
                detail="No metrics found for specified models"
            )
        
        result = {
            "models_compared": len(comparison_data),
            "comparison": comparison_data,
            "best_accuracy": max(m.get("accuracy", 0) for m in comparison_data),
            "best_precision": max(m.get("precision", 0) for m in comparison_data),
            "best_recall": max(m.get("recall", 0) for m in comparison_data),
            "best_f1": max(m.get("f1_score", 0) for m in comparison_data),
            "recommendation": _get_model_recommendation(comparison_data)
        }
        
        return wrap_response_with_disclaimer(result, "model")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing models: {str(e)}")


def _get_model_recommendation(models: List[Dict]) -> str:
    """Get recommendation based on model comparison"""
    if not models:
        return "No models to compare"
    
    # Find model with highest F1 score (balanced metric)
    best_model = max(models, key=lambda x: x.get("f1_score", 0))
    
    return (
        f"Recommended: {best_model.get('model_name')} "
        f"(F1: {best_model.get('f1_score'):.4f}, "
        f"Accuracy: {best_model.get('accuracy'):.4f})"
    )
