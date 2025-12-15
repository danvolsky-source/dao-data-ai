"""ML Service for DAO Governance Analytics

Предоставляет ML модели для предсказания исходов голосований,
анализа влияния делегатов и оценки участия.
"""

__version__ = "0.1.0"

from .features.feature_engineering import FeatureEngineer
from .models.base_model import BaseModel
from .models.random_forest_model import RandomForestProposalModel
from .inference.predictor import ProposalPredictor

__all__ = [
    "FeatureEngineer",
    "BaseModel",
    "RandomForestProposalModel",
    "ProposalPredictor",
]
