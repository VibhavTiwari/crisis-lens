import asyncio
from datetime import datetime
from agents.publishing.advisory_drafting import AdvisoryDraftingAgent
from agents.publishing.translation import AdvisoryTranslationAgent
from schemas.item import NormalizedItem
from schemas.claim import Claim

async def main():
    # Mock verified item
    item = NormalizedItem(
        id="item_verified_1",
        source="test",
        source_id="1",
        url="http://test.com",
        title="Floods in Mumbai",
        text="Heavy rains have caused water logging.",
        timestamp=datetime.utcnow(),
        risk_score=0.9,
        claims=[
            Claim(id="c1", text="Trains stopped.", normalized_item_id="item_verified_1", veracity_likelihood=0.95),
            Claim(id="c2", text="Aliens caused rain.", normalized_item_id="item_verified_1", veracity_likelihood=0.05)
        ]
    )

    print("Testing Advisory Drafting...")
    draft_agent = AdvisoryDraftingAgent()
    advisory = await draft_agent.process(item)
    print(f"Advisory Title: {advisory.title}")
    print(f"Summary Preview:\n{advisory.summary}")
    print(f"Action Preview:\n{advisory.narrative_action}")

    print("\nTesting Translation...")
    trans_agent = AdvisoryTranslationAgent()
    advisory = await trans_agent.process(advisory)
    print(f"Translations available: {list(advisory.translations.keys())}")
    print(f"Hindi Title: {advisory.translations['hi']['title']}")

if __name__ == "__main__":
    asyncio.run(main())
