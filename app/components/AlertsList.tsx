import React from 'react';
import { Alert } from '@/app/types/api';

interface AlertsListProps {
  alerts: Alert[];
}

const AlertsList: React.FC<AlertsListProps> = ({ alerts }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '📊';
      default:
        return 'ℹ️';
    }
  };

  if (alerts.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
        No active alerts
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">Active Alerts</h3>
      {alerts.map((alert) => (
        <div
          key={alert.alert_id}
          className={`rounded-lg p-4 border-l-4 ${getSeverityColor(alert.severity)}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{getSeverityIcon(alert.severity)}</span>
              <div>
                <h4 className="font-medium text-sm">{alert.alert_type}</h4>
                <p className="text-sm mt-1">{alert.message}</p>
                {alert.recommendation && (
                  <p className="text-xs mt-2 opacity-75">
                    <strong>Recommendation:</strong> {alert.recommendation}
                  </p>
                )}
              </div>
            </div>
            <span className="text-xs opacity-60 whitespace-nowrap ml-2">
                {alert.triggered_at ? new Date(alert.triggered_at).toLocaleDateString() : 'N/A'}            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertsList;
