import asyncio
from agents.digestion.evidence_retrieval import EvidenceRetrievalAgent
from agents.digestion.factcheck_lookup import FactCheckLookupAgent
from schemas.claim import Claim

async def main():
    claims = [
        Claim(id="c1", text="Floods in Mumbai are caused by cloudburst.", normalized_item_id="item1"),
        Claim(id="c2", text="Alien spaceship landed in Delhi.", normalized_item_id="item2")
    ]

    print("Testing Evidence Retrieval...")
    ev_agent = EvidenceRetrievalAgent()
    claims = await ev_agent.process_claims(claims)
    print(f"Claim 1 evidence count: {len(claims[0].evidence)}")
    print(f"Claim 1 evidence snippet: {claims[0].evidence[0].text_snippet}")

    print("\nTesting Fact-Check Lookup...")
    fc_agent = FactCheckLookupAgent()
    claims = await fc_agent.process_claims(claims)
    # Claim 1 has "Mumbai", so it should get a mock fact-check
    print(f"Claim 1 evidence count (after FC lookup): {len(claims[0].evidence)}")
    if len(claims[0].evidence) > 1:
        print(f"Claim 1 FC snippet: {claims[0].evidence[1].text_snippet}")

if __name__ == "__main__":
    asyncio.run(main())
