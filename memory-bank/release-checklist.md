# Release Checklist

## Pre-Release Checks

1. **Version Sync**
   - [ ] Update version in `pyproject.toml` to match intended release version
   - [ ] Ensure version follows semantic versioning (MAJOR.MINOR.PATCH)

2. **Code Quality**
   - [ ] Run tests locally: `pytest tests/ -v`
   - [ ] Run linting: `ruff check src/ tests/`
   - [ ] Run formatting: `black --check src/ tests/`
   - [ ] Ensure CI passes on main branch

3. **Documentation**
   - [ ] Update README.md if features added
   - [ ] Update CHANGELOG.md (if exists)
   - [ ] Verify installation instructions are current

## Release Process

1. **Create Git Tag**
   ```bash
   git tag -a v0.X.Y -m "Release v0.X.Y - Brief description"
   git push origin v0.X.Y
   ```

2. **Create GitHub Release**
   ```bash
   gh release create v0.X.Y --title "v0.X.Y - Release Title" --notes "Release notes..."
   ```

3. **Verify PyPI Publishing**
   - Check GitHub Actions: `gh run list --workflow=publish.yml --limit=3`
   - Wait for workflow completion (usually ~30 seconds)
   - Verify on PyPI: `pip index versions fal-mcp-server`
   - Test installation: `pip install --upgrade fal-mcp-server`

## Post-Release Verification

1. **PyPI Checks**
   - [ ] Package appears on https://pypi.org/project/fal-mcp-server/
   - [ ] Version number is correct
   - [ ] README renders correctly on PyPI page

2. **Installation Test**
   ```bash
   # In a fresh environment
   pip install fal-mcp-server
   python -m fal_mcp_server.server --version  # If version flag exists
   ```

3. **Update Memory Bank**
   - [ ] Log release in progress.md
   - [ ] Update active-context.md with next steps
   - [ ] Document any decisions in decision-log.md

## Common Issues & Solutions

### Version Mismatch
- **Problem**: PyPI shows wrong version
- **Solution**: Ensure `pyproject.toml` version matches git tag

### PyPI Publishing Failed
- **Problem**: Workflow fails to publish
- **Solution**: Check PYPI_API_TOKEN secret is set correctly

### Tag Already Exists
- **Problem**: Git tag already exists
- **Solution**: Delete old tag: `git tag -d v0.X.Y && git push origin :refs/tags/v0.X.Y`

## Required Secrets
- `PYPI_API_TOKEN`: Required for PyPI publishing
- `FAL_KEY`: Required for running tests (if tests use Fal API)

## Version Strategy
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes, documentation updates