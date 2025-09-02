# Testing Policy

## Mandatory Testing Requirements

### Every PR Must Include Tests

1. **New Features**
   - Unit tests for all new functions/methods
   - Integration tests for API endpoints
   - Edge case testing
   - Error handling tests

2. **Bug Fixes**
   - Regression test that reproduces the bug
   - Test confirming the fix works
   - Related edge cases

3. **Refactoring**
   - Existing tests must pass
   - Add tests if coverage is insufficient
   - Performance tests if optimization claimed

## Test Implementation

### Test Files
- Place in `tests/` directory
- Name: `test_<feature>.py`
- Use pytest as primary test runner
- Mock external dependencies (APIs, databases)

### Test Coverage
- Minimum 80% code coverage required
- New code should have 90%+ coverage
- Use `pytest --cov` to measure

### Test Types Required

1. **Unit Tests**
   ```python
   def test_function_normal_case():
       # Test expected behavior
   
   def test_function_edge_case():
       # Test boundary conditions
   
   def test_function_error_case():
       # Test error handling
   ```

2. **Integration Tests**
   ```python
   async def test_api_endpoint():
       # Test full request/response cycle
   ```

3. **Async Tests** (for MCP server)
   ```python
   @pytest.mark.asyncio
   async def test_async_operation():
       # Test async functions
   ```

## CI/CD Integration

### PR Workflow
1. Tests run automatically on every PR
2. PR cannot merge if tests fail
3. Coverage report posted as PR comment

### Release Workflow
1. **ALL existing tests must pass** - No regression allowed
2. Run full test suite before any release/PyPI publish
3. If ANY test fails (new or existing), fix and retry
4. After 3 failed attempts, escalate to maintainer

### Regression Prevention
- **Every release must pass 100% of existing tests**
- New features cannot break old functionality
- Test suite grows with each feature - never shrinks
- Historical tests serve as regression guards
- Breaking changes require explicit version bump (major version)

## Release Failure Protocol

### Automated Retry Logic
```
Attempt 1: Run tests → Fail → Auto-fix common issues → Retry
Attempt 2: Run tests → Fail → Check dependencies → Retry  
Attempt 3: Run tests → Fail → STOP → Ask for manual intervention
```

### Common Auto-Fixes
- Update dependencies
- Clear cache
- Regenerate lock files
- Format code

### Manual Intervention Required After 3 Failures
- Review error logs
- Check for environment issues
- Verify API keys/secrets
- Consider rolling back changes

## Test Examples for This Project

### Image Generation Test
```python
@pytest.mark.asyncio
async def test_generate_image():
    # Mock fal_client
    with patch('fal_client.run_async') as mock_run:
        mock_run.return_value = {"images": [{"url": "http://example.com/image.jpg"}]}
        
        result = await generate_image("test prompt")
        assert result["images"][0]["url"] == "http://example.com/image.jpg"
```

### MCP Server Test
```python
@pytest.mark.asyncio
async def test_mcp_tool_registration():
    server = FalMCPServer()
    tools = await server.list_tools()
    
    assert "generate_image" in [t.name for t in tools]
    assert len(tools) > 0
```

### Error Handling Test
```python
@pytest.mark.asyncio
async def test_api_key_missing():
    with pytest.raises(ValueError, match="FAL_KEY"):
        await server.initialize()
```

## Testing Checklist for PRs

- [ ] All new functions have unit tests
- [ ] Integration tests for new features
- [ ] Error cases are tested
- [ ] Async operations tested with pytest-asyncio
- [ ] Mocks used for external services
- [ ] Coverage >= 80%
- [ ] Tests pass locally (`make test`)
- [ ] CI/CD passes on PR

## Test Commands

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ --cov=src/fal_mcp_server --cov-report=term-missing

# Run specific test
pytest tests/test_server.py::test_function_name

# Run with verbose output
pytest -v tests/

# Run async tests
pytest --asyncio-mode=auto tests/
```

## Enforcement

- PRs without tests will be automatically rejected
- Coverage reports are mandatory
- Test failures block merges
- Release process halts on test failures

This policy ensures code quality, prevents regressions, and maintains reliability.