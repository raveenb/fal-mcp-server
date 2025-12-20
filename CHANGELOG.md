# CHANGELOG

<!-- version list -->

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
