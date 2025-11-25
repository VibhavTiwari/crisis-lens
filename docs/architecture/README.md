# CrisisLens Architecture

System architecture and design documentation.

## System Overview

CrisisLens is a distributed, event-driven platform for real-time crisis intelligence.

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Ingestion Layer                    │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   Twitter   │     RSS     │   Reddit    │    News API     │
│   Agent     │    Agent    │    Agent    │     Agent       │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬───────────┘
       │             │              │             │
       └─────────────┴──────────────┴─────────────┘
                            │
                    ┌───────▼───────┐
                    │     Kafka     │
                    │   (Streaming) │
                    └───────┬───────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
┌──────▼──────┐     ┌───────▼───────┐   ┌───────▼────────┐
│   Entity    │     │   Sentiment   │   │  Risk Scoring  │
│ Extraction  │     │   Analysis    │   │   Workflow     │
└──────┬──────┘     └───────┬───────┘   └───────┬────────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  PostgreSQL   │
                    │   (Storage)   │
                    └───────┬───────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
┌──────▼──────┐     ┌───────▼───────┐   ┌───────▼────────┐
│   FastAPI   │     │  OpenSearch   │   │     Redis      │
│    (API)    │     │   (Search)    │   │   (Cache)      │
└──────┬──────┘     └───────────────┘   └────────────────┘
       │
       ├─────────────────┬─────────────────┬──────────────┐
       │                 │                 │              │
┌──────▼──────┐   ┌──────▼──────┐  ┌──────▼──────┐  ┌────▼────┐
│   Next.js   │   │   React     │  │  WebSocket  │  │  Mobile │
│  Web App    │   │   Native    │  │   Clients   │  │   Apps  │
└─────────────┘   └─────────────┘  └─────────────┘  └─────────┘
```

## Components

### 1. Data Ingestion Layer

**Agents:**
- Twitter Agent (Twitter API v2)
- RSS Feed Agent (feedparser)
- Reddit Agent (PRAW)
- News API Agent (NewsAPI)

**Responsibilities:**
- Fetch data from sources
- Normalize data format
- Publish to Kafka topics
- Handle rate limiting
- Error recovery

### 2. Stream Processing (Kafka)

**Topics:**
- `raw-items`: Unprocessed data
- `normalized-items`: Structured data
- `claims`: Extracted claims
- `alerts`: High-risk notifications
- `user-activity`: User actions

**Consumers:**
- Workflow processors
- Real-time notification service
- Analytics aggregator

### 3. AI/ML Workflows

**LangChain Workflows:**
- Entity extraction (spaCy, GPT)
- Sentiment analysis
- Risk scoring
- Claim extraction
- Evidence gathering

**Models:**
- GPT-4 for analysis
- spaCy for NER
- Custom risk scoring ML

### 4. Data Storage

**PostgreSQL:**
- Items, claims, users
- Verification history
- Audit logs
- Relational data

**OpenSearch:**
- Full-text search
- Geospatial queries
- Analytics aggregations

**Redis:**
- Session storage
- Rate limiting
- Caching layer
- Real-time counters

### 5. API Layer (FastAPI)

**Endpoints:**
- RESTful CRUD operations
- WebSocket connections
- Server-Sent Events
- File uploads
- Authentication

**Features:**
- JWT authentication
- RBAC authorization
- Input validation
- Rate limiting
- API documentation

### 6. Frontend Applications

**Web (Next.js):**
- Server-side rendering
- Real-time updates
- Interactive dashboards
- Map visualization

**Mobile (React Native):**
- Offline-first
- Push notifications
- Camera integration
- Geolocation

## Data Flow

### Item Processing Pipeline

```
1. Agent fetches data
   ↓
2. Normalize format
   ↓
3. Publish to Kafka (raw-items)
   ↓
4. Entity extraction workflow
   ↓
5. Sentiment analysis
   ↓
6. Risk scoring
   ↓
7. Store in PostgreSQL
   ↓
8. Index in OpenSearch
   ↓
9. Broadcast via WebSocket
   ↓
10. Notify users (if high-risk)
```

### Claim Verification Flow

```
1. Extract claim from item
   ↓
2. Search for evidence
   ↓
3. Present to analyst
   ↓
4. Analyst reviews
   ↓
5. Submit verdict
   ↓
6. Update item status
   ↓
7. Notify stakeholders
   ↓
8. Log to audit trail
```

## Deployment Architecture

### Kubernetes Cluster

```
┌─────────────────────────────────────────┐
│          Load Balancer (ALB)            │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │  Ingress (NGINX)│
        └────────┬─────────┘
                 │
    ┌────────────┼────────────┐
    │                         │
┌───▼───┐               ┌─────▼──────┐
│  API  │               │  Workers   │
│  Pods │               │   Pods     │
│ (3-10)│               │    (2)     │
└───┬───┘               └─────┬──────┘
    │                         │
    └──────────┬──────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌──▼────┐
│  RDS  │  │ Redis │  │  MSK  │
│ (DB)  │  │(Cache)│  │(Kafka)│
└───────┘  └───────┘  └───────┘
```

## Security Architecture

### Authentication Flow

```
1. User → Login credentials → API
2. API → Verify → PostgreSQL
3. API → Generate JWT → User
4. User → JWT in headers → API
5. API → Verify JWT → Process request
```

### Authorization (RBAC)

**Roles:**
- Admin: Full access
- Analyst: Review and verify
- Viewer: Read-only
- API User: Limited API access

**Permissions:**
- `items:read`
- `items:write`
- `claims:verify`
- `users:manage`

## Scalability

### Horizontal Scaling

- API pods: 3-10 (auto-scale on CPU)
- Worker pods: 2+ (scale on queue depth)
- Database: Read replicas
- Cache: Redis cluster

### Performance Optimizations

- CDN for static assets
- Database connection pooling
- Query result caching
- Async processing
- Batch operations

## Monitoring & Observability

### Metrics (Prometheus)

- Request rate, latency, errors
- CPU, memory usage
- Kafka lag
- Database connections

### Logging

- Structured JSON logs
- Centralized (CloudWatch/ELK)
- Log levels: DEBUG, INFO, WARN, ERROR
- Correlation IDs

### Tracing

- Distributed tracing (Jaeger)
- Request path visualization
- Performance bottlenecks

## Technology Stack

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy
- Celery
- LangChain

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- TailwindCSS

**Data:**
- PostgreSQL 15
- Redis 7
- Kafka 3.5
- OpenSearch 2.11

**Infrastructure:**
- Docker
- Kubernetes
- Terraform
- AWS (EKS, RDS, ElastiCache)

**Monitoring:**
- Prometheus
- Grafana
- Jaeger

---

**For detailed component documentation, see individual service READMEs.**
