---
layout: page
title: API Documentation - Fal MCP Server
description: Complete API reference for Fal MCP Server tools. Learn how to generate images, videos, and audio using Claude with detailed parameters and examples.
keywords: Fal MCP API, generate_image, generate_video, generate_music, MCP tools, Claude tools
---

# API Documentation

Complete reference for all Fal MCP Server tools available in Claude.

## Available Tools

The Fal MCP Server provides three main tools that Claude can use:

### 🎨 generate_image

Generate images from text descriptions using various AI models.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ Yes | - | Text description of the image to generate |
| `model` | string | No | `flux_schnell` | Model to use for generation |
| `negative_prompt` | string | No | - | What to avoid in the image |
| `image_size` | string | No | `landscape_16_9` | Aspect ratio of the image |
| `num_images` | integer | No | 1 | Number of images to generate (1-4) |
| `seed` | integer | No | random | Seed for reproducible generation |

#### Available Models

- **flux_schnell** - Fastest generation, good quality
- **flux_dev** - Better quality, slower generation
- **flux_pro** - Professional quality, requires Pro API
- **sdxl** - Stable Diffusion XL
- **stable_diffusion** - Stable Diffusion v3

#### Image Sizes

- `square` - 1:1 aspect ratio
- `landscape_4_3` - 4:3 aspect ratio
- `landscape_16_9` - 16:9 aspect ratio (default)
- `portrait_3_4` - 3:4 aspect ratio  
- `portrait_9_16` - 9:16 aspect ratio

#### Example Usage

```json
{
  "tool": "generate_image",
  "arguments": {
    "prompt": "A serene mountain landscape at sunset with a lake",
    "model": "flux_dev",
    "image_size": "landscape_16_9",
    "num_images": 2,
    "negative_prompt": "people, buildings, text"
  }
}
```

#### Response

```json
{
  "type": "text",
  "text": "🎨 Generated 2 image(s) with flux_dev:\n\nImage 1: https://fal.ai/generated/image1.jpg\nImage 2: https://fal.ai/generated/image2.jpg"
}
```

---

### 🎬 generate_video

Transform static images into dynamic videos using AI models.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_url` | string | ✅ Yes | - | URL of the starting image |
| `model` | string | No | `svd` | Video generation model |
| `duration` | integer | No | 4 | Video duration in seconds (2-10) |

#### Available Models

- **svd** - Stable Video Diffusion (default)
- **animatediff** - Fast AnimateDiff
- **kling** - Kling Video model

#### Example Usage

```json
{
  "tool": "generate_video",
  "arguments": {
    "image_url": "https://example.com/image.jpg",
    "model": "svd",
    "duration": 5
  }
}
```

#### Response

```json
{
  "type": "text",
  "text": "🎬 Video generated (via queue): https://fal.ai/generated/video.mp4"
}
```

#### Processing Notes

- Video generation uses queue API for long processing
- Typical generation time: 30-60 seconds
- Progress updates provided during generation
- Maximum duration varies by model

---

### 🎵 generate_music

Generate music and audio from text descriptions.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ Yes | - | Description of the music (genre, mood, instruments) |
| `duration_seconds` | integer | No | 30 | Duration in seconds (5-300) |
| `model` | string | No | `musicgen` | Music generation model |

#### Available Models

- **musicgen** - MusicGen Medium (default)
- **musicgen_large** - MusicGen Large, higher quality

#### Example Usage

```json
{
  "tool": "generate_music",
  "arguments": {
    "prompt": "Upbeat electronic dance music with synthesizers",
    "duration_seconds": 45,
    "model": "musicgen_large"
  }
}
```

#### Response

```json
{
  "type": "text",
  "text": "🎵 Generated 45s of music (via queue): https://fal.ai/generated/audio.wav"
}
```

---

## Performance Characteristics

### Fast Operations (Async API)

**generate_image** with `flux_schnell`:
- Processing time: 2-3 seconds
- Direct async API call
- Immediate response

### Queue Operations

**generate_video** and **generate_music**:
- Processing time: 20-60 seconds
- Queue-based processing
- Progress tracking available
- Automatic retry on failure

---

## Error Handling

The server handles various error conditions:

### Authentication Errors

```json
{
  "type": "text",
  "text": "❌ Error: FAL_KEY environment variable not set!"
}
```

### Timeout Errors

```json
{
  "type": "text",
  "text": "❌ Error: Timeout after 300 seconds"
}
```

### Invalid Parameters

```json
{
  "type": "text",
  "text": "❌ Error: Invalid model 'unknown_model'"
}
```

---

## Rate Limits

Fal.ai API rate limits apply:

| Tier | Images/min | Videos/min | Audio/min |
|------|------------|------------|-----------|
| Free | 10 | 2 | 5 |
| Starter | 60 | 10 | 30 |
| Pro | 300 | 50 | 100 |

---

## Best Practices

### 1. Model Selection

- Use `flux_schnell` for quick iterations
- Use `flux_dev` or `flux_pro` for final quality
- Choose `sdxl` for specific artistic styles

### 2. Prompt Engineering

```python
# Good prompt
"A detailed oil painting of a mountain landscape at golden hour, 
dramatic lighting, highly detailed, artstation quality"

# Better with negative prompt
negative_prompt: "low quality, blurry, watermark, text"
```

### 3. Batch Generation

Generate multiple variations efficiently:

```python
# Generate 4 variations with same prompt
num_images: 4
```

### 4. Seed Control

For reproducible results:

```python
# Use fixed seed
seed: 12345
```

---

## Integration Examples

### Claude Desktop

In Claude, you can naturally request generation:

```
User: Create an image of a futuristic city

Claude: I'll generate a futuristic city image for you.
[Uses generate_image tool with appropriate parameters]
```

### Programmatic Access

Using the MCP protocol directly:

```python
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "generate_image",
    "arguments": {
      "prompt": "futuristic city skyline"
    }
  }
}
```

---

## Transport Modes

### STDIO Mode

Default mode for Claude Desktop:
- Direct process communication
- No network overhead
- Fastest response time

### HTTP/SSE Mode

For web integrations:
- Server-Sent Events for streaming
- RESTful endpoints
- CORS support

### Dual Mode

Best of both worlds:
- STDIO for Claude Desktop
- HTTP for web access
- Single configuration

---

## Troubleshooting

### Common Issues

**No response from tool**
- Check FAL_KEY is set correctly
- Verify network connectivity
- Check server logs for errors

**Slow generation**
- Normal for video/music (20-60s)
- Check Fal.ai service status
- Consider using faster models

**Quality issues**
- Improve prompt specificity
- Use negative prompts
- Try different models

---

## API Changelog

### v0.4.0 (Latest)
- Added Docker support
- HTTP/SSE transport mode
- Dual transport mode

### v0.3.0
- Native async API integration
- Queue management improvements
- Better error handling

### v0.2.0
- Added music generation
- Extended video duration support
- Performance optimizations

### v0.1.0
- Initial release
- Basic image and video generation
- STDIO transport only

---

<div class="nav-buttons">
  <a href="{{ '/installation' | relative_url }}" class="btn">← Installation</a>
  <a href="{{ '/examples' | relative_url }}" class="btn btn-primary">Examples →</a>
</div>