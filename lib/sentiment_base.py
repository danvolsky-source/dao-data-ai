from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseSentimentAnalyzer(ABC):
    """Базовый интерфейс для всех sentiment-анализаторов."""

    @abstractmethod
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Анализ тональности одного сообщения."""
        raise NotImplementedError

    @abstractmethod
    def aggregate_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Агрегация sentiment-метрик по списку сообщений."""
        raise NotImplementedError

    @abstractmethod
    def get_source_name(self) -> str:
        """Имя источника (discord, forum, twitter, telegram, reddit)."""
        raise NotImplementedError
