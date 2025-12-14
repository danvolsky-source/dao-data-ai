# Arbitrum DAO Data Collection

## Overview
This directory contains scripts for collecting Arbitrum DAO governance data from multiple sources for ML model training.

## Data Sources

### 1. Forum Data (governance.arbitrum.foundation)
- **Source**: Discourse forum
- **Data**: Proposal discussions, comments, voting threads
- **Collection Method**: Web scraping + Discourse API
- **Key Metrics**:
  - Thread activity (views, replies, participants)
  - Sentiment analysis of comments
  - Author reputation and participation patterns
  - Discussion timeline relative to voting

### 2. Snapshot Data (snapshot.org/#/arbitrumfoundation.eth)
- **Source**: Snapshot GraphQL API
- **Data**: Voting records, proposal metadata, voter addresses
- **Collection Method**: GraphQL queries
- **Key Metrics**:
  - Vote outcomes (For/Against/Abstain)
  - Voting power distribution
  - Voter participation rate
  - Proposal status and timing

### 3. On-Chain Data (Arbitrum Governance Contracts)
- **Source**: Arbitrum blockchain via RPC
- **Data**: On-chain proposal execution, governance transactions
- **Collection Method**: Web3.py + Etherscan API
- **Key Metrics**:
  - Execution status
  - Gas costs
  - Transaction timing
  - Smart contract interactions

## Data Pipeline

```
Forum Scraper → Raw Text Data
                      ↓
                Preprocessing
                      ↓
Snapshot API → Structured Vote Data → Feature Engineering → ML Training Dataset
                      ↓
                  Supabase
                      ↓
On-Chain RPC → Execution Data
```

## Implementation Phases

### Phase 1: Forum Scraper (Priority)
- Scrape proposal threads from governance.arbitrum.foundation
- Extract: title, body, comments, timestamps, authors
- Store in Supabase `forum_threads` table

### Phase 2: Snapshot Collector
- Query Snapshot GraphQL for arbitrumfoundation.eth space
- Extract: proposals, votes, scores
- Store in Supabase `snapshot_proposals` and `snapshot_votes` tables

### Phase 3: On-Chain Collector
- Connect to Arbitrum RPC
- Track proposal execution events
- Store in Supabase `onchain_executions` table

### Phase 4: Data Integration
- Link forum → snapshot → on-chain via proposal IDs
- Build unified dataset for ML training

## Usage

```bash
# Install dependencies
cd data_collection
pip install -r requirements.txt

# Run forum scraper
python scrapers/forum_scraper.py

# Run snapshot collector
python collectors/snapshot_collector.py

# Run on-chain collector
python collectors/onchain_collector.py
```

## Database Schema

See `schema.sql` for complete table definitions.

## Notes
- Rate limiting: Respect API limits (Snapshot: 1 req/sec, Discourse: 60 req/min)
- Data freshness: Run collectors daily via cron job
- Historical data: Backfill from genesis (Arbitrum DAO launch: March 2023)
