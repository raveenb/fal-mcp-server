# Multi-stage Dockerfile for Fal MCP Server
# Supports both STDIO and HTTP/SSE transports

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./

# Create a temporary setup for package installation
COPY src ./src

# Install dependencies and the package
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash mcp && \
    mkdir -p /app && \
    chown -R mcp:mcp /app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=mcp:mcp . .

# Switch to non-root user
USER mcp

# Environment variables with defaults
ENV FAL_KEY="" \
    FAL_MCP_TRANSPORT="http" \
    FAL_MCP_HOST="0.0.0.0" \
    FAL_MCP_PORT="8080" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose HTTP port
EXPOSE 8080

# Health check for HTTP mode
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/sse').read()" || exit 1

# Default command - runs dual transport server
# Can be overridden for specific transport modes
CMD ["python", "-m", "fal_mcp_server.server_dual", \
     "--transport", "${FAL_MCP_TRANSPORT}", \
     "--host", "${FAL_MCP_HOST}", \
     "--port", "${FAL_MCP_PORT}"]

# Alternative commands (examples):
# For HTTP only:
#   docker run -e FAL_MCP_TRANSPORT=http ghcr.io/raveenb/fal-mcp-server
# For STDIO only:
#   docker run -e FAL_MCP_TRANSPORT=stdio ghcr.io/raveenb/fal-mcp-server
# For dual mode:
#   docker run -e FAL_MCP_TRANSPORT=dual ghcr.io/raveenb/fal-mcp-server