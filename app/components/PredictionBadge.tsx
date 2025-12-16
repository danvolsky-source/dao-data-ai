import React from 'react';
import { Prediction } from '@/app/types/api';

interface PredictionBadgeProps {
  prediction: Prediction;
}

const PredictionBadge: React.FC<PredictionBadgeProps> = ({ prediction }) => {
  const getColor = () => {
    if (prediction.confidence > 0.7) return 'bg-green-100 text-green-800';
    if (prediction.confidence > 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getColor()}`}>
      <span className="mr-2">🎯</span>
      <span>{prediction.predicted_outcome === 'pass' ? '✓ Pass' : '✗ Fail'}</span>
      <span className="ml-2 text-xs opacity-75">{Math.round(prediction.confidence * 100)}%</span>
    </div>
  );
};

export default PredictionBadge;
