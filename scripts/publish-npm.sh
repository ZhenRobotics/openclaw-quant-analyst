#!/bin/bash

# Publish to npm script

set -e

echo "======================================"
echo "Publishing to npm"
echo "======================================"

# Check if logged in to npm
if ! npm whoami &> /dev/null; then
    echo "⚠️  You are not logged in to npm"
    echo "Please run: npm login"
    exit 1
fi

# Check package
echo "🔍 Checking package..."
npm pack --dry-run

# Publish
echo "📤 Publishing to npm..."
npm publish

echo ""
echo "✅ Published to npm successfully!"
echo ""
echo "Users can now install with:"
echo "  npm install -g openclaw-quant-analyst"
echo ""
