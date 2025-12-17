/**
 * Advanced API Service for DAO Data AI
 * Provides functions to interact with ML, scoring, alerts, and sentiment endpoints
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
import { logger, logApiRequest, logApiResponse, logError, logPerformance } from '@/lib/logger';

// TypeScript interfaces
export interface Prediction {
  proposal_id: string;
  prediction: number;
  confidence: number;
  model: string;
  features_used?: number;
}

export interface Score {
  proposal_id: string;
  overall_score: number;
  rating: 'EXCELLENT' | 'GOOD' | 'MODERATE' | 'POOR' | 'CRITICAL';
  component_scores: {
    prediction_confidence: number;
    sentiment: number;
    participation: number;
    risk_assessment: number;
    treasury_impact: number;
    execution_quality: number;
  };
  recommendation: {
    action: string;
    confidence: string;
    message: string;
  };
}

export interface Alert {
    type?: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'INFO';
  message: string;
    alert_id?: string;
    alert_type?: string;
    triggered_at?: string;
    recommendation?: string;
}

export interface Sentiment {
  proposal_id: string;
  overall_sentiment: number;
  sentiment_label: string;
  positive_ratio: number;
  negative_ratio: number;
  neutral_ratio: number;
  message_count: number;
  top_topics: string[];
}

export interface DashboardSummary {
  total_proposals: number;
  active_proposals: number;
  average_prediction: number;
  active_alerts: number;
  sentiment_score: number;
  recent_predictions: Array<{
    id: string;
    prediction: number;
    confidence: number;
    score: number;
  }>;
  top_scored_proposals: Array<{
    id: string;
    title: string;
    score: number;
    rating: string;
  }>;
}

/**
 * Get ML prediction for a proposal
 */
export async function getPrediction(proposalId: string): Promise<Prediction | null> {
  try {
        const startTime = Date.now();
    logApiRequest('GET', `/api/advanced/predictions/${proposalId}`, { proposalId });
    const res = await fetch(`${API_BASE}/api/advanced/predictions/${proposalId}`);
    const data = await res.json();
    return data.status === 'success' ? data.data : null;
  } catch (error) {
    console.error('Error fetching prediction:', error);
        logError('Error fetching prediction', error as Error, { proposalId });
    return null;
      const duration = Date.now() - startTime;
    logApiResponse('GET', `/api/advanced/predictions/${proposalId}`, 200, duration, { status: data.status });
  }
}

/**
 * Get batch predictions for multiple proposals
 */
export async function getBatchPredictions(proposalIds: string[]): Promise<Prediction[]> {
  try {
    const res = await fetch(`${API_BASE}/api/advanced/predictions/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(proposalIds)
    });
    const data = await res.json();
    return data.status === 'success' ? data.data : [];
  } catch (error) {
    console.error('Error fetching batch predictions:', error);
    return [];
  }
}

/**
 * Get comprehensive score for a proposal
 */
export async function getScore(proposalId: string): Promise<Score | null> {
  try {
    const res = await fetch(`${API_BASE}/api/advanced/scoring/${proposalId}`);
    const data = await res.json();
    return data.status === 'success' ? data.data : null;
  } catch (error) {
    console.error('Error fetching score:', error);
    return null;
  }
}

/**
 * Get proposal rankings/leaderboard
 */
export async function getLeaderboard(limit: number = 10) {
  try {
    const res = await fetch(`${API_BASE}/api/advanced/scoring/leaderboard?limit=${limit}`);
    const data = await res.json();
    return data.status === 'success' ? data.data : [];
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    return [];
  }
}

/**
 * Get active alerts
 */
export async function getAlerts(severity?: string): Promise<Alert[]> {
  try {
    const url = severity
      ? `${API_BASE}/api/advanced/alerts?severity=${severity}`
      : `${API_BASE}/api/advanced/alerts`;
    const res = await fetch(url);
    const data = await res.json();
    return data.status === 'success' ? data.data : [];
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return [];
  }
}

/**
 * Subscribe to alerts
 */
export async function subscribeToAlerts(email: string, alertTypes: string[]) {
  try {
    const res = await fetch(`${API_BASE}/api/advanced/alerts/subscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, alert_types: alertTypes })
    });
    const data = await res.json();
    return data;
  } catch (error) {
    console.error('Error subscribing to alerts:', error);
    return null;
  }
}

/**
 * Get sentiment analysis for a proposal
 */
export async function getSentiment(proposalId: string): Promise<Sentiment | null> {
  try {
    const res = await fetch(`${API_BASE}/api/advanced/sentiment/${proposalId}`);
    const data = await res.json();
    return data.status === 'success' ? data.data : null;
  } catch (error) {
    console.error('Error fetching sentiment:', error);
    return null;
  }
}

/**
 * Get on-chain data for a DAO
 */
export async function getOnChainData(dao: string) {
  try {
    const res = await fetch(`${API_BASE}/api/advanced/onchain/${dao}`);
    const data = await res.json();
    return data.status === 'success' ? data.data : null;
  } catch (error) {
    console.error('Error fetching on-chain data:', error);
    return null;
  }
}

/**
 * Get complete dashboard summary
 */
export async function getDashboardSummary(): Promise<DashboardSummary | null> {
  try {
    const res = await fetch(`${API_BASE}/api/advanced/dashboard/summary`);
    const data = await res.json();
    return data.status === 'success' ? data.data : null;
  } catch (error) {
    console.error('Error fetching dashboard summary:', error);
    return null;
  }
}

/**
 * Helper function to format prediction percentage
 */
export function formatPrediction(prediction: number): string {
  return `${Math.round(prediction * 100)}%`;
}

/**
 * Helper function to get color for prediction
 */
export function getPredictionColor(prediction: number): string {
  if (prediction >= 0.7) return 'green';
  if (prediction >= 0.5) return 'yellow';
  return 'red';
}

/**
 * Helper function to get color for score rating
 */
export function getScoreColor(rating: string): string {
  const colorMap: Record<string, string> = {
    'EXCELLENT': 'green',
    'GOOD': 'blue',
    'MODERATE': 'yellow',
    'POOR': 'orange',
    'CRITICAL': 'red'
  };
  return colorMap[rating] || 'gray';
  }

// Default export object for convenient usage
const advancedApi =  {
  getPrediction,
  getPredictions: async () => {
    // TODO: Implement fetching all predictions
    // For now, return empty array
    return [];
  },
  getBatchPredictions,
  getScore,
  getScores: async () => {
    // TODO: Implement fetching all scores  
    // For now, return empty array
    return [];
  },
  getLeaderboard,
  getAlerts,
  subscribeToAlerts,
  getSentiment,
  getOnChainData,
  getDashboardSummary,
  // Helper functions
  formatPrediction,
  getPredictionColor,
  getScoreColor
};

export default advancedApi;

