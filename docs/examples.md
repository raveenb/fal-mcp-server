---
layout: page
title: Examples - Fal MCP Server
description: Real-world examples of using Fal MCP Server with Claude to generate images, videos, and audio. Copy-paste ready prompts and code.
keywords: Fal MCP examples, Claude AI examples, image generation examples, video generation examples, AI prompts
---

# Examples Gallery

Real-world examples of what you can create with Fal MCP Server and Claude.

## Image Generation Examples

### 🎨 Artistic Styles

#### Photorealistic Portrait
```
Generate a photorealistic portrait of a wise elderly person with kind eyes,
natural lighting, high detail, professional photography
```

#### Fantasy Landscape
```
Create a fantasy landscape with floating islands, waterfalls flowing into clouds,
bioluminescent plants, magical atmosphere, Studio Ghibli style
```

#### Cyberpunk Scene
```
Generate a cyberpunk street scene at night, neon lights, rain-slicked streets,
holographic advertisements, blade runner aesthetic
```

### 🏗️ Architecture & Design

#### Modern House
```
Design a modern minimalist house with large windows, concrete and wood materials,
surrounded by nature, architectural photography, golden hour lighting
```

#### Interior Design
```
Create an interior design of a cozy reading nook with built-in bookshelves,
warm lighting, comfortable chair, plants, scandinavian style
```

### 🎮 Game Assets

#### Character Design
```
Design a fantasy RPG character: elven archer with ornate armor,
detailed costume design, character sheet style, multiple angles
```

#### Environment Concept
```
Create a game environment concept: ancient temple ruins in a jungle,
overgrown with vines, mysterious atmosphere, concept art style
```

## Video Generation Examples

### 🎬 Animation from Images

#### Portrait Animation
```python
# First generate an image
image_prompt = "Portrait of a person with flowing hair, dramatic lighting"

# Then animate it
video_prompt = {
  "image_url": "generated_image_url",
  "model": "svd",
  "duration": 4
}
```

#### Landscape Motion
```python
# Generate a landscape
image_prompt = "Serene mountain lake at sunset, calm water"

# Add motion
video_prompt = {
  "image_url": "generated_image_url",
  "model": "animatediff",
  "duration": 5
}
```

## Music Generation Examples

### 🎵 Genre-Specific Music

#### Ambient Soundtrack
```
Generate 60 seconds of ambient electronic music, 
calm and atmospheric, suitable for meditation
```

#### Upbeat Pop
```
Create 30 seconds of upbeat pop music with catchy melody,
electronic drums, synthesizers, energetic
```

#### Classical Inspiration
```
Compose 45 seconds of classical-inspired piano music,
emotional and contemplative, minor key
```

### 🎮 Game Music

#### Battle Theme
```
Generate epic orchestral battle music, 
intense drums, brass section, 90 seconds
```

#### Exploration Theme
```
Create peaceful exploration music for an RPG,
acoustic instruments, celtic influence, 2 minutes
```

## Complete Workflows

### Workflow 1: Social Media Content

```markdown
User: Create a social media post about AI technology

Claude: I'll help you create engaging social media content about AI technology.

Step 1: Generate the main image
[Generates futuristic AI visualization]

Step 2: Create variations for carousel
[Generates 3 additional related images]

Result: Complete social media post with visuals ready!
```

### Workflow 2: Story Illustration

```markdown
User: Illustrate a short story about a magical forest

Claude: I'll create illustrations for your magical forest story.

Scene 1: The Entrance
[Generates mystical forest entrance]

Scene 2: The Discovery
[Generates glowing magical artifact in forest]

Scene 3: The Guardian
[Generates forest spirit character]

Video: Bringing it to life
[Animates the key scene]
```

### Workflow 3: Product Visualization

```markdown
User: Create product shots for a new smartwatch

Claude: I'll generate product visualizations for your smartwatch.

Hero Shot:
[Generates sleek smartwatch on gradient background]

Lifestyle Shot:
[Generates smartwatch on wrist in active scenario]

Feature Highlights:
[Generates close-up of watch face with UI]
```

## Advanced Techniques

### Prompt Engineering Tips

#### Be Specific
```
❌ "Generate a car"
✅ "Generate a vintage 1960s muscle car, cherry red, 
   parked in front of a retro diner, golden hour lighting"
```

#### Use Style References
```
"In the style of Studio Ghibli"
"Artstation trending"
"Unreal Engine render"
"Oil painting technique"
```

#### Negative Prompts
```python
prompt = "Beautiful landscape"
negative_prompt = "people, text, watermark, low quality, blurry"
```

### Model Selection Strategy

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Quick iteration | flux_schnell | 2-3 second generation |
| Final quality | flux_dev | Better details |
| Artistic style | sdxl | More artistic control |
| Video from image | svd | Most stable |
| Long music | musicgen_large | Better quality |

## Code Integration Examples

### Python Script
```python
import os
import subprocess

# Set API key
os.environ['FAL_KEY'] = 'your-key'

# Run server
subprocess.run(['fal-mcp'])
```

### Node.js Integration
```javascript
const { spawn } = require('child_process');

// Start MCP server
const mcp = spawn('fal-mcp', {
  env: {
    ...process.env,
    FAL_KEY: 'your-key'
  }
});
```

### Docker Compose
```yaml
version: '3.8'
services:
  fal-mcp:
    image: ghcr.io/raveenb/fal-mcp-server
    environment:
      - FAL_KEY=${FAL_KEY}
    ports:
      - "8080:8080"
```

## Batch Processing Examples

### Multiple Variations
```python
# Generate 4 variations of the same concept
for i in range(4):
    generate_image(
        prompt="Futuristic city skyline",
        seed=i * 1000  # Different seeds
    )
```

### Style Exploration
```python
styles = ["photorealistic", "anime", "oil painting", "watercolor"]
for style in styles:
    generate_image(
        prompt=f"Mountain landscape in {style} style"
    )
```

## Performance Optimization

### Fast Prototyping
```python
# Use schnell for quick iterations
model="flux_schnell"
image_size="square"  # Smaller = faster
num_images=1
```

### Production Quality
```python
# Use dev/pro for final output
model="flux_dev"
image_size="landscape_16_9"
num_images=4  # Generate options
```

## Troubleshooting Common Issues

### Issue: Blurry Images
**Solution**: Add quality modifiers
```
"highly detailed, sharp focus, 4k, high resolution"
```

### Issue: Wrong Style
**Solution**: Be more specific
```
"photorealistic" vs "cartoon" vs "oil painting"
```

### Issue: Unwanted Elements
**Solution**: Use negative prompts
```
negative_prompt="text, watermark, signature, border"
```

## Community Showcases

### User Creations

> "Used Fal MCP to generate all artwork for my indie game!" - @gamedev

> "Created an entire comic book with consistent characters" - @artist

> "Generated background music for my YouTube channel" - @creator

## Share Your Creations

Have you created something amazing with Fal MCP Server? Share it with the community:

- Tag us on Twitter: [@fal_ai](https://twitter.com/fal_ai)
- Join our [Discord](#)
- Submit to our [Gallery](https://github.com/raveenb/fal-mcp-server/discussions)

---

<div class="nav-buttons">
  <a href="{{ '/api' | relative_url }}" class="btn">← API Docs</a>
  <a href="{{ '/troubleshooting' | relative_url }}" class="btn btn-primary">Troubleshooting →</a>
</div>