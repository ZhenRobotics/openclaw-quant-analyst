#!/bin/bash

# Publish to both PyPI and npm

set -e

echo "======================================"
echo "Publishing to PyPI and npm"
echo "======================================"

# Publish to PyPI
echo ""
echo "Step 1/2: Publishing to PyPI..."
echo ""
./scripts/publish-pypi.sh

# Publish to npm
echo ""
echo "Step 2/2: Publishing to npm..."
echo ""
./scripts/publish-npm.sh

echo ""
echo "======================================"
echo "✅ Published to both platforms!"
echo "======================================"
echo ""
echo "PyPI:  pip install openclaw-quant-analyst"
echo "npm:   npm install -g openclaw-quant-analyst"
echo ""
