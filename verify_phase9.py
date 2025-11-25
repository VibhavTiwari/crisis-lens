import asyncio
from agents.digestion.nli_veracity import NliVeracityAgent
from agents.digestion.harm_assessment import HarmAssessmentAgent
from agents.digestion.risk_scoring import RiskScoringAgent
from schemas.claim import Claim

async def main():
    claims = [
        Claim(
            id="c1", 
            text="Drink bleach to cure the virus.", 
            normalized_item_id="item1",
            veracity_likelihood=0.1, # Likely false
            checkworthiness=0.8
        ),
        Claim(
            id="c2", 
            text="The sky is blue.", 
            normalized_item_id="item2",
            veracity_likelihood=0.95, # Likely true
            checkworthiness=0.1
        )
    ]

    print("Testing Harm Assessment...")
    harm_agent = HarmAssessmentAgent()
    claims = await harm_agent.process_claims(claims)
    print(f"Claim 1 Harm: {claims[0].harm_potential}") # Should be high (drink/cure)
    print(f"Claim 2 Harm: {claims[1].harm_potential}") # Should be low

    print("\nTesting NLI Veracity...")
    nli_agent = NliVeracityAgent()
    claims = await nli_agent.process_claims(claims)
    # Claim 1 veracity might drop slightly or stay low
    print(f"Claim 1 Veracity: {claims[0].veracity_likelihood}")

    print("\nTesting Risk Scoring...")
    risk_agent = RiskScoringAgent()
    claims = await risk_agent.process_claims(claims)
    print(f"Claim 1 Risk: {claims[0].risk_score}") # Should be high
    print(f"Claim 2 Risk: {claims[1].risk_score}") # Should be low

if __name__ == "__main__":
    asyncio.run(main())
