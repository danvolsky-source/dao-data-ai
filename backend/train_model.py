#!/usr/bin/env python3
"""
ML Model Training Script for DAO Governance Predictions
Trains XGBoost classifier on historical proposal data
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import joblib
from supabase import create_client, Client

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    try:
    from ml_service.feature_engineer import ProposalFeatureEngineer
    from ml_service.predictor import ProposalPredictor
    from sentiment_repository import SentimentRepository
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
except ImportError as e:
    print(f"Error: Missing required packages. Install with: pip install xgboost scikit-learn")
    print(f"Details: {e}")
    sys.exit(1)


class ModelTrainer:
    """Train and evaluate XGBoost model for proposal outcome prediction"""
    
    def __init__(self, db_url: str = None, db_key: str = None):
        """Initialize trainer with database connection"""
        self.db_url = db_url or os.getenv("SUPABASE_URL")
        self.db_key = db_key or os.getenv("SUPABASE_KEY")
        
        if not self.db_url or not self.db_key:
            raise ValueError("Database credentials required (SUPABASE_URL, SUPABASE_KEY)")
        
        self.supabase: Client = create_client(self.db_url, self.db_key)
        self.feature_engineer = FeatureEngineer()
        self.model = None
        
    def fetch_training_data(self) -> pd.DataFrame:
        """
        Fetch historical proposals from database
        Returns DataFrame with proposal data
        """
        print("\n📊 Fetching training data from database...")
        
        try:
            # Get all proposals with votes
            proposals_result = self.supabase.table("proposals").select("*").execute()
            
            if not proposals_result.data:
                raise ValueError("No training data found in database")
            
            df = pd.DataFrame(proposals_result.data)
            print(f"✅ Loaded {len(df)} proposals")
            
            # Get votes for each proposal
            votes_result = self.supabase.table("votes").select("*").execute()
            votes_df = pd.DataFrame(votes_result.data) if votes_result.data else pd.DataFrame()
            
            if not votes_df.empty:
                # Aggregate votes per proposal
                votes_grouped = votes_df.groupby('proposal_id').agg({
                    'voting_power': 'sum',
                    'voter': 'nunique'
                }).rename(columns={'voting_power': 'total_voting_power', 'voter': 'unique_voters'})
                
                df = df.merge(votes_grouped, left_on='proposal_id', right_index=True, how='left')
            
            # Create target variable (outcome)
            df['outcome'] = (df['votes_for'] > df['votes_against']).astype(int)
            
            return df
            
        except Exception as e:
            raise Exception(f"Failed to fetch training data: {str(e)}")
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Engineer features and prepare training data
        Returns X (features), y (labels)
        """
        print("\n🔧 Engineering features...")
        
        X_list = []
        y_list = []
        
        for idx, row in df.iterrows():
            try:
                # Convert row to proposal dict
                proposal = row.to_dict()
                
                # Engineer features
                features = self.feature_engineer.engineer_features(proposal)
                feature_vector = list(features.values())
                
                X_list.append(feature_vector)
                y_list.append(row['outcome'])
                
            except Exception as e:
                print(f"⚠️  Skipping proposal {row.get('proposal_id')}: {str(e)}")
                continue
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        print(f"✅ Engineered {X.shape[1]} features for {X.shape[0]} samples")
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Train XGBoost model with cross-validation
        Returns training metrics
        """
        print("\n🎯 Training XGBoost model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train model
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_proba)
        }
        
        print("\n📈 Model Performance:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
        
        return metrics
    
    def save_model(self, path: str = "ml_service/models/proposal_predictor.pkl"):
        """
        Save trained model to disk
        """
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
        
        model_dir = os.path.dirname(path)
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(self.model, path)
        print(f"\n💾 Model saved to: {path}")
    
    def run(self):
        """
        Complete training pipeline
        """
        print("="*60)
        print("🚀 DAO Governance ML Model Training")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # Fetch data
            df = self.fetch_training_data()
            
            # Prepare features
            X, y = self.prepare_features(df)
            
            if len(X) < 10:
                raise ValueError(f"Insufficient training data: {len(X)} samples (minimum 10 required)")
            
            # Train model
            metrics = self.train(X, y)
            
            # Save model
            self.save_model()
            
            print("\n" + "="*60)
            print("✅ Training completed successfully!")
            print("="*60)
            
            return metrics
            
        except Exception as e:
            print(f"\n❌ Training failed: {str(e)}")
            raise


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()
