import aiohttp
from typing import List, Dict, Any
from datetime import datetime
from agents.ingestion.base import IngestionAgent
from schemas.item import RawItem, MediaItem

class GDELTFetchAgent(IngestionAgent):
    def __init__(self):
        super().__init__(name="GDELTFetchAgent", source_name="gdelt")
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    async def fetch(self) -> List[RawItem]:
        # Example query: fetching recent news about "crisis" or "disaster" in India
        # In a real scenario, this query would be dynamic
        params = {
            "query": "(crisis OR disaster OR flood OR earthquake) sourcecountry:IN",
            "mode": "artlist",
            "maxrecords": "50",
            "format": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    self.log(f"Error fetching from GDELT: {response.status}")
                    return []
                
                data = await response.json()
                articles = data.get("articles", [])
                
                items = []
                for art in articles:
                    # GDELT 2.0 JSON format mapping
                    # url, title, seendate, socialimage, domain, language, sourcegeography
                    
                    # Parse timestamp (GDELT format: YYYYMMDDHHMMSS)
                    seendate = art.get("seendate")
                    timestamp = datetime.utcnow()
                    if seendate:
                        try:
                            timestamp = datetime.strptime(seendate, "%Y%m%dT%H%M%SZ")
                        except ValueError:
                            pass # Fallback to now

                    media = []
                    if art.get("socialimage"):
                        media.append(MediaItem(
                            url=art.get("socialimage"),
                            type="image"
                        ))

                    item = RawItem(
                        id=f"gdelt_{art.get('url')}", # Simple ID generation
                        source="gdelt",
                        source_id=art.get("url"),
                        url=art.get("url"),
                        title=art.get("title"),
                        text=None, # GDELT API doesn't give full text, need to scrape separately if needed
                        timestamp=timestamp,
                        language_hint=art.get("language"),
                        media=media,
                        raw_data=art
                    )
                    items.append(item)
                
                return items
