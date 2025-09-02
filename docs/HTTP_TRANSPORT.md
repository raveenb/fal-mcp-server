# HTTP/SSE Transport Documentation

The Fal.ai MCP Server now supports HTTP Server-Sent Events (SSE) transport in addition to the standard STDIO transport. This enables web-based clients, remote access, and better integration with cloud deployments.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Transport Modes](#transport-modes)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Examples](#examples)
- [Security Considerations](#security-considerations)

## Features

- **Multiple Transport Modes**: Choose between STDIO, HTTP/SSE, or dual mode
- **Server-Sent Events**: Real-time streaming communication with clients
- **Configurable Host/Port**: Bind to any network interface and port
- **Environment Variables**: Configure via environment variables or CLI
- **CORS Support**: Built-in CORS handling for browser-based clients
- **Concurrent Connections**: Handle multiple HTTP clients simultaneously

## Installation

The HTTP transport dependencies are included in the base installation:

```bash
pip install fal-mcp-server
```

Or install from source:

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

The package provides three command-line entry points:

1. **Standard STDIO server** (default):
```bash
fal-mcp
```

2. **HTTP/SSE server only**:
```bash
fal-mcp-http --host 0.0.0.0 --port 8000
```

3. **Dual transport server** (both STDIO and HTTP):
```bash
fal-mcp-dual --transport dual --host 0.0.0.0 --port 8000
```

### Python Module

You can also run the servers directly as Python modules:

```bash
# HTTP server
python -m fal_mcp_server.server_http --host 127.0.0.1 --port 8000

# Dual transport server
python -m fal_mcp_server.server_dual --transport dual --port 8000
```

## Transport Modes

### STDIO Transport (Default)
Traditional Model Context Protocol communication through standard input/output:
```bash
fal-mcp-dual --transport stdio
```

### HTTP/SSE Transport
HTTP server with Server-Sent Events for real-time communication:
```bash
fal-mcp-dual --transport http --host 0.0.0.0 --port 8000
```

### Dual Transport
Run both STDIO and HTTP transports simultaneously:
```bash
fal-mcp-dual --transport dual --host 0.0.0.0 --port 8000
```

## Configuration

### CLI Arguments

| Argument | Description | Default | Options |
|----------|-------------|---------|---------|
| `--transport` | Transport mode | `stdio` | `stdio`, `http`, `dual` |
| `--host` | HTTP server host | `127.0.0.1` | Any valid IP/hostname |
| `--port` | HTTP server port | `8000` | Any valid port number |
| `--log-level` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Environment Variables

Configure the server using environment variables:

```bash
export FAL_KEY="your-api-key"           # Fal.ai API key (required)
export FAL_MCP_TRANSPORT="http"         # Transport mode
export FAL_MCP_HOST="0.0.0.0"          # HTTP host
export FAL_MCP_PORT="8080"             # HTTP port
```

## API Endpoints

When running in HTTP mode, the server exposes the following endpoints:

### SSE Endpoint
- **URL**: `GET /sse`
- **Description**: Establishes Server-Sent Events connection for real-time communication
- **Headers**: 
  - `Accept: text/event-stream`
  - `Cache-Control: no-cache`

### Message Endpoint
- **URL**: `POST /messages/`
- **Description**: Receives client messages linked to an SSE session
- **Content-Type**: `application/json`
- **Body**: MCP protocol messages

## Examples

### Starting the HTTP Server

```bash
# Basic HTTP server
fal-mcp-http

# HTTP server on all interfaces
fal-mcp-http --host 0.0.0.0 --port 8080

# HTTP server with debug logging
fal-mcp-http --log-level DEBUG
```

### Using with Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install fal-mcp-server

EXPOSE 8000

# Run HTTP server
CMD ["fal-mcp-http", "--host", "0.0.0.0", "--port", "8000"]
```

### Connecting from a Web Client

```javascript
// Example JavaScript client
const eventSource = new EventSource('http://localhost:8000/sse');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send messages
fetch('http://localhost:8000/messages/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/list',
        id: 1
    })
});
```

### Using Dual Transport

Run both transports to support multiple client types:

```bash
# Terminal 1: Start dual transport server
fal-mcp-dual --transport dual --port 8000

# Terminal 2: Connect via STDIO
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | fal-mcp

# Browser: Connect via HTTP
# Navigate to http://localhost:8000/sse
```

## Security Considerations

### Network Binding
- Default binding is `127.0.0.1` (localhost only)
- Use `0.0.0.0` to accept connections from any interface
- Consider firewall rules when exposing to network

### API Key Management
- Store FAL_KEY securely in environment variables
- Never commit API keys to version control
- Use secrets management in production

### CORS Configuration
- The server includes basic CORS support
- Configure appropriate origins for production use
- Consider using a reverse proxy for additional security

### HTTPS/TLS
- For production, use a reverse proxy (nginx, caddy) with TLS
- Example with Caddy:
```
yourdomain.com {
    reverse_proxy localhost:8000
}
```

## Troubleshooting

### Server Won't Start
- Check if port is already in use: `lsof -i :8000`
- Verify FAL_KEY is set: `echo $FAL_KEY`
- Check firewall settings

### Connection Refused
- Verify server is running: `ps aux | grep fal-mcp`
- Check binding address (127.0.0.1 vs 0.0.0.0)
- Test with curl: `curl http://localhost:8000/sse`

### SSE Connection Drops
- Check client timeout settings
- Monitor server logs with `--log-level DEBUG`
- Verify network stability

## Advanced Usage

### Custom Integration

```python
from fal_mcp_server.server_dual import FalMCPServer

# Create server instance
server = FalMCPServer()

# Run with custom configuration
server.run_http(host="0.0.0.0", port=9000)
```

### Load Balancing

For high availability, run multiple instances behind a load balancer:

```nginx
upstream fal_mcp {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    location /sse {
        proxy_pass http://fal_mcp;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

## Performance Considerations

- HTTP/SSE adds minimal overhead compared to STDIO
- Supports hundreds of concurrent connections
- Use connection pooling for high-traffic scenarios
- Monitor memory usage with multiple clients

## Migration Guide

### From STDIO to HTTP

1. Install the latest version with HTTP support
2. Test HTTP mode locally: `fal-mcp-http`
3. Update client configuration to use HTTP endpoint
4. Deploy with appropriate network settings

### Backward Compatibility

- STDIO transport remains unchanged
- Existing integrations continue to work
- Dual mode allows gradual migration