"""Arbitrum DAO On-Chain Data Collector using Web3.py"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Arbitrum Governor Contract ABI (minimal)
GOVERNOR_ABI = [
    {"inputs": [{"internalType": "uint256", "name": "proposalId", "type": "uint256"}],
     "name": "state", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "proposalId", "type": "uint256"}],
     "name": "proposalVotes",
     "outputs": [{"internalType": "uint256", "name": "againstVotes", "type": "uint256"},
                  {"internalType": "uint256", "name": "forVotes", "type": "uint256"},
                  {"internalType": "uint256", "name": "abstainVotes", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"anonymous": False,
     "inputs": [{"indexed": False, "internalType": "uint256", "name": "proposalId", "type": "uint256"}],
     "name": "ProposalCreated", "type": "event"},
    {"anonymous": False,
     "inputs": [{"indexed": True, "internalType": "address", "name": "voter", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "proposalId", "type": "uint256"}],
     "name": "VoteCast", "type": "event"}
]

class ArbitrumOnChainCollector:
    """Collects on-chain governance data from Arbitrum DAO"""
    
    RPC_URL = os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc")
    GOVERNOR_ADDRESS = "0xf07DeD9dC292157749B6Fd268E37DF6EA38395B9"
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(self.RPC_URL))
        self.governor = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.GOVERNOR_ADDRESS),
            abi=GOVERNOR_ABI
        )
        
    def get_proposal_state(self, proposal_id: int) -> Dict:
        """Get current state and votes for a proposal"""
        try:
            state = self.governor.functions.state(proposal_id).call()
            states = ["Pending", "Active", "Canceled", "Defeated", 
                     "Succeeded", "Queued", "Expired", "Executed"]
            
            votes = self.governor.functions.proposalVotes(proposal_id).call()
            
            return {
                "proposal_id": str(proposal_id),
                "state": states[state].lower() if state < len(states) else "unknown",
                "votes_against": int(votes[0]),
                "votes_for": int(votes[1]),
                "votes_abstain": int(votes[2]),
                "synced_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error fetching proposal {proposal_id}: {e}")
            return None
    
    def get_recent_proposals(self, from_block: int = 0) -> List[Dict]:
        """Fetch ProposalCreated events"""
        try:
            event_filter = self.governor.events.ProposalCreated.create_filter(
                fromBlock=from_block, toBlock='latest'
            )
            events = event_filter.get_all_entries()
            
            proposals = []
            for event in events:
                proposals.append({
                    "proposal_id": str(event['args']['proposalId']),
                    "block": event['blockNumber'],
                    "tx_hash": event['transactionHash'].hex()
                })
            return proposals
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def sync_proposals(self, proposal_ids: List[int]) -> List[Dict]:
        """Sync multiple proposals"""
        results = []
        for pid in proposal_ids:
            data = self.get_proposal_state(pid)
            if data:
                results.append(data)
        return results

if __name__ == "__main__":
    collector = ArbitrumOnChainCollector()
    print("Arbitrum On-Chain Collector initialized")
    print(f"RPC: {collector.RPC_URL}")
    print(f"Governor: {collector.GOVERNOR_ADDRESS}")
