import asyncio
from datetime import datetime
from agents.digestion.entity_extraction import EntityExtractionAgent
from agents.digestion.claim_extraction import ClaimExtractionAgent
from services.storage_service import storage_service
from schemas.item import NormalizedItem

async def main():
    # Create a dummy normalized item
    item = NormalizedItem(
        id="test_item_1",
        source="test",
        source_id="1",
        url="http://test.com",
        title="Breaking: 5 people injured in a building collapse in Mumbai.",
        text="Rescue operations are underway. The building was old.",
        timestamp=datetime.utcnow(),
        language_detected="en"
    )

    print("Testing Entity Extraction...")
    entity_agent = EntityExtractionAgent()
    enriched_item = await entity_agent.process(item)
    print(f"Entities found: {enriched_item.entities}")

    print("\nTesting Claim Extraction...")
    claim_agent = ClaimExtractionAgent()
    claims = await claim_agent.process(enriched_item)
    print(f"Claims extracted: {len(claims)}")
    for c in claims:
        print(f" - {c.text}")

    print("\nTesting Storage...")
    await storage_service.save_item(enriched_item)
    await storage_service.save_claims(claims)

if __name__ == "__main__":
    asyncio.run(main())
