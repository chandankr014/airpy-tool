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
1. Update the version number in following:
- setup.py
- pyproject.toml
- publish.yml

2. Commit and push your changes to GitHub.
```
git add .
git commit -m "released new version x.x.x"
git tag -a v1.0.0 -m "released new version x.x.x"
git push origin main
```

3. push the latest tag now.
-  `git push origin v1.0.1`

4. This will start the github CICD Pipeline, you can check in the Github Action.
The GitHub Actions workflow will automatically build and publish your package.

# 
Optional:
```
If you want delete the old tag:
-  git tag -d v1.0.0
-  git push --delete origin v1.0.0
Fill in the release title and description.
Publish the release.
```

## Testing
- `pip install --no-cache-dir airpy-tool`
- Package page: `https://pypi.org/project/airpy-tool/`
