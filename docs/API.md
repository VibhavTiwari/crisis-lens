# CrisisLens API Documentation

## Base URL
```
Production: https://api.crisislen.example.com
Development: http://localhost:8000
```

## Authentication

### JWT Bearer Token
```http
Authorization: Bearer <access_token>
```

### API Key (Alternative)
```http
X-API-Key: <your_api_key>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "user",
  "password": "securepass123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "username": "user",
  "roles": ["verifier"]
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Workflows

#### Start Verification Workflow
```http
POST /workflows/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "raw_item": {
    "id": "item_123",
    "source": "twitter",
    "source_id": "1234567890",
    "url": "https://twitter.com/user/status/123",
    "title": "Breaking news",
    "text": "Flood reported in Mumbai",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "message": "Workflow started successfully"
}
```

#### Get Workflow Status
```http
GET /workflows/{workflow_id}/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "workflow_id": "wf_abc123",
  "status": "running",
  "risk_score": 0.75,
  "needs_human_review": true,
  "human_review_status": "pending",
  "errors": [],
  "started_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:15Z"
}
```

#### Resume Workflow (After Human Review)
```http
POST /workflows/{workflow_id}/resume
Authorization: Bearer <token>
Content-Type: application/json

{
  "human_decision": "approved",
  "feedback": "Verified with additional sources"
}
```

#### Cancel Workflow
```http
POST /workflows/{workflow_id}/cancel
Authorization: Bearer <token>
```

### Items

#### List Items
```http
GET /api/items?status=pending_review&limit=20&offset=0
Authorization: Bearer <token>
```

**Query Parameters:**
- `status`: Filter by status (pending_review, verified_true, verified_false)
- `limit`: Number of items (default: 20, max: 100)
- `offset`: Pagination offset
- `risk_min`: Minimum risk score (0-1)
- `risk_max`: Maximum risk score (0-1)

**Response:**
```json
{
  "items": [
    {
      "id": "item_123",
      "title": "Flood in Mumbai",
      "text": "Heavy rains...",
      "risk_score": 0.85,
      "status": "pending_review",
      "topics": ["flooding", "weather"],
      "claims": [
        {
          "id": "claim_1",
          "text": "100mm rain in 2 hours",
          "veracity_likelihood": 0.75
        }
      ],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

#### Get Item Details
```http
GET /api/items/{item_id}
Authorization: Bearer <token>
```

#### Update Item Status
```http
POST /api/items/{item_id}/verify
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "verified_true",
  "analyst_notes": "Confirmed by official sources"
}
```

### Claims

#### List Claims
```http
GET /api/claims?veracity_min=0.5&limit=20
Authorization: Bearer <token>
```

#### Get Claim Details
```http
GET /api/claims/{claim_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "claim_123",
  "text": "100mm rainfall in Mumbai",
  "veracity_likelihood": 0.75,
  "evidence": [
    {
      "source": "IMD Official",
      "text": "Mumbai recorded 95mm rainfall",
      "support_score": 0.8,
      "url": "https://imd.gov.in/..."
    }
  ],
  "risk_factors": {
    "source_reliability": 0.9,
    "evidence_quality": 0.75
  }
}
```

### Advisories

#### List Advisories
```http
GET /api/advisories?status=published&limit=20
Authorization: Bearer <token>
```

#### Get Advisory
```http
GET /api/advisories/{advisory_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "adv_123",
  "title": "Crisis Advisory: Mumbai Floods",
  "summary": "Heavy rainfall has caused flooding...",
  "narrative_what_happened": "On January 15, 2024...",
  "narrative_verified": "Weather authorities confirm...",
  "narrative_action": "Residents should avoid...",
  "status": "pub lished",
  "translations": {
    "hi": {...},
    "mr": {...}
  },
  "published_at": "2024-01-15T11:00:00Z"
}
```

### API Keys

#### Create API Key
```http
POST /auth/api-keys
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Production API Key",
  "expires_in_days": 90
}
```

**Response:**
```json
{
  "id": "key_abc123",
  "name": "Production API Key",
  "key": "cls_3x4mpl3_k3y_0nly_sh0wn_0nc3",
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2024-04-15T10:00:00Z"
}
```

⚠️ **Important**: The `key` field is only shown once. Store it securely!

#### List API Keys
```http
GET /auth/api-keys
Authorization: Bearer <token>
```

#### Revoke API Key
```http
DELETE /auth/api-keys/{key_id}
Authorization: Bearer <token>
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "request_id": "req_abc123"
}
```

## Rate Limits

- **Authenticated**: 1000 requests/hour
- **Unauthenticated**: 100 requests/hour
- **Workflow starts**: 50/hour per user

## Webhooks

Configure webhooks to receive real-time notifications:

```http
POST /webhooks/configure
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["advisory.published", "item.high_risk"],
  "secret": "your_webhook_secret"
}
```

**Webhook Payload:**
```json
{
  "event": "advisory.published",
  "timestamp": "2024-01-15T11:00:00Z",
  "data": {
    "advisory_id": "adv_123",
    "title": "Crisis Advisory: Mumbai Floods"
  },
  "signature": "sha256=..."
}
```

## SDKs

### Python
```python
from crisislen import CrisisLensClient

client = CrisisLensClient(api_key="your_api_key")

# Start workflow
workflow = client.workflows.start({
    "source": "twitter",
    "text": "Breaking news..."
})

# Check status
status = client.workflows.get_status(workflow.id)
```

### JavaScript
```javascript
import { CrisisLens } from '@crisislen/sdk';

const client = new CrisisLens({ apiKey: 'your_api_key' });

// Start workflow
const workflow = await client.workflows.start({
  source: 'twitter',
  text: 'Breaking news...'
});
```

## OpenAPI Spec

Download complete OpenAPI 3.0 specification:
```
GET /openapi.json
```

## Support

- Email: api-support@crisislen.example.com
- Slack: crisislen-community.slack.com
- Status: status.crisislen.example.com
