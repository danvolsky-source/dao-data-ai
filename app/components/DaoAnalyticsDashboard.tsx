'use client';

import React, { useState, useEffect } from 'react';
import ProposalsChart from './ProposalsChart';
import StatusPieChart from './StatusPieChart';

interface ProposalData {
  id: string;
  title: string;
  status: string;
  votesFor: number;
  votesAgainst: number;
  prediction: number;
}

const DaoAnalyticsDashboard = () => {
  const [proposals, setProposals] = useState<ProposalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProposals = async () => {
      try {
        const response = await fetch('/api/proposals');
        if (!response.ok) {
          throw new Error('Failed to fetch proposals');
        }
        const data = await response.json();
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
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-white text-xl">Loading DAO Analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-400 text-xl">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto">
      <h1 className="text-4xl font-bold text-white mb-8">
        Arbitrum DAO Analytics Dashboard
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Total Proposals</h3>
          <p className="text-3xl font-bold text-white">{proposals.length}</p>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Active Proposals</h3>
          <p className="text-3xl font-bold text-white">
            {proposals.filter(p => p.status === 'active').length}
          </p>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-gray-400 text-sm font-medium mb-2">Avg Prediction</h3>
          <p className="text-3xl font-bold text-white">
            {proposals.length > 0 
              ? (proposals.reduce((acc, p) => acc + p.prediction, 0) / proposals.length).toFixed(1)
              : '0'}%
          </p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-2xl font-bold text-white">Proposals</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Votes For
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Votes Against
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  AI Prediction
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {proposals.map((proposal) => (
                <tr key={proposal.id} className="hover:bg-gray-750">
                  <td className="px-6 py-4 text-sm text-white">
                    {proposal.title}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      proposal.status === 'active' 
                        ? 'bg-green-900 text-green-300' 
                        : 'bg-gray-700 text-gray-300'
                    }`}>
                      {proposal.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-green-400">
                    {proposal.votesFor.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-red-400">
                    {proposal.votesAgainst.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-white font-medium">
                    {proposal.prediction}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ProposalsChart proposals={proposals} />
        <StatusPieChart proposals={proposals} />
);
};

      <StatusPieChart proposals={proposals} />
export default DaoAnalyticsDashboard;
