-- Arbitrum DAO Data Collection Schema
-- Supabase PostgreSQL Database

-- Forum Threads Table
CREATE TABLE IF NOT EXISTS forum_threads (
  id BIGSERIAL PRIMARY KEY,
  thread_id TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  author TEXT,
  category TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE,
  views INTEGER DEFAULT 0,
  replies INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  participants INTEGER DEFAULT 0,
  body TEXT,
  tags TEXT[],
  status TEXT, -- 'active', 'archived', 'closed'
  proposal_id TEXT, -- Links to snapshot_proposals
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Forum Posts Table (Comments)
CREATE TABLE IF NOT EXISTS forum_posts (
  id BIGSERIAL PRIMARY KEY,
  post_id TEXT UNIQUE NOT NULL,
  thread_id TEXT REFERENCES forum_threads(thread_id),
  author TEXT,
  body TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  likes INTEGER DEFAULT 0,
  reply_to_post_id TEXT, -- For nested replies
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Snapshot Proposals Table
CREATE TABLE IF NOT EXISTS snapshot_proposals (
  id BIGSERIAL PRIMARY KEY,
  proposal_id TEXT UNIQUE NOT NULL,
  space TEXT NOT NULL DEFAULT 'arbitrumfoundation.eth',
  title TEXT NOT NULL,
  body TEXT,
  author TEXT NOT NULL,
  ipfs TEXT, -- IPFS hash
  start TIMESTAMP WITH TIME ZONE NOT NULL,
  "end" TIMESTAMP WITH TIME ZONE NOT NULL,
  snapshot TEXT, -- Block number
  state TEXT NOT NULL, -- 'pending', 'active', 'closed'
  choices TEXT[] NOT NULL,
  scores FLOAT[] NOT NULL,
  scores_total FLOAT NOT NULL,
  quorum FLOAT,
  votes_count INTEGER DEFAULT 0,
  type TEXT, -- 'single-choice', 'weighted', etc.
  strategies JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Snapshot Votes Table
CREATE TABLE IF NOT EXISTS snapshot_votes (
  id BIGSERIAL PRIMARY KEY,
  vote_id TEXT UNIQUE NOT NULL,
  proposal_id TEXT REFERENCES snapshot_proposals(proposal_id),
  voter TEXT NOT NULL,
  choice INTEGER, -- For single-choice
  choice_weights JSONB, -- For weighted voting
  voting_power FLOAT NOT NULL,
  reason TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- On-Chain Executions Table
CREATE TABLE IF NOT EXISTS onchain_executions (
  id BIGSERIAL PRIMARY KEY,
  proposal_id TEXT, -- Links to snapshot_proposals
  transaction_hash TEXT UNIQUE NOT NULL,
  block_number BIGINT NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  from_address TEXT,
  to_address TEXT,
  value TEXT, -- Wei amount as string
  gas_used BIGINT,
  gas_price TEXT,
  status TEXT NOT NULL, -- 'success', 'failed'
  function_signature TEXT,
  input_data TEXT,
  output_data TEXT,
  event_logs JSONB,
  collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Delegate Information
CREATE TABLE IF NOT EXISTS delegates (
  id BIGSERIAL PRIMARY KEY,
  address TEXT UNIQUE NOT NULL,
  ens_name TEXT,
  voting_power FLOAT DEFAULT 0,
  delegators_count INTEGER DEFAULT 0,
  votes_cast INTEGER DEFAULT 0,
  proposals_created INTEGER DEFAULT 0,
  forum_username TEXT,
  twitter_handle TEXT,
  first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_activity_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- On-Chain Executions Table
CREATE TABLE IF NOT EXISTS onchain_executions (
    id BIGSERIAL PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    transaction_hash TEXT UNIQUE NOT NULL,
    block_number BIGINT NOT NULL,
    executor_address TEXT NOT NULL,
    gas_used BIGINT,
    gas_price TEXT,
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- On-Chain Events Table (General)
CREATE TABLE IF NOT EXISTS onchain_events (
    id BIGSERIAL PRIMARY KEY,
    proposal_id TEXT,
    event_type TEXT NOT NULL, -- 'executed', 'vote', 'delegate', 'transfer'
    block_number BIGINT NOT NULL,
    transaction_hash TEXT NOT NULL,
    voter_address TEXT,
    vote_choice TEXT,
    voting_power TEXT,
    voted_at TIMESTAMP WITH TIME ZONE,
    executor_address TEXT,
    executed_at TIMESTAMP WITH TIME ZONE,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- On-Chain Sync Status
CREATE TABLE IF NOT EXISTS onchain_sync_status (
    id BIGSERIAL PRIMARY KEY,
    chain TEXT UNIQUE NOT NULL, -- 'arbitrum', 'ethereum'
    last_block BIGINT NOT NULL,
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Proposal Analytics (Aggregated)
CREATE TABLE IF NOT EXISTS proposal_analytics (
  id BIGSERIAL PRIMARY KEY,
  proposal_id TEXT UNIQUE NOT NULL,
  forum_thread_id TEXT REFERENCES forum_threads(thread_id),
  snapshot_proposal_id TEXT REFERENCES snapshot_proposals(proposal_id),
  execution_tx_hash TEXT REFERENCES onchain_executions(transaction_hash),
  
  -- Forum metrics
  forum_views INTEGER DEFAULT 0,
  forum_replies INTEGER DEFAULT 0,
  forum_participants INTEGER DEFAULT 0,
  forum_sentiment_score FLOAT, -- -1 to 1
  forum_discussion_days INTEGER,
  
  -- Voting metrics
  total_votes INTEGER DEFAULT 0,
  voter_participation_rate FLOAT,
  voting_power_concentration FLOAT, -- Gini coefficient
  winning_margin FLOAT,
  outcome TEXT, -- 'passed', 'rejected', 'pending'
  
  -- On-chain metrics
  executed BOOLEAN DEFAULT FALSE,
  execution_delay_days INTEGER,
  
  -- ML features
  features JSONB,
  prediction_score FLOAT,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_forum_threads_proposal_id ON forum_threads(proposal_id);
CREATE INDEX IF NOT EXISTS idx_forum_threads_created_at ON forum_threads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_posts_thread_id ON forum_posts(thread_id);
CREATE INDEX IF NOT EXISTS idx_forum_posts_created_at ON forum_posts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_snapshot_proposals_space ON snapshot_proposals(space);
CREATE INDEX IF NOT EXISTS idx_snapshot_proposals_state ON snapshot_proposals(state);
CREATE INDEX IF NOT EXISTS idx_snapshot_proposals_start ON snapshot_proposals(start DESC);
CREATE INDEX IF NOT EXISTS idx_onchain_events_proposal_id ON onchain_events(proposal_id);
CREATE INDEX IF NOT EXISTS idx_onchain_events_type ON onchain_events(event_type);
CREATE INDEX IF NOT EXISTS idx_onchain_events_block ON onchain_events(block_number);
CREATE INDEX IF NOT EXISTS idx_onchain_executions_proposal_id ON onchain_executions(proposal_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_votes_proposal_id ON snapshot_votes(proposal_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_votes_voter ON snapshot_votes(voter);

CREATE INDEX IF NOT EXISTS idx_onchain_executions_proposal_id ON onchain_executions(proposal_id);
CREATE INDEX IF NOT EXISTS idx_onchain_executions_block_number ON onchain_executions(block_number DESC);

CREATE INDEX IF NOT EXISTS idx_delegates_voting_power ON delegates(voting_power DESC);
CREATE INDEX IF NOT EXISTS idx_delegates_address ON delegates(address);

CREATE INDEX IF NOT EXISTS idx_proposal_analytics_proposal_id ON proposal_analytics(proposal_id);
CREATE INDEX IF NOT EXISTS idx_proposal_analytics_outcome ON proposal_analytics(outcome);

-- Row Level Security (RLS)
ALTER TABLE forum_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE forum_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshot_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshot_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE onchain_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onchain_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE onchain_sync_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE delegates ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposal_analytics ENABLE ROW LEVEL SECURITY;

-- Policies (Read-only for anon, full access for service_role)
CREATE POLICY "Allow public read access" ON forum_threads FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON forum_posts FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON snapshot_proposals FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON snapshot_votes FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON onchain_executions FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON delegates FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON proposal_analytics FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON onchain_events FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON onchain_sync_status FOR SELECT USING (true);
