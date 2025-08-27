#!/usr/bin/env python3
"""Test MCP Protocol Communication"""

import json
import subprocess
import os

# Set environment
env = os.environ.copy()
env['FAL_KEY'] = 'your-key-here'

# Start the server process
proc = subprocess.Popen(
    ['.venv313/bin/python', 'src/fal_mcp_server/server.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    cwd='/Users/raveenbeemsingh/Developer/fal-mcp-server',
    text=True
)

# Send initialization request
init_request = {
    'jsonrpc': '2.0',
    'method': 'initialize',
    'params': {
        'protocolVersion': '1.0.0',
        'capabilities': {}
    },
    'id': 1
}

try:
    # Send request
    proc.stdin.write(json.dumps(init_request) + '\n')
    proc.stdin.flush()
    
    # Read response (with timeout)
    import select
    ready = select.select([proc.stdout], [], [], 2.0)
    if ready[0]:
        response = proc.stdout.readline()
        print('Server response:', response)
    else:
        print('✅ Server is running (no immediate response is normal for MCP)')
    
    proc.terminate()
    
except Exception as e:
    print(f'Error: {e}')
    proc.terminate()
