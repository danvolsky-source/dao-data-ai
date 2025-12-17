from typing import Dict, List, Any
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob


class CombinedSentimentEngine:
    """
    Общий движок sentiment-аналитики для dao-data-ai.

    - analyze_text: VADER + TextBlob для одного сообщения
    - aggregate_scores: агрегация списка результатов (avg_sentiment, ratios, trend)
    """

    def __init__(self) -> None:
        self.vader = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ одного текста (VADER + TextBlob + итоговая метка)."""
        if not text or not text.strip():
            return {
                "vader_compound": 0.0,
                "vader_pos": 0.0,
                "vader_neu": 1.0,
                "vader_neg": 0.0,
                "textblob_polarity": 0.0,
                "textblob_subjectivity": 0.0,
                "combined_score": 0.0,
                "sentiment": "neutral",
                "confidence": 0.0,
            }

        vader_scores = self.vader.polarity_scores(text)

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        combined_score = (vader_scores["compound"] + polarity) / 2

        if combined_score >= 0.2:
            label = "positive"
        elif combined_score <= -0.2:
            label = "negative"
        else:
            label = "neutral"

        return {
            "vader_compound": vader_scores["compound"],
            "vader_pos": vader_scores["pos"],
            "vader_neu": vader_scores["neu"],
            "vader_neg": vader_scores["neg"],
            "textblob_polarity": polarity,
            "textblob_subjectivity": subjectivity,
            "combined_score": combined_score,
            "sentiment": label,
            "confidence": abs(combined_score),
        }

    def aggregate_scores(self, scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Агрегация списка результатов analyze_text."""
        if not scores:
            return {
                "avg_sentiment": 0.0,
                "std_sentiment": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "total_messages": 0,
                "sentiment_trend": "neutral",
            }

        sentiments = [s.get("sentiment", "neutral") for s in scores]
        combined_scores = [float(s.get("combined_score", 0.0)) for s in scores]

        positive_count = sentiments.count("positive")
        negative_count = sentiments.count("negative")
        neutral_count = sentiments.count("neutral")
        total = len(sentiments)

        avg = float(np.mean(combined_scores))
        std = float(np.std(combined_scores))

        last_score = combined_scores[-1]
        trend = "improving" if last_score > avg else "declining"

        return {
            "avg_sentiment": avg,
            "std_sentiment": std,
            "positive_ratio": positive_count / total,
            "negative_ratio": negative_count / total,
            "neutral_ratio": neutral_count / total,
            "total_messages": total,
            "sentiment_trend": trend,
        }
