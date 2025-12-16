import React from 'react';
import { Score } from '@/app/types/api';

interface ScoreBadgeProps {
  score: Score;
}

const ScoreBadge: React.FC<ScoreBadgeProps> = ({ score }) => {
  const getColor = () => {
    if (score.total_score > 80) return 'bg-green-500';
    if (score.total_score > 60) return 'bg-blue-500';
    if (score.total_score > 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700">Composite Score</h3>
        <div className={`${getColor()} text-white px-3 py-1 rounded-full text-lg font-bold`}>
          {Math.round(score.total_score)}/100
        </div>
      </div>
      <div className="space-y-2">
        <ScoreBreakdown label="On-Chain" value={score.onchain_score} />
        <ScoreBreakdown label="Sentiment" value={score.sentiment_score} />
        <ScoreBreakdown label="Activity" value={score.activity_score} />
        <ScoreBreakdown label="Quality" value={score.quality_score} />
      </div>
    </div>
  );
};

const ScoreBreakdown: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="flex items-center justify-between text-sm">
    <span className="text-gray-600">{label}</span>
    <div className="flex items-center gap-2">
      <div className="w-24 bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full"
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-gray-700 font-medium w-8">{Math.round(value)}</span>
    </div>
  </div>
);

export default ScoreBadge;
