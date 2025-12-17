import logging
from typing import Any, Dict
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the input data by cleaning and transforming it.

    Args:
        data (pd.DataFrame): Input data to preprocess.

    Returns:
        pd.DataFrame: Preprocessed data.
    """
    try:
        logger.debug("Starting data preprocessing")
        
        # Drop duplicates and reset index
        data_cleaned = data.drop_duplicates().reset_index(drop=True)
        logger.debug("Dropped duplicates and reset index")

        # Fill missing values with median for numeric columns
        numeric_cols = data_cleaned.select_dtypes(include=['number']).columns
        logger.debug(f"Numeric columns identified: {numeric_cols}")
        
        for col in numeric_cols:
            median_value = data_cleaned[col].median()
            data_cleaned[col].fillna(median_value, inplace=True)
            logger.debug(f"Filled missing values in column {col} with median: {median_value}")

        return data_cleaned

    except Exception as e:
        logger.error(f"Error in preprocess_data: {e}")
        raise

def engineer_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer new features from the input data.

    Args:
        data (pd.DataFrame): Input data for feature engineering.

    Returns:
        pd.DataFrame: Data with engineered features.
    """
    try:
        logger.debug("Starting feature engineering")
        
        # Example feature engineering
        data['feature_sum'] = data.sum(axis=1)
        logger.debug("Generated feature: feature_sum (row-wise sum of DataFrame)")

        return data

    except Exception as e:
        logger.error(f"Error in engineer_features: {e}")
        raise

if __name__ == "__main__":
    import pytest

    # Example for testing
    logger.debug("Starting testing feature engineering script")

    @pytest.fixture
    def sample_data() -> pd.DataFrame:
        return pd.DataFrame({
            "A": [1, 2, None, 4],
            "B": [None, 2, 3, 4],
            "C": [1, 2, 3, None]
        })

    def test_preprocess_data(sample_data):
        processed = preprocess_data(sample_data)
        assert not processed.isnull().any().any()
        assert len(processed) == 4

    def test_engineer_features(sample_data):
        engineered = engineer_features(sample_data.fillna(0))  # Fill NaNs for mock test
        assert 'feature_sum' in engineered.columns
        assert engineered['feature_sum'][0] == sum([1, 0, 1])

    pytest.main()