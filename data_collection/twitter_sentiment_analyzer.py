from typing import Dict, List, Any
import numpy as np

from .lib.sentiment_base import BaseSentimentAnalyzer
from .lib.sentiment_engine import CombinedSentimentEngine


class TwitterSentimentAnalyzer(BaseSentimentAnalyzer):
    """Sentiment-анализатор для Twitter/X с учётом engagement."""

    def __init__(self) -> None:
        self.engine = CombinedSentimentEngine()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        return self.engine.analyze_text(text)

    def aggregate_messages(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not tweets:
            return {
                "avg_sentiment": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "total_tweets": 0,
                "total_engagement": 0,
                "avg_engagement_per_tweet": 0.0,
                "influential_accounts": [],
            }

        scores = [self.analyze_text(t["text"]) for t in tweets]

        engagements = [
            t.get("likes", 0) + t.get("retweets", 0) for t in tweets
        ]
        max_engagement = max(engagements) or 1
        weights = [e / max_engagement for e in engagements]

        weighted_scores = [
            s["combined_score"] * w for s, w in zip(scores, weights)
        ]

        sentiments = [s["sentiment"] for s in scores]
        total = len(scores)

        positive_ratio = sum(1 for s in sentiments if s == "positive") / total
        negative_ratio = sum(1 for s in sentiments if s == "negative") / total
        neutral_ratio = sum(1 for s in sentiments if s == "neutral") / total

        total_engagement = sum(engagements)
        avg_engagement = total_engagement / total if total else 0.0

        aggregated = {
            "avg_sentiment": float(np.mean(weighted_scores)),
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "neutral_ratio": neutral_ratio,
            "total_tweets": total,
            "total_engagement": int(total_engagement),
            "avg_engagement_per_tweet": float(avg_engagement),
            "influential_accounts": self.get_influential_accounts(tweets, scores),
        }
        return aggregated

    def get_influential_accounts(
        self, tweets: List[Dict[str, Any]], scores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        account_data: Dict[str, Dict[str, Any]] = {}

        for tweet, score in zip(tweets, scores):
            author = str(tweet.get("author_id") or "unknown")
            engagement = tweet.get("likes", 0) + tweet.get("retweets", 0)
            account_data.setdefault(
                author, {"sentiment_scores": [], "total_engagement": 0}
            )
            account_data[author]["sentiment_scores"].append(score["combined_score"])
            account_data[author]["total_engagement"] += engagement

        influential = []
        for author, data in account_data.items():
            avg_sent = float(np.mean(data["sentiment_scores"]))
            total_eng = int(data["total_engagement"])
            influence_score = avg_sent * (total_eng / 100.0)
            influential.append(
                {
                    "author_id": author,
                    "avg_sentiment": avg_sent,
                    "total_engagement": total_eng,
                    "influence_score": influence_score,
                }
            )

        return sorted(
            influential, key=lambda x: x["influence_score"], reverse=True
        )[:5]

    def get_source_name(self) -> str:
        return "twitter"
