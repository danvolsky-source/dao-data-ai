'use client';

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ProposalData {
  id: string;
  title: string;
  status: string;
  votesFor: number;
  votesAgainst: number;
  prediction: number;
}

interface ProposalsChartProps {
  proposals: ProposalData[];
}

const ProposalsChart: React.FC<ProposalsChartProps> = ({ proposals }) => {
  const data = {
    labels: proposals.map(p => p.title.substring(0, 30) + '...'),
    datasets: [
      {
        label: 'Votes For',
        data: proposals.map(p => p.votesFor),
        backgroundColor: 'rgba(34, 197, 94, 0.7)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1,
      },
      {
        label: 'Votes Against',
        data: proposals.map(p => p.votesAgainst),
        backgroundColor: 'rgba(239, 68, 68, 0.7)',
        borderColor: 'rgb(239, 68, 68)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#fff',
        },
      },
      title: {
        display: true,
        text: 'Proposal Voting Comparison',
        color: '#fff',
        font: {
          size: 18,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#9ca3af',
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
      },
      y: {
        ticks: {
          color: '#9ca3af',
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.1)',
        },
      },
    },
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="h-96">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default ProposalsChart;
