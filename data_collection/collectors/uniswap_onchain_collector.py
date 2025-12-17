#!/usr/bin/env python3
"""
Uniswap DAO On-Chain Data Collector

Collects:
- Proposal executions from Uniswap Governor contract
- Vote casting events
- Delegate voting power changes

Requires:
- Web3.py for Ethereum RPC connection
- Supabase for data storage
"""

import os
import time
import json
from datetime import datetime
from web3 import Web3
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
ETHEREUM_RPC = os.getenv('ETHEREUM_RPC_URL', 'https://eth.llamarpc.com')

# Uniswap DAO Governor contract (Timelock)
GOVERNOR_ADDRESS = '0x5e4be8Bc9637f0EAA1A755019e06A68ce081D58F'  # Uniswap Governance Timelock

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
w3 = Web3(Web3.HTTPProvider(ETHEREUM_RPC))

if not w3.is_connected():
    print(f'Warning: Failed to connect to Ethereum RPC at {ETHEREUM_RPC}')

# Governor ABI (relevant events)
GOVERNOR_ABI = [
    {
        'anonymous': False,
        'inputs': [
            {'indexed': False, 'name': 'proposalId', 'type': 'uint256'}
        ],
        'name': 'ProposalExecuted',
        'type': 'event'
    },
    {
        'anonymous': False,
        'inputs': [
            {'indexed': True, 'name': 'voter', 'type': 'address'},
            {'indexed': False, 'name': 'proposalId', 'type': 'uint256'},
            {'indexed': False, 'name': 'support', 'type': 'uint8'},
            {'indexed': False, 'name': 'weight', 'type': 'uint256'},
            {'indexed': False, 'name': 'reason', 'type': 'string'}
        ],
        'name': 'VoteCast',
        'type': 'event'
    }
]

def get_latest_block():
    """Get the latest processed block from database"""
    if not supabase:
        return w3.eth.block_number - 10000  # Start 10k blocks back if no DB
        
    try:
        result = supabase.table('onchain_sync_status').select('*').eq('chain', 'uniswap').single().execute()
        if result.data:
            return result.data['last_block']
    except:
        pass
    return w3.eth.block_number - 10000  # Start 10k blocks back if first run

def update_sync_status(block_number):
    """Update the latest processed block"""
    if not supabase:
        return
        
    try:
        supabase.table('onchain_sync_status').upsert({
            'chain': 'uniswap',
            'last_block': block_number,
            'synced_at': datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Error updating sync status: {e}")

def process_proposal_executed(event):
    """Process ProposalExecuted event"""
    if not supabase:
        return
        
    proposal_id = event['args']['proposalId']
    block = w3.eth.get_block(event['blockNumber'])
    tx = w3.eth.get_transaction(event['transactionHash'])
    
    data = {
        'proposal_id': str(proposal_id),
        'event_type': 'executed',
        'chain': 'uniswap',
        'block_number': event['blockNumber'],
        'transaction_hash': event['transactionHash'].hex(),
        'executed_at': datetime.fromtimestamp(block['timestamp']).isoformat(),
        'executor_address': tx['from']
    }
    
    try:
        supabase.table('onchain_events').insert(data).execute()
        print(f"✓ Stored execution for proposal {proposal_id}")
    except Exception as e:
        print(f"Error storing execution event: {e}")

def process_vote_cast(event):
    """Process VoteCast event"""
    if not supabase:
        return
        
    voter = event['args']['voter']
    proposal_id = event['args']['proposalId']
    support = event['args']['support']
    weight = event['args']['weight']
    block = w3.eth.get_block(event['blockNumber'])
    
    # Map support values (0=Against, 1=For, 2=Abstain)
    choice_map = {0: 'Against', 1: 'For', 2: 'Abstain'}
    
    data = {
        'proposal_id': str(proposal_id),
        'event_type': 'vote',
        'chain': 'uniswap',
        'block_number': event['blockNumber'],
        'transaction_hash': event['transactionHash'].hex(),
        'voter_address': voter.lower(),
        'vote_choice': choice_map.get(support, 'Unknown'),
        'voting_power': str(weight),
        'voted_at': datetime.fromtimestamp(block['timestamp']).isoformat()
    }
    
    try:
        supabase.table('onchain_events').insert(data).execute()
        print(f"✓ Stored vote from {voter[:8]}... on proposal {proposal_id}")
    except Exception as e:
        print(f"Error storing vote event: {e}")

def collect_events(from_block, to_block):
    """Collect events from Governor contract"""
    if not w3.is_connected():
        print("Not connected to RPC")
        return 0
        
    contract = w3.eth.contract(address=GOVERNOR_ADDRESS, abi=GOVERNOR_ABI)
    
    total_events = 0
    
    try:
        # Fetch ProposalExecuted events
        executed_filter = contract.events.ProposalExecuted.create_filter(
            fromBlock=from_block,
            toBlock=to_block
        )
        executed_events = executed_filter.get_all_entries()
        
        for event in executed_events:
            try:
                process_proposal_executed(event)
                total_events += 1
            except Exception as e:
                print(f"Error processing executed event: {e}")
        
        # Fetch VoteCast events
        vote_filter = contract.events.VoteCast.create_filter(
            fromBlock=from_block,
            toBlock=to_block
        )
        vote_events = vote_filter.get_all_entries()
        
        for event in vote_events:
            try:
                process_vote_cast(event)
                total_events += 1
            except Exception as e:
                print(f"Error processing vote event: {e}")
    except Exception as e:
        print(f"Error collecting events: {e}")
    
    return total_events

def main():
    """Main collection loop"""
    print("Starting Uniswap on-chain collector...")
    print(f"Governor: {GOVERNOR_ADDRESS}")
    print(f"Connected to Ethereum: {w3.is_connected()}")
    
    if not w3.is_connected():
        print("Cannot proceed without RPC connection")
        return
    
    last_block = get_latest_block()
    current_block = w3.eth.block_number
    
    print(f"\nSyncing from block {last_block} to {current_block}")
    
    # Process in chunks of 1000 blocks
    chunk_size = 1000
    total_events = 0
    
    for start_block in range(last_block, current_block, chunk_size):
        end_block = min(start_block + chunk_size - 1, current_block)
        
        print(f"\nProcessing blocks {start_block} - {end_block}...")
        events_count = collect_events(start_block, end_block)
        total_events += events_count
        
        update_sync_status(end_block)
        print(f"Synced to block {end_block} ({events_count} events)")
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"Sync complete!")
    print(f"Total events collected: {total_events}")
    print(f"Current block: {current_block}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
