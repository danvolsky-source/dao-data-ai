"""
Discord Sentiment Analyzer
Analyzes sentiment from Discord messages using NLP
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from supabase import Client


class DiscordSentimentAnalyzer:
    """
    Analyzes sentiment from Discord messages related to DAO proposals.
    
    Uses both TextBlob and VADER for more accurate sentiment analysis.
    TextBlob: General purpose sentiment analysis
    VADER: Better for social media/informal text
    """
    
    def __init__(self, supabase_client: Client, discord_token: Optional[str] = None):
        """
        Initialize Discord sentiment analyzer
        
        Args:
            supabase_client: Supabase client for data storage
            discord_token: Optional Discord bot token (for live monitoring)
        """
        self.supabase = supabase_client
        self.discord_token = discord_token
        self.vader = SentimentIntensityAnalyzer()
        
    def _analyze_with_textblob(self, text: str) -> float:
        """
        Analyze sentiment using TextBlob
        
        Args:
            text: Text to analyze
            
        Returns:
            Polarity score (-1 to 1)
        """
        try:
            analysis = TextBlob(text)
            return analysis.sentiment.polarity
        except Exception as e:
            print(f"TextBlob analysis error: {e}")
            return 0.0
    
    def _analyze_with_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using VADER
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with compound, positive, negative, neutral scores
        """
        try:
            scores = self.vader.polarity_scores(text)
            return scores
        except Exception as e:
            print(f"VADER analysis error: {e}")
            return {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 0.0}
    
    def _combine_sentiment_scores(self, textblob_score: float, vader_compound: float) -> float:
        """
        Combine TextBlob and VADER scores for more accurate result
        
        Args:
            textblob_score: TextBlob polarity (-1 to 1)
            vader_compound: VADER compound score (-1 to 1)
            
        Returns:
            Combined sentiment score (-1 to 1)
        """
        # Weight VADER more heavily for social media text
        return (textblob_score * 0.3) + (vader_compound * 0.7)
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single message
        
        Args:
            message: Message text to analyze
            
        Returns:
            Dict with sentiment analysis results
        """
        # Get scores from both analyzers
        textblob_score = self._analyze_with_textblob(message)
        vader_scores = self._analyze_with_vader(message)
        
        # Combine scores
        combined_score = self._combine_sentiment_scores(
            textblob_score,
            vader_scores["compound"]
        )
        
        # Classify sentiment
        if combined_score > 0.1:
            classification = "positive"
        elif combined_score < -0.1:
            classification = "negative"
        else:
            classification = "neutral"
        
        return {
            "sentiment_score": combined_score,
            "classification": classification,
            "textblob_score": textblob_score,
            "vader_compound": vader_scores["compound"],
            "vader_positive": vader_scores["pos"],
            "vader_negative": vader_scores["neg"],
            "vader_neutral": vader_scores["neu"]
        }
    
    def analyze_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment of multiple messages
        
        Args:
            messages: List of message dicts with 'content', 'author', 'timestamp'
            
        Returns:
            Aggregated sentiment analysis
        """
        if not messages:
            return {
                "sentiment_score": 0.0,
                "message_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "messages": []
            }
        
        analyzed_messages = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_score = 0.0
        
        for msg in messages:
            content = msg.get("content", "")
            
            # Skip empty or very short messages
            if len(content.strip()) < 3:
                continue
            
            # Analyze message
            analysis = self.analyze_message(content)
            
            # Count classifications
            if analysis["classification"] == "positive":
                positive_count += 1
            elif analysis["classification"] == "negative":
                negative_count += 1
            else:
                neutral_count += 1
            
            total_score += analysis["sentiment_score"]
            
            # Store analyzed message
            analyzed_messages.append({
                "content": content[:200],  # First 200 chars only
                "author": msg.get("author", "unknown"),
                "timestamp": msg.get("timestamp"),
                "sentiment_score": analysis["sentiment_score"],
                "classification": analysis["classification"]
            })
        
        message_count = len(analyzed_messages)
        avg_sentiment = total_score / message_count if message_count > 0 else 0.0
        
        return {
            "sentiment_score": round(avg_sentiment, 4),
            "message_count": message_count,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_ratio": round(positive_count / message_count, 4) if message_count > 0 else 0,
            "negative_ratio": round(negative_count / message_count, 4) if message_count > 0 else 0,
            "neutral_ratio": round(neutral_count / message_count, 4) if message_count > 0 else 0,
            "messages": analyzed_messages
        }
    
    async def analyze_proposal_discussion(
        self,
        proposal_id: str,
        channel_id: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze Discord discussion for a specific proposal
        
        Args:
            proposal_id: Proposal identifier to search for
            channel_id: Optional specific channel ID
            limit: Maximum number of messages to analyze
            
        Returns:
            Sentiment analysis results
        """
        # In production, this would fetch messages from Discord API
        # For now, return mock data structure
        
        # TODO: Implement actual Discord API integration
        # This requires:
        # 1. Discord bot token
        # 2. Discord.py library
        # 3. Permission to read messages
        # 4. Channel IDs where proposals are discussed
        
        print(f"Analyzing Discord sentiment for proposal: {proposal_id}")
        print("Note: Live Discord integration requires Discord bot token and permissions")
        
        # For now, return empty structure
        return {
            "proposal_id": proposal_id,
            "source": "discord",
            "sentiment_score": 0.0,
            "message_count": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "channel_id": channel_id,
            "analyzed_at": datetime.utcnow().isoformat(),
            "note": "Live Discord integration pending bot setup"
        }
    
    async def save_sentiment_analysis(
        self,
        proposal_id: str,
        sentiment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save sentiment analysis to database
        
        Args:
            proposal_id: Proposal identifier
            sentiment_data: Sentiment analysis results
            
        Returns:
            Saved record
        """
        try:
            data = {
                "proposal_id": proposal_id,
                "source": "discord",
                "sentiment_score": sentiment_data.get("sentiment_score", 0),
                "message_count": sentiment_data.get("message_count", 0),
                "positive_count": sentiment_data.get("positive_count", 0),
                "negative_count": sentiment_data.get("negative_count", 0),
                "neutral_count": sentiment_data.get("neutral_count", 0),
                "analyzed_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "positive_ratio": sentiment_data.get("positive_ratio", 0),
                    "negative_ratio": sentiment_data.get("negative_ratio", 0),
                    "neutral_ratio": sentiment_data.get("neutral_ratio", 0),
                    "channel_id": sentiment_data.get("channel_id"),
                    "sample_messages": sentiment_data.get("messages", [])[:5]  # Save only 5 examples
                }
            }
            
            response = self.supabase.table("sentiment_analysis").insert(data).execute()
            
            return {
                "status": "success",
                "data": response.data[0] if response.data else data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def analyze_and_save(
        self,
        proposal_id: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        channel_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment and save to database in one call
        
        Args:
            proposal_id: Proposal identifier
            messages: Optional list of messages to analyze
            channel_id: Optional Discord channel ID
            
        Returns:
            Analysis results with save status
        """
        # If messages provided, analyze them directly
        if messages:
            sentiment_data = self.analyze_messages(messages)
            sentiment_data["proposal_id"] = proposal_id
            sentiment_data["channel_id"] = channel_id
        else:
            # Otherwise, try to fetch from Discord (requires bot)
            sentiment_data = await self.analyze_proposal_discussion(
                proposal_id=proposal_id,
                channel_id=channel_id
            )
        
        # Save to database
        save_result = await self.save_sentiment_analysis(proposal_id, sentiment_data)
        
        return {
            "sentiment_analysis": sentiment_data,
            "save_result": save_result
        }


# Example usage and testing functions
async def example_usage():
    """Example of how to use DiscordSentimentAnalyzer"""
    from supabase import create_client
    import os
    
    # Initialize
    supabase = create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_KEY", "")
    )
    
    analyzer = DiscordSentimentAnalyzer(supabase)
    
    # Example messages
    messages = [
        {"content": "This proposal is great! I love the idea.", "author": "user1", "timestamp": "2025-12-18T00:00:00Z"},
        {"content": "I'm not sure about this. Seems risky.", "author": "user2", "timestamp": "2025-12-18T00:01:00Z"},
        {"content": "Strong support! This will help the DAO.", "author": "user3", "timestamp": "2025-12-18T00:02:00Z"},
        {"content": "Bad idea, waste of treasury funds.", "author": "user4", "timestamp": "2025-12-18T00:03:00Z"},
        {"content": "Neutral on this one.", "author": "user5", "timestamp": "2025-12-18T00:04:00Z"}
    ]
    
    # Analyze
    result = await analyzer.analyze_and_save("prop_001", messages)
    
    print("Sentiment Analysis Result:")
    print(f"Score: {result['sentiment_analysis']['sentiment_score']}")
    print(f"Positive: {result['sentiment_analysis']['positive_count']}")
    print(f"Negative: {result['sentiment_analysis']['negative_count']}")
    print(f"Neutral: {result['sentiment_analysis']['neutral_count']}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
