from typing import Dict, List, Any
import numpy as np
import logging

from .lib.sentiment_base import BaseSentimentAnalyzer
from .lib.sentiment_engine import CombinedSentimentEngine

# Configure logger for this module
logger = logging.getLogger("TwitterSentimentAnalyzer")


class TwitterSentimentAnalyzer(BaseSentimentAnalyzer):
    """
    Анализатор настроений для Twitter/X.

    Примечания:
    - Предполагается, что сборщик (collector) отдаёт список твитов в виде словарей
      с полями: 'text', 'author_id', 'likes', 'retweets', 'created_at', 'id' и т.п.
    - Для production рекомендуется подключать rate-limiter и resilient fetchers.
    """

    def __init__(self) -> None:
        self.engine = CombinedSentimentEngine()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        logger.debug("Analyzing tweet text.")
        return self.engine.analyze_text(text)

    def aggregate_messages(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Агрегирование твитов по proposal/хэштегу.

        Args:
            tweets: список твитов, каждый твит — dict
        Returns:
            агрегированная статистика
        """
        if not tweets:
            logger.warning("No tweets provided to aggregate.")
            return {
                "avg_sentiment": 0.0,
                "std_sentiment": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "total_tweets": 0,
                "total_engagement": 0,
                "avg_engagement_per_tweet": 0.0,
                "influential_accounts": [],
            }

        logger.info("Aggregating %d tweets.", len(tweets))

        # Анализ каждого твита
        scores = [self.analyze_text(t.get("text", "")) for t in tweets]

        # Engagement = likes + retweets (можно расширить: replies, quotes)
        engagements = [t.get("likes", 0) + t.get("retweets", 0) for t in tweets]
        max_engagement = max(engagements) or 1
        weights = [e / max_engagement for e in engagements]

        # Взвешенное агрегирование комбинированных скоров
        combined_scores = [s["combined_score"] for s in scores]
        weighted_scores = [cs * w for cs, w in zip(combined_scores, weights)]

        avg_sentiment = float(np.mean(weighted_scores))
        std_sentiment = float(np.std(weighted_scores))

        positive_count = sum(1 for s in scores if s["sentiment"] == "positive")
        negative_count = sum(1 for s in scores if s["sentiment"] == "negative")
        neutral_count = sum(1 for s in scores if s["sentiment"] == "neutral")
        total = len(scores)

        total_engagement = sum(engagements)
        avg_engagement_per_tweet = total_engagement / total if total else 0.0

        aggregated = {
            "avg_sentiment": avg_sentiment,
            "std_sentiment": std_sentiment,
            "positive_ratio": positive_count / total,
            "negative_ratio": negative_count / total,
            "neutral_ratio": neutral_count / total,
            "total_tweets": total,
            "total_engagement": int(total_engagement),
            "avg_engagement_per_tweet": float(avg_engagement_per_tweet),
            "influential_accounts": self._get_influential_accounts(tweets, scores),
        }

        logger.info("Twitter aggregation complete.")
        return aggregated

    def _get_influential_accounts(self, tweets: List[Dict[str, Any]], scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Собирает метрики по аккаунтам и возвращает топ-N по influence_score.
        influence_score = avg_sentiment * (total_engagement / 100)
        """
        logger.debug("Computing influential accounts.")
        account_data: Dict[str, Dict[str, Any]] = {}
        for tw, sc in zip(tweets, scores):
            author = tw.get("author_id") or "unknown"
            ent = tw.get("likes", 0) + tw.get("retweets", 0)
            if author not in account_data:
                account_data[author] = {"sentiment_scores": [], "total_engagement": 0, "tweet_count": 0}
            account_data[author]["sentiment_scores"].append(sc["combined_score"])
            account_data[author]["total_engagement"] += ent
            account_data[author]["tweet_count"] += 1

        influential: List[Dict[str, Any]] = []
        for author, d in account_data.items():
            avg_s = float(np.mean(d["sentiment_scores"]))
            total_e = int(d["total_engagement"])
            influence_score = avg_s * (total_e / 100.0)
            influential.append({
                "author": author,
                "avg_sentiment": avg_s,
                "total_engagement": total_e,
                "tweet_count": d["tweet_count"],
                "influence_score": float(influence_score),
            })

        # сортируем по убыванию influence_score, возвращаем топ-5
        influential_sorted = sorted(influential, key=lambda x: x["influence_score"], reverse=True)[:5]
        logger.debug("Top influential accounts computed: %s", influential_sorted)
        return influential_sorted

    def get_source_name(self) -> str:
        return "twitter"
