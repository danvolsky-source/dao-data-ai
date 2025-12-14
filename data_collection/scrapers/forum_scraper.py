#!/usr/bin/env python3
"""
Forum Scraper for Arbitrum Governance
Scrapes proposal discussions from governance.arbitrum.foundation (Discourse)
"""

import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Configuration
FORUM_BASE_URL = "https://governance.arbitrum.foundation"
DISCOURSE_API_BASE = f"{FORUM_BASE_URL}"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_latest_topics(category_id: Optional[int] = None, limit: int = 30) -> List[Dict]:
    """
    Fetch latest topics from Discourse forum using API
    """
    url = f"{DISCOURSE_API_BASE}/latest.json"
    params = {}
    if category_id:
        params['category'] = category_id
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        topics = data.get('topic_list', {}).get('topics', [])
        return topics[:limit]
    except Exception as e:
        print(f"Error fetching topics: {e}")
        return []

def fetch_topic_details(topic_id: int) -> Optional[Dict]:
    """
    Fetch detailed information about a specific topic
    """
    url = f"{DISCOURSE_API_BASE}/t/{topic_id}.json"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching topic {topic_id}: {e}")
        return None

def fetch_topic_posts(topic_id: int) -> List[Dict]:
    """
    Fetch all posts in a topic
    """
    url = f"{DISCOURSE_API_BASE}/t/{topic_id}/posts.json"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('post_stream', {}).get('posts', [])
    except Exception as e:
        print(f"Error fetching posts for topic {topic_id}: {e}")
        return []

def store_forum_thread(topic: Dict, details: Dict) -> bool:
    """
    Store forum thread in Supabase
    """
    try:
        # Extract proposal ID from title or content if available
        proposal_id = None
        title = topic.get('title', '')
        # Look for proposal patterns like "AIP-123" or "Proposal #456"
        import re
        proposal_match = re.search(r'(AIP[- ]?\d+|Proposal[- ]?#?\d+)', title, re.IGNORECASE)
        if proposal_match:
            proposal_id = proposal_match.group(0)
        
        data = {
            "thread_id": str(topic['id']),
            "title": title,
            "url": f"{FORUM_BASE_URL}/t/{topic['slug']}/{topic['id']}",
            "author": details.get('post_stream', {}).get('posts', [{}])[0].get('username'),
            "category": topic.get('category_id'),
            "created_at": topic.get('created_at'),
            "updated_at": topic.get('last_posted_at'),
            "views": topic.get('views', 0),
            "replies": topic.get('posts_count', 0) - 1,  # Subtract original post
            "likes": topic.get('like_count', 0),
            "participants": len(details.get('details', {}).get('participants', [])),
            "body": details.get('post_stream', {}).get('posts', [{}])[0].get('cooked'),
            "tags": topic.get('tags', []),
            "status": 'active' if not topic.get('closed') else 'closed',
            "proposal_id": proposal_id
        }
        
        result = supabase.table("forum_threads").upsert(data).execute()
        return True
    except Exception as e:
        print(f"Error storing thread {topic['id']}: {e}")
        return False

def store_forum_post(post: Dict, topic_id: int) -> bool:
    """
    Store forum post in Supabase
    """
    try:
        data = {
            "post_id": str(post['id']),
            "thread_id": str(topic_id),
            "author": post.get('username'),
            "body": post.get('cooked'),
            "created_at": post.get('created_at'),
            "likes": post.get('score', 0),
            "reply_to_post_id": str(post['reply_to_post_number']) if post.get('reply_to_post_number') else None
        }
        
        result = supabase.table("forum_posts").upsert(data).execute()
        return True
    except Exception as e:
        print(f"Error storing post {post['id']}: {e}")
        return False

def scrape_governance_forum():
    """
    Main scraping function for Arbitrum governance forum
    """
    print("=" * 60)
    print("Arbitrum Governance Forum Scraper")
    print("=" * 60)
    
    # Fetch latest topics
    print("\nFetching latest governance topics...")
    topics = fetch_latest_topics(limit=50)
    print(f"Found {len(topics)} topics")
    
    total_threads = 0
    total_posts = 0
    
    for topic in topics:
        topic_id = topic['id']
        print(f"\nProcessing topic {topic_id}: {topic['title'][:60]}...")
        
        # Fetch detailed information
        details = fetch_topic_details(topic_id)
        if not details:
            continue
        
        # Store thread
        if store_forum_thread(topic, details):
            total_threads += 1
            print(f"  ✓ Stored thread")
        
        # Fetch and store posts
        posts = fetch_topic_posts(topic_id)
        for post in posts:
            if store_forum_post(post, topic_id):
                total_posts += 1
        
        print(f"  ✓ Stored {len(posts)} posts")
        
        # Rate limiting: respect Discourse API limits (60 requests/min)
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Scraping complete!")
    print(f"Threads collected: {total_threads}")
    print(f"Posts collected: {total_posts}")
    print("=" * 60)

if __name__ == "__main__":
    scrape_governance_forum()
