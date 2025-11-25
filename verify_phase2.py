import asyncio
from agents.ingestion.gdelt_fetcher import GDELTFetchAgent
from agents.ingestion.factcheck_fetcher import FactCheckFetchAgent
from agents.ingestion.youtube_fetcher import YouTubeFetchAgent
from services.normalization_service import normalization_service
from schemas.item import RawItem

async def main():
    print("Testing GDELT Fetcher...")
    gdelt = GDELTFetchAgent()
    # GDELT doesn't need a key, so this might actually fetch something if network allows
    # But we'll just check if it runs without crashing
    try:
        items = await gdelt.fetch()
        print(f"GDELT fetched {len(items)} items.")
        if items:
            norm = normalization_service.normalize_item(items[0])
            print(f"Normalized item language: {norm.language_detected}")
    except Exception as e:
        print(f"GDELT failed: {e}")

    print("\nTesting FactCheck Fetcher...")
    fc = FactCheckFetchAgent()
    items = await fc.fetch() # Should return empty list due to dummy key
    print(f"FactCheck fetched {len(items)} items.")

    print("\nTesting YouTube Fetcher...")
    yt = YouTubeFetchAgent()
    items = await yt.fetch() # Should return empty list due to dummy key
    print(f"YouTube fetched {len(items)} items.")

if __name__ == "__main__":
    asyncio.run(main())
