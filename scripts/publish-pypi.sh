#!/bin/bash

# Publish to PyPI script

set -e

echo "======================================"
echo "Publishing to PyPI"
echo "======================================"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build package
echo "📦 Building package..."
python3 -m pip install --upgrade build twine
python3 -m build

# Check package
echo "🔍 Checking package..."
python3 -m twine check dist/*

# Upload to PyPI
echo "📤 Uploading to PyPI..."
echo "⚠️  You will be prompted for your PyPI credentials"
python3 -m twine upload dist/*

echo ""
echo "✅ Published to PyPI successfully!"
echo ""
echo "Users can now install with:"
echo "  pip install openclaw-quant-analyst"
echo ""
