import { NextResponse } from 'next/server';

// Mock data for development
export async function GET() {
  const mockProposals = [
    {
      id: '1',
      title: 'Increase Treasury Allocation for Development',
      status: 'active',
      votesFor: 25400000,
      votesAgainst: 8500000,
      prediction: 78
    },
    {
      id: '2',
      title: 'Establish Grants Program for Layer 2 Solutions',
      status: 'active',
      votesFor: 18900000,
      votesAgainst: 12300000,
      prediction: 62
    },
    {
      id: '3',
      title: 'Protocol Upgrade v2.5 Proposal',
      status: 'passed',
      votesFor: 32100000,
      votesAgainst: 4200000,
      prediction: 89
    },
    {
      id: '4',
      title: 'Expand Security Council to 12 Members',
      status: 'active',
      votesFor: 14200000,
      votesAgainst: 9800000,
      prediction: 58
    },
    {
      id: '5',
      title: 'Create DAO Education Initiative',
      status: 'passed',
      votesFor: 21500000,
      votesAgainst: 6700000,
      prediction: 76
    }
  ];

  return NextResponse.json(mockProposals);
}
