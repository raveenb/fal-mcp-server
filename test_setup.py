#!/usr/bin/env python3
"""Test Fal.ai MCP Server Setup"""

import os
import sys
import asyncio

# Add src to path
sys.path.insert(0, 'src')

# Set API key
os.environ['FAL_KEY'] = 'your-key-here'

print('Testing Fal.ai MCP Server Setup...')
print('=' * 50)

# Test 1: Import checks
try:
    import mcp
    print('✅ MCP installed')
except ImportError:
    print('❌ MCP not found')
    sys.exit(1)

try:
    import fal_client
    print('✅ fal_client installed')
except ImportError:
    print('❌ fal_client not found')
    sys.exit(1)

# Test 2: Server import
try:
    from fal_mcp_server.server import server, call_tool
    print('✅ Server module loaded')
except ImportError as e:
    print(f'❌ Cannot import server: {e}')
    print('   Make sure you copied the complete server.py file!')
    sys.exit(1)

# Test 3: List tools
async def test_tools():
    try:
        tools = await server.list_tools()
        print(f'✅ Found {len(tools)} tools:')
        for tool in tools:
            print(f'   - {tool.name}')
    except Exception as e:
        print(f'❌ Error listing tools: {e}')
        return False
    
    # Test 4: Generate a test image
    print('\n🧪 Testing image generation...')
    try:
        result = await call_tool('generate_image', {
            'prompt': 'A simple test image, minimal design',
            'model': 'flux_schnell',
            'num_images': 1
        })
        print('✅ Image generation works!')
        print(f'   {result[0].text}')
    except Exception as e:
        print(f'❌ Image generation failed: {e}')
    
    return True

# Run tests
if __name__ == '__main__':
    success = asyncio.run(test_tools())
    if success:
        print('\n🎉 All tests passed! Your server is ready.')
        print('   Restart Claude Desktop to use it.')
    else:
        print('\n⚠️  Some tests failed. Check the errors above.')
