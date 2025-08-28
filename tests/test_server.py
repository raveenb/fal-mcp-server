#!/usr/bin/env python3
"""Basic tests for Fal.ai MCP Server"""

import sys
import os
sys.path.insert(0, '../src')

def test_import():
    """Test that the server can be imported"""
    try:
        from fal_mcp_server.server import server
        assert server.name == "fal-ai-mcp"
        print("✓ Server imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_models_config():
    """Test that model configurations are present"""
    try:
        from fal_mcp_server.server import MODELS
        assert "image" in MODELS
        assert "video" in MODELS
        assert "audio" in MODELS
        assert "flux_schnell" in MODELS["image"]
        print("✓ Model configurations present")
        return True
    except Exception as e:
        print(f"✗ Models config failed: {e}")
        return False

if __name__ == "__main__":
    tests_passed = 0
    tests_failed = 0
    
    if test_import():
        tests_passed += 1
    else:
        tests_failed += 1
    
    if test_models_config():
        tests_passed += 1
    else:
        tests_failed += 1
    
    print(f"
Tests: {tests_passed} passed, {tests_failed} failed")
    sys.exit(0 if tests_failed == 0 else 1)
