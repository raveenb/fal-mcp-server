# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Testing
```bash
# Run tests
pytest tests/

# Run tests with async support
pytest tests/ -v --asyncio-mode=auto

# Test specific file
pytest tests/test_server.py -v
```

### Linting and Formatting
```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```

### Development Setup
```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Or using uv (recommended)
uv pip install -e ".[dev]"
```

### Running the Server
```bash
# Direct execution (requires FAL_KEY environment variable)
python src/fal_mcp_server/server.py

# Or via the convenience wrapper
python fal_mcp.py
```

## GitHub Workflow

### Development Planning
```bash
# Create issue for new feature/task
gh issue create --title "Feature: Add new model support" --body "Description of the task"

# List open issues (our task backlog)
gh issue list --state open

# View specific issue details
gh issue view <issue-number>

# Create issue with labels
gh issue create --title "Bug: Fix async timeout" --label "bug,priority-high"
```

### Branch and PR Workflow
```bash
# Create feature branch from issue
gh issue develop <issue-number> --checkout

# Or manually create branch
git checkout -b feature/issue-<number>-description

# After implementation, create PR linked to issue
gh pr create --title "Fix #<issue>: Description" --body "Closes #<issue>"

# Create draft PR for work in progress
gh pr create --draft --title "WIP: Feature implementation"

# Check PR status and CI results
gh pr checks
gh pr view
```

### CI/CD and Deployment
```bash
# View workflow runs
gh workflow list
gh run list

# Watch CI status for current branch
gh run watch

# Trigger manual deployment (when workflow exists)
gh workflow run deploy.yml

# Create release after PR merge
gh release create v0.2.0 --title "Release v0.2.0" --notes "Release notes"
```

### Working Across Machines

When starting work on a different machine:
1. Check open issues: `gh issue list --assignee @me`
2. Check open PRs: `gh pr list --author @me`
3. Continue from existing branch: `gh pr checkout <pr-number>`

### Issue Templates for Planning

Store development plans as GitHub issues with structured format:
- **Title**: Clear feature/task description
- **Body**: Include acceptance criteria, technical approach, dependencies
- **Labels**: Use for categorization (feature, bug, enhancement, docs)
- **Milestone**: Group related issues for releases

## Architecture

### Core Components

**MCP Server Implementation** (`src/fal_mcp_server/server.py`)
- Single-file async MCP server using the Model Context Protocol
- Integrates with Fal.ai's async API for fast operations (image generation)
- Uses queue API with polling for long-running tasks (video/music generation)
- All operations are truly asynchronous using native `fal_client.run_async()` and `fal_client.submit_async()`

### Key Design Patterns

1. **Async-First Architecture**: The server uses `asyncio` throughout with native async Fal client methods. Fast operations use `run_async()` while long operations use `submit_async()` with queue polling.

2. **Queue Management**: Video and music generation use the queue API pattern:
   - Submit job with `submit_async()`
   - Poll status with `get_async()` 
   - Return progress updates to client
   - Final result includes generated media URLs

3. **Tool Registration**: Tools are registered with MCP using structured schemas that define parameters, models, and capabilities. Each tool maps to specific Fal.ai model endpoints.

4. **Model Configuration**: Models are organized by type (IMAGE_MODELS, VIDEO_MODELS, AUDIO_MODELS) with their corresponding Fal.ai endpoints mapped in the server.

### Entry Points

- **Primary**: `src/fal_mcp_server/server.py` - Complete server implementation
- **Wrapper**: `fal_mcp.py` - Simple convenience wrapper for running the server

### Environment Requirements

- Python 3.10+ required
- FAL_KEY environment variable must be set with valid Fal.ai API key
- Async support throughout - all I/O operations are non-blocking