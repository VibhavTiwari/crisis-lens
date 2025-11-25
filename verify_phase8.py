import asyncio
from agents.digestion.source_reliability import SourceReliabilityAgent
from agents.digestion.corroboration_scoring import CorroborationScoringAgent
from schemas.claim import Claim, Evidence

async def main():
    claims = [
        Claim(id="c1", text="Floods in Mumbai", normalized_item_id="item1")
    ]
    
    # Add some mock evidence
    claims[0].evidence = [
        Evidence(url="http://google_fact_check/1", text_snippet="True", support_score=1.0), # High reliability (0.95)
        Evidence(url="http://reddit.com/post", text_snippet="Maybe", support_score=0.0)    # Low reliability (0.4)
    ]

    print("Testing Source Reliability...")
    rel_agent = SourceReliabilityAgent()
    claims = await rel_agent.process_claims(claims)
    for ev in claims[0].evidence:
        print(f"Evidence {ev.url} reliability: {ev.source_reliability}")

    print("\nTesting Corroboration Scoring...")
    cor_agent = CorroborationScoringAgent()
    claims = await cor_agent.process_claims(claims)
    print(f"Claim Veracity Likelihood: {claims[0].veracity_likelihood}")
    # Expected: 
    # Ev1: 1.0 * 0.95 = 0.95
    # Ev2: 0.0 * 0.4 = 0.0
    # Sum = 0.95, Total Weight = 1.35
    # Score = 0.95 / 1.35 = 0.703
    # Veracity = (0.703 + 1) / 2 = 0.85

if __name__ == "__main__":
    asyncio.run(main())
