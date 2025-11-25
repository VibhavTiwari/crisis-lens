# CrisisLens Testing Guide

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio locust

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Structure

```
tests/
├── unit/           # Unit tests (fast, isolated)
├── integration/    # Integration tests (with services)
├── e2e/           # End-to-end tests (full workflows)
├── load/          # Load tests (Locust)
├── security/      # Security tests
└── conftest.py    # Shared fixtures
```

## Running Tests

### By Type
```bash
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests
pytest tests/e2e/              # E2E tests
pytest -m security             # Security tests only
```

### By Module
```bash
pytest tests/unit/agents/                    # All agent tests
pytest tests/unit/services/test_kafka_producer.py  # Specific file
```

### With Markers
```bash
pytest -m "not slow"           # Skip slow tests
pytest -m "unit"               # Unit tests only
pytest -m "integration"        # Integration tests
```

## Load Testing

```bash
# Start Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Open browser to http://localhost:8089
# Configure users and spawn rate
```

## Coverage

```bash
# Generate coverage report
pytest --cov=. --cov-report=term --cov-report=html

# Coverage by module
pytest --cov=agents --cov=services --cov-report=term

# Fail if coverage < 80%
pytest --cov=. --cov-fail-under=80
```

## CI/CD

Tests run automatically on:
- Push to main/develop
- Pull requests
- Pre-commit hooks

### Local Pre-commit

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Writing Tests

### Unit Test Example
```python
@pytest.mark.unit
def test_my_function():
    result = my_function(input_data)
    assert result == expected_output
```

### Integration Test Example
```python
@pytest.mark.integration
def test_api_endpoint(api_client):
    response = api_client.get("/items")
    assert response.status_code == 200
```

### Async Test Example
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## Fixtures

Common fixtures available in `conftest.py`:
- `db_session` - Database session
- `api_client` - FastAPI test client
- `mock_kafka_producer` - Mock Kafka producer
- `sample_crisis_item` - Sample test data
- `auth_headers` - Authentication headers

## Best Practices

1. **Isolation**: Unit tests should not depend on external services
2. **Mocking**: Use mocks for external APIs and services
3. **Coverage**: Aim for 80%+ coverage
4. **Speed**: Keep tests fast (< 1s per test)
5. **Clarity**: Test one thing per test
6. **Setup**: Use fixtures for common setup
7. **Cleanup**: Always cleanup resources

## Troubleshooting

### Tests fail locally
```bash
# Clear pytest cache
pytest --cache-clear

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Coverage not accurate
```bash
# Delete coverage data
rm .coverage
coverage erase

# Run tests again
pytest --cov=.
```

### Async tests failing
```bash
# Ensure pytest-asyncio installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```
