"""
Forum Sentiment Analyzer
Analyzes sentiment from forum discussions (Discourse, Snapshot forums, etc.)
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from supabase import Client
import re


class ForumSentimentAnalyzer:
    """
    Analyzes sentiment from forum discussions related to DAO proposals.
    
    Works with:
    - Discourse forums
    - Snapshot discussion threads
    - Custom DAO forums
    
    Uses both TextBlob and VADER for robust sentiment analysis.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize forum sentiment analyzer
        
        Args:
            supabase_client: Supabase client for data storage
        """
        self.supabase = supabase_client
        self.vader = SentimentIntensityAnalyzer()
    
    def _clean_text(self, text: str) -> str:
        """
        Clean forum post text for analysis
        
        Args:
            text: Raw forum post text
            
        Returns:
            Cleaned text
        """
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'[*_~`]', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove quotes (they're usually previous messages)
        text = re.sub(r'>\s.*?\n', '', text)
        
        return text.strip()
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using both TextBlob and VADER
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment analysis results
        """
        # Clean text
        cleaned_text = self._clean_text(text)
        
        if len(cleaned_text) < 3:
            return {
                "sentiment_score": 0.0,
                "classification": "neutral",
                "confidence": 0.0
            }
        
        # TextBlob analysis
        try:
            textblob_analysis = TextBlob(cleaned_text)
            textblob_score = textblob_analysis.sentiment.polarity
        except:
            textblob_score = 0.0
        
        # VADER analysis
        try:
            vader_scores = self.vader.polarity_scores(cleaned_text)
            vader_compound = vader_scores["compound"]
        except:
            vader_compound = 0.0
        
        # Combine scores (weight VADER more for informal text)
        combined_score = (textblob_score * 0.4) + (vader_compound * 0.6)
        
        # Classify sentiment
        if combined_score > 0.15:
            classification = "positive"
        elif combined_score < -0.15:
            classification = "negative"
        else:
            classification = "neutral"
        
        # Calculate confidence based on score magnitude
        confidence = min(abs(combined_score) * 2, 1.0)
        
        return {
            "sentiment_score": combined_score,
            "classification": classification,
            "confidence": confidence,
            "textblob_score": textblob_score,
            "vader_compound": vader_compound
        }
    
    def analyze_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment of a single forum post
        
        Args:
            post: Dict with 'content', 'author', 'created_at'
            
        Returns:
            Post with sentiment analysis added
        """
        content = post.get("content", "")
        analysis = self._analyze_sentiment(content)
        
        return {
            "post_id": post.get("id"),
            "author": post.get("author"),
            "created_at": post.get("created_at"),
            "content_preview": content[:150],
            "sentiment_score": analysis["sentiment_score"],
            "classification": analysis["classification"],
            "confidence": analysis["confidence"]
        }
    
    def analyze_thread(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment of an entire forum thread
        
        Args:
            posts: List of forum posts
            
        Returns:
            Aggregated sentiment analysis
        """
        if not posts:
            return {
                "sentiment_score": 0.0,
                "message_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            }
        
        analyzed_posts = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_score = 0.0
        total_confidence = 0.0
        
        for post in posts:
            analysis = self.analyze_post(post)
            
            # Count classifications
            if analysis["classification"] == "positive":
                positive_count += 1
            elif analysis["classification"] == "negative":
                negative_count += 1
            else:
                neutral_count += 1
            
            total_score += analysis["sentiment_score"]
            total_confidence += analysis["confidence"]
            analyzed_posts.append(analysis)
        
        message_count = len(analyzed_posts)
        avg_sentiment = total_score / message_count if message_count > 0 else 0.0
        avg_confidence = total_confidence / message_count if message_count > 0 else 0.0
        
        # Get unique authors
        unique_authors = len(set(post.get("author") for post in posts if post.get("author")))
        
        return {
            "sentiment_score": round(avg_sentiment, 4),
            "average_confidence": round(avg_confidence, 4),
            "message_count": message_count,
            "unique_authors": unique_authors,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_ratio": round(positive_count / message_count, 4) if message_count > 0 else 0,
            "negative_ratio": round(negative_count / message_count, 4) if message_count > 0 else 0,
            "neutral_ratio": round(neutral_count / message_count, 4) if message_count > 0 else 0,
            "analyzed_posts": analyzed_posts
        }
    
    async def fetch_forum_posts(
        self,
        proposal_id: str,
        thread_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch forum posts from database
        
        Args:
            proposal_id: Proposal identifier
            thread_id: Optional specific thread ID
            
        Returns:
            List of forum posts
        """
        try:
            # Try to fetch from forum_posts table
            query = self.supabase.table("forum_posts").select("*")
            
            if thread_id:
                query = query.eq("thread_id", thread_id)
            
            response = query.execute()
            
            if response.data:
                return [
                    {
                        "id": post.get("post_id"),
                        "content": post.get("body", ""),
                        "author": post.get("author", "anonymous"),
                        "created_at": post.get("created_at")
                    }
                    for post in response.data
                ]
            
            # If no posts found, try forum_threads table
            thread_query = self.supabase.table("forum_threads").select("*")
            
            if proposal_id:
                thread_query = thread_query.eq("proposal_id", proposal_id)
            
            thread_response = thread_query.execute()
            
            if thread_response.data:
                # Create a pseudo-post from thread body
                return [
                    {
                        "id": thread.get("thread_id"),
                        "content": thread.get("body", thread.get("title", "")),
                        "author": thread.get("author", "anonymous"),
                        "created_at": thread.get("created_at")
                    }
                    for thread in thread_response.data
                ]
            
            return []
            
        except Exception as e:
            print(f"Error fetching forum posts: {e}")
            return []
    
    async def analyze_proposal_discussion(
        self,
        proposal_id: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze forum discussion for a specific proposal
        
        Args:
            proposal_id: Proposal identifier
            thread_id: Optional specific thread ID
            
        Returns:
            Sentiment analysis results
        """
        # Fetch posts from database
        posts = await self.fetch_forum_posts(proposal_id, thread_id)
        
        if not posts:
            return {
                "proposal_id": proposal_id,
                "source": "forum",
                "sentiment_score": 0.0,
                "message_count": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "analyzed_at": datetime.utcnow().isoformat(),
                "note": "No forum posts found for this proposal"
            }
        
        # Analyze thread
        analysis = self.analyze_thread(posts)
        
        return {
            "proposal_id": proposal_id,
            "thread_id": thread_id,
            "source": "forum",
            "sentiment_score": analysis["sentiment_score"],
            "average_confidence": analysis["average_confidence"],
            "message_count": analysis["message_count"],
            "unique_authors": analysis["unique_authors"],
            "positive_count": analysis["positive_count"],
            "negative_count": analysis["negative_count"],
            "neutral_count": analysis["neutral_count"],
            "positive_ratio": analysis["positive_ratio"],
            "negative_ratio": analysis["negative_ratio"],
            "neutral_ratio": analysis["neutral_ratio"],
            "analyzed_at": datetime.utcnow().isoformat(),
            "sample_posts": analysis["analyzed_posts"][:5]  # First 5 posts as examples
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
                "source": "forum",
                "sentiment_score": sentiment_data.get("sentiment_score", 0),
                "message_count": sentiment_data.get("message_count", 0),
                "positive_count": sentiment_data.get("positive_count", 0),
                "negative_count": sentiment_data.get("negative_count", 0),
                "neutral_count": sentiment_data.get("neutral_count", 0),
                "analyzed_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "thread_id": sentiment_data.get("thread_id"),
                    "unique_authors": sentiment_data.get("unique_authors", 0),
                    "average_confidence": sentiment_data.get("average_confidence", 0),
                    "positive_ratio": sentiment_data.get("positive_ratio", 0),
                    "negative_ratio": sentiment_data.get("negative_ratio", 0),
                    "neutral_ratio": sentiment_data.get("neutral_ratio", 0),
                    "sample_posts": sentiment_data.get("sample_posts", [])
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
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze forum sentiment and save to database in one call
        
        Args:
            proposal_id: Proposal identifier
            thread_id: Optional specific thread ID
            
        Returns:
            Analysis results with save status
        """
        # Analyze
        sentiment_data = await self.analyze_proposal_discussion(
            proposal_id=proposal_id,
            thread_id=thread_id
        )
        
        # Save to database
        save_result = await self.save_sentiment_analysis(proposal_id, sentiment_data)
        
        return {
            "sentiment_analysis": sentiment_data,
            "save_result": save_result
        }


# Example usage
async def example_usage():
    """Example of how to use ForumSentimentAnalyzer"""
    from supabase import create_client
    import os
    
    # Initialize
    supabase = create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_KEY", "")
    )
    
    analyzer = ForumSentimentAnalyzer(supabase)
    
    # Analyze proposal
    result = await analyzer.analyze_and_save("prop_001")
    
    print("Forum Sentiment Analysis:")
    print(f"Score: {result['sentiment_analysis']['sentiment_score']}")
    print(f"Messages: {result['sentiment_analysis']['message_count']}")
    print(f"Positive: {result['sentiment_analysis']['positive_count']}")
    print(f"Negative: {result['sentiment_analysis']['negative_count']}")


if __name__ == "__main__":
    asyncio.run(example_usage())
