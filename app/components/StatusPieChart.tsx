'use client';

import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

interface ProposalData {
  id: string;
  title: string;
  status: string;
  votesFor: number;
  votesAgainst: number;
  prediction: number;
}

interface StatusPieChartProps {
  proposals: ProposalData[];
}

const StatusPieChart: React.FC<StatusPieChartProps> = ({ proposals }) => {
  // Count proposals by status
  const statusCounts = proposals.reduce((acc, proposal) => {
    acc[proposal.status] = (acc[proposal.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const data = {
    labels: Object.keys(statusCounts).map(
      status => status.charAt(0).toUpperCase() + status.slice(1)
    ),
    datasets: [
      {
        label: 'Proposals by Status',
        data: Object.values(statusCounts),
        backgroundColor: [
          'rgba(34, 197, 94, 0.7)',   // green for active/passed
          'rgba(59, 130, 246, 0.7)',  // blue
          'rgba(249, 115, 22, 0.7)',  // orange
          'rgba(239, 68, 68, 0.7)',   // red
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(249, 115, 22)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#fff',
          padding: 15,
          font: {
            size: 12,
          },
        },
      },
      title: {
        display: true,
        text: 'Proposal Status Distribution',
        color: '#fff',
        font: {
          size: 18,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="h-80">
        <Pie data={data} options={options} />
      </div>
    </div>
  );
};

export default StatusPieChart;
