# Phase 15: Authentication & Authorization - Complete!

## Components Implemented

### 1. JWT Token Management (`apps/api/auth/jwt.py`)
- Password hashing with bcrypt
- Access token generation (30 min expiry)
- Refresh token generation (7 day expiry)
- Token verification and decoding
- Password verification

### 2. OAuth 2.0 Integration (`apps/api/auth/oauth.py`)
- Google OAuth provider
- GitHub OAuth provider
- User info extraction
- Profile management

### 3. RBAC - Role-Based Access Control (`apps/api/auth/rbac.py`)
- `get_current_user()` - Extract user from JWT
- `require_roles()` - Enforce role requirements
- `require_permission()` - Enforce granular permissions
- `verify_api_key()` - API key authentication
- Token blacklist checking

### 4. API Key Management (`apps/api/auth/api_keys.py`)
- Generate secure API keys
- Hash keys for storage (SHA-256)
- Set expiration dates
- Revoke keys
- Track last usage

### 5. Audit Logging (`services/audit_service.py`)
- Log all user actions to PostgreSQL
- Log analytics to ClickHouse
- Track:
  - Login/logout
  - Claim verification
  - Advisory publishing
  - API key creation/revocation
  - Resource modifications

### 6. Session Management (`apps/api/auth/sessions.py`)
- Redis-backed sessions
- Create/read/update/delete sessions
- Session refresh (TTL extension)
- Automatic expiration

### 7. Authentication Router (`apps/api/routers/auth.py`)
Endpoints:
- `POST /auth/register` - User registration
- `POST /auth/login` - Email/password login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `GET /auth/google/login` - Initiate Google OAuth
- `GET /auth/google/callback` - Handle Google callback
- `POST /auth/api-keys` - Create API key
- `GET /auth/api-keys` - List user's API keys
- `DELETE /auth/api-keys/{id}` - Revoke API key
- `GET /auth/users` - List users (admin only)

### 8. Database Models
Already created in Phase 13:
- `User` - User accounts
- `Role` - User roles (admin, analyst, verifier, public)
- `Permission` - Fine-grained permissions
- `APIKey` - API key storage
- `AuditLog` - Audit trail

### 9. Role Initialization (`scripts/init_roles.py`)
Creates 4 default roles with permissions:
- **Admin**: Full system access
- **Analyst**: Verify claims, draft & publish advisories
- **Verifier**: Verify claims only
- **Public**: Read-only access

## Configuration
Added to `config.py`:
- `SECRET_KEY` - JWT signing key
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`

## Testing
- Integration tests in `tests/integration/test_auth.py`
- Tests for:
  - Registration
  - Login/logout
  - Token refresh
  - Current user retrieval
  - API key management
  - Permission checks

## Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Access protected endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Create API key
```bash
curl -X POST http://localhost:8000/auth/api-keys \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "expires_in_days": 90
  }'
```

### Use in code
```python
from fastapi import Depends
from apps.api.auth.rbac import get_current_user, require_permission

@app.post("/items")
async def create_item(
    user: User = Depends(require_permission("items", "create"))
):
    # Only users with "create" permission on "items" can access
    ...
```

## Security Features
- ✅ Password hashing (bcrypt)
- ✅ JWT with expiration
- ✅ Refresh token rotation
- ✅ Token blacklisting (revocation)
- ✅ API key expiration
- ✅ Rate limiting support (Redis)
- ✅ Audit logging
- ✅ Session management
- ✅ Role-based access control
- ✅ Permission-based access control
- ✅ OAuth 2.0 integration

## Setup Instructions

1. **Initialize database**
```bash
python scripts/init_databases.py
```

2. **Initialize roles and permissions**
```bash
python scripts/init_roles.py
```

3. **Set environment variables**
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

4. **Run tests**
```bash
pytest tests/integration/test_auth.py -v
```

5. **Start API**
```bash
uvicorn apps.api.main:app --reload
```

## Next Steps (Phase 16)
Implement LangGraph orchestration for agent workflows.
