# CrisisLens

**From chaos to clarity, fast.**

CrisisLens is a verification-first, math-grounded, India-first, multimodal crisis intelligence system.

## Vision

Anyone, anywhere, stuck in or following a crisis should be able to open CrisisLens and quickly see:
* What actually happened.
* How sure we are, and why.
* What they should do next, in their context.

## Architecture

* **Ingestion Engine**: Fetches content from GDELT, Fact-Checks, YouTube, Reddit, etc.
* **Digestion Engine**: Extracts claims, verifies them using AI and math-grounded models.
* **Storage Engine**: Polyglot storage (Iceberg, OpenSearch, ClickHouse, Qdrant, Neo4j).
* **Publishing Engine**: Drafts and publishes clear advisories.
* **Orchestration Engine**: Coordinates agents via LangGraph.

## Repository Structure

* `apps/`: Entrypoint applications (Web, API, Console).
* `agents/`: AI Agents for ingestion, digestion, etc.
* `services/`: Shared microservices.
* `ml/`: Model training and evaluation.
* `infrastructure/`: IaC (Docker, K8s).
* `schemas/`: Data contracts.

## Getting Started

1. **Prerequisites**: Docker, Python 3.10+, Node.js 18+.
2. **Setup**:
   ```bash
   pip install poetry
   poetry install
   docker-compose up -d
   ```
