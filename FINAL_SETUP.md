# Final Setup Instructions

## ✅ What's Done:
1. Virtual environment created with Python 3.13
2. MCP and fal-client installed
3. Claude config updated
4. Your FAL API key is configured

## 📋 Last Step - Copy the Complete Server Code:

1. **Copy the content from the 'server.py' artifact** shown in the Claude conversation above
2. **Replace the content** in: `src/fal_mcp_server/server.py`
3. **Restart Claude Desktop**

## 🧪 Test Your Setup:

Run this command to test:
```bash
cd ~/Developer/fal-mcp-server
.venv313/bin/python -c "from src.fal_mcp_server.server import server; import asyncio; print(asyncio.run(server.list_tools()))"
```

## 🎨 After Restarting Claude:

You can ask Claude to:
- Generate an image of a sunset
- Create a video from an image
- Generate music
- Convert text to speech
- Transcribe audio
- Upscale images

Your configuration is at:
`~/Library/Application Support/Claude/claude_desktop_config.json`

