# Fal MCP Server

## Project Overview
An MCP (Model Context Protocol) server that integrates with Fal.ai's API to provide AI-powered image, video, and audio generation capabilities to Claude and other MCP-compatible clients.

## Core Features
- **Image Generation**: Multiple models including Flux, Recraft, Stable Diffusion
- **Video Generation**: AnimateDiff, CogVideoX, LTX Video models  
- **Audio Generation**: MusicGen for music composition
- **Async Architecture**: Native async operations with queue support for long-running tasks

## Technical Stack
- Python 3.10+
- MCP SDK for server implementation
- Fal.ai client SDK for AI model access
- Asyncio for concurrent operations
- Queue-based polling for video/music generation

## Architecture Highlights
- Single-file server implementation (`src/fal_mcp_server/server.py`)
- Fast operations use `run_async()` 
- Long operations use `submit_async()` with queue polling
- Environment-based configuration (FAL_KEY required)

## Current Status
- Core functionality implemented and working
- Supports all major Fal.ai model categories
- Ready for deployment and integration