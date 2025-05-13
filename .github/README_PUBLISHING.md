# Publishing airpy-tool to PyPI with GitHub Actions

This package automatically publishes to PyPI when a new release is created on GitHub. Follow these steps to use this workflow:

## Prerequisites
1. Create an account on [PyPI](https://pypi.org/).
2. Generate an API token.

## Setting up GitHub Secrets
Add your PyPI API token as a GitHub secret:
1. Navigate to your GitHub repository → Settings → Secrets and variables → Actions.
2. Add the secret:
   - `PYPI_API_TOKEN`: Your PyPI API token.

## Publishing a New Release
To release a new version:
1. Update the version number in `setup.py`.
2. Commit and push your changes to GitHub.
3. Go to your GitHub repository → Releases → Create a new release.
4. Create a new tag with the version (e.g., `v1.0.0`).

If you need to update the tag:
- Delete the old tag:
  ```
  git tag -d v1.0.0
  git push --delete origin v1.0.0
  ```
- Add the new tag:
  ```
  git tag v1.0.1
  git push origin v1.0.1
  ```

5. Fill in the release title and description.
6. Publish the release.

The GitHub Actions workflow will automatically build and publish your package.

## Testing
- pip install airpy-tool
