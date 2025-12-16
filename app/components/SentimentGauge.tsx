import React from 'react';
import { Sentiment } from '@/app/types/api';

interface SentimentGaugeProps {
  sentiment: Sentiment;
}

const SentimentGauge: React.FC<SentimentGaugeProps> = ({ sentiment }) => {
  const getSentimentColor = () => {
    if (sentiment.overall_sentiment > 0.5) return '#10b981';
    if (sentiment.overall_sentiment > 0) return '#3b82f6';
    if (sentiment.overall_sentiment > -0.5) return '#f59e0b';
    return '#ef4444';
  };

  const getSentimentLabel = () => {
    if (sentiment.overall_sentiment > 0.5) return 'Very Positive';
    if (sentiment.overall_sentiment > 0) return 'Positive';
    if (sentiment.overall_sentiment > -0.5) return 'Neutral';
    return 'Negative';
  };

  const getSentimentEmoji = () => {
    if (sentiment.overall_sentiment > 0.5) return '😄';
    if (sentiment.overall_sentiment > 0) return '🙂';
    if (sentiment.overall_sentiment > -0.5) return '😐';
    return '☹️';
  };

  const normalizedScore = ((sentiment.overall_sentiment + 1) / 2) * 100;

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Community Sentiment</h3>
      <div className="flex items-center justify-center mb-4">
        <div className="relative w-32 h-32">
          <svg className="transform -rotate-90" viewBox="0 0 120 120">
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="10"
            />
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke={getSentimentColor()}
              strokeWidth="10"
              strokeDasharray={`${normalizedScore * 3.14} 314`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <span className="text-3xl">{getSentimentEmoji()}</span>
            <span className="text-xs font-medium text-gray-600 mt-1">
              {Math.round(normalizedScore)}%
            </span>
          </div>
        </div>
      </div>
      <div className="text-center">
        <p className="text-lg font-semibold" style={{ color: getSentimentColor() }}>
          {getSentimentLabel()}
        </p>
      </div>
      <div className="mt-4 pt-4 border-t space-y-2">
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Positive</span>
          <span className="font-medium text-green-600">
            {Math.round(sentiment.positive_ratio * 100)}%
          </span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Negative</span>
          <span className="font-medium text-red-600">
            {Math.round(sentiment.negative_ratio * 100)}%
          </span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Neutral</span>
          <span className="font-medium text-gray-600">
            {Math.round(sentiment.neutral_ratio * 100)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default SentimentGauge;
