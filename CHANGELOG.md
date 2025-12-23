# CHANGELOG

<!-- version list -->

## v1.18.0 (2025-12-23)

### Bug Fixes

- Add pillow and httpx dependencies for compose_images
  ([#104](https://github.com/raveenb/fal-mcp-server/pull/104),
  [`4d28122`](https://github.com/raveenb/fal-mcp-server/commit/4d2812236554e55b2ad0659136c9a9683417527b))

- Address PR review issues for compose_images
  ([#104](https://github.com/raveenb/fal-mcp-server/pull/104),
  [`4d28122`](https://github.com/raveenb/fal-mcp-server/commit/4d2812236554e55b2ad0659136c9a9683417527b))

### Features

- Add compose_images tool for image compositing
  ([#104](https://github.com/raveenb/fal-mcp-server/pull/104),
  [`4d28122`](https://github.com/raveenb/fal-mcp-server/commit/4d2812236554e55b2ad0659136c9a9683417527b))


## v1.17.1 (2025-12-23)

### Bug Fixes

- Use image_urls array for Flux 2 Edit API
  ([`534d1e1`](https://github.com/raveenb/fal-mcp-server/commit/534d1e1ca9caf285136eef6270ec51a83f53309e))


## v1.17.0 (2025-12-23)

### Features

- Add image editing tools (remove_background, upscale, edit, inpaint, resize)
  ([`ba11278`](https://github.com/raveenb/fal-mcp-server/commit/ba112787a76ba088a8383f5b52d32428910a09f0))


## v1.16.4 (2025-12-23)

### Bug Fixes

- Update deprecated svd alias to fast-svd-lcm
  ([`4c4394c`](https://github.com/raveenb/fal-mcp-server/commit/4c4394c32b0707f437dad0399de3431088014b49))


## v1.16.3 (2025-12-23)

### Bug Fixes

- Remove unrecognized fields from plugin.json
  ([`acedd17`](https://github.com/raveenb/fal-mcp-server/commit/acedd17d47765053b26bdbe4a8774850e8678694))

### Chores

- Clean up Claude Code hooks and update startup reminders
  ([`c0dc441`](https://github.com/raveenb/fal-mcp-server/commit/c0dc44118db4071598e29c34d988b3852bdac8b3))

- Update uv.lock
  ([`588223a`](https://github.com/raveenb/fal-mcp-server/commit/588223ad4a28fb653341ef180f5a33a4fea15fc8))


## v1.16.2 (2025-12-23)

### Bug Fixes

- Update marketplace.json owner email
  ([`9d768d6`](https://github.com/raveenb/fal-mcp-server/commit/9d768d63b9b871fe29ccfc551edf11c6322527e4))

### Documentation

- Add Claude Code plugin installation instructions
  ([`c202c7c`](https://github.com/raveenb/fal-mcp-server/commit/c202c7c52e8dacbe7db497af0f38bd7a89d54bc3))


## v1.16.1 (2025-12-23)

### Bug Fixes

- Move plugin.json to correct location
  ([`9db5a75`](https://github.com/raveenb/fal-mcp-server/commit/9db5a75cb443f7eb65a7e5470306691d08e73066))


## v1.16.0 (2025-12-23)

### Features

- Add Luminary Lane Tools marketplace
  ([`1747fff`](https://github.com/raveenb/fal-mcp-server/commit/1747fff1546b92c760277b1568d6a4bbe227eb34))


## v1.15.0 (2025-12-23)

### Chores

- **deps**: Bump actions/checkout from 4 to 6
  ([#92](https://github.com/raveenb/fal-mcp-server/pull/92),
  [`4215eb3`](https://github.com/raveenb/fal-mcp-server/commit/4215eb3a5273ab7be214b4a1a002bf5428841827))

- **deps**: Bump actions/setup-python from 4 to 6
  ([#91](https://github.com/raveenb/fal-mcp-server/pull/91),
  [`ff7db94`](https://github.com/raveenb/fal-mcp-server/commit/ff7db9432c7cf22ff4b2dc3142f2b09342aa4f50))

### Documentation

- Add troubleshooting section and update tools list
  ([`2de3fcc`](https://github.com/raveenb/fal-mcp-server/commit/2de3fcc98d0129ac2591ba4caa9d41c992238766))

### Features

- Add Claude Code plugin manifest
  ([`95a333a`](https://github.com/raveenb/fal-mcp-server/commit/95a333a591d891ca24a52aa3a82e58088fada870))


## v1.14.0 (2025-12-22)

### Bug Fixes

- Improve error handling in video-to-video handler
  ([#90](https://github.com/raveenb/fal-mcp-server/pull/90),
  [`8cfc5d4`](https://github.com/raveenb/fal-mcp-server/commit/8cfc5d44cc0b29692eecb4a5df46d3afc89414e8))

### Features

- Add video-to-video transformation tool ([#90](https://github.com/raveenb/fal-mcp-server/pull/90),
  [`8cfc5d4`](https://github.com/raveenb/fal-mcp-server/commit/8cfc5d44cc0b29692eecb4a5df46d3afc89414e8))


## v1.13.1 (2025-12-22)

### Refactoring

- Convert server files to thin wrappers using shared handlers
  ([#86](https://github.com/raveenb/fal-mcp-server/pull/86),
  [`a42888d`](https://github.com/raveenb/fal-mcp-server/commit/a42888d567e75649de5bd32d5b90f35c4618ece7))


## v1.13.0 (2025-12-22)

### Bug Fixes

- Format test_model_registry.py with black
  ([#85](https://github.com/raveenb/fal-mcp-server/pull/85),
  [`cdcf8bb`](https://github.com/raveenb/fal-mcp-server/commit/cdcf8bb37119b150b464977a64d2dd11f6de72f3))

- Resolve mypy type errors in queue and handlers
  ([#85](https://github.com/raveenb/fal-mcp-server/pull/85),
  [`cdcf8bb`](https://github.com/raveenb/fal-mcp-server/commit/cdcf8bb37119b150b464977a64d2dd11f6de72f3))

### Features

- Fix musicgen alias and extract shared modules
  ([#85](https://github.com/raveenb/fal-mcp-server/pull/85),
  [`cdcf8bb`](https://github.com/raveenb/fal-mcp-server/commit/cdcf8bb37119b150b464977a64d2dd11f6de72f3))


## v1.12.1 (2025-12-22)

### Bug Fixes

- Add missing tools to HTTP/SSE transport servers
  ([#81](https://github.com/raveenb/fal-mcp-server/pull/81),
  [`ba37709`](https://github.com/raveenb/fal-mcp-server/commit/ba3770951d5da61527ed132a912aa80da441463f))

- Address code review feedback for PR #81 ([#81](https://github.com/raveenb/fal-mcp-server/pull/81),
  [`ba37709`](https://github.com/raveenb/fal-mcp-server/commit/ba3770951d5da61527ed132a912aa80da441463f))

### Code Style

- Apply Black formatting ([#81](https://github.com/raveenb/fal-mcp-server/pull/81),
  [`ba37709`](https://github.com/raveenb/fal-mcp-server/commit/ba3770951d5da61527ed132a912aa80da441463f))

- Fix import sorting (ruff I001) ([#81](https://github.com/raveenb/fal-mcp-server/pull/81),
  [`ba37709`](https://github.com/raveenb/fal-mcp-server/commit/ba3770951d5da61527ed132a912aa80da441463f))


## v1.12.0 (2025-12-22)

### Bug Fixes

- Add transparent fallback warnings when API search fails
  ([#80](https://github.com/raveenb/fal-mcp-server/pull/80),
  [`746c846`](https://github.com/raveenb/fal-mcp-server/commit/746c846dddc0cce8e6645bc0a729a08d631b0993))

- Resolve mypy type errors by renaming result variable
  ([#80](https://github.com/raveenb/fal-mcp-server/pull/80),
  [`746c846`](https://github.com/raveenb/fal-mcp-server/commit/746c846dddc0cce8e6645bc0a729a08d631b0993))

### Features

- Add intelligent model selection using Fal Platform API (#79)
  ([#80](https://github.com/raveenb/fal-mcp-server/pull/80),
  [`746c846`](https://github.com/raveenb/fal-mcp-server/commit/746c846dddc0cce8e6645bc0a729a08d631b0993))

- Add intelligent model selection with recommend_model tool and task-aware list_models
  ([#80](https://github.com/raveenb/fal-mcp-server/pull/80),
  [`746c846`](https://github.com/raveenb/fal-mcp-server/commit/746c846dddc0cce8e6645bc0a729a08d631b0993))


## v1.11.0 (2025-12-21)

### Bug Fixes

- Add timeout protection and error check to server.py
  ([#78](https://github.com/raveenb/fal-mcp-server/pull/78),
  [`69da03d`](https://github.com/raveenb/fal-mcp-server/commit/69da03d874bef3d828ed63e3fee026a8ce4574ea))

- Address PR review findings for generate_image_from_image
  ([#78](https://github.com/raveenb/fal-mcp-server/pull/78),
  [`69da03d`](https://github.com/raveenb/fal-mcp-server/commit/69da03d874bef3d828ed63e3fee026a8ce4574ea))

- Rename fal_args to img2img_args to fix mypy no-redef error
  ([#78](https://github.com/raveenb/fal-mcp-server/pull/78),
  [`69da03d`](https://github.com/raveenb/fal-mcp-server/commit/69da03d874bef3d828ed63e3fee026a8ce4574ea))

### Code Style

- Run black formatter ([#78](https://github.com/raveenb/fal-mcp-server/pull/78),
  [`69da03d`](https://github.com/raveenb/fal-mcp-server/commit/69da03d874bef3d828ed63e3fee026a8ce4574ea))

### Features

- Add generate_image_from_image tool for img2img transformation
  ([#78](https://github.com/raveenb/fal-mcp-server/pull/78),
  [`69da03d`](https://github.com/raveenb/fal-mcp-server/commit/69da03d874bef3d828ed63e3fee026a8ce4574ea))

- Add generate_image_from_image tool for img2img transformation (#65)
  ([#78](https://github.com/raveenb/fal-mcp-server/pull/78),
  [`69da03d`](https://github.com/raveenb/fal-mcp-server/commit/69da03d874bef3d828ed63e3fee026a8ce4574ea))


## v1.10.0 (2025-12-21)

### Bug Fixes

- Address PR review issues - error handling and logging
  ([#77](https://github.com/raveenb/fal-mcp-server/pull/77),
  [`72a15fb`](https://github.com/raveenb/fal-mcp-server/commit/72a15fb027f8df38770a1dd554a915132aac236c))

- Rename video_result to i2v_result to avoid mypy redefinition error
  ([#77](https://github.com/raveenb/fal-mcp-server/pull/77),
  [`72a15fb`](https://github.com/raveenb/fal-mcp-server/commit/72a15fb027f8df38770a1dd554a915132aac236c))

### Features

- Add generate_video_from_image tool for dedicated image-to-video
  ([#77](https://github.com/raveenb/fal-mcp-server/pull/77),
  [`72a15fb`](https://github.com/raveenb/fal-mcp-server/commit/72a15fb027f8df38770a1dd554a915132aac236c))


## v1.9.0 (2025-12-21)

### Bug Fixes

- Address PR review issues for upload_file tool
  ([#76](https://github.com/raveenb/fal-mcp-server/pull/76),
  [`833d76d`](https://github.com/raveenb/fal-mcp-server/commit/833d76d75e2c900995cc83849c33244906c4166b))

### Features

- Add upload_file tool for uploading local files (#64)
  ([#76](https://github.com/raveenb/fal-mcp-server/pull/76),
  [`833d76d`](https://github.com/raveenb/fal-mcp-server/commit/833d76d75e2c900995cc83849c33244906c4166b))

- Add upload_file tool for uploading local files to Fal.ai storage
  ([#76](https://github.com/raveenb/fal-mcp-server/pull/76),
  [`833d76d`](https://github.com/raveenb/fal-mcp-server/commit/833d76d75e2c900995cc83849c33244906c4166b))


## v1.8.2 (2025-12-21)

### Bug Fixes

- Make image_url optional in generate_video for text-to-video support
  ([#67](https://github.com/raveenb/fal-mcp-server/pull/67),
  [`5f27d5f`](https://github.com/raveenb/fal-mcp-server/commit/5f27d5f98f9d94341225571f8f7b3fa8d15b9475))


## v1.8.1 (2025-12-21)

### Bug Fixes

- Add optional video parameters and fix server_dual.py handler
  ([#59](https://github.com/raveenb/fal-mcp-server/pull/59),
  [`fef5fef`](https://github.com/raveenb/fal-mcp-server/commit/fef5fefe15d426a195e5d20af81775fc78353c6b))

- Add prompt parameter to generate_video and update default model
  ([#59](https://github.com/raveenb/fal-mcp-server/pull/59),
  [`fef5fef`](https://github.com/raveenb/fal-mcp-server/commit/fef5fefe15d426a195e5d20af81775fc78353c6b))


## v1.8.0 (2025-12-21)

### Bug Fixes

- Address PR review feedback for generate_image_structured
  ([#57](https://github.com/raveenb/fal-mcp-server/pull/57),
  [`8b52593`](https://github.com/raveenb/fal-mcp-server/commit/8b5259390cbba9c73988462610f3c5daac5b08fb))

### Features

- Add generate_image_structured tool for detailed AI-friendly prompts
  ([#57](https://github.com/raveenb/fal-mcp-server/pull/57),
  [`8b52593`](https://github.com/raveenb/fal-mcp-server/commit/8b5259390cbba9c73988462610f3c5daac5b08fb))


## v1.7.0 (2025-12-20)

### Bug Fixes

- Address PR review feedback for get_usage tool
  ([#53](https://github.com/raveenb/fal-mcp-server/pull/53),
  [`a241abf`](https://github.com/raveenb/fal-mcp-server/commit/a241abf33140ce137899fc2b2e16927e9bb01008))

### Features

- Add get_usage MCP tool for spending reports
  ([#53](https://github.com/raveenb/fal-mcp-server/pull/53),
  [`a241abf`](https://github.com/raveenb/fal-mcp-server/commit/a241abf33140ce137899fc2b2e16927e9bb01008))


## v1.6.0 (2025-12-20)

### Bug Fixes

- Add type annotation for httpx params to satisfy mypy
  ([#52](https://github.com/raveenb/fal-mcp-server/pull/52),
  [`aedbe96`](https://github.com/raveenb/fal-mcp-server/commit/aedbe963efb972d36e8aebf3d371c8f8fb62d633))

- Replace bare Exception catch with specific httpx exceptions
  ([#52](https://github.com/raveenb/fal-mcp-server/pull/52),
  [`aedbe96`](https://github.com/raveenb/fal-mcp-server/commit/aedbe963efb972d36e8aebf3d371c8f8fb62d633))

### Features

- Add get_pricing MCP tool for cost transparency
  ([#52](https://github.com/raveenb/fal-mcp-server/pull/52),
  [`aedbe96`](https://github.com/raveenb/fal-mcp-server/commit/aedbe963efb972d36e8aebf3d371c8f8fb62d633))


## v1.5.1 (2025-12-20)

### Bug Fixes

- Add timeout and error handling to subscribe_async calls
  ([#51](https://github.com/raveenb/fal-mcp-server/pull/51),
  [`bfa5b51`](https://github.com/raveenb/fal-mcp-server/commit/bfa5b51bb44e2f9281c42a2f3bf80888746e34ef))

### Refactoring

- Use subscribe_async for video/music generation
  ([#51](https://github.com/raveenb/fal-mcp-server/pull/51),
  [`bfa5b51`](https://github.com/raveenb/fal-mcp-server/commit/bfa5b51bb44e2f9281c42a2f3bf80888746e34ef))


## v1.5.0 (2025-12-20)

### Features

- **image**: Add enable_safety_checker and output_format parameters
  ([#50](https://github.com/raveenb/fal-mcp-server/pull/50),
  [`6cb8a29`](https://github.com/raveenb/fal-mcp-server/commit/6cb8a2909b1fcf680b766f6fbc293fddd3656407))


## v1.4.4 (2025-12-20)

### Bug Fixes

- Address PR review feedback for model registry
  ([#45](https://github.com/raveenb/fal-mcp-server/pull/45),
  [`dbcc245`](https://github.com/raveenb/fal-mcp-server/commit/dbcc2452ee6f116104b983de4153f251773b5505))

- Correct API response parsing for Fal.ai Platform API
  ([#45](https://github.com/raveenb/fal-mcp-server/pull/45),
  [`dbcc245`](https://github.com/raveenb/fal-mcp-server/commit/dbcc2452ee6f116104b983de4153f251773b5505))

- List_models returns fallback legacy aliases when API unavailable
  ([#45](https://github.com/raveenb/fal-mcp-server/pull/45),
  [`dbcc245`](https://github.com/raveenb/fal-mcp-server/commit/dbcc2452ee6f116104b983de4153f251773b5505))

### Code Style

- Fix Black formatting in model_registry.py
  ([#45](https://github.com/raveenb/fal-mcp-server/pull/45),
  [`dbcc245`](https://github.com/raveenb/fal-mcp-server/commit/dbcc2452ee6f116104b983de4153f251773b5505))

### Documentation

- Improve Docker setup instructions with clear steps
  ([`25b1b4d`](https://github.com/raveenb/fal-mcp-server/commit/25b1b4d94906695a7b8f8a0ccc65a589bab603d7))


## v1.4.3 (2025-12-20)

### Bug Fixes

- Correct uvx command syntax in README and .mcp.json
  ([`e2bf532`](https://github.com/raveenb/fal-mcp-server/commit/e2bf5327370927c870dc6df7eea02c23735b0741))

### Documentation

- Add documentation section to README with direct links
  ([`d0e13ac`](https://github.com/raveenb/fal-mcp-server/commit/d0e13ac6ea9aa469d574cdc9fd3a0f6aae0c8ae7))


## v1.4.2 (2025-12-20)

### Bug Fixes

- **docs**: Use correct Rouge class names for code block styling
  ([#40](https://github.com/raveenb/fal-mcp-server/pull/40),
  [`88617c2`](https://github.com/raveenb/fal-mcp-server/commit/88617c282a5a70608fd6c8194332197e5604d325))


## v1.4.1 (2025-12-20)

### Bug Fixes

- **docs**: Properly style Rouge syntax highlighter code blocks
  ([#38](https://github.com/raveenb/fal-mcp-server/pull/38),
  [`2c3331c`](https://github.com/raveenb/fal-mcp-server/commit/2c3331cef2183bf47d7bb53ff31eb8afcea63933))


## v1.4.0 (2025-12-20)

### Features

- **docs**: Add custom header with modern navigation design
  ([#37](https://github.com/raveenb/fal-mcp-server/pull/37),
  [`6bbc52a`](https://github.com/raveenb/fal-mcp-server/commit/6bbc52a778b606fd5c6827c7d70a6ef041e8f611))


## v1.3.2 (2025-12-20)

### Bug Fixes

- Move stylesheet to correct path for minima theme
  ([#36](https://github.com/raveenb/fal-mcp-server/pull/36),
  [`6d40cf6`](https://github.com/raveenb/fal-mcp-server/commit/6d40cf69b03166b2bdb85548b99d38d97faee2fd))

### Testing

- Update assets test for new stylesheet location
  ([#36](https://github.com/raveenb/fal-mcp-server/pull/36),
  [`6d40cf6`](https://github.com/raveenb/fal-mcp-server/commit/6d40cf69b03166b2bdb85548b99d38d97faee2fd))


## v1.3.1 (2025-12-20)

### Bug Fixes

- Repair GitHub Pages Jekyll configuration
  ([#35](https://github.com/raveenb/fal-mcp-server/pull/35),
  [`9b7ab27`](https://github.com/raveenb/fal-mcp-server/commit/9b7ab2709fd92b6c7bbe176a41154d69bed4556d))

### Chores

- Add Dependabot configuration for automated updates
  ([#27](https://github.com/raveenb/fal-mcp-server/pull/27),
  [`e880598`](https://github.com/raveenb/fal-mcp-server/commit/e880598385f5bc07ef06d59c437cbad3abfbb131))

- Upgrade Docker image to Python 3.13 with dynamic paths
  ([#33](https://github.com/raveenb/fal-mcp-server/pull/33),
  [`76453e7`](https://github.com/raveenb/fal-mcp-server/commit/76453e75b60e72fcef294d71902ca886dc5a3a6c))

- **deps**: Bump actions/configure-pages from 4 to 5
  ([#29](https://github.com/raveenb/fal-mcp-server/pull/29),
  [`7d4f78c`](https://github.com/raveenb/fal-mcp-server/commit/7d4f78c439df60c7ab1ac2722e582058c9205e71))

- **deps**: Bump actions/upload-pages-artifact from 3 to 4
  ([#30](https://github.com/raveenb/fal-mcp-server/pull/30),
  [`565251f`](https://github.com/raveenb/fal-mcp-server/commit/565251fce41c292cc0123d7b3e2a5e346198eba2))

- **deps**: Bump docker/build-push-action from 5 to 6
  ([#31](https://github.com/raveenb/fal-mcp-server/pull/31),
  [`7cd964b`](https://github.com/raveenb/fal-mcp-server/commit/7cd964b4a993ef1e8bd5e9eb373ce5b8d6bb171f))

### Testing

- Make Docker tests version-agnostic ([#33](https://github.com/raveenb/fal-mcp-server/pull/33),
  [`76453e7`](https://github.com/raveenb/fal-mcp-server/commit/76453e75b60e72fcef294d71902ca886dc5a3a6c))


## v1.3.0 (2025-12-19)

### Bug Fixes

- Use PAT for release workflow to bypass branch protection
  ([#25](https://github.com/raveenb/fal-mcp-server/pull/25),
  [`2b4d503`](https://github.com/raveenb/fal-mcp-server/commit/2b4d503c7b5c8df1edfe886d9d0254fef54ddd5e))

### Chores

- Add .serena/ to gitignore
  ([`cb2eb8b`](https://github.com/raveenb/fal-mcp-server/commit/cb2eb8bdeb65f9526bf5fd199a8fc049cfcf2214))

- Update uv.lock for dependency upgrades ([#26](https://github.com/raveenb/fal-mcp-server/pull/26),
  [`49da0c9`](https://github.com/raveenb/fal-mcp-server/commit/49da0c98a76598f2c5d455b0088b5c4b6ad1e59c))

- Upgrade dependency minimum versions ([#26](https://github.com/raveenb/fal-mcp-server/pull/26),
  [`49da0c9`](https://github.com/raveenb/fal-mcp-server/commit/49da0c98a76598f2c5d455b0088b5c4b6ad1e59c))

### Continuous Integration

- Add CODEOWNERS for automatic reviewer assignment
  ([`ffb3074`](https://github.com/raveenb/fal-mcp-server/commit/ffb307497469e2b08ee21867049728e53ed36c0a))

### Features

- Add uvx support and fix PyPI publishing
  ([`264d0af`](https://github.com/raveenb/fal-mcp-server/commit/264d0af36701d5c04c9c42c295d1403b3ddf70d0))


## v1.2.0 (2025-12-19)

### Bug Fixes

- Add missing asset directories for documentation
  ([#11](https://github.com/raveenb/fal-mcp-server/pull/11),
  [`b4556d1`](https://github.com/raveenb/fal-mcp-server/commit/b4556d198168a3999eb42e94cc61df3225cff940))

- Add proper logging and fix mypy type errors
  ([`42acd30`](https://github.com/raveenb/fal-mcp-server/commit/42acd309f37ea075d564576ee035070014ef90ca))

- Add pyyaml to dev dependencies for documentation tests
  ([#11](https://github.com/raveenb/fal-mcp-server/pull/11),
  [`b4556d1`](https://github.com/raveenb/fal-mcp-server/commit/b4556d198168a3999eb42e94cc61df3225cff940))

- Check only commit subject for skip-release marker
  ([`685d08a`](https://github.com/raveenb/fal-mcp-server/commit/685d08a05f22a06b834fd4228d35931137d2e778))

- Fix Docker CMD to expand environment variables
  ([`7ee4c7a`](https://github.com/raveenb/fal-mcp-server/commit/7ee4c7ab8d007327f26e43adaf238d6e48fff449))

- Fix ruff linting issues in test_docs.py ([#11](https://github.com/raveenb/fal-mcp-server/pull/11),
  [`b4556d1`](https://github.com/raveenb/fal-mcp-server/commit/b4556d198168a3999eb42e94cc61df3225cff940))

- Format test_docs.py with black ([#11](https://github.com/raveenb/fal-mcp-server/pull/11),
  [`b4556d1`](https://github.com/raveenb/fal-mcp-server/commit/b4556d198168a3999eb42e94cc61df3225cff940))

- Make Docker volume test more portable
  ([`936a789`](https://github.com/raveenb/fal-mcp-server/commit/936a789e04477d9219f1da6f25439a46ff2b21da))

- Remove unused imports
  ([`ae9b40a`](https://github.com/raveenb/fal-mcp-server/commit/ae9b40ad54b12ff85045ade3499f8e91d595756b))

- Resolve linting issues
  ([`8d18386`](https://github.com/raveenb/fal-mcp-server/commit/8d18386c2ca76c677f0ffb2b10475f05e7ce572a))

- Split Docker tests for CI compatibility
  ([`0a6f011`](https://github.com/raveenb/fal-mcp-server/commit/0a6f01188207d9be85e4c5d4f0d1acbb7f1ecad8))

- Update Docker documentation with GitHub Packages info and rename to lowercase
  ([#13](https://github.com/raveenb/fal-mcp-server/pull/13),
  [`f2cc106`](https://github.com/raveenb/fal-mcp-server/commit/f2cc10624def4d51de7cd221985716fdf1ae4b47))

- Update Docker tests for reliability
  ([`0691037`](https://github.com/raveenb/fal-mcp-server/commit/0691037e67f57f789edbf07e555cb59101de6075))

### Chores

- Update MCP server config and remove Cline rules files
  ([`ce9eb38`](https://github.com/raveenb/fal-mcp-server/commit/ce9eb3828d1d3de598307b9e1afdc5a924c10d79))

### Code Style

- Apply black formatting
  ([`1d97e39`](https://github.com/raveenb/fal-mcp-server/commit/1d97e396d026c061759bae49a6e524e8fbce5d44))

### Continuous Integration

- Add automated semantic release and Docker versioning
  ([`581c11e`](https://github.com/raveenb/fal-mcp-server/commit/581c11ea3c178b381e32e6dc42976e2f74978d3e))

- Add comprehensive Docker integration tests
  ([`190e80d`](https://github.com/raveenb/fal-mcp-server/commit/190e80deeb03c623992b11f5a5d647274a70bfd6))

### Documentation

- Add MCP directory submission documentation
  ([#12](https://github.com/raveenb/fal-mcp-server/pull/12),
  [`b62d87c`](https://github.com/raveenb/fal-mcp-server/commit/b62d87c2f1e04fddfef5afd83e9bd2777f083035))

- Document Docker environment variables in README
  ([`212cac9`](https://github.com/raveenb/fal-mcp-server/commit/212cac9f23a8f3603a870092fd0e49ce38853735))

- Update documentation to highlight Docker image availability on GitHub Packages
  ([#11](https://github.com/raveenb/fal-mcp-server/pull/11),
  [`b4556d1`](https://github.com/raveenb/fal-mcp-server/commit/b4556d198168a3999eb42e94cc61df3225cff940))

- Update README for dynamic model discovery feature
  ([`b8ebd8f`](https://github.com/raveenb/fal-mcp-server/commit/b8ebd8f4fb5552064a31db9f3d783901074b7c1c))

- Update README with Docker installation and badges
  ([#14](https://github.com/raveenb/fal-mcp-server/pull/14),
  [`5d91466`](https://github.com/raveenb/fal-mcp-server/commit/5d914664d01cd7a954c2061ea1e876f0f70afedc))

### Features

- Add Docker support with multi-transport capabilities
  ([`96abbeb`](https://github.com/raveenb/fal-mcp-server/commit/96abbeb84ba2af4fc1f85ec3dd699788047d6240))

- Add dynamic model discovery from Fal.ai API
  ([#16](https://github.com/raveenb/fal-mcp-server/pull/16),
  [`83453d8`](https://github.com/raveenb/fal-mcp-server/commit/83453d8ee692f9d6f6366c5cec6b4367dd535373))

- Add GitHub Pages documentation site with SEO
  ([#11](https://github.com/raveenb/fal-mcp-server/pull/11),
  [`b4556d1`](https://github.com/raveenb/fal-mcp-server/commit/b4556d198168a3999eb42e94cc61df3225cff940))

- Add GitHub Pages documentation site with SEO optimization
  ([#11](https://github.com/raveenb/fal-mcp-server/pull/11),
  [`b4556d1`](https://github.com/raveenb/fal-mcp-server/commit/b4556d198168a3999eb42e94cc61df3225cff940))

### Testing

- Add comprehensive Docker integration tests
  ([`f35e312`](https://github.com/raveenb/fal-mcp-server/commit/f35e312940225d964358488c034e58ce1452f1f3))


## v0.3.0 (2025-09-02)


## v0.2.1 (2025-09-02)


## v0.2.0 (2025-09-02)


## v1.1.0 (2025-08-28)


## v0.1.0 (2025-08-28)

- Initial Release
