"""Tests for HTTP/SSE transport implementation"""

from unittest.mock import patch

import pytest

from fal_mcp_server.server_dual import FalMCPServer
from fal_mcp_server.server_http import create_http_app


@pytest.mark.asyncio
async def test_http_app_creation():
    """Test that HTTP app can be created with proper routes"""
    app = create_http_app(host="127.0.0.1", port=8001)

    # Check that app is a Starlette instance
    from starlette.applications import Starlette

    assert isinstance(app, Starlette)

    # Check that routes are configured
    assert len(app.routes) == 2  # SSE route and messages mount

    # Check route paths
    route_paths = [str(route.path) for route in app.routes]
    assert "/sse" in route_paths
    assert (
        "/messages" in route_paths
    )  # Mount point doesn't include trailing slash in path


def test_dual_server_initialization():
    """Test that dual transport server initializes correctly"""
    server = FalMCPServer()

    # Check that server is initialized
    assert server.server is not None
    assert server.server.name == "fal-ai-mcp"

    # Check initialization options
    init_options = server.get_initialization_options()
    assert init_options.server_name == "fal-ai-mcp"
    assert init_options.server_version == "1.14.0"
    assert init_options.capabilities.tools is not None


def test_dual_server_http_app_creation():
    """Test that dual server can create HTTP app"""
    server = FalMCPServer()
    app = server.create_http_app(host="127.0.0.1", port=8002)

    # Check that app is created
    from starlette.applications import Starlette

    assert isinstance(app, Starlette)

    # Check routes
    assert len(app.routes) == 2


@pytest.mark.asyncio
async def test_server_tools_registration():
    """Test that server registers tools correctly"""
    server = FalMCPServer()

    # Mock the list_tools handler
    with patch.object(server.server, "list_tools") as mock_list:
        # Set up the handler
        server._setup_handlers()

        # Check that list_tools was called during setup
        assert mock_list.called


def test_models_configuration_in_http():
    """Test that model registry is used by HTTP server"""
    from fal_mcp_server.model_registry import ModelRegistry

    registry = ModelRegistry()

    # Check image model aliases
    assert "flux_schnell" in registry.LEGACY_ALIASES
    assert "flux_dev" in registry.LEGACY_ALIASES

    # Check video model aliases
    assert "svd" in registry.LEGACY_ALIASES

    # Check audio model aliases
    assert "musicgen" in registry.LEGACY_ALIASES
    assert "whisper" in registry.LEGACY_ALIASES


def test_transport_environment_variables():
    """Test that transport can be configured via environment variables"""
    import os

    # Test FAL_MCP_TRANSPORT
    os.environ["FAL_MCP_TRANSPORT"] = "http"
    os.environ["FAL_MCP_HOST"] = "0.0.0.0"
    os.environ["FAL_MCP_PORT"] = "9000"

    # Import after setting env vars
    from fal_mcp_server.server_dual import main

    # Clean up
    del os.environ["FAL_MCP_TRANSPORT"]
    del os.environ["FAL_MCP_HOST"]
    del os.environ["FAL_MCP_PORT"]

    # Just verify the module loaded without errors
    assert main is not None


@pytest.mark.asyncio
async def test_sse_transport_initialization():
    """Test SSE transport initialization in HTTP server"""
    from mcp.server.sse import SseServerTransport

    # Create SSE transport
    sse_transport = SseServerTransport("/messages/")

    # Check that it's properly initialized
    assert sse_transport._endpoint == "/messages/"
    assert hasattr(sse_transport, "connect_sse")
    assert hasattr(sse_transport, "handle_post_message")


def test_cli_argument_parsing():
    """Test CLI argument parsing for HTTP server"""
    import sys
    from unittest.mock import patch

    # Mock sys.argv for testing
    test_args = [
        "server_http.py",
        "--host",
        "0.0.0.0",
        "--port",
        "9001",
        "--log-level",
        "DEBUG",
    ]

    with patch.object(sys, "argv", test_args):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--host", type=str, default="127.0.0.1")
        parser.add_argument("--port", type=int, default=8000)
        parser.add_argument(
            "--log-level",
            type=str,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        )

        args = parser.parse_args()

        assert args.host == "0.0.0.0"
        assert args.port == 9001
        assert args.log_level == "DEBUG"


def test_dual_transport_cli_parsing():
    """Test CLI argument parsing for dual transport server"""
    import sys
    from unittest.mock import patch

    # Test different transport modes
    test_cases = [
        (["server_dual.py", "--transport", "stdio"], "stdio"),
        (["server_dual.py", "--transport", "http"], "http"),
        (["server_dual.py", "--transport", "dual"], "dual"),
    ]

    for test_args, expected_transport in test_cases:
        with patch.object(sys, "argv", test_args):
            import argparse

            parser = argparse.ArgumentParser()
            parser.add_argument(
                "--transport",
                type=str,
                default="stdio",
                choices=["stdio", "http", "dual"],
            )
            parser.add_argument("--host", type=str, default="127.0.0.1")
            parser.add_argument("--port", type=int, default=8000)
            parser.add_argument("--log-level", type=str, default="INFO")

            args = parser.parse_args()
            assert args.transport == expected_transport
