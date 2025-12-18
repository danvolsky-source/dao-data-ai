"""
Audit Log API Routes - Regulatory Compliance
Admin-only access to audit logs for compliance and security monitoring
"""
from fastapi import APIRouter, HTTPException, Request, Query, Depends
from typing import Optional, Dict, Any
import os
from supabase import create_client, Client

# Import audit logger
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from regulatory.audit_logger import AuditLogger
from regulatory.disclaimers import wrap_response_with_disclaimer

# Initialize router
router = APIRouter(prefix="/api/audit", tags=["audit"])

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Initialize audit logger
audit_logger = AuditLogger(supabase) if supabase else None


# Simple auth check (In production, use proper JWT/OAuth)
def verify_admin_access(request: Request):
    """
    Verify admin access (Placeholder - implement proper auth)
    
    In production:
    - Use JWT tokens
    - Check user roles
    - Validate service_role key
    """
    # For now, just check if a specific header is present
    # In production, implement proper authentication
    auth_header = request.headers.get("X-Admin-Key")
    admin_key = os.getenv("ADMIN_KEY", "change-me-in-production")
    
    if not auth_header or auth_header != admin_key:
        raise HTTPException(
            status_code=403,
            detail="Admin access required. Audit logs are restricted for security and compliance."
        )
    return True


@router.get("/logs", response_model=Dict[str, Any])
async def get_audit_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to retrieve"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    is_admin: bool = Depends(verify_admin_access)
):
    """
    Get audit logs (Admin only)
    
    Retrieves comprehensive audit trail for regulatory compliance and security monitoring.
    
    **Admin Authentication Required**
    - Set X-Admin-Key header with admin key
    - In production, use proper JWT/OAuth authentication
    
    Args:
        limit: Number of logs to retrieve (1-1000)
        offset: Offset for pagination
        action: Filter by action type
        resource_type: Filter by resource type
        user_id: Filter by user ID
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
    
    Returns:
        Audit logs with metadata
    """
    if not audit_logger:
        raise HTTPException(status_code=500, detail="Audit logging not configured")
    
    try:
        logs = await audit_logger.get_audit_logs(
            limit=limit,
            offset=offset,
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add metadata
        logs["metadata"] = {
            "admin_access": True,
            "filters": {
                "action": action,
                "resource_type": resource_type,
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
        return logs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching audit logs: {str(e)}")


@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_user_audit_logs(
    user_id: str,
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    is_admin: bool = Depends(verify_admin_access)
):
    """
    Get audit logs for a specific user (Admin only)
    
    **Admin Authentication Required**
    
    Args:
        user_id: User identifier to retrieve logs for
        limit: Number of logs to retrieve
    
    Returns:
        User-specific audit logs
    """
    if not audit_logger:
        raise HTTPException(status_code=500, detail="Audit logging not configured")
    
    try:
        logs = await audit_logger.get_user_activity(user_id=user_id, limit=limit)
        return logs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user audit logs: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_audit_stats(
    request: Request,
    is_admin: bool = Depends(verify_admin_access)
):
    """
    Get audit log statistics (Admin only)
    
    Provides overview of system usage and activity patterns.
    
    **Admin Authentication Required**
    
    Returns:
        Aggregated statistics from audit logs
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Get total count
        total_response = supabase.table("audit_log").select("id", count="exact").execute()
        total_logs = total_response.count if hasattr(total_response, 'count') else 0
        
        # Get counts by action
        actions_response = supabase.table("audit_log").select("action").execute()
        actions_data = actions_response.data
        
        action_counts = {}
        for log in actions_data:
            action = log.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Get counts by resource type
        resource_response = supabase.table("audit_log").select("resource_type").execute()
        resource_data = resource_response.data
        
        resource_counts = {}
        for log in resource_data:
            resource = log.get("resource_type", "unknown")
            resource_counts[resource] = resource_counts.get(resource, 0) + 1
        
        # Get unique users count
        users_response = supabase.table("audit_log").select("user_id").execute()
        unique_users = len(set(log.get("user_id") for log in users_response.data))
        
        result = {
            "total_logs": total_logs,
            "unique_users": unique_users,
            "by_action": action_counts,
            "by_resource_type": resource_counts,
            "most_common_actions": sorted(
                action_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching audit statistics: {str(e)}")


@router.get("/compliance-report", response_model=Dict[str, Any])
async def get_compliance_report(
    request: Request,
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    is_admin: bool = Depends(verify_admin_access)
):
    """
    Generate compliance report for specified date range (Admin only)
    
    Provides comprehensive report for regulatory compliance audits.
    
    **Admin Authentication Required**
    
    Args:
        start_date: Report start date (ISO format)
        end_date: Report end date (ISO format)
    
    Returns:
        Detailed compliance report
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    
    try:
        # Fetch logs for date range
        response = (
            supabase.table("audit_log")
            .select("*")
            .gte("timestamp", start_date)
            .lte("timestamp", end_date)
            .execute()
        )
        
        logs = response.data
        
        # Generate report
        report = {
            "report_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_events": len(logs),
                "unique_users": len(set(log.get("user_id") for log in logs)),
                "api_calls": sum(1 for log in logs if log.get("resource_type") == "api_call"),
                "predictions_requested": sum(1 for log in logs if log.get("action") == "prediction_requested"),
                "sentiment_analyses": sum(1 for log in logs if log.get("action") == "sentiment_analyzed"),
                "model_trainings": sum(1 for log in logs if log.get("action") == "model_trained")
            },
            "by_action": {},
            "by_resource_type": {},
            "by_user": {},
            "compliance_notes": [
                "All user actions are logged for audit trail",
                "No sensitive data is stored without encryption",
                "All predictions include regulatory disclaimers",
                "Model performance is transparently reported"
            ]
        }
        
        # Group by action
        for log in logs:
            action = log.get("action", "unknown")
            report["by_action"][action] = report["by_action"].get(action, 0) + 1
        
        # Group by resource type
        for log in logs:
            resource = log.get("resource_type", "unknown")
            report["by_resource_type"][resource] = report["by_resource_type"].get(resource, 0) + 1
        
        # Group by user (top 20 active users)
        for log in logs:
            user_id = log.get("user_id", "anonymous")
            report["by_user"][user_id] = report["by_user"].get(user_id, 0) + 1
        
        # Sort top users
        top_users = sorted(report["by_user"].items(), key=lambda x: x[1], reverse=True)[:20]
        report["top_users"] = [{"user_id": user, "actions": count} for user, count in top_users]
        
        return {
            "status": "success",
            "report": report,
            "generated_at": request.url.path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating compliance report: {str(e)}")
