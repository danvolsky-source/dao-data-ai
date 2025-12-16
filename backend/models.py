"""SQLAlchemy Database Models for DAO Data AI"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Proposal(Base):
    """DAO Proposal Model"""
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(String, unique=True, index=True, nullable=False)
    dao_name = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    proposer = Column(String)  # Wallet address
    status = Column(String, index=True)  # active, passed, failed, pending
    voting_start = Column(DateTime)
    voting_end = Column(DateTime)
    votes_for = Column(Float, default=0.0)
    votes_against = Column(Float, default=0.0)
    votes_abstain = Column(Float, default=0.0)
    total_votes = Column(Float, default=0.0)
    quorum = Column(Float)
    category = Column(String)  # treasury, governance, technical, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prediction = relationship("Prediction", back_populates="proposal", uselist=False)
    score = relationship("ProposalScore", back_populates="proposal", uselist=False)
    alerts = relationship("Alert", back_populates="proposal")
    discussions = relationship("DiscussionData", back_populates="proposal")


class Prediction(Base):
    """ML Prediction Model"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), unique=True, nullable=False)
    predicted_outcome = Column(String)  # pass, fail
    confidence = Column(Float)  # 0.0 to 1.0
    probability_pass = Column(Float)
    probability_fail = Column(Float)
    model_version = Column(String)
    features_used = Column(JSON)  # Store feature importance
    prediction_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    proposal = relationship("Proposal", back_populates="prediction")


class ProposalScore(Base):
    """Proposal Quality Score Model"""
    __tablename__ = "proposal_scores"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), unique=True, nullable=False)
    overall_score = Column(Float)  # 0.0 to 100.0
    clarity_score = Column(Float)
    feasibility_score = Column(Float)
    impact_score = Column(Float)
    community_support_score = Column(Float)
    risk_score = Column(Float)
    engagement_score = Column(Float)
    score_breakdown = Column(JSON)  # Detailed scoring metrics
    recommendations = Column(JSON)  # List of improvement suggestions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    proposal = relationship("Proposal", back_populates="score")


class Alert(Base):
    """Alert/Notification Model"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    alert_type = Column(String, index=True)  # critical, warning, info
    severity = Column(String)  # high, medium, low
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional context
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    
    # Relationship
    proposal = relationship("Proposal", back_populates="alerts")


class DiscussionData(Base):
    """Discord/Forum Discussion Data Model"""
    __tablename__ = "discussion_data"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    source = Column(String)  # discord, discourse, snapshot
    message_id = Column(String, unique=True)
    author = Column(String)
    content = Column(Text)
    sentiment = Column(String)  # positive, negative, neutral
    sentiment_score = Column(Float)  # -1.0 to 1.0
    engagement_metrics = Column(JSON)  # likes, replies, etc.
    timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    proposal = relationship("Proposal", back_populates="discussions")


class OnChainData(Base):
    """On-chain Transaction/Event Data Model"""
    __tablename__ = "onchain_data"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(String, index=True)
    dao_name = Column(String, index=True)
    transaction_hash = Column(String, unique=True)
    block_number = Column(Integer)
    event_type = Column(String)  # vote_cast, proposal_created, etc.
    voter_address = Column(String)
    vote_choice = Column(String)  # for, against, abstain
    vote_weight = Column(Float)
    timestamp = Column(DateTime)
    raw_data = Column(JSON)  # Full transaction/event data
    created_at = Column(DateTime, default=datetime.utcnow)


class HistoricalData(Base):
    """Historical Analysis Data for ML Training"""
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(String, unique=True, index=True)
    dao_name = Column(String, index=True)
    actual_outcome = Column(String)  # pass, fail
    features = Column(JSON)  # All features used for training
    prediction_accuracy = Column(Float)  # How accurate was prediction
    timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
