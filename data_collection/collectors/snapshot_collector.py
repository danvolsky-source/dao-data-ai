#!/usr/bin/env python3
"""
Snapshot Collector for Arbitrum DAO
Collects proposal and vote data from Snapshot GraphQL API
"""

import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client

# Configuration
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"
ARBITRUM_SPACE = "arbitrumfoundation.eth"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_proposals(space: str = ARBITRUM_SPACE, limit: int = 1000, skip: int = 0) -> List[Dict]:
    """
    Fetch proposals from Snapshot GraphQL API
    """
    query = """
    query Proposals($space: String!, $first: Int!, $skip: Int!) {
      proposals(
        where: { space: $space }
        first: $first
        skip: $skip
        orderBy: "created"
        orderDirection: desc
      ) {
        id
        ipfs
        title
        body
        start
        end
        snapshot
        state
        author
        created
        choices
        scores
        scores_total
        votes
        quorum
        type
        strategies {
          name
          params
        }
      }
    }
    """
    
    variables = {
        "space": space,
        "first": limit,
        "skip": skip
    }
    
    try:
        response = requests.post(
            SNAPSHOT_API_URL,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
            return []
        
        return data.get("data", {}).get("proposals", [])
    except Exception as e:
        print(f"Error fetching proposals: {e}")
        return []

def fetch_votes(proposal_id: str, limit: int = 10000, skip: int = 0) -> List[Dict]:
    """
    Fetch votes for a specific proposal
    """
    query = """
    query Votes($proposal: String!, $first: Int!, $skip: Int!) {
      votes(
        where: { proposal: $proposal }
        first: $first
        skip: $skip
        orderBy: "created"
        orderDirection: desc
      ) {
        id
        voter
        created
        choice
        vp
        reason
      }
    }
    """
    
    variables = {
        "proposal": proposal_id,
        "first": limit,
        "skip": skip
    }
    
    try:
        response = requests.post(
            SNAPSHOT_API_URL,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
            return []
        
        return data.get("data", {}).get("votes", [])
    except Exception as e:
        print(f"Error fetching votes for {proposal_id}: {e}")
        return []

def store_proposal(proposal: Dict) -> bool:
    """
    Store proposal in Supabase
    """
    try:
        data = {
            "proposal_id": proposal["id"],
            "title": proposal["title"],
            "description": proposal.get("body", ""),
            "proposer_address": proposal["author"],            "voting_start": datetime.fromtimestamp(proposal["start"]).isoformat(),
            "voting_end": datetime.fromtimestamp(proposal["end"]).isoformat(),
            "snapshot_block": proposal.get("snapshot"),
            "status": proposal["state"],
            "source": "snapshot",        }
        
        result = supabase.table("proposals").upsert(data, on_conflict="proposal_id").execute()
        return True    except Exception as e:
        print(f"Error storing proposal {proposal['id']}: {e}")
        return False

def store_vote(vote: Dict, proposal_id: str) -> bool:
    """
    Store vote in Supabase
    """
    try:
        data = {
            "vote_id": vote["id"],
            "proposal_id": proposal_id,
            "voter": vote["voter"],
            "choice": vote.get("choice") if isinstance(vote.get("choice"), int) else None,
            "choice_weights": vote.get("choice") if isinstance(vote.get("choice"), dict) else None,
            "voting_power": vote["vp"],
            "reason": vote.get("reason"),
            "created_at": datetime.fromtimestamp(vote["created"]).isoformat(),
        }
        
        result = supabase.table("votes").upsert(data, on_conflict="vote_id").execute()        return True
    except Exception as e:
        print(f"Error storing vote {vote['id']}: {e}")
        return False

def collect_all_proposals() -> int:
    """
    Collect all proposals from Arbitrum Snapshot space
    """
    print(f"Starting collection for {ARBITRUM_SPACE}...")
    
    total_proposals = 0
    skip = 0
    batch_size = 1000
    
    while True:
        proposals = fetch_proposals(space=ARBITRUM_SPACE, limit=batch_size, skip=skip)
        
        if not proposals:
            break
        
        for proposal in proposals:
            if store_proposal(proposal):
                total_proposals += 1
                print(f"Stored proposal: {proposal['id']} - {proposal['title'][:60]}...")
            
            # Rate limiting: 1 request per second
            time.sleep(1)
        
        skip += batch_size
        print(f"Processed {total_proposals} proposals so far...")
        
        # Break if we got fewer results than requested (last page)
        if len(proposals) < batch_size:
            break
    
    print(f"\nTotal proposals collected: {total_proposals}")
    return total_proposals

def collect_votes_for_proposal(proposal_id: str) -> int:
    """
    Collect all votes for a specific proposal
    """
    print(f"Collecting votes for proposal {proposal_id}...")
    
    total_votes = 0
    skip = 0
    batch_size = 10000
    
    while True:
        votes = fetch_votes(proposal_id, limit=batch_size, skip=skip)
        
        if not votes:
            break
        
        for vote in votes:
            if store_vote(vote, proposal_id):
                total_votes += 1
        
        skip += batch_size
        
        # Break if we got fewer results than requested (last page)
        if len(votes) < batch_size:
            break
        
        # Rate limiting
        time.sleep(1)
    
    print(f"Collected {total_votes} votes for proposal {proposal_id}")
    return total_votes

def collect_all_votes() -> int:
    """
    Collect votes for all proposals in database
    """
    print("Fetching proposals from database...")
    
    try:
        result = supabase.table("proposals").select("proposal_id").execute()
        proposals = result.data
        
        total_votes = 0
        for proposal in proposals:
            votes_count = collect_votes_for_proposal(proposal["proposal_id"])
            total_votes += votes_count
            time.sleep(1)  # Rate limiting
        
        print(f"\nTotal votes collected: {total_votes}")
        return total_votes
    except Exception as e:
        print(f"Error collecting votes: {e}")
        return 0

def main():
    """
    Main entry point
    """
    print("=" * 60)
    print("Arbitrum DAO Snapshot Collector")
    print("=" * 60)
    
    # Collect proposals
    proposals_count = collect_all_proposals()
    
    # Collect votes
    if proposals_count > 0:
        print("\n" + "=" * 60)
        votes_count = collect_all_votes()
        print("=" * 60)
        print(f"\nCollection complete!")
        print(f"Proposals: {proposals_count}")
        print(f"Votes: {votes_count}")
    else:
        print("No proposals found to collect votes for.")

if __name__ == "__main__":
    main()
