import asyncio
from datetime import datetime
from agents.digestion.media_extraction import MediaExtractionAgent
from agents.digestion.keyframe_extraction import KeyframeExtractionAgent
from agents.digestion.invid_verification import InvidVerificationAgent
from schemas.item import NormalizedItem, MediaItem

async def main():
    # Create a dummy item with media
    item = NormalizedItem(
        id="test_media_item",
        source="test",
        source_id="1",
        url="http://test.com",
        timestamp=datetime.utcnow(),
        media=[
            MediaItem(url="http://test.com/image.jpg", type="image"),
            MediaItem(url="http://test.com/video.mp4", type="video")
        ]
    )

    print("Testing Media Extraction (Hashing)...")
    media_agent = MediaExtractionAgent()
    item = await media_agent.process(item)
    print(f"Media count: {len(item.media)}")
    print(f"Image pHash: {item.media[0].phash}")

    print("\nTesting Keyframe Extraction...")
    keyframe_agent = KeyframeExtractionAgent()
    item = await keyframe_agent.process(item)
    print(f"Media count (after keyframes): {len(item.media)}")
    # Should have 3 items: image, video, keyframe
    
    print("\nTesting InVID Verification...")
    invid_agent = InvidVerificationAgent()
    item = await invid_agent.process(item)
    print(f"Video metadata: {item.media[1].metadata}")

if __name__ == "__main__":
    asyncio.run(main())
