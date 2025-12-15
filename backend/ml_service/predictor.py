predictor.py# ML Predictor for DAO Governance
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import joblib
import os
from .features.feature_engineering import FeatureEngineer

class ProposalPredictor:
    def __init__(self, supabase_client):
        self.feature_engineer = FeatureEngineer(supabase_client)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_path = "proposal_model.pkl"
        self.is_trained = False
    
    def train(self, proposals_df):
        """Train model on historical proposals
        proposals_df должен содержать: proposal_id, outcome (passed/rejected)
        """
        X, y = self.feature_engineer.prepare_training_data(proposals_df)
        if len(X) < 10:
            raise ValueError("Need at least 10 proposals for training")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        self.is_trained = True
        return {"train_accuracy": train_score, "test_accuracy": test_score}
    
    def predict(self, proposal_id: str) -> dict:
        """Predict proposal outcome"""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        features = self.feature_engineer.extract_proposal_features(proposal_id)
        X = pd.DataFrame([features])
        X = X.fillna(0)
        
        probability = self.model.predict_proba(X)[0][1]
        prediction = "passed" if probability > 0.5 else "rejected"
        
        return {
            "proposal_id": proposal_id,
            "prediction": prediction,
            "confidence": float(probability),
            "features_used": len(features)
        }
    
    def save_model(self):
        joblib.dump(self.model, self.model_path)
    
    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            return True
        return False
