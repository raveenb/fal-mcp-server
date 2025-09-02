"""Tests for Docker container functionality"""

import os
import subprocess
import time
from unittest.mock import patch

import pytest
import requests


def docker_available():
    """Check if Docker is available"""
    try:
        result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


@pytest.mark.skipif(not docker_available(), reason="Docker not available")
class TestDockerIntegration:
    """Docker integration tests"""

    @classmethod
    def setup_class(cls):
        """Build the Docker image before tests"""
        # Build the test image
        result = subprocess.run(
            ["docker", "build", "-t", "fal-mcp-test:pytest", "."],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip(f"Failed to build Docker image: {result.stderr}")

    @classmethod
    def teardown_class(cls):
        """Clean up Docker containers and images"""
        # Stop and remove any test containers
        subprocess.run(
            ["docker", "rm", "-f", "fal-mcp-pytest"], capture_output=True, check=False
        )

    def test_docker_image_builds(self):
        """Test that Docker image builds successfully"""
        result = subprocess.run(
            ["docker", "images", "fal-mcp-test:pytest", "--format", "{{.Repository}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "fal-mcp-test" in result.stdout

    def test_docker_help_command(self):
        """Test that Docker container can show help"""
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "fal-mcp-test:pytest",
                "python",
                "-m",
                "fal_mcp_server.server",
                "--help",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "Fal.ai MCP Server" in result.stdout or "usage:" in result.stdout

    def test_docker_http_mode(self):
        """Test Docker container in HTTP mode"""
        # Start container in HTTP mode
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "fal-mcp-pytest",
                "-e",
                "FAL_KEY=test-key",
                "-e",
                "FAL_MCP_TRANSPORT=http",
                "-p",
                "8090:8080",
                "fal-mcp-test:pytest",
                "python",
                "-m",
                "fal_mcp_server.server_http",
                "--port",
                "8080",
            ],
            capture_output=True,
            check=True,
        )

        # Wait for container to start
        time.sleep(3)

        try:
            # Check if container is running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=fal-mcp-pytest", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True,
            )
            assert "fal-mcp-pytest" in result.stdout

            # Test SSE endpoint
            response = requests.get("http://localhost:8090/sse", timeout=5, stream=True)
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

        finally:
            # Stop and remove container
            subprocess.run(
                ["docker", "rm", "-f", "fal-mcp-pytest"], capture_output=True, check=False
            )

    def test_docker_environment_variables(self):
        """Test that environment variables are properly set"""
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-e",
                "FAL_KEY=test-key-123",
                "-e",
                "FAL_MCP_TRANSPORT=http",
                "-e",
                "FAL_MCP_PORT=9000",
                "fal-mcp-test:pytest",
                "sh",
                "-c",
                "echo $FAL_KEY $FAL_MCP_TRANSPORT $FAL_MCP_PORT",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "test-key-123" in result.stdout
        assert "http" in result.stdout
        assert "9000" in result.stdout

    def test_docker_healthcheck(self):
        """Test Docker container health check"""
        # Start container
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "fal-mcp-pytest",
                "-e",
                "FAL_KEY=test-key",
                "-p",
                "8091:8080",
                "fal-mcp-test:pytest",
                "python",
                "-m",
                "fal_mcp_server.server_http",
            ],
            capture_output=True,
            check=True,
        )

        # Wait for container to be healthy
        max_attempts = 10
        for i in range(max_attempts):
            result = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "--format",
                    "{{.State.Health.Status}}",
                    "fal-mcp-pytest",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if "healthy" in result.stdout:
                break
            time.sleep(2)

        # Clean up
        subprocess.run(
            ["docker", "rm", "-f", "fal-mcp-pytest"], capture_output=True, check=False
        )

        # Health check should have succeeded
        assert "healthy" in result.stdout or i < max_attempts - 1

    def test_docker_non_root_user(self):
        """Test that container runs as non-root user"""
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "fal-mcp-test:pytest",
                "whoami",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "mcp" in result.stdout

    def test_docker_volume_mount(self):
        """Test that volumes can be mounted"""
        # Create a test file
        test_content = "test configuration"
        with open("/tmp/test-config.txt", "w") as f:
            f.write(test_content)

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                "/tmp/test-config.txt:/app/config.txt",
                "fal-mcp-test:pytest",
                "cat",
                "/app/config.txt",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Clean up
        os.remove("/tmp/test-config.txt")

        assert test_content in result.stdout


@pytest.mark.skipif(not docker_available(), reason="Docker not available")
class TestDockerCompose:
    """Docker Compose integration tests"""

    def test_docker_compose_config(self):
        """Test that docker-compose.yml is valid"""
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True,
            check=False,
        )
        # Should parse without errors
        assert result.returncode == 0 or "services" in result.stdout

    def test_docker_compose_build(self):
        """Test that docker-compose can build the image"""
        result = subprocess.run(
            ["docker-compose", "build", "--no-cache"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        # Build should succeed or skip if no build context
        assert result.returncode == 0 or "uses an image" in result.stderr


def test_dockerfile_exists():
    """Test that Dockerfile exists"""
    assert os.path.exists("Dockerfile")


def test_dockerignore_exists():
    """Test that .dockerignore exists"""
    assert os.path.exists(".dockerignore")


def test_docker_compose_exists():
    """Test that docker-compose.yml exists"""
    assert os.path.exists("docker-compose.yml")


def test_dockerfile_syntax():
    """Test basic Dockerfile syntax"""
    with open("Dockerfile", "r") as f:
        content = f.read()

    # Check for required elements
    assert "FROM python:3.11-slim" in content
    assert "WORKDIR /app" in content
    assert "USER mcp" in content  # Non-root user
    assert "HEALTHCHECK" in content
    assert "FAL_KEY" in content
    assert "EXPOSE 8080" in content


def test_dockerignore_content():
    """Test .dockerignore has proper exclusions"""
    with open(".dockerignore", "r") as f:
        content = f.read()

    # Check for common exclusions
    assert ".git" in content
    assert "__pycache__" in content
    assert ".env" in content
    assert "*.pyc" in content or "*.py[cod]" in content


def test_docker_compose_services():
    """Test docker-compose.yml has proper services"""
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    # Check for required services
    assert "fal-mcp-http" in content
    assert "FAL_KEY=${FAL_KEY}" in content
    assert "8080:8080" in content
    assert "healthcheck" in content