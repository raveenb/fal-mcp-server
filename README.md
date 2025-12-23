# 🎨 Fal.ai MCP Server

[![CI](https://github.com/raveenb/fal-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/raveenb/fal-mcp-server/actions/workflows/ci.yml)
[![Docker](https://github.com/raveenb/fal-mcp-server/actions/workflows/docker.yml/badge.svg)](https://github.com/raveenb/fal-mcp-server/actions/workflows/docker.yml)
[![MCP](https://img.shields.io/badge/MCP-1.0-blue)](https://modelcontextprotocol.io)
[![GitHub Release](https://img.shields.io/github/v/release/raveenb/fal-mcp-server)](https://github.com/raveenb/fal-mcp-server/releases)
[![PyPI](https://img.shields.io/pypi/v/fal-mcp-server)](https://pypi.org/project/fal-mcp-server/)
[![Docker Image](https://img.shields.io/badge/Docker-ghcr.io-blue?logo=docker)](https://github.com/raveenb/fal-mcp-server/pkgs/container/fal-mcp-server)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A Model Context Protocol (MCP) server that enables Claude Desktop (and other MCP clients) to generate images, videos, music, and audio using [Fal.ai](https://fal.ai) models.

<a href="https://glama.ai/mcp/servers/@raveenb/fal-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@raveenb/fal-mcp-server/badge" alt="Fal.ai Server MCP server" />
</a>

## ✨ Features

### 🚀 Performance
- **Native Async API** - Uses fal_client.run_async() for optimal performance
- **Queue Support** - Long-running tasks (video/music) use queue API with progress updates
- **Non-blocking** - All operations are truly asynchronous

### 🌐 Transport Modes (New!)
- **STDIO** - Traditional Model Context Protocol communication
- **HTTP/SSE** - Web-based access via Server-Sent Events
- **Dual Mode** - Run both transports simultaneously

### 🎨 Media Generation (12 Tools)

**Image Tools:**
- 🖼️ **generate_image** - Create images from text prompts (Flux, SDXL, etc.)
- 🎯 **generate_image_structured** - Fine-grained control over composition, lighting, subjects
- 🔄 **generate_image_from_image** - Transform existing images with style transfer

**Video Tools:**
- 🎬 **generate_video** - Text-to-video and image-to-video generation
- 📹 **generate_video_from_image** - Animate images into videos
- 🔀 **generate_video_from_video** - Video restyling and motion transfer (NEW!)

**Audio Tools:**
- 🎵 **generate_music** - Create instrumental music or songs with vocals

**Utility Tools:**
- 🔍 **list_models** - Discover 600+ available models with smart filtering
- 💡 **recommend_model** - AI-powered model recommendations for your task
- 💰 **get_pricing** - Check costs before generating content
- 📊 **get_usage** - View spending history and usage stats
- ⬆️ **upload_file** - Upload local files for use with generation tools

### 🔍 Dynamic Model Discovery (New!)
- **600+ Models** - Access all models available on Fal.ai platform
- **Auto-Discovery** - Models are fetched dynamically from the Fal.ai API
- **Smart Caching** - TTL-based cache for optimal performance
- **Flexible Input** - Use full model IDs or friendly aliases

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [Fal.ai API key](https://fal.ai) (free tier available)
- Claude Desktop (or any MCP-compatible client)

### Installation

#### Option 0: Claude Code Plugin (Simplest for Claude Code Users) 🔌

If you're using [Claude Code](https://claude.ai/code), install directly via the plugin system:

```bash
# Add the Luminary Lane Tools marketplace
/plugin marketplace add raveenb/fal-mcp-server

# Install the fal-ai plugin
/plugin install fal-ai@luminary-lane-tools
```

Or install directly without adding the marketplace:
```bash
/plugin install fal-ai@raveenb/fal-mcp-server
```

> **Note:** You'll need to set `FAL_KEY` in your environment before using the plugin.

#### Option 1: uvx (Recommended - Zero Install) ⚡

Run directly without installation using [uv](https://docs.astral.sh/uv/):

```bash
# Run the MCP server directly
uvx --from fal-mcp-server fal-mcp

# Or with specific version
uvx --from fal-mcp-server==1.4.0 fal-mcp
```

**Claude Desktop Configuration for uvx:**
```json
{
  "mcpServers": {
    "fal-ai": {
      "command": "uvx",
      "args": ["--from", "fal-mcp-server", "fal-mcp"],
      "env": {
        "FAL_KEY": "your-fal-api-key"
      }
    }
  }
}
```

> **Note:** Install uv first: `curl -LsSf https://astral.sh/uv/install.sh | sh`

#### Option 2: Docker (Recommended for Production) 🐳

Official Docker image available on GitHub Container Registry.

**Step 1: Start the Docker container**

```bash
# Pull and run with your API key
docker run -d \
  --name fal-mcp \
  -e FAL_KEY=your-api-key \
  -p 8080:8080 \
  ghcr.io/raveenb/fal-mcp-server:latest

# Verify it's running
docker logs fal-mcp
```

**Step 2: Configure Claude Desktop to connect**

Add to your Claude Desktop config file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fal-ai": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8080/sse"]
    }
  }
}
```

> **Note:** This uses [mcp-remote](https://www.npmjs.com/package/mcp-remote) to connect to the HTTP/SSE endpoint. Alternatively, if you have `curl` available: `"command": "curl", "args": ["-N", "http://localhost:8080/sse"]`

**Step 3: Restart Claude Desktop**

The fal-ai tools should now be available.

**Docker Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `FAL_KEY` | (required) | Your Fal.ai API key |
| `FAL_MCP_TRANSPORT` | `http` | Transport mode: `http`, `stdio`, or `dual` |
| `FAL_MCP_HOST` | `0.0.0.0` | Host to bind the server to |
| `FAL_MCP_PORT` | `8080` | Port for the HTTP server |

**Using Docker Compose:**

```bash
curl -O https://raw.githubusercontent.com/raveenb/fal-mcp-server/main/docker-compose.yml
echo "FAL_KEY=your-api-key" > .env
docker-compose up -d
```

**⚠️ File Upload with Docker:**

The `upload_file` tool requires volume mounts to access host files:

```bash
docker run -d -p 8080:8080 \
  -e FAL_KEY="${FAL_KEY}" \
  -e FAL_MCP_TRANSPORT=http \
  -v ${HOME}/Downloads:/downloads:ro \
  -v ${HOME}/Pictures:/pictures:ro \
  ghcr.io/raveenb/fal-mcp-server:latest
```

Then use container paths like `/downloads/image.png` instead of host paths.

| Feature | stdio (uvx) | Docker (HTTP/SSE) |
|---------|:-----------:|:-----------------:|
| `upload_file` | ✅ Full filesystem | ⚠️ Needs volume mounts |
| Security | Runs as user | Sandboxed container |

#### Option 3: Install from PyPI

```bash
pip install fal-mcp-server
```

Or with uv:
```bash
uv pip install fal-mcp-server
```

#### Option 4: Install from source

```bash
git clone https://github.com/raveenb/fal-mcp-server.git
cd fal-mcp-server
pip install -e .
```

### Configuration

1. Get your Fal.ai API key from [fal.ai](https://fal.ai)

2. Configure Claude Desktop by adding to:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

#### For PyPI/pip Installation:
```json
{
  "mcpServers": {
    "fal-ai": {
      "command": "fal-mcp",
      "env": {
        "FAL_KEY": "your-fal-api-key"
      }
    }
  }
}
```

> **Note:** For Docker configuration, see [Option 2: Docker](#option-2-docker-recommended-for-production-) above.

#### For Source Installation:
```json
{
  "mcpServers": {
    "fal-ai": {
      "command": "python",
      "args": ["/path/to/fal-mcp-server/src/fal_mcp_server/server.py"],
      "env": {
        "FAL_KEY": "your-fal-api-key"
      }
    }
  }
}
```

3. Restart Claude Desktop

## 💬 Usage

### With Claude Desktop

Once configured, ask Claude to:

- "Generate an image of a sunset"
- "Create a video from this image"
- "Generate 30 seconds of ambient music"
- "Convert this text to speech"
- "Transcribe this audio file"

### Discovering Available Models

Use the `list_models` tool to discover available models:

- "What image models are available?"
- "List video generation models"
- "Search for flux models"

### Using Any Fal.ai Model

You can use any model from the Fal.ai platform:

```
# Using a friendly alias (backward compatible)
"Generate an image with flux_schnell"

# Using a full model ID (new capability)
"Generate an image using fal-ai/flux-pro/v1.1-ultra"
"Create a video with fal-ai/kling-video/v1.5/pro"
```

### HTTP/SSE Transport (New!)

Run the server with HTTP transport for web-based access:

```bash
# Using Docker (recommended)
docker run -d -e FAL_KEY=your-key -p 8080:8080 ghcr.io/raveenb/fal-mcp-server:latest

# Using pip installation
fal-mcp-http --host 0.0.0.0 --port 8000

# Or dual mode (STDIO + HTTP)
fal-mcp-dual --transport dual --port 8000
```

Connect from web clients via Server-Sent Events:
- SSE endpoint: `http://localhost:8080/sse` (Docker) or `http://localhost:8000/sse` (pip)
- Message endpoint: `POST http://localhost:8080/messages/`

See [Docker Documentation](docs/docker.md) and [HTTP Transport Documentation](docs/HTTP_TRANSPORT.md) for details.

## 📦 Supported Models

This server supports **600+ models** from the Fal.ai platform through dynamic discovery. Use the `list_models` tool to explore available models, or use any model ID directly.

### Popular Aliases (Quick Reference)

These friendly aliases are always available for commonly used models:

| Alias | Model ID | Type |
|-------|----------|------|
| `flux_schnell` | `fal-ai/flux/schnell` | Image |
| `flux_dev` | `fal-ai/flux/dev` | Image |
| `flux_pro` | `fal-ai/flux-pro` | Image |
| `sdxl` | `fal-ai/fast-sdxl` | Image |
| `stable_diffusion` | `fal-ai/stable-diffusion-v3-medium` | Image |
| `svd` | `fal-ai/stable-video-diffusion` | Video |
| `animatediff` | `fal-ai/fast-animatediff` | Video |
| `kling` | `fal-ai/kling-video` | Video |
| `musicgen` | `fal-ai/musicgen-medium` | Audio |
| `musicgen_large` | `fal-ai/musicgen-large` | Audio |
| `bark` | `fal-ai/bark` | Audio |
| `whisper` | `fal-ai/whisper` | Audio |

### Using Full Model IDs

You can also use any model directly by its full ID:

```python
# Examples of full model IDs
"fal-ai/flux-pro/v1.1-ultra"      # Latest Flux Pro
"fal-ai/kling-video/v1.5/pro"     # Kling Video Pro
"fal-ai/hunyuan-video"            # Hunyuan Video
"fal-ai/minimax-video"            # MiniMax Video
```

Use `list_models` with category filters to discover more:
- `list_models(category="image")` - All image generation models
- `list_models(category="video")` - All video generation models
- `list_models(category="audio")` - All audio models
- `list_models(search="flux")` - Search for specific models

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [Installation Guide](docs/installation.md) | Detailed setup instructions for all platforms |
| [API Reference](docs/api.md) | Complete tool documentation with parameters |
| [Examples](docs/examples.md) | Usage examples for image, video, and audio generation |
| [Docker Guide](docs/docker.md) | Container deployment and configuration |
| [HTTP Transport](docs/HTTP_TRANSPORT.md) | Web-based SSE transport setup |
| [Local Testing](docs/LOCAL_TESTING.md) | Running CI locally with `act` |

📖 **Full documentation site**: [raveenb.github.io/fal-mcp-server](https://raveenb.github.io/fal-mcp-server/)

### 🔌 Claude Code Plugin Marketplace

This project is part of the **Luminary Lane Tools** marketplace for Claude Code plugins.

**Add the marketplace:**
```bash
/plugin marketplace add raveenb/fal-mcp-server
```

**Available plugins:**
| Plugin | Description |
|--------|-------------|
| `fal-ai` | Generate images, videos, and music using 600+ Fal.ai models |

*More plugins coming soon!*

## 🔧 Troubleshooting

### Common Errors

#### FAL_KEY not set
```
Error: FAL_KEY environment variable is required
```
**Solution:** Set your Fal.ai API key:
```bash
export FAL_KEY="your-api-key"
```

#### Model not found
```
Error: Model 'xyz' not found
```
**Solution:** Use `list_models` to discover available models, or check the model ID spelling.

#### File not found (Docker)
```
Error: File not found: /Users/username/image.png
```
**Solution:** When using Docker, mount the directory as a volume. See [File Upload with Docker](#-file-upload-with-docker) above.

#### Timeout on video/music generation
```
Error: Generation timed out after 300s
```
**Solution:** Video and music generation can take several minutes. This is normal for high-quality models. Try:
- Using a faster model variant (e.g., `schnell` instead of `pro`)
- Reducing duration or resolution

#### Rate limiting
```
Error: Rate limit exceeded
```
**Solution:** Wait a few minutes and retry. Consider upgrading your Fal.ai plan for higher limits.

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set debug environment variable
export FAL_MCP_DEBUG=true

# Run the server
fal-mcp
```

### Reporting Issues

If you encounter a bug or unexpected behavior:

1. **Check existing issues:** [GitHub Issues](https://github.com/raveenb/fal-mcp-server/issues)

2. **Gather information:**
   - Error message (full text)
   - Steps to reproduce
   - Model ID used
   - Environment (OS, Python version, transport mode)

3. **Open a new issue** with:
   ```
   **Error:** [paste error message]
   **Steps to reproduce:** [what you did]
   **Model:** [model ID if applicable]
   **Environment:** [OS, Python version, Docker/uvx/pip]
   ```

4. **Include logs** if available (with sensitive data removed)

[📝 Open an Issue](https://github.com/raveenb/fal-mcp-server/issues/new)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Local Development

We support local CI testing with `act`:

```bash
# Quick setup
make ci-local  # Run CI locally before pushing

# See detailed guide
cat docs/LOCAL_TESTING.md
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Fal.ai](https://fal.ai) for providing the AI models
- [Anthropic](https://anthropic.com) for the MCP specification