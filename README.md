# 🎨 Fal.ai MCP Server

[![CI](https://github.com/raveenb/fal-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/raveenb/fal-mcp-server/actions/workflows/ci.yml)
[![MCP](https://img.shields.io/badge/MCP-1.0-blue)](https://modelcontextprotocol.io)
[![GitHub Release](https://img.shields.io/github/v/release/raveenb/fal-mcp-server)](https://github.com/raveenb/fal-mcp-server/releases)
[![PyPI](https://img.shields.io/pypi/v/fal-mcp-server)](https://pypi.org/project/fal-mcp-server/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A Model Context Protocol (MCP) server that enables Claude Desktop (and other MCP clients) to generate images, videos, music, and audio using [Fal.ai](https://fal.ai) models.

## ✨ Features

### 🚀 Performance
- **Native Async API** - Uses fal_client.run_async() for optimal performance
- **Queue Support** - Long-running tasks (video/music) use queue API with progress updates
- **Non-blocking** - All operations are truly asynchronous

- 🖼️ **Image Generation** - Create images using Flux, SDXL, and other models
- 🎬 **Video Generation** - Generate videos from images or text prompts  
- 🎵 **Music Generation** - Create music from text descriptions
- 🗣️ **Text-to-Speech** - Convert text to natural speech
- 📝 **Audio Transcription** - Transcribe audio using Whisper
- ⬆️ **Image Upscaling** - Enhance image resolution
- 🔄 **Image-to-Image** - Transform existing images with prompts

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [Fal.ai API key](https://fal.ai) (free tier available)
- Claude Desktop (or any MCP-compatible client)

### Installation

#### Option 1: Using uv (Recommended)

```bash
git clone https://github.com/raveenb/fal-mcp-server.git
cd fal-mcp-server
uv pip install -e .
```

#### Option 2: Using pip

```bash
git clone https://github.com/raveenb/fal-mcp-server.git
cd fal-mcp-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Configuration

1. Get your Fal.ai API key from [fal.ai](https://fal.ai)

2. Configure Claude Desktop by adding to:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fal-ai": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "--with",
        "fal-client",
        "python",
        "/path/to/fal-mcp-server/src/fal_mcp_server/server.py"
      ],
      "env": {
        "FAL_KEY": "your-fal-api-key"
      }
    }
  }
}
```

3. Restart Claude Desktop

## 💬 Usage

Once configured, ask Claude to:

- "Generate an image of a sunset"
- "Create a video from this image"  
- "Generate 30 seconds of ambient music"
- "Convert this text to speech"
- "Transcribe this audio file"

## 📦 Supported Models

### Image Models
- `flux_schnell` - Fast high-quality generation
- `flux_dev` - Development version with more control
- `sdxl` - Stable Diffusion XL

### Video Models
- `svd` - Stable Video Diffusion
- `animatediff` - Text-to-video animation

### Audio Models
- `musicgen` - Music generation
- `bark` - Text-to-speech
- `whisper` - Audio transcription

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Fal.ai](https://fal.ai) for providing the AI models
- [Anthropic](https://anthropic.com) for the MCP specification
