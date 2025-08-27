#!/usr/bin/env python3
"""Simple Fal.ai test without MCP"""

import os
import sys

# Test if we can import fal_client
try:
    import fal_client
    print('✅ fal_client installed successfully!')
    
    # Set API key
    os.environ['FAL_KEY'] = '5ba82550-c252-4430-90d9-68adbaeb731d:b2107824b055c4fd157c1d2ac0b0fccc'
    
    # Test image generation
    print('Testing image generation...')
    result = fal_client.run(
        'fal-ai/flux/schnell',
        arguments={
            'prompt': 'A beautiful sunset over mountains'
        }
    )
    
    if 'images' in result and result['images']:
        print(f"✅ Image generated: {result['images'][0]['url']}")
    else:
        print('❌ No image generated')
        
except ImportError:
    print('❌ fal_client not installed. Installing...')
    os.system('pip3 install fal-client --user')
    print('Please run this script again.')
except Exception as e:
    print(f'Error: {e}')
