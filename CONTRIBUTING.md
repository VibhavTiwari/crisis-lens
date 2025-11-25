# Contributing to CrisisLens

Thank you for your interest in contributing to CrisisLens! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Constructive feedback only
- Focus on the issue, not the person
- Help create a welcoming environment

## Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/crisis-lens.git
cd crisis-lens
```

### 2. Set Up Development Environment
```bash
# Install dependencies
pip install -r requirements.txt
cd apps/web && npm install

# Start services
docker-compose up -d

# Run migrations
python scripts/migrate.py
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## Development Workflow

### Making Changes

1. **Write tests first** (TDD approach preferred)
2. **Implement your feature/fix**
3. **Run tests**:
   ```bash
   pytest
   pytest --cov=. --cov-report=html
   ```
4. **Lint your code**:
   ```bash
   flake8 .
   black .
   ```

### Commit Guidelines

Use conventional commits:
```
feat: add new feature
fix: fix bug
docs: update documentation
test: add tests
refactor: refactor code
style: formatting changes
chore: maintenance tasks
```

Examples:
```bash
git commit -m "feat: add sentiment analysis to Twitter agent"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
```

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md**
5. **Create Pull Request** with description

**PR Title Format**:
```
[Type] Brief description

Examples:
[Feature] Add Reddit ingestion agent
[Fix] Resolve WebSocket connection issues
[Docs] Update deployment guide
```

**PR Description Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Docstrings for all public functions
- Line length: 127 characters
- Use Black for formatting

```python
def process_item(item_id: str, user_id: int) -> Dict[str, Any]:
    """
    Process crisis item with given ID.
    
    Args:
        item_id: Unique item identifier
        user_id: User performing action
    
    Returns:
        Processed item data
    """
    # Implementation
    pass
```

### TypeScript/JavaScript
- Use TypeScript for type safety
- ESLint for linting
- Prettier for formatting
- Functional components (React)

```typescript
interface Item {
  id: string;
  title: string;
  riskScore: number;
}

export const ItemCard: React.FC<{ item: Item }> = ({ item }) => {
  return <div>{item.title}</div>;
};
```

## Testing Guidelines

### Unit Tests
```python
import pytest

def test_twitter_agent_initialization():
    agent = TwitterAgent(bearer_token="test")
    assert agent is not None
    assert agent.bearer_token == "test"

@pytest.mark.asyncio
async def test_fetch_tweets():
    agent = TwitterAgent(bearer_token="test")
    results = await agent.fetch_recent_tweets("crisis")
    assert isinstance(results, list)
```

### Integration Tests
```python
@pytest.mark.integration
def test_api_endpoint(api_client, db_session):
    response = api_client.get("/items")
    assert response.status_code == 200
```

## Project Structure

```
crisis-lens/
├── agents/           # Data ingestion agents
├── workflows/        # Processing workflows
├── services/         # Shared services
├── apps/
│   ├── api/         # FastAPI backend
│   └── web/         # Next.js frontend
├── tests/           # Test suites
├── infrastructure/  # K8s, Docker configs
└── docs/            # Documentation
```

## Areas to Contribute

### High Priority
- [ ] New data source agents
- [ ] Enhanced ML models
- [ ] Performance optimizations
- [ ] Security improvements
- [ ] Documentation

### Features
- Multi-language support
- Advanced analytics
- Custom workflows
- API improvements

### Bug Fixes
Check [Issues](https://github.com/org/crisis-lens/issues) labeled `bug`

### Documentation
- Improve existing docs
- Add tutorials
- Create videos
- Translate documentation

## Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** verification
4. **Approval** required before merge

## Questions?

- **Issues**: [GitHub Issues](https://github.com/org/crisis-lens/issues)
- **Discussions**: [GitHub Discussions](https://github.com/org/crisis-lens/discussions)
- **Email**: dev@crisislens.io

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to CrisisLens! 🙏**
