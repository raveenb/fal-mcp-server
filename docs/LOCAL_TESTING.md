# Local CI/CD Testing with Act

This guide explains how to test GitHub Actions workflows locally using [act](https://github.com/nektos/act).

## Why Use Act?

- **Faster feedback**: Test CI changes without pushing to GitHub
- **Save Actions minutes**: No GitHub Actions minutes consumed
- **Debug locally**: Troubleshoot CI issues on your machine
- **Validate secrets**: Ensure secrets work before deployment

## Installation

### macOS (Homebrew)
```bash
brew install act
```

Or use our Makefile:
```bash
make act-install
```

### Linux (Bash script)
```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Windows (Chocolatey)
```powershell
choco install act-cli
```

### Docker (Alternative)
```bash
docker pull ghcr.io/nektos/act:latest
```

## Configuration

### 1. Copy Secrets Template
```bash
cp .secrets.example .secrets
```

### 2. Edit .secrets File
Add your actual API keys:
```bash
FAL_KEY=your_actual_fal_key
PYPI_API_TOKEN=pypi-your_actual_token  # Only needed for publish testing
```

**⚠️ IMPORTANT**: Never commit `.secrets` to version control!

## Usage

### Quick Start with Makefile

```bash
# Run full CI workflow
make ci-local

# Test specific Python version
make ci-test

# Test publish workflow (dry run)
make ci-publish
```

### Direct Act Commands

```bash
# Run CI workflow on push event
act push --workflows .github/workflows/ci.yml

# Run CI workflow on pull request
act pull_request

# Test specific job
act -j test

# Test with specific Python version
act -j test --matrix python-version:3.11

# List available workflows
act -l

# Dry run (see what would execute)
act -n

# Verbose output for debugging
act -v
```

## Testing Specific Scenarios

### Test All Python Versions
```bash
act push --workflows .github/workflows/ci.yml
```

### Test Single Python Version
```bash
act push --workflows .github/workflows/ci.yml --matrix python-version:3.10
```

### Test Publishing (Dry Run)
```bash
act push --workflows .github/workflows/publish.yml --dryrun
```

### Test with Custom Event
```bash
# Create event.json
echo '{"ref": "refs/tags/v1.0.0"}' > event.json
act push --eventpath event.json
```

## Troubleshooting

### Common Issues

#### 1. Docker Not Running
```
Error: Cannot connect to the Docker daemon
```
**Solution**: Start Docker Desktop or Docker daemon

#### 2. Secrets Not Found
```
Error: Required secret FAL_KEY not found
```
**Solution**: Ensure `.secrets` file exists with correct format

#### 3. Platform Issues
```
Error: unsupported platform
```
**Solution**: Use `--container-architecture linux/amd64` flag

#### 4. Large Image Downloads
First run downloads runner images (~1GB). Subsequent runs are faster.

### Debugging Tips

1. **Verbose Mode**: Use `-v` flag for detailed output
   ```bash
   act -v push
   ```

2. **List Workflows**: Check available workflows
   ```bash
   act -l
   ```

3. **Dry Run**: Preview without execution
   ```bash
   act -n push
   ```

4. **Shell Access**: Debug inside container
   ```bash
   act -j test --container-shell
   ```

## Act Configuration

The `.actrc` file configures act defaults:

```bash
# Runner images matching GitHub Actions
-P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest

# Architecture
--container-architecture linux/amd64

# Reuse containers
--reuse

# Default secrets file
--secret-file .secrets
```

## Differences from GitHub Actions

1. **No GitHub Context**: Some GitHub-specific variables unavailable
2. **Network Limitations**: Local network, not GitHub's infrastructure
3. **Cache Differences**: No access to GitHub's cache
4. **Service Containers**: May need manual configuration
5. **Artifacts**: Stored locally, not uploaded

## Best Practices

1. **Test Before Push**: Always run `make ci-local` before pushing
2. **Keep Secrets Secure**: Never commit `.secrets` file
3. **Update Act**: Keep act updated for latest features
   ```bash
   brew upgrade act
   ```
4. **Clean Containers**: Periodically clean old containers
   ```bash
   docker system prune
   ```

## Advanced Usage

### Custom Runner Image
```bash
act -P ubuntu-latest=custom-image:tag
```

### Bind Mount for Speed
```bash
act --bind
```

### Run Specific Step
```bash
act -j job-name -s step-name
```

### Matrix Testing
```bash
# Test all matrix combinations
act push

# Test specific matrix value
act push --matrix os:ubuntu-latest --matrix python-version:3.10
```

## Resources

- [Act Documentation](https://github.com/nektos/act)
- [Act Runner Images](https://github.com/catthehacker/docker_images)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)