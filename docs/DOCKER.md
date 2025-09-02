---
layout: page
title: Docker Deployment - Fal MCP Server
description: Deploy Fal MCP Server using the official Docker image from GitHub Container Registry with comprehensive transport mode support.
keywords: Docker, container, GitHub Packages, deployment, Fal MCP Server
---

# Docker Support

**🎉 Official Docker image now available on GitHub Container Registry!**

[![Docker Image](https://img.shields.io/badge/Docker-ghcr.io-blue?logo=docker)](https://github.com/raveenb/fal-mcp-server/pkgs/container/fal-mcp-server)
[![Image Size](https://img.shields.io/badge/Size-~150MB-green)](https://github.com/raveenb/fal-mcp-server/pkgs/container/fal-mcp-server)

The Fal MCP Server provides comprehensive Docker support with multi-transport capabilities, allowing you to run the server in various configurations without local Python installation.

## Quick Start

### Using Docker Compose (Recommended)

1. Create a `.env` file with your FAL API key:
```bash
echo "FAL_KEY=your-fal-api-key-here" > .env
```

2. Start the HTTP/SSE server:
```bash
docker-compose up -d
```

3. Access the server at `http://localhost:8080/sse`

### Using Docker Run

Run the HTTP server:
```bash
docker run -d \
  -e FAL_KEY=your-fal-api-key \
  -p 8080:8080 \
  ghcr.io/raveenb/fal-mcp-server:latest
```

## Available Images

**✅ Official images are published to GitHub Container Registry with every release!**

Pull the official image:
```bash
docker pull ghcr.io/raveenb/fal-mcp-server:latest
```

Available tags:
- `ghcr.io/raveenb/fal-mcp-server:latest` - Latest stable release (recommended)
- `ghcr.io/raveenb/fal-mcp-server:v0.3.0` - Specific version for production
- `ghcr.io/raveenb/fal-mcp-server:v0.2.0` - Previous stable version
- `ghcr.io/raveenb/fal-mcp-server:main` - Latest development build

## Transport Modes

### HTTP/SSE Mode (Default)
The default mode for Docker containers. Provides web-based access via Server-Sent Events.

```bash
docker run -d \
  -e FAL_KEY=your-key \
  -e FAL_MCP_TRANSPORT=http \
  -e FAL_MCP_HOST=0.0.0.0 \
  -e FAL_MCP_PORT=8080 \
  -p 8080:8080 \
  ghcr.io/raveenb/fal-mcp-server:latest
```

### STDIO Mode
For command-line integration and debugging.

```bash
docker run -it \
  -e FAL_KEY=your-key \
  -e FAL_MCP_TRANSPORT=stdio \
  ghcr.io/raveenb/fal-mcp-server:latest
```

### Dual Mode
Runs both STDIO and HTTP transports simultaneously.

```bash
docker run -it \
  -e FAL_KEY=your-key \
  -e FAL_MCP_TRANSPORT=dual \
  -e FAL_MCP_PORT=8081 \
  -p 8081:8081 \
  ghcr.io/raveenb/fal-mcp-server:latest
```

## Docker Compose Configuration

The `docker-compose.yml` file provides three pre-configured services:

### HTTP Service (Default)
```yaml
services:
  fal-mcp-http:
    image: ghcr.io/raveenb/fal-mcp-server:latest
    environment:
      - FAL_KEY=${FAL_KEY}
      - FAL_MCP_TRANSPORT=http
    ports:
      - "8080:8080"
```

### Dual Transport Service
Uncomment in `docker-compose.yml` to use:
```yaml
services:
  fal-mcp-dual:
    image: ghcr.io/raveenb/fal-mcp-server:latest
    environment:
      - FAL_KEY=${FAL_KEY}
      - FAL_MCP_TRANSPORT=dual
    ports:
      - "8081:8081"
    stdin_open: true
    tty: true
```

### STDIO Service
For debugging and command-line use:
```yaml
services:
  fal-mcp-stdio:
    image: ghcr.io/raveenb/fal-mcp-server:latest
    environment:
      - FAL_KEY=${FAL_KEY}
      - FAL_MCP_TRANSPORT=stdio
    stdin_open: true
    tty: true
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FAL_KEY` | Your Fal.ai API key (required) | - |
| `FAL_MCP_TRANSPORT` | Transport mode: `http`, `stdio`, or `dual` | `http` |
| `FAL_MCP_HOST` | Host to bind HTTP server | `0.0.0.0` |
| `FAL_MCP_PORT` | Port for HTTP server | `8080` |

## Building Locally

### Build the Image
```bash
docker build -t fal-mcp-server:local .
```

### Build with Docker Compose
```bash
docker-compose build
```

### Multi-Platform Build
Build for both AMD64 and ARM64:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t fal-mcp-server:local .
```

## Health Checks

The Docker image includes built-in health checks for HTTP mode:
```bash
# Check container health
docker ps
docker inspect --format='{{.State.Health.Status}}' fal-mcp-http

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' fal-mcp-http
```

## Container Management

### View Logs
```bash
# Docker Compose
docker-compose logs -f fal-mcp-http

# Docker
docker logs -f <container-id>
```

### Stop Services
```bash
# Docker Compose
docker-compose down

# Docker
docker stop <container-id>
```

### Remove Containers and Networks
```bash
docker-compose down --volumes --remove-orphans
```

## Security Features

- **Non-root user**: Containers run as user `mcp` (UID 1000) for enhanced security
- **Minimal base image**: Uses Python 3.11-slim for reduced attack surface
- **Multi-stage build**: Optimizes image size and excludes build dependencies
- **Health checks**: Automatic container health monitoring
- **Network isolation**: Custom bridge network for service communication

## Troubleshooting

### Container Won't Start
Check if FAL_KEY is set:
```bash
docker logs fal-mcp-http
```

### Port Already in Use
Change the port mapping:
```bash
docker run -p 9000:8080 ghcr.io/raveenb/fal-mcp-server:latest
```

### Permission Denied
Ensure Docker daemon is running and you have permissions:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Memory Issues
Limit container memory usage:
```bash
docker run -m 512m ghcr.io/raveenb/fal-mcp-server:latest
```

## Integration with MCP Clients

### Claude Desktop
Configure Claude Desktop to use the Docker HTTP server:
```json
{
  "fal-ai": {
    "command": "curl",
    "args": ["-N", "http://localhost:8080/sse"]
  }
}
```

### Custom Client Integration
Connect to the SSE endpoint:
```python
import requests

response = requests.get('http://localhost:8080/sse', stream=True)
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## Development Workflow

1. Make changes to the code
2. Build locally: `docker build -t test .`
3. Test: `docker run --rm -e FAL_KEY=$FAL_KEY test`
4. Run tests in container: `docker run --rm test pytest`
5. Push changes and let CI build official images

## CI/CD Integration

The Docker workflow automatically:
- Builds images on every push to main
- Creates tagged releases for version tags
- Publishes to GitHub Container Registry
- Supports multi-platform builds (AMD64/ARM64)
- Runs tests before publishing

See `.github/workflows/docker.yml` for details.