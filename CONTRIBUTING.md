# Contributing to Fal MCP Server

Thank you for your interest in contributing to the Fal MCP Server! This guide will help you get started.

## Development Setup

### Prerequisites
- Python 3.10+
- Docker (for local CI testing)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/raveenb/fal-mcp-server.git
cd fal-mcp-server

# Install in development mode
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

### Environment Setup
```bash
# Copy secrets template
cp .secrets.example .secrets

# Add your Fal.ai API key to .secrets
# FAL_KEY=your_api_key_here
```

## Development Workflow

### 1. Create an Issue
Before starting work, create or find an issue describing the feature/bug.

### 2. Create a Branch
```bash
# Using GitHub CLI
gh issue develop <issue-number> --checkout

# Or manually
git checkout -b feature/issue-<number>-description
```

### 3. Make Changes
Follow the existing code style and conventions.

### 4. Test Locally

#### Run Tests
```bash
make test
# Or
pytest tests/ -v --asyncio-mode=auto
```

#### Check Code Quality
```bash
make lint    # Run linting
make format  # Format code
```

#### Test CI Locally
```bash
make ci-local  # Run full CI workflow locally
```

See [docs/LOCAL_TESTING.md](docs/LOCAL_TESTING.md) for detailed act usage.

### 5. Commit Changes
```bash
git add .
git commit -m "Clear, descriptive commit message"
```

### 6. Push and Create PR
```bash
git push origin your-branch-name

# Create PR with GitHub CLI
gh pr create --title "Fix #<issue>: Description" --body "Details..."
```

## Code Style

### Python
- Use Black for formatting (line length: 88)
- Use Ruff for linting
- Follow PEP 8
- Add type hints where appropriate

### Commits
- Clear, descriptive messages
- Reference issues: "Fix #123: Description"
- Keep commits focused and atomic

## Testing

### Running Tests
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_server.py

# With coverage
pytest tests/ --cov=src/fal_mcp_server --cov-report=term-missing
```

### Writing Tests
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use pytest fixtures for setup
- Mock external API calls

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update Memory Bank files if needed

## Pull Request Process

1. **Ensure CI passes**: All tests, linting, and formatting
2. **Update documentation**: README, docstrings, examples
3. **Write clear PR description**: 
   - What changed
   - Why it changed
   - How to test
4. **Link to issue**: Use "Closes #123" in PR description
5. **Request review**: Tag maintainers if needed

## Release Process

See [memory-bank/release-checklist.md](memory-bank/release-checklist.md) for detailed release steps.

## Local CI Testing

We use `act` for local GitHub Actions testing:

```bash
# Install act
make act-install

# Run CI locally
make ci-local

# Test specific Python version
act push --matrix python-version:3.11
```

## Project Structure

```
fal-mcp-server/
├── src/
│   └── fal_mcp_server/
│       ├── __init__.py
│       └── server.py       # Main MCP server
├── tests/
│   └── test_*.py          # Test files
├── docs/                  # Documentation
├── memory-bank/           # Project documentation
├── .github/
│   └── workflows/         # CI/CD workflows
├── pyproject.toml         # Package configuration
└── Makefile              # Development commands
```

## Getting Help

- Check existing [issues](https://github.com/raveenb/fal-mcp-server/issues)
- Read the [documentation](docs/)
- Ask in PR comments
- Review Memory Bank files for project context

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what's best for the project

Thank you for contributing!