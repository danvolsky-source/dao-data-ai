import os
import discord
from typing import Dict, List, Any
from datetime import datetime

from .lib.sentiment_base import BaseSentimentAnalyzer
from .lib.sentiment_engine import CombinedSentimentEngine


class DiscordAnalyzer(BaseSentimentAnalyzer):
    """Analyzes Discord threads for DAO proposals."""

    def __init__(self, token: str = None) -> None:
        self.token = token or os.getenv("DISCORD_TOKEN")
        self.engine = CombinedSentimentEngine()
        self.client = discord.Client(intents=discord.Intents.default())

    # --- BaseSentimentAnalyzer API ---

    def analyze_text(self, text: str) -> Dict[str, Any]:
        return self.engine.analyze_text(text)

    def aggregate_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            return self._empty_analysis()

        scores = []
        positive_count = negative_count = neutral_count = 0

        for msg in messages:
            text = msg.get("content", "")
            if not text or len(text) < 5:
                continue
            sentiment = self.analyze_text(text)
            scores.append(sentiment)

            if sentiment["sentiment"] == "positive":
                positive_count += 1
            elif sentiment["sentiment"] == "negative":
                negative_count += 1
            else:
                neutral_count += 1

        if not scores:
            return self._empty_analysis()

        agg = self.engine.aggregate_scores(scores)
        total_messages = agg["total_messages"]

        agg.update(
            {
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_ratio": positive_count / total_messages,
                "negative_ratio": negative_count / total_messages,
            }
        )
        # оставляем avg_vader / avg_textblob, если нужно:
        agg["avg_vader_score"] = float(
            sum(s["vader_compound"] for s in scores) / total_messages
        )
        agg["avg_textblob_polarity"] = float(
            sum(s["textblob_polarity"] for s in scores) / total_messages
        )

        return agg

    def get_source_name(self) -> str:
        return "discord"

    # --- старые вспомогательные методы (слегка адаптированы) ---

    def _empty_analysis(self) -> Dict[str, Any]:
        return {
            "total_messages": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "positive_ratio": 0.0,
            "negative_ratio": 0.0,
            "avg_sentiment": 0.0,
            "overall_sentiment": "neutral",
            "engagement_level": "none",
        }

    def _calculate_engagement(self, messages: List[Dict[str, Any]]) -> str:
        count = len(messages)
        if count >= 100:
            return "very_high"
        elif count >= 50:
            return "high"
        elif count >= 20:
            return "medium"
        elif count >= 5:
            return "low"
        else:
            return "very_low"

    async def fetch_thread_messages(self, channel_id: int, thread_id: int) -> List[Dict]:
        # TODO: реальная интеграция с Discord API
        return []

    def extract_key_topics(self, messages: List[Dict]) -> List[str]:
        # TODO: TF-IDF / keyword extraction
        return ["governance", "proposal", "voting"]
