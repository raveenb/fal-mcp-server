# Development Practices

## Package Version Documentation

When using external packages, always check their documentation using the context7 MCP server:
1. Check the version in requirements.txt or pyproject.toml
2. Use context7 to get the docs for that specific package version
3. This ensures we're using the correct API methods and parameters

## Pre-PR Checklist

Before submitting any PR:
1. Run local CI tests (without publication/release):
   ```bash
   make ci-local  # This runs tests only, NO release
   ```
2. Ensure all checks pass:
   - Black formatting
   - Ruff linting
   - Mypy type checking
   - All tests pass with coverage
3. Fix any issues before pushing

## Testing Requirements

- Every PR must include corresponding test code
- All existing tests must pass before making a release (regression prevention)
- Never release if ANY test fails
- 3-strike rule: After 3 consecutive failed releases, stop and reassess

## CI/CD Workflow

1. **Local Development**: Run `make check` or `make ci-local`
2. **PR Creation**: Push only after local CI passes
3. **GitHub CI**: Automatically runs on PR
4. **Merge**: Only after CI passes
5. **Release**: Only on version tags (v*)

## Code Quality Tools

- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **Mypy**: Static type checking
- **Pytest**: Testing with coverage

Remember: Always run local CI before submitting PRs!