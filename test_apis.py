#!/usr/bin/env python3
import asyncio
import os
import sys
import time
sys.path.insert(0, 'src')

os.environ['FAL_KEY'] = '5ba82550-c252-4430-90d9-68adbaeb731d:b2107824b055c4fd157c1d2ac0b0fccc'

from fal_mcp_server.server import call_tool

async def test_apis():
    print("Testing Fal.ai MCP Server - Async & Queue APIs")
    print("=" * 60)
    
    # Test 1: Image Generation (Async API)
    print("
1. Testing Image Generation (should use async):")
    start = time.time()
    result = await call_tool('generate_image', {
        'prompt': 'A simple test pattern',
        'model': 'flux_schnell'
    })
    print(f"   Time: {time.time() - start:.2f}s")
    print(f"   Result: {result[0].text[:150]}...")
    
    # Test 2: Music Generation (Queue API) 
    print("
2. Testing Music Generation (should use queue):")
    start = time.time()
    result = await call_tool('generate_music', {
        'prompt': 'Short test music',
        'duration_seconds': 5
    })
    print(f"   Time: {time.time() - start:.2f}s")
    print(f"   Result: {result[0].text[:150]}...")
    
    print("
✅ Tests completed! Check for '(async)' and '(via queue)' markers.")

asyncio.run(test_apis())
