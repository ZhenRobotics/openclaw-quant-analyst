# Publishing Guide

This document explains how to publish `openclaw-quant-analyst` to PyPI and npm.

## Prerequisites

### For PyPI
- Python 3.9+
- PyPI account: https://pypi.org/account/register/
- API token (recommended) or username/password

### For npm
- Node.js 14+
- npm account: https://www.npmjs.com/signup
- Logged in via `npm login`

## Quick Publish (Both Platforms)

```bash
# Publish to both PyPI and npm
./scripts/publish-all.sh
```

## Publish to PyPI Only

### Step 1: Setup PyPI credentials

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE
```

Or use username/password interactively.

### Step 2: Publish

```bash
# Run publish script
./scripts/publish-pypi.sh

# Or manually:
python3 -m pip install --upgrade build twine
python3 -m build
python3 -m twine upload dist/*
```

### Step 3: Verify

```bash
pip install openclaw-quant-analyst
python3 -c "from openclaw_quant import Strategy, Backtest; print('✓ Installed')"
```

## Publish to npm Only

### Step 1: Login to npm

```bash
npm login
```

### Step 2: Publish

```bash
# Run publish script
./scripts/publish-npm.sh

# Or manually:
npm publish
```

### Step 3: Verify

```bash
npm install -g openclaw-quant-analyst
openclaw-quant-analyst help
```

## Version Management

### Bump version

Update version in THREE places:
1. `setup.py` - line 11
2. `pyproject.toml` - line 6
3. `package.json` - line 3
4. `src/openclaw_quant/__init__.py` - line 6

```bash
# Example: bump to 0.1.1
sed -i 's/version="0.1.0"/version="0.1.1"/' setup.py
sed -i 's/version = "0.1.0"/version = "0.1.1"/' pyproject.toml
sed -i 's/"version": "0.1.0"/"version": "0.1.1"/' package.json
sed -i 's/__version__ = "0.1.0"/__version__ = "0.1.1"/' src/openclaw_quant/__init__.py
```

## Pre-publish Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run tests: `pytest`
- [ ] Check package contents: `python3 -m build && tar -tzf dist/*.tar.gz`
- [ ] Check npm package: `npm pack --dry-run`
- [ ] Commit all changes
- [ ] Create git tag: `git tag v0.1.0`
- [ ] Push to GitHub: `git push && git push --tags`

## Post-publish

### Update ClawHub

```bash
# Update to latest version
clawhub publish quant-analyst --version 0.1.0
```

### Verify Installation

```bash
# PyPI
pip install openclaw-quant-analyst
python3 -c "from openclaw_quant import __version__; print(f'PyPI version: {__version__}')"

# npm
npm install -g openclaw-quant-analyst
openclaw-quant-analyst help
```

### Announce

- Update GitHub Release
- Update README badges
- Announce on social media
- Update documentation

## Troubleshooting

### PyPI: "File already exists"

You cannot overwrite an existing version on PyPI. Bump the version number.

### npm: "You do not have permission"

Make sure you're logged in and have permission to publish:

```bash
npm whoami
npm owner ls openclaw-quant-analyst
```

### "Package name already taken"

If the name is taken, you'll need to:
1. Choose a different name
2. Or request transfer from current owner

## Automated CI/CD (Future)

Consider setting up GitHub Actions for automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish

on:
  push:
    tags:
      - 'v*'

jobs:
  publish-pypi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}

  publish-npm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Links

- PyPI: https://pypi.org/project/openclaw-quant-analyst/
- npm: https://www.npmjs.com/package/openclaw-quant-analyst
- GitHub: https://github.com/ZhenRobotics/openclaw-quant-analyst
- ClawHub: https://clawhub.ai/ZhenStaff/quant-analyst
