"""Discord Thread Analyzer with Sentiment Analysis"""
import os
import discord
from typing import Dict, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from datetime import datetime

class DiscordAnalyzer:
    """Analyzes Discord threads for DAO proposals"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv('DISCORD_TOKEN')
        self.vader = SentimentIntensityAnalyzer()
        self.client = discord.Client(intents=discord.Intents.default())
        
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of a single message"""
        # VADER sentiment (good for social media)
        vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob sentiment (more general)
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity
        
        # Combined sentiment
        combined_score = (vader_scores['compound'] + textblob_polarity) / 2
        
        # Classify sentiment
        if combined_score >= 0.2:
            sentiment_label = 'positive'
        elif combined_score <= -0.2:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'vader_compound': vader_scores['compound'],
            'vader_pos': vader_scores['pos'],
            'vader_neu': vader_scores['neu'],
            'vader_neg': vader_scores['neg'],
            'textblob_polarity': textblob_polarity,
            'textblob_subjectivity': textblob_subjectivity,
            'combined_score': combined_score,
            'sentiment': sentiment_label
        }
    
    def analyze_thread(self, messages: List[Dict]) -> Dict:
        """Analyze sentiment across entire thread"""
        if not messages:
            return self._empty_analysis()
        
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for msg in messages:
            text = msg.get('content', '')
            if not text or len(text) < 5:
                continue
            
            sentiment = self.analyze_sentiment(text)
            sentiments.append(sentiment)
            
            if sentiment['sentiment'] == 'positive':
                positive_count += 1
            elif sentiment['sentiment'] == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
        
        if not sentiments:
            return self._empty_analysis()
        
        # Aggregate metrics
        avg_vader = sum(s['vader_compound'] for s in sentiments) / len(sentiments)
        avg_textblob = sum(s['textblob_polarity'] for s in sentiments) / len(sentiments)
        avg_combined = sum(s['combined_score'] for s in sentiments) / len(sentiments)
        
        total_messages = len(sentiments)
        
        return {
            'total_messages': total_messages,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': positive_count / total_messages,
            'negative_ratio': negative_count / total_messages,
            'avg_sentiment': avg_combined,
            'avg_vader_score': avg_vader,
            'avg_textblob_polarity': avg_textblob,
            'overall_sentiment': self._classify_overall(avg_combined),
            'engagement_level': self._calculate_engagement(messages)
        }
    
    def _classify_overall(self, score: float) -> str:
        """Classify overall thread sentiment"""
        if score >= 0.3:
            return 'very_positive'
        elif score >= 0.1:
            return 'positive'
        elif score <= -0.3:
            return 'very_negative'
        elif score <= -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_engagement(self, messages: List[Dict]) -> str:
        """Calculate engagement level from message count"""
        count = len(messages)
        if count >= 100:
            return 'very_high'
        elif count >= 50:
            return 'high'
        elif count >= 20:
            return 'medium'
        elif count >= 5:
            return 'low'
        else:
            return 'very_low'
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis"""
        return {
            'total_messages': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'positive_ratio': 0,
            'negative_ratio': 0,
            'avg_sentiment': 0,
            'overall_sentiment': 'neutral',
            'engagement_level': 'none'
        }
    
    async def fetch_thread_messages(self, channel_id: int, thread_id: int) -> List[Dict]:
        """Fetch messages from a Discord thread"""
        # This would use discord.py to fetch actual messages
        # For now, returning mock structure
        # In production: use self.client to fetch from Discord API
        return []
    
    def extract_key_topics(self, messages: List[Dict]) -> List[str]:
        """Extract key topics from thread (placeholder)"""
        # Would use NLP techniques like TF-IDF or keyword extraction
        # For now return placeholder
        return ['governance', 'proposal', 'voting']

if __name__ == "__main__":
    analyzer = DiscordAnalyzer()
    
    # Test with mock messages
    mock_messages = [
        {'content': 'This proposal looks great! I fully support it.'},
        {'content': 'I have some concerns about the implementation.'},
        {'content': 'The budget seems reasonable to me.'},
        {'content': 'Strongly against this, too risky!'},
        {'content': 'Good idea overall but needs more details.'}
    ]
    
    result = analyzer.analyze_thread(mock_messages)
    print("Thread Analysis:")
    print(f"  Total messages: {result['total_messages']}")
    print(f"  Positive: {result['positive_count']} ({result['positive_ratio']:.1%})")
    print(f"  Negative: {result['negative_count']} ({result['negative_ratio']:.1%})")
    print(f"  Overall sentiment: {result['overall_sentiment']}")
    print(f"  Average score: {result['avg_sentiment']:.3f}")
