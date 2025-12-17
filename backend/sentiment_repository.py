"""
SentimentRepository: обёртка для чтения sentiment-метрик из Supabase.

Ожидаемые таблицы в schema public:
  - discord_sentiment
  - forum_sentiment
  - twitter_sentiment
  - cross_channel_sentiment
"""

from typing import Optional, Dict, Any
from supabase import Client


class SentimentRepository:
    """Simple repository for sentiment-related tables."""

    def __init__(self, client: Client) -> None:
        """
        client: Supabase Client, например созданный через create_client(
            SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
        )
        """
        self.client = client

    def _single(self, table: str, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Возвращает одну строку из таблицы по proposal_id или None."""
        resp = (
            self.client.table(table)
            .select("*")
            .eq("proposal_id", proposal_id)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None

    # ----- Discord -----

    def get_discord_sentiment(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Ожидается таблица discord_sentiment с полями:
          proposal_id, avg_sentiment, positive_ratio, negative_ratio, ...
        """
        return self._single("discord_sentiment", proposal_id)

    # ----- Forum -----

    def get_forum_sentiment(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Ожидается таблица forum_sentiment с полями:
          proposal_id, avg_sentiment, positive_ratio, unique_authors, ...
        Если у proposal_id несколько thread_id, здесь пока берём первую запись.
        """
        return self._single("forum_sentiment", proposal_id)

    # ----- Twitter -----

    def get_twitter_sentiment(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Ожидается таблица twitter_sentiment с полями:
          proposal_id, avg_sentiment, total_engagement, ...
        """
        return self._single("twitter_sentiment", proposal_id)

    # ----- Cross-channel -----

    def get_cross_channel_sentiment(
        self, proposal_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Ожидается таблица cross_channel_sentiment с полями:
          proposal_id, overall_avg_sentiment, channel_consistency, ...
        """
        return self._single("cross_channel_sentiment", proposal_id)
