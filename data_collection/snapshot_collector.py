"""Snapshot.org GraphQL API Collector for off-chain voting"""
import httpx
from typing import Dict, List

class SnapshotCollector:
    """Fetches off-chain voting data from Snapshot.org"""
    
    API_URL = "https://hub.snapshot.org/graphql"
    ARBITRUM_SPACE = "arbitrumfoundation.eth"
    
    async def get_proposals(self, limit: int = 20) -> List[Dict]:
        """Fetch recent proposals from Snapshot"""
        query = """
        query($space: String!, $first: Int!) {
          proposals(
            first: $first,
            where: {space: $space},
            orderBy: "created",
            orderDirection: desc
          ) {
            id
            title
            body
            choices
            start
            end
            state
            scores
            scores_total
            votes
            author
          }
        }
        """
        
        variables = {"space": self.ARBITRUM_SPACE, "first": limit}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.API_URL,
                    json={"query": query, "variables": variables},
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("proposals", [])
            except Exception as e:
                print(f"Snapshot API error: {e}")
        return []
    
    async def get_votes(self, proposal_id: str) -> List[Dict]:
        """Fetch votes for a specific proposal"""
        query = """
        query($proposal: String!) {
          votes(
            first: 1000,
            where: {proposal: $proposal}
          ) {
            id
            voter
            choice
            vp
            created
          }
        }
        """
        
        variables = {"proposal": proposal_id}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.API_URL,
                    json={"query": query, "variables": variables},
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("votes", [])
            except Exception as e:
                print(f"Error fetching votes: {e}")
        return []

if __name__ == "__main__":
    import asyncio
    
    async def test():
        collector = SnapshotCollector()
        print("Fetching Snapshot proposals...")
        proposals = await collector.get_proposals(limit=5)
        print(f"Found {len(proposals)} proposals")
        for p in proposals[:3]:
            print(f"- {p.get('title', 'Untitled')[:50]}")
    
    asyncio.run(test())
