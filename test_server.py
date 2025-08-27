#!/usr/bin/env python3
"""Test the Fal.ai MCP server locally"""

import os
import asyncio
import sys
sys.path.insert(0, 'src')

from fal_mcp_server.server import server, call_tool

async def test():
    # Set your API key
    if not os.getenv('FAL_KEY'):
        print('Please set FAL_KEY environment variable')
        return
    
    # List available tools
    tools = await server.list_tools()
    print(f"Available tools: {[t.name for t in tools]}")
    
    # Test image generation
    print("\n--- Testing Image Generation ---")
    result = await call_tool("generate_image", {
        "prompt": "A beautiful sunset over mountains, digital art style",
        "model": "fal-ai/flux/schnell"
    })
    print(result[0].text)

if __name__ == "__main__":
    asyncio.run(test())
