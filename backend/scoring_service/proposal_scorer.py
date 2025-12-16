"""Proposal Scoring System for DAO Governance"""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class ProposalScorer:
    """Calculates comprehensive scores for DAO proposals"""
    
    def __init__(self, weights: Optional[Dict] = None):
        # Default weights for scoring components (must sum to 1.0)
        self.weights = weights or {
            'prediction_confidence': 0.25,  # ML model prediction weight
            'sentiment': 0.20,              # Community sentiment weight
            'participation': 0.15,          # Voting participation weight
            'risk_assessment': 0.20,        # Risk factors weight
            'treasury_impact': 0.10,        # Financial impact weight
            'execution_quality': 0.10       # Proposal quality metrics
        }
        
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def score_prediction_confidence(self, proposal: Dict) -> float:
        """Score based on ML prediction confidence and outcome"""
        prediction = proposal.get('prediction', 0.5)
        confidence = proposal.get('confidence', 0)
        
        # Higher scores for confident predictions of passing
        if prediction > 0.5:
            # Likely to pass
            score = prediction * confidence
        else:
            # Likely to fail - lower score
            score = (1 - prediction) * confidence * 0.5
        
        return min(1.0, max(0.0, score))
    
    def score_sentiment(self, proposal: Dict) -> float:
        """Score based on community sentiment"""
        sentiment = proposal.get('sentiment_score', 0)
        
        # Convert sentiment from [-1, 1] to [0, 1]
        # Positive sentiment = higher score
        score = (sentiment + 1) / 2
        
        return min(1.0, max(0.0, score))
    
    def score_participation(self, proposal: Dict) -> float:
        """Score based on voting participation metrics"""
        votes_count = proposal.get('votes_count', 0)
        total_eligible = proposal.get('total_eligible_voters', 1000)
        voting_power_used = proposal.get('voting_power_percentage', 0)
        
        # Participation rate
        participation_rate = min(1.0, votes_count / total_eligible)
        
        # Voting power usage (higher is better for legitimacy)
        power_score = min(1.0, voting_power_used)
        
        # Combine both metrics
        score = (participation_rate * 0.5) + (power_score * 0.5)
        
        return min(1.0, max(0.0, score))
    
    def score_risk_assessment(self, proposal: Dict) -> float:
        """Score based on risk factors (lower risk = higher score)"""
        risk_score = proposal.get('risk_score', 0.5)
        
        # Various risk factors
        has_audit = proposal.get('has_audit', False)
        execution_complexity = proposal.get('execution_complexity', 0.5)  # 0=simple, 1=complex
        voting_concentration = proposal.get('top_voter_power', 0)
        
        # Invert risk score (lower risk = higher score)
        base_score = 1 - risk_score
        
        # Bonus for audit
        if has_audit:
            base_score += 0.1
        
        # Penalty for high complexity
        base_score -= execution_complexity * 0.1
        
        # Penalty for voting concentration (centralization risk)
        if voting_concentration > 0.2:
            base_score -= (voting_concentration - 0.2) * 0.5
        
        return min(1.0, max(0.0, base_score))
    
    def score_treasury_impact(self, proposal: Dict) -> float:
        """Score based on treasury and financial impact"""
        requested_amount = proposal.get('requested_amount', 0)
        treasury_balance = proposal.get('treasury_balance', 1000000)
        expected_roi = proposal.get('expected_roi', 0)  # -1 to +inf
        
        # Calculate percentage of treasury requested
        if treasury_balance > 0:
            treasury_percentage = requested_amount / treasury_balance
        else:
            treasury_percentage = 1.0
        
        # Lower percentage = higher score (more sustainable)
        size_score = max(0, 1 - treasury_percentage * 2)
        
        # ROI score (positive ROI = higher score)
        if expected_roi > 0:
            roi_score = min(1.0, expected_roi / 2)  # Cap at 200% ROI
        else:
            roi_score = max(0, 0.5 + expected_roi)  # Penalty for negative ROI
        
        # Combine metrics
        score = (size_score * 0.4) + (roi_score * 0.6)
        
        return min(1.0, max(0.0, score))
    
    def score_execution_quality(self, proposal: Dict) -> float:
        """Score based on proposal quality and execution plan"""
        has_detailed_plan = proposal.get('has_detailed_plan', False)
        has_milestones = proposal.get('has_milestones', False)
        has_team = proposal.get('has_team', False)
        discussion_length = proposal.get('discussion_messages', 0)
        
        score = 0.0
        
        # Quality indicators
        if has_detailed_plan:
            score += 0.3
        if has_milestones:
            score += 0.3
        if has_team:
            score += 0.2
        
        # Discussion engagement (normalized)
        discussion_score = min(0.2, discussion_length / 100)
        score += discussion_score
        
        return min(1.0, max(0.0, score))
    
    def calculate_overall_score(self, proposal: Dict) -> Dict:
        """Calculate overall score with all components"""
        # Calculate individual scores
        scores = {
            'prediction_confidence': self.score_prediction_confidence(proposal),
            'sentiment': self.score_sentiment(proposal),
            'participation': self.score_participation(proposal),
            'risk_assessment': self.score_risk_assessment(proposal),
            'treasury_impact': self.score_treasury_impact(proposal),
            'execution_quality': self.score_execution_quality(proposal)
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[component] * self.weights[component]
            for component in scores
        )
        
        # Determine rating category
        if overall_score >= 0.8:
            rating = 'EXCELLENT'
        elif overall_score >= 0.65:
            rating = 'GOOD'
        elif overall_score >= 0.5:
            rating = 'MODERATE'
        elif overall_score >= 0.35:
            rating = 'POOR'
        else:
            rating = 'CRITICAL'
        
        return {
            'overall_score': round(overall_score, 3),
            'rating': rating,
            'component_scores': {k: round(v, 3) for k, v in scores.items()},
            'weighted_contributions': {
                k: round(scores[k] * self.weights[k], 3) 
                for k in scores
            },
            'proposal_id': proposal.get('id', 'unknown')
        }
    
    def get_recommendation(self, score_result: Dict) -> Dict:
        """Generate investment recommendation based on score"""
        overall_score = score_result['overall_score']
        rating = score_result['rating']
        
        if rating == 'EXCELLENT':
            recommendation = {
                'action': 'STRONG_SUPPORT',
                'confidence': 'HIGH',
                'message': 'This proposal shows excellent metrics across all dimensions. Recommended for strong support.'
            }
        elif rating == 'GOOD':
            recommendation = {
                'action': 'SUPPORT',
                'confidence': 'MEDIUM-HIGH',
                'message': 'This proposal has strong fundamentals with minor concerns. Recommended for support.'
            }
        elif rating == 'MODERATE':
            recommendation = {
                'action': 'NEUTRAL',
                'confidence': 'MEDIUM',
                'message': 'This proposal has mixed signals. Further analysis recommended before voting.'
            }
        elif rating == 'POOR':
            recommendation = {
                'action': 'OPPOSE',
                'confidence': 'MEDIUM-HIGH',
                'message': 'This proposal shows concerning metrics. Opposition recommended unless addressed.'
            }
        else:  # CRITICAL
            recommendation = {
                'action': 'STRONG_OPPOSE',
                'confidence': 'HIGH',
                'message': 'This proposal presents significant risks and poor metrics. Strong opposition recommended.'
            }
        
        return recommendation
    
    def batch_score_proposals(self, proposals: List[Dict]) -> List[Dict]:
        """Score multiple proposals and rank them"""
        results = []
        
        for proposal in proposals:
            score_result = self.calculate_overall_score(proposal)
            recommendation = self.get_recommendation(score_result)
            
            results.append({
                **score_result,
                'recommendation': recommendation,
                'proposal_title': proposal.get('title', 'Unknown'),
                'dao': proposal.get('dao', 'Unknown')
            })
        
        # Sort by overall score (highest first)
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return results


