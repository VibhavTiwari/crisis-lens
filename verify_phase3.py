import asyncio
from agents.ingestion.reddit_fetcher import RedditFetchAgent
from agents.ingestion.who_ears_fetcher import WhoEarsFetchAgent
from services.observability import observability_service

async def main():
    print("Testing Reddit Fetcher...")
    reddit = RedditFetchAgent()
    try:
        items = await reddit.fetch()
        print(f"Reddit fetched {len(items)} items.")
    except Exception as e:
        print(f"Reddit failed: {e}")

    print("\nTesting WHO EARS Fetcher...")
    who = WhoEarsFetchAgent()
    try:
        items = await who.fetch()
        print(f"WHO EARS fetched {len(items)} items.")
        if items:
            print(f"Sample item title: {items[0].title}")
    except Exception as e:
        print(f"WHO EARS failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
