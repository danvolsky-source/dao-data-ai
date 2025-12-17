'use client';

import { useEffect, useState } from 'react';
import DaoAnalyticsDashboard from './components/DaoAnalyticsDashboard';
import PredictionBadge from './components/PredictionBadge';
import ScoreBadge from './components/ScoreBadge';
import AlertsList from './components/AlertsList';
import SentimentGauge from './components/SentimentGauge';
import advancedApi from './lib/advancedApi';
import type { Prediction, Score, Alert, Sentiment } from './types/api';

export default function Home() {
  const [advancedData, setAdvancedData] = useState<{
    predictions: Prediction[];
    scores: Score[];
    alerts: Alert[];
    sentiment: Sentiment | null;
  }>({ predictions: [], scores: [], alerts: [], sentiment: null });

  useEffect(() => {
    async function fetchAdvancedData() {
      try {
        const [predictions, scores, alerts, sentiment] = await Promise.all([
          advancedApi.getPredictions(),
          advancedApi.getScores(),
          advancedApi.getAlerts(),
          advancedApi.getSentiment()
        ]);
        setAdvancedData({ predictions, scores, alerts, sentiment });
      } catch (error) {
        console.error('Failed to fetch advanced data:', error);
      }
    }
    fetchAdvancedData();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Advanced Analytics Sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1 space-y-6">
            {/* Sentiment Gauge */}
            {advancedData.sentiment && (
              <SentimentGauge sentiment={advancedData.sentiment} />
            )}
            {/* Alerts List */}
            <AlertsList alerts={advancedData.alerts} />
          </div>
          
          {/* Main Dashboard */}
          <div className="lg:col-span-3">
            <DaoAnalyticsDashboard />
          </div>
        </div>

        {/* Predictions & Scores Grid */}
        {(advancedData.predictions.length > 0 || advancedData.scores.length > 0) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            {/* Predictions */}
            {advancedData.predictions.length > 0 && (
              <div className="bg-white rounded-lg p-6 shadow-lg">
                <h2 className="text-xl font-bold text-gray-900 mb-4">ML Predictions</h2>
                <div className="space-y-3">
                  {advancedData.predictions.map((prediction) => (
                    <div key={prediction.proposal_id} className="border-b pb-3 last:border-b-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">Proposal #{prediction.proposal_id}</span>
                        <PredictionBadge prediction={prediction} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Scores */}
            {advancedData.scores.length > 0 && (
              <div>
                {advancedData.scores.map((score) => (
                  <ScoreBadge key={score.proposal_id} score={score} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