if __name__ == "__main__":
    # Test with mock data
    scorer = ProposalScorer()
    
    mock_proposals = [
        {
            'id': 'ARB-001',
            'title': 'Marketing Campaign Funding',
            'dao': 'Arbitrum DAO',
            'prediction': 0.75,
            'confidence': 0.85,
            'sentiment_score': 0.4,
            'votes_count': 150,
            'total_eligible_voters': 500,
            'voting_power_percentage': 0.35,
            'risk_score': 0.3,
            'has_audit': True,
            'execution_complexity': 0.2,
            'top_voter_power': 0.08,
            'requested_amount': 50000,
            'treasury_balance': 2000000,
            'expected_roi': 1.5,
            'has_detailed_plan': True,
            'has_milestones': True,
            'has_team': True,
            'discussion_messages': 75
        },
        {
            'id': 'ARB-002',
            'title': 'High Risk Protocol Upgrade',
            'dao': 'Arbitrum DAO',
            'prediction': 0.45,
            'confidence': 0.65,
            'sentiment_score': -0.3,
            'votes_count': 50,
            'total_eligible_voters': 500,
            'voting_power_percentage': 0.15,
            'risk_score': 0.8,
            'has_audit': False,
            'execution_complexity': 0.9,
            'top_voter_power': 0.25,
            'requested_amount': 200000,
            'treasury_balance': 2000000,
            'expected_roi': -0.2,
            'has_detailed_plan': False,
            'has_milestones': False,
            'has_team': True,
            'discussion_messages': 20
        }
    ]
    
    results = scorer.batch_score_proposals(mock_proposals)
    
    print("Proposal Scoring Results:\n")
    for result in results:
        print(f"{'='*60}")
        print(f"Proposal: {result['proposal_title']} ({result['proposal_id']})")
        print(f"Overall Score: {result['overall_score']} ({result['rating']})")
        print(f"\nRecommendation: {result['recommendation']['action']}")
        print(f"Confidence: {result['recommendation']['confidence']}")
        print(f"Message: {result['recommendation']['message']}")
        print(f"\nComponent Scores:")
        for component, score in result['component_scores'].items():
            print(f"  {component}: {score}")
        print()
