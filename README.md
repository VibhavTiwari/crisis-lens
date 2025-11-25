# CrisisLens 🔍

A verification-first, math-grounded, India-first, multimodal crisis intelligence system.

## Vision
CrisisLens combats misinformation during crises by providing real-time, verified intelligence to analysts and the public.

## 📊 Implementation Status

### ✅ Completed Phases (1-12)
- **Phase 1-3**: Full ingestion pipeline (GDELT, YouTube, Reddit, WHO EARS, Google Fact Check)
- **Phase 4**: Entity & claim extraction
- **Phase 5**: Media processing (pHash, keyframes, InVID)
- **Phase 6**: Topics, novelty detection, and burst detection
- **Phase 7**: Evidence retrieval and fact-check integration
- **Phase 8**: Source reliability & corroboration scoring
- **Phase 9**: NLI veracity, harm assessment, risk scoring
- **Phase 10**: Verifier Console (FastAPI + Web UI)
- **Phase 11**: Advisory drafting, translation, public feed
- **Phase 12**: Load testing & security audit

## 🏗️ Architecture
- **Ingestion**: Multi-source data collection
- **Digestion**: NLP-based extraction & verification  
- **Verification**: Evidence-based claim assessment
- **Publishing**: Multilingual advisories

## 📁 Repository Structure
```
crisis-lens/
├── agents/          # Ingestion, digestion, publishing agents
├── services/        # Core services (language, storage, observability)
├── schemas/         # Pydantic data models
├── apps/           
│   ├── api/         # FastAPI backend
│   ├── frontend/    # Verifier console
│   └── public/      # Public feed
├── tests/           # Load tests
├── scripts/         # Security audit
└── infrastructure/  # Docker compose
```

## 🚀 Getting Started
```bash
# Install dependencies
pip install -e .

# Start infrastructure
docker-compose up -d

# Run verifier console
uvicorn apps.api.main:app --reload

# Run security audit
python scripts/security_audit.py

# Run load tests  
locust -f tests/load_test.py
```

## 🔑 Configuration
Set environment variables in `.env`:
```
GOOGLE_FACT_CHECK_KEY=your_key
YOUTUBE_API_KEY=your_key
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
OPENAI_API_KEY=your_key
```

## 🧪 Verification Scripts
- `verify_phase2.py` - Test ingestion agents
- `verify_phase4.py` - Test entity/claim extraction  
- `verify_phase7.py` - Test evidence retrieval
- `verify_phase9.py` - Test risk scoring
- `verify_phase11.py` - Test advisory drafting

## 📝 License
MIT
