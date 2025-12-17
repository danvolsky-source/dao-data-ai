-- Migration: create twitter_sentiment table
CREATE TABLE IF NOT EXISTS twitter_sentiment (
    id BIGSERIAL PRIMARY KEY,
    proposal_id VARCHAR(255),
    hashtag VARCHAR(255),
    avg_sentiment FLOAT,
    std_sentiment FLOAT,
    positive_ratio FLOAT,
    negative_ratio FLOAT,
    neutral_ratio FLOAT,
    total_tweets INT,
    total_engagement INT,
    avg_engagement_per_tweet FLOAT,
    influential_accounts JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(proposal_id, hashtag)
);
