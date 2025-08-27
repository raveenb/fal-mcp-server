#!/usr/bin/env python3
"""
Basic usage example for Fal.ai MCP Server
This shows how to test the server functionality directly
"""

import os
import asyncio
import sys
sys.path.insert(0, '../src')

from fal_mcp_server.server import server, call_tool

async def main():
    # Make sure to set your API key
    if not os.getenv('FAL_KEY'):
        print('Please set FAL_KEY environment variable')
        return
    
    print('🎨 Fal.ai MCP Server Examples')
    print('=' * 40)
    
    # List available tools
    tools = await server.list_tools()
    print(f'Available tools: {[t.name for t in tools]}')
    
    # Example 1: Generate an image
    print('\n1. Generating an image...')
    result = await call_tool('generate_image', {
        'prompt': 'A serene mountain landscape at dawn',
        'model': 'flux_schnell',
        'num_images': 1
    })
    print(result[0].text)
    
    # Example 2: Generate music
    print('\n2. Generating music...')
    result = await call_tool('generate_music', {
        'prompt': 'Calm ambient piano music',
        'duration_seconds': 10
    })
    print(result[0].text)

if __name__ == '__main__':
    asyncio.run(main())
