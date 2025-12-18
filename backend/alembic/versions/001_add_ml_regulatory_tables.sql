-- Phase 1: ML, Predictions, Sentiment Analysis, and Regulatory Tables
-- Migration: 001_add_ml_regulatory_tables
-- Date: 2025-12-18

-- ========================================
-- PREDICTIONS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    prediction_type TEXT NOT NULL, -- 'outcome', 'sentiment', 'risk'
    predicted_value DECIMAL NOT NULL,
    confidence_score DECIMAL NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    actual_value DECIMAL, -- filled after vote completion
    accuracy_status TEXT CHECK (accuracy_status IN ('correct', 'incorrect', 'pending')),
    metadata JSONB DEFAULT '{}',
    CONSTRAINT fk_proposal FOREIGN KEY (proposal_id) REFERENCES snapshot_proposals(proposal_id) ON DELETE CASCADE
);

-- ========================================
-- SENTIMENT ANALYSIS TABLE (Aggregated)
-- ========================================
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id BIGSERIAL PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('discord', 'forum', 'twitter', 'telegram', 'aggregated')),
    sentiment_score DECIMAL NOT NULL CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    message_count INTEGER NOT NULL DEFAULT 0,
    positive_count INTEGER NOT NULL DEFAULT 0,
    negative_count INTEGER NOT NULL DEFAULT 0,
    neutral_count INTEGER NOT NULL DEFAULT 0,
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    CONSTRAINT fk_proposal_sentiment FOREIGN KEY (proposal_id) REFERENCES snapshot_proposals(proposal_id) ON DELETE CASCADE,
    UNIQUE(proposal_id, source, analyzed_at)
);

-- ========================================
-- MODEL METRICS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS model_metrics (
    id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    accuracy DECIMAL NOT NULL CHECK (accuracy >= 0 AND accuracy <= 1),
    precision DECIMAL NOT NULL CHECK (precision >= 0 AND precision <= 1),
    recall DECIMAL NOT NULL CHECK (recall >= 0 AND recall <= 1),
    f1_score DECIMAL NOT NULL CHECK (f1_score >= 0 AND f1_score <= 1),
    backtesting_period TEXT NOT NULL,
    total_predictions INTEGER NOT NULL DEFAULT 0,
    correct_predictions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(model_name, model_version, created_at)
);

-- ========================================
-- AUDIT LOG TABLE (Regulatory Requirement)
-- ========================================
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL CHECK (resource_type IN ('proposal', 'vote', 'prediction', 'sentiment', 'model', 'api_call')),
    resource_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- Predictions indexes
CREATE INDEX IF NOT EXISTS idx_predictions_proposal_id ON predictions(proposal_id);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_accuracy_status ON predictions(accuracy_status);

-- Sentiment analysis indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_proposal_id ON sentiment_analysis(proposal_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_source ON sentiment_analysis(source);
CREATE INDEX IF NOT EXISTS idx_sentiment_analyzed_at ON sentiment_analysis(analyzed_at DESC);

-- Model metrics indexes
CREATE INDEX IF NOT EXISTS idx_model_metrics_name ON model_metrics(model_name);
CREATE INDEX IF NOT EXISTS idx_model_metrics_version ON model_metrics(model_version);
CREATE INDEX IF NOT EXISTS idx_model_metrics_created_at ON model_metrics(created_at DESC);

-- Audit log indexes
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource_type ON audit_log(resource_type);

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Enable RLS on all tables
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Public read access policies
CREATE POLICY "Allow public read access on predictions" ON predictions FOR SELECT USING (true);
CREATE POLICY "Allow public read access on sentiment_analysis" ON sentiment_analysis FOR SELECT USING (true);
CREATE POLICY "Allow public read access on model_metrics" ON model_metrics FOR SELECT USING (true);

-- Audit log: Admin only (this requires service_role key)
CREATE POLICY "Allow admin read access on audit_log" ON audit_log FOR SELECT USING (
    current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
);

-- ========================================
-- COMMENTS FOR DOCUMENTATION
-- ========================================

COMMENT ON TABLE predictions IS 'ML predictions for proposal outcomes with confidence scores and backtesting results';
COMMENT ON TABLE sentiment_analysis IS 'Aggregated sentiment analysis from various sources (Discord, forums, Twitter)';
COMMENT ON TABLE model_metrics IS 'Performance metrics for ML models - used for transparency and regulatory compliance';
COMMENT ON TABLE audit_log IS 'Comprehensive audit trail for regulatory compliance and security monitoring';

COMMENT ON COLUMN predictions.confidence_score IS 'Model confidence from 0 to 1. Only predictions with >0.85 should be displayed prominently';
COMMENT ON COLUMN predictions.accuracy_status IS 'Tracks if prediction was correct after proposal completion - used for live tracking';
COMMENT ON COLUMN sentiment_analysis.sentiment_score IS 'Normalized sentiment from -1 (very negative) to 1 (very positive)';
COMMENT ON COLUMN audit_log.details IS 'JSON object containing request details, response data, and any relevant context';
