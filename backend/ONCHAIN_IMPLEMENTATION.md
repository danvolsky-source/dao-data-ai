# On-Chain Data Implementation Plan

## Priority Tasks from Gap Analysis

Based on the gap analysis, here are the critical missing components:

### 1. ❌ On-Chain Data Parser (CRITICAL)

**Status**: Currently absent
**Priority**: P0 (Highest)
**Effort**: 2-3 days

#### Requirements:
- Parse Arbitrum DAO smart contracts
- Fetch on-chain voting data
- Track proposal lifecycle events
- Monitor delegate voting power

#### Implementation Steps:

**A. Web3 Integration**
```python
# backend/data_collectors/onchain_collector.py
- ArbitrumDAOCollector class
- Web3.py integration
- Governor contract ABI
- Event listeners (ProposalCreated, VoteCast)
```

**B. Key Functions**:
- `fetch_proposal_data(proposal_id)` - Get proposal state & votes
- `fetch_recent_proposals()` - Scan blockchain for new proposals
- `fetch_votes_for_proposal()` - Get all votes for a proposal
- `get_delegate_voting_power()` - Track delegate power
- `sync_all_proposals()` - Full blockchain sync

**C. Snapshot.org Integration**
- GraphQL API client
- Fetch off-chain votes
- Combine with on-chain data

#### Dependencies:
```bash
web3==6.11.3
eth-abi==4.2.1
eth-utils==2.3.1
```

### 2. ⚠️  Discord Thread Analysis (PARTIAL)

**Status**: Mentioned but not implemented
**Priority**: P1 (High)
**Effort**: 2-3 days

#### Requirements:
- Parse Discord discussion threads
- Extract sentiment from messages
- Link discussions to proposals
- Track community engagement

#### Implementation:
```python
# backend/analyzers/discord_analyzer.py
class DiscordAnalyzer:
    - fetch_threads_for_proposal()
    - analyze_thread_sentiment()
    - extract_key_topics()
    - calculate_engagement_score()
```

#### Dependencies:
```bash
discord.py==2.3.2
transformers==4.35.2  # For sentiment
```

### 3. ❌ ML Prediction Model (NOT FUNCTIONAL)

**Status**: Stub exists, no actual functionality
**Priority**: P0 (Highest)
**Effort**: 3-4 days

#### Current Issues:
- RandomForest model is placeholder
- No training data pipeline
- No feature engineering
- No model persistence

#### Implementation:
```python
# backend/ml_service/predictor.py
class ProposalPredictor:
    - load_training_data()
    - engineer_features()
    - train_model()
    - predict_outcome()
    - save_model()
```

#### Features to Extract:
1. **On-chain**:
   - Current vote ratio
   - Voting participation rate
   - Delegate concentration
   - Proposal history

2. **Off-chain**:
   - Discussion sentiment
   - Engagement metrics
   - Author reputation

3. **Historical**:
   - Similar proposal outcomes
   - Seasonal voting patterns

### 4. ❌ Alert System

**Status**: Absent
**Priority**: P1 (High)
**Effort**: 1-2 days

#### Requirements:
- Threshold-based alerts
- Real-time monitoring
- Multi-channel delivery (email, webhook)

#### Implementation:
```python
# backend/alerts/alert_manager.py
class AlertManager:
    - check_threshold(proposal, threshold=0.7)
    - send_alert(channel, message)
    - track_alert_history()
```

### 5. ❌ Scoring System

**Status**: Absent
**Priority**: P1 (High)
**Effort**: 2-3 days

#### Requirements:
- Risk scoring
- Tokenomics impact analysis
- Delegate scoring

#### Implementation:
```python
# backend/scoring/proposal_scorer.py
class ProposalScorer:
    - calculate_risk_score()
    - assess_tokenomics_impact()
    - generate_recommendation()
```

### 6. ⚠️  Dashboard Enhancement

**Status**: Partial - table exists, no predictions/sentiment
**Priority**: P2 (Medium)
**Effort**: 1-2 days

#### Missing Features:
- ML predictions display
- Sentiment indicators
- Risk scores
- Alert status

## Implementation Roadmap

### Week 1: Critical Foundation
- Day 1-3: On-chain parser (Web3 integration)
- Day 4-5: ML model (basic prediction)

### Week 2: Data Collection
- Day 1-2: Discord analyzer
- Day 3-4: Sentiment analysis
- Day 5: Data pipeline integration

### Week 3: Intelligence Features
- Day 1-2: Alert system
- Day 3-4: Scoring system
- Day 5: Dashboard integration

### Week 4: Testing & Refinement
- Integration testing
- Performance optimization
- Documentation

## Technical Architecture

```
┌─────────────────────┐
│  Data Collection    │
├─────────────────────┤
│ • Web3 (On-chain)   │
│ • Snapshot API      │
│ • Discord API       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Processing    │
├─────────────────────┤
│ • Sentiment Analyzer│
│ • Feature Engineer  │
│ • Data Cleaner      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ML & Scoring       │
├─────────────────────┤
│ • Prediction Model  │
│ • Risk Scorer       │
│ • Alert Manager     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  API & Dashboard    │
├─────────────────────┤
│ • FastAPI Endpoints │
│ • Next.js Frontend  │
│ • Real-time Updates │
└─────────────────────┘
```

## Environment Variables

Add to `.env`:
```bash
# Blockchain
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
GOVERNOR_CONTRACT=0xf07DeD9dC292157749B6Fd268E37DF6EA38395B9

# Discord
DISCORD_TOKEN=your_token_here
DISCORD_GUILD_ID=your_guild_id

# ML Models
OPENAI_API_KEY=your_key_here  # For sentiment
HUGGINGFACE_TOKEN=your_token_here

# Alerts
ALERT_EMAIL=alerts@example.com
ALERT_WEBHOOK_URL=https://your-webhook.url
```

## Next Steps

1. **Immediate**: Implement on-chain collector
2. **This Week**: Add ML prediction model
3. **Next Week**: Discord analyzer + sentiment
4. **Following**: Alert system + scoring

## Success Metrics

- [ ] Can fetch all Arbitrum DAO proposals from blockchain
- [ ] Can analyze Discord threads for sentiment
- [ ] ML model predicts with >70% accuracy
- [ ] Alerts trigger within 5 minutes of threshold
- [ ] Scoring system provides actionable insights
- [ ] Dashboard shows real-time predictions
