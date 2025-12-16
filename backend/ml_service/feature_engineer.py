"""Feature Engineering for DAO Proposal Prediction

This module provides feature engineering capabilities for DAO governance proposals.
It extracts various features including voting patterns, temporal information,
participation metrics, and historical data to support ML-based prediction models.

Examples:
    Basic usage:
        >>> from feature_engineer import ProposalFeatureEngineer
        >>> engineer = ProposalFeatureEngineer()
        >>> 
        >>> proposal = {
        ...     'id': '1',
        ...     'votes_for': 25000000,
        ...     'votes_against': 8000000,
        ...     'votes_abstain': 1000000,
        ...     'vote_count': 150,
        ...     'status': 'passed',
        ...     'created_at': '2025-12-01T00:00:00Z'
        ... }
        >>> features = engineer.extract_features(proposal)
        >>> print(features['vote_ratio'])
        0.757
    
    Processing multiple proposals:
        >>> proposals = [proposal1, proposal2, proposal3]
        >>> df = engineer.prepare_dataset(proposals)
        >>> print(df.shape)
        (3, 12)
"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List


class ProposalFeatureEngineer:
    """Инженер признаков для ML-модели предсказания исходов голосований.
    
    Extracts and transforms features from DAO proposal data to prepare them
    for machine learning models. Generates multiple feature categories including
    voting patterns, temporal features, participation metrics, and historical data.
    
    Attributes:
        None (stateless feature extraction)
    
    Examples:
        Create an engineer and extract features from a single proposal:
            >>> engineer = ProposalFeatureEngineer()
            >>> proposal_data = {
            ...     'votes_for': 1000000,
            ...     'votes_against': 500000,
            ...     'vote_count': 100,
            ...     'created_at': '2025-12-01T00:00:00Z'
            ... }
            >>> features = engineer.extract_features(proposal_data)
            >>> print(features.keys())
            dict_keys(['vote_ratio', 'vote_margin', 'total_votes', ...])
        
        Process a dataset of proposals:
            >>> proposals_list = load_proposals()  # Your data source
            >>> df = engineer.prepare_dataset(proposals_list)
            >>> # df is ready for ML model training
    """

    def extract_features(self, proposal: Dict) -> Dict:
        """Extract all features from a single proposal.
        
        This is the main entry point for feature extraction. It orchestrates
        the extraction of features from different categories and combines them
        into a single feature dictionary.
        
        Args:
            proposal: Dictionary containing proposal data with keys such as:
                - votes_for (int): Number of votes in favor
                - votes_against (int): Number of votes against
                - votes_abstain (int): Number of abstentions
                - vote_count (int): Total number of voters
                - created_at (str): ISO format timestamp
                - status (str): Proposal status
        
        Returns:
            Dictionary of extracted features with keys:
                - vote_ratio (float): Ratio of for votes to total
                - vote_margin (float): Margin between for and against
                - total_votes (int): Total vote count
                - days_active (int): Days since proposal creation
                - voter_count (int): Number of participants
                ... and other features
        
        Examples:
            >>> engineer = ProposalFeatureEngineer()
            >>> proposal = {'votes_for': 100, 'votes_against': 50}
            >>> features = engineer.extract_features(proposal)
            >>> features['vote_ratio']
            0.667
        """
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
        """Extract voting pattern features.
        
        Computes various metrics based on voting distribution including
        vote ratios, margins, and concentration metrics.
        
        Args:
            proposal: Proposal dictionary with vote counts
        
        Returns:
            Dictionary with voting-related features:
                - vote_ratio: For votes / (for + against + 1)
                - vote_margin: (For - against) / total
                - total_votes: Sum of all votes
                - votes_for_pct: Percentage voting for
                - votes_against_pct: Percentage voting against  
                - vote_concentration: Max vote type / total
        
        Examples:
            >>> engineer = ProposalFeatureEngineer()
            >>> proposal = {'votes_for': 75, 'votes_against': 25, 'votes_abstain': 0}
            >>> features = engineer._voting_features(proposal)
            >>> features['vote_margin']
            0.5
        """
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
        """Extract time-based features.
        
        Computes temporal features based on proposal creation time,
        including age and recency indicators.
        
        Args:
            proposal: Proposal dictionary with 'created_at' timestamp
        
        Returns:
            Dictionary with temporal features:
                - days_active: Number of days since creation
                - is_recent: Binary flag (1 if < 7 days old)
        
        Examples:
            >>> engineer = ProposalFeatureEngineer()
            >>> proposal = {'created_at': '2025-12-10T00:00:00Z'}
            >>> features = engineer._temporal_features(proposal)
            >>> 'days_active' in features
            True
        """
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
        """Extract participation metrics.
        
        Computes features related to voter participation levels.
        
        Args:
            proposal: Proposal dictionary with 'vote_count'
        
        Returns:
            Dictionary with participation features:
                - voter_count: Number of unique voters
                - has_high_participation: Binary flag (1 if > 100 voters)
        
        Examples:
            >>> engineer = ProposalFeatureEngineer()
            >>> proposal = {'vote_count': 150}
            >>> features = engineer._participation_features(proposal)
            >>> features['has_high_participation']
            1
        """
        vote_count = proposal.get('vote_count', 0)

        return {
            'voter_count': vote_count,
            'has_high_participation': 1 if vote_count > 100 else 0
        }

    def _historical_features(self, proposal: Dict) -> Dict:
        """Extract features based on historical data.
        
        Computes features based on historical proposal outcomes and
        proposer track record. Currently returns placeholder values.
        
        Args:
            proposal: Proposal dictionary with 'proposer' identifier
        
        Returns:
            Dictionary with historical features:
                - proposer_success_rate: Historical success rate (0-1)
                - similar_proposals_passed: Success rate of similar proposals
        
        Note:
            This is currently a placeholder implementation. In production,
            these values should be calculated from historical data.
        
        Examples:
            >>> engineer = ProposalFeatureEngineer()
            >>> proposal = {'proposer': '0x123...'}
            >>> features = engineer._historical_features(proposal)
            >>> 'proposer_success_rate' in features
            True
        """
        # Placeholder - would use historical proposal outcomes
        proposer = proposal.get('proposer', '')

        return {
            'proposer_success_rate': 0.5,  # Would calculate from history
            'similar_proposals_passed': 0.5  # Would calculate from similar props
        }

    def prepare_dataset(self, proposals: List[Dict]) -> pd.DataFrame:
        """Prepare full dataset from proposals list.
        
        Processes a list of proposals and creates a complete dataset with
        features and targets ready for ML model training/inference.
        
        Args:
            proposals: List of proposal dictionaries, each containing:
                - All fields required by extract_features()
                - id: Unique proposal identifier
                - status: Proposal outcome (optional, for training data)
        
        Returns:
            pandas DataFrame with:
                - All extracted features as columns
                - proposal_id column with unique identifiers
                - target column (1 for passed, 0 for failed, None for pending)
        
        Examples:
            >>> engineer = ProposalFeatureEngineer()
            >>> proposals = [
            ...     {'id': '1', 'votes_for': 100, 'votes_against': 50, 'status': 'passed'},
            ...     {'id': '2', 'votes_for': 40, 'votes_against': 60, 'status': 'failed'}
            ... ]
            >>> df = engineer.prepare_dataset(proposals)
            >>> df.shape[0]
            2
            >>> 'target' in df.columns
            True
        """
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
