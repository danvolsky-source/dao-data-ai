# Feature Engineering for DAO Analytics
import pandas as pd
import numpy as np
from datetime import datetime
from supabase import Client

class FeatureEngineer:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    def extract_proposal_features(self, proposal_id: str) -> dict:
        features = {}
        features.update(self._get_proposal_basic_features(proposal_id))
        features.update(self._get_temporal_features(proposal_id))
        features.update(self._get_voting_features(proposal_id))
        features.update(self._get_forum_features(proposal_id))
        return features
    
    def _get_proposal_basic_features(self, proposal_id: str) -> dict:
        result = self.supabase.table("snapshot_proposals").select("*").eq("proposal_id", proposal_id).execute()
        if not result.data: return {}
        p = result.data[0]
        return {
            "title_length": len(p.get("title", "")),
            "body_length": len(p.get("body", "")),
            "choices_count": len(p.get("choices", [])),
            "quorum": float(p.get("quorum", 0) or 0)
        }
    
    def _get_temporal_features(self, proposal_id: str) -> dict:
        result = self.supabase.table("snapshot_proposals").select("start, end").eq("proposal_id", proposal_id).execute()
        if not result.data: return {}
        p = result.data[0]
        start = datetime.fromisoformat(p["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(p["end"].replace("Z", "+00:00"))
        duration = (end - start).total_seconds() / 3600
        return {
            "voting_duration_hours": duration,
            "start_day_of_week": start.weekday(),
            "is_weekend": 1 if start.weekday() >= 5 else 0
        }
    
    def _get_voting_features(self, proposal_id: str) -> dict:
        result = self.supabase.table("snapshot_votes").select("*").eq("proposal_id", proposal_id).execute()
        if not result.data:
            return {"total_votes": 0, "total_voting_power": 0.0, "avg_voting_power": 0.0}
        df = pd.DataFrame(result.data)
        vp = df["voting_power"].astype(float)
        return {
            "total_votes": len(df),
            "total_voting_power": float(vp.sum()),
            "avg_voting_power": float(vp.mean()),
            "unique_voters": df["voter"].nunique()
        }
    
    def _get_forum_features(self, proposal_id: str) -> dict:
        result = self.supabase.table("forum_threads").select("*").eq("proposal_id", proposal_id).execute()
        if not result.data:
            return {"forum_views": 0, "forum_replies": 0}
        t = result.data[0]
        return {
            "forum_views": t.get("views", 0),
            "forum_replies": t.get("replies", 0),
            "forum_participants": t.get("participants", 0)
        }
