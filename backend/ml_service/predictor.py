"""ML Predictor for DAO Proposal Outcomes"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from feature_engineer import ProposalFeatureEngineer

class ProposalPredictor:
    """Predicts DAO proposal outcomes using ML"""
    
    def __init__(self, model_path: str = "models/proposal_model.pkl"):
        self.model_path = model_path
        self.feature_engineer = ProposalFeatureEngineer()
        self.model = None
        self.feature_cols = None
        
        # Try to load existing model
        if os.path.exists(model_path):
            self.load_model()
        else:
            self._init_model()
    
    def _init_model(self):
        """Initialize XGBoost model with optimal parameters"""
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
    
    def train(self, proposals: List[Dict]):
        """Train model on historical proposals"""
        # Prepare dataset
        df = self.feature_engineer.prepare_dataset(proposals)
        
        # Filter out proposals without labels
        df_labeled = df[df['target'].notna()].copy()
        
        if len(df_labeled) < 10:
            print("Not enough labeled data for training")
            return False
        
        # Separate features and target
        self.feature_cols = [c for c in df_labeled.columns 
                            if c not in ['proposal_id', 'target']]
        
        X = df_labeled[self.feature_cols]
        y = df_labeled['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"Training accuracy: {train_score:.3f}")
        print(f"Test accuracy: {test_score:.3f}")
        
        # Save model
        self.save_model()
        
        return True
    
    def predict(self, proposal: Dict) -> Dict:
        """Predict outcome probability for a proposal"""
        if self.model is None:
            return {'probability': 0.5, 'confidence': 'low'}
        
        # Extract features
        features = self.feature_engineer.extract_features(proposal)
        
        # Create DataFrame with correct columns
        if self.feature_cols:
            feat_df = pd.DataFrame([features])[self.feature_cols]
        else:
            feat_df = pd.DataFrame([features])
        
        # Get prediction
        proba = self.model.predict_proba(feat_df)[0]
        
        # Calculate confidence
        confidence_score = abs(proba[1] - 0.5) * 2
        if confidence_score > 0.7:
            confidence = 'high'
        elif confidence_score > 0.4:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'probability': float(proba[1]),
            'confidence': confidence,
            'pass_likelihood': 'likely' if proba[1] > 0.6 else 'unlikely'
        }
    
    def predict_batch(self, proposals: List[Dict]) -> List[Dict]:
        """Predict outcomes for multiple proposals"""
        results = []
        for prop in proposals:
            pred = self.predict(prop)
            pred['proposal_id'] = prop.get('id', '')
            results.append(pred)
        return results
    
    def save_model(self):
        """Save model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_cols': self.feature_cols
        }
        
        joblib.dump(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load model from disk"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.feature_cols = model_data['feature_cols']
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self._init_model()

if __name__ == "__main__":
    # Test predictor
    predictor = ProposalPredictor()
    
    # Mock training data
    mock_proposals = [
        {'id': '1', 'votes_for': 30000000, 'votes_against': 5000000, 
         'status': 'passed', 'vote_count': 200},
        {'id': '2', 'votes_for': 10000000, 'votes_against': 25000000, 
         'status': 'defeated', 'vote_count': 150},
        {'id': '3', 'votes_for': 28000000, 'votes_against': 8000000, 
         'status': 'passed', 'vote_count': 180}
    ]
    
    print("Training model...")
    predictor.train(mock_proposals)
    
    # Test prediction
    test_proposal = {
        'id': '4',
        'votes_for': 27000000,
        'votes_against': 9000000,
        'vote_count': 175
    }
    
    result = predictor.predict(test_proposal)
    print(f"\nPrediction: {result}")
