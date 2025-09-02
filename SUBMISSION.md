# MCP Directory Submission Information

This document contains all the information needed for submitting Fal MCP Server to various MCP directories and registries.

## Project Information

**Name**: Fal MCP Server  
**Version**: v0.3.0  
**License**: MIT  
**Repository**: https://github.com/raveenb/fal-mcp-server  
**Documentation**: https://raveenb.github.io/fal-mcp-server/  
**PyPI**: https://pypi.org/project/fal-mcp-server/  
**Docker**: ghcr.io/raveenb/fal-mcp-server  

## Short Description (< 100 chars)

Generate stunning AI images, videos & music in Claude using Fal.ai models via MCP

## Long Description

Fal MCP Server is a Model Context Protocol server that integrates Fal.ai's powerful AI models directly into Claude Desktop. It enables users to generate high-quality images, videos, and music using state-of-the-art models like FLUX, Stable Diffusion, Stable Video Diffusion, and MusicGen, all through natural language conversations.

## Key Features

- 🎨 **Image Generation**: Create images with FLUX (Schnell, Dev, Pro), Stable Diffusion XL, and more
- 🎬 **Video Creation**: Transform images into videos with Stable Video Diffusion and AnimateDiff
- 🎵 **Music & Audio**: Generate music and speech with MusicGen and Bark
- ⚡ **Fast Performance**: Native async API with queue management for optimal performance
- 🐳 **Docker Support**: Official Docker image available on GitHub Container Registry
- 🔧 **Easy Setup**: Simple installation via pip, Docker, or from source
- 🌐 **Multiple Transports**: STDIO, HTTP/SSE, and dual mode support

## Categories

- AI/ML Generation
- Image Generation
- Video Generation
- Audio Generation
- Creative Tools
- Claude Integration

## Installation

```bash
# Via pip
pip install fal-mcp-server

# Via Docker
docker pull ghcr.io/raveenb/fal-mcp-server:latest

# Via uv
uv pip install fal-mcp-server
```

## Configuration for Claude Desktop

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

## Supported Models

### Image Models
- FLUX Schnell, Dev, Pro
- Stable Diffusion XL, 3
- LCM variants

### Video Models
- Stable Video Diffusion
- AnimateDiff
- Kling Video

### Audio Models
- MusicGen (Small, Medium, Large)
- Bark (Text-to-Speech)

## Requirements

- Python 3.10+
- Fal.ai API key (get from https://fal.ai/dashboard/keys)
- Claude Desktop application

## Example Usage

```
User: Generate an image of a cyberpunk city at sunset

Claude: I'll generate a cyberpunk city at sunset for you.
[Uses generate_image tool with FLUX]
🎨 Generated image: https://fal.ai/generated/image.jpg
```

## Links

- **GitHub**: https://github.com/raveenb/fal-mcp-server
- **Documentation**: https://raveenb.github.io/fal-mcp-server/
- **PyPI**: https://pypi.org/project/fal-mcp-server/
- **Docker Hub**: https://github.com/raveenb/fal-mcp-server/pkgs/container/fal-mcp-server
- **Issues**: https://github.com/raveenb/fal-mcp-server/issues
- **License**: MIT

## Badges

[![PyPI version](https://badge.fury.io/py/fal-mcp-server.svg)](https://badge.fury.io/py/fal-mcp-server)
[![Docker Image](https://img.shields.io/badge/Docker-ghcr.io-blue?logo=docker)](https://github.com/raveenb/fal-mcp-server/pkgs/container/fal-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-1.0-green)](https://github.com/modelcontextprotocol)

## Author

**Raveen Beemsingh**  
GitHub: [@raveenb](https://github.com/raveenb)  
Email: raveen.b@gmail.com

## Submission Entries

### For modelcontextprotocol/servers

```markdown
- **[Fal MCP Server](https://github.com/raveenb/fal-mcp-server)** - Generate AI images, videos, and music using Fal.ai models (FLUX, Stable Diffusion, MusicGen) directly in Claude
```

### For awesome-mcp-servers

```markdown
[fal-mcp-server](https://github.com/raveenb/fal-mcp-server) 🐍 ☁️ - Generate AI images, videos, and music using Fal.ai models (FLUX, Stable Diffusion, MusicGen) directly in Claude Desktop
```

### For Smithery Registry

```json
{
  "name": "fal-mcp-server",
  "title": "Fal MCP Server",
  "description": "Generate AI images, videos, and music using Fal.ai models directly in Claude",
  "version": "0.3.0",
  "author": "Raveen Beemsingh",
  "license": "MIT",
  "repository": "https://github.com/raveenb/fal-mcp-server",
  "homepage": "https://raveenb.github.io/fal-mcp-server/",
  "categories": ["ai", "generation", "images", "video", "audio"],
  "keywords": ["fal", "ai", "image-generation", "video-generation", "music", "claude", "mcp"],
  "runtime": "python",
  "requirements": {
    "python": ">=3.10",
    "fal_key": "required"
  },
  "installation": {
    "pip": "pip install fal-mcp-server",
    "docker": "docker pull ghcr.io/raveenb/fal-mcp-server:latest"
  },
  "tools": [
    {
      "name": "generate_image",
      "description": "Generate images from text prompts using AI models"
    },
    {
      "name": "generate_video", 
      "description": "Create videos from images using AI models"
    },
    {
      "name": "generate_music",
      "description": "Generate music and audio from text descriptions"
    }
  ]
}
```

## Screenshots/Demo

1. **Image Generation Example**
   - Prompt: "Generate a cyberpunk city at sunset"
   - Model: FLUX Dev
   - Result: High-quality image with neon lights and futuristic buildings

2. **Video Generation Example**
   - Input: Generated image
   - Model: Stable Video Diffusion
   - Result: 4-second animated video

3. **Music Generation Example**
   - Prompt: "Create ambient electronic music"
   - Model: MusicGen Large
   - Result: 60-second audio track

## Metrics

- PyPI Downloads: [![Downloads](https://pepy.tech/badge/fal-mcp-server)](https://pepy.tech/project/fal-mcp-server)
- GitHub Stars: ![GitHub stars](https://img.shields.io/github/stars/raveenb/fal-mcp-server?style=social)
- Docker Pulls: Available on GitHub Container Registry
- Test Coverage: 95%+
- Python Support: 3.10, 3.11, 3.12

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/fal_mcp_server

# Run CI locally
act push --workflows .github/workflows/ci.yml
```