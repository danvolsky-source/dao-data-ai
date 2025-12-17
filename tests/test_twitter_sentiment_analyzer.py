import pytest
from data_collection.twitter_sentiment_analyzer import TwitterSentimentAnalyzer

@pytest.fixture
def sample_tweets():
    return [
        {"text": "I love this proposal! Great work", "author_id": "a1", "likes": 10, "retweets": 2},
        {"text": "Not sure this is good", "author_id": "a2", "likes": 1, "retweets": 0},
        {"text": "Neutral comment", "author_id": "a3", "likes": 0, "retweets": 0},
        {"text": "Absolutely fantastic decision!", "author_id": "a1", "likes": 5, "retweets": 1},
    ]


def test_aggregate_messages(sample_tweets):
    analyzer = TwitterSentimentAnalyzer()
    agg = analyzer.aggregate_messages(sample_tweets)
    assert "avg_sentiment" in agg
    assert agg["total_tweets"] == 4
    assert isinstance(agg["influential_accounts"], list)


def test_empty_list():
    analyzer = TwitterSentimentAnalyzer()
    agg = analyzer.aggregate_messages([])
    assert agg["total_tweets"] == 0
