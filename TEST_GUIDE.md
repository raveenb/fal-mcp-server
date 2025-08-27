# 🧪 Testing Your Fal.ai MCP Server

## Step 1: Test the API Connection
```bash
cd ~/Developer/fal-mcp-server
.venv313/bin/python -c "
import fal_client, os
os.environ['FAL_KEY'] = '5ba82550-c252-4430-90d9-68adbaeb731d:b2107824b055c4fd157c1d2ac0b0fccc'
result = fal_client.run('fal-ai/flux/schnell', arguments={'prompt': 'test'})
print('✅ API works!' if 'images' in result else '❌ API failed')
"
```

## Step 2: Test MCP Installation
```bash
.venv313/bin/python -c "import mcp; print('✅ MCP installed')"
```

## Step 3: Test Server Import
```bash
.venv313/bin/python -c "from src.fal_mcp_server.server import server; print('✅ Server imports')"
```

## Step 4: Restart Claude Desktop
1. Quit Claude completely (Cmd+Q)
2. Start Claude again
3. Look for any error messages when starting

## Step 5: Test in Claude
After restarting, try these prompts:

### Basic Test:
"Can you generate an image of a sunset?"

### If that works, try:
- "Generate an image of a futuristic city"
- "Create 2 images of cute puppies"
- "Generate an image using the sdxl model"

## Step 6: Check Logs
If something doesn't work, check:
```bash
# View Claude's config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Test the server directly
cd ~/Developer/fal-mcp-server
FAL_KEY='5ba82550-c252-4430-90d9-68adbaeb731d:b2107824b055c4fd157c1d2ac0b0fccc' \
.venv313/bin/python src/fal_mcp_server/server.py
```

## Troubleshooting

### If Claude doesn't recognize the commands:
1. Make sure you restarted Claude completely
2. Check the config file is correct
3. Try: "What MCP servers do you have access to?"

### If you get "server not found":
1. Check the path in the config is exactly:
   /Users/raveenbeemsingh/Developer/fal-mcp-server/.venv313/bin/python

### If you get permission errors:
```bash
chmod +x ~/Developer/fal-mcp-server/src/fal_mcp_server/server.py
chmod +x ~/Developer/fal-mcp-server/.venv313/bin/python
```

## Expected Success Output
When everything works, asking Claude to generate an image should return:
"🎨 Generated 1 image(s) with flux_schnell:
Image 1: https://v3.fal.media/files/..."

