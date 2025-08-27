# 🎨 MCP Server for Fal.ai

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0.0-green)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables AI agents to generate images, videos, music, and speech using Fal.ai powerful AI models.

## ✨ Features

- 🖼️ **Image Generation** - Create images with Flux, SDXL, and other models
- 🎬 **Video Generation** - Transform images into videos
- 🎵 **Music Generation** - Generate music from text descriptions
- 🗣️ **Text-to-Speech** - Convert text to natural speech
- 📝 **Speech-to-Text** - Transcribe audio with Whisper

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A [Fal.ai API key](https://fal.ai/dashboard)
- An MCP-compatible client (Claude Desktop, Cline, etc.)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mcp-server-fal.git
cd mcp-server-fal
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key:
```bash
cp .env.example .env
# Edit .env and add your Fal.ai API key
```

### Configuration for Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "fal-ai": {
      "command": "python",
      "args": ["/path/to/mcp-server-fal/src/fal_mcp_server/server.py"],
      "env": {
        "FAL_KEY": "your-fal-api-key-here"
      }
    }
  }
}
```

## 📖 Usage

Once configured, your AI assistant can generate images, videos, music, and more!

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Fal.ai](https://fal.ai) for providing the AI models
- [Anthropic](https://anthropic.com) for creating the MCP protocol
