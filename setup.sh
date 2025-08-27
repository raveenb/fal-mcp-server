#!/bin/bash
# Setup script for Fal.ai MCP Server

echo "🎨 Setting up Fal.ai MCP Server"
echo "================================"

# Check Python version
python_version=\$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.10"

if [ "\$(printf '%s\n' "\$required_version" "\$python_version" | sort -V | head -n1)" != "\$required_version" ]; then
    echo "❌ Python 3.10+ is required (you have \$python_version)"
    exit 1
fi

echo "✅ Python version \$python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -e .

# Check for API key
if [ -z "\$FAL_KEY" ] && [ ! -f .env ]; then
    echo ""
    echo "⚠️  No FAL_KEY found!"
    echo "Please set your Fal.ai API key:"
    echo "  export FAL_KEY='your-key-here'"
    echo "Or create a .env file with:"
    echo "  FAL_KEY='your-key-here'"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your FAL_KEY environment variable"
echo "2. Configure Claude Desktop (see README.md)"
echo "3. Restart Claude Desktop"
echo ""
echo "To test the installation:"
echo "  source .venv/bin/activate"
echo "  python examples/basic_usage.py"
