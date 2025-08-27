#!/usr/bin/env python3
"""
Tests for Fal.ai MCP Server
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, '../src')

@pytest.fixture
def mock_fal_client():
    with patch('fal_mcp_server.server.fal_client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_server_initialization():
    """Test that the server initializes correctly"""
    from fal_mcp_server.server import server
    assert server.name == "fal-ai-mcp"

@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools are listed correctly"""
    from fal_mcp_server.server import server
    
    tools = await server.list_tools()
    assert len(tools) > 0
    
    tool_names = [tool.name for tool in tools]
    assert 'generate_image' in tool_names
    assert 'generate_video' in tool_names
    assert 'generate_music' in tool_names

@pytest.mark.asyncio
async def test_generate_image_tool(mock_fal_client):
    """Test image generation tool"""
    from fal_mcp_server.server import call_tool
    
    # Mock the fal_client response
    mock_fal_client.run.return_value = {
        'images': [{'url': 'https://example.com/image.jpg'}]
    }
    
    result = await call_tool('generate_image', {
        'prompt': 'test image',
        'model': 'flux_schnell'
    })
    
    assert len(result) == 1
    assert 'Generated' in result[0].text
    assert 'https://example.com/image.jpg' in result[0].text

@pytest.mark.asyncio
async def test_missing_api_key():
    """Test error handling when API key is missing"""
    from fal_mcp_server.server import call_tool
    
    # Remove API key
    original_key = os.environ.pop('FAL_KEY', None)
    
    try:
        result = await call_tool('generate_image', {
            'prompt': 'test'
        })
        assert '❌ Error' in result[0].text or 'FAL_KEY' in result[0].text
    finally:
        # Restore API key if it existed
        if original_key:
            os.environ['FAL_KEY'] = original_key

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
