"""Feature Engineering for DAO Proposal Prediction"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List

class ProposalFeatureEngineer:
    """Extracts features from proposal data for ML models"""
    
    def extract_features(self, proposal: Dict) -> Dict:
        """Extract all features from a proposal"""
        features = {}
        
        # On-chain voting features
        features.update(self._voting_features(proposal))
        
        # Temporal features
        features.update(self._temporal_features(proposal))
        
        # Participation features
        features.update(self._participation_features(proposal))
        
        # Historical features (if available)
        features.update(self._historical_features(proposal))
        
        return features
    
    def _voting_features(self, proposal: Dict) -> Dict:
        """Extract voting pattern features"""
        votes_for = proposal.get('votes_for', 0)
        votes_against = proposal.get('votes_against', 0)
        votes_abstain = proposal.get('votes_abstain', 0)
        total_votes = votes_for + votes_against + votes_abstain
        
        if total_votes == 0:
            return {
                'vote_ratio': 0.5,
                'vote_margin': 0,
                'total_votes': 0,
                'votes_for_pct': 0,
                'votes_against_pct': 0,
                'vote_concentration': 0
            }
        
        return {
            'vote_ratio': votes_for / (votes_for + votes_against + 1),
            'vote_margin': (votes_for - votes_against) / total_votes,
            'total_votes': total_votes,
            'votes_for_pct': votes_for / total_votes,
            'votes_against_pct': votes_against / total_votes,
            'vote_concentration': max(votes_for, votes_against) / total_votes
        }
    
    def _temporal_features(self, proposal: Dict) -> Dict:
        """Extract time-based features"""
        created_at = proposal.get('created_at')
        if not created_at:
            return {'days_active': 0, 'is_recent': 0}
        
        try:
            created = pd.to_datetime(created_at)
            now = pd.Timestamp.now()
            days_active = (now - created).days
            
            return {
                'days_active': days_active,
                'is_recent': 1 if days_active < 7 else 0
            }
        except:
            return {'days_active': 0, 'is_recent': 0}
    
    def _participation_features(self, proposal: Dict) -> Dict:
        """Extract participation metrics"""
        vote_count = proposal.get('vote_count', 0)
        
        return {
            'voter_count': vote_count,
            'has_high_participation': 1 if vote_count > 100 else 0
        }
    
    def _historical_features(self, proposal: Dict) -> Dict:
        """Extract features based on historical data"""
        # Placeholder - would use historical proposal outcomes
        proposer = proposal.get('proposer', '')
        
        return {
            'proposer_success_rate': 0.5,  # Would calculate from history
            'similar_proposals_passed': 0.5  # Would calculate from similar props
        }
    
    def prepare_dataset(self, proposals: List[Dict]) -> pd.DataFrame:
        """Prepare full dataset from proposals list"""
        features_list = []
        
        for prop in proposals:
            features = self.extract_features(prop)
            features['proposal_id'] = prop.get('id', '')
            
            # Add target if available
            status = prop.get('status', '').lower()
            if status in ['passed', 'succeeded', 'executed']:
                features['target'] = 1
            elif status in ['defeated', 'rejected', 'failed']:
                features['target'] = 0
            else:
                features['target'] = None
            
            features_list.append(features)
        
        return pd.DataFrame(features_list)

if __name__ == "__main__":
    # Test feature engineering
    engineer = ProposalFeatureEngineer()
    
    test_proposal = {
        'id': '1',
        'votes_for': 25000000,
        'votes_against': 8000000,
        'votes_abstain': 1000000,
        'vote_count': 150,
        'status': 'passed',
        'created_at': '2025-12-01T00:00:00Z'
    }
    
    features = engineer.extract_features(test_proposal)
    print("Extracted features:")
    for k, v in features.items():
        print(f"  {k}: {v}")
