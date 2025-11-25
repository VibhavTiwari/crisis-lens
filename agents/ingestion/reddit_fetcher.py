import aiohttp
from typing import List
from datetime import datetime
from agents.ingestion.base import IngestionAgent
from schemas.item import RawItem, MediaItem
from config import settings
from services.observability import observability_service

class RedditFetchAgent(IngestionAgent):
    def __init__(self):
        super().__init__(name="RedditFetchAgent", source_name="reddit")
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        # Note: In a real app, we'd use PRAW (Python Reddit API Wrapper)
        # For this implementation, we'll use a direct HTTP request to Reddit's public JSON endpoints
        # or mock it if credentials are dummy.
        self.base_url = "https://www.reddit.com/r"

    async def fetch(self) -> List[RawItem]:
        if self.client_id == "dummy_id":
            observability_service.log_info("Skipping Reddit fetch: No Client ID")
            return []

        # Example: Fetching from r/india
        subreddit = "india"
        url = f"{self.base_url}/{subreddit}/search.json"
        params = {
            "q": "crisis OR flood OR disaster",
            "restrict_sr": "1",
            "sort": "new",
            "limit": "20"
        }
        headers = {"User-Agent": "CrisisLens/0.1"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    observability_service.log_error(f"Error fetching from Reddit: {response.status}")
                    return []

                data = await response.json()
                children = data.get("data", {}).get("children", [])
                
                items = []
                for child in children:
                    post = child.get("data", {})
                    
                    # Reddit timestamp is UTC epoch
                    created_utc = post.get("created_utc")
                    timestamp = datetime.utcnow()
                    if created_utc:
                        timestamp = datetime.utcfromtimestamp(created_utc)

                    media = []
                    if post.get("url") and post.get("url").endswith(('.jpg', '.png', '.jpeg')):
                        media.append(MediaItem(url=post.get("url"), type="image"))
                    
                    item = RawItem(
                        id=f"reddit_{post.get('id')}",
                        source="reddit",
                        source_id=post.get("id"),
                        url=f"https://reddit.com{post.get('permalink')}",
                        title=post.get("title"),
                        text=post.get("selftext"),
                        author=post.get("author"),
                        timestamp=timestamp,
                        media=media,
                        raw_data=post
                    )
                    items.append(item)
                
                return items
