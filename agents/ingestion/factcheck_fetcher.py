import aiohttp
from typing import List
from datetime import datetime
from agents.ingestion.base import IngestionAgent
from schemas.item import RawItem
from config import settings

class FactCheckFetchAgent(IngestionAgent):
    def __init__(self):
        super().__init__(name="FactCheckFetchAgent", source_name="google_fact_check")
        self.api_key = settings.GOOGLE_FACT_CHECK_KEY
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    async def fetch(self) -> List[RawItem]:
        if self.api_key == "dummy_key":
            self.log("Skipping FactCheck fetch: No API Key")
            return []

        params = {
            "key": self.api_key,
            "query": "India", # Broad query for demo
            "languageCode": "en,hi", # English and Hindi
            "pageSize": 20
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    self.log(f"Error fetching from FactCheck Tools: {response.status}")
                    return []

                data = await response.json()
                claims = data.get("claims", [])
                
                items = []
                for claim in claims:
                    # Structure: claimReview list inside claim
                    # We take the first review for simplicity or create multiple items
                    
                    claim_text = claim.get("text")
                    claim_date_str = claim.get("claimDate")
                    timestamp = datetime.utcnow()
                    if claim_date_str:
                        try:
                            timestamp = datetime.strptime(claim_date_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            pass

                    # The item represents the CLAIM itself, or the FACT CHECK?
                    # In this system, we ingest the fact-check as a source of truth/evidence, 
                    # but it can also be a RawItem.
                    
                    reviews = claim.get("claimReview", [])
                    for review in reviews:
                        url = review.get("url")
                        title = review.get("title")
                        publisher = review.get("publisher", {}).get("name")
                        
                        item = RawItem(
                            id=f"factcheck_{url}",
                            source="google_fact_check",
                            source_id=url,
                            url=url,
                            title=title or claim_text, # Fallback
                            text=claim_text,
                            author=publisher,
                            timestamp=timestamp,
                            raw_data=claim
                        )
                        items.append(item)
                
                return items
