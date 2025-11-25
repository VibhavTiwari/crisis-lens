import aiohttp
from typing import List
from datetime import datetime
from agents.ingestion.base import IngestionAgent
from schemas.item import RawItem, MediaItem
from config import settings

class YouTubeFetchAgent(IngestionAgent):
    def __init__(self):
        super().__init__(name="YouTubeFetchAgent", source_name="youtube")
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3/search"

    async def fetch(self) -> List[RawItem]:
        if self.api_key == "dummy_key":
            self.log("Skipping YouTube fetch: No API Key")
            return []

        params = {
            "part": "snippet",
            "q": "crisis India",
            "type": "video",
            "order": "date",
            "maxResults": 20,
            "key": self.api_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    self.log(f"Error fetching from YouTube: {response.status}")
                    return []

                data = await response.json()
                items_data = data.get("items", [])
                
                items = []
                for vid in items_data:
                    snippet = vid.get("snippet", {})
                    video_id = vid.get("id", {}).get("videoId")
                    
                    if not video_id:
                        continue

                    timestamp_str = snippet.get("publishedAt")
                    timestamp = datetime.utcnow()
                    if timestamp_str:
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            pass

                    media = []
                    thumbnails = snippet.get("thumbnails", {})
                    high_res = thumbnails.get("high", {}).get("url")
                    if high_res:
                        media.append(MediaItem(url=high_res, type="image"))
                    
                    # Video URL
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    media.append(MediaItem(url=video_url, type="video"))

                    item = RawItem(
                        id=f"youtube_{video_id}",
                        source="youtube",
                        source_id=video_id,
                        url=video_url,
                        title=snippet.get("title"),
                        text=snippet.get("description"),
                        author=snippet.get("channelTitle"),
                        timestamp=timestamp,
                        media=media,
                        raw_data=vid
                    )
                    items.append(item)
                
                return items
