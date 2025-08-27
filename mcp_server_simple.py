#!/usr/bin/env python3
"""Simplified MCP Server for Fal.ai that works with Python 3.9"""

import sys
import json
import asyncio
import os
from typing import Dict, Any, List

# Since MCP requires Python 3.10+, we'll create a simple stdin/stdout protocol
# that mimics MCP behavior

os.environ['FAL_KEY'] = '5ba82550-c252-4430-90d9-68adbaeb731d:b2107824b055c4fd157c1d2ac0b0fccc'

try:
    import fal_client
except ImportError:
    print(json.dumps({'error': 'fal_client not installed'}))
    sys.exit(1)

def generate_image(prompt: str, model: str = 'fal-ai/flux/schnell') -> Dict:
    try:
        result = fal_client.run(
            model,
            arguments={'prompt': prompt}
        )
        if 'images' in result and result['images']:
            return {
                'success': True,
                'url': result['images'][0]['url'],
                'message': f'Generated image: {result["images"][0]["url"]}'
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    return {'success': False, 'error': 'No image generated'}

def main():
    # Simple request/response loop
    while True:
        try:
            line = input()
            if not line:
                continue
                
            request = json.loads(line)
            
            if request.get('method') == 'generate_image':
                response = generate_image(
                    request.get('prompt', 'A beautiful landscape'),
                    request.get('model', 'fal-ai/flux/schnell')
                )
            else:
                response = {'error': 'Unknown method'}
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except EOFError:
            break
        except Exception as e:
            print(json.dumps({'error': str(e)}))
            sys.stdout.flush()

if __name__ == '__main__':
    main()
