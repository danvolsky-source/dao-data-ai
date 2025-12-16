'use client';

import React, { useState, useEffect } from 'react';
import type { Proposal } from '../types/api';
import ProposalsChart from './ProposalsChart';
import StatusPieChart from './StatusPieChart';

const DaoAnalyticsDashboard = () => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProposals = async () => {
      try {
        const response = await fetch('/api/proposals');
        if (!response.ok) {
          throw new Error('Failed to fetch proposals');
        }
        const data: Proposal[] = await response.json();
        setProposals(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchProposals();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8">
        <div className="text-white text-center">Loading DAO Analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8">
        <div className="text-red-500 text-center">Error: {error}</div>
      </div>
    );
  }

  const totalProposals = proposals.length;
  const activeProposals = proposals.filter(p => p.status === 'active').length;
  const avgPrediction = totalProposals > 0
    ? (proposals.reduce((acc, p) => acc + p.prediction, 0) / totalProposals).toFixed(1)
    : '0';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8">
      <h1 className="text-4xl font-bold text-white mb-8">
        Arbitrum DAO Analytics Dashboard
      </h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white/80 mb-2">Total Proposals</h3>
          <p className="text-3xl font-bold text-white">{totalProposals}</p>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white/80 mb-2">Active Proposals</h3>
          <p className="text-3xl font-bold text-white">{activeProposals}</p>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white/80 mb-2">Avg Prediction</h3>
          <p className="text-3xl font-bold text-white">{avgPrediction}%</p>
        </div>
      </div>

      {/* Proposals Table */}
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20 mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Proposals</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-white">
            <thead>
              <tr className="border-b border-white/20">
                <th className="text-left p-3">Title</th>
                <th className="text-left p-3">Status</th>
                <th className="text-right p-3">Votes For</th>
                <th className="text-right p-3">Votes Against</th>
                <th className="text-right p-3">AI Prediction</th>
              </tr>
            </thead>
            <tbody>
              {proposals.map((proposal) => (
                <tr key={proposal.id} className="border-b border-white/10">
                  <td className="p-3">{proposal.title}</td>
                  <td className="p-3">{proposal.status}</td>
                  <td className="text-right p-3">{proposal.votesFor.toLocaleString()}</td>
                  <td className="text-right p-3">{proposal.votesAgainst.toLocaleString()}</td>
                  <td className="text-right p-3">{proposal.prediction}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4">Votes Distribution</h3>
          <ProposalsChart proposals={proposals} />
        </div>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4">Status Overview</h3>
          <StatusPieChart proposals={proposals} />
        </div>
      </div>
    </div>
  );
};

export default DaoAnalyticsDashboard;
