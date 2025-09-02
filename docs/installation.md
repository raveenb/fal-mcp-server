---
layout: page
title: Installation Guide - Fal MCP Server
description: Step-by-step guide to install and configure Fal MCP Server for Claude Desktop. Multiple installation methods including pip, Docker, and source.
keywords: install Fal MCP server, Claude MCP setup, Fal.ai API key, Docker installation, pip install
---

# Installation Guide

Get Fal MCP Server up and running in minutes with our comprehensive installation guide.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** (for pip installation)
- **Claude Desktop** application
- **Fal.ai API Key** ([Get one here](https://fal.ai/dashboard/keys))
- **Docker** (optional, for containerized deployment)

## Installation Methods

### Method 1: Install via pip (Recommended)

The simplest way to install Fal MCP Server:

```bash
# Install the package
pip install fal-mcp-server

# Verify installation
fal-mcp --help
```

### Method 2: Install via uv (Fastest)

Using the modern Python package manager:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Fal MCP Server
uv pip install fal-mcp-server
```

### Method 3: Docker Installation (Recommended for Production)

**✅ Docker image is now available on GitHub Container Registry!**

For isolated, reproducible deployments:

```bash
# Pull the official Docker image from GitHub Packages
docker pull ghcr.io/raveenb/fal-mcp-server:latest

# Run with your API key
docker run -d \
  --name fal-mcp \
  -e FAL_KEY=your-api-key \
  -p 8080:8080 \
  ghcr.io/raveenb/fal-mcp-server:latest

# Or use docker-compose
curl -O https://raw.githubusercontent.com/raveenb/fal-mcp-server/main/docker-compose.yml
docker-compose up -d
```

**Available Docker tags:**
- `latest` - Most recent stable release
- `v0.3.0`, `v0.2.0`, etc. - Specific versions
- `main` - Latest development build

### Method 4: Install from Source

For development or customization:

```bash
# Clone the repository
git clone https://github.com/raveenb/fal-mcp-server.git
cd fal-mcp-server

# Install in development mode
pip install -e ".[dev]"
```

## Configuration

### Step 1: Set Your Fal.ai API Key

```bash
# Linux/macOS
export FAL_KEY="your-api-key-here"

# Windows (PowerShell)
$env:FAL_KEY="your-api-key-here"

# Or create a .env file
echo "FAL_KEY=your-api-key-here" > .env
```

### Step 2: Configure Claude Desktop

Add the server to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fal-mcp-server": {
      "command": "fal-mcp",
      "args": [],
      "env": {
        "FAL_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

After configuration, restart Claude Desktop to load the MCP server.

## Transport Modes

### STDIO Mode (Default)

Standard input/output mode for Claude Desktop:

```bash
fal-mcp
```

### HTTP/SSE Mode

For web-based access:

```bash
# Start HTTP server
fal-mcp-http --host 0.0.0.0 --port 8080

# Access at http://localhost:8080/sse
```

Configure in Claude:

```json
{
  "mcpServers": {
    "fal-mcp-server": {
      "command": "curl",
      "args": ["-N", "http://localhost:8080/sse"]
    }
  }
}
```

### Dual Mode

Run both STDIO and HTTP simultaneously:

```bash
fal-mcp-dual --transport dual --port 8081
```

## Docker Configuration

### Using Docker Compose

1. Create a `.env` file:

```bash
FAL_KEY=your-api-key-here
```

2. Start the service:

```bash
docker-compose up -d
```

3. Configure Claude to connect to the Docker container:

```json
{
  "mcpServers": {
    "fal-mcp-server": {
      "command": "curl",
      "args": ["-N", "http://localhost:8080/sse"]
    }
  }
}
```

### Using Docker Run

**The official Docker image is available on GitHub Container Registry!**

```bash
# Pull the latest image (updated regularly)
docker pull ghcr.io/raveenb/fal-mcp-server:latest

# Run the container
docker run -d \
  --name fal-mcp \
  -e FAL_KEY=your-api-key \
  -p 8080:8080 \
  ghcr.io/raveenb/fal-mcp-server:latest

# Verify it's running
docker ps | grep fal-mcp

# Check logs
docker logs fal-mcp
```

**Docker Image Features:**
- 🔒 Non-root user for security
- 📦 Multi-stage build (optimized size ~150MB)
- 🚀 Pre-configured for production use
- ♻️ Automatic updates with CI/CD
- 🏷️ Tagged releases for version pinning

## Verification

### Test the Installation

1. Open Claude Desktop
2. Type: "Generate an image of a sunset"
3. Claude should use the `generate_image` tool

### Check Available Tools

In Claude, ask: "What tools do you have available?"

You should see:
- `generate_image` - Create images from text
- `generate_video` - Create videos from images
- `generate_music` - Generate music from descriptions

### Troubleshooting

#### Server Not Found

If Claude doesn't recognize the server:

1. Check the config file path is correct
2. Ensure JSON syntax is valid
3. Restart Claude Desktop completely

#### Authentication Error

If you get "FAL_KEY not set":

1. Verify your API key is correct
2. Check environment variable is set
3. Ensure the key is active on [Fal.ai Dashboard](https://fal.ai/dashboard/keys)

#### Connection Issues

For HTTP mode connection problems:

1. Check the server is running: `curl http://localhost:8080/sse`
2. Verify firewall allows the port
3. Try using `127.0.0.1` instead of `localhost`

## Advanced Configuration

### Custom Models

You can specify different models in your requests:

```python
# In Claude, you can request specific models:
"Generate an image using flux_dev model"
"Create a video with kling model"
```

### Environment Variables

All configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `FAL_KEY` | Your Fal.ai API key | Required |
| `FAL_MCP_TRANSPORT` | Transport mode | `stdio` |
| `FAL_MCP_HOST` | HTTP server host | `127.0.0.1` |
| `FAL_MCP_PORT` | HTTP server port | `8080` |
| `FAL_LOG_LEVEL` | Logging level | `INFO` |

### Performance Tuning

For optimal performance:

```bash
# Increase timeout for long operations
export FAL_TIMEOUT=600

# Enable debug logging
export FAL_LOG_LEVEL=DEBUG
```

## Platform-Specific Notes

### macOS

- Requires macOS 11+ for Claude Desktop
- May need to allow network access on first run
- Use Homebrew for Python: `brew install python@3.11`

### Windows

- Use PowerShell or WSL2 for best experience
- Path to config: `%APPDATA%\Claude\claude_desktop_config.json`
- May need to disable Windows Defender for Docker

### Linux

- Works on Ubuntu 20.04+, Debian 11+, Fedora 35+
- May need to install additional dependencies: `apt install python3-pip`
- Docker requires sudo or docker group membership

## Next Steps

Now that you have Fal MCP Server installed:

1. [View Examples]({{ '/examples' | relative_url }}) - See what you can create
2. [API Documentation]({{ '/api' | relative_url }}) - Understand the tools
3. [Docker Guide]({{ '/docker' | relative_url }}) - Advanced Docker setup
4. [Troubleshooting]({{ '/troubleshooting' | relative_url }}) - Common issues

## Getting Help

If you encounter issues:

- [GitHub Issues](https://github.com/raveenb/fal-mcp-server/issues)
- [Discussions](https://github.com/raveenb/fal-mcp-server/discussions)
- [Discord Community](#) <!-- Add your Discord link -->

---

<div class="nav-buttons">
  <a href="{{ '/' | relative_url }}" class="btn">← Home</a>
  <a href="{{ '/examples' | relative_url }}" class="btn btn-primary">Examples →</a>
</div>