#!/bin/bash
# Push to GitHub helper script

echo "📦 Preparing to push Fal.ai MCP Server to GitHub"
echo "================================================"
echo ""
echo "Before running this script, make sure you:"
echo "1. Created a new repository on GitHub (don't initialize with README)"
echo "2. Have your GitHub username ready"
echo ""
read -p "Enter your GitHub username: " github_username
read -p "Enter your repository name (default: fal-mcp-server): " repo_name

repo_name=\${repo_name:-fal-mcp-server}

echo ""
echo "Adding GitHub remote..."
git remote add origin "https://github.com/\${github_username}/\${repo_name}.git" 2>/dev/null || {
    echo "Remote already exists, updating URL..."
    git remote set-url origin "https://github.com/\${github_username}/\${repo_name}.git"
}

echo ""
echo "Repository URL: https://github.com/\${github_username}/\${repo_name}"
echo ""
echo "Ready to push! Run these commands:"
echo ""
echo "  git push -u origin main"
echo ""
echo "If you get an error about 'main' branch, try:"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "After pushing, update the README.md and pyproject.toml with your:"
echo "  - GitHub username"
echo "  - Email address"
echo "  - Any other personal information"
