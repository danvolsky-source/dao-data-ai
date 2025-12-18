"""
Regulatory Disclaimer Content
Standard disclaimers for all prediction and analytical outputs
"""

# Primary Regulatory Disclaimer
MAIN_DISCLAIMER = """
⚠️ IMPORTANT RISK AND LIMITATION NOTICE

Information on this platform is provided exclusively for 
informational and educational purposes. This is NOT:
- Investment advice
- Trading signals
- Financial recommendations
- A guarantee of future results

LIMITATIONS AND RISKS:
1. Predictions are based on historical data and may be inaccurate
2. Past performance does not guarantee future results
3. Only public data from official sources is used
4. Sentiment analysis may not reflect actual community opinion
5. ML models are experimental and may contain errors

RECOMMENDATIONS:
- DO NOT use this information for making trading decisions
- Conduct your own research (DYOR)
- Consult with qualified financial advisors
- Only invest funds you can afford to lose

All risks are borne by the user. We are not responsible for any losses
arising from use of this platform.
"""

# Short Disclaimer for API Responses
SHORT_DISCLAIMER = (
    "⚠️ This is analytical information, not investment advice. "
    "Use for educational purposes only. All risks are borne by the user."
)

# Prediction-Specific Disclaimer
PREDICTION_DISCLAIMER = (
    "This prediction is based on ML model and historical data. "
    "Accuracy is not guaranteed. DO NOT use for trading decisions. "
    "Confidence score shows model certainty but is not a guarantee."
)

# Sentiment Analysis Disclaimer
SENTIMENT_DISCLAIMER = (
    "Sentiment analysis is based on public messages and may not reflect "
    "the true opinion of the entire community. Use as one of many factors "
    "in your research. This is not investment advice."
)

# Model Performance Disclaimer
MODEL_DISCLAIMER = (
    "Model metrics are based on backtesting historical data. "
    "Past performance does not guarantee future results. "
    "Models are regularly updated and may change."
)

# Live Tracking Disclaimer
LIVE_TRACKING_DISCLAIMER = (
    "Live tracking shows actual model performance on "
    "completed proposals. This is for transparency and is not "
    "a guarantee of future accuracy."
)

# Data Source Disclaimer
DATA_SOURCE_DISCLAIMER = (
    "All data obtained from public sources: Snapshot, Tally, Discord, "
    "community forums. We do not guarantee completeness or accuracy of data. "
    "Always verify information from primary sources."
)

# Confidence Threshold Message
CONFIDENCE_THRESHOLD_MESSAGE = (
    "Predictions with confidence score below 85% may be insufficiently reliable. "
    "Use such predictions with extra caution."
)

# Terms of Service Summary
TOS_SUMMARY = """
TERMS OF SERVICE (SUMMARY)

1. SERVICE PURPOSE
   The platform is intended for analysis and research of DAO data.
   This is a tool for education, not for trading.

2. NO FINANCIAL ADVICE
   We do not provide financial, investment, or legal advice.
   Users must consult with qualified professionals.

3. LIMITATION OF LIABILITY
   We are not responsible for any losses resulting from
   the use of the platform or reliance on the information provided.

4. EXPERIMENTAL NATURE
   ML models and analytics are experimental. They may contain
   errors and inaccuracies. Do not rely solely on them.

5. PUBLIC DATA
   We use only publicly available data. Users are responsible
   for verifying the accuracy of information.

6. CHANGES TO SERVICE
   We reserve the right to modify, suspend, or terminate
   any part of the service at any time without prior notice.

By using this platform, you agree to these terms.
"""

# Privacy Policy Summary
PRIVACY_SUMMARY = """
PRIVACY POLICY (SUMMARY)

1. DATA COLLECTION
   We collect minimally necessary data:
   - IP addresses (for security and audit)
   - User agents (for technical support)
   - API requests (to improve service)
   - Wallet addresses (only if you connect a wallet)

2. DATA USAGE
   Data is used for:
   - Providing and improving the service
   - Ensuring security
   - Regulatory compliance
   - Analytics and research

3. DATA STORAGE
   - Data stored in secure database (Supabase)
   - Encryption applied during transmission and storage
   - Access limited to authorized personnel

4. DATA DISCLOSURE
   We do not sell your data to third parties.
   Disclosure is possible only:
   - As required by regulators
   - To prevent fraud
   - With your explicit consent

5. YOUR RIGHTS
   You have the right to:
   - Request access to your data
   - Request data deletion
   - Withdraw consent for processing

For privacy questions: privacy@daodataai.com
"""


def get_full_disclaimer() -> str:
    """Return complete disclaimer text"""
    return MAIN_DISCLAIMER


def get_api_disclaimer(disclaimer_type: str = "short") -> str:
    """
    Get appropriate disclaimer for API response
    
    Args:
        disclaimer_type: Type of disclaimer ('short', 'prediction', 'sentiment', 'model', 'tracking')
    
    Returns:
        Appropriate disclaimer text
    """
    disclaimers = {
        "short": SHORT_DISCLAIMER,
        "prediction": PREDICTION_DISCLAIMER,
        "sentiment": SENTIMENT_DISCLAIMER,
        "model": MODEL_DISCLAIMER,
        "tracking": LIVE_TRACKING_DISCLAIMER,
        "data": DATA_SOURCE_DISCLAIMER
    }
    
    return disclaimers.get(disclaimer_type, SHORT_DISCLAIMER)


def get_confidence_warning(confidence: float) -> str:
    """
    Get warning message based on confidence score
    
    Args:
        confidence: Model confidence score (0-1)
    
    Returns:
        Warning message if confidence is low
    """
    if confidence < 0.85:
        return CONFIDENCE_THRESHOLD_MESSAGE
    return ""


def wrap_response_with_disclaimer(data: dict, disclaimer_type: str = "short") -> dict:
    """
    Wrap API response with appropriate disclaimer
    
    Args:
        data: Response data
        disclaimer_type: Type of disclaimer to include
    
    Returns:
        Response dict with disclaimer
    """
    return {
        "disclaimer": get_api_disclaimer(disclaimer_type),
        "data": data,
        "terms": "By using this data, you agree to our Terms of Service",
        "privacy": "See our Privacy Policy for data handling practices"
    }
