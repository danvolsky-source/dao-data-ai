# Multi-DAO Data Collection

## Overview
This directory contains scripts for collecting DAO governance data from multiple sources for ML model training. Supports Arbitrum, Optimism, Uniswap, and Aave DAOs.

## Supported DAOs

| DAO | Snapshot Space | Governor Contract | Network |
|-----|----------------|-------------------|---------|
| **Arbitrum** | arbitrumfoundation.eth | 0xf07DeD9dC292157749B6Fd268E37DF6EA38395B9 | Arbitrum One |
| **Optimism** | optimism.eth | 0xcDF27F107725988f2261Ce2256bDfCdE8B382B10 | Optimism |
| **Uniswap** | uniswap.eth | 0x5e4be8Bc9637f0EAA1A755019e06A68ce081D58F | Ethereum |
| **Aave** | aave.eth | 0xEC568fffba86c094cf06b22134B23074DFE2252c | Ethereum |

## Data Sources

### 1. Forum Data
- **Source**: DAO governance forums (Discourse/various platforms)
- **Data**: Proposal discussions, comments, voting threads
- **Collection Method**: Web scraping + Forum APIs
- **Key Metrics**:
  - Thread activity (views, replies, participants)
  - Sentiment analysis of comments
  - Author reputation and participation patterns
  - Discussion timeline relative to voting

### 2. Snapshot Data
- **Source**: Snapshot GraphQL API
- **Data**: Off-chain voting records, proposal metadata, voter addresses
- **Collection Method**: GraphQL queries
- **Supported Spaces**: arbitrumfoundation.eth, optimism.eth, uniswap.eth, aave.eth
- **Key Metrics**:
  - Vote outcomes (For/Against/Abstain)
  - Voting power distribution
  - Voter participation rate
  - Proposal status and timing

### 3. On-Chain Data
- **Source**: Blockchain via RPC endpoints
- **Data**: On-chain proposal execution, governance transactions
- **Collection Method**: Web3.py + Governor contract events
- **Supported Networks**: Arbitrum One, Optimism, Ethereum Mainnet
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

### Quick Start - Multi-DAO Collector

Collect data from all DAOs at once:
```bash
# Install dependencies
cd data_collection
pip install -r requirements.txt

# Collect all data from all DAOs (Snapshot + On-chain)
python collectors/multi_dao_collector.py --dao all --type all

# Collect only Snapshot data from all DAOs
python collectors/multi_dao_collector.py --dao all --type snapshot

# Collect data from a specific DAO
python collectors/multi_dao_collector.py --dao optimism --type all
python collectors/multi_dao_collector.py --dao uniswap --type snapshot
python collectors/multi_dao_collector.py --dao aave --type onchain
```

### Individual DAO Collectors

#### Arbitrum
```bash
# Snapshot data
python collectors/snapshot_collector.py

# On-chain data
python collectors/onchain_collector.py

# Forum data
python scrapers/forum_scraper.py
```

#### Optimism
```bash
# Snapshot data
python collectors/optimism_collector.py

# On-chain data
python collectors/optimism_onchain_collector.py
```

#### Uniswap
```bash
# Snapshot data
python collectors/uniswap_collector.py

# On-chain data
python collectors/uniswap_onchain_collector.py
```

#### Aave
```bash
# Snapshot data
python collectors/aave_collector.py

# On-chain data
python collectors/aave_onchain_collector.py
```

## Environment Variables

Create a `.env` file in the `data_collection` directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here

# RPC Endpoints
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
OPTIMISM_RPC_URL=https://mainnet.optimism.io
ETHEREUM_RPC_URL=https://eth.llamarpc.com

# Optional: Custom RPC endpoints for better rate limits
# ARBITRUM_RPC_URL=https://arbitrum-mainnet.infura.io/v3/YOUR_KEY
# OPTIMISM_RPC_URL=https://optimism-mainnet.infura.io/v3/YOUR_KEY
# ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
```

## Database Schema

See `schema.sql` for complete table definitions.

## Notes
- Rate limiting: Respect API limits (Snapshot: 1 req/sec, Discourse: 60 req/min)
- Data freshness: Run collectors daily via cron job
- Historical data: Backfill from DAO launch dates
  - Arbitrum DAO: March 2023
  - Optimism Collective: 2022
  - Uniswap DAO: 2020
  - Aave DAO: 2020
- RPC rate limits: Free public RPCs have rate limits; consider using Infura, Alchemy, or QuickNode for production

## Collector Files

### Snapshot Collectors
- `collectors/snapshot_collector.py` - Arbitrum DAO
- `collectors/optimism_collector.py` - Optimism Collective
- `collectors/uniswap_collector.py` - Uniswap DAO
- `collectors/aave_collector.py` - Aave DAO

### On-Chain Collectors
- `collectors/onchain_collector.py` - Arbitrum DAO
- `collectors/optimism_onchain_collector.py` - Optimism Collective
- `collectors/uniswap_onchain_collector.py` - Uniswap DAO
- `collectors/aave_onchain_collector.py` - Aave DAO

### Forum Scrapers
- `scrapers/forum_scraper.py` - Arbitrum governance forum

### Unified Collector
- `collectors/multi_dao_collector.py` - Multi-DAO data collection script
