"""Basic Docker tests that work in CI environment"""

import os


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

    # Check for required elements (version-agnostic)
    assert "FROM python:" in content
    assert "-slim" in content
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


def test_dockerfile_build_stages():
    """Test Dockerfile has proper multi-stage build"""
    with open("Dockerfile", "r") as f:
        content = f.read()

    # Check for multi-stage build (version-agnostic)
    assert "AS builder" in content
    assert "FROM python:" in content and "AS builder" in content
    assert "COPY --from=builder" in content


def test_dockerfile_security():
    """Test Dockerfile follows security best practices"""
    with open("Dockerfile", "r") as f:
        content = f.read()

    # Check security practices
    assert "USER mcp" in content  # Non-root user
    assert "useradd" in content  # User creation
    assert "--no-cache-dir" in content  # No pip cache


def test_docker_compose_environment():
    """Test docker-compose.yml environment configuration"""
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    # Check environment variables
    assert "FAL_KEY" in content
    assert "FAL_MCP_TRANSPORT" in content
    assert "FAL_MCP_HOST" in content
    assert "FAL_MCP_PORT" in content
