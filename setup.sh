#!/bin/bash
# Setup script for Fal.ai MCP Server

echo 'Setting up Fal.ai MCP Server...'

# Make sure directories exist
mkdir -p ~/Desktop/fal-mcp-server/src/fal_mcp_server

# Create __init__.py
echo '"""Fal.ai MCP Server"""
__version__ = "0.1.0"' > ~/Desktop/fal-mcp-server/src/fal_mcp_server/__init__.py

# Create fal_mcp.py
echo '#!/usr/bin/env python3
from fal_mcp_server.server import main

if __name__ == "__main__":
    main()' > ~/Desktop/fal-mcp-server/fal_mcp.py

# Make executable
chmod +x ~/Desktop/fal-mcp-server/fal_mcp.py

echo 'Basic files created. Please copy the server.py content from the artifacts above.'
echo 'Location: ~/Desktop/fal-mcp-server/src/fal_mcp_server/server.py'
