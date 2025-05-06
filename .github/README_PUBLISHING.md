# Publishing airpy-tool to PyPI with GitHub Actions

This package is set up to automatically publish to PyPI whenever a new release is created on GitHub. Here's how to use this workflow:

## Prerequisites

1. Create accounts on [PyPI](https://pypi.org/) and [Test PyPI](https://test.pypi.org/)
2. Create API tokens:
   - Go to your account settings on PyPI → API tokens → Add API token
   - Do the same for Test PyPI

## Setting up GitHub Secrets

Before you can publish, you need to add your PyPI API tokens as GitHub secrets:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI API token

## Publishing a New Release

To publish a new version:

1. Update the version number in `setup.py`
2. Commit and push your changes to GitHub
3. Go to your GitHub repository → Releases → Create a new release
4. Create a new tag with the version (e.g., `v1.0.0`)
5. Fill out the release title and description
6. Publish the release

The GitHub Actions workflow will automatically:
1. Build your package
2. Upload it to Test PyPI first
3. Upload it to the real PyPI

## Testing Your Package

After publication, you can verify that your package was published correctly:

```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ airpy-tool

# Install from PyPI (once published)
pip install airpy-tool
``` 