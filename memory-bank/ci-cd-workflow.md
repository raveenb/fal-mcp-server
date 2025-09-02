# CI/CD Workflow Policy

## Pre-PR Submission Checklist

### ALWAYS Run Local CI Before Creating PR

Before submitting any PR, developers MUST:

1. **Run local CI (NO release/publication workflows)**
   ```bash
   # Run full CI suite locally using act (tests only, NO release)
   make ci-local
   
   # Or run individual checks
   make check  # Runs format, lint, typecheck, test
   ```
   
   **⚠️ IMPORTANT**: Local CI with act will NEVER:
   - Trigger release/publish workflows
   - Publish to PyPI
   - Create GitHub releases
   - Push to any registry
   
   The `make ci-local` command explicitly runs ONLY the CI workflow, NOT the publish workflow.

2. **Verify all checks pass locally**
   - ✅ Black formatting
   - ✅ Ruff linting  
   - ✅ Mypy type checking
   - ✅ All tests pass with coverage
   - ✅ No regression in existing tests

3. **Fix any issues before pushing**
   - If CI fails locally, fix issues and re-run
   - Never push code that fails local CI
   - This saves GitHub Actions minutes and prevents broken PRs

## CI/CD Pipeline Stages

### 1. Local Development (Pre-PR)
```bash
# Format code
make format

# Check linting
make lint

# Type check
make typecheck

# Run tests with coverage
make test

# Or run all at once
make check

# Test full CI locally with act
make ci-local
```

### 2. PR Creation
- Push branch with passing local CI
- GitHub Actions automatically runs CI
- PR cannot merge if CI fails

### 3. GitHub CI/CD (Automated)
When PR is created or updated:
- Runs same checks as local CI
- Tests on matrix of Python versions (3.10, 3.11, 3.12)
- Posts results as PR status checks

### 4. Merge to Main
- Only after CI passes
- Squash and merge preferred
- Triggers any main branch workflows

### 5. Release/Publication
- Only triggered by version tags (v*)
- Separate workflow from CI
- Publishes to PyPI
- Creates GitHub release

## Important Notes

### Why Local CI First?
1. **Faster feedback** - No waiting for GitHub Actions
2. **Save Actions minutes** - Free tier has limits
3. **Prevent broken PRs** - Catch issues before they're public
4. **Better developer experience** - Fix issues immediately

### Act Configuration
The project includes act configuration for local CI:
- `.actrc` - Default act settings
- `.secrets` - Local secrets (never commit!)
- `make ci-local` - Convenience command

### CI Components
All PRs must pass:
1. **Black** - Code formatting
2. **Ruff** - Linting and import sorting
3. **Mypy** - Static type checking
4. **Pytest** - All tests with 80%+ coverage

### Publication Workflow
Publication to PyPI is separate:
- Never runs on PRs
- Only runs on version tags
- Requires PYPI_API_TOKEN secret
- Manual trigger via git tag

## Commands Reference

```bash
# Before creating PR - ALWAYS RUN
make ci-local

# Individual checks
make format      # Format with black
make lint        # Lint with ruff
make typecheck   # Type check with mypy
make test        # Run tests with coverage

# All checks at once
make check

# After PR is merged and ready to release
git tag v0.x.y
git push origin v0.x.y
# This triggers PyPI publication
```

## Enforcement
- PRs with failing CI cannot be merged
- Local CI should match GitHub CI exactly
- Use act to ensure consistency
- Never skip local CI to "save time"

This workflow ensures code quality and prevents CI failures in PRs.