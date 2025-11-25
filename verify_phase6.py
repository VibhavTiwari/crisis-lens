import asyncio
from datetime import datetime
from agents.digestion.topic_assignment import TopicAssignmentAgent
from agents.digestion.novelty_scoring import NoveltyScoringAgent
from agents.digestion.burst_detection import BurstDetectionAgent
from schemas.item import NormalizedItem
from schemas.claim import Claim

async def main():
    item = NormalizedItem(
        id="test_topic_item",
        source="test",
        source_id="1",
        url="http://test.com",
        title="Heavy floods in Mumbai causing traffic jams.",
        text="Water logging reported in Bandra.",
        timestamp=datetime.utcnow()
    )

    print("Testing Topic Assignment...")
    topic_agent = TopicAssignmentAgent()
    item = await topic_agent.process(item)
    print(f"Topics: {item.topics}")

    print("\nTesting Burst Detection...")
    burst_agent = BurstDetectionAgent()
    # Simulate a burst
    for _ in range(6):
        await burst_agent.process(item)

    print("\nTesting Novelty Scoring (on Claims)...")
    novelty_agent = NoveltyScoringAgent()
    claims = [
        Claim(id="c1", text="Floods in Mumbai", normalized_item_id=item.id),
        Claim(id="c2", text="A very long detailed claim about the specific water levels in Bandra East.", normalized_item_id=item.id)
    ]
    claims = await novelty_agent.process_claims(claims)
    for c in claims:
        print(f"Claim '{c.text[:20]}...' Checkworthiness: {c.checkworthiness}")

if __name__ == "__main__":
    asyncio.run(main())
