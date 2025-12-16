// API Response Types for DAO Data AI Platform

// ============================================
// PROPOSAL TYPES
// ============================================

export type ProposalStatus = 'active' | 'passed' | 'rejected' | 'pending';

export interface Proposal {
  id: string;
  title: string;
  status: ProposalStatus;
  votesFor: number;
  votesAgainst: number;
  prediction: number;
  createdAt?: string;
  updatedAt?: string;
  description?: string;
  proposer?: string;
}

export interface ProposalsResponse {
  proposals: Proposal[];
  total: number;
  page?: number;
  limit?: number;
}

// ============================================
// VOTE TYPES
// ============================================

export type VoteChoice = 'for' | 'against' | 'abstain';

export interface Vote {
  id: string;
  proposalId: string;
  voter: string;
  choice: VoteChoice;
  votingPower: number;
  timestamp: string;
  transactionHash?: string;
}

export interface VotesResponse {
  votes: Vote[];
  total: number;
  page?: number;
  limit?: number;
}

// ============================================
// DELEGATE TYPES
// ============================================

export interface Delegate {
  id: string;
  address: string;
  delegatedVotes: number;
  votesCount: number;
  proposalsCreated: number;
  participationRate: number;
  joinedAt?: string;
}

export interface DelegatesResponse {
  delegates: Delegate[];
  total: number;
  page?: number;
  limit?: number;
}

// ============================================
// ANALYTICS TYPES
// ============================================

export interface DashboardStats {
  totalProposals: number;
  activeProposals: number;
  averagePrediction: number;
  totalVotes: number;
  totalDelegates: number;
  participationRate: number;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
  }[];
}

// ============================================
// ERROR TYPES
// ============================================

export interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
}

// ============================================
// COMMON TYPES
// ============================================

export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  order?: 'asc' | 'desc';
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  timestamp: string;
}
