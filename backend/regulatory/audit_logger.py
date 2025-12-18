"""
Audit Logger - Regulatory Compliance
Logs all system actions for audit trail and regulatory requirements
"""
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import Client
import json


class AuditLogger:
    """
    Comprehensive audit logging for regulatory compliance.
    Tracks all actions on proposals, predictions, votes, and API calls.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize audit logger with Supabase client
        
        Args:
            supabase_client: Authenticated Supabase client
        """
        self.client = supabase_client
    
    async def log_action(
        self,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an action to the audit log
        
        Args:
            action: Action performed (e.g., 'prediction_requested', 'model_trained', 'api_call')
            resource_type: Type of resource ('proposal', 'vote', 'prediction', 'sentiment', 'model', 'api_call')
            user_id: User identifier (IP, wallet address, or 'anonymous')
            resource_id: ID of the resource being accessed
            ip_address: Client IP address
            user_agent: Client user agent string
            details: Additional context as JSON object
            
        Returns:
            Dict containing the created audit log entry
        """
        try:
            log_entry = {
                "user_id": user_id or "anonymous",
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("audit_log").insert(log_entry).execute()
            
            return {
                "status": "success",
                "data": response.data[0] if response.data else log_entry
            }
        except Exception as e:
            # Don't fail the main operation if logging fails
            print(f"Audit logging failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def log_prediction_request(
        self,
        proposal_id: str,
        user_id: Optional[str] = None,
        confidence: Optional[float] = None,
        model_version: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a prediction request
        
        Args:
            proposal_id: ID of the proposal
            user_id: User requesting the prediction
            confidence: Model confidence score
            model_version: Version of the ML model used
            ip_address: Client IP address
            
        Returns:
            Dict containing the audit log entry
        """
        return await self.log_action(
            action="prediction_requested",
            resource_type="prediction",
            user_id=user_id,
            resource_id=proposal_id,
            ip_address=ip_address,
            details={
                "confidence": confidence,
                "model_version": model_version,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def log_sentiment_analysis(
        self,
        proposal_id: str,
        source: str,
        sentiment_score: float,
        message_count: int
    ) -> Dict[str, Any]:
        """
        Log sentiment analysis operation
        
        Args:
            proposal_id: ID of the proposal
            source: Source of sentiment data ('discord', 'forum', etc.)
            sentiment_score: Calculated sentiment score
            message_count: Number of messages analyzed
            
        Returns:
            Dict containing the audit log entry
        """
        return await self.log_action(
            action="sentiment_analyzed",
            resource_type="sentiment",
            resource_id=proposal_id,
            details={
                "source": source,
                "sentiment_score": sentiment_score,
                "message_count": message_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def log_model_training(
        self,
        model_name: str,
        model_version: str,
        accuracy: float,
        training_samples: int
    ) -> Dict[str, Any]:
        """
        Log ML model training event
        
        Args:
            model_name: Name of the model
            model_version: Version identifier
            accuracy: Model accuracy score
            training_samples: Number of samples used for training
            
        Returns:
            Dict containing the audit log entry
        """
        return await self.log_action(
            action="model_trained",
            resource_type="model",
            resource_id=f"{model_name}_{model_version}",
            details={
                "model_name": model_name,
                "model_version": model_version,
                "accuracy": accuracy,
                "training_samples": training_samples,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def log_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        response_time_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Log API call for monitoring and compliance
        
        Args:
            endpoint: API endpoint called
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP response status code
            user_id: User making the request
            ip_address: Client IP address
            user_agent: Client user agent
            response_time_ms: Response time in milliseconds
            
        Returns:
            Dict containing the audit log entry
        """
        return await self.log_action(
            action=f"api_{method.lower()}",
            resource_type="api_call",
            user_id=user_id,
            resource_id=endpoint,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def get_audit_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve audit logs with filters (Admin only)
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)
            action: Filter by action type
            resource_type: Filter by resource type
            user_id: Filter by user ID
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            
        Returns:
            Dict containing audit logs and pagination info
        """
        try:
            query = self.client.table("audit_log").select("*")
            
            # Apply filters
            if action:
                query = query.eq("action", action)
            if resource_type:
                query = query.eq("resource_type", resource_type)
            if user_id:
                query = query.eq("user_id", user_id)
            if start_date:
                query = query.gte("timestamp", start_date)
            if end_date:
                query = query.lte("timestamp", end_date)
            
            # Apply pagination and ordering
            query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)
            
            response = query.execute()
            
            return {
                "status": "success",
                "data": response.data,
                "count": len(response.data),
                "offset": offset,
                "limit": limit
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_user_activity(
        self,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get activity log for a specific user
        
        Args:
            user_id: User identifier
            limit: Maximum number of records
            
        Returns:
            Dict containing user activity logs
        """
        try:
            response = (
                self.client.table("audit_log")
                .select("*")
                .eq("user_id", user_id)
                .order("timestamp", desc=True)
                .limit(limit)
                .execute()
            )
            
            return {
                "status": "success",
                "user_id": user_id,
                "data": response.data,
                "count": len(response.data)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
