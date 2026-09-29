# Tech Stack Rules (Python)

## Python Package Management

When adding or updating Python packages:
1. ALWAYS research online to verify you're using the LATEST stable versions from PyPI
2. Check PyPI.org for each package to confirm the latest version
3. Use `uv add <package>` to add packages (uv automatically gets the latest version)
4. After adding packages, verify in pyproject.toml that versions are current
5. Example workflow:
   - Check https://pypi.org/project/<package-name>/ for latest version
   - Run `uv add <package>` to install latest
   - Verify version in pyproject.toml matches PyPI

This ensures dependencies are up-to-date and secure.

## Python-Specific Standards

### Modern Python Features
- **Modern Python**: Use latest Python features (3.10+: match/case, type unions with |, etc.)
- **Type Safety**: Full type hints throughout the codebase
- **Dataclasses**: Use dataclasses for configuration and data structures

### Environment Variables
- **Environment Variables**: Always load from .env file using `python-dotenv` at entry points (CLI, main scripts)

### Python Logging
- Use Python's `logging` module
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages

### Package Updates
1. Always check PyPI for latest stable versions
2. Use `uv add package` for automatic latest version
3. Test after updates to ensure compatibility
4. Update version in pyproject.toml if making a release
