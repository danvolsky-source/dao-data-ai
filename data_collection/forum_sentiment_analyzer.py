from typing import Dict, List, Any
import pandas as pd

from .lib.sentiment_base import BaseSentimentAnalyzer
from .lib.sentiment_engine import CombinedSentimentEngine


class ForumSentimentAnalyzer(BaseSentimentAnalyzer):
    """Sentiment-анализатор для Discourse форума Arbitrum."""

    def __init__(self) -> None:
        self.engine = CombinedSentimentEngine()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        return self.engine.analyze_text(text)

    def aggregate_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not messages:
            base = self.engine.aggregate_scores([])
            base.update(
                {
                    "unique_authors": 0,
                    "avg_posts_per_author": 0.0,
                    "top_positive_authors": [],
                }
            )
            return base

        scores = [self.analyze_text(m.get("content", "")) for m in messages]
        aggregated = self.engine.aggregate_scores(scores)

        df = pd.DataFrame(messages)
        unique_authors = df["author"].nunique() if "author" in df.columns else 0
        aggregated["unique_authors"] = int(unique_authors)
        aggregated["avg_posts_per_author"] = (
            len(messages) / unique_authors if unique_authors else 0.0
        )

        author_sentiments: Dict[str, List[float]] = {}
        for msg, score in zip(messages, scores):
            author = msg.get("author") or "unknown"
            author_sentiments.setdefault(author, []).append(score["combined_score"])

        top_positive = sorted(
            (
                {
                    "author": author,
                    "avg_sentiment": float(sum(vals) / len(vals)),
                    "message_count": len(vals),
                }
                for author, vals in author_sentiments.items()
            ),
            key=lambda x: x["avg_sentiment"],
            reverse=True,
        )[:3]

        aggregated["top_positive_authors"] = top_positive
        return aggregated

    def get_source_name(self) -> str:
        return "forum"
