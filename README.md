# CrisisLens - Crisis Intelligence Verification Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

CrisisLens is a production-ready, AI-powered crisis intelligence verification platform that processes, verifies, and disseminates crisis information at scale.

## 🎯 Overview

CrisisLens provides **verification-first crisis intelligence** through:
- 🔍 **Multi-source ingestion** (Twitter, Reddit, YouTube, webhooks)
- 🤖 **AI-powered verification** (NLI, evidence retrieval, fact-checking)
- 📊 **Risk scoring** (composite scores from 8 factors)
- 🌐 **Multi-language support** (translation to 5 Indian languages)
- ⚡ **Real-time processing** (LangGraph workflow orchestration)
- 📈 **Advanced analytics** (geospatial, temporal, social network)

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     Ingestion Layer                         │
│  Twitter │ Reddit │ YouTube │ RSS │ Webhooks │ Screenshots │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│                 Normalization & Enrichment                  │
│     Language Detection │ Media Download │ Deduplication    │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│                   LangGraph Workflow                        │
│  Entity → Claims → Topics → Evidence → NLI → Risk → Advisory│
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│                   Storage & Indexing                        │
│  PostgreSQL │ OpenSearch │ Qdrant │ Neo4j │ ClickHouse     │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│                      Publishing                             │
│     Web Dashboard │ Mobile App │ API │ Notifications       │
└────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Kubernetes cluster (for production)
- FFmpeg (for media processing)
- Tesseract OCR (for image text extraction)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/crisis-lens.git
cd crisis-lens

# 2. Install dependencies
pip install -e .

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Start databases
docker-compose up -d

# 5. Initialize databases
python scripts/init_databases.py
python scripts/init_roles.py

# 6. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 7. Run API
uvicorn apps.api.main:app --reload

# 8. Access dashboard
# Open http://localhost:8000
```

### Production Deployment

```bash
# Deploy to Kubernetes
bash scripts/deploy.sh production

# Verify deployment
kubectl get pods -n crisislen
```

## 📚 Documentation

- [**API Documentation**](./docs/API.md) - Complete REST API reference
- [**User Guide**](./docs/USER_GUIDE.md) - End-user documentation
- [**Deployment Guide**](./docs/DEPLOYMENT.md) - Production deployment
- [**Architecture**](./docs/ARCHITECTURE.md) - System architecture
- [**Security**](./docs/SECURITY.md) - Security best practices
- [**Performance**](./docs/PERFORMANCE.md) - Tuning guide

## 🔑 Key Features

### Verification Pipeline
1. **Entity Extraction** - Identify people, organizations, locations
2. **Claim Extraction** - Extract verifiable claims
3. **Evidence Retrieval** - Google Fact Check API + semantic search
4. **NLI Verification** - DeBERTa-based natural language inference
5. **Risk Scoring** - 8-factor composite score
6. **Advisory Drafting** - GPT-4 powered summaries
7. **Translation** - Google Translate to 5 languages

### ML Models
- **Sentence Transformers** - Text embeddings (384-dim)
- **BERTopic** - Dynamic topic modeling
- **DeBERTa** - Natural language inference  
- **CLIP** - Multimodal image-text understanding
- **Whisper** - Speech-to-text transcription
- **GPT-4/Claude** - Advisory generation

### Analytics
- **Temporal Reasoning** - Timeline extraction
- **Geospatial Analysis** - Location clustering
- **Social Network** - Influence & community detection
- **Sentiment Analysis** - VADER + urgency detection

### Infrastructure
- **Kubernetes** - Container orchestration
- **Horizontal Scaling** - 3-20 pods (HPA)
- **Prometheus** - Metrics & alerting
- **Grafana** - Dashboards
- **Jaeger** - Distributed tracing

## 📊 Tech Stack

**Backend:**
- FastAPI, Pydantic, SQLAlchemy
- LangGraph (workflow orchestration)
- Celery (async tasks)

**ML/AI:**
- Transformers, Sentence Transformers, BERTopic
- OpenAI GPT-4, Anthropic Claude
- Google Cloud Translate, Whisper

**Databases:**
- PostgreSQL (relational)
- OpenSearch (full-text search)
- Qdrant (vector similarity)
- Neo4j (graph relationships)
- ClickHouse (time-series analytics)
- Redis (caching & sessions)

**Infrastructure:**
- Kubernetes, Helm, Docker
- Prometheus, Grafana, Jaeger
- NGINX Ingress, cert-manager

## 🔒 Security

- **Authentication**: OAuth 2.0 (Google/GitHub) + JWT
- **Authorization**: Role-based access control (RBAC)
- **API Keys**: SHA-256 hashed with expiration
- **Audit Logging**: All actions logged to PostgreSQL + ClickHouse
- **Rate Limiting**: Redis-backed rate limiter
- **TLS**: Let's Encrypt auto-renewal

## 📈 Performance

- **Throughput**: 1000+ items/hour
- **Latency**: <2s per item (p95)
- **Scalability**: Horizontal scaling to 20+ pods
- **Caching**: Redis for frequent queries
- **Batch Processing**: Parallel claim verification

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests  
pytest tests/integration/ -v

# All tests
pytest -v
```

## 📦 Project Structure

```
crisis-lens/
├── apps/
│   ├── api/           # FastAPI application
│   └── frontend/      # Web dashboard
├── agents/            # Verification agents
│   ├── ingestion/
│   ├── digestion/
│   ├── scoring/
│   └── publishing/
├── ml/                # ML models
│   ├── models/        # Production models
│   ├── media/         # Media processing
│   └── nlp/           # Advanced NLP
├── workflows/         # LangGraph workflows
├── services/          # Core services
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── infrastructure/    # K8s & Helm
│   ├── k8s/
│   ├── helm/
│   └── monitoring/
├── scripts/           # Utility scripts
├── tests/             # Test suites
└── docs/              # Documentation
```

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details.

---

**Built with ❤️ for crisis response teams worldwide**
