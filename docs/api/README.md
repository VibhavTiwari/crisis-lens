# CrisisLens API Documentation

Complete API reference for the CrisisLens platform.

## Base URL

```
Production: https://api.crisislens.io
Staging: https://api-staging.crisislens.io
Local: http://localhost:8000
```

## Authentication

All API requests require authentication using JWT tokens.

### Get Token

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Use Token

Include token in Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### Items

#### List Items
```http
GET /items?limit=20&offset=0&status=pending_review&search=earthquake
```

**Query Parameters:**
- `limit` (int): Results per page (default: 20, max: 100)
- `offset` (int): Pagination offset
- `status` (string): Filter by status
- `search` (string): Full-text search
- `risk_min` (float): Minimum risk score (0-1)
- `risk_max` (float): Maximum risk score (0-1)

**Response:**
```json
{
  "items": [
    {
      "id": "item_123",
      "title": "Earthquake in Japan",
      "content": "7.5 magnitude earthquake...",
      "source": "twitter",
      "risk_score": 0.85,
      "status": "verified",
      "location": "Tokyo, Japan",
      "latitude": 35.6762,
      "longitude": 139.6503,
      "created_at": "2024-01-01T00:00:00Z",
      "claims": []
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

#### Get Item
```http
GET /items/{item_id}
```

**Response:**
```json
{
  "id": "item_123",
  "title": "Earthquake in Japan",
  "content": "Full content...",
  "risk_score": 0.85,
  "entities": [
    {"text": "Tokyo", "type": "LOCATION"},
    {"text": "Japan", "type": "LOCATION"}
  ],
  "sentiment": {
    "score": -0.6,
    "label": "negative"
  },
  "claims": [
    {
      "id": "claim_456",
      "text": "7.5 magnitude earthquake",
      "verdict": "true",
      "confidence": 0.92
    }
  ]
}
```

#### Create Item
```http
POST /items
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "Breaking: Wildfire in California",
  "content": "Large wildfire reported...",
  "source": "manual",
  "url": "https://example.com/news",
  "location": "California, USA"
}
```

#### Update Item
```http
PATCH /items/{item_id}
Authorization: Bearer {token}

{
  "status": "verified",
  "notes": "Verified by multiple sources"
}
```

### Claims

#### List Claims
```http
GET /claims?item_id=item_123&verdict=uncertain
```

#### Get Claim
```http
GET /claims/{claim_id}
```

#### Verify Claim
```http
POST /claims/{claim_id}/verify
Authorization: Bearer {token}

{
  "verdict": "true",
  "confidence": 0.9,
  "evidence": [
    {
      "source": "Official Report",
      "url": "https://example.com/report",
      "text": "Evidence text"
    }
  ]
}
```

### Statistics

#### Get Stats
```http
GET /stats
```

**Response:**
```json
{
  "pending": 45,
  "in_review": 12,
  "verified": 234,
  "rejected": 8,
  "total_items": 299,
  "avg_risk_score": 0.62,
  "claims_total": 156,
  "claims_verified": 89
}
```

### WebSocket

#### Connect
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

#### Events
- `item.new` - New item created
- `item.updated` - Item status changed
- `claim.verified` - Claim verified
- `alert.high_risk` - High-risk event detected

## Rate Limiting

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Premium**: 10,000 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## Error Responses

```json
{
  "error": "not_found",
  "message": "Item not found",
  "status_code": 404
}
```

**Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## SDKs

### Python
```python
from crisis_lens import Client

client = Client(api_key="your_api_key")

# List items
items = client.items.list(limit=10, status="verified")

# Get item
item = client.items.get("item_123")

# Create item
new_item = client.items.create(
    title="New Event",
    content="Description",
    source="manual"
)
```

### JavaScript
```javascript
import { CrisisLens } from '@crisis-lens/sdk';

const client = new CrisisLens({ apiKey: 'your_api_key' });

// List items
const items = await client.items.list({ limit: 10 });

// Subscribe to updates
client.subscribe('item.new', (item) => {
  console.log('New item:', item);
});
```

## Interactive Documentation

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI.

Alternative: [http://localhost:8000/redoc](http://localhost:8000/redoc) for ReDoc.
