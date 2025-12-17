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
        const [predictions, scores, alerts] = await Promise.all([
          advancedApi.getPredictions(),
          advancedApi.getScores(),
          advancedApi.getAlerts()
        ]);
        setAdvancedData({ predictions, scores, alerts, sentiment: null });
      } catch (error) {
        console.error('Failed to fetch advanced data:', error);
      }
    }
    fetchAdvancedData();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-gray-900 via-blue-900 to-gray-900 py-16 px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Real-time DAO Analytics
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mt-2">
              Powered by AI
            </span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Track proposals, votes, and delegate activity across multiple DAOs. 
            Get AI-powered insights and predictive analytics for better governance decisions.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-cyan-600 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
              Explore Dashboard
            </button>
            <button className="bg-white/10 backdrop-blur-sm text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/20 transition-all duration-200 border border-white/20">
              View Documentation
            </button>
          </div>
        </div>
      </section>

      {/* Stats Overview */}
      <section className="py-8 px-8 bg-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10 text-center">
              <div className="text-3xl font-bold text-cyan-400 mb-2">1,000+</div>
              <div className="text-gray-400 text-sm">Active Proposals</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10 text-center">
              <div className="text-3xl font-bold text-blue-400 mb-2">50K+</div>
              <div className="text-gray-400 text-sm">Total Votes</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10 text-center">
              <div className="text-3xl font-bold text-purple-400 mb-2">500+</div>
              <div className="text-gray-400 text-sm">Active Delegates</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-6 border border-white/10 text-center">
              <div className="text-3xl font-bold text-green-400 mb-2">95%</div>
              <div className="text-gray-400 text-sm">Prediction Accuracy</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section id="dashboard" className="py-8 px-8">
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
      </section>
    </main>
  );
}
